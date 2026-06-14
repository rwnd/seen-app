"""Tests for reflection form validation."""

from __future__ import annotations

import pytest

from seen.validation import ReflectionInputError, validate_reflect_input


@pytest.fixture
def archetypes() -> dict:
    return {
        "commander": {"name": "Commander", "category": "Leaders"},
    }


@pytest.fixture
def narrators() -> dict:
    return {
        "jobs": {"name": "Steve Jobs"},
    }


def test_validate_reflect_input_accepts_valid_submission(archetypes, narrators) -> None:
    result = validate_reflect_input(
        "commander",
        "identity",
        "  This is a long enough honest answer.  ",
        "jobs",
        archetypes=archetypes,
        narrators=narrators,
    )
    assert result == "This is a long enough honest answer."


@pytest.mark.parametrize(
    ("response", "detail"),
    [
        ("too short", "Response must be at least 20 characters"),
        ("x" * 19, "Response must be at least 20 characters"),
    ],
)
def test_validate_reflect_input_rejects_short_response(
    archetypes,
    narrators,
    response: str,
    detail: str,
) -> None:
    with pytest.raises(ReflectionInputError) as exc:
        validate_reflect_input(
            "commander",
            "identity",
            response,
            "jobs",
            archetypes=archetypes,
            narrators=narrators,
        )
    assert exc.value.detail == detail


def test_validate_reflect_input_rejects_unknown_archetype(archetypes, narrators) -> None:
    with pytest.raises(ReflectionInputError, match="Unknown archetype"):
        validate_reflect_input(
            "missing",
            "identity",
            "This is a long enough honest answer.",
            "jobs",
            archetypes=archetypes,
            narrators=narrators,
        )


def test_validate_reflect_input_rejects_unknown_narrator(archetypes, narrators) -> None:
    with pytest.raises(ReflectionInputError, match="Unknown narrator"):
        validate_reflect_input(
            "commander",
            "identity",
            "This is a long enough honest answer.",
            "missing",
            archetypes=archetypes,
            narrators=narrators,
        )


def test_validate_reflect_input_rejects_unknown_category(archetypes, narrators) -> None:
    with pytest.raises(ReflectionInputError, match="Unknown question category"):
        validate_reflect_input(
            "commander",
            "not-a-category",
            "This is a long enough honest answer.",
            "jobs",
            archetypes=archetypes,
            narrators=narrators,
        )
