"""
House of AI™ YouTube Knowledge Extraction Bot

Extracts content from Chase Hughes, Leanne Mosley (Rich Queen), and
Brooke Shelton — then uses Claude to build the marketing engine knowledge
base with buyer psychology, messaging, and content structure markers.

Usage:
    python bot.py                          # Run all creators
    python bot.py --creator chase-hughes   # Run one creator
    python bot.py --max-videos 10          # Limit videos per channel
    python bot.py --skip-extraction        # Use cached data, re-run analysis only
"""

import os
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic

from config import CREATORS
from extractor import fetch_creator_data
from analyzer import analyze_video, synthesize_creator_knowledge, build_master_engine_brief

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "output"


def save_json(data: dict | list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    log.info("Saved: %s", path)


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    log.info("Saved: %s", path)


def load_json(path: Path) -> dict | list | None:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def process_creator(
    creator_key: str,
    creator: dict,
    youtube_api_key: str,
    anthropic_client: anthropic.Anthropic,
    max_videos: int,
    skip_extraction: bool,
) -> dict:
    creator_dir = OUTPUT_DIR / creator_key
    raw_data_path = creator_dir / "raw_videos.json"
    analysis_path = creator_dir / "video_analyses.json"
    profile_path = creator_dir / "knowledge_profile.json"

    # --- Step 1: Fetch YouTube data ---
    if skip_extraction and raw_data_path.exists():
        log.info("[%s] Using cached video data", creator["name"])
        videos = load_json(raw_data_path)
    else:
        log.info("[%s] Fetching YouTube channel data...", creator["name"])
        videos = fetch_creator_data(creator, youtube_api_key, max_videos=max_videos)
        if not videos:
            log.warning("[%s] No videos found. Check channel config.", creator["name"])
            return {}
        save_json(videos, raw_data_path)

        # Save raw transcripts as individual text files for NotebookLM / RAG
        transcripts_dir = creator_dir / "transcripts"
        for video in videos:
            if video.get("transcript"):
                safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in video["title"])[:60]
                transcript_path = transcripts_dir / f"{video['video_id']}_{safe_title}.txt"
                transcript_path.parent.mkdir(parents=True, exist_ok=True)
                content = f"# {video['title']}\n\nURL: {video['url']}\nPublished: {video['published_at']}\n\n{video['transcript']}"
                transcript_path.write_text(content)

    log.info("[%s] Processing %d videos", creator["name"], len(videos))

    # --- Step 2: Analyze each video with Claude ---
    if skip_extraction and analysis_path.exists():
        log.info("[%s] Using cached video analyses", creator["name"])
        analyses = load_json(analysis_path)
    else:
        log.info("[%s] Running Claude analysis on transcripts...", creator["name"])
        analyses = []
        for i, video in enumerate(videos):
            log.info("[%s] Analyzing %d/%d: %s", creator["name"], i + 1, len(videos), video["title"][:50])
            result = analyze_video(anthropic_client, creator, video)
            if result:
                analyses.append(result)
        save_json(analyses, analysis_path)

    log.info("[%s] Analyzed %d videos with content", creator["name"], len(analyses))

    # --- Step 3: Synthesize creator knowledge profile ---
    log.info("[%s] Synthesizing master knowledge profile...", creator["name"])
    profile = synthesize_creator_knowledge(anthropic_client, creator, analyses)
    save_json(profile, profile_path)

    return profile


def run(args: argparse.Namespace) -> None:
    youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not youtube_api_key:
        raise ValueError("YOUTUBE_API_KEY is not set. Copy .env.example to .env and add your key.")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")

    anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

    creators_to_run = (
        {args.creator: CREATORS[args.creator]} if args.creator else CREATORS
    )

    creator_profiles = []

    for creator_key, creator in creators_to_run.items():
        log.info("=" * 60)
        log.info("Processing creator: %s", creator["name"])
        log.info("=" * 60)

        profile = process_creator(
            creator_key=creator_key,
            creator=creator,
            youtube_api_key=youtube_api_key,
            anthropic_client=anthropic_client,
            max_videos=args.max_videos,
            skip_extraction=args.skip_extraction,
        )

        if profile:
            creator_profiles.append(profile)

    # --- Step 4: Build master marketing engine brief ---
    if len(creator_profiles) >= 1:
        log.info("=" * 60)
        log.info("Building Master Marketing Engine Brief...")
        log.info("=" * 60)

        master_brief = build_master_engine_brief(anthropic_client, creator_profiles)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        brief_path = OUTPUT_DIR / f"marketing-engine-master-brief_{timestamp}.md"
        save_text(master_brief, brief_path)

        # Also save the latest as a stable filename
        latest_path = OUTPUT_DIR / "marketing-engine-master-brief.md"
        save_text(master_brief, latest_path)

        print("\n" + "=" * 60)
        print("DONE")
        print("=" * 60)
        print(f"\nMaster Marketing Engine Brief: {latest_path}")
        print(f"\nCreator knowledge profiles saved to: {OUTPUT_DIR}/")
        print("\nNext steps:")
        print("  1. Review the master brief at output/marketing-engine-master-brief.md")
        print("  2. Upload transcript files from output/*/transcripts/ to NotebookLM")
        print("  3. Use the master brief as the system prompt for your AI marketing agent")
        print("  4. Feed the knowledge_profile.json files into your vector database")


def main():
    parser = argparse.ArgumentParser(description="House of AI™ YouTube Knowledge Extraction Bot")
    parser.add_argument(
        "--creator",
        choices=list(CREATORS.keys()),
        help="Run for a single creator only",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=int(os.environ.get("MAX_VIDEOS_PER_CHANNEL", 50)),
        help="Max videos to process per channel (default: 50)",
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip YouTube fetching and re-run Claude analysis on cached data",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
