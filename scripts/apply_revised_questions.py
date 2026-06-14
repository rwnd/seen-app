#!/usr/bin/env python3
"""Apply revised questions with starters to archetypes.json."""

import json
from pathlib import Path

from revised_questions_data import REVISED_QUESTIONS

BASE = Path(__file__).resolve().parent.parent
ARCHETYPES_PATH = BASE / "archetypes.json"


def main() -> None:
    with ARCHETYPES_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    for slug, questions in REVISED_QUESTIONS.items():
        if slug not in data["archetypes"]:
            raise KeyError(f"Unknown archetype slug: {slug}")
        data["archetypes"][slug]["questions"] = questions

    with ARCHETYPES_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Updated questions for {len(REVISED_QUESTIONS)} archetypes in {ARCHETYPES_PATH}")


if __name__ == "__main__":
    main()
