"""Submit explicitly selected production URLs to IndexNow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

HOST = "peterroelants.github.io"
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10_000
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ConfigurationError(ValueError):
    """Raised when the local IndexNow verification setup is invalid."""


def find_key_file() -> Path:
    """Return the sole root-level IndexNow key file."""
    key_files = sorted(
        path for path in REPOSITORY_ROOT.glob("*.txt") if path.name != "robots.txt"
    )
    if len(key_files) != 1:
        raise ConfigurationError(
            "expected exactly one root-level IndexNow key file besides robots.txt"
        )
    return key_files[0]


def read_key(key_file: Path) -> str:
    """Read and validate the key whose filename proves host ownership."""
    try:
        key = key_file.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ConfigurationError(f"cannot read key file {key_file}: {error}") from error

    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise ConfigurationError(
            "IndexNow key must contain 8–128 letters, numbers, or hyphens"
        )
    if key_file.name != f"{key}.txt":
        raise ConfigurationError("IndexNow key filename and contents do not match")
    return key


def validate_urls(urls: Sequence[str]) -> list[str]:
    """Validate and deduplicate URLs belonging to this production host."""
    if not urls:
        raise ConfigurationError("provide at least one production URL")
    if len(urls) > MAX_URLS:
        raise ConfigurationError(f"provide no more than {MAX_URLS} URLs")

    unique_urls = list(dict.fromkeys(urls))
    for url in unique_urls:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname != HOST
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ConfigurationError(f"URL must belong to https://{HOST}/: {url}")
        if parsed.fragment:
            raise ConfigurationError(f"URL must not contain a fragment: {url}")
    return unique_urls


def submit_urls(key: str, urls: Sequence[str]) -> tuple[int, str]:
    """Submit URLs as one IndexNow request and return its status and body."""
    payload = json.dumps({"host": HOST, "key": key, "urlList": urls}).encode("utf-8")
    request = Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return error.code, body
    except (TimeoutError, URLError) as error:
        reason = getattr(error, "reason", error)
        raise RuntimeError(f"IndexNow request failed: {reason}") from error


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Notify IndexNow about explicitly selected production URLs after "
            "a major deployed change."
        )
    )
    parser.add_argument(
        "--key-file",
        type=Path,
        help="key file path, defaulting to the sole root-level key file",
    )
    parser.add_argument("urls", nargs="+", metavar="URL")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate configuration, submit URLs, and report the result."""
    args = parse_args(argv)
    try:
        key_file = (args.key_file or find_key_file()).resolve()
        key = read_key(key_file)
        urls = validate_urls(args.urls)
        status, body = submit_urls(key, urls)
    except (ConfigurationError, RuntimeError) as error:
        print(f"IndexNow submission failed: {error}", file=sys.stderr)
        return 1

    print(f"Submitted {len(urls)} URL(s) to IndexNow: HTTP {status}")
    if body.strip():
        print(body.strip())
    if status not in {200, 202}:
        print("IndexNow did not accept the submission.", file=sys.stderr)
        return 1
    print("The notification was received; indexing is not guaranteed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
