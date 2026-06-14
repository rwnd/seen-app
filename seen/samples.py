"""Seed bundled sample reflections for first-time gallery setup."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from seen.config import RESULTS_DIR, SAMPLES_DIR, logger


def _has_gallery_results() -> bool:
    """True when at least one completed reflection exists in results."""
    for path in RESULTS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("status") != "error" and "the_line" in data:
            return True
    return False


def seed_sample_results_if_empty() -> int:
    """
    Copy bundled sample files into data/results when no gallery items exist.

    Returns the number of files copied.
    """
    if not SAMPLES_DIR.is_dir():
        return 0
    if _has_gallery_results():
        return 0

    copied = 0
    for src in sorted(SAMPLES_DIR.iterdir()):
        if not src.is_file() or src.name.startswith("."):
            continue
        dest = RESULTS_DIR / src.name
        if dest.exists():
            continue
        shutil.copy2(src, dest)
        copied += 1

    if copied:
        logger.info(
            "Seeded %d sample file(s) from %s into %s",
            copied,
            SAMPLES_DIR,
            RESULTS_DIR,
        )
    return copied
