# House of AI™ YouTube Knowledge Extraction Bot

Extracts buyer psychology, messaging frameworks, and content structure from
YouTube channels and synthesizes them into a **Marketing Engine Master Brief** —
the document that programs your AI marketing & content agent.

## Creators

| Creator | Role in Engine |
|---|---|
| **Chase Hughes** | Buyer psychology triggers, behavioral influence, compliance sequences |
| **Leanne Mosley (Rich Queen)** | Premium messaging, identity-based language, authority positioning |
| **Brooke Shelton** | Content structure, story arcs, hook formulas, content strategy |
| **Russell Brunson** | Funnel hacking, value ladder, offer stacking, hook-story-offer, webinar/VSL scripts |

## What It Produces

```
output/
  chase-hughes/
    raw_videos.json              # All video metadata
    transcripts/                 # Individual transcript files (upload to NotebookLM)
    video_analyses.json          # Claude-extracted frameworks per video
    knowledge_profile.json       # Synthesized creator knowledge profile
  leanne-mosley/
    ...
  brooke-shelton/
    ...
  marketing-engine-master-brief.md   # ← The main output: programs your AI agent
```

## Setup

### 1. Get API Keys

**YouTube Data API v3** (free, 10,000 units/day)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable "YouTube Data API v3"
3. Create credentials → API Key

**Anthropic API**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
# Run all three creators (recommended first run)
python bot.py

# Run one creator only
python bot.py --creator chase-hughes

# Limit videos per channel (good for testing)
python bot.py --max-videos 10

# Re-run Claude analysis without re-fetching YouTube data
python bot.py --skip-extraction
```

## Using the Output

### Marketing Engine Brief
The file `output/marketing-engine-master-brief.md` is the master document.
Use it as:
- The **system prompt** for your AI marketing agent
- The **knowledge base** loaded at the start of every content generation session

### Transcript Files
The `output/*/transcripts/` folders contain all raw transcripts as text files.
Upload these to:
- **Google NotebookLM** as knowledge sources
- A **vector database** (Pinecone, Chroma, Supabase) for RAG

### Knowledge Profiles
The `output/*/knowledge_profile.json` files contain structured markers:
- `psychology_markers` → embed in sales copy and email
- `content_markers` → use for content structure and hooks
- `funnel_architecture` → value ladder, offer stack, and funnel stage sequences
- `story_selling` → epiphany bridge, hook-story-offer, and VSL/webinar scripts
- `top_10_markers` → the highest-priority programming instructions
- `programming_instructions` → direct instructions for your AI agent

## Updating the Knowledge Base

Re-run anytime to pull new videos:

```bash
python bot.py --max-videos 20  # Only fetch 20 newest videos
```

To update analysis without re-fetching:

```bash
python bot.py --skip-extraction
```

---

*Part of the House of AI™ Infrastructure — AI Marketing Employee Knowledge System*
