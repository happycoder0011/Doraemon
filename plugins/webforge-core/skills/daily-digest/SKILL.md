---
name: digest
description: Produce the morning digest — a flat list of every WebForge item currently waiting on the operator across all clients. Use when the operator asks "what needs my attention?" or runs /webforge:digest. Async by default: nothing runs silently, nothing demands real-time attention.
disable-model-invocation: true
---

# /webforge:digest — Morning summary

Run when the operator invokes `/webforge:digest`. Scans every project under `projects/` and surfaces the items that need a human decision.

## Inputs

None. The skill scans `projects/*/project.config.yaml`, `projects/*/state.json`, and the latest `audit/<run-id>.jsonl` per project.

## How to scan

For each project directory under `projects/`:

1. Read `project.config.yaml` and `state.json`.
2. From `state.json`, find the current phase and any `pending_approvals[]` and `pending_questions[]`.
3. From the latest audit log, find the last agent action and its timestamp.
4. Compute `days_since_last_activity`.
5. Apply the rules below to decide if this client should appear in the digest.

## Inclusion rules

Include a client if **any** of:

- `state.json.pending_approvals` is non-empty.
- `state.json.pending_questions` is non-empty.
- `days_since_last_activity >= 7` — "stalled, needs check-in"
- The current phase is `launch` and `days_since_last_activity < 1` — "launch in flight"
- `state.json.confidence` < 0.7 — "confidence low, review output"

## Output — flat list

```
<NN> things need your eyes today:

1. **<Client>** — <one-line summary>
   - <what's pending, in plain language>
   - <estimated time to review>
   - <command to act, e.g. `/webforge:show <slug>` or `/webforge:approve <thing> <slug>`>

2. ...
```

If the list is empty:

> Nothing waiting on you. Next scheduled check: <tomorrow>.

## Plain-language rules

Same as `/webforge:show`: translate jargon. Default to non-technical phrasing unless `operator.expertise` is `developer`.

## Time estimates

Map action type to estimated review time:
- approval card (A/B/C pick) — 5–15 min
- design direction review — 15–30 min
- voice sample approval — 10–20 min
- pre-launch checklist — 20–40 min
- monthly report review — 30–60 min
- crisis response (traffic drop / penalty) — 30+ min

## What you must NOT do

- Mutate any state.
- Skip clients because of inactivity alone — flag stalled ones.
- Send notifications or emails. This skill renders to the terminal only.

## Scheduling

This skill is designed to be wired to a scheduler (cron, Task Scheduler, GitHub Action). The plugin ships a sample hook config at `hooks/hooks.json` once a niche plugin (e.g. `webforge-saas`) sets it up. For now, the operator runs it manually.