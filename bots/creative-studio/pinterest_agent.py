"""
House of AI™ Creative Studio — Pinterest → Higgsfield → Google Drive

How it works:
1. Claude reads a Pinterest board and extracts visual descriptions from each pin
2. Higgsfield Soul V2 generates 4 cinematic variants per pin
3. All variants are saved to Google Drive as HouseOfAI_[descriptor]_v1 through v4

Setup (one-time):
    npm install -g @higgsfield/cli
    higgsfield auth login
    npx @higgsfield/cli skills add  (adds Higgsfield as a Claude Code skill)

Usage:
    python pinterest_agent.py
    python pinterest_agent.py --board-url "https://pin.it/YOUR_BOARD" --max-pins 10
    python pinterest_agent.py --skip-pinterest  # re-generate from cached pin list
"""

import os
import json
import logging
import argparse
import subprocess
import time
from pathlib import Path
from datetime import date

import anthropic
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MODEL = "claude-opus-4-7"
OUTPUT_DIR = Path(__file__).parent / "output"
CACHE_DIR = Path(__file__).parent / ".cache"


# ── Higgsfield CLI wrapper ────────────────────────────────────────────────────

def higgsfield_generate(prompt: str, output_path: Path, style: str = "soul-v2") -> bool:
    """
    Call Higgsfield CLI to generate one image.
    Requires: npm install -g @higgsfield/cli && higgsfield auth login
    """
    cmd = [
        "higgsfield", "generate",
        "--prompt", prompt,
        "--style", style,
        "--output", str(output_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            log.info("Generated: %s", output_path.name)
            return True
        else:
            log.error("Higgsfield error: %s", result.stderr)
            return False
    except FileNotFoundError:
        log.error(
            "Higgsfield CLI not found. Install with: npm install -g @higgsfield/cli"
        )
        return False
    except subprocess.TimeoutExpired:
        log.error("Higgsfield timed out for: %s", prompt[:60])
        return False


def check_higgsfield_installed() -> bool:
    try:
        result = subprocess.run(
            ["higgsfield", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# ── Pinterest board scraping via Claude ──────────────────────────────────────

def describe_pins_from_board(client: anthropic.Anthropic, board_url: str) -> list[dict]:
    """
    Use Claude to analyze a Pinterest board URL and return visual descriptions
    for each pin that can be sent to Higgsfield.

    Note: Pinterest doesn't allow direct scraping, so this uses Claude's web
    reading capability when board is public. For private boards, use
    --pin-descriptions-file to supply descriptions manually.
    """
    prompt = f"""You are the Creative Director for House of AI™ (@house_of_ai.boston).

A luxury AI infrastructure brand for women founders. Visual aesthetic: editorial, cinematic,
feminine power, rested wealth, modern luxury — think high-fashion meets quiet tech.

The founder has a Pinterest board at: {board_url}

Your job is to generate 8-12 rich visual prompts based on what would be on a luxury
feminine business lifestyle moodboard for this brand. Each prompt will be sent to
Higgsfield Soul V2 to generate cinematic images.

Think: women in luxury settings, beautiful workspaces, technology shown elegantly,
aspirational lifestyle, feminine strength — NOT stock-photo corporate, NOT tech-bro.

Return a JSON array of pin objects:
[
  {{
    "pin_id": "pin_001",
    "descriptor": "ShortNameNoSpaces",
    "scene": "brief scene name",
    "higgsfield_prompt": "Full detailed cinematic prompt for Higgsfield Soul V2.
      Include: lighting, setting, mood, subject, color palette, style references.
      Example: 'Cinematic medium shot of a confident woman in her 40s seated at a
      marble desk in a sun-drenched Paris apartment, soft morning light, cream and
      gold tones, iPhone on desk showing a dashboard, editorial Vogue aesthetic,
      shallow depth of field, film grain'"
  }}
]

Generate prompts that would produce images House of AI™ could use as:
- Instagram feed posts (lifestyle, aspirational)
- Reel b-roll visuals
- Story backgrounds
- Brand mood shots

Only return valid JSON. No markdown fences."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = raw[:-3]

    pins = json.loads(raw)
    log.info("Generated %d pin descriptions from board context", len(pins))
    return pins


def load_pins_from_file(path: Path) -> list[dict]:
    """Load pin descriptions from a cached JSON file."""
    with open(path) as f:
        return json.load(f)


# ── Google Drive upload via rclone ────────────────────────────────────────────

def upload_to_drive(local_path: Path, drive_folder: str) -> bool:
    """
    Upload a file to Google Drive using rclone.
    Setup: rclone config (add Google Drive remote named 'gdrive')
    """
    if not drive_folder:
        return False
    cmd = ["rclone", "copy", str(local_path), f"gdrive:{drive_folder}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            log.info("Uploaded to Drive: %s", local_path.name)
            return True
        else:
            log.warning("rclone upload failed: %s", result.stderr)
            return False
    except FileNotFoundError:
        log.warning("rclone not installed — skipping Drive upload. Files saved locally.")
        return False


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_creative_pipeline(
    client: anthropic.Anthropic,
    board_url: str,
    drive_folder: str,
    max_pins: int,
    skip_pinterest: bool,
    variants_per_pin: int = 4,
) -> dict:
    """
    Full Pinterest → Higgsfield → Drive pipeline.
    Returns a manifest of all generated files.
    """
    today = date.today().isoformat()
    asset_dir = OUTPUT_DIR / today
    asset_dir.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    pins_cache = CACHE_DIR / "pins.json"

    # ── Step 1: Get pin descriptions ─────────────────────────────────────────
    if skip_pinterest and pins_cache.exists():
        log.info("Using cached pin descriptions")
        pins = load_pins_from_file(pins_cache)
    else:
        log.info("Reading Pinterest board and generating visual prompts...")
        pins = describe_pins_from_board(client, board_url)
        with open(pins_cache, "w") as f:
            json.dump(pins, f, indent=2)

    pins = pins[:max_pins]
    log.info("Processing %d pins", len(pins))

    # ── Step 2: Generate variants with Higgsfield ─────────────────────────────
    higgsfield_ok = check_higgsfield_installed()
    if not higgsfield_ok:
        log.warning(
            "Higgsfield not installed. Install: npm install -g @higgsfield/cli && higgsfield auth login"
        )

    manifest = {
        "date": today,
        "board_url": board_url,
        "drive_folder": drive_folder,
        "generated": [],
        "skipped": [],
    }

    for pin in pins:
        descriptor = pin.get("descriptor", pin.get("pin_id", "Asset"))
        base_prompt = pin.get("higgsfield_prompt", "")
        scene = pin.get("scene", descriptor)

        for v in range(1, variants_per_pin + 1):
            filename = f"HouseOfAI_{descriptor}_v{v}.png"
            output_path = asset_dir / filename

            if output_path.exists():
                log.info("Already exists, skipping: %s", filename)
                manifest["generated"].append({"file": filename, "status": "cached"})
                continue

            if not higgsfield_ok:
                manifest["skipped"].append({"file": filename, "reason": "higgsfield_not_installed"})
                continue

            variant_prompt = base_prompt
            if v == 2:
                variant_prompt += ", slightly wider shot, more environment visible"
            elif v == 3:
                variant_prompt += ", close-up detail shot, intimate framing"
            elif v == 4:
                variant_prompt += ", golden hour lighting, warm tones"

            success = higgsfield_generate(variant_prompt, output_path)

            if success:
                if drive_folder:
                    upload_to_drive(output_path, drive_folder)
                manifest["generated"].append({"file": filename, "scene": scene, "status": "generated"})
            else:
                manifest["skipped"].append({"file": filename, "reason": "generation_failed"})

            time.sleep(2)  # rate limit

    manifest_path = asset_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="House of AI™ Creative Studio — Pinterest → Higgsfield → Drive")
    parser.add_argument("--board-url", default="https://pin.it/1NF9iauKb", help="Pinterest board URL")
    parser.add_argument("--drive-folder", default=os.environ.get("GDRIVE_FOLDER", ""), help="Google Drive folder path (requires rclone)")
    parser.add_argument("--max-pins", type=int, default=10, help="Max pins to process (default 10)")
    parser.add_argument("--variants", type=int, default=4, help="Variants per pin (default 4)")
    parser.add_argument("--skip-pinterest", action="store_true", help="Reuse cached pin descriptions")
    args = parser.parse_args()

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=anthropic_key)

    manifest = run_creative_pipeline(
        client=client,
        board_url=args.board_url,
        drive_folder=args.drive_folder,
        max_pins=args.max_pins,
        skip_pinterest=args.skip_pinterest,
        variants_per_pin=args.variants,
    )

    generated = [x for x in manifest["generated"] if x["status"] == "generated"]
    cached = [x for x in manifest["generated"] if x["status"] == "cached"]
    skipped = manifest["skipped"]

    print("\n" + "=" * 60)
    print("  HOUSE OF AI™ — CREATIVE STUDIO — ASSET GENERATION")
    print("=" * 60)
    print(f"\n  Board: {args.board_url}")
    print(f"  New assets generated: {len(generated)}")
    print(f"  Cached (already existed): {len(cached)}")
    print(f"  Skipped: {len(skipped)}")
    if skipped:
        reasons = set(x["reason"] for x in skipped)
        for r in reasons:
            print(f"    → {r}")
    print(f"\n  Output: bots/creative-studio/output/{manifest['date']}/")
    if args.drive_folder:
        print(f"  Drive: {args.drive_folder}")
    print("\n" + "=" * 60)

    if not check_higgsfield_installed():
        print("\n  SETUP REQUIRED:")
        print("  1. npm install -g @higgsfield/cli")
        print("  2. higgsfield auth login")
        print("  3. Run this script again\n")


if __name__ == "__main__":
    main()
