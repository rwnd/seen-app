"""External API clients for reflection, images, and TTS."""

from seen.gateways.claude import generate_reflection
from seen.gateways.images import generate_comic_image
from seen.gateways.tts import generate_tts

__all__ = ["generate_reflection", "generate_comic_image", "generate_tts"]
