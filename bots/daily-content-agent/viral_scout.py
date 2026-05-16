"""
Viral Scout — runs daily to find what's trending and going viral
in your niche so the content agent can ride the wave.
"""

import os
import logging
from googleapiclient.discovery import build
import anthropic

log = logging.getLogger(__name__)

NICHE_KEYWORDS = [
    "women entrepreneurs",
    "AI business",
    "feminine leadership",
    "high ticket coaching",
    "online business for women",
    "manifestation business",
    "digital marketing women",
    "content creation strategy",
    "buyer psychology",
    "sales funnel",
]

COMPETITOR_CHANNELS = [
    # Add channel IDs of accounts in your niche to monitor
    # e.g. "UCxxxxxxx"
]


def get_trending_videos(api_key: str, max_results: int = 20) -> list[dict]:
    """Pull trending YouTube videos in the business/entrepreneur niche."""
    client = build("youtube", "v3", developerKey=api_key)
    trending = []

    for keyword in NICHE_KEYWORDS[:5]:
        resp = client.search().list(
            part="snippet",
            q=keyword,
            type="video",
            order="viewCount",
            publishedAfter="2025-01-01T00:00:00Z",
            maxResults=5,
            relevanceLanguage="en",
        ).execute()

        for item in resp.get("items", []):
            snippet = item["snippet"]
            trending.append({
                "video_id": item["id"]["videoId"],
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "description": snippet.get("description", "")[:300],
                "keyword": keyword,
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            })

    log.info("Found %d trending videos across niche keywords", len(trending))
    return trending


def analyze_viral_patterns(
    anthropic_client: anthropic.Anthropic,
    trending_videos: list[dict],
) -> dict:
    """Use Claude to identify what's working virally right now."""
    videos_text = "\n".join(
        f"- [{v['keyword']}] {v['title']} (by {v['channel']})"
        for v in trending_videos
    )

    message = anthropic_client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Analyze these trending YouTube videos in the women entrepreneur / AI business niche.

{videos_text}

Identify:
1. The top 5 viral content ANGLES working right now (what topics/frames get attention)
2. The top 5 viral HOOK patterns from the titles
3. Emotional triggers being used (fear, desire, curiosity, identity, transformation)
4. Content formats that are dominating (lists, stories, how-tos, controversies, revelations)
5. The 3 biggest trending TOPICS to create content about TODAY

Return JSON:
{{
  "viral_angles": ["angle 1", "angle 2", "angle 3", "angle 4", "angle 5"],
  "hook_patterns": ["pattern 1", "pattern 2", "pattern 3", "pattern 4", "pattern 5"],
  "emotional_triggers": ["trigger 1", "trigger 2", "trigger 3"],
  "winning_formats": ["format 1", "format 2", "format 3"],
  "todays_topics": [
    {{"topic": "topic 1", "angle": "why this is hot right now", "content_idea": "specific idea"}},
    {{"topic": "topic 2", "angle": "why this is hot right now", "content_idea": "specific idea"}},
    {{"topic": "topic 3", "angle": "why this is hot right now", "content_idea": "specific idea"}}
  ]
}}

Only return valid JSON.""",
        }],
    )

    import json
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
