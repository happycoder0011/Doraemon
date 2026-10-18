---
name: new-client
description: Onboard a new WebForge client. Walks the operator through a 4-question wizard (business sentence, deliverables, infrastructure stack, budget tier) and produces a draft project.config.yaml at projects/<slug>/. Never proceeds past questions without operator answers.
disable-model-invocation: true
---

# /webforge:new-client — Onboard a new client

Run this when an operator says "I have a new client" or `/webforge:new-client`. Produces a draft `project.config.yaml` for review. Does NOT auto-execute the project — that's a separate kickoff.

## Inputs you must collect from the operator

Ask exactly **four** questions, in this order. Wait for an answer before moving on. If the operator says "I don't know" or "you decide", use the safe defaults from the per-question guidance below and flag it in the output.

### Q1 — Business in one sentence

> "What's the business in one sentence?"

From the answer, infer `project.type` (one of `local-services | saas | ecommerce | info-site | personal-brand | agency`) and `project.goals.primary` (one of `leads | sales | awareness | signups | rankings`). Show your reasoning, then continue.

### Q2 — Deliverables (multi-select)

> "What do they want done?"

Common options — present as checkboxes:
- [ ] Website (recommended for everyone)
- [ ] Initial content (blog posts, service pages)
- [ ] SEO research + technical audit
- [ ] Ongoing SEO (how many months?)
- [ ] Backlink / outreach campaign
- [ ] Analytics + monthly reporting

If the operator picks Website, ask the page list as a follow-up.

### Q3 — Stack

> "Where does the site live?"

Common options — present with default highlighted:
- **WordPress on Kinsta** (default for `local-services`)
- **Next.js on Vercel** (default for `saas`)
- **Webflow** (default for `personal-brand`, `agency`)
- **Shopify** (default for `ecommerce`)
- **Static HTML** (default for `info-site`)
- "I'll think about it" → flag and use safe default

Map the choice to `deliverables.website.cms` + `deliverables.website.template` + `infrastructure.deployment_target`.

### Q4 — Budget tier

> "What's the budget?"

Three tiers:
- **Starter** — $1,500 project + $0 retainer → `budget.total_project_usd: 1500`, `budget.per_run_cap_usd: 10`
- **Growth** — $5,000 project + $400/mo retainer → `budget.total_project_usd: 5000`, `budget.monthly_retainer_usd: 400`, `budget.per_run_cap_usd: 20`
- **Scale** — $15,000 project + $1,500/mo retainer → `budget.total_project_usd: 15000`, `budget.monthly_retainer_usd: 1500`, `budget.per_run_cap_usd: 50`

## Output

1. Compute `project.slug` from the business name (lowercase, hyphens, no leading/trailing hyphens).
2. Create `projects/<slug>/project.config.yaml` from the `templates/project.config.yaml.example` template, filling in collected answers.
3. Run the validator:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_config.py projects/<slug>/project.config.yaml
   ```
4. If validation passes, show the operator:
   > Created `projects/<slug>/project.config.yaml`. Review and reply `kickoff` to start, or edit and re-run me.
5. If validation fails, show the plain-language errors and offer to fix them in-place after operator confirms.

## Approval

This skill does not require approval — it produces a draft, not a running project. The kickoff phase (which would dispatch the Planner and Discovery agents) requires `/webforge:approve brief` per ARCHITECTURE.md §14.

## Templates you depend on

- `templates/project.config.yaml.example` — the schema template you fill in
- `scripts/validate_config.py` — the validator you run

Both live inside this plugin at the listed locations. Use `${CLAUDE_PLUGIN_ROOT}` to resolve them at runtime.