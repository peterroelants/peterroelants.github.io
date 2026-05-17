---
layout: post_markdown
title: Hosting Jupyter Notebooks on a Blog
description: How this blog, hosted on GitHub Pages, uses Jekyll and Jupyter Notebooks to view notebooks as blog posts.
tags:
- Jekyll
- GitHub Pages
- Blog
- Notebook
---

_About this blog_

I started this blog in 2015 from some notes I took in [Jupyter Notebooks](https://jupyter.org/). Starting from these notebooks, it was only a small effort to publish them via GitHub Pages so that they might be of benefit to others.

This post, created way after I initially created this blog, intends to describe how to use GitHub pages to host Jupyter notebooks as blog posts.


## GitHub Pages

[GitHub Pages](https://pages.github.com/) is a service provided by GitHub to host static webpages under the `*.github.io` domain. Setting up a GitHub pages is remarkably simple, and only requires creating a GitHub repository with the right name and push some static content to it. See more at the [GitHub Pages website](https://pages.github.com/) and [this guide from GitHub](https://guides.github.com/features/pages/).

For example, this blog is backed by [this GitHub repository](https://github.com/peterroelants/peterroelants.github.io), the page you are reading now is build by GitHub from this repository.


### Jekyll

To further customize the site, GitHub Pages supports [Jekyll](https://jekyllrb.com/), a popular static site generator described on the [Jekyll GitHub repo](https://github.com/jekyll/jekyll) as:

> Jekyll is a simple, blog-aware, static site generator perfect for personal, project, or organization sites. Think of it like a file-based CMS, without all the complexity.

Jekyll itself is written in [Ruby](https://en.wikipedia.org/wiki/Ruby_%28programming_language%29), however, you don't need to know any Ruby to be able to use Jekyll. Jekyll itself provides us a few useful functionalities:

* Besides handling HTML files, Jekyll is able to render [Markdown](https://en.wikipedia.org/wiki/Markdown) to HTML. For example the page you are currently reading is rendered from [this Markdown file](https://github.com/peterroelants/peterroelants.github.io/tree/main/_posts/2021/05/2021-05-15-about-this-blog.md).
* [Liquid](https://github.com/Shopify/liquid) as a templating engine, which allows us to reuse a lot of similar functionality like the html head, and the navigation bar at the top. For example, the default layout for content on this blog is defined by [a html file build by liquid](https://github.com/peterroelants/peterroelants.github.io/tree/main/_layouts/default.html)
* Post's metadata processing via YAML [front matter](https://jekyllrb.com/docs/front-matter/). For example notice the title and the tags defined at the top of [this posts' markdown file](https://github.com/peterroelants/peterroelants.github.io/tree/main/_posts/2021/05/2021-05-15-about-this-blog.md).

To learn more about using Jekyll and GitHub Pages see the documentation on "[Setting up a GitHub Pages site with Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll)".


### Theme

GitHub Pages supports a few [themes](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/adding-a-theme-to-your-github-pages-site-using-jekyll) out-of-the-box nowadays. However, this site uses some custom layouting based on [Bootstrap](https://getbootstrap.com/) components and the various CSS and JS files. For example, the navigation bar at the top of this page is created using Bootstrap, and is defined in [this file](https://github.com/peterroelants/peterroelants.github.io/tree/main/_includes/navbar.html).

The notebook formatting on this site is based on Jupyter's CSS files used to export notebooks.


## Notebook conversion

Lot's of posts on this blog are generated from [Jupyter Notebooks](https://jupyter.org/). To convert notebooks to HTML Jupyter provides a tool called [nbconvert](https://github.com/jupyter/nbconvert), which is used to convert the notebooks in this blog.

I've made a [small Python script](https://github.com/peterroelants/peterroelants.github.io/tree/main/notebooks/notebook_convert.py) that uses nbconvert's [HTMLExporter](https://nbconvert.readthedocs.io/en/latest/api/exporters.html?highlight=HTMLExporter#nbconvert.exporters.HTMLExporter) to convert the notebooks to HTML. The resulting HTML is processed using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a HTML parser, to extract some information, and enable custom features like the cell collapse buttons you might have seen on this site (implemented [in this JavaScript file](https://github.com/peterroelants/peterroelants.github.io/tree/main/js/input_expand_collapse.js)).

This conversion script is run on a notebook before I push the changes to the GitHub repository. The resulting HTML is written somewhere to the `_posts` directory which will be picked up by Jekyll for rendering as a post.


## Math rendering

Most of the notebooks contain mathematical formulas written in [$$\LaTeX$$](https://en.wikipedia.org/wiki/LaTeX). To enable the same formulas being rendered [MathJax](https://www.mathjax.org/) is being used on this site. MathJax describes itself as a:

> A JavaScript display engine for mathematics that works in all browsers. 

I have a [local copy](https://github.com/mathjax/MathJax#hosting-your-own-copy-of-the-mathjax-components) of MathJax in my repository. The JavaScript is loaded with the help of [this template](https://github.com/peterroelants/peterroelants.github.io/tree/main/_includes/mathjax.html) that is loaded in the head of each HTML page. To use MathJax yourself I recommend to start with [loading it from a CDN on the web](https://github.com/mathjax/MathJax#using-mathjax-components-from-a-cdn-on-the-web).

