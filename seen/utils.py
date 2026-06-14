"""Shared helpers for config loading, result storage, and normalization."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from seen.config import ARCHETYPES_FULL_PATH, ARCHETYPES_PATH, NARRATORS_PATH, QUESTION_LABELS, RESULTS_DIR

TERMINAL_STEP_STATUSES = {"ready", "error", "skipped"}
RETRY_INPUT_FIELDS = (
    "archetype_slug",
    "question_category",
    "user_response",
    "narrator_slug",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_archetypes() -> tuple[list[str], dict[str, Any]]:
    data = load_json(ARCHETYPES_PATH)
    categories = data.get("categories") or sorted(
        {a["category"] for a in data["archetypes"].values()}
    )
    return categories, data["archetypes"]


def get_question(archetype: dict[str, Any], category: str) -> dict[str, Any]:
    """Return question text and starters for a category."""
    raw = archetype["questions"][category]
    if isinstance(raw, str):
        return {"text": raw, "starters": []}
    return raw


def load_narrators() -> dict[str, Any]:
    data = load_json(NARRATORS_PATH)
    return data.get("narrators", data)


def get_archetype_full(name: str) -> dict[str, Any] | None:
    """Return PrinciplesYou full profile for an archetype by display name."""
    data = load_json(ARCHETYPES_FULL_PATH)
    target = name.strip().lower()
    for category, items in data.get("archetypes", {}).items():
        for archetype_name, entry in items.items():
            if archetype_name.strip().lower() == target:
                return {**entry, "category": category}
    return None


def reload_config() -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    """Reload JSON config on each request (easy editing without restart)."""
    categories, archetypes = load_archetypes()
    narrators = load_narrators()
    return categories, archetypes, narrators


def result_path(uuid_str: str) -> Path:
    return RESULTS_DIR / f"{uuid_str}.json"


def read_result(uuid_str: str) -> dict[str, Any] | None:
    path = result_path(uuid_str)
    if not path.exists():
        return None
    return load_json(path)


def save_result(result: dict[str, Any]) -> None:
    result_path(result["uuid"]).write_text(json.dumps(result, indent=2))


def write_pending(
    uuid_str: str,
    archetype_slug: str,
    question_category: str,
    user_response: str,
    narrator_slug: str,
) -> None:
    save_result({
        "uuid": uuid_str,
        "status": "pending",
        "archetype_slug": archetype_slug,
        "question_category": question_category,
        "user_response": user_response,
        "narrator_slug": narrator_slug,
    })


def can_retry(data: dict[str, Any]) -> bool:
    return all(data.get(field) for field in RETRY_INPUT_FIELDS)


def write_error(uuid_str: str, message: str) -> None:
    existing = read_result(uuid_str) or {}
    retry_data = {
        field: existing[field]
        for field in RETRY_INPUT_FIELDS
        if field in existing
    }
    save_result({
        **retry_data,
        "uuid": uuid_str,
        "status": "error",
        "message": message,
        "steps": {
            "text": {"status": "error", "error": message},
            "image": {"status": "skipped"},
            "voice": {"status": "skipped"},
        },
    })


def initial_steps(*, enable_text: bool, enable_image: bool, enable_voice: bool) -> dict[str, Any]:
    return {
        "text": {"status": "generating" if enable_text else "skipped"},
        "image": {"status": "pending" if enable_image else "skipped"},
        "voice": {"status": "pending" if enable_voice else "skipped"},
    }


def enrich_result(data: dict[str, Any]) -> dict[str, Any]:
    """Add display-friendly labels for saved input fields."""
    result = dict(data)
    category = result.get("question_category")
    if category:
        result.setdefault(
            "question_category_label",
            QUESTION_LABELS.get(category, category.replace("_", " ").title()),
        )
    if result.get("narrator_slug") and not result.get("narrator_tone_label"):
        narrators = load_narrators()
        narrator = narrators.get(result["narrator_slug"])
        if narrator:
            result.setdefault("narrator_tone_label", narrator.get("tone_label"))
    return result


def normalize_result(data: dict[str, Any]) -> dict[str, Any]:
    data = enrich_result(data)
    if data.get("steps"):
        return data

    text_ready = bool(data.get("reflection"))
    return {
        **data,
        "steps": {
            "text": {
                "status": "ready" if text_ready else (
                    "error" if data.get("status") == "error" else "pending"
                ),
                "error": data.get("message"),
            },
            "image": {
                "status": "ready" if data.get("comic_file") else "skipped",
            },
            "voice": {
                "status": "ready" if data.get("audio_file") else "skipped",
            },
        },
    }


def text_is_ready(data: dict[str, Any]) -> bool:
    data = normalize_result(data)
    return data["steps"]["text"]["status"] == "ready"


def all_steps_terminal(data: dict[str, Any]) -> bool:
    data = normalize_result(data)
    return all(
        data["steps"][step]["status"] in TERMINAL_STEP_STATUSES
        for step in ("text", "image", "voice")
    )


def parse_claude_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)
