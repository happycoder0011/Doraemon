# WebForge Agency — User Manual

> A practical guide to installing, running, and customizing the WebForge plugin family. Pair this with `ARCHITECTURE.md` (the design doc) when you want to understand *why*, not just *how*.

---

## Table of contents

1. [What WebForge is](#1-what-webforge-is)
2. [Install](#2-install)
3. [Day-to-day commands](#3-day-to-day-commands)
4. [The config file](#4-the-config-file)
5. [Phases of a project](#5-phases-of-a-project)
6. [Plugin reference — core](#6-plugin-reference--core)
7. [Plugin reference — saas](#7-plugin-reference--saas)
8. [Plugin reference — local-services](#8-plugin-reference--local-services)
9. [Plugin reference — ecommerce](#9-plugin-reference--ecommerce)
10. [Plugin reference — personal-brand](#10-plugin-reference--personal-brand)
11. [Plugin reference — ops](#11-plugin-reference--ops)
12. [Agents — when Claude uses them](#12-agents--when-claude-uses-them)
13. [Customization](#13-customization)
14. [Troubleshooting](#14-troubleshooting)
15. [Where to read more](#15-where-to-read-more)

---

## 1. What WebForge is

WebForge is a family of **Claude Code plugins** that automate the work of a small website agency — intake, SEO strategy, design, copy, build, deploy, and ongoing ops.

You describe what a client needs in plain language. WebForge runs the right agents for that client's type, follows your budget and approval rules, and stops for human approval on anything irreversible.

**You need:** Claude Code installed and signed in, plus the project-specific MCP servers or CLI tools each skill lists as required (WordPress CLI, Shopify CLI, Vercel CLI, etc.).

**You don't need:** to know any code, agent names, or implementation details. Every command is a plain-English verb.

### The plugins

| Plugin | What it's for |
|---|---|
| **webforge** (core) | The orchestrator. Always installed. |
| **webforge-saas** | SaaS landing + blog work (Next.js + Vercel). |
| **webforge-local-services** | Plumber, dentist, lawyer, gym, etc. (WordPress + Kinsta). |
| **webforge-ecommerce** | Shopify stores, product schema, reviews. |
| **webforge-personal-brand** | Coach / consultant / creator sites (Webflow). |
| **webforge-ops** | Cross-cutting: outreach, analytics, monthly reports, crisis response. Install for retainer clients. |

You install **webforge** plus **exactly one niche plugin** per client type. Add **webforge-ops** if the client is on a retainer.

---

## 2. Install

### From a Git repository (recommended)

```bash
# Add the marketplace (once)
claude plugin marketplace add <org>/<repo>

# Install the core (always)
claude plugin install webforge@webforge-marketplace

# Install exactly one niche plugin
claude plugin install webforge-local-services@webforge-marketplace

# For retainer clients, also install ops
claude plugin install webforge-ops@webforge-marketplace
```

Replace `<org>/<repo>` with the repository that contains this code (e.g. `happycoder0011/Doraemon`).

### From a local directory (development)

```bash
git clone <repo> webforge
cd webforge

claude plugin marketplace add ./
claude plugin install webforge@webforge-marketplace
claude plugin install webforge-local-services@webforge-marketplace
```

### Verify the install

```bash
claude plugin list
```

You should see all the plugins you installed, marked ✔ enabled.

```bash
claude plugin details webforge
claude plugin details webforge-local-services
```

Both should show a **Component inventory** section listing skills and agents.

---

## 3. Day-to-day commands

WebForge is operated entirely through **slash commands**. Type the command into a Claude Code session and the skill runs.

### Core commands (always available)

| Command | What it does |
|---|---|
| `/webforge:new-client` | Walks you through a 4-question wizard that creates a new `project.config.yaml` for a client. |
| `/webforge:show <slug>` | Renders the status dashboard for a client (phase, budget spent, next action). |
| `/webforge:digest` | Scans every project and lists what's waiting on your attention today. |

**`<slug>`** is the kebab-case client name (e.g. `acme-plumbing`, `beta-saas`). It's set by `/webforge:new-client` and matches the project directory under `projects/<slug>/`.

### Common patterns

```bash
/webforge:new-client                           # start onboarding a new client
/webforge:show acme-plumbing                   # how is acme-plumbing doing?
/webforge:show                                 # list every project, then pick
/webforge:digest                               # what needs my eyes today?
```

### Niche-specific commands

See sections 7–11 for each plugin's commands.

---

## 4. The config file

Every client has a `project.config.yaml` — a single source of truth that drives which agents and skills run. It lives at:

```
projects/<slug>/project.config.yaml
```

### Key sections

```yaml
project:                 # who the client is, what they want
  name: "Acme Plumbing Co"
  slug: "acme-plumbing"
  type: "local-services"
  goals:
    primary: "leads"

deliverables:            # WHAT to build
  website:    { cms: "wordpress", pages: [...], template: "wordpress-theme" }
  content:    { blog_posts_initial: 5, service_pages: 4 }
  seo:        { ongoing_months: 6, local_seo: true }
  outreach:   { citations_local: 15 }
  analytics:  { monthly_reporting: true }

infrastructure:          # WHERE it runs
  deployment_target: "wp-hosting"
  hosting_provider: "kinsta"
  domain: "acmeplumbing.com"

operator:                # HOW you operate
  expertise: "non-technical"
  judgment_strength: "high"
  preferences: { communication_style: "concise", report_format: "pdf" }

budget:                  # money limits
  total_project_usd: 2500
  monthly_retainer_usd: 400
  per_run_cap_usd: 20

approvals:               # what requires your sign-off
  mode: "judgment-gated"
  required_for: ["kickoff", "design_direction", "voice_sample", "pre_launch"]

fallbacks:               # what to do when input is missing
  primary_keyword_source: ["client_brief", "dataforseo", "llm_inference", "ask_human"]
```

### Validate a config

After editing a config, run the validator:

```bash
python3 ~/.claude/plugins/webforge/scripts/validate_config.py \
  projects/acme-plumbing/project.config.yaml
```

The validator emits **plain-language errors** (per ARCHITECTURE.md §3.5). For example:

> ❌ You picked WordPress but `vercel` for hosting. WordPress sites need a WordPress-capable host (wp-hosting or aws). Want me to switch hosting?

Not technical jargon like "Invalid `infrastructure.deployment_target` for `cms=wordpress`".

### Templates

Every niche plugin ships a starter config you copy and fill in:

| Template | From plugin |
|---|---|
| `templates/project.config.yaml.example` | webforge (universal) |
| `templates/saas.project.config.yaml` | webforge-saas |
| `templates/local-services.project.config.yaml` | webforge-local-services |
| `templates/ecommerce.project.config.yaml` | webforge-ecommerce |
| `templates/personal-brand.project.config.yaml` | webforge-personal-brand |
| `templates/ops.project.config.yaml` | webforge-ops |

Templates have empty `name` and `slug` fields by design — they're meant to be filled in.

---

## 5. Phases of a project

Every project flows through the same phases (ARCHITECTURE.md §9):

```
INTAKE → RESEARCH → STRATEGY → DESIGN → CONTENT → BUILD → LAUNCH → MEASURE → ITERATE
```

What runs in each phase depends on `project.type` and the rest of the config.

### What each plugin does per phase

| Phase | webforge (core) | webforge-local-services | webforge-ecommerce | webforge-saas | webforge-personal-brand |
|---|---|---|---|---|---|
| **INTAKE** | `/webforge:new-client` wizard | discovery agent | discovery agent | discovery agent | discovery agent |
| **RESEARCH + STRATEGY** | — | seo-strategist agent (local-tuned) | seo-strategist agent (ecom-tuned) | seo-strategist agent (saas-tuned) | seo-strategist agent (personal-brand-tuned) |
| **DESIGN** | — | — | — | — | designer + ia-architect agents |
| **CONTENT** | — | (via frontend-eng + seo-tech) | copywriter agent (product + category + email) | (via frontend-eng) | copywriter agent (home + about + offer + lead magnet) |
| **BUILD** | — | `wordpress-build` skill | `shopify-build` skill | `nextjs-build` skill | `webflow-build` skill |
| **LAUNCH** | — | `kinsta-deploy` skill | (Shopify native) | `vercel-deploy` skill | (Webflow native) |
| **MEASURE** | — | `site-audit` skill | `ab-test`, `product-schema`, `review-markup` skills | — | — |
| **ITERATE** | `/webforge:digest` | `webforge-ops:link-outreach`, `webforge-ops:monthly-report` | same | same | same |

The **state** of a project (which phase, what was last done) is tracked in `projects/<slug>/state.json`. Plugins read it on each invocation.

---

## 6. Plugin reference — core (`webforge`)

### Subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| `webforge:director` | opus | High-stakes decisions, ambiguous briefs, approval framing, cost-ceiling enforcement. |
| `webforge:planner` | sonnet | Decomposes a Director-approved goal into a DAG with per-step agent, model, and budget. |
| `webforge:critic` | opus | Reviews specialist outputs against a 6-dimensional rubric. Returns `accept` or `revise`. |

### Skills

- **`/webforge:new-client`** — Onboarding wizard. Asks 4 questions, generates `projects/<slug>/project.config.yaml`, runs the validator.
- **`/webforge:show <slug>`** — Status dashboard. Renders an ASCII view of phase, budget, pending approvals, confidence, next action.
- **`/webforge:digest`** — Morning summary. Scans every project and lists items waiting on you.

### Scripts

- **`scripts/validate_config.py`** — Config validator with plain-language errors. Invoked by `/webforge:new-client` and by every niche build skill.

---

## 7. Plugin reference — saas (`webforge-saas`)

Use for clients with `project.type: saas`, `template: nextjs-marketing`, `deployment_target: vercel`.

### Subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| `webforge-saas:discovery` | sonnet | Intake phase. SaaS-tuned intake (sub-niche, persona, value prop, conversion event). |
| `webforge-saas:seo-strategist` | opus | Strategy phase. SaaS-tuned keyword clusters (TOFU/MOFU/BOFU), comparison keywords, programmatic SEO. |

### Skills

- **`/webforge-saas:nextjs-build <slug>`** — Scaffold a Next.js 14 (App Router) site. Installs theme, generates pages from config, wires the chosen CMS (Sanity / Contentful / markdown), generates sitemap + JSON-LD schema.
- **`/webforge-saas:vercel-deploy <slug> [production]`** — Deploy to Vercel. Runs preview by default; pass `production` to deploy to the live alias. Includes smoke tests.

### Required tools

- **Vercel MCP server** OR **`vercel` CLI** installed and authenticated.
- **`npx create-next-app`** (run via the Bash tool).
- Optional: **Sanity / Contentful MCP** if you're using one of those CMSes.

---

## 8. Plugin reference — local-services (`webforge-local-services`)

Use for clients with `project.type: local-services` (plumber, dentist, lawyer, gym, HVAC, salon, etc.) on WordPress + a WP host.

### Subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| `webforge-local-services:discovery` | sonnet | Intake phase. Surfaces GBP / NAP / services gaps. Blocks if GBP unclaimed or NAP undefined. |
| `webforge-local-services:seo-strategist` | opus | Strategy phase. Geo-keyword clusters, GBP optimization gaps, citation plan, review strategy, schema inventory. |
| `webforge-local-services:frontend-eng` | sonnet | Build phase. WordPress theme scaffold, page templates, schema injection, Core Web Vitals. |
| `webforge-local-services:seo-tech` | sonnet | Build + measure. Technical SEO audit, Lighthouse, schema validation, opens per-issue PRs. |

### Skills

- **`/webforge-local-services:wordpress-build <slug>`** — Scaffold WordPress. Snapshots the host, installs theme (GeneratePress / Kadence / custom), installs plugins (Rank Math, WPForms, WP Super Cache, etc.), generates pages.
- **`/webforge-local-services:kinsta-deploy <slug> [production]`** — Deploy to Kinsta (or any WP host). Git push, search-replace, flush cache, smoke tests. Defaults to staging.
- **`/webforge-local-services:local-seo <slug>`** — GBP optimization playbook. Generates GBP description, categories, photo checklist, 8 weekly posts, Q&A seeds, NAP block.
- **`/webforge-local-services:citations <slug> [build|audit]`** — Citation submissions (default `build`) or NAP-consistency audit (`audit`). Generates drafts for 15 directories across 3 tiers.
- **`/webforge-local-services:site-audit <slug>`** — Full site audit. Scores technical SEO (40), content (30), local SEO (30). Produces prioritized fix list with effort per fix.

### Required tools

- **WordPress MCP server** OR **`wp` CLI + SSH** access to the host.
- **Rank Math SEO** (or Yoast) installed on the target site.
- For GBP optimization: the operator (you) does the actual edits in Google Business Profile — the skill produces drafts.

---

## 9. Plugin reference — ecommerce (`webforge-ecommerce`)

Use for clients with `project.type: ecommerce`, `cms: shopify`, `deployment_target: shopify`.

### Subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| `webforge-ecommerce:discovery` | sonnet | Intake phase. SKU count, fulfillment model, payment providers, reviews platform, brand tier. |
| `webforge-ecommerce:seo-strategist` | opus | Strategy phase. Category keyword map, faceted-nav policy, programmatic SEO opportunities, content plan. |
| `webforge-ecommerce:copywriter` | sonnet | Content phase. Product pages (PDP), category pages, cart-abandon + post-purchase email sequences. |
| `webforge-ecommerce:frontend-eng` | sonnet | Build phase. Shopify theme + custom sections + app integrations. |

### Skills

- **`/webforge-ecommerce:shopify-build <slug>`** — Scaffold Shopify. Creates dev store, installs theme (Dawn / Prestige / Motion / custom), installs apps (Judge.me, Klaviyo, etc.), imports products.
- **`/webforge-ecommerce:product-schema <slug>`** — Validate `Product` + `Offer` JSON-LD across the catalog. Fixes common errors (price-as-string, missing `aggregateRating`, missing `gtin`).
- **`/webforge-ecommerce:review-markup <slug>`** — Validate `AggregateRating` + individual `Review` JSON-LD. Checks schema matches visible page content (no fabricated reviews).
- **`/webforge-ops:ab-test <slug>`** — (Lives in `webforge-ops`.) Hypothesis-driven A/B test with sample-size calculation, mid-test check, final verdict.

### Required tools

- **Shopify MCP server** OR **Shopify CLI** (`shopify theme dev`) + Partner account.
- For analytics: **GA4** + **Google Search Console** connected to the store domain.

---

## 10. Plugin reference — personal-brand (`webforge-personal-brand`)

Use for clients with `project.type: personal-brand` (coach, consultant, creator, fractional exec) on Webflow.

### Subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| `webforge-personal-brand:discovery` | sonnet | Intake phase. Positioning (niche, transformation, offer), lead magnet, calendar tool. |
| `webforge-personal-brand:seo-strategist` | opus | Strategy phase. Niche pillar, "search-of-self" keywords, 90-day calendar (web + LinkedIn + newsletter + podcast). |
| `webforge-personal-brand:copywriter` | sonnet | Content phase. Home, about, offer, lead-magnet landing — voice-matched to the operator. |
| `webforge-personal-brand:designer` | sonnet | Design + build. Brand identity (if no existing kit), three-direction proposal, Webflow layout. |
| `webforge-personal-brand:ia-architect` | sonnet | Strategy phase. Sitemap, conversion path, navigation, page hierarchy. |

### Skills

- **`/webforge-personal-brand:webflow-build <slug>`** — Scaffold Webflow. Creates project, applies design tokens, builds component library, wires pages + integrations.
- **`/webforge-personal-brand:calendar-embed <slug>`** — Embed a booking widget (Cal.com / Calendly / SavvyCal). Verifies the full booking flow end-to-end.
- **`/webforge-personal-brand:lead-magnet <slug>`** — Design + build a lead magnet (PDF / template / mini-course / quiz) + the opt-in form + the 3-email post-submit sequence.

### Required tools

- **Webflow Designer** (browser-based, operator present) OR **Webflow MCP server**.
- A booking tool account (Cal.com / Calendly / SavvyCal).
- An email tool (ConvertKit / Beehiiv / Mailchimp) for the lead magnet flow.

---

## 11. Plugin reference — ops (`webforge-ops`)

Cross-cutting. Install for **retainer clients** (those with `ongoing_months > 0`).

### Subagents

| Agent | Model | When Claude uses it |
|---|---|---|
| `webforge-ops:outreach` | sonnet | Backlink / partnership / guest-post prospect drafting. Operator reviews and sends. |
| `webforge-ops:analytics` | haiku | Daily/weekly analytics scan. Detects traffic drops, ranking drops, conversion changes. Triggers crisis-response when needed. |
| `webforge-ops:content-strategist` | opus | Quarterly content plan. Refresh existing pages, fill gaps, prune underperformers. |

### Skills

- **`/webforge-ops:link-outreach <slug>`** — Build a 25-prospect list, draft personalized emails, track replies. Max 10 emails/week/client.
- **`/webforge-ops:monthly-report <slug>`** — Generate the client monthly report (PDF / HTML / Markdown per `report_format`). Requires operator approval before sending.
- **`/webforge-ops:crisis-response <slug>`** — Triage traffic drops, ranking drops, manual actions, HCU impact. Diagnoses cause, builds recovery plan with operator approval per action.
- **`/webforge-ops:gsc-monitor <slug>`** — Daily/weekly GSC monitor. Indexing, manual actions, security, mobile usability, CWV, performance deltas. Triggers crisis-response on severity.

### Required tools

- **Google Search Console MCP** (or API access).
- **GA4 MCP** (or API access).
- An email tool for outreach (Gmail / Outlook / Hunter.io / Apollo).

---

## 12. Agents — when Claude uses them

You don't invoke agents directly. Claude picks the right one based on what you're asking for, and the agent's `description` field tells Claude when to use it.

If you want to nudge Claude toward a specific agent, name it explicitly:

> "Run webforge:critic on the home page copy."

Otherwise, Claude uses the matching agent automatically. Examples:

- You say "we have a new client" → Claude calls the matching niche's `discovery` agent.
- You say "what's acme's status?" → Claude runs `/webforge:show acme-plumbing`.
- You say "we lost 30% of traffic last week" → Claude calls `webforge-ops:crisis-response`.

### Agent output schemas

Every agent returns a structured YAML block. The Critic's output (most common to see) looks like:

```yaml
verdict: accept | revise
score: 0-100
breakdown:
  factual_accuracy: 0-100
  brand_voice_fit: 0-100
  schema_validity: 0-100
  seo_hygiene: 0-100
  risk_surface: 0-100
  cost_honesty: 0-100
flags:
  - type: hallucination | brand_drift | seo_antipattern | cost_overrun | schema_mismatch
    severity: low | medium | high | blocker
    location: <where>
    evidence: <quote>
revisions:
  - <concrete change>
```

Score ≥ 85 with no blocker flags = accept. Lower = revise with specific instructions.

---

## 13. Customization

### Add a config template

1. Edit `projects/<slug>/project.config.yaml` directly, or
2. Drop a starter template in any niche plugin's `templates/` folder:
   ```
   plugins/webforge-local-services/templates/my-niche.project.config.yaml
   ```
3. Run the validator to confirm it's valid.

### Change approval depth

In `project.config.yaml`:

```yaml
approvals:
  mode: "judgment-gated"      # default for non-technical operators
  # mode: "technical-gated"  # every change needs sign-off (for technical operators)
  # mode: "minimal"           # only kickoff + monthly report
```

You can also override per-event:

```yaml
approvals:
  auto_approve_below_cost_usd: 0.50   # anything cheaper auto-proceeds
```

### Add MCP servers

Each skill lists the MCP servers it needs in its body. To wire them:

1. Add to your local `~/.claude/.mcp.json` (user scope) or to a project `.mcp.json`.
2. Restart Claude Code or run `/reload-plugins`.
3. Confirm with `/mcp` — the server should appear.

Example `.mcp.json`:

```json
{
  "mcpServers": {
    "shopify": {
      "command": "npx",
      "args": ["-y", "@shopify/mcp-server"]
    },
    "dataforseo": {
      "command": "npx",
      "args": ["-y", "dataforseo-mcp-server"],
      "env": {
        "DATAFORSEO_LOGIN": "<your-login>",
        "DATAFORSEO_PASSWORD": "<your-password>"
      }
    }
  }
}
```

### Tighten the budget cap

In `project.config.yaml`:

```yaml
budget:
  per_run_cap_usd: 10           # tighter default
  total_project_usd: 1500       # if your real budget is lower
```

The validator will catch inconsistencies (e.g., `per_run_cap_usd > total_project_usd`).

### Pin plugin versions

The marketplace lists plugins at the version in their `plugin.json`. To stay pinned:

```bash
# Once installed, the version is locked until you run:
claude plugin update webforge@webforge-marketplace
```

Skip updates when you don't want them.

---

## 14. Troubleshooting

### "Plugin not found"

```bash
claude plugin list            # check what's installed
claude plugin marketplace list # check marketplaces
```

If the marketplace isn't registered:

```bash
claude plugin marketplace add <org>/<repo>
```

If the marketplace is registered but the plugin doesn't appear, your version of Claude Code may be too old. Run `claude --version` (should be ≥ 2.1.265 for folders-of-plugins support, ≥ 2.1.281 for marketplace.json beside plugin folders).

### "Validation failed" on the config

Run the validator directly:

```bash
python3 ~/.claude/plugins/webforge/scripts/validate_config.py \
  projects/<slug>/project.config.yaml
```

Errors come out as plain-language sentences, not stack traces. The two most common:

1. **Wrong deployment target for CMS** — WordPress needs a WP host, Shopify deploys itself, etc. The error tells you which combo is invalid and how to fix it.
2. **Missing required section** — every project needs `project`, `deliverables`, `infrastructure`, `operator`, `budget`.

### "I don't see a project for `<slug>`"

Either the project was never created (`/webforge:new-client` produces the directory), or the operator is invoking from outside the project root. The project root is wherever `projects/<slug>/` lives.

### "Skill requires MCP server X — I don't have it"

Two options:

1. **Add the MCP server** to `.mcp.json` (see [Customization](#13-customization)).
2. **Use the CLI equivalent** if the skill lists one (e.g., `wp` CLI instead of WordPress MCP, `vercel` CLI instead of Vercel MCP).

If neither is feasible, surface it as a blocker and don't proceed.

### "Token cost is too high"

Check what's loaded:

```bash
claude plugin details webforge
claude plugin details webforge-local-services
```

The **Always-on** line is the per-session cost. **Per-component** shows what each skill/agent costs when invoked.

Strategies to lower cost:

- Don't install plugins you don't need. For example, don't install `webforge-ops` for a non-retainer project.
- Disable unused plugins with `claude plugin disable <plugin>`.
- Prefer sonnet / haiku agents for routine work — opus is reserved for high-stakes calls in the agent defaults.

### "The Critic keeps rejecting my output"

Read the **flags** + **revisions** blocks. The Critic scores 6 dimensions; revise only what it flags. Hallucinated citations are always blockers, regardless of total score.

### "I started a build but want to roll back"

Every skill creates a snapshot or commits before mutation. Specific paths:

- `wordpress-build` → host snapshot at the path in `projects/<slug>/build/SNAPSHOTS.md`
- `kinsta-deploy` → host dashboard → Restore
- `nextjs-build` / `webflow-build` → git revert
- `vercel-deploy` → `vercel rollback` (instant) + git revert (next deploy)

In a running session, run `/reload-plugins` to pick up edits to plugin files.

---

## 15. Where to read more

- **`ARCHITECTURE.md`** — the full design doc. Read this when you want the *why* behind a decision.
- **A skill's `SKILL.md`** — the source of truth for what a skill does. Read this when a skill's behavior surprises you.
- **An agent's `.md`** — the agent's system prompt. Read this to see exactly what an agent is told to do and not-do.
- **`templates/project.config.schema.json`** — the full config schema. Read this when adding new config fields.

### Plugin-internal references

| File | What's in it |
|---|---|
| `plugins/webforge/.claude-plugin/plugin.json` | Manifest for the core plugin. |
| `plugins/webforge-core/agents/director.md` | The Director agent's full system prompt. |
| `plugins/webforge-core/scripts/validate_config.py` | The validator (read the docstring). |
| `plugins/webforge-core/templates/project.config.schema.json` | The schema the validator checks against. |
| `plugins/<niche>/.claude-plugin/plugin.json` | That niche's manifest. |
| `plugins/<niche>/agents/*.md` | That niche's agents. |
| `plugins/<niche>/skills/*/SKILL.md` | That niche's skills. |
| `plugins/<niche>/templates/*.yaml` | That niche's config templates. |

### Contributing

WebForge is opinionated. When you change a plugin:

1. Validate the plugin locally: `claude plugin validate --strict ./plugins/<name>`
2. Validate the marketplace: `claude plugin validate --strict ./`
3. Test the affected skill end-to-end on a sandbox project before shipping.
4. Update `ARCHITECTURE.md §21` if the change is structural (new plugin, new component type, etc.).

---

**You're ready.** Start a session with the plugins installed and run `/webforge:new-client` to onboard your first client.