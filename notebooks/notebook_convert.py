#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "ipython",
#   "beautifulsoup4",
#   "nbformat",
#   "nbconvert",
#   "Pillow",
#   "PyYAML",
#   "python-slugify",
# ]
# ///
"""
Convert jupyter notebook into Jekyll blogpost.

Example usage:
```
uv run ./notebook_convert.py \
    --nbpath <filename>.ipynb \
    --date "YYYY-MM-DD" \
    --layout <layout_template> \
    --subdir <_posts subdir to move exported html to> \
    --description <Post description> \
    --image <Social preview image path> \
    --tags <List of tags>
```
"""

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

import nbformat
import yaml
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExtractOutputPreprocessor

# Get the base directory of this project relative to this script
BASE_DIR = Path(os.path.realpath(__file__)).parent.parent
GITHUB_BLOB_ROOT = "https://github.com/peterroelants/peterroelants.github.io/blob/main"
BOKEH_SITE_ASSET_ROOT = "/js/bokeh/3.9.1"
BOKEH_LAZY_LOADER_URL = "/js/notebook_bokeh_lazy.js"
BOKEH_LAZY_TAG = "lazy-bokeh"
STATIC_OUTPUT_URL_ROOT = "/images/notebook_outputs"
BOKEH_LAZY_ASSET_ROOT = STATIC_OUTPUT_URL_ROOT
BOKEH_CDN_URL_RE = re.compile(
    r"https://cdn\.bokeh\.org/bokeh/release/bokeh-(?:(?P<component>gl|widgets|tables|mathjax)-)?3\.9\.1\.min\.js"
)
BOKEH_LOCAL_URL_RE = re.compile(
    rf"{re.escape(BOKEH_SITE_ASSET_ROOT)}/[A-Za-z0-9._-]+\.js"
)
JEKYLL_POST_URL_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((\{% post_url [^%]+%\}(?:#[^)]+)?)\)"
)
STATIC_OUTPUT_HASH_LENGTH = 12
STATIC_OUTPUT_MIME_TYPES = {"image/png", "image/jpeg", "image/svg+xml"}
EMBEDDED_MEDIA_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/svg+xml": ".svg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/avif": ".avif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/ogg": ".ogv",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/webm": ".weba",
}
DATA_URI_RE = re.compile(
    r"^data:(?P<mime>[^;,]+)(?:;[^;,]*)*;base64,(?P<data>.*)$",
    re.DOTALL,
)


def escape_liquid_control_sequences(text: str) -> str:
    """Preserve literal Liquid-looking text in code and script output."""
    return text.replace("{%", "{% raw %}{%{% endraw %}").replace(
        "{{", "{% raw %}{{{% endraw %}"
    )


def escape_liquid_control_sequences_in_code(soup: BeautifulSoup) -> None:
    """
    Escape Liquid delimiters in notebook code/script/pre output.

    Jekyll still processes Liquid in prose links and front matter, but large
    notebook outputs such as Bokeh JavaScript can contain literal `{%` text.
    """
    for tag in soup.select("code, pre, script, style"):
        for node in list(tag.descendants):
            if not isinstance(node, NavigableString):
                continue
            escaped = escape_liquid_control_sequences(str(node))
            if escaped != str(node):
                node.replace_with(NavigableString(escaped))


def add_classes(tag: Tag, class_names: list[str]) -> None:
    """Add CSS classes while preserving any classes already present."""
    existing_classes = tag.get("class")
    if isinstance(existing_classes, str):
        classes = existing_classes.split()
    elif isinstance(existing_classes, list):
        classes = [str(class_name) for class_name in existing_classes]
    else:
        classes = []
    tag["class"] = " ".join([*classes, *class_names])


def preserve_jekyll_post_url_links(notebook):
    """
    Render Markdown links with Jekyll post_url tags as raw HTML anchors.

    Modern notebook Markdown renderers do not always recognize Liquid tags as
    valid Markdown link hrefs, but Jekyll should still process the tag after the
    notebook has been converted to HTML.
    """
    for cell in notebook.cells:
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", "")
        cell["source"] = JEKYLL_POST_URL_LINK_RE.sub(r'<a href="\2">\1</a>', source)
    return notebook


def preserve_output_alt_text(soup: BeautifulSoup, notebook) -> None:
    """Apply notebook output alt text to the corresponding rendered figures.

    ``nbconvert`` applies output metadata to raster images, but older SVG
    rendering paths can fall back to a generic description. The HTML exporter
    emits output areas in notebook output order, so use that order to apply the
    source metadata to rendered images and inline SVGs.
    """
    notebook_outputs = [
        output for cell in notebook.cells for output in cell.get("outputs", [])
    ]
    output_areas = soup.select("div.output_area")
    for output_area, output in zip(output_areas, notebook_outputs, strict=False):
        metadata = output.get("metadata") or {}
        alt_text = metadata.get("alt")
        if not isinstance(alt_text, str) or not alt_text.strip():
            continue

        for image in output_area.find_all("img"):
            image["alt"] = alt_text
        for svg in output_area.find_all("svg"):
            svg["role"] = "img"
            svg["aria-label"] = alt_text


class ExtractStaticImagePreprocessor(ExtractOutputPreprocessor):
    """Extract static images and expose SVG filenames to nbconvert's template."""

    def preprocess_cell(self, cell, resources, cell_index):
        cell, resources = super().preprocess_cell(cell, resources, cell_index)
        for output in cell.get("outputs", []):
            filenames = (output.get("metadata") or {}).get("filenames") or {}
            svg_filename = filenames.get("image/svg+xml")
            if svg_filename:
                # The classic nbconvert template uses this legacy attribute for SVG.
                output["svg_filename"] = svg_filename
        return cell, resources


def notebook_asset_id(nb_filepath: Path) -> str:
    """Return a stable asset namespace for a notebook path."""
    repo_root = BASE_DIR.resolve()
    notebooks_dir = (repo_root / "notebooks").resolve()
    try:
        relative_path = nb_filepath.resolve().relative_to(notebooks_dir)
    except ValueError:
        relative_path = Path(nb_filepath.name)

    path_without_suffix = relative_path.with_suffix("")
    safe_parts = [
        re.sub(r"[^A-Za-z0-9._-]+", "-", part).strip("-") or "notebook"
        for part in path_without_suffix.parts
    ]
    return "/".join(safe_parts)


def write_site_asset(filename: str, data: bytes | str) -> None:
    """Write one generated asset while keeping it inside the repository."""
    relative_path = Path(filename.lstrip("/"))
    repo_root = BASE_DIR.resolve()
    output_path = (repo_root / relative_path).resolve()
    try:
        output_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(
            f"Generated asset path escapes the repository: {filename}"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    output_path.write_bytes(data)


def asset_bytes(data: bytes | str) -> bytes:
    """Return generated asset data as bytes for hashing and writing."""
    if isinstance(data, str):
        return data.encode("utf-8")
    return data


def content_hashed_filename(filename: str, data: bytes | str) -> str:
    """Add a short content hash before an asset filename's extension."""
    path = Path(filename)
    digest = hashlib.sha256(asset_bytes(data)).hexdigest()[:STATIC_OUTPUT_HASH_LENGTH]
    return (path.parent / f"{path.stem}-{digest}{path.suffix}").as_posix()


def hash_extracted_output_filenames(resources: dict) -> dict[str, str]:
    """Hash extracted output filenames and return old-to-new path mappings."""
    output_resources = resources.get("outputs", {})
    replacements: dict[str, str] = {}
    hashed_resources = {}
    for filename, data in output_resources.items():
        if not isinstance(filename, str) or not filename.startswith(
            f"{STATIC_OUTPUT_URL_ROOT}/"
        ):
            hashed_resources[filename] = data
            continue

        hashed_filename = content_hashed_filename(filename, data)
        replacements[filename] = hashed_filename
        hashed_resources[hashed_filename] = data

    resources["outputs"] = hashed_resources
    return replacements


def rewrite_extracted_output_references(html: str, replacements: dict[str, str]) -> str:
    """Rewrite HTML references after extracted output names are hashed."""
    for old_filename, new_filename in replacements.items():
        html = html.replace(old_filename, new_filename)
    return html


def notebook_asset_directory(nb_filepath: Path) -> Path:
    """Return the exact generated-asset directory for one notebook."""
    asset_root = (BASE_DIR / STATIC_OUTPUT_URL_ROOT.lstrip("/")).resolve()
    asset_directory = (asset_root / notebook_asset_id(nb_filepath)).resolve()
    try:
        asset_directory.relative_to(asset_root)
    except ValueError as exc:
        raise ValueError(
            "Notebook asset directory escapes the generated asset root: "
            f"{asset_directory}"
        ) from exc
    return asset_directory


def clear_notebook_assets(nb_filepath: Path) -> None:
    """Remove only the generated asset namespace for one notebook."""
    asset_directory = notebook_asset_directory(nb_filepath)
    if asset_directory.is_symlink() or (
        asset_directory.exists() and not asset_directory.is_dir()
    ):
        raise ValueError(f"Generated asset path is not a directory: {asset_directory}")
    if asset_directory.is_dir():
        shutil.rmtree(asset_directory)


def write_extracted_outputs(resources: dict) -> int:
    """Write native nbconvert output resources into the site's asset tree."""
    output_resources = resources.get("outputs", {})
    written_count = 0
    for filename, data in output_resources.items():
        if not isinstance(filename, str) or not filename.startswith(
            f"{STATIC_OUTPUT_URL_ROOT}/"
        ):
            continue

        write_site_asset(filename, data)
        written_count += 1

    return written_count


def externalize_embedded_media(
    soup: BeautifulSoup, nb_filepath: Path
) -> dict[str, bytes]:
    """Extract supported base64 media URLs from notebook HTML outputs."""
    asset_id = notebook_asset_id(nb_filepath)
    extracted_assets: dict[str, bytes] = {}
    for output_index, output_area in enumerate(soup.select("div.output_area")):
        media_index = 0
        for media_tag in output_area.find_all(["img", "video", "audio", "source"]):
            src = media_tag.get("src")
            if not isinstance(src, str):
                continue

            match = DATA_URI_RE.match(src)
            if match is None:
                continue

            mime_type = match.group("mime").lower()
            extension = EMBEDDED_MEDIA_EXTENSIONS.get(mime_type)
            if extension is None:
                continue

            encoded_data = re.sub(r"\s+", "", match.group("data"))
            try:
                media_data = base64.b64decode(encoded_data, validate=True)
            except (ValueError, binascii.Error) as exc:
                raise ValueError(
                    f"Invalid base64 media data in notebook output ({mime_type})"
                ) from exc

            filename = (
                f"{STATIC_OUTPUT_URL_ROOT}/{asset_id}/"
                f"media-{output_index:04d}-{media_index:02d}"
                f"-{hashlib.sha256(media_data).hexdigest()[:STATIC_OUTPUT_HASH_LENGTH]}"
                f"{extension}"
            )
            media_tag["src"] = filename
            extracted_assets[filename] = media_data
            media_index += 1

    return extracted_assets


def configure_static_output_extraction(
    exporter: HTMLExporter, nb_filepath: Path
) -> None:
    """Configure nbconvert to reference static files for image outputs."""
    asset_id = notebook_asset_id(nb_filepath)
    preprocessor = ExtractStaticImagePreprocessor()
    preprocessor.extract_output_types = STATIC_OUTPUT_MIME_TYPES
    preprocessor.output_filename_template = (
        f"{STATIC_OUTPUT_URL_ROOT}/{asset_id}/"
        "figure-{cell_index:04d}-{index:02d}{extension}"
    )
    exporter.register_preprocessor(preprocessor, enabled=True)


def nb2html(nb_filepath: Path, externalize_media: bool = False) -> str:
    """
    Convert notebook to html string.
    """
    notebook = nbformat.read(nb_filepath, as_version=4)
    notebook = preserve_jekyll_post_url_links(notebook)
    exporter = HTMLExporter(template_name="classic")
    # Use simple `nbconvert` provided template that excludes css and js.
    exporter.template_file = "base.html.j2"
    if externalize_media:
        configure_static_output_extraction(exporter, nb_filepath)
    output, resources = exporter.from_notebook_node(notebook)
    resource_replacements = {}
    if externalize_media:
        resource_replacements = hash_extracted_output_filenames(resources)
        output = rewrite_extracted_output_references(output, resource_replacements)
    extracted_count = 0
    soup = BeautifulSoup(output, "html.parser")
    embedded_assets = {}
    if externalize_media:
        embedded_assets = externalize_embedded_media(soup, nb_filepath)
        # Cleanup happens only after conversion and extraction have succeeded,
        # so a failed conversion does not destroy the previous asset set.
        clear_notebook_assets(nb_filepath)
        extracted_count += write_extracted_outputs(resources)
        for filename, data in embedded_assets.items():
            write_site_asset(filename, data)
        extracted_count += len(embedded_assets)
        print(f"extracted media outputs: {extracted_count}")
    preserve_output_alt_text(soup, notebook)
    return str(soup)


def insert_collapse_buttons(soup: BeautifulSoup) -> None:
    """
    Insert the collapse buttons on the code input field.
    If the input field ends with a line with only `#` it gets
    collapsed by default.

    Effect:
        Changes soup object to have the collapse buttons.
    """
    input_areas = soup.select("div.inner_cell > div.input_area")
    for input_area in input_areas:
        # Add the collapse/expand button
        collapse_expand_button_tag = soup.new_tag("div")
        collapse_expand_button_tag["class"] = "collapse_expand_button fa-1x"
        input_area.insert(0, collapse_expand_button_tag)
        # Collapse if needed (annotated by `#` on last line)
        span_tags = input_area.find_all("span")
        if span_tags and span_tags[-1].get_text(strip=True) == "#":
            add_classes(tag=input_area, class_names=["collapsed"])


def get_title(soup: BeautifulSoup) -> str:
    """
    Get the notebook title from the first h1 element.
    """
    h1_tag = soup.find("h1")
    if h1_tag is None:
        msg = "Converted notebook HTML does not contain an h1 title."
        raise RuntimeError(msg)
    if h1_tag.contents:
        return str(h1_tag.contents[0]).strip()
    return h1_tag.get_text(strip=True)


def remove_output_stderr(soup: BeautifulSoup) -> None:
    """
    Remove stderr-only output areas from the notebook outputs.

    If an output area contains both stderr and another output subarea, remove
    only the stderr subarea so that normal text, HTML, and figures are kept.

    Effect:
        Changes soup object to have stderr output removed without leaving empty
        output-area containers in the generated post.
    """
    for stderr_tag in soup.select("div.output_stderr"):
        output_area = stderr_tag.find_parent("div", class_="output_area")
        if output_area is None:
            stderr_tag.decompose()
            continue

        output_subareas = output_area.find_all(
            "div", class_="output_subarea", recursive=False
        )
        normal_subareas = [
            subarea
            for subarea in output_subareas
            if "output_stderr" not in (subarea.get("class") or [])
        ]
        if normal_subareas:
            stderr_tag.decompose()
        else:
            output_area.decompose()


def externalize_bokeh_resources(soup: BeautifulSoup) -> None:
    """Replace inline or supported CDN BokehJS with version-pinned site bundles."""
    replacements = {
        "bokeh.min.js": f"{BOKEH_SITE_ASSET_ROOT}/bokeh.min.js",
        "bokeh-widgets.min.js": f"{BOKEH_SITE_ASSET_ROOT}/bokeh-widgets.min.js",
    }
    marker_re = re.compile(
        r"/\* BEGIN (bokeh(?:-gl|-widgets|-tables|-mathjax)?\.min\.js) \*/"
    )

    for script in list(soup.find_all("script")):
        script_text = script.get_text()
        marker_match = marker_re.search(script_text)
        if marker_match:
            filename = marker_match.group(1)
            if filename in replacements:
                replacement = soup.new_tag("script", src=replacements[filename])
                script.replace_with(replacement)
            else:
                script.decompose()
            continue

        def replace_bokeh_cdn_url(match: re.Match[str]) -> str:
            component = match.group("component")
            filename = f"bokeh-{component}.min.js" if component else "bokeh.min.js"
            return f"{BOKEH_SITE_ASSET_ROOT}/{filename}"

        updated_script_text = BOKEH_CDN_URL_RE.sub(replace_bokeh_cdn_url, script_text)
        if updated_script_text != script_text:
            script.clear()
            script.append(updated_script_text)


def cell_tags(cell: dict) -> list[str]:
    """Return standard Jupyter cell tags as strings."""
    tags = (cell.get("metadata") or {}).get("tags", [])
    if not isinstance(tags, list):
        return []
    return [tag for tag in tags if isinstance(tag, str)]


def tagged_value(tags: list[str], prefix: str) -> str | None:
    """Return the value from the first cell tag with the requested prefix."""
    for tag in tags:
        if tag.startswith(prefix):
            value = tag.removeprefix(prefix).strip()
            if value:
                return value
    return None


def lazy_bokeh_cell_height(tags: list[str]) -> int | None:
    """Return an optional positive placeholder height from a cell tag."""
    value = tagged_value(tags, f"{BOKEH_LAZY_TAG}-height=")
    if value is None:
        return None
    try:
        height = int(value)
    except ValueError as exc:
        raise ValueError(
            f"{BOKEH_LAZY_TAG}-height must be a positive integer, got {value!r}"
        ) from exc
    if height <= 0:
        raise ValueError(f"{BOKEH_LAZY_TAG}-height must be positive, got {height}")
    return height


def script_contents(script: Tag) -> str:
    """Return script source reliably across BeautifulSoup script node types."""
    return str(script.string or script.get_text())


def local_bokeh_bundle_urls(soup: BeautifulSoup) -> list[str]:
    """Return the local BokehJS bundle URLs referenced by a rendered page."""
    urls: list[str] = []
    for script in soup.find_all("script"):
        candidates = []
        src = script.get("src")
        if isinstance(src, str):
            candidates.append(src)
        candidates.extend(BOKEH_LOCAL_URL_RE.findall(script_contents(script)))
        for url in candidates:
            if url not in urls:
                urls.append(url)
    return urls


def standalone_bokeh_scripts(
    output_container: Tag, bundle_urls: list[str]
) -> tuple[list[str], list[str]]:
    """Return local Bokeh bundles and embed scripts from one notebook cell."""
    scripts = output_container.find_all("script")
    embed_scripts = [
        script
        for script in scripts
        if "docs_json" in script_contents(script)
        and "embed_items" in script_contents(script)
    ]
    if not embed_scripts:
        return [], []

    server_markers = (
        "server_id",
        "session_id",
        "DEFAULT_SERVER_WEBSOCKET_URL",
        "ws://",
        "wss://",
        "server_document",
        "server_session",
    )
    output_text = str(output_container)
    if any(marker in output_text for marker in server_markers):
        raise ValueError(
            f"Tagged {BOKEH_LAZY_TAG} output contains Bokeh server/session metadata"
        )

    root = output_container.select_one("[data-root-id]")
    if not isinstance(root, Tag) or not root.get("id"):
        raise ValueError(
            f"Tagged {BOKEH_LAZY_TAG} output has no identifiable Bokeh root element"
        )

    if not bundle_urls:
        raise ValueError(
            f"Tagged {BOKEH_LAZY_TAG} output has no local BokehJS bundle references"
        )
    inline_scripts = [script_contents(script) for script in embed_scripts]
    return bundle_urls, inline_scripts


def all_bokeh_outputs_are_lazy(soup: BeautifulSoup) -> bool:
    """Return whether every rendered Bokeh output belongs to a tagged cell."""
    bokeh_cells = []
    for cell in soup.select("div.cell"):
        has_root = cell.select_one("[data-root-id]") is not None
        has_embed = any(
            "docs_json" in script_contents(script)
            and "embed_items" in script_contents(script)
            for script in cell.find_all("script")
        )
        if has_root or has_embed:
            bokeh_cells.append(cell)
    return bool(bokeh_cells) and all(
        "celltag_lazy-bokeh" in (cell.get("class") or []) for cell in bokeh_cells
    )


def remove_eager_bokeh_loaders(soup: BeautifulSoup) -> None:
    """Remove page-level Bokeh resource loaders when all outputs are lazy."""
    local_urls = set(local_bokeh_bundle_urls(soup))
    if not local_urls or not all_bokeh_outputs_are_lazy(soup):
        return

    for script in soup.find_all("script"):
        script_text = script_contents(script)
        if "js_urls" in script_text and any(url in script_text for url in local_urls):
            script.decompose()


def extract_lazy_bokeh_outputs(
    soup: BeautifulSoup,
    notebook: dict,
    nb_filepath: Path,
    clear_assets: bool,
) -> int:
    """Extract standalone Bokeh outputs from cells tagged ``lazy-bokeh``."""
    tagged_cells = [
        (cell_index, cell)
        for cell_index, cell in enumerate(notebook.get("cells", []))
        if BOKEH_LAZY_TAG in cell_tags(cell)
    ]
    if not tagged_cells:
        return 0

    bundle_urls = local_bokeh_bundle_urls(soup)
    # Remove a page-level output_notebook loader before extracting the embeds;
    # otherwise it would eagerly load BokehJS and defeat lazy loading.
    remove_eager_bokeh_loaders(soup)

    if clear_assets:
        clear_notebook_assets(nb_filepath)

    asset_id = notebook_asset_id(nb_filepath)
    extracted_count = 0
    rendered_tagged_cells = [
        cell
        for cell in soup.select("div.cell")
        if "celltag_lazy-bokeh" in (cell.get("class") or [])
    ]
    if len(rendered_tagged_cells) != len(tagged_cells):
        raise ValueError(
            f"Found {len(rendered_tagged_cells)} rendered tagged Bokeh cells, "
            f"but the notebook contains {len(tagged_cells)}"
        )

    for tagged_index, (cell_index, cell) in enumerate(tagged_cells):
        cell_id = cell.get("id")
        if isinstance(cell_id, str) and cell_id:
            rendered_cell = soup.find("div", id=f"cell-id={cell_id}")
        else:
            # Older notebooks may predate nbformat's cell-id requirement. The
            # converter's rendered tag class gives those cells a deterministic
            # fallback without rewriting the source notebook format.
            rendered_cell = rendered_tagged_cells[tagged_index]
        if rendered_cell is None:
            raise ValueError(
                f"Could not find rendered HTML for tagged cell {cell_id or cell_index}"
            )

        output_areas = rendered_cell.select("div.output_area")
        transformed = 0
        tags = cell_tags(cell)
        height = lazy_bokeh_cell_height(tags)
        title = tagged_value(tags, f"{BOKEH_LAZY_TAG}-title=") or (
            "Interactive Bokeh visualization"
        )
        bundles, inline_scripts = standalone_bokeh_scripts(rendered_cell, bundle_urls)
        if not inline_scripts:
            raise ValueError(
                f"Tagged {BOKEH_LAZY_TAG} output has no inline embed script"
            )

        bokeh_subareas = [
            subarea
            for output_area in output_areas
            for subarea in output_area.select("div.output_subarea")
            if subarea.select_one("[data-root-id]") is not None
            or any(
                "docs_json" in script_contents(script)
                and "embed_items" in script_contents(script)
                for script in subarea.find_all("script")
            )
        ]
        if not bokeh_subareas:
            raise ValueError(f"Cell {cell_id!r} has no identifiable Bokeh output areas")
        root_elements = [
            root
            for subarea in bokeh_subareas
            for root in subarea.select("[data-root-id]")
        ]

        script_content = "(function() {\n" + "\n\n".join(inline_scripts)
        script_content += "\n})();\n"
        filename = (
            f"{BOKEH_LAZY_ASSET_ROOT}/{asset_id}/interactive-{extracted_count:04d}.js"
        )
        hashed_filename = content_hashed_filename(filename, script_content)
        write_site_asset(hashed_filename, script_content)

        placeholder = soup.new_tag(
            "div",
            attrs={
                "class": "notebook-bokeh-lazy",
                "data-bokeh-script": hashed_filename,
                "data-bokeh-bundles": json.dumps(
                    bundles,
                    separators=(",", ":"),
                ),
                "data-bokeh-title": title,
            },
        )
        if height is not None:
            placeholder["style"] = f"min-height: {height}px;"

        status = soup.new_tag(
            "p",
            attrs={"class": "notebook-bokeh-lazy-status", "aria-live": "polite"},
        )
        status.string = "Interactive visualization loading…"
        placeholder.append(status)

        target_output_area = bokeh_subareas[0].find_parent("div", class_="output_area")
        for root in root_elements:
            root.extract()
        for subarea in bokeh_subareas:
            subarea.decompose()
        if target_output_area is None:
            raise ValueError(f"Cell {cell_id!r} has no Bokeh output container")
        for root in root_elements:
            placeholder.append(root)
        target_output_area.append(placeholder)
        transformed += 1
        extracted_count += 1

        if transformed == 0:
            raise ValueError(
                f"Cell {cell_id!r} tagged {BOKEH_LAZY_TAG} has no standalone Bokeh output"
            )

    return extracted_count


def add_lazy_bokeh_loader(soup: BeautifulSoup) -> None:
    """Add the shared browser-side lazy Bokeh loader when needed."""
    if not soup.select_one("[data-bokeh-script]"):
        return
    loader_url = lazy_bokeh_loader_url()
    for script in soup.find_all("script"):
        src = script.get("src")
        if (
            isinstance(src, str)
            and src.split("?", maxsplit=1)[0] == BOKEH_LAZY_LOADER_URL
        ):
            return
    loader = soup.new_tag("script", src=loader_url)
    loader["defer"] = ""
    soup.append(loader)


def lazy_bokeh_loader_url() -> str:
    """Return the shared loader URL with a content-hash cache key."""
    loader_path = BASE_DIR / BOKEH_LAZY_LOADER_URL.lstrip("/")
    try:
        digest = hashlib.sha256(loader_path.read_bytes()).hexdigest()[:12]
    except OSError as exc:
        raise RuntimeError(f"Could not read lazy Bokeh loader {loader_path}") from exc
    return f"{BOKEH_LAZY_LOADER_URL}?v={digest}"


def set_anchor_links(soup: BeautifulSoup) -> None:
    """
    Set the anchor links to link symbol

    Effect:
        Change anchor-link content to link symbol.
    """
    for a_tag in soup.find_all("a", {"class": "anchor-link"}):
        # Remove previous content
        a_tag.string = ""
        # Insert link symbol as tag
        a_tag.append(soup.new_tag("i", attrs={"class": "fa-solid fa-sm fa-link"}))


def add_table_class(soup: BeautifulSoup) -> None:
    """
    Add `.table` class to table dataframe.
    Now pandas tables are visualised by html `<table class="dataframe">`. To
     be able to use bootstrap tables they need to have the `.table` class.
     https://getbootstrap.com/docs/4.0/content/tables/

    Effect:
        Changes dataframe tables to include Bootstrap table classes.
    """
    for table in soup.find_all("table", {"class": "dataframe"}):
        add_classes(
            tag=table,
            class_names=["table", "table-sm", "table-hover", "w-auto", "text-right"],
        )
        # Add table container class to parent
        if isinstance(table.parent, Tag):
            add_classes(tag=table.parent, class_names=["contains-table"])


def parse_svg_length(value: str | None) -> int | None:
    """Parse a numeric SVG length when it can be used as an HTML dimension."""
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(?:px)?\s*", value)
    if match is None:
        return None
    dimension = round(float(match.group(1)))
    return dimension if dimension > 0 else None


def svg_dimensions(image_path: Path) -> tuple[int, int] | None:
    """Read SVG width and height, falling back to its viewBox."""
    try:
        svg_text = image_path.read_text(encoding="utf-8")[:16_384]
    except (OSError, UnicodeDecodeError):
        return None

    root_match = re.search(r"<svg\b(?P<attributes>[^>]*)>", svg_text, re.IGNORECASE)
    if root_match is None:
        return None
    attributes = root_match.group("attributes")

    def attribute(name: str) -> str | None:
        match = re.search(rf"\b{name}\s*=\s*(['\"])(.*?)\1", attributes, re.IGNORECASE)
        return match.group(2) if match else None

    width = parse_svg_length(attribute("width"))
    height = parse_svg_length(attribute("height"))
    if width and height:
        return width, height

    view_box = attribute("viewBox")
    if view_box:
        values = re.findall(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", view_box)
        if len(values) == 4:
            view_width = round(float(values[2]))
            view_height = round(float(values[3]))
            if view_width > 0 and view_height > 0:
                return view_width, view_height
    return None


def local_image_dimensions(image_path: Path, image_reader) -> tuple[int, int] | None:
    """Return intrinsic dimensions for a local raster image or SVG."""
    if image_path.suffix.lower() == ".svg":
        return svg_dimensions(image_path)
    if image_reader is None:
        return None
    try:
        with image_reader.open(image_path) as image:
            width, height = image.size
            return int(width), int(height)
    except (OSError, ValueError, TypeError):
        return None


def enrich_images(soup: BeautifulSoup, add_dimensions: bool, base_dir: Path) -> None:
    """
    Ensure all <img> tags have lazy-loading and async decoding.
    Optionally add width/height for local images to reduce layout shift.

    Effect:
        Mutates soup in-place.
    """
    # Import Pillow only when dimensions are requested. It is a converter
    # dependency, so this remains independent of the notebook environments.
    Image = None
    if add_dimensions:
        try:
            from PIL import Image as PILImage

            Image = PILImage
        except ImportError:
            Image = None  # Pillow not available; skip dimensions silently

    for img in soup.find_all("img"):
        # Add lazy-loading and async decoding if missing
        if not img.has_attr("loading"):
            img["loading"] = "lazy"
        if not img.has_attr("decoding"):
            img["decoding"] = "async"

        # Optionally add width/height for local images
        if add_dimensions:
            src = img.get("src", "")
            if isinstance(src, str) and src.startswith("/images/"):
                img_path = base_dir / src.split("?", maxsplit=1)[0].lstrip("/")
                dimensions = local_image_dimensions(img_path, Image)
                if dimensions:
                    width, height = dimensions
                    if not img.has_attr("width"):
                        img["width"] = str(width)
                    if not img.has_attr("height"):
                        img["height"] = str(height)


def get_notebook_source_url(nbpath: Path) -> str:
    """Return the GitHub source URL for a notebook path."""
    try:
        rel_path = nbpath.resolve().relative_to(BASE_DIR)
    except ValueError:
        rel_path = nbpath
    return f"{GITHUB_BLOB_ROOT}/{rel_path.as_posix()}"


def add_notebook_source_note(soup: BeautifulSoup, nbpath: Path) -> None:
    """Append a standard source note for notebook-generated posts."""
    cell = soup.new_tag(
        "div", attrs={"class": "cell border-box-sizing text_cell rendered"}
    )
    prompt = soup.new_tag("div", attrs={"class": "prompt input_prompt"})
    inner_cell = soup.new_tag("div", attrs={"class": "inner_cell"})
    rendered = soup.new_tag(
        "div", attrs={"class": "text_cell_render border-box-sizing rendered_html"}
    )
    paragraph = soup.new_tag("p")

    notebook_link = soup.new_tag("a", href=get_notebook_source_url(nbpath=nbpath))
    notebook_link.string = "Link to the full IPython notebook file"

    paragraph.append("This post is generated from an IPython notebook file. ")
    paragraph.append(notebook_link)

    rendered.append(paragraph)
    inner_cell.append(rendered)
    cell.append(prompt)
    cell.append(inner_cell)
    body = soup.find("body")
    if isinstance(body, Tag):
        body.append(cell)
    else:
        soup.append(cell)


def get_front_matter(args: argparse.Namespace, title: str) -> str:
    """
    Return Jekyll Front-Matter metadata.

    Front-Matter is YAML formatted.
    """
    dct = {
        "layout": args.layout,
        "title": title,
        "description": args.description,
        "tags": args.tags,
    }
    if args.image:
        dct["image"] = args.image
    if args.last_modified_at:
        dct["last_modified_at"] = args.last_modified_at
    if args.updates:
        dct["updates"] = args.updates
    if args.redirect_from:
        dct["redirect_from"] = args.redirect_from
    header_str = "\n".join(
        [
            "---",
            yaml.safe_dump(
                dct,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                width=2147483647,
            ).rstrip("\n"),
            "---",
            "",
        ]
    )
    return header_str


def parse_update(value: str) -> dict[str, str]:
    """Parse one post-history entry from DATE|TITLE|DESCRIPTION text."""
    parts = [part.strip() for part in value.split("|", maxsplit=2)]
    if len(parts) < 2 or not parts[0] or not parts[1]:
        msg = "updates must use DATE|TITLE or DATE|TITLE|DESCRIPTION"
        raise argparse.ArgumentTypeError(msg)

    update = {"date": parts[0], "title": parts[1]}
    if len(parts) == 3 and parts[2]:
        update["description"] = parts[2]
    return update


def add_jekyll_header(html_str: str, args: argparse.Namespace, title: str) -> str:
    """
    Add the Jekyll header to the given html (as str).
    """
    header = get_front_matter(args, title)
    return f"{header}\n{html_str}"


def strip_trailing_whitespace(html_str: str) -> str:
    """Remove insignificant line-end whitespace from generated HTML."""
    return "\n".join(line.rstrip() for line in html_str.splitlines())


def save_conversion(html_str: str, nbpath: Path, date: str, subdir: str = "") -> None:
    """
    Save converted notebook file to Jekyll templated html file.

    args:
        html_str (str): Jekyll templated html str.
        nbpath (str): Filepath of original notebook file.
        date (str): Blogpost orginal publishing date (YYYY-MM-DD)

    Effect:

    """
    filename = nbpath.stem
    output_path = BASE_DIR / "_posts" / subdir / f"{date}-{filename}.html"
    print(f"conversion output path: {output_path!s}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(html_str)


def get_arguments() -> argparse.ArgumentParser:
    """Get input arguments"""
    parser = argparse.ArgumentParser(description="Convert notebook to Jekyll blogpost.")
    parser.add_argument(
        "--nbpath", type=str, help="File path of notebook file to convert to blogpost"
    )
    parser.add_argument(
        "--date", type=str, help="Date of original publication of post."
    )
    parser.add_argument(
        "--layout",
        type=str,
        help="Layout template name to use as Jekyll layout for blogpost.",
    )
    parser.add_argument("--description", type=str, help="Description of the blogpost.")
    parser.add_argument(
        "--image",
        type=str,
        default="",
        help="Social preview image path for the generated post front matter.",
    )
    parser.add_argument(
        "--last_modified_at",
        type=str,
        default="",
        help="Substantive modification date for the generated post sitemap entry.",
    )
    parser.add_argument(
        "--subdir", type=str, default="", help="Sub directory of base dir to put post."
    )
    parser.add_argument(
        "--tags", nargs="+", type=str, default=[], help="Tags related to the post."
    )
    parser.add_argument(
        "--redirect_from",
        nargs="*",
        default=[],
        help="Legacy paths that should redirect to the generated post.",
    )
    parser.add_argument(
        "--update",
        dest="updates",
        action="append",
        type=parse_update,
        default=[],
        help=("Major update in DATE|TITLE|DESCRIPTION format. Can be repeated."),
    )
    parser.add_argument(
        "--add_img_dimensions",
        action="store_true",
        help=(
            "If set, add width/height to local images; this is also enabled "
            "automatically with --externalize_media."
        ),
    )
    parser.add_argument(
        "--add_notebook_source_note",
        action="store_true",
        help=(
            "If set, append a footer linking to the generated post and source notebook."
        ),
    )
    parser.add_argument(
        "--externalize_bokeh",
        action="store_true",
        help=("If set, replace CDN BokehJS with site bundles."),
    )
    parser.add_argument(
        "--lazy_bokeh",
        action="store_true",
        help=(
            "If set, extract standalone Bokeh outputs from cells tagged "
            f"{BOKEH_LAZY_TAG} and load them on demand."
        ),
    )
    parser.add_argument(
        "--externalize_media",
        "--externalize_static_images",
        dest="externalize_media",
        action="store_true",
        help=("If set, extract supported notebook media into site asset files."),
    )
    return parser


def run(args: argparse.Namespace):
    """Run conversion script."""
    nb_path = Path(args.nbpath)
    print(f"\nConverting: {nb_path!s}")
    notebook = nbformat.read(nb_path, as_version=4)
    # Convert notebook into html
    html_str = nb2html(nb_path, externalize_media=args.externalize_media)
    soup = BeautifulSoup(html_str, "html.parser")
    # Create Title, cell collapse buttons, remove stderr, pandas tables
    insert_collapse_buttons(soup)
    title = get_title(soup)
    print("title: ", title)
    remove_output_stderr(soup)
    if args.externalize_bokeh or args.lazy_bokeh:
        externalize_bokeh_resources(soup)
    if args.lazy_bokeh:
        extracted_count = extract_lazy_bokeh_outputs(
            soup,
            notebook,
            nb_path,
            clear_assets=not args.externalize_media,
        )
        if extracted_count:
            print(f"extracted lazy Bokeh outputs: {extracted_count}")
        add_lazy_bokeh_loader(soup)
    add_table_class(soup)
    set_anchor_links(soup)
    escape_liquid_control_sequences_in_code(soup)
    # Enrich images with lazy-loading/decoding and optional dimensions
    enrich_images(
        soup,
        add_dimensions=args.add_img_dimensions or args.externalize_media,
        base_dir=BASE_DIR,
    )
    if args.add_notebook_source_note:
        add_notebook_source_note(soup, nbpath=nb_path)
    # Do not use `prettify()` here: it inserts indentation whitespace around
    # inline tags, which can render as spaces before punctuation after links.
    html_str = strip_trailing_whitespace(soup.decode(formatter="html"))
    # Add Jekyll header
    html_str = add_jekyll_header(html_str, args, title)
    # Export
    save_conversion(html_str, nb_path, args.date, args.subdir)


def main():
    parser = get_arguments()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
