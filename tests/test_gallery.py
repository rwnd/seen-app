"""Tests for gallery loading."""

from __future__ import annotations

from seen.gallery import build_archetype_filters, load_gallery_items


def test_load_gallery_items_skips_errors_and_incomplete(tmp_results_dir, gallery_result_file) -> None:
    (tmp_results_dir / "bad.json").write_text("{not json", encoding="utf-8")
    (tmp_results_dir / "error.json").write_text(
        '{"status":"error","the_line":"x"}',
        encoding="utf-8",
    )
    items = load_gallery_items()
    assert len(items) == 1
    assert items[0]["uuid"] == "gallery-test-uuid"


def test_build_archetype_filters_counts_items(gallery_result_file) -> None:
    items = load_gallery_items()
    filters = build_archetype_filters(items)
    assert filters == [{"slug": "commander", "name": "Commander", "count": 1}]
