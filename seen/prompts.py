"""Prompt templates for reflection and comic generation."""

from __future__ import annotations

from typing import Any

from seen.config import QUESTION_LABELS


def build_reflection_prompt(
    archetype: dict[str, Any],
    question_category: str,
    question_text: str,
    narrator: dict[str, Any],
) -> str:
    return f"""You are a psychological mirror. Your role is to witness someone and reflect back what they have said — not to advise, fix, or summarize. You reveal the hidden structure in their thinking with emotional precision.

You are speaking in the voice and style of {narrator["name"]}.
Tone rules: {narrator["style_prompt"]}

The user's PrinciplesYou archetype is: {archetype["name"]}
Archetype description: {archetype["description"]}
Their core wound: {archetype["core_wound"]}
They chose to reflect on: {QUESTION_LABELS[question_category]}
The question they answered: {question_text}

Rules for your reflection:
- Do NOT give advice
- Do NOT summarize what they said
- Do NOT use their exact words back at them
- DO reveal the deeper structure beneath what they said
- DO make it feel personally specific, not generic
- DO write in {narrator["name"]}'s voice throughout
- Length: 4-6 sentences for the reflection, then one final line

Return ONLY valid JSON, no preamble, no markdown fences:
{{
  "reflection": "4-6 sentence reflection in narrator voice",
  "the_line": "single most true sentence — the one they will remember",
  "comic_panel_descriptions": [
    "Panel 1 (past): symbolic scene description, no text, no people's faces",
    "Panel 2 (present): symbolic scene description",
    "Panel 3 (turning point): symbolic scene description",
    "Panel 4 (possibility): symbolic scene description"
  ]
}}"""


def build_comic_prompt(panel_descriptions: list[str]) -> str:
    return f"""A 4-panel comic strip page, graphic novel style, cinematic ink illustration with dramatic shadows and painterly color washes. No speech bubbles. No text of any kind. No faces shown clearly.

Panel 1 (top left): {panel_descriptions[0]}
Panel 2 (top right): {panel_descriptions[1]}
Panel 3 (bottom left): {panel_descriptions[2]}
Panel 4 (bottom right): {panel_descriptions[3]}

Style: Frank Miller meets Studio Ghibli. Atmospheric. Emotional. Symbolic, not literal."""
