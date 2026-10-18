---
name: citations
description: Build and audit citation listings for a local-services WebForge client. Use during the Launch and Iterate phases. Reads strategy/keywords.json citation_plan, generates submission drafts, and audits existing citations for NAP consistency.
disable-model-invocation: true
---

# /webforge-local-services:citations — Citation build + audit

Run when the operator invokes `/webforge-local-services:citations <client-slug>`.

Two modes:

- `citations build` (default) — generate submission drafts for every directory in the citation plan
- `citations audit` — check existing listings for NAP consistency

## Pre-flight checks

1. `projects/<slug>/strategy/keywords.json` exists (Strategy phase complete).
2. `deliverables.outreach.citations_local: <n>` is set in `project.config.yaml`.
3. NAP block is locked (from the local-seo skill output).

## Build mode

Generate `projects/<slug>/strategy/citation-submissions.md`:

### Output structure

For each of the 15 directories in `citation_plan`:

```
### <directory name>
- URL: <submission URL>
- Tier: <tier-1 | tier-2 | tier-3>
- Login: <link to claim/manage page>
- Required fields:
  - Business name: <from NAP>
  - Address: <from NAP>
  - Phone: <from NAP>
  - Website: <from NAP>
  - Categories: <from local-seo output>
  - Description: <750 char version, with primary keyword + city>
  - Hours: <from operator>
  - Photos: <upload 5 to start; rest later>
- Special notes: <verification required? paid tier? email loop?>
```

Tiers:
- **Tier-1 (must-have, do first):** Google, Bing, Apple Maps, Facebook, Yelp, BBB
- **Tier-2 (high-value):** Yellow Pages, Superpages, Citysearch, Foursquare (clean), MapQuest
- **Tier-3 (volume):** Hotfrog, EZlocal, Manta, local chamber of commerce, niche directories

Approximate time per listing: 10–20 minutes for the first one, 5–10 for subsequent.

## Audit mode

Generate `projects/<slug>/strategy/citation-audit-<date>.md`:

For each known existing listing:
- Name as listed
- Address as listed
- Phone as listed
- Match against NAP? (Y/N)
- Action needed (claim, fix NAP, leave, escalate)

## Approval

Citation submissions are time-consuming and irreversible once submitted. Each one requires explicit operator `yes` before submission. The skill generates drafts; the operator does the actual entry work (or delegates to a VA).

## What you must NOT do

- Submit citations without operator approval per listing.
- Use inconsistent NAP across directories. NAP inconsistency is the failure mode this skill prevents.
- Recommend paid citation services (Yext, Moz Local) without flagging the cost and surfacing the alternative (manual submission, which is what this skill produces).