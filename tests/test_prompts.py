"""Tests for comic prompt helpers."""

from __future__ import annotations

import pytest

from seen.prompts import (
    COMIC_PANEL_COUNT,
    normalize_panel_size,
    validate_comic_page,
)


def test_normalize_panel_size_aliases() -> None:
    assert normalize_panel_size("full-width") == "full_width"
    assert normalize_panel_size("medium") == "half"
    assert normalize_panel_size(None) == "half"


def test_validate_comic_page_accepts_valid_payload(sample_reflection_payload) -> None:
    validate_comic_page(sample_reflection_payload)


def test_validate_comic_page_rejects_wrong_panel_count(sample_reflection_payload) -> None:
    sample_reflection_payload["comic_page"]["panels"] = (
        sample_reflection_payload["comic_page"]["panels"][:2]
    )
    with pytest.raises(ValueError, match=str(COMIC_PANEL_COUNT)):
        validate_comic_page(sample_reflection_payload)


def test_validate_comic_page_requires_caption_on_panel_one(sample_reflection_payload) -> None:
    sample_reflection_payload["comic_page"]["panels"][0]["caption"] = ""
    with pytest.raises(ValueError, match="Panel 1 missing caption"):
        validate_comic_page(sample_reflection_payload)
