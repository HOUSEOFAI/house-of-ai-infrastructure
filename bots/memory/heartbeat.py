"""
Layer 3 — Heartbeat
Checks every 30 minutes that all your automations are alive.
If something died, it logs it and attempts a restart.
Mirrors Ray CFU's architecture exactly.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

MEMORY_DIR = Path(__file__).parent / "state"
HEARTBEAT_FILE = MEMORY_DIR / "heartbeat.json"
BOTS_DIR = Path(__file__).parent.parent


# ─── DEFINE YOUR MONITORED PROCESSES ──────────────────────────────────────────
# Add any background processes your business depends on.
# Each entry: name, how to check it's alive, how to restart it.
MONITORED_TASKS = [
    {
        "id": "daily_content_agent",
        "name": "Daily Content Agent",
        "description": "Generates today's marketing content every morning",
        "check_type": "file_exists_today",
        "check_target": str(BOTS_DIR / "daily-content-agent" / "output"),
        "restart_cmd": None,  # Scheduled — no restart needed mid-day
        "severity": "warn",
    },
    {
        "id": "knowledge_base",
        "name": "Knowledge Base",
        "description": "Nightly knowledge base rebuild",
        "check_type": "kb_fresh",
        "check_target": str(MEMORY_DIR / "knowledge_base.json"),
        "restart_cmd": [sys.executable, str(BOTS_DIR / "memory" / "rebuild_kb.py")],
        "severity": "critical",
    },
    {
        "id": "daily_notes",
        "name": "Daily Notes",
        "description": "Today's task and content tracking",
        "check_type": "file_exists_today",
        "check_target": str(MEMORY_DIR / "daily_notes.json"),
        "restart_cmd": None,
        "severity": "info",
    },
]
# ──────────────────────────────────────────────────────────────────────────────


def _check_file_exists_today(path: str) -> tuple[bool, str]:
    """Check if a file or directory has been updated today."""
    from datetime import date
    import os
    p = Path(path)
    if p.is_dir():
        today = date.today().isoformat()
        day_dir = p / today
        if day_dir.exists():
            return True, f"Today's output found at {day_dir}"
        return False, f"No output for today at {path}"
    if p.exists():
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        if mtime.date() == date.today():
            return True, f"File updated today at {mtime.strftime('%H:%M')}"
        return False, f"File last updated {mtime.strftime('%Y-%m-%d %H:%M')} — stale"
    return False, f"File not found: {path}"


def _check_kb_fresh(path: str) -> tuple[bool, str]:
    """Check if the knowledge base was rebuilt recently (within 25 hours)."""
    from datetime import date
    p = Path(path)
    if not p.exists():
        return False, "Knowledge base file not found"
    with open(p) as f:
        kb = json.load(f)
    rebuild_date = kb.get("rebuild_date")
    if rebuild_date == date.today().isoformat():
        return True, f"Rebuilt today at {kb.get('last_rebuilt', 'unknown time')}"
    return False, f"Last rebuilt: {rebuild_date or 'never'} — needs rebuild"


def _attempt_restart(task: dict) -> bool:
    """Try to restart a failed task."""
    if not task.get("restart_cmd"):
        log.info("[%s] No restart command configured", task["id"])
        return False
    try:
        log.info("[%s] Attempting restart...", task["id"])
        subprocess.Popen(task["restart_cmd"])
        return True
    except Exception as e:
        log.error("[%s] Restart failed: %s", task["id"], e)
        return False


def run_check() -> dict:
    """Run a full heartbeat check across all monitored tasks."""
    results = []
    any_critical = False

    for task in MONITORED_TASKS:
        check_type = task["check_type"]
        target = task["check_target"]

        if check_type == "file_exists_today":
            alive, message = _check_file_exists_today(target)
        elif check_type == "kb_fresh":
            alive, message = _check_kb_fresh(target)
        else:
            alive, message = False, f"Unknown check type: {check_type}"

        restarted = False
        if not alive and task["severity"] == "critical":
            any_critical = True
            restarted = _attempt_restart(task)

        result = {
            "id": task["id"],
            "name": task["name"],
            "alive": alive,
            "message": message,
            "severity": task["severity"],
            "restarted": restarted,
            "checked_at": datetime.now().isoformat(),
        }
        results.append(result)

        status_icon = "OK" if alive else ("RESTARTING" if restarted else "DEAD")
        log.info("[heartbeat] %-25s %s — %s", task["name"], status_icon, message)

    heartbeat = {
        "last_check": datetime.now().isoformat(),
        "all_healthy": all(r["alive"] for r in results),
        "any_critical": any_critical,
        "tasks": results,
    }

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEARTBEAT_FILE, "w") as f:
        json.dump(heartbeat, f, indent=2)

    return heartbeat


def status_summary() -> str:
    """One-line status summary for logging."""
    if not HEARTBEAT_FILE.exists():
        return "Heartbeat: never run"
    with open(HEARTBEAT_FILE) as f:
        hb = json.load(f)
    alive = sum(1 for t in hb["tasks"] if t["alive"])
    total = len(hb["tasks"])
    last = hb.get("last_check", "unknown")
    return f"Heartbeat: {alive}/{total} healthy | last check: {last}"
