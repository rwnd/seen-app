# Editing SEEN data files

Archetypes and narrators live as JSON at the project root. **Restart the server** after edits (or rely on `--reload` which picks up JSON on the next request).

## `narrators.json`

Add a new narrator by copying this block under `"narrators"` and giving it a unique slug key:

```json
"your_slug": {
  "name": "Display Name",
  "tone_label": "Short tone label",
  "tone_description": "One line shown on the picker tile (no celebrity name).",
  "voice_id": "onyx",
  "style_prompt": "Instructions for Claude's reflection voice.",
  "voice_bridge": "Short phrase before the_line in audio, e.g. 'Remember this' (ellipsis added automatically)",
  "voice_signoff": "Optional override for closing catchphrase in audio (defaults to signature_line)",
  "voice_include_signoff": true,
  "voicebox_profile": "Voicebox cloned profile name (for Voicebox primary TTS)",
  "initials": "DN",
  "avatar_color": "#1E3A5F",
  "signature_line": "The line shown on the result page."
}
```

| Field | Notes |
|-------|--------|
| `voice_id` | OpenAI TTS voice: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` (used when OpenAI is the provider) |
| `voicebox_profile` | Voicebox profile name for cloned celebrity voice |
| `voice_bridge` | Spoken pause phrase before **the line** in audio (e.g. `Alright... remember this`) |
| `voice_include_signoff` | If true, narrator `signature_line` is spoken after the line (when different) |
| `initials` | Shown in placeholder avatar (2–3 chars) |
| `avatar_color` | Hex background for placeholder circle |
| `photo` | Optional. If set, uses `static/images/narrators/{photo}` instead of initials |

**Optional photo:** drop `jobs.jpg` in `static/images/narrators/` and add `"photo": "jobs.jpg"`.

### Voice cloning (Voicebox) — better celebrity match

1. **Reference audio:** 45–90 seconds of clean speech per narrator — no music, room echo, or crowd noise. WAV preferred.
2. **Match the role:** Use clips where they speak slowly and reflectively (interviews, narration), not shouting or laughing.
3. **Multiple samples:** Add 2–3 samples per profile in Voicebox; re-clone if the first sample was short or noisy.
4. **Re-create profiles** after better samples — delete old profile, upload new reference, test with the narrator's `signature_line` first.
5. **Keep Voicebox primary** (`VOICE_PROVIDER_PRIMARY=voicebox`) — OpenAI voices are stylistic only, not likeness.
6. **Tune bridges:** Adjust `voice_bridge` / `voice_signoff` in this file so pacing feels natural for that voice.

Audio script order: `reflection` → bridge + `the_line` → optional `signature_line` sign-off.

## `archetypes.json`

Add a new archetype under `"archetypes"`:

```json
"your_slug": {
  "name": "Display Name",
  "category": "Leaders",
  "slug": "your_slug",
  "tagline": "One-line core drive summary",
  "core_wound": "The psychological tension",
  "description": "2–3 sentence description for Claude context.",
  "questions": {
    "identity": "What I know about myself — question text",
    "fear": "What I fear — question text",
    "memory": "A memory that shaped me — question text",
    "unsaid": "What I haven't said yet — question text"
  },
  "image_direction": "Symbolic scene for archetype card art direction",
  "image_style": "cinematic graphic novel, ink illustration, dramatic shadows, no speech bubbles, no text"
}
```

Categories (for `<optgroup>`): `Leaders`, `Advocates`, `Enthusiasts`, `Givers`, `Architects`, `Producers`, `Creators`, `Seekers`, `Fighters`, `Individualist`

**Archetype image:** run `python scripts/fetch_archetype_images.py` or add `static/images/archetypes/{slug}.png` manually.

## Validate after editing

```bash
.venv/bin/python -c "from main import load_archetypes, load_narrators; load_archetypes(); load_narrators(); print('OK')"
```
