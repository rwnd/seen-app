"""Shared helpers for JSON I/O and result storage."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from seen.config import ARCHETYPES_PATH, NARRATORS_PATH, RESULTS_DIR


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_archetypes() -> tuple[list[str], dict[str, Any]]:
    data = load_json(ARCHETYPES_PATH)
    categories = data.get("categories") or sorted(
        {a["category"] for a in data["archetypes"].values()}
    )
    return categories, data["archetypes"]


def load_narrators() -> dict[str, Any]:
    data = load_json(NARRATORS_PATH)
    return data.get("narrators", data)


def reload_config() -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    """Reload JSON config on each request (easy editing without restart)."""
    categories, archetypes = load_archetypes()
    narrators = load_narrators()
    return categories, archetypes, narrators


def result_path(uuid_str: str) -> Path:
    return RESULTS_DIR / f"{uuid_str}.json"


def write_error(uuid_str: str, message: str) -> None:
    result_path(uuid_str).write_text(
        json.dumps({"uuid": uuid_str, "status": "error", "message": message}, indent=2)
    )


def parse_claude_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)
