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

## Execution Environments

The converter environment is separate from environments used to execute or
regenerate notebook outputs.

- Use the converter with `uv run notebooks/notebook_convert.py` or the
  topic-specific conversion scripts.
- Use topic-local environment files, such as `conda_env.yml`, `env.yml`,
  `pyproject.toml`, or `uv.lock`, when you need to run the notebook itself.
- Do not move post-specific runtime dependencies into the converter unless the
  converter code imports them directly.

## Generated Posts

Converted posts are written under `_posts/` as HTML files. When changing a
notebook-derived post, prefer editing the source notebook and rerunning the
conversion script. Manual edits to generated HTML are best kept small and
intentional.
