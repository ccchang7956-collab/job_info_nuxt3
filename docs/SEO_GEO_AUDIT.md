# SEO / GEO Audit

Audit date: 2026-05-17

## Current Findings

1. Domain signals were split across multiple hosts:
   - `opendgpa.shibaalin.com`
   - `www.opendgpa.site`
   - `opendgpa.site`
   - `job.ccchang.tw`
   - `nuxt3.opendgpa.site`

   Google Search Console indexing can be delayed or skipped when sitemap URLs, canonical URLs, structured data URLs, robots references, and documentation point to different hosts.

2. The live `robots.txt` is modified by Cloudflare Managed Content Signals before the app's own rules. On 2026-05-17 the live file allowed general search indexing, but Cloudflare inserted `Disallow` rules for several AI crawlers, including `GPTBot`, `ClaudeBot`, and `Google-Extended`. This hurts GEO discovery even though the repository's own `robots.txt` allows those bots.

3. The live sitemap contains valid canonical URLs, but every job URL currently reports the same `lastmod` date. This makes the sitemap less trustworthy as a freshness signal.

4. Job detail pages are technically indexable and SSR-rendered, but individual job pages are short-lived. Google may choose not to index many of them before they expire. The stable pages (`/`, `/charts`, `/comments`, `/about`) should be treated as the main SEO landing pages.

5. `/logs` is intentionally `noindex,follow`, which is appropriate for crawl budget.

## Code Changes Applied

1. Added `NUXT_PUBLIC_SITE_URL` as the shared frontend SEO host.
2. Updated frontend canonical, Open Graph, and structured data URLs to derive from the shared site URL.
3. Updated backend `SITE_DOMAIN` default to `https://opendgpa.shibaalin.com`.
4. Fixed sitemap `lastmod` conversion for ROC dates (`YYYMMDD`) and escaped XML URLs.
5. Updated `.env`, `.env.example`, Docker build args, and README to use the canonical host.

## Deployment Checklist

1. Rebuild and redeploy frontend and backend after setting:

   ```env
   SITE_DOMAIN=https://opendgpa.shibaalin.com
   NUXT_PUBLIC_SITE_URL=https://opendgpa.shibaalin.com
   CORS_ORIGINS=https://opendgpa.shibaalin.com
   ```

2. In Cloudflare, review AI crawler / managed robots settings. If GEO matters, disable the managed rule that prepends `Disallow` for AI bots, or configure it to allow the bots you want.

3. In Google Search Console:
   - Submit `https://opendgpa.shibaalin.com/sitemap.xml`.
   - Use URL Inspection on `/`, `/charts`, `/comments`, and one active `/job/{id}` page.
   - Confirm the canonical selected by Google is `https://opendgpa.shibaalin.com/...`.
   - Check whether excluded pages are marked as `Discovered - currently not indexed`, `Crawled - currently not indexed`, `Duplicate`, or `Alternate page with proper canonical tag`.

4. Add evergreen landing pages for high-value searches:
   - by location, such as `/jobs/taipei`, `/jobs/kaohsiung`
   - by job system/category, such as `/jobs/sysnam/general-administration`
   - by agency, such as `/agency/{slug}`

   These pages should have stable text, internal links to current jobs, and their own sitemap entries.

## GEO Improvements

1. Keep `llms.txt` and `llms-full.txt` current with the canonical host.
2. Add a concise "資料來源與更新頻率" section on the home and about pages.
3. Add FAQ-style content that answers natural-language queries:
   - "如何查公務員職缺？"
   - "事求人與開放事求人差在哪？"
   - "如何看重複開缺？"
4. Avoid blocking AI crawlers in Cloudflare if you want ChatGPT, Perplexity, Claude, and similar systems to discover and cite the site.
