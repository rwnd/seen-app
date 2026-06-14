"""Tests for narrator speech assembly."""

from __future__ import annotations

from seen.gateways.tts import build_narrator_speech


def test_build_narrator_speech_includes_bridge_and_signoff() -> None:
    narrator = {
        "voice_bridge": "One more thing",
        "signature_line": "You already know the answer.",
        "voice_include_signoff": True,
    }
    speech = build_narrator_speech(
        "You built a machine that never stops.",
        "Perfection is knowing when to start.",
        narrator,
    )
    assert "You built a machine that never stops." in speech
    assert "One more thing... Perfection is knowing when to start." in speech
    assert speech.endswith("You already know the answer.")


def test_build_narrator_speech_skips_duplicate_signoff() -> None:
    narrator = {
        "voice_bridge": "Remember this",
        "signature_line": "That's all.",
        "voice_include_signoff": True,
    }
    speech = build_narrator_speech(
        "Ten years of mirrors.",
        "That's all.",
        narrator,
    )
    assert speech.count("That's all.") == 1


def test_build_narrator_speech_can_disable_signoff() -> None:
    narrator = {
        "voice_bridge": "Remember this",
        "signature_line": "That's all.",
        "voice_include_signoff": False,
    }
    speech = build_narrator_speech("Body text.", "Final line.", narrator)
    assert "That's all." not in speech
