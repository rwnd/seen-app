"""Runtime settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_list(name: str, default: str = "") -> list[str]:
    raw = _env_str(name, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    enable_text: bool
    enable_voice: bool
    enable_image: bool

    text_model_primary: str
    text_model_secondary: str

    voice_provider_primary: str
    voice_provider_secondary: str
    voice_model_primary: str
    voice_model_secondary: str

    image_provider_primary: str
    image_provider_secondary: str
    image_model_primary: str
    image_model_secondary: str
    image_gemini_fallback_models: list[str]


def get_settings() -> Settings:
    return Settings(
        enable_text=_env_bool("SEEN_ENABLE_TEXT", True),
        enable_voice=_env_bool("SEEN_ENABLE_VOICE", False),
        enable_image=_env_bool("SEEN_ENABLE_IMAGE", False),
        text_model_primary=_env_str("TEXT_MODEL_PRIMARY", "claude-sonnet-4-20250514"),
        text_model_secondary=_env_str("TEXT_MODEL_SECONDARY"),
        voice_provider_primary=_env_str("VOICE_PROVIDER_PRIMARY", "openai"),
        voice_provider_secondary=_env_str("VOICE_PROVIDER_SECONDARY", "voicebox"),
        voice_model_primary=_env_str("VOICE_MODEL_PRIMARY", "gpt-4o-mini-tts"),
        voice_model_secondary=_env_str("VOICE_MODEL_SECONDARY", "tts-1"),
        image_provider_primary=_env_str("IMAGE_PROVIDER_PRIMARY", "gemini"),
        image_provider_secondary=_env_str("IMAGE_PROVIDER_SECONDARY", "openai"),
        image_model_primary=_env_str("IMAGE_MODEL_PRIMARY", "imagen-4.0-generate-001"),
        image_model_secondary=_env_str("IMAGE_MODEL_SECONDARY", "dall-e-3"),
        image_gemini_fallback_models=_env_list(
            "IMAGE_GEMINI_FALLBACK_MODELS",
            "imagen-4.0-fast-generate-001,imagen-3.0-generate-002",
        ),
    )
