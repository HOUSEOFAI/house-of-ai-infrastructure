"""
Claude-powered framework analyzer.
Extracts buyer psychology markers, messaging frameworks, and content
structure patterns from raw YouTube transcripts for the House of AI™
marketing & content engine.
"""

import json
import logging
from typing import Optional
import anthropic

log = logging.getLogger(__name__)

MODEL = "claude-opus-4-7"
MAX_TRANSCRIPT_CHARS = 12_000  # ~3k tokens per transcript chunk


def _build_extraction_prompt(creator: dict, video: dict) -> str:
    transcript = (video.get("transcript") or "")[:MAX_TRANSCRIPT_CHARS]
    focus_list = "\n".join(f"  - {f}" for f in creator["extract_focus"])

    return f"""You are an expert at extracting marketing intelligence from expert content.

## Creator
**{creator['name']}** — Role in marketing engine: {creator['role']}

## Video
Title: {video['title']}
Description: {video.get('description', '')}

## Transcript (may be truncated)
{transcript}

## Your Task
Extract structured marketing intelligence from this content. Focus specifically on:
{focus_list}

Return a JSON object with this exact structure:
{{
  "video_id": "{video['video_id']}",
  "title": "{video['title']}",
  "creator": "{creator['name']}",
  "has_valuable_content": true/false,
  "frameworks_identified": [
    {{
      "name": "Framework name",
      "description": "What it is and how it works",
      "marketing_application": "How to use this in marketing content",
      "key_language": ["exact phrases or language patterns from this framework"]
    }}
  ],
  "psychology_triggers": ["trigger 1", "trigger 2"],
  "language_patterns": [
    {{
      "pattern": "the language pattern or script",
      "context": "when/how to use it",
      "marker_category": "one of: psychology_triggers | messaging_language | content_structure | hooks_and_opens | objection_handling | authority_signals | identity_shifts | conversion_sequences"
    }}
  ],
  "key_concepts": ["concept 1", "concept 2"],
  "actionable_markers": [
    {{
      "marker": "specific, actionable instruction for the marketing engine",
      "category": "marker category",
      "priority": "high | medium | low"
    }}
  ]
}}

Only return valid JSON. No explanation before or after."""


def analyze_video(
    client: anthropic.Anthropic,
    creator: dict,
    video: dict,
) -> Optional[dict]:
    """Run Claude analysis on a single video. Returns parsed JSON or None."""
    if not video.get("transcript"):
        log.debug("Skipping %s — no transcript", video["video_id"])
        return None

    prompt = _build_extraction_prompt(creator, video)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()

        # Strip markdown code fences if Claude adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw)
    except json.JSONDecodeError as e:
        log.warning("JSON parse error for %s: %s", video["video_id"], e)
        return None
    except Exception as e:
        log.error("Claude API error for %s: %s", video["video_id"], e)
        return None


def synthesize_creator_knowledge(
    client: anthropic.Anthropic,
    creator: dict,
    video_analyses: list[dict],
) -> dict:
    """
    Synthesize all video analyses for one creator into a master knowledge
    profile — the final set of markers for the marketing engine.
    """
    analyses_json = json.dumps(video_analyses, indent=2)[:40_000]

    prompt = f"""You are synthesizing marketing intelligence from {creator['name']}'s complete YouTube content.

## Creator Profile
Name: {creator['name']}
Role: {creator['role']}
Marketing Application: {creator['marketing_application']}

## All Video Analyses (may be truncated)
{analyses_json}

## Your Task
Create a master knowledge profile that will program the House of AI™ marketing & content engine.

Return a JSON object with this structure:
{{
  "creator": "{creator['name']}",
  "role": "{creator['role']}",
  "core_philosophy": "2-3 sentence summary of their core philosophy",
  "signature_frameworks": [
    {{
      "name": "Framework name",
      "description": "Clear explanation",
      "how_to_apply": "Step-by-step application in marketing content",
      "example_language": "Example copy or language using this framework"
    }}
  ],
  "master_language_patterns": [
    {{
      "pattern": "the language pattern",
      "category": "marker category",
      "example": "example of it in use",
      "priority": "high | medium | low"
    }}
  ],
  "psychology_markers": {{
    "buyer_triggers": ["list of buyer psychology triggers to embed"],
    "identity_shifts": ["identity-based statements that shift self-concept"],
    "resistance_dissolvers": ["language that removes objections and resistance"],
    "authority_builders": ["patterns that build trust and authority"]
  }},
  "content_markers": {{
    "hook_formulas": ["proven hook structures to use"],
    "story_arcs": ["narrative structures to employ"],
    "content_pillars": ["core content themes and angles"],
    "call_to_action_patterns": ["CTA language that converts"]
  }},
  "programming_instructions": [
    "Specific instruction 1 for programming the marketing engine",
    "Specific instruction 2 for programming the marketing engine"
  ],
  "top_10_markers": [
    {{
      "marker": "The most important marker to program",
      "why": "Why this is critical",
      "implementation": "How to implement it in content"
    }}
  ]
}}

Only return valid JSON."""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        log.error("Synthesis error for %s: %s", creator["name"], e)
        return {}


def build_master_engine_brief(
    client: anthropic.Anthropic,
    creator_profiles: list[dict],
) -> str:
    """
    Combine all creator profiles into a single master marketing engine brief
    — the document that programs the AI marketing agent.
    """
    profiles_json = json.dumps(creator_profiles, indent=2)

    prompt = f"""You are creating the master programming brief for an AI-powered marketing & content engine.

The engine is for a House of AI™ business — helping women entrepreneurs build AI-supported businesses.

## Creator Knowledge Profiles
{profiles_json}

## Your Task
Write a comprehensive markdown document titled:
"# House of AI™ Marketing Engine Master Brief"

This document will be used to program an AI agent that generates all marketing content.
It must synthesize:
- Buyer psychology and behavioral influence from **Chase Hughes**
- Premium messaging and identity language from **Leanne Mosley (Rich Queen)**
- Content structure and strategy from **Brooke Shelton**
- Funnel hacking, offer architecture, and hook-story-offer from **Russell Brunson**
- Feminine power, quantum identity, and desire-based transformation from **Melanie Ann Layer**

Structure the document with these sections:
1. **Core Philosophy** — The unified marketing philosophy combining all five systems
2. **Buyer Psychology Markers** — Chase Hughes frameworks to embed in every piece
3. **Messaging Framework** — Leanne Mosley's language and premium positioning system
4. **Content Architecture** — Brooke Shelton's structure and strategy system
5. **Funnel Architecture** — Russell Brunson's value ladder, offer stack, and funnel sequences
6. **Feminine Power & Desire Activation** — Melanie Ann Layer's identity-elevation and quantum frameworks
7. **Hook-Story-Offer System** — How to open, narrate, and close every piece of content
8. **Master Marker List** — All high-priority markers numbered and categorized
9. **Content Generation Instructions** — Step-by-step instructions for the AI agent
10. **Language Patterns Library** — Ready-to-use language patterns by category
11. **Funnel Stage Playbook** — What content to produce at each funnel stage (cold/warm/hot)
12. **Programming Rules** — Non-negotiable rules for every piece of content

Write this as a detailed, actionable brief. Be specific. Include actual language patterns,
frameworks, funnel structures, and instructions. This is the brain of the marketing engine."""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        log.error("Master brief generation error: %s", e)
        return ""
