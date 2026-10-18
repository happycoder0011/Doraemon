---
name: local-seo
description: Optimize Google Business Profile and local search signals for a local-services WebForge client. Use during any phase when GBP optimization is needed. Reads strategy/keywords.json, generates GBP description, post ideas, photo checklist, and Q&A seed.
disable-model-invocation: true
---

# /webforge-local-services:local-seo — Google Business Profile optimization

Run when the operator invokes `/webforge-local-services:local-seo <client-slug>` to generate GBP content + a local-seo action checklist.

## Pre-flight checks

1. `projects/<slug>/strategy/keywords.json` exists (Strategy phase complete).
2. `deliverables.seo.local_seo: true` in `project.config.yaml`.
3. GBP is claimed (verified by the Discovery agent in `intake.json.gbp_state`).

If GBP is unclaimed, **stop** and say: "GBP isn't claimed yet. Reply `claimed` once it's set up, or `skip` to disable local SEO."

## What you generate

Output to `projects/<slug>/strategy/local-seo-playbook.md`:

### 1. GBP business description (580 char max)

Reads `intake.json.value_prop_draft` + `strategy/keywords.json.clusters[0]` and produces a description with:
- Primary service + city in first sentence
- Top 3 services listed
- Years in business / certifications if known
- CTA (call or book)

### 2. Primary + secondary categories

Recommend 1 primary + 5–7 secondary categories from Google's category list. Match to the client's sub-niche.

### 3. Photo checklist (20+ photos)

A bulleted list specifying what photos to upload:
- Exterior (3 angles, different times of day)
- Interior (5 shots: reception, treatment area, equipment)
- Team (headshots, in action)
- Work (before/after if applicable)
- Vehicles (for mobile services)
- Branded (logo wall, uniforms)

### 4. Weekly post ideas (8 weeks)

8 GBP post drafts (one per week) covering:
- Service highlight
- Customer testimonial
- Tip / educational content
- Behind-the-scenes
- Offer / seasonal
- Local event tie-in
- Team intro
- Q&A from common questions

Each draft: title, body (150–300 chars), CTA, suggested photo.

### 5. Q&A seed (10 questions)

10 questions prospects commonly ask, with operator-approved answers. Q&A is a GBP section Google sometimes surfaces in search.

### 6. NAP block

Canonical Name, Address, Phone, Website block to copy into every directory listing. Identical strings across all directories is the entire game.

## Output format

Single markdown file `projects/<slug>/strategy/local-seo-playbook.md`. Operator reviews, then either:
- Copies each section into GBP manually, OR
- Provides GBP MCP access and lets the agent do it (advanced; not in v1.0)

## What you must NOT do

- Write to GBP without explicit operator approval per section.
- Generate fake reviews. Never.
- Use a different NAP than what's in the project file. NAP consistency is the point.