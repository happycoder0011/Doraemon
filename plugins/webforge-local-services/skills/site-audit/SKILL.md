---
name: site-audit
description: Run a full technical + content + local SEO audit on a WebForge client's existing site. Use during any phase when an audit is requested (existing client check-in, post-launch verification, post-penalty recovery). Produces a scored report with prioritized fixes.
disable-model-invocation: true
---

# /webforge-local-services:site-audit — Full site audit

Run when the operator invokes `/webforge-local-services:site-audit <client-slug>` (or just `site-audit` if there's one project).

## Inputs

- `<client-slug>` — optional; if omitted, ask
- The site's URL (from `project.config.yaml → infrastructure.domain`)

## What you audit

Three buckets, scored 0–100 each:

### Technical SEO (40 points)

- SSL valid + HTTPS-only
- Page speed (Lighthouse mobile): target ≥ 90
- Core Web Vitals: LCP < 2.5s, INP < 200ms, CLS < 0.1
- Mobile usability: viewport set, tap targets ≥ 48px, font ≥ 16px
- Sitemap: exists, valid XML, in robots.txt
- robots.txt: blocks /wp-admin/, allows content crawl
- Schema markup: validated JSON-LD on home + service pages
- Indexability: every important page returns 200 and is `index, follow`
- Canonical tags: every page has a self-referencing canonical
- 404 page: exists and is helpful

### Content (30 points)

- NAP block in footer (matches the locked NAP)
- Service area mentioned on every page (city + state)
- Service pages: count vs. `deliverables.website.pages`, missing pages flagged
- Internal linking: home → services → each service, all linked
- Duplicate titles / meta descriptions
- Thin content (< 300 words on key pages)
- Hreflang if `i18n: true`

### Local SEO (30 points)

- GBP claimed + verified
- GBP description optimized
- GBP photos: ≥ 20
- GBP review count vs. `review_strategy.target_count`
- GBP reply rate on negative reviews
- Citation consistency: NAP identical across top 15 directories
- LocalBusiness schema with full address on every page
- Embedded Google Map on contact page
- Click-to-call phone number in header

## Output

Write `projects/<slug>/audit/audit-<date>.md`:

```yaml
client_slug: <slug>
audit_date: <iso8601>
total_score: 0-100
breakdown:
  technical_seo: 0-100
  content: 0-100
  local_seo: 0-100
critical_issues:
  - issue: <description>
    severity: blocker | high | medium | low
    fix_skill: <which webforge skill fixes it>
    estimated_effort: <hours or <5min | 30min | 2h | sprint>
quick_wins:  # <30 min to fix, high impact
  - <fix>
recommended_sprint:  # fixes needing 1-3 days
  - <fix>
```

## Decision rules

- score ≥ 85 — healthy; recommend maintenance cadence only
- 70–84 — minor issues; produce a quick-wins list for next session
- 50–69 — significant gaps; produce a sprint plan with `webforge-director` approval
- <50 — broken; trigger `webforge-ops:crisis-response` skill for triage

## Required MCP / CLI

This skill benefits from:
- Lighthouse CLI for performance
- A browser tool for visual verification
- The Search Console MCP for indexability data

If none are available, surface what's missing and proceed with what you have.

## What you must NOT do

- Edit the site directly. Audit is read-only.
- Mark an issue as fixed without re-verification.
- Skip a bucket because tools aren't available — note the gap and continue with what you can verify.