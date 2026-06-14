"""Tests for sample result seeding."""

from __future__ import annotations

import json
from pathlib import Path

from seen.samples import seed_sample_results_if_empty


def test_seed_sample_results_if_empty_copies_bundled_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    samples = tmp_path / "samples"
    results = tmp_path / "results"
    samples.mkdir()
    results.mkdir()

    payload = {
        "uuid": "demo-uuid",
        "status": "ready",
        "the_line": "One line.",
    }
    (samples / "demo-uuid.json").write_text(json.dumps(payload), encoding="utf-8")
    (samples / "demo-uuid_comic.png").write_bytes(b"png")
    (samples / "demo-uuid_audio.mp3").write_bytes(b"mp3")

    monkeypatch.setattr("seen.samples.SAMPLES_DIR", samples)
    monkeypatch.setattr("seen.samples.RESULTS_DIR", results)

    assert seed_sample_results_if_empty() == 3
    assert (results / "demo-uuid.json").exists()
    assert (results / "demo-uuid_comic.png").exists()
    assert seed_sample_results_if_empty() == 0


def test_seed_sample_results_if_empty_skips_when_gallery_has_items(
    tmp_path: Path,
    monkeypatch,
) -> None:
    samples = tmp_path / "samples"
    results = tmp_path / "results"
    samples.mkdir()
    results.mkdir()

    (samples / "demo-uuid.json").write_text(
        '{"uuid":"demo-uuid","status":"ready","the_line":"x"}',
        encoding="utf-8",
    )
    (results / "existing.json").write_text(
        '{"uuid":"existing","status":"ready","the_line":"y"}',
        encoding="utf-8",
    )

    monkeypatch.setattr("seen.samples.SAMPLES_DIR", samples)
    monkeypatch.setattr("seen.samples.RESULTS_DIR", results)

    assert seed_sample_results_if_empty() == 0
    assert not (results / "demo-uuid.json").exists()
