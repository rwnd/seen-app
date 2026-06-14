"""Image generation via configured primary/secondary providers."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from openai import OpenAI

from seen.config import logger
from seen.settings import get_settings


def _gemini_models() -> list[str]:
    settings = get_settings()
    models = [settings.image_model_primary]
    models.extend(settings.image_gemini_fallback_models)
    seen: set[str] = set()
    ordered: list[str] = []
    for model in models:
        if model and model not in seen:
            seen.add(model)
            ordered.append(model)
    return ordered


def _generate_with_gemini(prompt: str, dest: Path) -> None:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=gemini_key)
    last_err: Exception | None = None
    for model in _gemini_models():
        try:
            response = client.models.generate_images(
                model=model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="3:4",
                ),
            )
            if response.generated_images:
                dest.write_bytes(response.generated_images[0].image.image_bytes)
                logger.info("Comic image generated with Gemini %s", model)
                return
        except Exception as exc:
            last_err = exc
            logger.warning("Gemini model %s failed: %s", model, exc)

    raise RuntimeError(f"Gemini image generation failed: {last_err}") from last_err


def _generate_with_openai(prompt: str, dest: Path) -> None:
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    settings = get_settings()
    client = OpenAI(api_key=openai_key)
    result = client.images.generate(
        model=settings.image_model_secondary,
        prompt=prompt[:4000],
        size="1024x1792",
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    dest.write_bytes(base64.b64decode(result.data[0].b64_json))
    logger.info("Comic image generated with OpenAI %s", settings.image_model_secondary)


def generate_comic_image(prompt: str, dest: Path) -> None:
    settings = get_settings()
    providers = [
        settings.image_provider_primary,
        settings.image_provider_secondary,
    ]
    seen_providers: set[str] = set()
    last_err: Exception | None = None

    for provider in providers:
        provider = provider.lower()
        if not provider or provider in seen_providers:
            continue
        seen_providers.add(provider)

        try:
            if provider == "gemini":
                _generate_with_gemini(prompt, dest)
                return
            if provider == "openai":
                _generate_with_openai(prompt, dest)
                return
            raise RuntimeError(f"Unknown image provider: {provider}")
        except Exception as exc:
            last_err = exc
            logger.warning("Image provider %s failed: %s", provider, exc)

    raise RuntimeError(f"Image generation failed: {last_err}") from last_err
