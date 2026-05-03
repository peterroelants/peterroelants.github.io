# Peter's Notes Blog

Responsibility: this README is the public entry point for the repository. Keep
it focused on what the project is, where the important docs live, and how to get
oriented. Put architecture details in `build_info/site_overview.md`, Jekyll
command details in `build_info/jekyll.md`, notebook workflow details in
`notebooks/README.md`, and agent-specific guidance in `AGENTS.md`.

## Overview
This is my personal technical blog, written and maintained by me, focused on Machine Learning, Mathematics, and Software Engineering. The site is built with Jekyll and hosted on GitHub Pages. For more background, see the About page on the site (`/about`) and the post `_posts/2021/05/2021-05-15-about-this-blog.md`.

## Live site
- Blog: https://peterroelants.github.io/

## Documentation Map
- `build_info/site_overview.md`: Detailed architecture, rendering behavior, notebook workflow, assets, theming, and implementation notes.
- `build_info/jekyll.md`: Jekyll/GitHub Pages command reference and deployment workflow notes.
- `notebooks/README.md`: Notebook conversion workflow and the boundary between converter tooling and per-post execution environments.
- `build_info/potential_improvements.md`: Backlog-style notes for future site improvements.
- `build_info/agent_friendliness.md`: Rationale and roadmap for making the repo easier for coding agents.
- `AGENTS.md`: Short operating guide for coding agents.
- Posts describing site mechanics:
  - `_posts/2021/05/2021-05-15-about-this-blog.md` (how the site works, notebooks → posts)
  - `_posts/2021/05/2021-05-15-adding-tags-to-github-pages.md` (tagging and tag index)

## Common Tasks
- Local setup, build, serve, dependency updates, and deployment: see `build_info/jekyll.md`.
- Site architecture, content workflow, assets, theming, SEO, feeds, and analytics: see `build_info/site_overview.md`.
- Notebook conversion and per-notebook environment notes: see `notebooks/README.md`.
- Coding-agent guidance: see `AGENTS.md`.

## License
See `LICENCE`.
