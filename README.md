Repository for my personal blog at https://peterroelants.github.io/

## Overview
This is my personal technical blog, written and maintained by me, focused on Machine Learning, Mathematics, and Software Engineering. The site is built with Jekyll and hosted on GitHub Pages. For more background, see the About page on the site (`/about`) and the post `_posts/2021/05/2021-05-15-about-this-blog.md`.

## Live site
- Blog: https://peterroelants.github.io/

## Tech stack
- Jekyll (via the `github-pages` gem)
- Liquid templating
- Bootstrap (layout/components)
- Font Awesome (icons)
- MathJax (math rendering)

## Directory structure (high level)
- `_config.yml`: Site configuration (plugins, permalink, analytics, etc.)
- `_layouts/`: Page/post layouts
- `_includes/`: Reusable HTML partials (head, navbar, footer, MathJax, etc.)
- `_posts/`: Blog posts (Markdown and notebook-converted HTML)
- `mathjax/`: Local MathJax assets
- `css/`, `js/`, `images/`, `webfonts/`: Static assets
- `build_info/`: Internal docs (site overview, Jekyll notes, improvement ideas)

## Useful docs in this repo
- Build and architecture:
  - `build_info/site_overview.md`
  - `build_info/jekyll.md`
  - `build_info/potential_improvements.md`
- Posts describing site mechanics:
  - `_posts/2021/05/2021-05-15-about-this-blog.md` (how the site works, notebooks → posts)
  - `_posts/2021/05/2021-05-15-adding-tags-to-github-pages.md` (tagging and tag index)

## Local development

See [`./build_info/jekyll.md`](./build_info/jekyll.md) for more details.

## Deployment (GitHub Pages via Actions)
- Deploys are handled by GitHub Actions: `.github/workflows/pages.yml`.
- On push to `main`, the workflow builds the site using `actions/jekyll-build-pages` and deploys with `actions/deploy-pages`.
- Ensure repo Settings → Pages → Source is set to GitHub Actions.

## Markdown and syntax highlighting
- Markdown engine: `kramdown` with `input: GFM` (GitHub Flavored Markdown).
- Syntax highlighting: Rouge.
- Math: MathJax is loaded conditionally (`page.math` or `layout.math`).

## CSS build and minification
- Tools: PostCSS (`autoprefixer`, `cssnano`). Config in `postcss.config.js`.
- First time:
```sh
npm install
```
- Build once:
```sh
npm run css:build
```
- Watch and rebuild:
```sh
npm run css:watch
```
- Notes: `cssnano` is configured conservatively to avoid longhand→shorthand issues. 

## Assets and cache-busting
- CSS/JS links use `relative_url` and a version query (`?v={{ asset_version }}`) where `asset_version` uses `site.github.build_revision` on Pages and a timestamp locally.

## Theme toggle and code themes
- Color modes: Light, Dark, Auto (system). Uses Bootstrap 5.3+ `data-bs-theme` (early bootstrapper in the head to avoid FOUC).
- Files:
  - Early theme bootstrap + CSS links: `_includes/header.html`
  - Toggle UI: `_includes/navbar.html`
  - Behavior/persistence: `js/theme_toggle.js`
  - Overrides and syntax themes (VS Code Light/Dark Modern): `css/theme-overrides.css`

## Content authoring
- Write posts under `_posts/` using Markdown or convert Jupyter notebooks to HTML posts.
- Notebook conversion: see `notebooks/notebook_convert.py` and the “About this blog” post for the workflow and customization (e.g., cell collapse buttons).

## SEO and feeds
- Plugins: `jekyll-seo-tag`, `jekyll-sitemap`, `jekyll-feed`.
- Default social image for posts is set via `_config.yml` (`defaults: ... image:`). Override per post as needed.

## Analytics
- Google Analytics (gtag) is included via `_includes/analytics.html` and configured in `_config.yml`.

## License
See `LICENCE`.