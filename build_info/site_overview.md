# Site overview

This document describes the overall architecture and workflows of the site at `https://peterroelants.github.io`.

## Stack
- Jekyll via GitHub Pages (`github-pages` gem) and GitHub Actions for deploys
- Plugins: `jekyll-sitemap`, `jekyll-redirect-from`, `jekyll-seo-tag`, `jekyll-feed`
- Templating: Liquid
- CSS/JS: Bootstrap (local), Font Awesome (local), custom CSS/JS
- Math: MathJax (conditionally included)

## Structure
- `_layouts/`: base templates. `default.html` wraps `header`/`navbar`/`footer`; `post.html` and `post_markdown.html` for posts (both set `math: true`).
- `_includes/`: shared partials. Key ones: `header.html` (head, SEO tag, MathJax gate, CSS), `footer.html` (deferred JS), `navbar.html`, `meta.html` (unused now), `favicons.html`.
- `_posts/`: blog posts (some generated from notebooks). Topic folders mirror site sections.
- `css/` and `js/`: local assets; Font Awesome v7 self-hosted as `fontawesome-all.min.css`.
- `images/`: post preview and illustration assets.
 - Tag templates: `_includes/post_tags.html` (renders tags under posts), `_includes/all_tags.html` and `tag_index.html` (site-wide tag index with pagination behavior via JS).

## Font Awesome
- Version: Font Awesome Free v7 (self-hosted)
- Files:
  - CSS: `css/fontawesome-all.min.css` (loaded from `_includes/header.html`)
  - Webfonts: `webfonts/fa-*.woff2` (brands/regular/solid)
- Markup conventions:
  - Use modern style prefixes: `fa-solid`, `fa-regular`, `fa-brands`
  - Prefer modern icon names (e.g., `fa-square-minus`, `fa-square-plus`)
- Updating:
  - Replace `css/fontawesome-all.min.css` and the `webfonts/*.woff2` files from the official Font Awesome Free v7 package/CDN.
  - Keep the same filenames/paths so templates don’t need changes.
  - No local alias/compat CSS is used; update markup to modern names if needed.

## Rendering behavior
- SEO: `{% seo %}` in `header.html` emits canonical, title, and social meta.
- MathJax: included only when `page.math` or `layout.math` is true.
- jQuery: loaded globally in the head to support inline scripts injected by notebook-derived posts (e.g., Bokeh widget code). Site JS (Bootstrap bundle, collapse/expand) remains deferred in the footer.
- Tag pagination: `tag_pages.js` is included only on the tag index via a page flag (`use_tag_pages_js`) and is deferred in the footer.
- Anchor links: implemented in vanilla JS with accessible labels; no jQuery dependency.
- Feed: `jekyll-feed` generates Atom feed automatically; custom `feed.xml` removed.
- 404: `404.html` served at `/404.html`.

Markdown: `kramdown` with `input: GFM`.

## Notebook-to-post workflow
1. Convert notebooks with `notebooks/notebook_convert.py`.
2. Script uses `nbconvert` to HTML and `BeautifulSoup` post-processing:
   - Inserts `.collapse_expand_button` into `.input_area` blocks
   - Optionally collapses inputs ending with a solitary `#`
   - Removes `output_stderr`
   - Adds Bootstrap table classes to pandas tables
   - Replaces anchor-link content with an icon
3. The collapse/expand behavior is wired by `js/input_expand_collapse.js` on DOM ready, relying on jQuery.

## Performance and accessibility
- Single viewport meta in head.
- Images on `index.html` use `loading="lazy"` and `decoding="async"` with improved alt text.
- Font Awesome served minified; consider icon subsetting in the future.

## Redirects
- Use `jekyll-redirect-from` front matter (`redirect_from`) on posts/pages to add aliases. Legacy static redirects remain under topic `redirects/` folders; migrate gradually if desired.

## Local development
```
gem install bundler
bundle update
bundle exec jekyll serve
```

## Deployment (GitHub Pages via Actions)
- Workflow: `.github/workflows/pages.yml`
- On push to `main`, builds with `actions/jekyll-build-pages` and deploys with `actions/deploy-pages`.
- Ensure repo Settings → Pages → Source is set to GitHub Actions.

## CSS build and minification
- Tooling: PostCSS (with `autoprefixer` and `cssnano`)
  - Config file: `postcss.config.js`
  - Key settings:
    - `cssnano` preset disables aggressive longhand→shorthand merges (`mergeLonghand: false`) to avoid issues like `overflow-y` being overridden by `overflow` during minification.
  - Source files: `css/main.css`, `css/notebook.css`
  - Outputs (minified): `css/main.min.css`, `css/notebook.min.css`

- Package scripts (in `package.json`):
  - Build once:
    ```sh
    npm run css:build
    ```
  - Watch mode (rebuild on change):
    ```sh
    npm run css:watch
    ```

- First-time setup (if needed):
  ```sh
  npm install
  ```

- How styles and scripts are loaded:
  - `_includes/header.html` links to `bootstrap.min.css`, `notebook.min.css`, `main.min.css`, `syntax.min.css`, and Font Awesome using `relative_url`.
  - `_includes/footer.html` loads JS bundles using `relative_url`.
  - A version query (`?v=...`) is appended for cache-busting via `asset_version` (commit SHA on Pages).

## Color modes and code themes
- Theme toggle: Light / Dark / Auto (system). Implemented with a small inline bootstrapper in `_includes/header.html` that sets `data-bs-theme` on `<html>` before CSS loads to prevent FOUC, a dropdown control in `_includes/navbar.html`, and logic in `js/theme_toggle.js` to persist preference (`localStorage`) and react to system changes.
- Bootstrap variables: The site relies on Bootstrap 5.3+ color-mode CSS variables. Custom overrides are layered in `css/theme-overrides.css`, which is loaded last.
- Notebook and code styling:
  - Uses Bootstrap variables for borders/backgrounds to adapt to theme.
  - Rouge token colors are remapped to match VS Code Modern themes:
    - Light Modern under `[data-bs-theme="light"]`
    - Dark Modern under `[data-bs-theme="dark"]`
  - Inline code (`code`, not inside `pre`) uses a small theme-specific chip background; block code (`pre > code`) stays transparent and inherits the container.
- Where to tweak:
  - UI theming and notebook/code overrides: `css/theme-overrides.css`
  - Toggle UI: `_includes/navbar.html`
  - Early theme bootstrap: `_includes/header.html`
  - Behavior/persistence: `js/theme_toggle.js`
- Notes:
  - Prefer using Bootstrap CSS variables (`--bs-*`) for surfaces/text to ensure both themes behave consistently.
  - If adjusting syntax colors, update only the `[data-bs-theme] .highlight .token` blocks in `css/theme-overrides.css`.

- Notes and gotchas:
  - Prefer using the same property type as upstream when overriding. Example: if upstream uses `overflow` (shorthand), prefer overriding with `overflow` rather than only `overflow-y`.
  - After changing CSS, hard-refresh the browser (Ctrl/Cmd+Shift+R) to bypass cache, or verify the versioned URL in DevTools Network tab.

## Further reading (posts about this site)
- Hosting Jupyter Notebooks on a Blog — explains the overall setup, Jupyter → HTML conversion, and MathJax usage. See `_posts/2021/05/2021-05-15-about-this-blog.md` and the post on the site.
  - Source: https://github.com/peterroelants/peterroelants.github.io/tree/main/_posts/2021/05/2021-05-15-about-this-blog.md
- Tagging GitHub Pages — details on Jekyll tags, how they are rendered, and the tag index. See `_posts/2021/05/2021-05-15-adding-tags-to-github-pages.md` and the post on the site.
  - Source: https://github.com/peterroelants/peterroelants.github.io/tree/main/_posts/2021/05/2021-05-15-adding-tags-to-github-pages.md


