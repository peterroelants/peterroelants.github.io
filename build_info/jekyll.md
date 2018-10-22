# Jekyll commands

GitHub pages with Jekyll info:
* https://help.github.com/articles/using-jekyll-as-a-static-site-generator-with-github-pages/

Setting up your GitHub Pages site locally with Jekyll: https://help.github.com/articles/setting-up-your-github-pages-site-locally-with-jekyll/

## Deployments (GitHub Actions)

Deployments are automated via GitHub Actions using the workflow at `.github/workflows/pages.yml`.

On push to `main`, the workflow:
1. Configures GitHub Pages
2. Installs Ruby gems via Bundler
3. Builds the site with `actions/jekyll-build-pages`
4. Uploads the artifact and deploys with `actions/deploy-pages`

Ensure repo Settings → Pages → Source is set to GitHub Actions.


To install bundler (Ruby package manager):
```sh
gem install bundler
```


To update the github-pages gem run:
```sh
bundle update github-pages
```

To update all packages (gems) run:
```sh
bundle update
```

To serve page locally:
```sh
bundle exec jekyll serve
```


## See also
- Potential todos and improvements: `build_info/potential_improvements.md`

