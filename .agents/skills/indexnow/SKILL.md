---
name: indexnow
description: Submit selected URLs from this repository to IndexNow after a major deployed content or URL change. Use when a public page is added, materially updated, redirected, or deleted and a manual crawl notification is wanted; do not use for minor styling, tooling, or asset-only changes.
---

# Notify IndexNow

Use this skill only for the site's manual IndexNow workflow. Read
`build_info/indexnow.md` first; it is the canonical source for the site's key,
protocol details, official references, and submission policy.

## Workflow

1. Submit only when the user asks for an IndexNow notification or the
   publishing workflow explicitly calls for one after a major public change.
   Do not submit minor styling, tooling, notebook-only, or asset-only changes.
2. Confirm that the change is deployed and the affected production URLs have
   been checked. Include only relevant added, materially updated, redirected,
   or deleted page URLs. Never submit local or preview URLs.
3. From the repository root, run the `just` recipe with the affected HTTPS
   URLs:

   ```sh
   just indexnow \
     https://peterroelants.github.io/posts/updated-post/ \
     https://peterroelants.github.io/posts/another-updated-post/
   ```

   Pass multiple URLs together when appropriate. The recipe invokes the
   repository's validation and submission script.
4. Inspect and report the result. HTTP 200 or 202 means that IndexNow received
   the notification; it does not guarantee crawling, indexing, ranking, or
   inclusion in search results.

Keep the existing root-level key unchanged during normal maintenance. Treat
validation errors and non-success responses as failures, report their details,
and avoid repeated retries without a meaningful reason. IndexNow supplements
the sitemap, internal links, and `robots.txt`; it does not replace them.
