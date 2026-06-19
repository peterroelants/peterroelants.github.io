# IndexNow

Responsibility: this is the canonical repository reference for the site's
IndexNow setup and manual workflow for notifying participating search engines
about major page changes.
Keep general site architecture in `site_overview.md`, deployment commands in
`jekyll.md`, and agent-specific guidance in `AGENTS.md`.

The reusable agent procedure is in `.agents/skills/indexnow/SKILL.md`.

## What IndexNow does

IndexNow is a notification protocol. It lets the site tell participating
search engines that a page was added, updated, or deleted so they can
prioritize crawling it. It does not guarantee crawling, indexing, ranking, or
inclusion in search results, and it does not replace the sitemap, internal
links, or `robots.txt`.

The site uses the shared endpoint at `https://api.indexnow.org/indexnow`.
Submitting to one participating endpoint is sufficient; the protocol shares
the notification with other participating search engines where applicable.

## Domain verification

The IndexNow key is the public file
`dddf7faa6a6cfb657df08d8c8e76c4b42917c59a7700ac1eb97e3b341037accb.txt` at the
repository root. GitHub Pages publishes it at:

```text
https://peterroelants.github.io/dddf7faa6a6cfb657df08d8c8e76c4b42917c59a7700ac1eb97e3b341037accb.txt
```

The file name and its contents must remain identical. The key is not a secret;
it is public verification data proving that the site owner controls the host.
Keep this key unchanged during normal site maintenance.

## Manual notifications

IndexNow notifications are intentionally manual for this low-frequency blog.
The GitHub Pages workflow builds and deploys the site but does not contact
IndexNow. This keeps minor commits from generating notifications and lets the
publisher inspect the result before submitting it.

After a major change has been deployed and the affected production URLs have
been checked, run:

```sh
just indexnow \
  https://peterroelants.github.io/posts/updated-post/ \
  https://peterroelants.github.io/posts/another-updated-post/
```

The dependency-free `tools/indexnow_submit.py` script validates the production
host, reads the root-level key file, removes duplicate URLs, submits one bulk
request, and reports the HTTP response. Include added, materially updated,
redirected, or deleted page URLs. Do not submit asset-only, notebook-only,
styling, or other minor implementation changes. Deleted URLs may be submitted
even after they stop returning `200`.

Submit only after deployment: the request tells search engines to crawl the
public URL, not the local build.

## Manual verification and submission

After deployment, first confirm that the key URL above returns the key as plain
text. The `just indexnow` command is preferred because it validates the key and
batches the selected URLs. A direct single-URL request would be:

```sh
curl --get 'https://api.indexnow.org/indexnow' \
  --data-urlencode 'url=https://peterroelants.github.io/posts/example/' \
  --data-urlencode 'key=REPLACE_WITH_THE_KEY'
```

For multiple URLs, use a JSON `POST` request to the same endpoint. IndexNow
accepts up to 10,000 URLs in one request, but submissions should be limited to
pages that were actually added, updated, or deleted. A `200` response means the
notification was received; an initial `202` means it was accepted while key
validation is pending. Neither response guarantees indexing.

## Official references

- [IndexNow protocol documentation](https://www.indexnow.org/documentation)
- [IndexNow FAQ](https://www.indexnow.org/faq)
- [Participating search engines](https://www.indexnow.org/searchengines)
