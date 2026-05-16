"""
Layer 2 — Knowledge Base
Long-term memory. Rebuilt every night at 2am from all accumulated context:
expert frameworks, what content performed, audience patterns, offer results.
The agent reads this at the start of every session to know everything.
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path
import anthropic

log = logging.getLogger(__name__)

MEMORY_DIR = Path(__file__).parent / "state"
KB_FILE = MEMORY_DIR / "knowledge_base.json"
EXPERT_DIR = Path(__file__).parent.parent / "youtube-knowledge-extractor" / "output"
CONTENT_DIR = Path(__file__).parent.parent / "daily-content-agent" / "output"


def load() -> dict:
    if KB_FILE.exists():
        with open(KB_FILE) as f:
            return json.load(f)
    return {"last_rebuilt": None, "projects": [], "content_history": [], "memory": {}}


def _collect_content_history(days: int = 30) -> list[dict]:
    """Collect recent content packages to learn what's been produced."""
    history = []
    if not CONTENT_DIR.exists():
        return history
    for day_dir in sorted(CONTENT_DIR.iterdir(), reverse=True)[:days]:
        if day_dir.is_dir():
            pkg_path = day_dir / "content_package.json"
            if pkg_path.exists():
                with open(pkg_path) as f:
                    pkg = json.load(f)
                history.append({
                    "date": day_dir.name,
                    "theme": pkg.get("theme_of_the_day", ""),
                    "social_hooks": [p.get("hook", "") for p in pkg.get("social_posts", [])],
                    "email_subject": pkg.get("email", {}).get("subject_line", ""),
                })
    return history


def _load_expert_profiles() -> dict:
    """Load all creator knowledge profiles."""
    profiles = {}
    if not EXPERT_DIR.exists():
        return profiles
    for creator_dir in EXPERT_DIR.iterdir():
        if creator_dir.is_dir():
            profile_path = creator_dir / "knowledge_profile.json"
            if profile_path.exists():
                with open(profile_path) as f:
                    profiles[creator_dir.name] = json.load(f)
    return profiles


def rebuild(anthropic_client: anthropic.Anthropic) -> dict:
    """
    Rebuild the full knowledge base from all accumulated context.
    Run this nightly at 2am — same as Ray CFU's architecture.
    """
    log.info("Rebuilding knowledge base...")

    expert_profiles = _load_expert_profiles()
    content_history = _collect_content_history(days=30)

    profiles_summary = json.dumps(
        {k: {"role": v.get("role", ""), "core_philosophy": v.get("core_philosophy", "")}
         for k, v in expert_profiles.items()},
        indent=2,
    )[:3000]

    history_summary = json.dumps(content_history[:10], indent=2)[:2000]

    prompt = f"""You are rebuilding the long-term memory for the House of AI™ marketing agent.

## Expert Knowledge Loaded
{profiles_summary}

## Recent Content History (last 30 days)
{history_summary}

Build a concise, structured knowledge base that the agent reads every morning.
Return JSON:
{{
  "core_mission": "1 sentence — what this agent exists to do",
  "brand_voice_rules": ["rule 1", "rule 2", "rule 3", "rule 4", "rule 5"],
  "top_frameworks_active": [
    {{"framework": "name", "creator": "who", "one_line": "what it does", "always_use_when": "trigger"}}
  ],
  "proven_hooks": ["hooks that have been used recently"],
  "content_themes_covered": ["themes recently covered — avoid repeating"],
  "audience_insights": ["what we know about the dream client"],
  "offer_context": "current offer and positioning",
  "what_is_working": ["patterns that are working in content"],
  "do_not_repeat": ["topics or angles covered recently"],
  "priorities_this_week": ["top 3 priorities for content this week"]
}}

Only return valid JSON."""

    try:
        message = anthropic_client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        memory = json.loads(raw)
    except Exception as e:
        log.error("KB rebuild error: %s", e)
        memory = {}

    kb = {
        "last_rebuilt": datetime.now().isoformat(),
        "rebuild_date": date.today().isoformat(),
        "expert_profiles_loaded": list(expert_profiles.keys()),
        "content_history_days": len(content_history),
        "memory": memory,
    }

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(KB_FILE, "w") as f:
        json.dump(kb, f, indent=2)

    log.info(
        "Knowledge base rebuilt: %d expert profiles, %d days of history",
        len(expert_profiles),
        len(content_history),
    )
    return kb


def get_agent_context() -> str:
    """Return the knowledge base as a text block for injecting into agent prompts."""
    kb = load()
    if not kb.get("memory"):
        return "Knowledge base not yet built. Run: python rebuild_kb.py"
    mem = kb["memory"]
    lines = [
        f"# Agent Memory (rebuilt: {kb.get('rebuild_date', 'unknown')})\n",
        f"**Mission:** {mem.get('core_mission', '')}\n",
        "\n**Brand Voice Rules:**",
    ]
    for rule in mem.get("brand_voice_rules", []):
        lines.append(f"- {rule}")
    lines.append("\n**What's Working:**")
    for w in mem.get("what_is_working", []):
        lines.append(f"- {w}")
    lines.append("\n**Do NOT Repeat (already covered):**")
    for d in mem.get("do_not_repeat", []):
        lines.append(f"- {d}")
    lines.append("\n**This Week's Priorities:**")
    for p in mem.get("priorities_this_week", []):
        lines.append(f"- {p}")
    return "\n".join(lines)
