# Jekyll Commands

Responsibility: this document is the command-oriented Jekyll/GitHub Pages
reference. Keep setup, build, serve, dependency-update, and deployment command
notes here. Keep architecture details in `build_info/site_overview.md`, project
orientation in `README.md`, and agent-specific behavior in `AGENTS.md`.

## Reference Links

- GitHub Pages with Jekyll: https://help.github.com/articles/using-jekyll-as-a-static-site-generator-with-github-pages/
- Setting up GitHub Pages locally with Jekyll: https://help.github.com/articles/setting-up-your-github-pages-site-locally-with-jekyll/

## Main Commands

Use `just` when available:

```sh
just
just setup
just check
just build
just serve
just doctor
just verify
```

The `justfile` uses the Ruby pinned in `.ruby-version` when the Homebrew
`ruby@3.3` package is available. If you use another Ruby manager, make sure the
pinned Ruby is active before running `just`, or override commands explicitly:

```sh
RUBY=/path/to/ruby BUNDLE=/path/to/bundle just setup
```

CSS-specific commands:

```sh
just css-build
just css-watch
```

Dependency-update commands:

```sh
just update-github-pages
just update-gems
```

## Ruby And Jekyll Commands

Use the Ruby version pinned in `.ruby-version`.

Install Bundler:
```sh
gem install bundler
```

Update the `github-pages` gem:
```sh
bundle update github-pages
```

Update all Ruby gems:
```sh
bundle update --all
```

Build the site locally:
```sh
bundle exec jekyll build --trace
```

Serve the site locally:
```sh
bundle exec jekyll serve
```

## CSS Commands

CSS minification uses PostCSS with `autoprefixer` and `cssnano`; behavior and
asset details live in `build_info/site_overview.md`.

Install Node dependencies from `package-lock.json`:
```sh
npm ci
```

Build CSS once:
```sh
npm run css:build
```

Watch and rebuild CSS:
```sh
npm run css:watch
```

## Deployment

Deployments are automated via GitHub Actions using the workflow at
`.github/workflows/pages.yml`.

On push to `main`, the workflow:
1. Configures GitHub Pages.
2. Installs Node dependencies from `package-lock.json`.
3. Rebuilds minified CSS assets.
4. Builds the site with GitHub Pages' managed Jekyll builder
   (`actions/jekyll-build-pages`).
5. Uploads the artifact and deploys with `actions/deploy-pages`.

Ensure repo Settings → Pages → Source is set to GitHub Actions.

The deployed Jekyll environment is managed by GitHub Pages. The local
`Gemfile.lock` and `.ruby-version` exist to keep local development close to that
environment, not to replace the Pages builder.

## See Also
- Notebook conversion workflow: `notebooks/README.md`
- Potential todos and improvements: `build_info/potential_improvements.md`
