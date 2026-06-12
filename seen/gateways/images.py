"""Image generation via Gemini Imagen with OpenAI fallback."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from openai import OpenAI

from seen.config import IMAGEN_MODELS, logger


def generate_comic_image(prompt: str, dest: Path) -> None:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            last_err: Exception | None = None
            for model in IMAGEN_MODELS:
                try:
                    response = client.models.generate_images(
                        model=model,
                        prompt=prompt,
                        config=types.GenerateImagesConfig(number_of_images=1),
                    )
                    if response.generated_images:
                        dest.write_bytes(response.generated_images[0].image.image_bytes)
                        logger.info("Comic image generated with %s", model)
                        return
                except Exception as exc:
                    last_err = exc
                    logger.warning("Imagen model %s failed: %s", model, exc)
            if last_err:
                logger.warning("All Imagen models failed, trying OpenAI fallback")
        except ImportError as exc:
            logger.warning("google-genai not available: %s", exc)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise RuntimeError("No image API available (GEMINI_API_KEY or OPENAI_API_KEY)")

    client = OpenAI(api_key=openai_key)
    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt[:4000],
        size="1792x1024",
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    dest.write_bytes(base64.b64decode(result.data[0].b64_json))
    logger.info("Comic image generated with OpenAI DALL-E 3")
