# Architecture

SEEN is a small FastAPI app with a linear reflection pipeline and file-based storage.

## Request flow

```
Browser → routes.py → logic/reflection.py (background)
                              ↓
                    gateways/claude.py   → reflection JSON
                    gateways/images.py   → comic PNG
                    gateways/tts.py      → audio WAV/MP3
                              ↓
                    utils.py (save_result) → data/results/{uuid}.json
```

## Module responsibilities

| Module | Role |
|--------|------|
| `routes.py` | HTTP only — no business logic |
| `validation.py` | Form validation before queueing |
| `gallery.py` | Read/filter saved reflections |
| `logic/reflection.py` | Pipeline orchestration + step status |
| `prompts.py` | Claude system prompt + comic layout rules |
| `gateways/` | One file per external provider |
| `utils.py` | Config loaders, result CRUD, normalization |

## Progressive delivery

The pipeline saves after each step. The processing page redirects when text is ready; the result page holds behind a curtain until image + voice finish.

## Adding a narrator

1. Add entry to `narrators.json` with `voicebox_profile`
2. Create cloned profile in Voicebox
3. Test with `curl` against `/speak`
4. No code changes required

See [EDITING_DATA.md](EDITING_DATA.md) for the full schema.
