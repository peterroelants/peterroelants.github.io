# Notebook Workflow

Responsibility: this document is the notebook workflow guide. Keep notebook
conversion commands, converter setup, and the boundary between conversion
tooling and per-post execution environments here. Keep site architecture in
`build_info/site_overview.md`, Jekyll/GitHub Pages commands in
`build_info/jekyll.md`, and agent-specific behavior in `AGENTS.md`.

## Canonical Converter

Use `notebooks/notebook_convert.py` as the canonical converter for
notebook-derived posts. Run it with `uv run`; the converter dependencies are
declared in the script metadata at the top of that file.

From a notebook topic directory:
```sh
uv run ../notebook_convert.py --nbpath <notebook>.ipynb --date YYYY-MM-DD --layout post --subdir <_posts-subdir>
```

From the repository root:
```sh
uv run ./notebooks/notebook_convert.py --nbpath notebooks/<topic>/<notebook>.ipynb --date YYYY-MM-DD --layout post --subdir <_posts-subdir>
```

Prefer the existing `*_convert.sh` script in each topic directory when one
exists; those scripts encode the post dates, target subdirectories,
descriptions, and tags.

To strip outputs and transient execution metadata from all source notebooks before
committing or rerunning them, use:
```sh
just clear-notebooks
```

When a notebook-derived post needs visible history metadata, add `--update`
entries to the topic conversion script. The value format is
`YYYY-MM-DD|Title|Description`, and the generated front matter is rendered by
`_includes/post_history.html`.

When a notebook-derived post should show a source link footer, add
`--add_notebook_source_note` to its conversion command. Keep that footer out of
the notebook itself so the converter remains the source of truth.

When a converted post has legacy URLs, add them with `--redirect_from` in the
topic conversion script so rerunning the converter preserves those redirects.

## Static notebook outputs

For large notebook-derived posts, pass `--externalize_media` to the converter.
It extracts PNG, JPEG, and SVG notebook outputs, along with supported embedded
GIF, WebP, video, and audio data URLs, into
`images/notebook_outputs/<topic>/<notebook>/` and makes the generated post
reference them as ordinary media files. Generated filenames include a short
content hash, and the exact notebook subdirectory is replaced on each
successful conversion so stale files are not retained. Extracted images include
their intrinsic width and height to reduce layout shift. The notebook's alt-text
metadata, lazy loading, and asynchronous decoding are preserved. This changes
only the conversion output; local notebook rendering is unchanged.

Run the conversion before `just clear-notebooks` from the repository root,
because the executed notebook outputs are needed to create the static files.

`just check-generated-media` (also included in `just verify`) checks the
currently externalized posts for missing assets, inline data media, missing or
generic image alt text, missing dimensions, and orphaned generated files. The
check is intentionally limited to posts that opt into media extraction; older
posts can be migrated independently.

## Figure Accessibility

For static Matplotlib figures included in generated posts, attach a concise
accessible description when displaying the figure:

```python
display(fig, metadata={"alt": "A concise description of what the figure shows."})
```

The notebook converter preserves this Jupyter metadata as the generated
image's `alt` attribute. Keep the description focused on the figure's content
or purpose, and use plain language rather than repeating the figure title.

For notebook outputs that use Bokeh, pass `--externalize_bokeh` in the topic
conversion script. The converter replaces inline BokehJS resources and
Bokeh 3.9.1 CDN loader URLs with the site's version-pinned bundles. This affects
generated web pages only; notebook execution remains controlled by the topic's
own setup and may use inline or CDN resources. The notebook environments used
by these Bokeh posts are pinned to Bokeh 3.9.1.

To lazy-load a standalone Bokeh output, add the standard Jupyter cell tag
`lazy-bokeh` and pass `--lazy_bokeh` to the converter. The converter validates
and moves only those tagged outputs into hashed JavaScript assets, then loads
them with the shared
`js/notebook_bokeh_lazy.js` browser loader when they approach the viewport.
Optional `lazy-bokeh-height=<pixels>` and `lazy-bokeh-title=<text>` tags set
the reserved placeholder height and accessible description. Untagged outputs
remain inline. This path supports standalone Bokeh output only; server-backed
output must never be published.

The focused browser regression check for this path is separate from the default
fast checks because it needs a Playwright browser. After installing the Node
dependencies and Chromium once with `npx playwright install chromium`, run
`just browser-test`. It builds the static site, verifies that the MENACE output
stays unloaded until it approaches the viewport, and checks that the interactive
controls still work. It also exercises the loader's handling of a Bokeh bundle
that is already loading.

## Browser-only Bokeh

Published Bokeh output must be standalone: the page contains the serialized
plot or app state and runs interactions in BokehJS in the visitor's browser.
Use `CustomJS` callbacks for published interactivity. `output_notebook` is fine
for local notebook rendering, but never publish output created with Bokeh server
APIs such as `bokeh serve`, `curdoc`, `server_document`, or `output_server`.

`just check-bokeh-standalone` checks Bokeh code cells and generated posts for
those server APIs, server URLs, session metadata, CDN references, and missing
local BokehJS bundles. It intentionally ignores stored notebook outputs and
Bokeh's generic client-side server-support code when no server metadata is
present; that code is part of BokehJS and does not start a Python backend.

## Execution Environments

The converter environment is separate from environments used to execute or
regenerate notebook outputs.

- Use the converter with `uv run notebooks/notebook_convert.py` or the
  topic-specific conversion scripts.
- Use topic-local environment files, such as `conda_env.yml`, `env.yml`,
  `pyproject.toml`, or `uv.lock`, when you need to run the notebook itself.
  If a topic directory has its own `README.md`, treat it as the command guide
  for that notebook environment.
- Do not move post-specific runtime dependencies into the converter unless the
  converter code imports them directly.

## Generated Posts

Converted posts are written under `_posts/` as HTML files. When changing a
notebook-derived post, prefer editing the source notebook and rerunning the
conversion script. Manual edits to generated HTML are best kept small and
intentional.
