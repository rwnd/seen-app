"""Orchestrates the full reflection pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from seen.config import QUESTION_LABELS, RESULTS_DIR, logger
from seen.gateways import generate_comic_image, generate_reflection, generate_tts
from seen.prompts import build_comic_prompt
from seen.utils import reload_config, result_path, write_error


def run_reflection(
    uuid_str: str,
    archetype_slug: str,
    question_category: str,
    user_response: str,
    narrator_slug: str,
) -> None:
    try:
        _, archetypes, narrators = reload_config()
        archetype = archetypes.get(archetype_slug)
        narrator = narrators.get(narrator_slug)
        if not archetype or not narrator:
            raise RuntimeError("Invalid archetype or narrator")
        if question_category not in QUESTION_LABELS:
            raise RuntimeError("Invalid question category")

        question_text = archetype["questions"][question_category]
        parsed = generate_reflection(
            user_response, archetype, question_category, question_text, narrator
        )

        comic_file = f"{uuid_str}_comic.png"
        audio_file = f"{uuid_str}_audio.mp3"
        generate_comic_image(
            build_comic_prompt(parsed["comic_panel_descriptions"]),
            RESULTS_DIR / comic_file,
        )

        speech_text = f"{parsed['reflection']}\n\n{parsed['the_line']}"
        generate_tts(speech_text, narrator["voice_id"], RESULTS_DIR / audio_file)

        result = {
            "uuid": uuid_str,
            "status": "ready",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "archetype_slug": archetype_slug,
            "archetype_name": archetype["name"],
            "archetype_category": archetype["category"],
            "question_category": question_category,
            "question_text": question_text,
            "user_response": user_response,
            "narrator_slug": narrator_slug,
            "narrator_name": narrator["name"],
            "narrator_initials": narrator.get("initials", narrator["name"][:2]),
            "narrator_avatar_color": narrator.get("avatar_color", "#1E3A5F"),
            "narrator_photo": narrator.get("photo"),
            "narrator_signature_line": narrator["signature_line"],
            "reflection": parsed["reflection"],
            "the_line": parsed["the_line"],
            "comic_panel_descriptions": parsed["comic_panel_descriptions"],
            "audio_file": audio_file,
            "comic_file": comic_file,
        }
        result_path(uuid_str).write_text(json.dumps(result, indent=2))
        logger.info("Reflection complete: %s", uuid_str)
    except Exception as exc:
        logger.exception("Reflection failed for %s", uuid_str)
        write_error(uuid_str, str(exc))
