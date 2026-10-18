---
name: monthly-report
description: Generate a client-ready monthly report (PDF/HTML/Markdown per config). Reads analytics data, summarizes the month's wins/losses/action items, and produces a deliverable that requires operator approval before sending to the client.
disable-model-invocation: true
---

# /webforge-ops:monthly-report — Client monthly report

Run when the operator invokes `/webforge-ops:monthly-report <client-slug>` (typically the first week of the new month for the previous month).

## Pre-flight checks

1. `deliverables.analytics.monthly_reporting: true` in `project.config.yaml`.
2. `brand.voice_doc` is set (reports must match client tone).
3. `operator.preferences.report_format` is set (pdf / html / markdown).

## What you generate

The report has six sections, each in plain language:

### 1. TL;DR (1 paragraph)

> "Last month, your site got 4,521 visits from Google (up 12% from the prior month). Your best new keyword ranking is X (now on page 1). Next month we're focusing on Y."

### 2. What happened

- Organic clicks + change (GSC)
- Sessions + change (GA4)
- Conversion rate + change (GA4) — if conversion tracking exists
- Notable: new keywords on page 1, keywords that improved, keywords that dropped

### 3. What we did

- Content published (titles + URLs)
- Backlinks earned (count + 2–3 highlights)
- Technical fixes shipped
- Local SEO updates (if local-services)

### 4. Wins + Losses

- 3 wins (specific, named)
- 3 losses or surprises (specific, named, with hypothesis for why)

### 5. Next month

- 3 priorities (specific, dated)
- Risks or open issues
- What's blocked

### 6. Appendix (data tables)

- Top 20 queries by clicks
- Top 10 pages by sessions
- Full backlink additions
- Core Web Vitals snapshot

## Format

- **pdf** — render via Pandoc + a brand-themed LaTeX template, or HTML→PDF via headless browser
- **html** — single self-contained HTML file with embedded CSS
- **markdown** — `projects/<slug>/reports/<YYYY-MM>.md`

Save to `projects/<slug>/reports/<YYYY-MM>.<ext>`.

## Approval gate

Per ARCHITECTURE.md §14, monthly reports require operator approval before sending to the client.

Render the report, then ask:
> "Monthly report ready for <Client>. Format: <ext>. Want me to (a) send it now, (b) edit it first, or (c) wait?"

## Plain-language rules

Default tone: confident, specific, no jargon. The client is non-technical by default (per `operator.expertise`).

Translate everything:
- "Organic clicks" → "visits from Google search"
- "Conversion rate" → "the percentage of visitors who did the thing you wanted"
- "Backlinks" → "other websites linking to yours"
- "SERP" → "Google's results page"

## What you must NOT do

- Fabricate numbers. If data is unavailable, say so.
- Skip sections because data is missing. Mark as "data unavailable" and explain.
- Send the report without operator approval.
- Edit `project.config.yaml`.