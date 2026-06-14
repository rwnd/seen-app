"""Text-to-speech via configured primary/secondary providers."""

from __future__ import annotations

import os
import time
from pathlib import Path

import httpx
from openai import OpenAI

from seen.config import logger
from seen.settings import get_settings

VOICEBOX_POLL_INTERVAL = 2.0
VOICEBOX_TIMEOUT = 300.0


def _normalize_line(text: str) -> str:
    return " ".join(text.lower().split())


def build_narrator_speech(
    reflection: str,
    the_line: str,
    narrator: dict,
) -> str:
    """Assemble TTS script: reflection → bridge pause → the line → optional sign-off."""
    parts: list[str] = [reflection.strip()]

    bridge = (narrator.get("voice_bridge") or "Remember this").strip().rstrip(".")
    parts.append(f"{bridge}... {the_line.strip()}")

    if narrator.get("voice_include_signoff", True):
        signoff = (narrator.get("voice_signoff") or narrator.get("signature_line") or "").strip()
        if signoff and _normalize_line(signoff) != _normalize_line(the_line):
            parts.append(signoff)

    return "\n\n".join(parts)


def _openai_models() -> list[str]:
    settings = get_settings()
    models = [settings.voice_model_primary]
    if settings.voice_model_secondary:
        models.append(settings.voice_model_secondary)
    seen: set[str] = set()
    ordered: list[str] = []
    for model in models:
        if model and model not in seen:
            seen.add(model)
            ordered.append(model)
    return ordered


def generate_tts_openai(text: str, voice_id: str, dest: Path) -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)
    last_err: Exception | None = None
    for model in _openai_models():
        try:
            response = client.audio.speech.create(
                model=model,
                voice=voice_id,
                input=text,
                speed=0.85,
            )
            dest.write_bytes(response.content)
            logger.info("TTS generated with OpenAI %s", model)
            return
        except Exception as exc:
            last_err = exc
            logger.warning("OpenAI TTS model %s failed: %s", model, exc)

    raise RuntimeError(f"OpenAI TTS failed: {last_err}") from last_err


def _voicebox_profile(voice_id: str, voicebox_profile: str | None = None) -> str:
    if voicebox_profile:
        return voicebox_profile.strip()
    profile = os.getenv("VOICEBOX_PROFILE_ID", "").strip()
    return profile or voice_id


def _wait_for_voicebox_generation(client: httpx.Client, base: str, generation_id: str) -> None:
    deadline = time.monotonic() + VOICEBOX_TIMEOUT
    while time.monotonic() < deadline:
        resp = client.get(f"{base}/history/{generation_id}")
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        if status == "completed":
            return
        if status == "failed":
            raise RuntimeError(data.get("error") or "Voicebox generation failed")
        time.sleep(VOICEBOX_POLL_INTERVAL)

    raise RuntimeError("Voicebox generation timed out")


def generate_tts_voicebox(
    text: str,
    voice_id: str,
    dest: Path,
    *,
    voicebox_profile: str | None = None,
) -> str:
    base = os.getenv("VOICEBOX_BASE_URL", "http://127.0.0.1:17493").rstrip("/")
    profile = _voicebox_profile(voice_id, voicebox_profile)
    payload = {"text": text, "profile": profile, "language": "en"}

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(f"{base}/speak", json=payload)
        resp.raise_for_status()
        generation_id = resp.json()["id"]
        _wait_for_voicebox_generation(client, base, generation_id)

        audio_resp = client.get(f"{base}/audio/{generation_id}")
        audio_resp.raise_for_status()
        audio_bytes = audio_resp.content

    if audio_bytes[:4] == b"RIFF" and dest.suffix.lower() == ".mp3":
        dest = dest.with_suffix(".wav")

    dest.write_bytes(audio_bytes)
    return dest.name


def generate_tts(
    text: str,
    voice_id: str,
    dest: Path,
    *,
    voicebox_profile: str | None = None,
) -> str:
    settings = get_settings()
    providers = [
        settings.voice_provider_primary,
        settings.voice_provider_secondary,
    ]
    seen_providers: set[str] = set()
    last_err: Exception | None = None

    for provider in providers:
        provider = provider.lower()
        if not provider or provider in seen_providers:
            continue
        seen_providers.add(provider)

        try:
            if provider == "openai":
                generate_tts_openai(text, voice_id, dest)
                return dest.name
            if provider == "voicebox":
                filename = generate_tts_voicebox(
                    text,
                    voice_id,
                    dest,
                    voicebox_profile=voicebox_profile,
                )
                logger.info("TTS generated with Voicebox")
                return filename
            raise RuntimeError(f"Unknown voice provider: {provider}")
        except Exception as exc:
            last_err = exc
            logger.warning("Voice provider %s failed: %s", provider, exc)

    raise RuntimeError(f"TTS failed: {last_err}") from last_err
