"""Application constants and paths."""

from __future__ import annotations

import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "data" / "results"
ARCHETYPES_PATH = BASE_DIR / "archetypes.json"
NARRATORS_PATH = BASE_DIR / "narrators.json"

QUESTION_LABELS = {
    "identity": "What I know about myself",
    "fear": "What I fear",
    "memory": "A memory that shaped me",
    "unsaid": "What I haven't said yet",
}

IMAGEN_MODELS = [
    "imagen-4.0-generate-001",
    "imagen-4.0-fast-generate-001",
    "imagen-3.0-generate-002",
]

logger = logging.getLogger("seen")


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)
