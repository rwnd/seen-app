"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from seen.config import RESULTS_DIR


@pytest.fixture
def sample_comic_page() -> dict:
    return {
        "archetype_character": "A robed commander in a war room",
        "narrator_character": "A campfire traveler",
        "setting": "An empty command center at dusk",
        "panels": [
            {
                "size": "full_width",
                "scene": "Wide shot of maps on a table",
                "caption": "THE WAR ROOM",
                "narration": "",
                "is_climax": False,
            },
            {
                "size": "half",
                "scene": "Guide at campfire",
                "caption": "",
                "narration": "STILL BECOMING",
                "is_climax": False,
            },
            {
                "size": "half",
                "scene": "Hands on a ledger",
                "caption": "",
                "narration": "",
                "is_climax": False,
            },
            {
                "size": "full_width",
                "scene": "Commander alone in light",
                "caption": "ENOUGH",
                "narration": "",
                "is_climax": True,
            },
        ],
    }


@pytest.fixture
def sample_reflection_payload(sample_comic_page: dict) -> dict:
    return {
        "reflection": "You carry standards no one else sees.",
        "the_line": "The weight was never proof you were weak.",
        "comic_page": sample_comic_page,
    }


@pytest.fixture
def tmp_results_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    results = tmp_path / "results"
    results.mkdir()
    monkeypatch.setattr("seen.config.RESULTS_DIR", results)
    monkeypatch.setattr("seen.utils.RESULTS_DIR", results)
    monkeypatch.setattr("seen.gallery.RESULTS_DIR", results)
    return results


@pytest.fixture
def gallery_result_file(tmp_results_dir: Path) -> Path:
    payload = {
        "uuid": "gallery-test-uuid",
        "status": "ready",
        "created_at": "2026-06-13T12:00:00+00:00",
        "archetype_slug": "commander",
        "archetype_name": "Commander",
        "the_line": "Leadership begins in silence.",
        "reflection": "You hold the line when no one is watching.",
        "steps": {
            "text": {"status": "ready"},
            "image": {"status": "ready"},
            "voice": {"status": "ready"},
        },
    }
    path = tmp_results_dir / "gallery-test-uuid.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
