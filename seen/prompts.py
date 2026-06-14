"""Prompt templates for reflection and comic page generation."""

from __future__ import annotations

from typing import Any

from seen.config import QUESTION_LABELS

NARRATOR_VISUAL_PERSONAS: dict[str, str] = {
    "mcconaughey": (
        "A weathered traveler sitting by a campfire, warm amber light on their face, "
        "relaxed posture, symbolic guide figure — evocative of Matthew McConaughey's "
        "presence but not a literal celebrity portrait"
    ),
    "miranda": (
        "A sharp-suited figure at a tall window, back partially to the reader, "
        "reflection visible in the glass, ice-blue city light — Miranda Priestly's "
        "archetype as visual persona, not a literal likeness"
    ),
    "tyson": (
        "An animated science communicator mid-gesture, starfield or cosmos subtly "
        "behind them, warm expressive eyes — Neil deGrasse Tyson's archetype as "
        "visual persona, not a literal celebrity portrait"
    ),
    "oprah": (
        "A warm, composed figure in soft light, leaning in with full attention, "
        "studio or intimate interview setting — Oprah Winfrey's archetype as "
        "visual persona, not a literal celebrity portrait"
    ),
    "jobs": (
        "A minimalist figure in black on an empty stage, single harsh spotlight, "
        "perfect stillness — Steve Jobs as visual archetype, not a literal likeness"
    ),
    "yoda": (
        "A small ancient sage in a misty forest, luminous eyes, robes blending with "
        "roots and moss — Yoda as symbolic guide figure"
    ),
}

PANEL_SIZE_LABELS = {
    "full_width": "FULL WIDTH",
    "half": "HALF WIDTH",
    "third": "THIRD WIDTH",
    "quarter": "QUARTER WIDTH",
}

VALID_PANEL_SIZES = frozenset(PANEL_SIZE_LABELS)

SIZE_ALIASES: dict[str, str] = {
    "full_width": "full_width",
    "full-width": "full_width",
    "fullwidth": "full_width",
    "full": "full_width",
    "large": "full_width",
    "wide": "full_width",
    "half": "half",
    "half_width": "half",
    "half-width": "half",
    "medium": "half",
    "third": "third",
    "one_third": "third",
    "one-third": "third",
    "small": "third",
    "quarter": "quarter",
    "one_quarter": "quarter",
    "one-quarter": "quarter",
    "tiny": "quarter",
}


def normalize_panel_size(size: Any) -> str:
    if not size:
        return "half"
    key = str(size).strip().lower().replace(" ", "_")
    if key in VALID_PANEL_SIZES:
        return key
    return SIZE_ALIASES.get(key, "half")


COMIC_PANEL_COUNT = 4

# Fixed 4-panel layout: fewer panels and fewer text boxes for image-model legibility.
FIXED_PANEL_LAYOUT = (
    {"size": "full_width", "has_caption": True, "has_narration": False},
    {"size": "half", "has_caption": False, "has_narration": True},
    {"size": "half", "has_caption": False, "has_narration": False},
    {"size": "full_width", "has_caption": True, "has_narration": False},
)


def normalize_comic_page(page: dict[str, Any]) -> None:
    panels = page["panels"]
    for index, panel in enumerate(panels):
        layout = FIXED_PANEL_LAYOUT[index]
        panel["size"] = layout["size"]
        panel["is_climax"] = index == len(panels) - 1
        if not layout["has_caption"]:
            panel["caption"] = ""
        if not layout["has_narration"]:
            panel["narration"] = ""


def narrator_visual_persona(narrator_slug: str, narrator: dict[str, Any]) -> str:
    if narrator_slug in NARRATOR_VISUAL_PERSONAS:
        return NARRATOR_VISUAL_PERSONAS[narrator_slug]
    return (
        f"A distinct symbolic guide figure embodying {narrator['name']}'s tone "
        f"({narrator['tone_label']}) — visual archetype, not a celebrity likeness"
    )


def _format_archetype_context(
    archetype: dict[str, Any],
    archetype_full: dict[str, Any] | None,
) -> str:
    lines = [
        f"The user's PrinciplesYou archetype is: {archetype['name']}",
        f"Category: {archetype['category']}",
    ]
    if archetype_full:
        if archetype_full.get("tagline"):
            lines.append(f"Archetype summary: {archetype_full['tagline']}")
        if archetype_full.get("overview"):
            lines.append(f"Archetype overview: {archetype_full['overview']}")
        growth = archetype_full.get("growth_opportunities") or []
        if growth:
            lines.append("Typical growth edges: " + "; ".join(growth))
        talents = archetype_full.get("talents") or []
        if talents:
            lines.append("Natural talents: " + "; ".join(talents))
    else:
        lines.append(f"Archetype description: {archetype['description']}")
    lines.append(f"Their core wound: {archetype['core_wound']}")
    if archetype.get("image_direction"):
        lines.append(f"Visual seed for their archetype character: {archetype['image_direction']}")
    return "\n".join(lines)


def build_reflection_prompt(
    archetype: dict[str, Any],
    question_category: str,
    question_text: str,
    narrator: dict[str, Any],
    *,
    narrator_slug: str,
    archetype_full: dict[str, Any] | None = None,
) -> str:
    narrator_persona = narrator_visual_persona(narrator_slug, narrator)
    archetype_context = _format_archetype_context(archetype, archetype_full)
    return f"""You are a psychological mirror. Your role is to witness someone and reflect back what they have said — not to advise, fix, or summarize. You reveal the hidden structure in their thinking with emotional precision.

You are speaking in the voice and style of {narrator["name"]}.
Tone rules: {narrator["style_prompt"]}

{archetype_context}
They chose to reflect on: {QUESTION_LABELS[question_category]}
The question they answered: {question_text}

Rules for your reflection:
- Do NOT give advice
- Do NOT summarize what they said
- Do NOT use their exact words back at them
- DO reveal the deeper structure beneath what they said
- DO connect their answer to specific archetype patterns — growth edges, talents, and core wound — only where genuinely visible in what they wrote
- DO make it feel personally specific to this person and this archetype, not a generic horoscope
- DO write in {narrator["name"]}'s voice throughout
- Length: 4-6 sentences for the reflection, then one final line

Comic page rules:
- Design exactly 4 panels in a fixed layout (portrait page, top to bottom):
  1. FULL WIDTH — establishing shot of the user's symbolic world. Caption only (max 6 words).
  2. HALF WIDTH — narrator guide appears here. Speech bubble only (max 8 words). No caption.
  3. HALF WIDTH — visual only. No caption, no speech bubble.
  4. FULL WIDTH — climax. Protagonist transformed. Caption only (max 6 words).
- Each panel advances the emotional arc through scene composition, symbolism, body language, and environment
- The protagonist is the user's archetype as their shadow/transcended self — NOT a generic superhero, no capes. They have either fully embraced their wound or transcended it. Emotionally symbolic, not literal.
- The narrator guide is this visual persona (use exactly): {narrator_persona}
- The protagonist NEVER speaks — they ARE the reader
- Panel 4 is the climax (is_climax: true)
- Panel scene descriptions must be specific and cinematic (what we see, lighting, composition)
- Captions and narration must be short, punchy phrases — not full sentences

Return ONLY valid JSON, no preamble, no markdown fences:
{{
  "reflection": "4-6 sentence reflection in narrator voice",
  "the_line": "single most true sentence — the one they will remember",
  "comic_page": {{
    "archetype_character": "visual description of protagonist — same clothing and silhouette in every panel",
    "narrator_character": "visual description of narrator guide — same look in every panel they appear",
    "setting": "symbolic world this story takes place in",
    "panels": [
      {{
        "size": "full_width",
        "scene": "specific cinematic visual — what is shown, lighting, composition, symbolism",
        "caption": "only on panels 1 and 4, max 6 words; empty string on panels 2-3",
        "narration": "only on panel 2, max 8 words in narrator voice; empty string elsewhere",
        "is_climax": false
      }}
    ]
  }}
}}

Return exactly 4 panels. Panel size must be exactly one of: "full_width", "half"."""


def validate_comic_page(parsed: dict[str, Any]) -> None:
    for key in ("reflection", "the_line", "comic_page"):
        if key not in parsed:
            raise ValueError(f"Missing key: {key}")

    page = parsed["comic_page"]
    for key in (
        "archetype_character",
        "narrator_character",
        "setting",
        "panels",
    ):
        if key not in page:
            raise ValueError(f"Missing comic_page key: {key}")

    panels = page["panels"]
    if not isinstance(panels, list) or len(panels) != COMIC_PANEL_COUNT:
        raise ValueError(f"Expected exactly {COMIC_PANEL_COUNT} comic panels")

    normalize_comic_page(page)

    for index, panel in enumerate(panels, start=1):
        layout = FIXED_PANEL_LAYOUT[index - 1]
        if panel.get("size") != layout["size"]:
            raise ValueError(f"Panel {index} must be {layout['size']}")
        if not panel.get("scene"):
            raise ValueError(f"Panel {index} missing scene")
        caption = str(panel.get("caption", "")).strip()
        narration = str(panel.get("narration", "")).strip()
        if layout["has_caption"] and not caption:
            raise ValueError(f"Panel {index} missing caption")
        if not layout["has_caption"] and caption:
            panel["caption"] = ""
        if layout["has_narration"] and not narration:
            raise ValueError(f"Panel {index} missing narration")
        if not layout["has_narration"] and narration:
            panel["narration"] = ""


def _panel_layout_line(
    index: int,
    panel: dict[str, Any],
) -> str:
    size = PANEL_SIZE_LABELS.get(panel["size"], panel["size"].upper())
    climax = " — CLIMAX PANEL" if panel.get("is_climax") else ""
    caption = panel.get("caption", "").strip()
    narration = panel.get("narration", "").strip()
    text_parts = []
    if caption:
        text_parts.append(f'CAPTION BOX: "{caption}"')
    if narration:
        text_parts.append(f'NARRATOR SPEECH BUBBLE: "{narration}"')
    text_line = f"\n  {' | '.join(text_parts)}" if text_parts else ""
    return f"PANEL {index} ({size}{climax}): {panel['scene']}{text_line}"


def build_comic_prompt(comic_page: dict[str, Any]) -> str:
    panels = comic_page["panels"]
    panel_blocks = "\n\n".join(
        _panel_layout_line(index, panel)
        for index, panel in enumerate(panels, start=1)
    )

    return f"""A single portrait comic book PAGE with exactly 4 panels in a fixed layout.
Orientation: portrait, roughly 3:4 aspect ratio (taller than wide).
Layout top to bottom: Panel 1 full width, Panels 2-3 side by side (half width each), Panel 4 full width.

CHARACTERS — draw with identical clothing, silhouette, and features every time they appear:
- Protagonist: {comic_page["archetype_character"]}
  The protagonist never speaks. They are the reader's symbolic self.
- Guide figure: {comic_page["narrator_character"]}
  The guide speaks only on Panel 2 via one speech bubble.

SETTING: {comic_page["setting"]}

PAGE LAYOUT (visual scenes with text):
{panel_blocks}

TEXT IN THE IMAGE — CRITICAL (only 3 text elements total):
- Panel 1: one caption box with the exact caption text, character-for-character
- Panel 2: one speech bubble with the exact narration text, character-for-character
- Panel 3: no text at all
- Panel 4: one caption box with the exact caption text, character-for-character
- Use clean comic-book lettering — bold sans-serif, high contrast
- Do NOT add any other text, labels, titles, watermarks, or page numbers anywhere

ART STYLE: Graphic novel. Cinematic ink illustration with dramatic shadows and painterly color washes. Frank Miller panel structure, Moebius atmosphere. Symbolic, emotionally charged, not photorealistic. Celebrity likenesses avoided — visual archetypes only."""
