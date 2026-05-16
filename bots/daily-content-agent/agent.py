"""
House of AI™ Daily Content Agent

Runs every morning to:
1. Scout what's viral in your niche today
2. Generate a full day's marketing content using all 5 expert frameworks
3. Save everything ready to post

Usage:
    python agent.py                         # Full daily run
    python agent.py --skip-scout            # Re-generate content from yesterday's trends
    python agent.py --output-dir ./today    # Custom output folder

Schedule this to run automatically:
    cron: 0 7 * * * /path/to/.venv/bin/python /path/to/agent.py
    or use a scheduler like n8n, Make.com, or GitHub Actions (see README)
"""

import os
import json
import logging
import argparse
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv
import anthropic

from viral_scout import get_trending_videos, analyze_viral_patterns
from content_generator import generate_daily_content_package, format_content_as_markdown

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "output"

# ─── CONFIGURE YOUR BUSINESS HERE ─────────────────────────────────────────────
BUSINESS_CONTEXT = {
    "business_name": "House of AI™",
    "founder_name": "Lisa Erickson",
    "core_offer": "AI-powered business infrastructure for women entrepreneurs",
    "dream_client": "women entrepreneurs who want to scale their business with AI without burning out",
    "brand_voice": "empowered, feminine, intelligent, direct, transformational",
    "call_to_action": "DM me 'AI' to learn how to build your AI-powered business",
    "platforms": ["Instagram", "LinkedIn", "Facebook", "Email", "YouTube"],
    "niche": "AI business + feminine leadership + women entrepreneurship",
}
# ──────────────────────────────────────────────────────────────────────────────


def save(data, path: Path, as_json: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if as_json:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    else:
        path.write_text(data)
    log.info("Saved: %s", path)


def run(args: argparse.Namespace) -> None:
    youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

    client = anthropic.Anthropic(api_key=anthropic_api_key)
    today = date.today().isoformat()
    output_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR / today

    # ── Step 1: Scout viral trends ──────────────────────────────────────────
    viral_cache = output_dir / "viral_intelligence.json"

    if args.skip_scout and viral_cache.exists():
        log.info("Using cached viral intelligence from %s", today)
        with open(viral_cache) as f:
            viral_intelligence = json.load(f)
    elif youtube_api_key:
        log.info("Scouting viral content in your niche...")
        trending = get_trending_videos(youtube_api_key)
        viral_intelligence = analyze_viral_patterns(client, trending)
        save(viral_intelligence, viral_cache, as_json=True)
    else:
        log.warning("No YOUTUBE_API_KEY — skipping viral scout, using topic defaults")
        viral_intelligence = {
            "viral_angles": [
                "AI tools that replace a full-time employee",
                "Why women entrepreneurs are leaving corporate",
                "The truth about passive income with AI",
                "How I automated my entire business in 30 days",
                "Feminine leadership is the future of business",
            ],
            "hook_patterns": [
                "Nobody talks about [secret]",
                "I was wrong about [belief] until [event]",
                "The [number] thing that changed everything for me",
                "Stop doing [thing] if you want [result]",
                "What [successful person] won't tell you about [topic]",
            ],
            "todays_topics": [
                {"topic": "AI automation for solo entrepreneurs", "angle": "freedom through systems", "content_idea": "Show the exact tools replacing your team"},
                {"topic": "Feminine power in business", "angle": "being vs hustle", "content_idea": "Why your energy is your biggest business asset"},
                {"topic": "High-ticket offers", "angle": "identity over price", "content_idea": "Why your clients don't have a money problem"},
            ],
        }

    log.info("Viral intelligence ready: %d topics identified", len(viral_intelligence.get("todays_topics", [])))

    # ── Step 2: Generate full content package ───────────────────────────────
    log.info("Generating today's full content package with all 5 expert frameworks...")
    content_package = generate_daily_content_package(client, viral_intelligence, BUSINESS_CONTEXT)

    save(content_package, output_dir / "content_package.json", as_json=True)

    # ── Step 3: Format as readable markdown ─────────────────────────────────
    markdown = format_content_as_markdown(content_package)
    save(markdown, output_dir / "content_package.md")

    # ── Step 4: Print summary ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  HOUSE OF AI™ — DAILY CONTENT PACKAGE — {today}")
    print("=" * 60)
    print(f"\n  Theme: {content_package.get('theme_of_the_day', '')}")
    print(f"\n  Generated:")
    print(f"    ✓ 3 social media posts (Instagram, LinkedIn, Facebook)")
    print(f"    ✓ 1 email to list")
    print(f"    ✓ 1 YouTube hook + outline")
    print(f"    ✓ 3 Reels / TikTok scripts")
    print(f"    ✓ 1 sales post")
    print(f"    ✓ 5 hooks for tomorrow")
    print(f"\n  Output: {output_dir}/content_package.md")
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="House of AI™ Daily Content Agent")
    parser.add_argument("--skip-scout", action="store_true", help="Skip viral scouting, reuse cached trends")
    parser.add_argument("--output-dir", help="Custom output directory path")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
