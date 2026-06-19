#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4"]
# ///
"""Check references and accessibility for extracted notebook media."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "_posts"
ASSET_ROOT_URL = "/images/notebook_outputs"
ASSET_ROOT = BASE_DIR / ASSET_ROOT_URL.lstrip("/")
GENERIC_ALT_TEXT = {
    "no description has been provided for this image",
    "image",
}
CONTENT_HASH_RE = re.compile(r"-(?P<hash>[0-9a-f]{12})(?P<extension>\.[^.]+)$")
MEDIA_TAGS = ("img", "video", "audio", "source")
ASSET_TAGS = (*MEDIA_TAGS, "script")
LAZY_BOKEH_ATTR = "data-bokeh-script"


def asset_path(src: str) -> Path | None:
    """Map a site-local extracted-media URL to a repository path."""
    path = urlsplit(src).path
    if not path.startswith(f"{ASSET_ROOT_URL}/"):
        return None
    return BASE_DIR / path.lstrip("/")


def meaningful_alt(tag: Tag) -> bool:
    """Return whether an image has useful non-generic alternative text."""
    alt = tag.get("alt")
    if not isinstance(alt, str):
        return False
    normalized = " ".join(alt.split()).strip().lower()
    return bool(normalized) and normalized not in GENERIC_ALT_TEXT


def has_dimensions(tag: Tag) -> bool:
    """Return whether an image has positive intrinsic dimensions."""
    width = tag.get("width")
    height = tag.get("height")
    if not isinstance(width, str) or not isinstance(height, str):
        return False
    try:
        width = int(width)
        height = int(height)
    except (TypeError, ValueError):
        return False
    return width > 0 and height > 0


def tag_src(tag: Tag) -> str | None:
    """Return a referenced asset URL from a media or lazy-output tag."""
    src = tag.get("src") or tag.get(LAZY_BOKEH_ATTR)
    return src if isinstance(src, str) else None


def asset_tags(soup: BeautifulSoup) -> list[Tag]:
    """Return tags that reference extracted media or lazy Bokeh assets."""
    return [*soup.find_all(ASSET_TAGS), *soup.select(f"[{LAZY_BOKEH_ATTR}]")]


def has_matching_content_hash(path: Path) -> bool:
    """Return whether a generated filename contains the file's content hash."""
    match = CONTENT_HASH_RE.search(path.name)
    if match is None:
        return False
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return digest == match.group("hash")


def main() -> int:
    errors: list[str] = []
    referenced_assets: set[Path] = set()
    extracted_posts = 0

    for post_path in sorted(POSTS_DIR.rglob("*.html")):
        html = post_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        tags = asset_tags(soup)
        post_has_extracted_assets = any(
            (src := tag_src(tag)) is not None and asset_path(src) is not None
            for tag in tags
        )
        if not post_has_extracted_assets:
            continue
        extracted_posts += 1
        for tag in tags:
            src = tag_src(tag)
            if src is None:
                continue
            if src.startswith("data:"):
                errors.append(f"{post_path}: inline data media remains in <{tag.name}>")
                continue

            path = asset_path(src)
            if path is None:
                continue
            referenced_assets.add(path)
            if not path.is_file():
                errors.append(f"{post_path}: missing extracted asset {src}")
            elif not has_matching_content_hash(path):
                errors.append(f"{post_path}: content hash mismatch for {src}")
            if tag.name == "img":
                if not meaningful_alt(tag):
                    errors.append(f"{post_path}: missing or generic alt text for {src}")
                if not has_dimensions(tag):
                    errors.append(f"{post_path}: missing dimensions for {src}")

    if ASSET_ROOT.is_dir():
        for path in sorted(path for path in ASSET_ROOT.rglob("*") if path.is_file()):
            if path not in referenced_assets:
                errors.append(f"orphaned extracted asset: {path.relative_to(BASE_DIR)}")

    if errors:
        print("generated media check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "generated media check passed: "
        f"{extracted_posts} post(s), {len(referenced_assets)} referenced asset(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
