---
name: gsc-monitor
description: Monitor Google Search Console for indexing issues, manual actions, mobile usability, and security events for a WebForge client. Use as a daily/weekly monitor or on-demand check. Triggers alerts to the operator and feeds crisis-response when needed.
disable-model-invocation: true
---

# /webforge-ops:gsc-monitor — Google Search Console monitor

Run when the operator invokes `/webforge-ops:gsc-monitor <client-slug>` (or on a schedule via hook).

## What you check

For each connected GSC property:

### Indexing

- **Pages with errors:** 5xx, 4xx, redirect chains, soft 404
- **Excluded pages:** why excluded (noindex, robots blocked, canonical mismatch)
- **Coverage delta:** new pages indexed vs. last check
- **Sitemap health:** submitted URLs vs. indexed count

### Manual actions + Security

- **Manual actions:** none (else trigger crisis-response)
- **Security issues:** hacked content, malware, phishing
- **Crawl anomalies:** sudden crawl rate drop

### Mobile usability

- New mobile usability issues
- Affected pages count

### Core Web Vitals (CrUX)

- Mobile + desktop CWV status (Good / Needs improvement / Poor)
- Affected URLs by status

### Performance deltas

- Clicks / impressions / position vs. prior period (matches what analytics-agent does but from GSC's perspective)
- Top queries lost / gained

## Output

`projects/<slug>/monitor/gsc-<date>.md`:

```yaml
period: <YYYY-MM-DD> vs <YYYY-MM-DD>
indexing:
  errors: 0
  excluded: 0
  new_indexed: 0
sitemap:
  submitted: 0
  indexed: 0
  coverage_pct: 0.0
manual_actions: none | <description>
security: clean | <issue>
mobile_usability:
  new_issues: 0
core_web_vitals:
  mobile: good | needs-improvement | poor
  desktop: good | needs-improvement | poor
performance_delta:
  clicks: {current: 0, prior: 0, delta_pct: 0.0}
  position: {current: 0.0, prior: 0.0, delta: 0.0}
alerts:
  - severity: info | warning | crisis
    summary: <one sentence>
    action: <crisis-response | investigate | nothing>
```

## Severity rules

- **info:** stable, no action
- **warning:** trend moving wrong (declining impressions, increasing exclusions)
- **crisis:** manual action, security issue, sudden index collapse — trigger `webforge-ops:crisis-response` immediately

## Plain-language rules

Default operator is non-technical. Translate jargon:
- "Indexing" → "Google has added your page to its search results"
- "Excluded" → "Google knows the page exists but isn't including it"
- "Manual action" → "Google has penalized the site for breaking rules"
- "Sitemap coverage" → "the percentage of pages you submitted that Google actually indexed"

## What you must NOT do

- Fix issues directly. Read-only monitor.
- Submit pages for indexing without operator approval (mass submissions can be flagged).
- Skip the mobile + CWV checks — they're separate from indexing but related.
- Touch `project.config.yaml`.