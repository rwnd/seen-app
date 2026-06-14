"""Validate user input before queuing a reflection."""

from __future__ import annotations

from seen.config import QUESTION_LABELS


class ReflectionInputError(ValueError):
    """Raised when reflect form input fails validation."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def validate_reflect_input(
    archetype_slug: str,
    question_category: str,
    user_response: str,
    narrator_slug: str,
    *,
    archetypes: dict,
    narrators: dict,
) -> str:
    """
    Validate and normalize a reflection submission.

    Returns stripped user_response on success.
    Raises ReflectionInputError with a user-facing message on failure.
    """
    cleaned = user_response.strip()
    if len(cleaned) < 20:
        raise ReflectionInputError("Response must be at least 20 characters")
    if archetype_slug not in archetypes:
        raise ReflectionInputError("Unknown archetype")
    if narrator_slug not in narrators:
        raise ReflectionInputError("Unknown narrator")
    if question_category not in QUESTION_LABELS:
        raise ReflectionInputError("Unknown question category")
    return cleaned
