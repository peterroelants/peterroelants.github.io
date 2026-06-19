#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML", "python-slugify"]
# ///

"""Generate the site's legacy tag pages and tag-slug data file.

Tag preprocessing.
- Generate all tag pages.
- Generate jekyll data file to lookup tag URL slugs.
"""

import itertools
import re
import shutil
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import yaml
from slugify import slugify

# Get the base directory of this project relative to this script
BASE_DIR = Path(__file__).resolve().parents[2]
POSTS_DIR = BASE_DIR / "_posts"
TAGS_DIR = BASE_DIR / "tags"
DATA_DIR = BASE_DIR / "_data"

FRONT_MATTER_REGEX = re.compile("^---\n(.*)\n---\n", flags=re.DOTALL)

TAGS_KEYWORD = "tags"


def get_all_posts() -> Iterator[Path]:
    """Get all post files recursively."""
    return itertools.chain(POSTS_DIR.glob("**/*.html"), POSTS_DIR.glob("**/*.md"))


def get_front_matter(post: Path) -> dict[str, Any]:
    """Extract front matter from a post file."""
    text = post.read_text(encoding="utf-8")
    match = FRONT_MATTER_REGEX.match(text)
    if not match:
        return {}

    parsed = yaml.safe_load(match.group(1))
    return parsed if isinstance(parsed, dict) else {}


def get_tags(post: Path) -> list[str]:
    """Get post's tags."""
    front_matter_dct = get_front_matter(post)
    tags = front_matter_dct.get(TAGS_KEYWORD, [])
    if isinstance(tags, str):
        return [tags]
    if not isinstance(tags, list):
        return []
    return [tag for tag in tags if isinstance(tag, str)]


def get_tag_counts(posts: Iterator[Path]) -> dict[str, int]:
    """Get all tags from given posts."""
    tag_counter = Counter[str]()
    for post in posts:
        tag_counter.update(get_tags(post))
    return tag_counter


def has_duplicate_tags_ignore_case(tags: Iterable[str]) -> bool:
    """Check for duplicate tags, ignoring case."""
    tag_list = list(tags)
    counter = Counter[str](tag.lower() for tag in tag_list)
    has_duplicates = False
    for tag_lower, cnt in counter.items():
        if cnt > 1:
            has_duplicates = True
            duplicate_tags = [tag for tag in tag_list if tag.lower() == tag_lower]
            print(f"Duplicate tags found for {tag_lower!r}: {duplicate_tags!r}")
    return has_duplicates


def create_tag_page(tags_dir: Path, tag: str) -> str:
    """Create tag page for tag and return string representation."""
    front_matter_dict = {
        "layout": "tag_page",
        "title": f"Posts with tag: {tag}",
        "tag": tag,
        "sitemap": False,
    }
    header_str = "\n".join(
        [
            "---",
            yaml.dump(
                front_matter_dict, sort_keys=False, default_flow_style=False
            ).rstrip("\n"),
            "---",
            "",
        ]
    )
    tag_url_slug = slugify(tag)
    tag_page_path = (tags_dir / tag_url_slug).with_suffix(".html")
    tag_page_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"create tag page at {tag_page_path!s}")
    tag_page_path.write_text(header_str, encoding="utf-8")
    return tag_url_slug


def clean_tag_pages() -> None:
    """Remove previously generated tag pages when they exist."""
    if TAGS_DIR.exists():
        shutil.rmtree(TAGS_DIR)


def create_tag_pages(tags: Iterable[str]) -> dict[str, str]:
    """Create tag pages for given tags."""
    tag_url_slugs = {}
    for tag in tags:
        tag_url_slugs[tag] = create_tag_page(TAGS_DIR, tag)
    return tag_url_slugs


def create_tag_slugs(tag_url_slugs: dict[str, str]) -> None:
    """Create the data file containing tag URL slugs."""
    tag_properties_path = DATA_DIR / "tag_url_slugs.yml"
    print(f"Create tag properties datafile at {tag_properties_path!s}")
    with tag_properties_path.open("w", encoding="utf-8") as f_handle:
        yaml.dump(tag_url_slugs, f_handle, default_flow_style=False)


def run() -> int:
    print("Create tag pages and tag properties data file.")
    print(f"Base directory to run in: {BASE_DIR!s}")
    posts = get_all_posts()
    tag_counts = get_tag_counts(posts)
    has_duplicates = has_duplicate_tags_ignore_case(tag_counts.keys())
    if has_duplicates:
        print("Duplicate tags found, please clean up first!")
        return 1
    clean_tag_pages()
    tag_url_slugs = create_tag_pages(tags=tag_counts.keys())
    create_tag_slugs(tag_url_slugs)
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
