#!/usr/bin/env python3
"""Fetch narrator profile portraits from Wikipedia / Wikimedia Commons."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "static" / "images" / "narrators"
NARRATORS_JSON = ROOT / "narrators.json"

# Wikipedia page titles; fallbacks used when the primary page has no thumbnail.
NARRATORS: dict[str, dict[str, str | list[str]]] = {
    "mcconaughey": {
        "search": "Matthew McConaughey portrait",
        "wikipedia": ["Matthew McConaughey"],
    },
    "miranda": {
        "search": "Meryl Streep 2014 portrait photograph",
        "wikipedia": ["Meryl Streep"],
    },
    "tyson": {
        "search": "Neil deGrasse Tyson portrait",
        "wikipedia": ["Neil deGrasse Tyson"],
    },
    "oprah": {
        "search": "Oprah Winfrey portrait",
        "wikipedia": ["Oprah Winfrey"],
    },
    "jobs": {
        "search": "Steve Jobs portrait",
        "wikipedia": ["Steve Jobs"],
    },
    "yoda": {
        "search": "Yoda Star Wars",
        "wikipedia": ["Yoda"],
    },
}

WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "SEEN/1.0 (narrator image fetch; local dev)"
THUMB_SIZE = 256


def fetch_wikipedia_thumbnail(client: httpx.Client, titles: list[str]) -> str | None:
    for title in titles:
        url = WIKI_SUMMARY.format(title=title.replace(" ", "_"))
        try:
            resp = client.get(url, timeout=30)
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            data = resp.json()
            thumb = data.get("thumbnail")
            if thumb and thumb.get("source"):
                return thumb["source"]
        except Exception:
            continue
    return None


def fetch_commons_thumbnail(client: httpx.Client, search: str) -> str | None:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f'filetype:bitmap {search}',
        "gsrnamespace": 6,
        "gsrlimit": 8,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 400,
        "format": "json",
    }
    try:
        resp = client.get(COMMONS_API, params=params, timeout=30)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        best: tuple[int, str] | None = None
        for page in pages.values():
            for info in page.get("imageinfo", []):
                mime = info.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                width = info.get("width", 0)
                height = info.get("height", 0)
                if width < 200 or height < 200:
                    continue
                ratio = width / height
                if ratio < 0.6 or ratio > 1.8:
                    continue
                score = min(width, height)
                url = info.get("thumburl") or info.get("url")
                if url and (best is None or score > best[0]):
                    best = (score, url)
        return best[1] if best else None
    except Exception:
        return None


def crop_square(img: Image.Image, size: int) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    cropped = img.crop((left, top, left + side, top + side))
    return cropped.resize((size, size), Image.Resampling.LANCZOS)


def download_and_save(client: httpx.Client, slug: str, image_url: str) -> bool:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{slug}.jpg"
    try:
        resp = client.get(image_url, follow_redirects=True, timeout=60)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        elif img.mode == "L":
            img = img.convert("RGB")
        square = crop_square(img, THUMB_SIZE)
        square.save(dest, "JPEG", quality=88, optimize=True)
        print(f"  {slug}: OK -> {dest.name} ({square.size[0]}x{square.size[1]})")
        return True
    except Exception as exc:
        print(f"  {slug}: save FAILED ({exc})")
        return False


def fetch_narrator_image(client: httpx.Client, slug: str, config: dict) -> bool:
    titles = config.get("wikipedia", [])
    if isinstance(titles, str):
        titles = [titles]
    image_url = fetch_wikipedia_thumbnail(client, list(titles))
    source = "wikipedia"
    if not image_url:
        image_url = fetch_commons_thumbnail(client, str(config["search"]))
        source = "commons"
    if not image_url:
        print(f"  {slug}: no image found")
        return False
    print(f"  {slug}: using {source}")
    return download_and_save(client, slug, image_url)


def update_narrators_json(slugs: list[str]) -> None:
    data = json.loads(NARRATORS_JSON.read_text(encoding="utf-8"))
    narrators = data.get("narrators", {})
    for slug in slugs:
        if slug in narrators:
            narrators[slug]["photo"] = f"{slug}.jpg"
    NARRATORS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {NARRATORS_JSON.name} with photo fields")


def main() -> None:
    print(f"Saving to {OUT_DIR}")
    ok_slugs: list[str] = []
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(headers=headers) as client:
        for slug, config in NARRATORS.items():
            if fetch_narrator_image(client, slug, config):
                ok_slugs.append(slug)
    print(f"Done: {len(ok_slugs)}/{len(NARRATORS)} succeeded")
    if ok_slugs:
        update_narrators_json(ok_slugs)


if __name__ == "__main__":
    main()
