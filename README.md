# CrowdWisdomTrading — AI Video Ad Generation Pipeline

A three-agent pipeline that researches competitor ads, generates data-grounded video ad scripts, and produces a production-ready brief for video generation — built with the `hermes-ai` framework, OpenRouter, Apify, and Tavily.

## What This Does

1. **Ads Manager Agent** — scrapes currently-running competitor ads from Meta's Ad Library (via Apify), then uses an LLM to extract pain points, hooks, and marketing concepts from real ad copy.
2. **Script Agent** — takes those pain points, researches them live via Tavily to confirm they're current and real, then generates 3 distinct video ad scripts (problem/solution, social proof, myth-busting) grounded in that research.
3. **Video Agent** — selects the strongest script and formats it into a clean, natural-language production brief, ready to hand off to [OpenMontage](https://github.com/calesthio/OpenMontage) for actual video rendering.

Each stage saves its output as human-readable JSON, so every step of the pipeline is inspectable and auditable.

## Architecture

```
Ads_project/
├── .env.example          # copy to .env and fill in your keys
├── config.py              # central config + environment loading
├── openrouter_patch.py    # patches hermes-ai to route through OpenRouter
├── main.py                 # runs all 3 agents end to end
├── agents/
│   ├── ads_manager_agent.py
│   ├── script_agent.py
│   └── video_agent.py
├── utils/
│   ├── llm_client.py
│   └── json_helpers.py
└── data/
    ├── raw_ads/            # scraped ad data (gitignored)
    ├── analyzed_ads/       # pain point / hook analysis (gitignored)
    ├── scripts/            # generated ad scripts (gitignored)
    └── videos/             # production briefs for OpenMontage (gitignored)
```

## Why `hermes-ai` + OpenRouter Needed a Patch

`hermes-ai` is built on top of `llama_index`, which hardcodes a whitelist of real OpenAI model names for context-window and function-calling validation. OpenRouter uses a different naming convention (`"openai/gpt-4o-mini"`, not `"gpt-4o-mini"`), which fails that whitelist check by default.

`openrouter_patch.py` fixes this by:
1. Setting `OPENAI_API_BASE` so requests route to OpenRouter instead of OpenAI directly
2. Registering the OpenRouter model slug in both `ALL_AVAILABLE_MODELS` and `CHAT_MODELS` (llama_index's internal whitelists) so context-window lookup and function-calling checks both pass

This must be imported **before** any `hermes.core.Agent` is created.

## Setup

**Requirements:** Python 3.11 or 3.12 (3.14 has wheel-availability issues with some dependencies at time of writing).

```bash
git clone https://github.com/PavanPreethamM/Video_Ads_Agent.git
cd Video_Ads_Agent

python3.12 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your real API keys:
#   OPENROUTER_API_KEY=
#   APIFY_TOKEN=
#   TAVILY_API_KEY=
```

## Running It

Run the full pipeline end to end:

```bash
python main.py
```

Or run each agent individually (useful for debugging or re-running just one stage):

```bash
python -m agents.ads_manager_agent
python -m agents.script_agent
python -m agents.video_agent
```

Each agent automatically picks up the most recent output from the previous stage (via timestamped filenames in `data/`), so they can be re-run independently once earlier stages have produced output.

## Output

- `data/analyzed_ads/analysis_*.json` — pain points, hooks, and marketing concepts extracted from real competitor ads
- `data/scripts/scripts_*.json` — 3 full video ad scripts, each with scene-by-scene voiceover, on-screen text, and a visual hook
- `data/videos/brief_*.txt` — a plain-language production brief for the selected script, formatted for handoff to OpenMontage

## Video Generation (OpenMontage)

OpenMontage isn't a callable API — it's designed to be operated by an AI coding assistant (Claude Code, Cursor, etc.) working inside a cloned copy of the repo, reading its own pipeline manifests and stage-director skills. `VideoAgent`'s job is to produce a clean, complete brief (see `data/videos/`) that can be handed directly to an AI assistant sitting inside a cloned OpenMontage repo to drive the actual render.

To render a video from a generated brief:
```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
# then open this folder in an AI coding assistant and provide the brief
```

A zero-key demo render (no API keys required, proves the render pipeline works) is available via:
```bash
make demo
```

## Known Limitations / Honest Notes

- `ScriptAgent`'s "unique data" section (CrowdWisdomTrading's proprietary performance stats/testimonials) is currently a placeholder — intended to be replaced with real data from the reference materials provided in the original brief.
- Video generation via OpenMontage, with zero paid API keys configured, is limited to Remotion-based motion graphics and local Piper TTS narration — no AI-generated video clips or images. This is a genuine, working, zero-cost path, not a mock.
- Meta's public Ad Library doesn't expose real spend/CTR data, so "best working ads" is approximated using how long an ad has remained active (advertisers tend to keep working ads live longer).

## Tech Stack

- **Framework:** `hermes-ai` (LlamaIndex-based agent orchestration)
- **LLM Provider:** OpenRouter
- **Ad Scraping:** Apify (`curious_coder/facebook-ads-library-scraper`)
- **Research:** Tavily
- **Video Rendering:** OpenMontage (Remotion + Piper TTS, zero-key path)
