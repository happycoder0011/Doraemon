---
name: show
description: Render the operator status dashboard for a WebForge client. Use when the operator asks "what's the status of <client>?" or runs /webforge:show <client>. Shows current phase, budget spent, pending approvals, and next action — all in plain language.
disable-model-invocation: true
---

# /webforge:show — Operator status dashboard

Run when the operator invokes `/webforge:show <client-slug>`. Renders an ASCII dashboard inline (and optionally saves HTML to `projects/<slug>/dashboard.html`).

## Inputs

- `<client-slug>` — required, kebab-case. e.g. `/webforge:show acme-plumbing`

If the operator runs `/webforge:show` with no argument, list every project under `projects/` and ask which one.

## What to read

1. `projects/<slug>/project.config.yaml` — for goals, budget, deliverables
2. `projects/<slug>/state.json` — for current phase, last transition, run history
3. `audit/<run-id>.jsonl` (latest) — for budget spent, pending approvals

If any of those files don't exist, say so in plain language — don't error.

## Output — ASCII dashboard

Render this exact shape (replace values with data from the files):

```
┌─ <Client Name> ────────────────────────────────┐
│ Phase: <PHASE>              Started: <n> ago   │
│ Budget: $<spent> of $<total> spent (<pct>%)    │
│ Pending: <n> approvals, <n> questions          │
│ Confidence: <pct>%   Avg critic score: <n>/100 │
│                                                 │
│ <progress bar — phase progress from state.json>│
│                                                 │
│ Next: <next action in plain language>          │
└─────────────────────────────────────────────────┘
```

**Progress bar rule:** use block characters `▓` for done and `░` for remaining. Round to whole characters. Default bar is 16 chars wide. e.g. `▓▓▓▓▓▓▓░░░░░░░░░░ STRATEGY (44% done)`.

## Plain-language rules

The operator is non-technical by default. Translate everything:
- "Generated 5 long-form content artifacts" → "Wrote 5 service pages"
- "Deployment successful — Workers build #1423 published" → "Site is live"
- "Lighthouse perf 92" → "Page loads fast"
- "JSON-LD schema validated" → "Search engines will understand the page"

If `operator.expertise` is `developer` in the config, technical phrasing is fine.

## What you must NOT do

- Read files outside `projects/<slug>/` or `audit/`.
- Modify state. This skill is read-only.
- Generate an approval card. The Director does that.

## Failure modes

- **`projects/<slug>/project.config.yaml` missing** → "I don't see a project for `<slug>` yet. Run `/webforge:new-client` to start one."
- **`state.json` missing** → "Project exists but hasn't kicked off. Run `/webforge:approve kickoff <slug>` when ready."
- **Both present but stale** (no transitions in 7+ days) → flag with: "No activity in 7 days. Want to resume or pause?"