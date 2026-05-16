"""
Heartbeat runner — checks all tasks every 30 minutes.

Schedule it:
  cron:         */30 * * * * /path/to/.venv/bin/python /path/to/run_heartbeat.py
  Make.com/n8n: Schedule trigger → every 30 minutes
"""

import logging
from heartbeat import run_check, status_summary

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    result = run_check()
    print(status_summary())
    if result["any_critical"]:
        print("CRITICAL: One or more critical tasks are down. Check logs.")
