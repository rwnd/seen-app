"""Smoke tests for HTTP routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from seen.app import app


client = TestClient(app)


def test_home_page_renders() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "What would you look like" in response.text


def test_reflect_rejects_short_response() -> None:
    response = client.post(
        "/reflect",
        data={
            "archetype_slug": "commander",
            "question_category": "identity",
            "user_response": "too short",
            "narrator_slug": "jobs",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400


def test_processing_page_renders() -> None:
    response = client.get("/processing/test-uuid")
    assert response.status_code == 200
    assert "Witnessing" in response.text


def test_api_status_pending_for_missing_result() -> None:
    response = client.get("/api/status/does-not-exist")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["text_ready"] is False


def test_demo_video_is_served() -> None:
    response = client.get("/docs-assets/demo.mp4")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("video/")
