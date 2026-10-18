---
name: crisis-response
description: Triage and respond to traffic drops, ranking drops, manual actions, or HCU (Helpful Content Update) impact for a WebForge client. Reads analytics, runs diagnosis, and produces a recovery plan with operator approval before any mutation.
disable-model-invocation: true
---

# /webforge-ops:crisis-response — Traffic / ranking crisis triage

Run when the operator invokes `/webforge-ops:crisis-response <client-slug>` or when the analytics agent surfaces a crisis-severity alert.

## What counts as a crisis

- Traffic drop > 20% week-over-week (sustained 2+ weeks)
- Average position drop > 5 across the keyword set
- Manual action notification from Google Search Console
- Helpful Content Update (HCU) impact
- Site hacked or compromised
- Security incident (cert expired, site down)

## What you do (in order)

### 1. Confirm it's real

- Compare 7-day moving avg vs. prior period — not single-day noise
- Check for seasonality (same period last year?)
- Check for site availability (downtime could be the cause)
- Confirm GSC data agrees with GA4

If it's not real, return to monitor.

### 2. Diagnose the cause

Check each possible cause:

| Cause | How to detect |
|---|---|
| Google algorithm update | Search Engine Land, SEMrush sensor |
| Manual action | GSC → Security & Manual Actions |
| HCU impact | "Helpful Content" in GSC + thin content audit |
| Technical issue (indexing, robots, errors) | GSC → Pages report, Coverage |
| Site speed / CWV drop | PageSpeed Insights, CrUX |
| Backlink loss | Ahrefs / SEMrush / Search Console |
| Brand search volume drop | Google Trends TTF |
| Competitor surge | Manual SERP check on top 10 keywords |
| Server outage | Uptime monitor logs |
| Tracking broken | GA4 debug view |

Document each in `projects/<slug>/crisis/<date>-diagnosis.md`.

### 3. Form a hypothesis

Based on the diagnosis, pick the most likely cause. State:
- Hypothesis (one sentence)
- Evidence (3–5 bullets)
- Confidence (low/medium/high)
- Recovery strategy (specific actions)

### 4. Build the recovery plan

| Action | Owner | Deadline | Reversible? |
|---|---|---|---|
| <action 1> | <who> | <when> | <Y/N> |
| <action 2> | <who> | <when> | <Y/N> |

Estimate timeline to recovery:
- Algorithm fluctuation: 2–6 weeks (no action; wait)
- Manual action: 1–3 months (reconsideration request)
- HCU: 3–6 months (content quality overhaul)
- Technical fix: 1–4 weeks (deploy + verify)
- Backlink recovery: depends on cause; 1–6 months

### 5. Set the operator's expectations

> "**The crisis:** <one sentence>
> **Likely cause:** <one sentence + confidence>
> **Recovery plan:** <n> actions over <timeline>
> **Estimated cost:** $<n>
> **Estimated recovery:** <date or range>
>
> Approve to start the plan?"

## Approval gate

Recovery actions that mutate the site (content rewrites, technical changes, link disavows) require operator approval per action. Approval card format per ARCHITECTURE.md §13.2.

## What you must NOT do

- Diagnose without checking algorithm update history.
- Recommend a "quick fix" for HCU impact. There isn't one.
- Disavow backlinks without operator approval — disavow is hard to reverse.
- Promise recovery timelines you can't back up. Be honest about uncertainty.
- Touch `project.config.yaml`.