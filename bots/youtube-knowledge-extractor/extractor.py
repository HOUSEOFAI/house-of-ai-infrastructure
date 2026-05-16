"""
YouTube channel data extractor.
Fetches video metadata and transcripts using the YouTube Data API and
youtube-transcript-api (no API key needed for transcripts).
"""

import os
import time
import logging
from typing import Optional
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

log = logging.getLogger(__name__)


def get_youtube_client(api_key: str):
    return build("youtube", "v3", developerKey=api_key)


def resolve_channel_id(client, creator: dict) -> Optional[str]:
    """Return the channel ID, resolving via search if not hardcoded."""
    if creator.get("channel_id"):
        return creator["channel_id"]

    query = creator.get("search_query", creator["name"])
    response = client.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=1,
    ).execute()

    items = response.get("items", [])
    if not items:
        log.warning("Could not find channel for: %s", creator["name"])
        return None

    channel_id = items[0]["snippet"]["channelId"]
    log.info("Resolved channel ID for %s: %s", creator["name"], channel_id)
    return channel_id


def get_channel_videos(client, channel_id: str, max_videos: int = 50) -> list[dict]:
    """Return a list of video dicts (id, title, description, published_at) for a channel."""
    videos = []
    next_page_token = None

    # Get the uploads playlist ID
    channel_resp = client.channels().list(
        part="contentDetails",
        id=channel_id,
    ).execute()

    items = channel_resp.get("items", [])
    if not items:
        log.warning("No channel found for ID: %s", channel_id)
        return []

    uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    while len(videos) < max_videos:
        playlist_resp = client.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=min(50, max_videos - len(videos)),
            pageToken=next_page_token,
        ).execute()

        for item in playlist_resp.get("items", []):
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "description": snippet.get("description", "")[:500],
                "published_at": snippet["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })

        next_page_token = playlist_resp.get("nextPageToken")
        if not next_page_token:
            break

    log.info("Found %d videos for channel %s", len(videos), channel_id)
    return videos


def get_transcript(video_id: str, languages: list[str] = None) -> Optional[str]:
    """Fetch the transcript for a video. Returns plain text or None."""
    if languages is None:
        languages = ["en", "en-US", "en-GB"]

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return " ".join(entry["text"] for entry in transcript_list)
    except (TranscriptsDisabled, NoTranscriptFound):
        log.debug("No transcript for video %s", video_id)
        return None
    except Exception as e:
        log.warning("Transcript error for %s: %s", video_id, e)
        return None


def fetch_creator_data(
    creator: dict,
    api_key: str,
    max_videos: int = 50,
    delay_seconds: float = 0.5,
) -> list[dict]:
    """
    Full pipeline: resolve channel -> list videos -> fetch transcripts.
    Returns a list of enriched video dicts including transcript text.
    """
    client = get_youtube_client(api_key)
    channel_id = resolve_channel_id(client, creator)
    if not channel_id:
        return []

    videos = get_channel_videos(client, channel_id, max_videos=max_videos)

    for i, video in enumerate(videos):
        log.info(
            "[%s] Fetching transcript %d/%d: %s",
            creator["name"], i + 1, len(videos), video["title"][:60],
        )
        video["transcript"] = get_transcript(video["video_id"])
        if delay_seconds:
            time.sleep(delay_seconds)

    return videos
