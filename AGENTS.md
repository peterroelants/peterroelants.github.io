# AGENTS.md

This repository is Peter Roelants' personal technical blog published at
https://peterroelants.github.io/. It is a Jekyll/GitHub Pages site with
notebook-derived posts, handwritten Markdown posts, and checked-in static assets.

Responsibility: this file is the agent-specific operating guide. It should point
agents to the right source documents and capture agent behavior that does not
belong in the human-facing README or architecture notes.

## Start Here

- Read `README.md` for the canonical project overview and navigation to deeper
  docs.
- Read `build_info/site_overview.md` for detailed architecture and site behavior.
- Read `build_info/jekyll.md` for Jekyll/GitHub Pages command details.
- Read `notebooks/README.md` before changing notebook-derived posts or
  conversion scripts.
- Keep this file as the agent-specific overlay. Do not duplicate details from
  those docs here; update the source doc instead.

## Agent Operating Notes

- Before changing a subsystem, read the relevant section of
  `build_info/site_overview.md` and inspect nearby files for the current
  pattern.
- Prefer source-of-truth edits. For notebook-derived posts, that usually means
  editing the source notebook or conversion workflow rather than large manual
  edits to generated HTML.
- If the public site mechanics or notebook workflow changes, consider whether
  `_posts/2021/05/2021-05-15-about-this-blog.md` also needs an update.
- When making a substantive change to an existing post, consider whether it
  needs an `updates` front matter entry as described in
  `build_info/site_overview.md`.
- Use the Ruby version pinned in `.ruby-version`. If Bundler is unavailable,
  install the needed Bundler version rather than rewriting dependency metadata,
  unless the user explicitly asks for a dependency update.
- Respect `.gitignore`; do not commit generated site output, dependency
  directories, or local caches.

## Verification

- Use command details from `build_info/jekyll.md` and behavior-specific context
  from `build_info/site_overview.md`.
- Prefer `just` recipes for standard setup, check, build, serve, and verification
  flows when `just` is available.
- Choose verification based on the change: build checks for templates/content,
  browser checks for layout or styling, and targeted page checks for affected
  post, tag, or notebook behavior.
- If a required check cannot run because local tooling is missing, state the
  exact command attempted and the error.

## Editing Principles

- Keep changes small and aligned with the existing Liquid, Bootstrap, and
  static-asset patterns.
- Preserve mathematical notation, code snippets, and notebook output carefully.
- Avoid large dependency or vendor-asset updates unless the task explicitly
  requires them.
