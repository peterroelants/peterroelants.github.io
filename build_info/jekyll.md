# Jekyll commands

GitHub pages with Jekyll info:
* https://help.github.com/articles/using-jekyll-as-a-static-site-generator-with-github-pages/

Setting up your GitHub Pages site locally with Jekyll: https://help.github.com/articles/setting-up-your-github-pages-site-locally-with-jekyll/


To install bundler (Ruby package manager):
```
gem install bundler
```


To update the github-pages gem run:
```
bundle update github-pages
```

To update all packages (gems) run:
```
bundle update
```

To serve page locally:
```
bundle exec jekyll serve
```


## TODO:
- Search in blog
  - Use navbar to display search field: https://getbootstrap.com/docs/4.0/components/navbar/#forms
  - Within-browser search engine: https://lunrjs.com/
  - https://medium.com/@kurtiskemple/setting-up-client-side-search-for-a-jekyll-github-pages-site-with-lunr-and-backbone-d644541d7260
  - https://learn.cloudcannon.com/jekyll/jekyll-search-using-lunr-js/
- Use Katex iso MathJax: https://github.com/KaTeX/KaTeX
