"""
Nightly knowledge base rebuild — run this at 2am every night.

Schedule it:
  cron:           0 2 * * * /path/to/.venv/bin/python /path/to/rebuild_kb.py
  Make.com/n8n:   HTTP trigger → run this script at 2am
"""

import os
import logging
from dotenv import load_dotenv
from pathlib import Path
import anthropic

load_dotenv(Path(__file__).parent.parent / "daily-content-agent" / ".env")
load_dotenv(Path(__file__).parent.parent / "youtube-knowledge-extractor" / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from knowledge_base import rebuild

if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=api_key)
    kb = rebuild(client)
    log.info("Done. Rebuilt with %d expert profiles.", len(kb.get("expert_profiles_loaded", [])))
