"""Claude API for reflection generation."""

from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic

from seen.config import logger
from seen.prompts import build_reflection_prompt
from seen.utils import parse_claude_json


def generate_reflection(
    user_response: str,
    archetype: dict[str, Any],
    question_category: str,
    question_text: str,
    narrator: dict[str, Any],
) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = Anthropic(api_key=api_key)
    system = build_reflection_prompt(archetype, question_category, question_text, narrator)

    for attempt in range(2):
        user_msg = user_response if attempt == 0 else (
            user_response + "\n\nReturn ONLY the JSON object, nothing else."
        )
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1200,
            temperature=0.4,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text
        try:
            parsed = parse_claude_json(raw)
            for key in ("reflection", "the_line", "comic_panel_descriptions"):
                if key not in parsed:
                    raise ValueError(f"Missing key: {key}")
            if len(parsed["comic_panel_descriptions"]) != 4:
                raise ValueError("Expected 4 comic panel descriptions")
            return parsed
        except (json.JSONDecodeError, ValueError, IndexError) as exc:
            logger.warning("Claude JSON parse attempt %s failed: %s", attempt + 1, exc)
            if attempt == 1:
                raise RuntimeError("Could not parse reflection from Claude") from exc

    raise RuntimeError("Reflection generation failed")
