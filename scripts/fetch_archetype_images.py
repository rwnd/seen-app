#!/usr/bin/env python3
"""Fetch PrinciplesYou og:image social cards for each archetype."""

from pathlib import Path

import httpx
from bs4 import BeautifulSoup

ARCHETYPES = [
    ("commander", "https://principlesyou.com/archetypes/commander"),
    ("shaper", "https://principlesyou.com/archetypes/shaper"),
    ("quietleader", "https://principlesyou.com/archetypes/quietleader"),
    ("inspirer", "https://principlesyou.com/archetypes/inspirer"),
    ("campaigner", "https://principlesyou.com/archetypes/campaigner"),
    ("coach", "https://principlesyou.com/archetypes/coach"),
    ("promoter", "https://principlesyou.com/archetypes/promoter"),
    ("impresario", "https://principlesyou.com/archetypes/impresario"),
    ("entertainer", "https://principlesyou.com/archetypes/entertainer"),
    ("peacekeeper", "https://principlesyou.com/archetypes/peacekeeper"),
    ("problemsolver", "https://principlesyou.com/archetypes/problemsolver"),
    ("helper", "https://principlesyou.com/archetypes/helper"),
    ("strategist", "https://principlesyou.com/archetypes/strategist"),
    ("planner", "https://principlesyou.com/archetypes/planner"),
    ("orchestrator", "https://principlesyou.com/archetypes/orchestrator"),
    ("implementer", "https://principlesyou.com/archetypes/implementer"),
    ("investigator", "https://principlesyou.com/archetypes/investigator"),
    ("technician", "https://principlesyou.com/archetypes/technician"),
    ("adventurer", "https://principlesyou.com/archetypes/adventurer"),
    ("artisan", "https://principlesyou.com/archetypes/artisan"),
    ("inventor", "https://principlesyou.com/archetypes/inventor"),
    ("explorer", "https://principlesyou.com/archetypes/explorer"),
    ("thinker", "https://principlesyou.com/archetypes/thinker"),
    ("growthseeker", "https://principlesyou.com/archetypes/growthseeker"),
    ("protector", "https://principlesyou.com/archetypes/protector"),
    ("enforcer", "https://principlesyou.com/archetypes/enforcer"),
    ("critic", "https://principlesyou.com/archetypes/critic"),
    ("individualist", "https://principlesyou.com/archetypes/individualist"),
]

OUT_DIR = Path(__file__).resolve().parent.parent / "static" / "images" / "archetypes"


def fetch_og_image(client: httpx.Client, slug: str, url: str) -> bool:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{slug}.png"
    try:
        resp = client.get(url, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", property="og:image")
        if not meta or not meta.get("content"):
            print(f"  {slug}: no og:image meta tag")
            return False
        img_url = meta["content"]
        img_resp = client.get(img_url, follow_redirects=True, timeout=60)
        img_resp.raise_for_status()
        dest.write_bytes(img_resp.content)
        print(f"  {slug}: OK -> {dest.name}")
        return True
    except Exception as exc:
        print(f"  {slug}: FAILED ({exc})")
        return False


def main() -> None:
    print(f"Saving to {OUT_DIR}")
    ok = 0
    with httpx.Client(headers={"User-Agent": "SEEN/1.0"}) as client:
        for slug, url in ARCHETYPES:
            if fetch_og_image(client, slug, url):
                ok += 1
    print(f"Done: {ok}/{len(ARCHETYPES)} succeeded")


if __name__ == "__main__":
    main()
