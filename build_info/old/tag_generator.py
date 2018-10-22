#!/usr/bin/env python3

"""
Old script to do offline tag-page and tag data-page generation.

Tag preprocessing.
- Generate all tag pages.
- Generate jekyll data file to lookup tag URL slugs.
"""
import itertools
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List

import yaml
from slugify import slugify

# Get the base directory of this project relative to this script
BASE_DIR = Path(os.path.realpath(__file__)).parent.parent
POSTS_DIR = BASE_DIR / "_posts"
TAGS_DIR = BASE_DIR / "tags"
DATA_DIR = BASE_DIR / "_data"

FRONT_MATTER_REGEX = re.compile("^---\n(.*)\n---\n", flags=re.DOTALL)

TAGS_KEYWORD = "tags"


def get_all_posts() -> Iterator[Path]:
    """Get all post files recursively."""
    return itertools.chain(POSTS_DIR.glob("**/*.html"), POSTS_DIR.glob("**/*.md"))


def get_front_matter(post: Path) -> Dict[str, Any]:
    """Extract front matter from a post file."""
    text = post.read_text()
    match = FRONT_MATTER_REGEX.match(text)
    if match:
        # Get first parenthesized subgroup
        group = match.group(1)
        return yaml.safe_load(group)
    return {}


def get_tags(post: Path) -> List[str]:
    """Get post's tags."""
    front_matter_dct = get_front_matter(post)
    tags = front_matter_dct.get(TAGS_KEYWORD, [])
    return tags


def get_tag_counts(posts: Iterator[Path]) -> Dict[str, int]:
    """Get all tags from given posts."""
    tag_counter = Counter[str]()
    for post in posts:
        tag_counter.update(get_tags(post))
    return tag_counter


def has_duplicate_tags_ignore_case(tags: Iterable[str]):
    """Check for duplicate tags (ignoring cases)"""
    counter = Counter[str]((t.lower() for t in tags))
    has_duplicates = False
    for tag_lower, cnt in counter.items():
        if cnt > 1:
            has_duplicates = True
            duplicate_tags = [tag for tag in tags if tag.lower() == tag_lower]
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
    tag_page_path.write_text(header_str)
    return tag_url_slug


def clean_tag_pages():
    """Cleanup tag pages dir"""
    shutil.rmtree(TAGS_DIR, ignore_errors=False)


def create_tag_pages(tags: Iterable[str]) -> Dict[str, str]:
    """Create tag pages for given tags."""
    tag_url_slugs = {}
    for tag in tags:
        tag_url_slugs[tag] = create_tag_page(TAGS_DIR, tag)
    return tag_url_slugs


def create_tag_slugs(tag_url_slugs: Dict[str, str]):
    """Create data file with tag URLS slugs."""
    tag_properties_path = DATA_DIR / "tag_url_slugs.yml"
    print(f"Create tag properties datafile at {tag_properties_path!s}")
    with tag_properties_path.open("w") as f_handle:
        yaml.dump(tag_url_slugs, f_handle, default_flow_style=False)


def run():
    print("Create tag pages and tag properties data file.")
    print(f"Base directory to run in: {BASE_DIR!s}")
    posts = get_all_posts()
    tag_counts = get_tag_counts(posts)
    has_duplicates = has_duplicate_tags_ignore_case(tag_counts.keys())
    if has_duplicates:
        print("Duplicate tags found, please clean up first!")
        sys.exit(1)
    clean_tag_pages()
    tag_url_slugs = create_tag_pages(tags=tag_counts.keys())
    create_tag_slugs(tag_url_slugs)


def main():
    run()


if __name__ == "__main__":
    main()
