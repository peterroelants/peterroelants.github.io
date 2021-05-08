---
layout: post_markdown
title: Tagging GitHub Pages
description: How to use Jekyll tags on GitHub Pages blogs. How to sort tags using liquid templating.
tags:
- Jekyll
- GitHub Pages
- Blog
- Liquid Templating
---

The posts on this site are tagged according to their content. These tags can hopefully improve the navigation experience and help find similar content on this site.


## Jekyll Tags

The tagging system used is provide by Jekyll, which has a concept of [Tags](https://jekyllrb.com/docs/posts/#tags).

### Tagging Posts

A post can be tagged by editing its [Front Matter](https://jekyllrb.com/docs/front-matter/). This front matter contains post's metadata and is formatted in [YAML](https://en.wikipedia.org/wiki/YAML). Tags can be added as a list with key `tags`.
For example for [this post](https://github.com/peterroelants/peterroelants.github.io/tree/master/_posts/2021/05/2021-05-15-adding-tags-to-github-pages.md) the front matter defines 3 tags:
```yaml
---
layout: post_markdown
title: Adding Tags to Posts on GitHub Pages
description: How to use Jekyll tags on GitHub Pages blogs.
tags:
- Jekyll
- GitHub Pages
- Blog
---
```

### Display Post's Tags

Tags for a given post can be accessed via the [Liquid templating](https://shopify.github.io/liquid/) system under `page.tags`. For example, this site has a [template](https://github.com/peterroelants/peterroelants.github.io/tree/master/_includes/post_tags.html) that gets included in every post that renders the post's tags at the bottom of the page, as you should be able to see at the bottom of this post.
Using [liquid](https://shopify.github.io/liquid/tags/iteration/), it is possible to show all tags (without formatting or links) as:
```
{% raw %}{% for tag in page.tags %}
    {{ tag }}
{% endfor %}{% endraw %}
```

The actual display of the tags at the bottom of this page (and on the rest of this website) is formatted using [Bootstrap buttons](https://getbootstrap.com/docs/5.0/components/buttons/) and [Font Awesome](https://fontawesome.com/) for the tag icon.


### Overview of all tags on website

To get all tags on the website (and not just the current page), Jekyll provides a `site.tags` that can be accessed via [Liquid templating](https://shopify.github.io/liquid/), as is done on this site's [Tag Index page](/tag_index).

The `tag` items of `site.tags` are nested objects containing the complete posts for each tags. The tag name is the first element of `tag`. All the posts corresponding to the tag are in the second (or last) element of `tag`. For example to print all tags and the number of posts corresponding to these tags use:
```
{% raw %}{% for tag in site.tags %}
  Name: {{ tag | first }},
  count: {{ tag | last | size}}
{% endfor %}{% endraw %}
```

`site.tags` can also be used to get all posts corresponding to a specific tag. For example to get the number of all posts with the "Jekyll" tag use:
```
{% raw %}{{ site.tags["Jekyll"].size }}{% endraw %}
```


#### Sorting tags

To sort tags in various ways we can use the [Liquid `sort`](https://shopify.github.io/liquid/filters/sort/) function, which sorts tags in a case-sensitive order.

The functionality of Liquid templates can be quite limited, for example, there is not much support for list processing. However, we can use a few tricks to still get a list of tags sorted in various ways. One such trick ([reference](https://blog.lanyonm.org/articles/2013/11/21/alphabetize-jekyll-page-tags-pure-liquid.html)) is to extract the information into a large string, separated by a chosen separator string, split the string by this separator, and sort.

As an example, to get a alphabetically sorted list of tag strings it is possible to use:
```
{% raw %}{% capture _site_tags %}{% for tag in site.tags %}{{ tag | first }}{% unless forloop.last %}###{% endunless %}{% endfor %}{% endcapture %}

{% assign tags_alphabetically_sorted = _site_tags | split:'###' | sort %}{% endraw %}

```
Where the separating string here is `###`. If we for example have 3 tags with names: "Bravo", "Charlie", "Alpha" this would first create a string `_site_tags`= "Bravo###Charlie###Alpha". These would then be splitted and sorted and assigned to a list `tags_alphabetically_sorted` = ["Alpha", "Bravo", "Charlie"]. It is possible to now iterate over this list.

The same trick can also be used to sort tags by the number of posts. For example, see [this StackOverflow post](https://stackoverflow.com/a/44696931/919431) and [this template used on this website](https://github.com/peterroelants/peterroelants.github.io/tree/master/_includes/all_tags.html)
