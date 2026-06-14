"""Claude API for reflection generation."""

from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic

from seen.config import logger
from seen.prompts import build_reflection_prompt, validate_comic_page
from seen.settings import get_settings
from seen.utils import get_archetype_full, parse_claude_json


def _text_models() -> list[str]:
    settings = get_settings()
    models = [settings.text_model_primary]
    if settings.text_model_secondary:
        models.append(settings.text_model_secondary)
    return models


def _request_reflection(
    client: Anthropic,
    model: str,
    system: str,
    user_msg: str,
) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=3000,
        temperature=0.4,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text


def generate_reflection(
    user_response: str,
    archetype: dict[str, Any],
    question_category: str,
    question_text: str,
    narrator: dict[str, Any],
    *,
    narrator_slug: str,
) -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = Anthropic(api_key=api_key)
    archetype_full = get_archetype_full(archetype["name"])
    system = build_reflection_prompt(
        archetype,
        question_category,
        question_text,
        narrator,
        narrator_slug=narrator_slug,
        archetype_full=archetype_full,
    )
    models = _text_models()
    last_err: Exception | None = None

    for model in models:
        for attempt in range(2):
            user_msg = user_response if attempt == 0 else (
                user_response + "\n\nReturn ONLY the JSON object, nothing else."
            )
            try:
                raw = _request_reflection(client, model, system, user_msg)
                parsed = parse_claude_json(raw)
                validate_comic_page(parsed)
                logger.info("Reflection generated with %s", model)
                return parsed
            except (json.JSONDecodeError, ValueError, IndexError) as exc:
                logger.warning("%s JSON parse attempt %s failed: %s", model, attempt + 1, exc)
                last_err = exc
                if attempt == 1:
                    break
            except Exception as exc:
                logger.warning("%s reflection attempt failed: %s", model, exc)
                last_err = exc
                break

    raise RuntimeError("Could not generate reflection") from last_err
