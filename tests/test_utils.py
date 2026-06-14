"""Tests for result normalization and JSON parsing."""

from __future__ import annotations

from seen.utils import normalize_result, parse_claude_json, text_is_ready


def test_parse_claude_json_strips_markdown_fence() -> None:
    raw = '```json\n{"reflection": "ok", "the_line": "line"}\n```'
    parsed = parse_claude_json(raw)
    assert parsed["reflection"] == "ok"


def test_normalize_result_adds_steps_for_legacy_payload() -> None:
    data = {
        "uuid": "legacy",
        "reflection": "Saved reflection",
        "the_line": "Saved line",
        "comic_file": "legacy_comic.png",
        "audio_file": "legacy_audio.wav",
    }
    normalized = normalize_result(data)
    assert normalized["steps"]["text"]["status"] == "ready"
    assert normalized["steps"]["image"]["status"] == "ready"
    assert normalized["steps"]["voice"]["status"] == "ready"


def test_normalize_result_adds_question_label() -> None:
    data = {
        "uuid": "x",
        "question_category": "identity",
        "steps": {
            "text": {"status": "ready"},
            "image": {"status": "skipped"},
            "voice": {"status": "skipped"},
        },
    }
    normalized = normalize_result(data)
    assert normalized["question_category_label"] == "IDENTITY"


def test_text_is_ready_requires_reflection_step() -> None:
    assert text_is_ready({"reflection": "yes", "steps": {"text": {"status": "ready"}}})
    assert not text_is_ready({"status": "pending"})
