"""Text-to-speech via OpenAI with Voicebox fallback."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from openai import OpenAI

from seen.config import logger


def generate_tts_openai(text: str, voice_id: str, dest: Path) -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice_id,
        input=text,
        speed=0.85,
    )
    dest.write_bytes(response.content)


def generate_tts_voicebox(text: str, voice_id: str, dest: Path) -> None:
    base = os.getenv("VOICEBOX_BASE_URL", "http://127.0.0.1:17493").rstrip("/")
    url = f"{base}/v1/audio/speech"
    payload = {
        "model": "tts-1-hd",
        "voice": voice_id,
        "input": text,
        "speed": 0.85,
        "response_format": "mp3",
    }
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        dest.write_bytes(resp.content)


def generate_tts(text: str, voice_id: str, dest: Path) -> None:
    try:
        generate_tts_openai(text, voice_id, dest)
        logger.info("TTS generated with OpenAI")
        return
    except Exception as exc:
        logger.warning("OpenAI TTS failed, trying Voicebox: %s", exc)

    try:
        generate_tts_voicebox(text, voice_id, dest)
        logger.info("TTS generated with Voicebox fallback")
    except Exception as exc:
        raise RuntimeError(f"TTS failed (OpenAI and Voicebox): {exc}") from exc
