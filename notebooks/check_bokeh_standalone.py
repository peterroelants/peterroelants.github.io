#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Check that Bokeh content published by the site is standalone browser output.

The notebook scan deliberately examines code cells only. Executed notebook
outputs can contain Bokeh's generic client-side server support, even when the
notebook did not connect to a server. The generated-page scan therefore checks
for actual server URLs and session metadata rather than those generic library
strings.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
POSTS_DIR = BASE_DIR / "_posts"
BOKEH_ASSET_ROOT = "/js/bokeh/3.9.1"

BOKEH_MARKERS = (
    "application/vnd.bokeh",
    "embed_items",
    BOKEH_ASSET_ROOT,
    "data-bokeh-script",
)

SERVER_SOURCE_PATTERNS = (
    (re.compile(r"\bbokeh\s*\.\s*serve\s*\("), "bokeh.serve(...)"),
    (re.compile(r"\bserver_document\s*\("), "server_document(...)"),
    (re.compile(r"\bserver_session\s*\("), "server_session(...)"),
    (re.compile(r"\boutput_server\s*\("), "output_server(...)"),
    (re.compile(r"\bshow_server\s*\("), "show_server(...)"),
    (re.compile(r"\bcurdoc\s*\("), "curdoc(...)"),
    (re.compile(r"\b(?:pull_session|push_session)\s*\("), "Bokeh session API"),
    (re.compile(r"\bClientSession\b"), "ClientSession"),
)

SERVER_PAGE_PATTERNS = (
    (re.compile(r"\bbokeh\s*\.\s*serve\s*\("), "bokeh.serve(...)"),
    (re.compile(r"\bserver_document\s*\("), "server_document(...)"),
    (re.compile(r"\bserver_session\s*\("), "server_session(...)"),
    (re.compile(r"\boutput_server\s*\("), "output_server(...)"),
    (re.compile(r"\bshow_server\s*\("), "show_server(...)"),
    (re.compile(r"\b(?:ws|wss)://"), "WebSocket URL"),
    (
        re.compile(r"\bhttps?://[^\"'\s<>]+/ws(?:[/?#\"']|$)"),
        "Bokeh server URL",
    ),
    (
        re.compile(r"\bDEFAULT_SERVER_WEBSOCKET_URL\b"),
        "Bokeh server WebSocket default",
    ),
    (
        re.compile(r"(?:\"|&quot;)server_id(?:\"|&quot;)\s*:"),
        "server_id metadata",
    ),
    (
        re.compile(r"(?:\"|&quot;)session_id(?:\"|&quot;)\s*:"),
        "session_id metadata",
    ),
)

LOCAL_BOKEH_ASSET_RE = re.compile(
    rf"{re.escape(BOKEH_ASSET_ROOT)}/(?P<filename>[A-Za-z0-9._-]+\.js)"
)
LAZY_BOKEH_ASSET_RE = re.compile(
    rf"data-bokeh-script=[\"'](?P<path>{re.escape('/images/notebook_outputs')}/[^\"']+\.js)"
)
BOKEH_SOURCE_RE = re.compile(
    r"(?m)^\s*(?:from|import)\s+bokeh\b"
    r"|\bbokeh\s*\.\s*[A-Za-z_]\w*"
    r"|\bCustomJS\b"
)


def source_files() -> list[Path]:
    """Return source Python files and notebooks, excluding local environments."""
    paths = list(NOTEBOOKS_DIR.rglob("*.py")) + list(NOTEBOOKS_DIR.rglob("*.ipynb"))
    checker_path = Path(__file__).resolve()
    return sorted(
        path
        for path in paths
        if ".venv" not in path.parts and path.resolve() != checker_path
    )


def source_text(path: Path) -> str:
    """Return executable source text, excluding stored notebook outputs."""
    if path.suffix == ".py":
        return path.read_text(encoding="utf-8")

    notebook = json.loads(path.read_text(encoding="utf-8"))
    code_cells = (
        "\n".join("".join(cell.get("source", [])) for cell in notebook.get("cells", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    )
    return "\n".join(code_cells)


def has_bokeh_source(text: str) -> bool:
    """Return whether executable source uses Bokeh."""
    return BOKEH_SOURCE_RE.search(text) is not None


def find_source_violations(path: Path, text: str) -> list[str]:
    """Return forbidden server API uses found in one source file."""
    if not has_bokeh_source(text):
        return []
    return [
        f"{path}: {label}"
        for pattern, label in SERVER_SOURCE_PATTERNS
        if pattern.search(text)
    ]


def page_uses_bokeh(html: str) -> bool:
    """Return whether generated HTML contains a Bokeh standalone output."""
    return any(marker in html for marker in BOKEH_MARKERS)


def page_asset_paths(html: str) -> list[Path]:
    """Return repository paths for version-pinned BokehJS assets in a page."""
    return [
        BASE_DIR / "js" / "bokeh" / "3.9.1" / match.group("filename")
        for match in LOCAL_BOKEH_ASSET_RE.finditer(html)
    ]


def lazy_bokeh_asset_paths(html: str) -> list[Path]:
    """Return repository paths for extracted lazy Bokeh embed scripts."""
    return [
        BASE_DIR / match.group("path").lstrip("/")
        for match in LAZY_BOKEH_ASSET_RE.finditer(html)
    ]


def find_page_violations(path: Path, html: str) -> list[str]:
    """Return standalone-output violations found in one generated page."""
    if not page_uses_bokeh(html):
        return []

    violations = [
        f"{path}: {label}"
        for pattern, label in SERVER_PAGE_PATTERNS
        if pattern.search(html)
    ]
    if "cdn.bokeh.org" in html or "cdn.bokeh" in html:
        violations.append(f"{path}: Bokeh CDN reference")

    lazy_paths = lazy_bokeh_asset_paths(html)
    if lazy_paths:
        loader_path = BASE_DIR / "js" / "notebook_bokeh_lazy.js"
        if not loader_path.is_file():
            violations.append(f"{path}: missing lazy Bokeh loader {loader_path}")
        for lazy_path in lazy_paths:
            if not lazy_path.is_file():
                violations.append(
                    f"{path}: missing lazy Bokeh embed script {lazy_path}"
                )
            else:
                lazy_html = lazy_path.read_text(encoding="utf-8")
                if "docs_json" not in lazy_html or "embed_items" not in lazy_html:
                    violations.append(
                        f"{path}: lazy Bokeh script has no standalone embed call"
                    )
                violations.extend(
                    f"{path}: {label} in lazy Bokeh script"
                    for pattern, label in SERVER_PAGE_PATTERNS
                    if pattern.search(lazy_html)
                )
    elif "embed_items" not in html:
        violations.append(f"{path}: no standalone Bokeh embed call")

    asset_paths = page_asset_paths(html)
    if not asset_paths:
        violations.append(f"{path}: no local BokehJS bundle")
    for asset_path in asset_paths:
        if not asset_path.is_file():
            violations.append(f"{path}: missing local BokehJS bundle {asset_path}")
    return violations


def main() -> int:
    errors: list[str] = []
    bokeh_sources = 0
    bokeh_pages = 0

    for path in source_files():
        text = source_text(path)
        if has_bokeh_source(text):
            bokeh_sources += 1
        errors.extend(find_source_violations(path, text))

    for path in sorted(POSTS_DIR.rglob("*.html")):
        html = path.read_text(encoding="utf-8")
        if page_uses_bokeh(html):
            bokeh_pages += 1
        errors.extend(find_page_violations(path, html))

    if errors:
        print("standalone Bokeh check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "standalone Bokeh check passed: "
        f"{bokeh_sources} source file(s), {bokeh_pages} generated page(s); "
        "no Python server APIs, server URLs, or session metadata found"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
