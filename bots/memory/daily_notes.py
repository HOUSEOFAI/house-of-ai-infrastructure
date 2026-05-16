"""
Layer 1 — Daily Notes
Tracks what's active, what's been posted, what tasks are running.
Updated continuously throughout the day.
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path

log = logging.getLogger(__name__)

MEMORY_DIR = Path(__file__).parent / "state"
NOTES_FILE = MEMORY_DIR / "daily_notes.json"


def _today() -> str:
    return date.today().isoformat()


def load() -> dict:
    if NOTES_FILE.exists():
        with open(NOTES_FILE) as f:
            data = json.load(f)
        # Reset if it's a new day
        if data.get("date") != _today():
            return _fresh()
        return data
    return _fresh()


def _fresh() -> dict:
    return {
        "date": _today(),
        "active_tasks": [],
        "content_posted": [],
        "content_queued": [],
        "emails_sent": 0,
        "last_viral_scout": None,
        "last_content_generated": None,
        "notes": [],
    }


def save(notes: dict) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


def add_task(task_id: str, description: str, status: str = "running") -> None:
    notes = load()
    notes["active_tasks"].append({
        "id": task_id,
        "description": description,
        "status": status,
        "started_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    })
    save(notes)
    log.info("Task added: %s — %s", task_id, description)


def update_task(task_id: str, status: str) -> None:
    notes = load()
    for task in notes["active_tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
    save(notes)


def mark_content_posted(platform: str, content_type: str, hook: str) -> None:
    notes = load()
    notes["content_posted"].append({
        "platform": platform,
        "type": content_type,
        "hook": hook[:80],
        "posted_at": datetime.now().isoformat(),
    })
    save(notes)


def mark_content_generated(output_path: str) -> None:
    notes = load()
    notes["last_content_generated"] = datetime.now().isoformat()
    notes["content_queued"].append({"path": output_path, "generated_at": datetime.now().isoformat()})
    save(notes)


def mark_viral_scout_done() -> None:
    notes = load()
    notes["last_viral_scout"] = datetime.now().isoformat()
    save(notes)


def add_note(text: str) -> None:
    notes = load()
    notes["notes"].append({"text": text, "at": datetime.now().isoformat()})
    save(notes)


def summary() -> str:
    notes = load()
    active = [t for t in notes["active_tasks"] if t["status"] == "running"]
    posted = len(notes["content_posted"])
    queued = len(notes["content_queued"])
    return (
        f"Date: {notes['date']} | "
        f"Active tasks: {len(active)} | "
        f"Content posted: {posted} | "
        f"Queued: {queued} | "
        f"Last scout: {notes['last_viral_scout'] or 'not yet'}"
    )
