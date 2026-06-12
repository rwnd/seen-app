# SEEN

A personalized reflection experience: archetype + honest answer + narrator voice → AI reflection, comic strip, and audio.

## Setup

```bash
cd ~/Documents/Github/seen-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
python scripts/fetch_archetype_images.py   # optional, one-time
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000

## Environment

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Reflection text (Claude) |
| `OPENAI_API_KEY` | TTS primary + comic image fallback |
| `GEMINI_API_KEY` | Comic image primary (Imagen 4 → 3) |
| `VOICEBOX_BASE_URL` | TTS fallback (default `http://127.0.0.1:17493`) |

**TTS order:** OpenAI `tts-1-hd` first (fast), Voicebox `/v1/audio/speech` if OpenAI fails.

## Editing data

- **Archetypes:** edit `archetypes.json` directly, or bulk-regenerate with `python scripts/generate_archetypes.py`
- **Narrators:** edit `narrators.json` — copy an existing block, change the slug key
- Full schema: [docs/EDITING_DATA.md](docs/EDITING_DATA.md)

JSON is reloaded on each request — no restart needed with `--reload`.

## Validate config

```bash
.venv/bin/python -c "from main import load_archetypes, load_narrators; load_archetypes(); load_narrators(); print('OK')"
```
