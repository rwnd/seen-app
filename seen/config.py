"""Application constants and paths."""

from __future__ import annotations

import logging
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "data" / "results"
SAMPLES_DIR = BASE_DIR / "data" / "samples"
LOGS_DIR = BASE_DIR / "data" / "logs"
ARCHETYPES_PATH = BASE_DIR / "archetypes.json"
ARCHETYPES_FULL_PATH = BASE_DIR / "archetypes_fulldescription.json"
NARRATORS_PATH = BASE_DIR / "narrators.json"

QUESTION_LABELS = {
    "identity": "IDENTITY",
    "fear": "FEAR",
    "memory": "MEMORY",
    "unsaid": "UNSAID",
}

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("seen")


def setup_logging() -> None:
    """Configure console + file logging for the seen package."""
    level_name = os.getenv("SEEN_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    seen_logger = logging.getLogger("seen")
    seen_logger.setLevel(level)
    seen_logger.propagate = False

    if seen_logger.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    seen_logger.addHandler(console)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOGS_DIR / "seen.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    seen_logger.addHandler(file_handler)

    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)

    seen_logger.info("Logging initialized (level=%s, file=%s)", level_name, LOGS_DIR / "seen.log")
