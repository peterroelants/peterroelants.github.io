#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["nbformat"]
# ///
"""Remove notebook outputs and transient execution metadata in place."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat


def clear_notebook(notebook_path: Path) -> bool:
    """Clear outputs and execution metadata, returning whether it changed."""
    notebook = nbformat.read(notebook_path, as_version=4)
    changed = False

    for cell in notebook.cells:
        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True
        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True
        if "execution" in cell.get("metadata", {}):
            del cell["metadata"]["execution"]
            changed = True

    if changed:
        nbformat.write(notebook, notebook_path)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clear outputs and transient execution metadata from notebooks."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Notebook files or directories to process recursively.",
    )
    args = parser.parse_args()

    notebook_paths = {
        path
        for root in args.paths
        for path in (root.rglob("*.ipynb") if root.is_dir() else [root])
    }
    changed_count = sum(clear_notebook(path) for path in sorted(notebook_paths))
    print(f"cleared notebook metadata: {changed_count} notebook(s)")


if __name__ == "__main__":
    main()
