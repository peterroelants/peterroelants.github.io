# Potential todos and improvements

## Site improvements guide

### 0) Client-side search (Lunr.js) and navbar integration
Rationale: Improves content discoverability and user experience without server-side infrastructure. A compact search field in the navbar makes it easy to access on any page.

Steps:
1. Add a small search form to the navbar (Bootstrap form). Consider a collapsible input on mobile.
2. Build a minimal JSON index of posts (title, url, tags, excerpts). This can be generated at build time or inlined via `jekyll-feed`-derived data.
3. Use Lunr.js in the browser to query the index and render results in a lightweight results panel or a dedicated search page.
4. References:
   - https://lunrjs.com/
   - https://getbootstrap.com/docs/4.0/components/navbar/#forms
   - https://learn.cloudcannon.com/jekyll/jekyll-search-using-lunr-js/
   - https://medium.com/@kurtiskemple/setting-up-client-side-search-for-a-jekyll-github-pages-site-with-lunr-and-backbone-d644541d7260


### 2) Social sharing previews: default image (DONE)
Rationale: Posts without an `image` front matter field produce weaker link previews on platforms (Twitter, LinkedIn). A site-wide default improves click-through and brand consistency.

Status: Implemented via `_config.yml` `defaults` for posts. Current default: `/images/ANN_preview.png`. Prefer setting a specific `image:` per post for best relevance.


### 3) Accessibility auditing and improvements
Rationale: Ensure keyboard navigation, color contrast, ARIA semantics, and headings remain compliant after UI changes.

Steps:
1. Quick in-browser checks
   - Chrome DevTools → Lighthouse → Accessibility (run per page).
   - Install axe DevTools extension and “Scan all of my page” for detailed guidance.

2. Automated locally (CLI)
   - Serve locally:
```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```
   - Run axe-core CLI on key pages:
```bash
npx @axe-core/cli http://127.0.0.1:4000/
npx @axe-core/cli http://127.0.0.1:4000/tag_index/
npx @axe-core/cli http://127.0.0.1:4000/posts_chrono/
npx @axe-core/cli http://127.0.0.1:4000/about/
```
   - Or Pa11y:
```bash
npx pa11y http://127.0.0.1:4000/ --timeout 30000
```

3. Automated across the whole site (CI-friendly)
   - Serve built site:
```bash
npx http-server _site -p 8080 -c-1
```
   - Crawl via sitemap with Pa11y CI:
```bash
npx pa11y-ci --sitemap http://127.0.0.1:4000/sitemap.xml
```

Acceptance checks:
- Keyboard: Full Tab/Shift+Tab navigation; visible focus; Escape closes overlays.
- Headings: Logical H1→H2 order; avoid skipped levels.
- Landmarks: One `main`; label additional `nav` if multiple (`aria-label`).
- Links/Buttons: Clear accessible names; no empty links.
- Images: Informative `alt`; empty `alt` for decorative.
- Color contrast: ≥ 4.5:1 for body text; ≥ 3:1 for large text and UI.
- Motion: Respect `prefers-reduced-motion`.

Optional enhancements:
- Add a “Skip to content” link and main landmark:
```html
<a class="visually-hidden-focusable" href="#main">Skip to content</a>
<main id="main">...</main>
```
- Use Bootstrap’s `.visually-hidden` utility for screen-reader-only content.
