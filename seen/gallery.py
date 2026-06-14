"""Load and filter saved reflections for the gallery page."""

from __future__ import annotations

import json
from typing import Any

from seen.config import RESULTS_DIR
from seen.utils import normalize_result


def load_gallery_items() -> list[dict[str, Any]]:
    """Return completed reflections newest-first, excluding errors and incomplete saves."""
    items: list[dict[str, Any]] = []
    for path in RESULTS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if data.get("status") == "error" or "the_line" not in data:
            continue
        items.append(normalize_result(data))
    items.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return items


def build_archetype_filters(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build archetype pill filters with counts for the gallery UI."""
    counts: dict[str, int] = {}
    names: dict[str, str] = {}
    for item in items:
        slug = item.get("archetype_slug")
        if not slug:
            continue
        counts[slug] = counts.get(slug, 0) + 1
        names.setdefault(slug, item.get("archetype_name", slug))

    return [
        {"slug": slug, "name": names[slug], "count": counts[slug]}
        for slug in sorted(names, key=lambda s: names[s].lower())
    ]
