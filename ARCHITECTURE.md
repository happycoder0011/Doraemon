# WebForge Agency — Agentic Architecture

> A solo-operated, locally orchestrated agency for end-to-end website creation + SEO marketing.
> **Configurable per client.** **Designed for a non-technical operator with good judgment.** Bulletproof by design: every input has fallbacks, every action is audited, every model choice is justified.

---

## 0. Operating Principles

1. **Resilience over cleverness.** A boring, recoverable pipeline beats a brilliant one that fails silently.
2. **Cheap first, expensive only when needed.** Haiku for the 80%; Sonnet for the 19%; Opus for the 1% that matters.
3. **Audit everything, decide nothing alone.** Every agent action is logged; every strategic decision has a critic pass; every client-facing output has a human approval gate.
4. **Idempotent and reversible.** Every operation has a stable ID; every change is in git; every run can be replayed.
5. **Boring state, smart agents.** Workflow state is an explicit, inspectable state machine — not hidden in LLM context.
6. **The operator's job is judgment, not typing.** The system hides implementation; surfaces decisions in plain language with context.
7. **Every client is a config, not a fork.** One codebase; thousands of possible client setups driven by `project.config.yaml`.

---

## 1. System Overview

```
                ┌────────────────────────────────────────────┐
                │            YOU (Solo Operator)             │
                │   judgment · approvals · client calls     │
                │   (no code, no infra, no jargon)           │
                └────────────────┬───────────────────────────┘
                                 │ plain-language commands
                                 ▼
       ┌─────────────────────────────────────────────────────────┐
       │              ORCHESTRATOR (Claude Code)                │
       │  ┌────────────┐  ┌──────────────┐  ┌───────────────┐  │
       │  │  Director  │→ │   Planner    │→ │   Critic /    │  │
       │  │ (Opus 4.7) │  │  (Sonnet)   │  │  QA (Opus)    │  │
       │  └────────────┘  └──────────────┘  └───────────────┘  │
       │         │             │                  ▲           │
       │         └──────► Workflow State Machine ─┘           │
       │                       │                               │
       │              reads project.config.yaml                │
       └─────────────────────────┬───────────────────────────────┘
                                 │ dispatches scoped tasks
       ┌─────────────────────────▼───────────────────────────────┐
       │            SPECIALIST SUB-AGENTS (config-filtered)     │
       │  Discovery · SEO-Strategist · IA-Architect · Designer  │
       │  Copywriter · Frontend-Eng · Backend-Eng · SEO-Tech    │
       │  Outreach · Analytics · QA-Critic                      │
       └─────────────────────────┬───────────────────────────────┘
                                 │ tool calls via MCP
       ┌─────────────────────────▼───────────────────────────────┐
       │                    MCP TOOL LAYER                      │
       │  filesystem · github · web-search · firecrawl          │
       │  dataforseo · gsc · ga4 · wordpress · webflow ·        │
       │  shopify · cloudflare · vercel · aws-sdk · image-gen   │
       └────────────────────────────────────────────────────────┘
                                 │
       ┌─────────────────────────▼───────────────────────────────┐
       │            PERSISTENCE / MEMORY / AUDIT                │
       │  projects/<client>/  ·  brand-voice/  ·  playbooks/    │
       └────────────────────────────────────────────────────────┘
```

---

## 2. Orchestration Layer

The orchestrator is **Claude Code itself**, configured via `.claude/settings.json` with subagents, skills, and MCP servers. It runs three core loops:

### 2.1 Director (Opus 4.7)
The only agent that sees the whole context window. Owns:
- Goal interpretation from your plain-language brief
- Project scoping and phase ordering
- Cross-agent conflict resolution
- Approval requests (in business terms, never implementation)
- Cost ceiling enforcement

**Invoked when:** project kickoff, phase transitions, ambiguity resolution, post-mortems.

### 2.2 Planner (Sonnet 4.5)
Decomposes a Director goal into:
- Ordered steps with dependencies (DAG)
- Per-step: agent assignment, model, budget, expected output schema
- Validation gates between steps
- Rollback plan for each step

**Output:** machine-readable plan JSON committed to `audit/plans/<run-id>.json`. This is what makes runs resumable and inspectable.

### 2.3 Critic / QA (Opus 4.7)
Runs the **reflection loop**:
- Reads agent output, rates 0–100 against rubric
- Flags: factual risk, brand-voice drift, hallucination, SEO anti-patterns
- Returns either `accept` or `revise: <specific instructions>`

**Always invoked before:** any client-facing output, any deploy, any paid action, any output >$5 of compute.

---

## 3. Configuration System  ← core of per-client flexibility

**One codebase. Many clients. Driven entirely by config.**

Every project lives or dies by its `project.config.yaml`. The Director reads it first, before touching anything else.

### 3.1 Config Schema (v1)

```yaml
# project.config.yaml — the single source of truth for a client

project:
  name: "Acme Plumbing Co"
  slug: "acme-plumbing"
  type: "local-services"     # template hint: local-services | saas | ecommerce | info-site | personal-brand
  goals:
    primary: "leads"         # leads | sales | awareness | signups | rankings
    secondary: ["local-awareness", "repeat-customers"]
  timeline: "6 weeks"
  start_date: "2026-11-01"

# ── WHAT we build ──────────────────────────────────────────────
deliverables:
  website:
    required: true
    pages: ["home", "services", "about", "contact", "blog"]
    template: "nextjs-marketing"   # or: "wordpress-theme", "webflow-template", "html-static", "shopify-theme"
    responsive: true
    i18n: false
    cms: "wordpress"               # wordpress | webflow | shopify | sanity | contentful | markdown | none
    cms_admin_user: "owner@acme.com"
  content:
    blog_posts_initial: 5
    service_pages: 4
    landing_pages: 1
  seo:
    technical_audit: true
    keyword_research: true
    ongoing_months: 6
    local_seo: true
    geo: ["New York, NY", "Brooklyn, NY"]
    languages: ["en"]
  outreach:
    backlink_campaign: true
    citations_local: 15
    guest_posts_per_month: 2
  analytics:
    gsc_setup: true
    ga4_setup: true
    monthly_reporting: true
    dashboard: true

# ── WHERE it runs ──────────────────────────────────────────────
infrastructure:
  deployment_target: "wp-hosting"  # vercel | cloudflare | netlify | aws | wp-hosting | shopify | webflow
  hosting_provider: "kinsta"
  domain: "acmeplumbing.com"
  dns: "cloudflare"
  email: "google_workspace"
  cdn: "cloudflare"

# ── HOW we operate ─────────────────────────────────────────────
operator:
  expertise: "non-technical"        # non-technical | technical | developer
  judgment_strength: "high"         # high | medium — adjusts approval depth
  language: "en"
  preferences:
    communication_style: "concise"  # concise | detailed
    report_format: "pdf"            # pdf | html | markdown
    meeting_cadence: "biweekly"

budget:
  total_project_usd: 2500
  monthly_retainer_usd: 400
  per_run_cap_usd: 20

# ── BRAND ──────────────────────────────────────────────────────
brand:
  existing_brand_kit: false
  voice_doc: "data/brand-voices/acme.json"
  tone: ["trustworthy", "approachable", "local-expert"]
  avoid_words: ["cheap", "discount"]

# ── APPROVALS ──────────────────────────────────────────────────
approvals:
  mode: "judgment-gated"            # judgment-gated | technical-gated | minimal
  required_for:
    - "kickoff"
    - "design_direction"
    - "voice_sample"
    - "pre_launch"
    - "outbound_comms"
    - "monthly_report"
  auto_approve_below_cost_usd: 0.50

# ── FALLBACKS ──────────────────────────────────────────────────
fallbacks:
  primary_keyword_source: ["client_brief", "dataforseo", "llm_inference", "ask_human"]
  design_inspiration_source: ["client_pins", "competitor_sites", "dribbble", "ask_human"]
  copy_reference_source: ["brand_voice_doc", "top10_serp_results", "past_projects", "ask_human"]
```

### 3.2 What the config enables

| Config value | What activates |
|---|---|
| `cms: wordpress` | WordPress MCP loaded; Frontend/Backend agents use WP APIs; deploy skill bypassed |
| `cms: webflow` | Webflow MCP loaded; no separate deploy needed |
| `deployment_target: vercel` | Vercel MCP + `vercel-deploy` skill |
| `deployment_target: wp-hosting` | No deploy agent; uses hosting provider's git push |
| `type: local-services` | Local-SEO skill, GBP optimization, citation templates auto-included |
| `type: ecommerce` | Product schema, Shopify/Medusa stack, review schema |
| `ongoing_months: 6` | Retainer phase activated; monthly report skill scheduled |
| `expertise: non-technical` | Plain-language outputs, wizard flows, hide infra logs |
| `judgment_strength: high` | Skips low-stakes confirmations; only business-meaningful approvals |

### 3.3 Config Templates

Pre-built configs you ship and tweak, not start from scratch:

```
templates/
├── local-services.yaml       # plumber, dentist, lawyer, gym
├── saas-yabo.com.yaml        # B2B SaaS landing + blog
├── ecommerce.yaml            # Shopify or Medusa
├── personal-brand.yaml       # coach, consultant, creator
├── info-site.yaml            # affiliate, directory, niche site
└── agency-yabo-website.yaml  # web design / marketing agency site
```

Each template has: default deliverables, default infrastructure stack, default SEO scope, default fallbacks.

### 3.4 Setup Wizard

For new clients, you run:

```
/new-client
```

This launches a 4-question wizard (not 40):
1. **What's the business in one sentence?** (LLM infers niche + goals)
2. **What do they want done?** (multi-select of common deliverables)
3. **Where does the site live?** (pick from common stacks; "I'll think about it" is an option)
4. **What's the budget?** (tier selector: starter / growth / scale)

Wizard outputs a draft `project.config.yaml`. You edit it in plain language afterward — the schema is documented and validated.

### 3.5 Config Validation

Every project load validates:
- All referenced MCP servers are configured
- All referenced skills exist
- Budget refers to monthly tiers are sane
- Domain/DNS combos make sense (e.g., WP-hosting + Vercel is invalid)

Validation failures surface as **plain-language errors**:
- ❌ "You picked WordPress but Vercel for hosting. WordPress sites need a WordPress host. Want me to switch hosting to Kinsta?"
- ✅ Not: `Invalid infrastructure.deployment_target for cms=wordpress`

---

## 4. Specialist Sub-Agents

Each sub-agent is a Claude Code subagent with:
- Isolated context window
- Own tool whitelist (least privilege — driven by config)
- Own output schema
- Own retry/confidence policy

| Agent | Model | Default tools (extended by config) | Output |
|---|---|---|---|
| **Discovery** | Sonnet | intake-questionnaire, web-search | `intake.json` (gaps flagged) |
| **SEO-Strategist** | Opus | dataforseo, gsc, web-search, firecrawl | `strategy.md` + `keywords.json` |
| **IA-Architect** | Sonnet | filesystem, web-search | `sitemap.yaml` + `wireframes/` |
| **Designer** | Sonnet | image-gen, web-search | `design-system.json` + mockups |
| **Copywriter** | Sonnet | filesystem, brand-voice | copy markdown files |
| **Frontend-Eng** | Sonnet | filesystem, github, browser | site code (config-driven stack) |
| **Backend-Eng** | Sonnet | filesystem, github, aws-sdk | APIs, integrations, CMS |
| **SEO-Tech** | Sonnet | firecrawl, lighthouse | audit report + fixes PR |
| **Outreach** | Sonnet | web-search, hunter.io | prospect list + email drafts |
| **Analytics** | Haiku→Sonnet | gsc, ga4 | dashboards, anomaly detection |
| **QA-Critic** | Opus | filesystem, web-search | rubric-scored review |

**Config-driven activation:**
- `cms: wordpress` → Frontend-Eng uses WordPress theme APIs, not Next.js scaffolding
- `cms: webflow` → Frontend-Eng is mostly bypassed; Designer+CMS-Migration handles it
- `deployment_target: wp-hosting` → no deploy agent; hosting-push skill handles it
- `ongoing_months: 0` → Outreach + Analytics agents dormant
- `local_seo: false` → local citations skill skipped

Sub-agents **never** call each other directly. They communicate only via shared project files + the orchestrator. This prevents context pollution and keeps the audit trail clean.

---

## 5. Reasoning Patterns

Used selectively, not as decoration:

| Pattern | Where | Why |
|---|---|---|
| **Plan-and-Execute** | Every multi-step task | Forces explicit DAG; enables checkpointing |
| **Chain-of-Thought** | SEO strategy, IA decisions | Forces trade-off articulation |
| **Tree-of-Thoughts** | Design system choices (3 directions → pick) | Prevents premature convergence |
| **Self-Reflection** | After every specialist output | Cheap quality lift, catch hallucinations |
| **Multi-Agent Debate** | High-stakes: pricing, legal copy, penalty recovery | Director + Critic + Strategist argue, Director adjudicates |
| **ReAct** | Web research, debugging | Tool-call loop with explicit reasoning trace |

**Default:** Plan-and-Execute + Self-Reflection. Reserve the rest for the 5% of decisions where they pay.

---

## 6. Model Routing

A task classifier (Haiku) routes every new task to a model based on:

| Signal | Routes to |
|---|---|
| Simple extraction, formatting, classification | **Haiku 4.5** |
| Standard execution: copy, code, analysis | **Sonnet 4.5** |
| Novel strategy, ambiguous problem, final QA | **Opus 4.7** |
| Output will go to client untouched | **Opus 4.7** + Critic pass |

**Cost guardrails:**
- Per-run budget cap (default $20/client project, configurable via `project.config.yaml`)
- Per-step budget in plan JSON
- Circuit breaker: if any step exceeds 2× expected cost, downgrade model or escalate to you
- Sonnet fallback if Opus is throttled (with quality flag in audit log)

---

## 7. MCP Tool Layer

Each MCP server is a thin, typed interface. Agents see clean tools; providers stay swappable.

```
mcp/
├── filesystem       # project-scoped file I/O (sandboxed per project)
├── github           # PRs, branches, code review automation
├── web-search       # Brave / Tavily for research
├── firecrawl        # site crawling, content extraction
├── dataforseo       # keywords, SERPs, backlinks, technical audit
├── gsc              # Google Search Console read
├── ga4              # Analytics read
├── wordpress        # CMS write (when cms=wordpress)
├── webflow          # CMS write (when cms=webflow)
├── shopify          # CMS write (when cms=shopify)
├── vercel           # deploy (when deployment_target=vercel)
├── cloudflare       # DNS, Workers, deploy (when dns=cloudflare or deployment=cloudflare)
├── netlify          # deploy (when deployment_target=netlify)
├── aws-sdk          # S3, CloudFront, Bedrock for self-hosting
└── image-gen        # hero images, OG images (Flux / Imagen via Bedrock)
```

**Why MCP:** it isolates the LLM from raw API noise; you can swap DataForSEO for Ahrefs without changing prompts, or switch from Vercel to Cloudflare by changing config.

**Config-driven loading:** only the MCP servers required by `project.config.yaml` are connected. A WordPress-on-Kinsta client doesn't pull Vercel credentials.

---

## 8. Skills Library

Skills are reusable, multi-step workflows invoked with `/skill-name`. Each skill is a folder with `SKILL.md` + supporting scripts.

```
.claude/skills/
├── new-client/             # wizard → config.yaml draft
├── client-onboarding/      # intake → research → brief
├── site-audit/             # full technical + content audit
├── competitor-spy/         # SERP + content gap analysis
├── keyword-clustering/     # build topical maps
├── content-brief/          # SERP-aware article brief
├── article-writer/         # SEO-optimized long-form
├── landing-page/           # high-conversion LP workflow
├── design-system/          # tokens, components, brand
├── nextjs-build/           # scaffold + ship (when template=nextjs-marketing)
├── wordpress-build/        # theme + plugins setup (when cms=wordpress)
├── webflow-build/          # CMS structure + design (when cms=webflow)
├── shopify-build/          # theme + product schema (when cms=shopify)
├── static-build/           # HTML/CSS/JS (when cms=none)
├── vercel-deploy/          # deploy (when deployment_target=vercel)
├── cloudflare-deploy/      # deploy + DNS (when deployment=cloudflare)
├── wp-hosting-deploy/      # git push to WP host (when deployment_target=wp-hosting)
├── schema-generator/       # JSON-LD for any page type
├── link-outreach/          # prospect + personalize + send
├── local-seo/              # GBP, citations, NAP consistency (when local_seo=true)
├── crisis-response/        # traffic drops, penalties, HCU
├── monthly-report/         # client-ready PDF/HTML (when monthly_reporting=true)
└── ab-test/                # hypothesis → variant → measure
```

Each skill declares:
- **Trigger:** when you say `/audit` etc., or when Director invokes automatically
- **Config prerequisites:** which config keys must be set
- **Inputs:** with fallbacks — see §10
- **Outputs:** schemas with validation
- **Quality gates:** what Critic checks
- **Estimated cost/time:** shown before run

---

## 9. Workflow State Machine

Phases are explicit. Each has **entry criteria**, **exit criteria**, and **rollback**.

```
INTENT → INTAKE → RESEARCH → STRATEGY → DESIGN
   → CONTENT → BUILD → LAUNCH → MEASURE → ITERATE
       │           │       │        │        │
       ▼           ▼       ▼        ▼        ▼
    [abort]    [revise] [rollback] [rollback] [next cycle]
```

**Config-driven skipping:**
- `cms: webflow` + no custom code → BUILD phase skipped (Designer + CMS-Build handle it)
- `ongoing_months: 0` → MEASURE/ITERATE skipped after launch
- `backlink_campaign: false` → OUTREACH sub-phase skipped

**State persistence:** `projects/<client>/state.json` updated on every transition. Commit to git on every phase exit. A run can be paused, resumed, or replayed from any phase.

**Parallelization:** within a phase, independent tasks run concurrently (multiple subagents in parallel). Dependencies are explicit.

---

## 10. Bulletproof Mechanisms

This is what makes the agency production-grade.

### 10.1 Input Fallbacks (3-deep rule)

Every external input has **three fallbacks** before the system blocks. The exact sources are listed in `project.config.yaml → fallbacks`.

```
Input needed: "primary keyword cluster"
  ├─ Source A: client brief (most authoritative)
  ├─ Source B: DataForSEO suggestion + your GSC (existing rankings)
  ├─ Source C: LLM inference from niche signals
  └─ Source D: ask human (last resort, max 1 round)
```

If all fail → halt phase, surface to operator with full diagnostic in plain language.

### 10.2 Validation Gates

Every inter-agent handoff validates against a JSON schema. Schema failures → return to producer agent with explicit error. No silent type drift.

### 10.3 Idempotency

Every operation has a content hash. Re-running the same step with the same inputs produces no side effects. Safe to retry.

### 10.4 Confidence Scores

Every agent output includes a `confidence` field (0–1) with `reasons[]`. Below threshold (default 0.7):
- For client-facing: → human review (judgment-gated)
- For internal: → Critic agent + retry once

### 10.5 Cost & Latency Budgets

Per-plan JSON declares per-step `max_cost_usd`, `max_latency_s`, `max_retries`. Project config declares `per_run_cap_usd` and `total_project_usd`. Exceeded → circuit breaker halts and surfaces to operator.

### 10.6 Checkpoints

After every state transition:
- `state.json` committed
- Outputs committed
- Audit log appended

Resume picks up exactly where it left off.

### 10.7 Rollback

Every change is in git. Every external mutation (CMS, DNS, deploy) records a reverse operation. `rollback <run-id>` reverts cleanly.

### 10.8 Dry-Run Mode

`/run --dry` executes the full plan, calls no mutating tools, reports what *would* happen. Use before any high-cost or irreversible action.

### 10.9 Circuit Breakers

- Tool failing >3× → swap tool, continue
- Same model error >2× → downgrade to next tier
- Same agent step failing >3× → escalate to human

### 10.10 Safe Defaults

When config is ambiguous or missing, the system picks a sensible default rather than blocking. Defaults are visible and reversible:
- Missing CMS → defaults to WordPress (most common, lowest friction)
- Missing deploy target → matches hosting provider
- Missing brand voice → LLM infers from client's existing site / competitors, flags for review
- Missing geo → inferred from domain TLD + business description

---

## 11. Memory Architecture

Four-tier memory, scoped and explicit:

| Tier | Storage | Lifetime | Used for |
|---|---|---|---|
| **Run memory** | in-context | one run | current task only |
| **Project memory** | `projects/<client>/memory.md` | project lifetime | brand, decisions, history |
| **Brand voice** | `data/brand-voices/<client>.json` | forever | consistent copy |
| **Playbook memory** | vector DB + `data/playbooks/` | forever | retrieval across projects |

**Retrieval:** before any strategy or copy task, the Director pulls top-3 relevant past projects + 1 brand-voice doc. Prevents reinventing wheels, enforces consistency.

**No silent memory:** agent never reads memory without it appearing in the audit log.

---

## 12. Audit & Observability

Every action recorded. Schema:

```json
{
  "ts": "2026-10-15T12:34:56Z",
  "run_id": "acme-launch-2026q4",
  "step_id": "s7",
  "agent": "copywriter",
  "model": "claude-sonnet-4-5",
  "action": "write",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "cost_usd": 0.012,
  "latency_ms": 3400,
  "tokens_in": 1240,
  "tokens_out": 890,
  "confidence": 0.86,
  "tools_called": ["filesystem.read", "brand-voice.retrieve"],
  "critic_score": null,
  "human_approved": null
}
```

Append-only JSONL: `audit/<run-id>.jsonl`. Queryable with `jq`.

**Built-in dashboards** (via `analytics` skill):
- Cost per project / per phase / per agent
- Time per phase
- Confidence drift over time
- Failure modes by category
- ROI per client (hours spent vs deliverables shipped)

**Replay:** `/replay <run-id> [--with --input=...]` re-executes a run with original or new inputs. Lets you A/B strategy choices cheaply.

---

## 13. Operator Experience  ← non-technical friendly

The operator's job is **judgment**, not implementation. The system is designed around that.

### 13.1 Plain-Language Commands

Never need to know flags or syntax:

```
/new-client                    → wizard
/show <client>                 → status dashboard
/audit acme-plumbing           → run audit
/launch acme-plumbing          → run launch
/pause acme-plumbing           → pause
/resume acme-plumbing          → resume
/why <step>                    → explain what agent did and why
/rollback acme-plumbing last   → undo last action
/digest                        → morning summary of pending items
/spend                         → where money went this week
```

### 13.2 Approval Surfaces

When the system needs a decision, it shows a card, not a log:

> **Acme Plumbing — Design Direction**
>
> Three homepage design directions proposed. Each scored against your brand brief.
>
> 🅰 **Trust-first** — clean, lots of reviews, blue/white. Best for: emergency plumbing, older homeowners. Risk: generic.
> 🅱 **Local-expert** — neighborhood photography, "your Brooklyn plumber" framing. Best for: local SEO, repeat customers. Risk: may feel small.
> 🅲 **Modern-tech** — sleek, app-like booking. Best for: young homeowners. Risk: feels impersonal.
>
> **My pick:** 🅱 for SEO + trust combo.
>
> 👉 Reply: `A`, `B`, `C`, or `tell me more about B`.

### 13.3 Status Dashboard

`/show acme-plumbing` renders an HTML page (saved to `projects/<client>/dashboard.html` and viewable in browser):

```
┌─ Acme Plumbing ──────────────────────────┐
│ Phase: STRATEGY        Started: 2d ago   │
│ Budget: $40 of $2,500 spent (1.6%)       │
│ Pending: 2 approvals, 1 question         │
│ Confidence: 87%  Avg critic score: 92/100 │
│                                            │
│ ▓▓▓▓▓▓▓░░░░░░░░ STRATEGY (60% done)     │
│                                            │
│ Next: design candidates ready in ~20 min │
└───────────────────────────────────────────┘
```

### 13.4 No-Jargon Output

All output to you (not to clients) uses business language:
- ✅ "We wrote 5 service pages"
- ❌ "Generated 5 long-form content artifacts using Sonnet 4.5"
- ✅ "The site is live at acmeplumbing.com"
- ❌ "Deployment successful — Cloudflare Workers build #1423 published"

Client-facing outputs use their language (no LLM fingerprints).

### 13.5 Daily Digest

Async by default. `/digest` (or scheduled every morning) shows:

> **3 things need your eyes today:**
>
> 1. **Acme Plumbing** — design directions ready (15 min to review)
> 2. **Beta Client** — outreach list ready, 23 prospects (10 min)
> 3. **Gamma Co** — traffic drop detected, possible HCU impact (read summary)

Nothing runs silently. Nothing demands real-time attention.

### 13.6 Pre-Flight Checks

Before any major action, a clear what-happens-next summary:

> **About to: launch Acme Plumbing site**
> - Site: acmeplumbing.com → Cloudflare → WordPress on Kinsta
> - Will do: deploy code, set DNS, submit sitemap to GSC, verify SSL
> - Won't do: send any email, change billing, touch other clients
> - Cost: ~$0.20 of API calls
> - Time: ~8 min
> - Reversible: yes, with `/rollback acme last`
>
> **Approve?** (yes / show me the plan / wait)

### 13.7 Error Messages

Errors tell you what to do, not what broke:

> ❌ "Couldn't reach Kinsta's API to push the site. **What this means:** the launch is on hold. **What to do:** check Kinsta is up, or reply `retry` in 5 min. **What I'm doing:** nothing — I won't spam retries."

> ❌ Not: "Error 503 from api.kinsta.com — ECONNREFUSED"

### 13.8 Decision History

Every approval/rejection logged with your reasoning (optional comment). Over time this is a record of why choices were made. Helps with client handoffs, retrospectives, and taxes.

### 13.9 Client Portal (Optional)

For retainer clients, an optional read-only view they can log into:
- Latest monthly report
- Rankings snapshot
- Pending content (for review)
- Comments on any deliverable

Implemented as static HTML + Cloudflare Access, no auth DB.

---

## 14. Human-in-the-Loop

You're the operator. The system never goes autonomous on irreversible or client-facing actions.

| Gate | When | Approval channel |
|---|---|---|
| **Kickoff** | New project | `/approve brief` |
| **Strategy** | After SEO-Strategist output | `/approve strategy` |
| **Design direction** | After 3 design candidates | pick one |
| **Voice sample** | First 3 pages of copy | `/approve voice` |
| **Pre-launch** | Final QA pass | `/approve launch` |
| **Outbound comms** | Every backlink/email send | explicit `/send` |
| **Monthly report** | Before sending to client | `/approve report` |

All approvals are PR-style: a markdown file is generated, you comment `LGTM` (or specify edits), the agent proceeds.

**Approval depth** driven by config:
- `approvals.mode: judgment-gated` (default for non-technical operators): only business-impact decisions require approval; technical implementation details auto-proceed
- `approvals.mode: technical-gated`: every change requires your sign-off (for technical operators who want full control)
- `approvals.mode: minimal`: only kickoff + monthly report require approval (high-trust, mature engagement)

**Async by default.** You wake up to a digest of what's pending review; nothing runs silently.

---

## 15. Project Structure

```
Web-app-workflow/
├── ARCHITECTURE.md              ← you are here
├── AGENTS.md                    ← how to operate the agency
├── .claude/
│   ├── settings.json            ← permissions, model defaults, MCP list
│   ├── agents/                  ← subagent .md files
│   ├── skills/                  ← reusable workflows
│   └── mcp.json                ← MCP server configs
├── templates/                   ← per-niche config presets
│   ├── local-services.yaml
│   ├── saas.yaml
│   ├── ecommerce.yaml
│   ├── personal-brand.yaml
│   ├── info-site.yaml
│   └── agency.yaml
├── projects/
│   └── <client-slug>/
│       ├── project.config.yaml  ← THE source of truth
│       ├── state.json
│       ├── memory.md
│       ├── brand-voice.json
│       ├── dashboard.html       ← operator dashboard
│       ├── strategy/
│       │   ├── seo-strategy.md
│       │   ├── keywords.json
│       │   └── competitors/
│       ├── design/
│       │   ├── design-system.json
│       │   └── mockups/
│       ├── content/
│       │   └── *.md
│       ├── build/                ← shipped code
│       ├── audit/
│       │   ├── plans/<run-id>.json
│       │   ├── logs/<run-id>.jsonl
│       │   └── approvals/<date>.md
│       └── client-portal/        ← optional read-only view
├── data/
│   ├── brand-voices/            ← reusable brand profiles
│   ├── playbooks/               ← SEO/content playbooks
│   └── past-projects/           ← embeddings + summaries
├── tools/                       ← helper scripts (Python/Node)
└── audit/                       ← global audit log mirror
```

---

## 16. Cost & Performance Budgets

Defaults — tune per project via config:

| Metric | Default cap | Override |
|---|---|---|
| Run cost | $20 | `budget.per_run_cap_usd` |
| Per-step cost | $2 | in plan JSON |
| Opus calls / run | 20 | `--opus-budget=50` |
| Web search / step | 10 | in plan JSON |
| Phase latency | 30 min wall | in plan JSON |
| Total project cost | $200 | `budget.total_project_usd` |

**Cost optimization patterns:**
- Cache: every tool call cached by `input_hash` for 24h
- Batch: bulk DataForSEO calls, single GSC export
- Speculative parallelism: run 3 design candidates concurrently, pick winner
- Early exit: if Critic scores <60 on first attempt, halt before wasting budget

---

## 17. Failure Modes & Recovery

| Failure | Detection | Recovery |
|---|---|---|
| Tool timeout | 30s circuit | swap tool, retry once |
| Model throttling | API response | downgrade one tier, flag in audit |
| Hallucinated SEO claim | Critic flags | cross-check via web search |
| Brand voice drift | Copywriter self-rates <0.7 | re-pull brand voice, retry |
| Cost overrun | budget guard | halt, surface to operator |
| Schema mismatch | validator | return to producer with diff |
| Git conflict | push fails | rebase on main, re-run |
| CMS mutation fails | API error | rollback via recorded reverse-op |
| External site down | tool fails 3× | skip, log, continue |
| Wrong CMS for this business | client request | swap config, rebuild from current phase |

**The cardinal rule:** never lose work. Every phase output is committed before moving on. Worst case is wasted compute, never lost data.

---

## 18. Security & Privacy

- All MCP calls scoped per-project (filesystem sandbox)
- Client secrets in `.env` per project, never in prompts
- Audit log excludes secret fields
- Brand voice and project memory never leak across clients
- Read-only tokens by default; write tokens only at mutation gates
- Per-client API keys (DataForSEO, etc.) so a leak in one project doesn't expose all

---

## 19. Roadmap to Build

Suggested order — each step is independently useful:

1. **Foundation** — `.claude/settings.json`, Director + Critic agents, MCP config, project skeleton, `project.config.yaml` schema + validator, config templates
2. **Operator Experience** — `/new-client` wizard, `/show`, `/digest`, plain-language outputs, approval cards, dashboard generator
3. **Discovery + Intake** — Discovery subagent + intake skill + 3-deep fallback (config-driven)
4. **SEO Strategy** — Strategist agent + DataForSEO MCP + keyword skill (config-driven: local vs national)
5. **Design System** — Designer agent + image-gen MCP + 3-candidate flow
6. **Copy** — Copywriter + brand-voice retrieval + voice approval gate
7. **Build** — Build skills per stack (wordpress-build, webflow-build, nextjs-build, static-build) — auto-selected by config
8. **Deploy** — Deploy skills per target (vercel, cloudflare, wp-hosting, netlify) — auto-selected by config
9. **SEO Tech** — Technical audit + schema + sitemap skill + GSC submit
10. **Launch** — Coordinated launch workflow with pre-flight summary
11. **Measure** — GSC/GA4 MCP + Analytics agent + monthly report skill
12. **Iterate** — Outreach + content cycle + ab-test skill (retainer clients)

After step 7 you can ship client work. Steps 11–12 turn it from a delivery shop into a growth engine.

---

## 20. Open Decisions

Things I'd want your input on before building:

1. **Naming.** "WebForge" is a placeholder. Rename for brand.
2. **Pricing model.** Project-based, retainer, or both?
3. **Niche focus.** Generalist, or specialize (e.g., SaaS, local services, e-com)?
4. **First client.** Real or sandbox project to validate the pipeline?
5. **Hosting partner(s).** Which ones to bake in (Kinsta for WP, Vercel for Next, etc.)?
7. **Client portal.** Worth building for retainer clients, or skip for v1?
8. **Outbound channels.** Email only, or also LinkedIn/social for outreach?

---

## 21. Distribution

The orchestrator + per-niche specialists are packaged as **Claude Code plugins** and live alongside this doc:

```
.claude-plugin/marketplace.json     # marketplace manifest, source ./plugins/
plugins/
├── webforge-core/                  # plugin name: webforge
│   ├── agents/{director,planner,critic}.md
│   ├── skills/{new-client,show-status,daily-digest}/SKILL.md
│   ├── scripts/validate_config.py
│   └── templates/{project.config.schema.json, project.config.yaml.example}
├── webforge-saas/                  # plugin name: webforge-saas
│   ├── agents/{discovery,seo-strategist}.md
│   └── skills/{nextjs-build,vercel-deploy}/SKILL.md
├── webforge-local-services/        # plugin name: webforge-local-services
│   ├── agents/{discovery,seo-strategist,frontend-eng,seo-tech}.md
│   └── skills/{wordpress-build,kinsta-deploy,local-seo,citations,site-audit}/SKILL.md
├── webforge-ecommerce/             # plugin name: webforge-ecommerce
│   ├── agents/{discovery,seo-strategist,copywriter,frontend-eng}.md
│   └── skills/{shopify-build,product-schema,review-markup,ab-test}/SKILL.md
├── webforge-personal-brand/        # plugin name: webforge-personal-brand
│   ├── agents/{discovery,seo-strategist,copywriter,designer,ia-architect}.md
│   └── skills/{webflow-build,calendar-embed,lead-magnet}/SKILL.md
└── webforge-ops/                   # plugin name: webforge-ops (cross-cutting)
    ├── agents/{outreach,analytics,content-strategist}.md
    └── skills/{link-outreach,monthly-report,crisis-response,gsc-monitor}/SKILL.md
```

**Why a plugin family, not a single plugin:** skills and agents load their names + descriptions into every session's context (see Claude docs on plugin context cost). A single mega-plugin carrying every niche would burn 3k+ tokens per turn even when only one type of client is active. The split keeps a typical client (core + 1 niche + ops) at ~1.5k always-on tokens, and lets a local-services client install only `webforge` + `webforge-local-services`.

**Why `webforge` is the orchestrator name:** the prefix on every skill (`/webforge:new-client`) and every agent (`webforge:director`) comes from this plugin's manifest. Niche plugins keep their own names (`webforge-saas:discovery`).

**Install (from this repo):**

```bash
claude plugin marketplace add ./
# Always install core + one niche:
claude plugin install webforge@webforge-marketplace
claude plugin install webforge-local-services@webforge-marketplace   # or any other niche
# Add ops for retainer clients (Iterate phase):
claude plugin install webforge-ops@webforge-marketplace
```

Or for development without install:

```bash
claude --plugin-dir ./plugins/webforge-core \
       --plugin-dir ./plugins/webforge-local-services \
       --plugin-dir ./plugins/webforge-ops
```

**Plugin inventory (v1.0):**

| Plugin | Always-on cost | Components |
|---|---|---|
| `webforge` (core) | ~447 tok | 3 agents, 3 skills, validator script, schema |
| `webforge-saas` | ~311 tok | 2 agents, 2 skills |
| `webforge-local-services` | ~670 tok | 4 agents, 5 skills |
| `webforge-ecommerce` | ~595 tok | 4 agents, 4 skills |
| `webforge-personal-brand` | ~576 tok | 5 agents, 3 skills |
| `webforge-ops` | ~448 tok | 3 agents, 4 skills |
| **Full install** | **~3,047 tok** | **21 agents, 21 skills** |

**Typical client setup:** `webforge` + 1 niche = ~750–1,200 tokens.
**Retainer client setup:** `webforge` + 1 niche + `webforge-ops` = ~1,200–1,700 tokens.

---

**Next step:** approve this doc, then I'll scaffold the repo per §15 (foundation + Operator Experience + first 2 build skills: Discovery + SEO Audit) end-to-end on a real or sandbox client. We'll pick a config template and a first client to validate the whole flow.