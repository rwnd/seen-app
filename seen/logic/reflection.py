"""Orchestrates the full reflection pipeline.

Runs sequentially in a background task:
  1. Claude → reflection + comic page brief
  2. Image gateway → portrait comic PNG
  3. TTS gateway → narrator audio

Each step updates `result.steps` and saves to disk so the UI can poll progress.
"""

from __future__ import annotations

from datetime import datetime, timezone

from seen.config import QUESTION_LABELS, RESULTS_DIR, logger
from seen.gateways import generate_comic_image, generate_reflection, generate_tts
from seen.gateways.tts import build_narrator_speech
from seen.prompts import build_comic_prompt
from seen.settings import get_settings
from seen.utils import (
    all_steps_terminal,
    get_question,
    initial_steps,
    reload_config,
    save_result,
    write_error,
)


def _base_result(
    uuid_str: str,
    archetype: dict,
    archetype_slug: str,
    question_category: str,
    question_text: str,
    user_response: str,
    narrator: dict,
    narrator_slug: str,
    *,
    enable_image: bool,
    enable_voice: bool,
) -> dict:
    return {
        "uuid": uuid_str,
        "status": "processing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "archetype_slug": archetype_slug,
        "archetype_name": archetype["name"],
        "archetype_category": archetype["category"],
        "question_category": question_category,
        "question_text": question_text,
        "user_response": user_response,
        "narrator_slug": narrator_slug,
        "narrator_name": narrator["name"],
        "narrator_tone_label": narrator.get("tone_label"),
        "narrator_initials": narrator.get("initials", narrator["name"][:2]),
        "narrator_avatar_color": narrator.get("avatar_color", "#1E3A5F"),
        "narrator_photo": narrator.get("photo"),
        "narrator_signature_line": narrator["signature_line"],
        "narrator_voice_id": narrator["voice_id"],
        "steps": initial_steps(
            enable_text=True,
            enable_image=enable_image,
            enable_voice=enable_voice,
        ),
        "audio_file": None,
        "comic_file": None,
        "has_audio": False,
        "has_comic": False,
    }


def _finalize(result: dict) -> None:
    result["has_audio"] = result["steps"]["voice"]["status"] == "ready"
    result["has_comic"] = result["steps"]["image"]["status"] == "ready"
    if all_steps_terminal(result):
        result["status"] = "ready"
    save_result(result)


def run_reflection(
    uuid_str: str,
    archetype_slug: str,
    question_category: str,
    user_response: str,
    narrator_slug: str,
) -> None:
    result: dict | None = None
    try:
        settings = get_settings()
        if not settings.enable_text:
            raise RuntimeError("Text generation is disabled (SEEN_ENABLE_TEXT=false)")

        _, archetypes, narrators = reload_config()
        archetype = archetypes.get(archetype_slug)
        narrator = narrators.get(narrator_slug)
        if not archetype or not narrator:
            raise RuntimeError("Invalid archetype or narrator")
        if question_category not in QUESTION_LABELS:
            raise RuntimeError("Invalid question category")

        question_text = get_question(archetype, question_category)["text"]
        result = _base_result(
            uuid_str,
            archetype,
            archetype_slug,
            question_category,
            question_text,
            user_response,
            narrator,
            narrator_slug,
            enable_image=settings.enable_image,
            enable_voice=settings.enable_voice,
        )
        save_result(result)

        logger.info("Starting text generation for %s", uuid_str)
        parsed = generate_reflection(
            user_response,
            archetype,
            question_category,
            question_text,
            narrator,
            narrator_slug=narrator_slug,
        )
        result["reflection"] = parsed["reflection"]
        result["the_line"] = parsed["the_line"]
        result["comic_page"] = parsed["comic_page"]
        result["steps"]["text"]["status"] = "ready"

        if settings.enable_image:
            result["steps"]["image"]["status"] = "generating"
        elif settings.enable_voice:
            result["steps"]["voice"]["status"] = "generating"

        save_result(result)
        logger.info("Text ready for %s", uuid_str)

        if settings.enable_image:
            comic_file = f"{uuid_str}_comic.png"
            logger.info("Starting Your Page generation for %s", uuid_str)
            try:
                generate_comic_image(
                    build_comic_prompt(parsed["comic_page"]),
                    RESULTS_DIR / comic_file,
                )
                result["comic_file"] = comic_file
                result["steps"]["image"]["status"] = "ready"
                logger.info("Comic image ready for %s", uuid_str)
            except Exception as exc:
                logger.warning("Comic image failed for %s: %s", uuid_str, exc)
                result["steps"]["image"]["status"] = "error"
                result["steps"]["image"]["error"] = str(exc)

            if settings.enable_voice and result["steps"]["voice"]["status"] == "pending":
                result["steps"]["voice"]["status"] = "generating"
            save_result(result)

        if settings.enable_voice:
            if result["steps"]["voice"]["status"] == "pending":
                result["steps"]["voice"]["status"] = "generating"
                save_result(result)

            logger.info("Starting voice generation for %s", uuid_str)
            speech_text = build_narrator_speech(
                parsed["reflection"],
                parsed["the_line"],
                narrator,
            )
            audio_dest = RESULTS_DIR / f"{uuid_str}_audio.mp3"
            try:
                result["audio_file"] = generate_tts(
                    speech_text,
                    narrator["voice_id"],
                    audio_dest,
                    voicebox_profile=narrator.get("voicebox_profile"),
                )
                result["steps"]["voice"]["status"] = "ready"
                logger.info("Voice ready for %s", uuid_str)
            except Exception as exc:
                logger.warning("Voice failed for %s: %s", uuid_str, exc)
                result["steps"]["voice"]["status"] = "error"
                result["steps"]["voice"]["error"] = str(exc)
            save_result(result)

        _finalize(result)
        logger.info("Reflection complete: %s", uuid_str)
    except Exception as exc:
        logger.exception("Reflection failed for %s", uuid_str)
        if result and result.get("reflection"):
            result["steps"]["text"]["status"] = "ready"
            for step in ("image", "voice"):
                if result["steps"][step]["status"] in {"pending", "generating"}:
                    result["steps"][step]["status"] = "error"
                    result["steps"][step]["error"] = str(exc)
            _finalize(result)
        else:
            write_error(uuid_str, str(exc))
