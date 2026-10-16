# ScriptForge — Agentic Architecture for Ad Creative Delivery

> A Claude Code desktop app system that turns a brief into a testable, Meta-ready video ad script — with operator in the loop, full audit, and zero hosted infra.
> **Surfaces:** Claude Code desktop (Pro/Max plan) as the operator surface. Anthropic API under the hood. Notion as structured DB. Google Docs as canonical artifacts. Local filesystem as source of truth.
> **v1 scope:** Brief → Hypothesis → Script. Meta video ads only (1–5 min duration). Launch / retro deferred to v2.
> **Outputs:** Hypothesis Doc + Script Doc (+ supporting: brief, hook bank, storyboard).

---

## 0. Operating Principles

1. **Quality first, speed follows.** v1 prioritizes output quality above all else. Spend the tokens, do the research, run the Critic. We are building a quality reputation, not chasing throughput.
2. **Knowledge compounds.** Every script you ship, every SOP you write, every research artifact you collect becomes reusable structured input. The 100th client should be 10× faster than the 1st.
3. **Research is a dump we mine, not a per-task expense.** Routine research artifacts are written to a shared dump (Notion Research Queue + Google Doc digests) and retrieved when relevant. Same artifact serves many campaigns.
4. **Cheap first, expensive only when needed.** Haiku for routine scans and classification. Sonnet for drafting. Opus for strategy and final QA.
5. **Hypothesis before script.** Never write a script without an explicit hypothesis. The hypothesis doc is the contract; the script is the experiment.
6. **Local files are source of truth; Notion + Google Docs are durable surfaces.** Prompts, schemas, configs, and SOPs live in the repo. Notion and Google Docs are the human-visible persistence layer (brand registry, audit, briefs, hypotheses, scripts, voice). MCP writes keep them in sync.
7. **Operator owns judgment; agents own execution.** The marketer decides the angle, the proof points, the risks. Agents do the legwork.
8. **One brand per worktree (optional).** Brand-specific context can live in a per-brand folder; cross-brand ops happen at the repo root. Default: single repo, brands as folders.
9. **Broad approval surface.** Operator can approve from chat, Google Doc comments, or Notion status fields. Agent watches all three.
10. **Budget is observed, not enforced.** Cost caps are advisory while we calibrate what good work actually costs. Director logs actual spend to the Budget DB; we review monthly and adjust.

---

## 1. System Overview

```
┌────────────────────────────────────────────────────────────┐
│           YOU (Operator) on Claude Code desktop            │
│        brief → review → approve (chat interface)           │
│        Pro / Pro Max plan                                  │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
   ┌─────────────────────────────────────────────┐
   │   Claude Code desktop app                   │
   │   • Loads CLAUDE.md (Director personality)  │
   │   • Reads .claude/agents/*.md (sub-agents)  │
   │   • Reads .claude/skills/*/SKILL.md         │
   │   • Configures MCP from .mcp.json           │
   │   • Reads local files (prompts/, brands/)   │
   └────────────┬────────────────────────────────┘
                │ Anthropic API (under hood)
                │ uses MCP tools
                ▼
   ┌─────────────────────────────────────────────┐
   │  • Notion        • Google Docs              │
   │  • Web search    • Firecrawl                │
   │  • Brave/Tavily  • Meta Ad Library          │
   │  • Image-gen                                  │
   └────────────┬────────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────────────────────┐
   │   NOTION (DB — structured state)            │
   │   • Brand Registry                          │
   │   • State Machine (per-brand phase)         │
   │   • SOP Library                             │
   │   • Audit Log                               │
   │   • Briefs (drafts + iteration)             │
   │   • Hooks working list                      │
   │   • Research Queue                          │
   └────────────┬────────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────────────────────┐
   │   GOOGLE DOCS (canonical artifacts)         │
   │   • hypothesis.md                           │
   │   • script.md                               │
   │   • research/*.md                           │
   │   • brand-voice/<brand>.doc                 │
   │   • retros/*.md (v2)                        │
   └─────────────────────────────────────────────┘

Plus: local filesystem (source of truth for prompts, configs, state, SOPs)
```

**v1 output flow (chat-driven):**

```
brief (Notion page) ─► hypothesis (Google Doc) ─► script (Google Doc)
    │                        │                         │
    └──── operator ◄──────────┴────── critic ◄─────────┘
         approval / edits        score / revise
```

---

## 2. Orchestration Layer

The Director / Planner / Critic pattern is preserved. Now implemented via Claude Code's native sub-agent system + skills, not custom instructions in a Project.

### 2.1 How Claude Code desktop loads the system

When the operator opens the `ad-agent/` project directory in Claude Code desktop:

1. **CLAUDE.md is auto-loaded** as the system context for the Director — encodes Director behavior, slash-phrase handling, approval keywords, error tone
2. **`.claude/agents/*.md`** files are available as sub-agents (Brief-Architect, Hypothesis-Strategist, etc.) — the main agent invokes them by name
3. **`.claude/skills/*/SKILL.md`** files are exposed as slash-phrases (`/new-brief`, `/hypothesize`, etc.)
4. **`.mcp.json`** configures MCP servers (Notion, Google Drive, web search, etc.) — they become available as tools
5. **Local files** (prompts, brand configs, SOPs) are readable as context

### 2.2 Director (Opus 4.7)

Lives in `CLAUDE.md`. The default top-level agent. Owns the whole conversation.

- Interprets the operator's plain-language message
- Sequences phases: Brief → Hypothesis → Hooks → Script
- Routes tasks to sub-agents by name
- Resolves conflicts between sub-agents
- Surfaces approval cards as markdown in chat
- Writes state transitions to Notion via MCP
- Writes audit log rows to Notion via MCP

### 2.3 Planner (Sonnet 4.5)

Sub-agent defined in `.claude/agents/planner.md`. Invoked by Director at the start of a campaign.

Decomposes a goal into:
- Ordered DAG of steps with dependencies
- Per-step: agent to invoke, expected output schema, fallback path
- Validation gates between steps
- Rollback plan per step

**Output:** a row in Notion **Runs** DB with the plan as JSON in the body. Makes the run inspectable, resumable, replayable.

### 2.4 Critic / QA (Opus 4.7)

Sub-agent in `.claude/agents/critic.md`. Invoked before:
- Any client-facing output (hypothesis, script)
- Any SOP promoted to "validated"

Checks (live, via MCP, not from cache):
- Brand voice match (reads live brand voice from Google Docs)
- Claim truthfulness (cross-check via web search / Firecrawl)
- Meta spec compliance (duration 1–5 min, hook lands by 0:10)
- SOP adherence
- Hypothesis–script alignment
- Hallucination risk
- Differentiation from past scripts (queries Notion + Google Drive)

Returns `accept`, `revise: <instructions>`, or `reject: <reason>` — surfaced in chat as a markdown card.

---

## 3. Configuration System

Brand config is **hybrid**: local file is source of truth, Notion DB is the human-visible mirror.

### 3.1 Local: `brands/<slug>/brand.config.yaml`

```yaml
# brand.config.yaml — source of truth for a brand

brand:
  name: "Acme Plumbing Co"
  slug: "acme-plumbing"
  industry: "local-services"        # local-services | d2c | b2b-saas | ecommerce | personal-brand | regulated
  one_liner: "Brooklyn's trusted emergency plumbing crew"
  tone: ["trustworthy", "approachable", "locally-rooted", "no-fluff"]
  avoid_words: ["cheap", "discount", "unbeatable"]
  required_words: ["licensed", "insured"]
  persona:
    name: "First-time homeowner Maya"
    pain: "Just bought a 1920s brownstone; terrified of plumbing surprises"
    desired_outcome: "one trusted number to call when something breaks"
    proof_that_matters: ["years in business", "real reviews", "neighborhood photos"]
    objection: "I'm not made of money; will they gouge?"

# ── WHAT we make ──────────────────────────────────────────────
deliverables:
  primary_format: "video-ads"        # video-ads only for v1
  cadence:
    briefs_per_month: 8
    hypotheses_per_brief: 3
  testing:
    primary_metric: "hook_rate"        # informational only in v1 (no launch automation)
    success_threshold: "hook_rate >= 25%"
  script_frameworks:
    - "PAS"
    - "BAB"
    - "AIDA"
    - "UGC-native"
    - "Founder-story"
  sop_overrides: []

# ── WHERE it runs ──────────────────────────────────────────────
integrations:
  notion_workspace: "acme-marketing"
  google_drive_folder: "clients/acme-plumbing"
  storage: "git"

# ── HOW we operate ─────────────────────────────────────────────
operator:
  expertise: "senior-marketer"
  judgment_strength: "high"
  language: "en"
  preferences:
    approval_style: "judgment-gated"

budget:
  per_campaign_usd: 5                # observational only, not enforced
  monthly_usd: 250                   # observational only, not enforced

# ── APPROVALS ──────────────────────────────────────────────────
approvals:
  mode: "judgment-gated"
  required_for:
    - "new_brief"
    - "hypothesis_doc"
    - "final_script"
    - "promote_to_global"
  auto_approve_below_cost_usd: 0.25

# ── KNOWLEDGE SOURCES ──────────────────────────────────────────
knowledge:
  past_scripts_path: "brands/acme-plumbing/scripts/"
  sops_path: "brands/acme-plumbing/sops/"
  global_sops: true

# ── FALLBACKS (3-deep rule) ────────────────────────────────────
fallbacks:
  audience_signal_source:
    - "client_brief"
    - "meta_audience_insights"
    - "competitor_comment_mining"
    - "llm_inference"
  competitor_ad_source:
    - "meta_ad_library"
    - "apify_competitor_crawler"
    - "brand_website_review_mining"
    - "ask_human"
  trend_signal_source:
    - "web_search"
    - "competitor_ad_themes"
    - "industry_publication_scan"
    - "llm_inference"
  proof_artifact_source:
    - "client_assets"
    - "review_sites"
    - "internal_past_winners"
    - "ask_human"

# ── META ──────────────────────────────────────────────────────
status: "active"                     # active | dormant | archived
created: "2026-10-15"
last_active: "2026-10-15"
```

### 3.2 Mirror: Notion Brand Registry DB

Same properties as the local file, but as a Notion DB row. Created/maintained by:
- `notion/provisioning.py` on first run (one-shot)
- Sub-agents via MCP on each config change

Operator can edit either side; sync logic prefers the most recent edit (content-hash-based).

### 3.3 What activates per property

| Config value | What loads / activates |
|---|---|
| `industry: local-services` | Local-services SOP pack, "neighborhood" proof patterns, geo-locale research skill |
| `primary_format: video-ads` | Script-Writer + Storyboarder active; static/email skills dormant |
| `tone: [trustworthy, approachable]` | Voice-Match agent calibrated; Critic checks against these |
| `avoid_words` | Pre-generation filter + post-generation Critic check |
| `script_frameworks: [PAS, BAB]` | Hypothesis agent proposes from this set |
| `cadence.briefs_per_month: 8` | Director suggests routine research cadence |
| `global_sops: true` | Cross-brand SOP retrieval enabled |
| `status: dormant` | Director skips this brand for routine suggestions |

### 3.4 Config Templates (ship-and-tweak)

```
brands/_templates/
├── local-services.yaml       # plumber, HVAC, dentist, lawyer, gym
├── d2c.yaml                # consumer product, Shopify
├── b2b-saas.yaml           # B2B SaaS, lead-gen
├── ecommerce.yaml          # retail, marketplace
├── personal-brand.yaml     # coach, consultant, creator
└── regulated-vertical.yaml # health, finance, legal — extra compliance gates
```

**Meta video ad constraints (durations, aspect ratios, hook window, captions) are baked into the Script-Writer agent definition (`.claude/agents/script-writer.md`) — not config — since v1 is Meta-only.**

### 3.5 New-Brand Wizard

The `/new-brand` slash-phrase (skill in `.claude/skills/new-brand/`) runs a 4-question wizard:

1. **What does the brand sell, in one sentence?** (Director infers industry)
2. **Who are we talking to?** (multi-select persona scaffold)
3. **What tone — pick 3 words?** (multi-select chips)
4. **Any regulated-vertical concerns?** (yes/no — if yes, triggers compliance pack)

Director:
- Creates local `brands/<slug>/brand.config.yaml` with inferred defaults
- Creates a row in Notion Brand Registry DB
- Creates a Google Drive folder structure for the brand
- Creates a Google Doc for voice (template filled with inferred tone notes)
- Suggests the operator review/edit the config

### 3.6 Validation

Every config load validates:
- All referenced MCP servers configured in `.mcp.json`
- `avoid_words` ≠ `required_words`
- Per-run budget ≤ monthly budget
- Required approvals list complete

Validation failures surface as plain-language errors in chat.

---

## 4. Specialist Sub-Agents

Each sub-agent is a `.claude/agents/<name>.md` file. Claude Code loads them automatically and the main agent invokes them by name.

```
.claude/agents/
├── director.md              # default top-level (loaded as CLAUDE.md context)
├── planner.md               # Sonnet — campaign decomposition
├── critic.md                # Opus — rubric-scored review
├── brief-architect.md       # Sonnet — brief structuring
├── hypothesis-strategist.md # Opus — hypothesis doc construction
├── hook-writer.md           # Sonnet — Tree-of-Thoughts 10-candidate generation
├── script-writer.md         # Sonnet — framework-driven script generation
├── storyboarder.md          # Sonnet — frame-by-frame visual plan
├── voice-match.md           # Sonnet — brand-voice scoring
├── routine-research.md      # Haiku — quick scans
├── trend-spotter.md         # Sonnet — trend synthesis
├── competitor-watch.md      # Sonnet — Meta Ad Library + review mining
├── audience-insights.md     # Sonnet — audience signal distillation
├── sop-freshness.md         # Haiku — SOP staleness check
└── universal-helper.md      # Sonnet — general-purpose fallback
```

### 4.1 Agent definition structure

Each `.claude/agents/<name>.md`:

```markdown
---
name: hypothesis-strategist
description: Constructs testable hypothesis docs for ad campaigns. Use when Director needs to draft a hypothesis from an approved brief.
model: opus
tools:
  - Read
  - Write
  - mcp__notion__*
  - mcp__google_drive__*
  - mcp__brave__*
---

# Hypothesis-Strategist

## Role
[role description]

## Process
1. Read approved brief from `brands/<slug>/briefs/<id>.md` and Notion
2. Read live brand voice from `brands/<slug>/voice.md` (or Google Doc)
3. Read top 3 past scripts from `brands/<slug>/scripts/`
4. Pull top 3 relevant research from Notion Research Queue
5. Construct hypothesis per schema in §13.1
6. Write Google Doc + local mirror

## Output
- Google Doc at `clients/<slug>/hypotheses/<id>.doc`
- Local mirror at `brands/<slug>/hypotheses/<id>.md`
- Notion row in Briefs DB

## Quality bar
- ≥2 testable hypotheses
- Each cited from a research source
- Each with explicit risks
```

### 4.2 Universal Helper

General-purpose Sonnet agent for tasks that don't fit a named specialist. Defined in `.claude/agents/universal-helper.md`.

Used when Director needs to:
- Format or transform an artifact (Google Doc → markdown, Notion page → table, JSON → CSV)
- Summarize a long doc or research dump
- Run a one-off validation
- Generate a quick asset (caption rewrite, alt-text, copy variant)
- Draft an ad-hoc schema or template
- Parse, extract, or restructure content

Universal-Helper does NOT replace specialists — it complements them. Director routes to a specialist first when one fits; Universal-Helper is the fallback.

### 4.3 Sub-agent discipline

**Sub-agents never call each other directly.** They communicate only via:
- Notion (read/write DBs)
- Google Docs (read/write artifacts)
- Local files (read/write via filesystem)
- The Director (in the conversation thread)

This keeps audit clean and prevents context pollution.

---

## 5. Reasoning Patterns

| Pattern | Where | Why |
|---|---|---|
| **Plan-and-Execute** | Every multi-step task | Forces explicit DAG; enables checkpointing |
| **Chain-of-Thought** | Hypothesis construction, audience insight distillation | Forces articulation of *why* |
| **Tree-of-Thoughts** | Hook generation (10 candidates → score → pick top 3) | Avoids premature convergence |
| **Self-Reflection** | After every specialist output | Cheap quality lift; catches hallucinations |
| **Multi-Agent Debate** | Brand-voice conflict, regulated claims | Director + Critic + Voice-Match argue |
| **ReAct** | Live research: trend check, competitor crawl | Tool-call loop with reasoning trace |

**Default in chat:** Plan-and-Execute + Self-Reflection. Reserve debate for high-stakes calls.

---

## 6. Model Routing

Claude Code allows specifying model per agent in the agent's frontmatter (see §4.1). Plus the operator can pick the model for the main conversation.

**Recommended defaults:**

| Task | Model |
|---|---|
| Director (main) | Opus |
| Brief intake | Sonnet |
| Hypothesis construction | Opus |
| Hook generation | Sonnet |
| Script writing | Sonnet |
| Storyboard | Sonnet |
| Voice-Match scoring | Sonnet |
| Final QA (Critic) | Opus |
| Trend / competitor sweep | Haiku (or Sonnet for synthesis) |
| SOP freshness check | Haiku |

**Cost guardrails (observational in v1):**
- Director surfaces running cost in chat as informational
- Sonnet fallback if Opus throttled; Director flags quality risk in audit

---

## 7. MCP / Tool Layer

MCP servers are configured in `.mcp.json` at the project root. Claude Code loads them on startup.

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}",
        "GOOGLE_REFRESH_TOKEN": "${GOOGLE_REFRESH_TOKEN}"
      }
    },
    "brave": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-firecrawl"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    },
    "meta-ad-library": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-meta-ads"],
      "env": {
        "META_ACCESS_TOKEN": "${META_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Tool usage per agent

| Agent | Primary MCP tools |
|---|---|
| Brief-Architect | Notion (write), Google Drive (read) |
| Hypothesis-Strategist | Notion, Google Drive, Brave, Firecrawl |
| Hook-Writer | Notion, Google Drive, Brave |
| Script-Writer | Notion, Google Drive, Image-gen |
| Storyboarder | Image-gen, Google Drive |
| Voice-Match | Google Drive (read live voice) |
| QA-Critic | Notion, Google Drive, Brave, Firecrawl |
| Routine-Research | Brave, Firecrawl, Meta Ad Library |
| Trend-Spotter | Brave, Firecrawl |
| Competitor-Watch | Meta Ad Library, Firecrawl, Brave |
| Audience-Insights | Brave, Meta Ad Library |
| SOP-Freshness | Notion, Google Drive |
| Universal-Helper | Notion, Google Drive, Brave, Image-gen |

**v2 (deferred):**
- Meta Ads API — launch automation + retro analytics
- GA4 — site analytics for retro
- Slack — daily digest delivery

---

## 8. Skills Library

Skills are multi-step workflows exposed as slash-phrases. Each lives in `.claude/skills/<name>/SKILL.md`.

```
.claude/skills/
├── new-brand/                 # wizard → brand.config.yaml + Notion row + Drive folder
├── new-brief/                 # plain-language brief → structured brief.md
├── brief-architect/           # scaffold brief from voice + audience + goals
├── trend-scan/                # weekly trend digest (manual trigger)
├── competitor-digest/         # weekly competitor creative digest (manual trigger)
├── audience-refresh/          # monthly audience signal refresh (manual trigger)
├── sop-author/                # draft a new SOP from examples
├── sop-freshness-check/       # detect stale/contradictory SOPs
├── hypothesis-builder/        # structured hypothesis doc generation
├── hook-bank/                 # generate 10 hook candidates per script
├── script-writer/             # framework-driven script generation
├── storyboard/                # frame-by-frame visual plan
├── voice-match/               # score & propose fixes vs brand voice
├── claim-check/               # factual claim verification
├── compliance-check/          # regulated-vertical claim + language gates
├── digest/                    # morning summary: pending + research
├── status/                    # current brand status dashboard
└── rollback/                  # undo last state transition
```

### Skill structure

Each `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: hypothesis-builder
description: Build a hypothesis doc from an approved brief. Use when brief is approved and operator types /hypothesize.
allowed-tools:
  - Read
  - Write
  - mcp__notion__*
  - mcp__google_drive__*
  - Task(hypothesis-strategist)
---

# /hypothesize

## When invoked
After brief is approved.

## Steps
1. Read approved brief from `brands/<slug>/briefs/<id>.md`
2. Read live brand voice from `brands/<slug>/voice.md`
3. Invoke hypothesis-strategist sub-agent
4. Wait for output (Google Doc + Notion row + local mirror)
5. Update state to HYPOTHESIS
6. Return approval card to operator

## Output
- Google Doc URL
- Notion row ID
- Local file path
- Markdown approval card with options A/B/C

## Quality gates
- Critic must score ≥80 before approval card shown
- If <80, retry once; if still <80, escalate to operator
```

---

## 9. Workflow State Machine

Phases are explicit. State lives locally + mirrors to Notion.

### v1 phases

```
INTAKE → BRIEF → HYPOTHESIS → HOOKS → SCRIPT
   │         │         │          │         │
   ▼         ▼         ▼          ▼         ▼
 cancel   re-brief  re-hypoth.  re-hook  re-script
```

### Phase contracts

| Phase | Entry | Exit | Rollback |
|---|---|---|---|
| INTAKE | Brand folder exists; operator pastes campaign context | Brief auto-drafted | Drop campaign |
| BRIEF | Operator message; brand context loaded | `briefs/<id>.md` + Notion Briefs row | Replace brief |
| HYPOTHESIS | Brief approved | Google Doc `hypotheses/<id>.doc` + local mirror | Discard, restart from BRIEF |
| HOOKS | Hypothesis approved | Notion Hooks row + local `hooks/<id>.json` with top-3 selected | Discard, return to HYPOTHESIS |
| SCRIPT | Approved hooks | Google Doc `scripts/<id>.doc` + local mirror | Discard, return to HOOKS |

### State persistence

**Local:** `brands/<slug>/state.json`

```json
{
  "current_phase": "SCRIPT",
  "current_run_id": "acme-q4-001",
  "last_transition": "2026-10-15T12:34:56Z",
  "history": [
    {"phase": "INTAKE", "entered": "...", "exited": "..."},
    ...
  ]
}
```

**Notion mirror:** State Machine DB row (one per active brand), updated by Director via MCP on each phase exit. Operator can edit either side; sync prefers most recent.

### Parallelization

Within a phase, Director invokes sub-agents in the same turn:
- Hook-Writer and Storyboarder can run after Hypothesis-Strategist
- Voice-Match and QA-Critic run on the script in parallel

### Config-driven skipping

- `frameworks: []` → Director asks operator to pick before hypothesis
- `research cadence: manual` → no auto-suggestions
- `approval mode: minimal` → Director skips mid-phase gates

---

## 10. Bulletproof Mechanisms

### 10.1 Input Fallbacks (3-deep rule)

Every external input has 3 fallbacks before the system blocks. Sources listed in `brand.config.yaml → fallbacks`.

```
Input needed: "primary audience pain"
  ├─ Source A: client brief (most authoritative)
  ├─ Source B: meta-audience-insights + competitor comment mining
  ├─ Source C: LLM inference from niche signals
  └─ Source D: ask operator (last resort)
```

If all fail → halt phase, Director explains in plain language what's missing.

### 10.2 Validation Gates

Every inter-agent handoff validates against a schema (Hypothesis doc sections, Script doc sections, Hook JSON shape). Failures → Director explains the mismatch, retries with explicit error.

### 10.3 Idempotency

Every operation has a content hash. Re-running the same step with same inputs produces no side effects. Safe to retry.

### 10.4 Confidence Scores

Every sub-agent output includes `confidence` (0–1) with `reasons[]`. Below threshold (default 0.7):
- Client-facing → operator review
- Internal → Critic + retry once

### 10.5 Cost & Latency Budgets

**Budget is observational, not enforced.** Cost is logged to the Budget DB on every action; we review monthly and calibrate.

Director surfaces running cost in chat as informational. If cost spikes anomalously (5× normal), Director flags but doesn't block.

**Default latency budgets:**
- BRIEF: 1 turn
- HYPOTHESIS: 2 turns
- HOOKS: 2 turns
- SCRIPT: 2 turns

**Operator time per brief target:** 15–20 minutes (vs. 60–90 minutes manual).

### 10.6 Checkpoints

After every state transition:
- `brands/<slug>/state.json` updated locally
- State Machine DB row updated via MCP
- Phase artifact created (Google Docs MCP write + local file write)
- Audit Log row appended via MCP

### 10.7 Rollback

`/rollback` skill reverts the last state transition. Director:
- Restores previous `state.json`
- Restores previous artifact (Google Docs version history + git)
- Writes audit row marking the rollback

### 10.8 Dry-Run Mode

Operator can prefix any slash-phrase with `--dry`: `/script --dry`. Director runs the full pipeline but skips all writes (local + Notion + Google Docs). Returns what *would* happen as markdown preview.

### 10.9 Circuit Breakers

- Tool failing >3× → Director switches tool, retries once
- Same sub-agent step failing >3× → Director escalates to operator
- **Cost is not a circuit breaker in v1** — observing, not enforcing
- Brand-voice score consistently <0.7 → Director halts, asks operator for voice doc review

### 10.10 Safe Defaults

When brand config is ambiguous:
- Missing `industry` → defaults to b2b-saas
- Missing `tone` → Director infers from past scripts, flags for review
- Missing audience persona → Director scaffolds 1 generic; operator edits
- Missing `frameworks` → defaults to [PAS, BAB]

---

## 11. Memory Architecture

Three-tier memory with local files as source of truth, Notion + Google Docs as durable surfaces.

| Tier | Storage | Lifetime | Used for |
|---|---|---|---|
| **Run memory** | conversation context | one conversation | current task only |
| **Brand memory** | `brands/<slug>/memory.md` + Notion page per brand | brand lifetime | tone evolution, persona updates, decision history |
| **Brand voice** *(source of truth)* | `brands/<slug>/voice.md` + Google Doc per brand | forever | voice scoring + copy consistency |
| **SOP library** *(source of truth)* | `data/sops/*.md` + Notion DB | forever | retrieval across brands |
| **Past scripts** | `brands/<slug>/scripts/*.md` + Google Drive folder per brand | forever | similarity guard + inspiration |
| **Research queue** | `data/research-queue/*.md` + Notion Research DB + Google Doc digests | 90 days | routine research outputs |

*v2 adds: Winners library (`data/winners/`) + Retro memory (`brands/<slug>/retros/`)*

### Local vs. surface sync

- **Local files are written first** (via filesystem tools)
- **Notion / Google Docs are written second** (via MCP), as the durable human-visible mirror
- Sub-agents always read live from Google Docs (via MCP) for brand voice, past scripts — not from local cache
- For research queue: local files are fast cache; Notion + Google Doc are durable + cross-brand retrievable

### Retrieval discipline

Before any strategy or script task, Director:
1. Reads live brand voice from Google Docs via MCP (NOT from local cache)
2. Reads live past scripts from Google Drive via MCP (similarity check)
3. Reads top-3 relevant SOPs from `data/sops/` (local) + Notion mirror
4. Reads Notion Audit log for recent context on this brand

**Critical rule:** past scripts inform; they do NOT copy. Similarity guard: any new script matching past script >0.85 → Director regenerates with diff seed.

### Memory write rules

- Brand memory updated only by Director (or Operator directly editing local / Notion)
- SOPs promoted to "validated" only after successful use on ≥1 brand
- No silent memory: every read/write appears as an Audit Log entry

---

## 12. Audit & Observability

Every action recorded as a row in Notion **Audit Log** DB.

| Property | Type | Example |
|---|---|---|
| Timestamp | Date | 2026-10-15T12:34:56Z |
| Run id | Text | `acme-q4-001` |
| Phase | Select | BRIEF, HYPOTHESIS, HOOKS, SCRIPT |
| Step | Text | `s4` |
| Agent | Text | `script-writer` |
| Model | Select | haiku / sonnet / opus |
| Action | Text | `write`, `read`, `tool_call` |
| Input hash | Text | `sha256:...` |
| Output hash | Text | `sha256:...` |
| Cost (USD) | Number | 0.034 |
| Latency (ms) | Number | 1820 |
| Tokens in | Number | 1840 |
| Tokens out | Number | 1290 |
| Confidence | Number | 0.88 |
| Tools called | Multi-select | brand-voice.retrieve, script-validator |
| Critic score | Number | 88 |
| Human approved | Checkbox | true |

**Local fallback:** if Notion MCP is down, Director appends to `audit/<run-id>.jsonl` and retries the Notion write on next opportunity. No data loss.

### Dashboards

`/metrics` slash-phrase → Director queries Audit Log, summarizes in chat:

- Cost per campaign / per brand / per phase
- Mean human approval turnaround
- Brand-voice drift over time
- SOP compliance score

*v2 adds: hook rate distribution, winner hit rate, retro insights.*

---

## 13. The Output Documents — Schema

### 13.1 Hypothesis Doc

**Local mirror:** `brands/<slug>/hypotheses/<id>.md`
**Google Doc:** `clients/<slug>/hypotheses/<id>.doc`

```markdown
# Hypothesis: <one-line statement>

## Audience
- Persona: <name + why this hook lands for them>
- Pain: <what keeps them up at night>
- Desired outcome: <what success looks like for them>
- Proof that matters: <what evidence moves them>
- Objection: <what holds them back>

## Insight
What we believe to be true that, if true, makes this work.
Cite the source: <trend scan, audience signal, competitor pattern>

## Mechanism
Why this *should* work — the psychological or contextual lever.

## Proof
What evidence/artifact backs the claim (review, stat, founder story).

## Risks
- Brand-voice risk
- Claim risk (factual substantiation)
- Differentiation risk (vs. past scripts)

## Variants planned
- V1: <angle>
- V2: <angle>
- V3: <angle>
```

### 13.2 Script Doc

**Local mirror:** `brands/<slug>/scripts/<id>.md`
**Google Doc:** `clients/<slug>/scripts/<id>.doc`

```markdown
# Script: <campaign-name>

## Meta
- Hypothesis: <link to hypothesis Google Doc>
- Duration: 90s                 # 1 min to 5 min
- Persona: <name>
- Tone: <from brand voice doc>

## Frame-by-frame
| # | Time | Visual | Audio / VO | On-screen text (= caption) |
|---|---|---|---|---|
| 1 | 0:00-0:08 | Plumber's van pulls up | "Hey Brooklyn —" | "Brooklyn's trusted plumber" |
| 2 | 0:08-0:20 | Owner shakes hand | "[Name], licensed plumber, 18 yrs" | — |
| 3 | 0:20-0:45 | Cut to busted pipe | "When something bursts at 2am—" | "24/7 emergency" |
| 4 | 0:45-1:10 | Owner fixing, smiling family behind | "You get one number, one price, one crew" | — |
| 5 | 1:10-1:30 | Logo + CTA | "Tap. We're already on the way." | "Tap to call" |

## Hook
First 10 seconds. **Validator enforces hook lands by 0:10.** This is what stops the scroll.

## CTA
Specific, single action. Avoid "learn more."

## On-screen text (= captions)
The "On-screen text" column above IS the caption text — burned in by default since 85%+ of video plays are muted. No separate captions section needed.

## Compliance
- Avoid words check: ✅
- Required words check: ✅
- Claim substantiation: ✅ <link to proof>
- Regulated-vertical check: ✅ <if applicable>

## Validator output
- Duration 1–5 min: ✅
- Hook lands by 0:10: ✅
- Voice-match score: 0.92
```

**Script-Writer agent constraints (baked into the system prompt):**
- Duration: 1 minute to 5 minutes
- Hook window: first 10 seconds must establish person + tension
- On-screen text doubles as captions (always burned in)
- CTA: single, action-specific
- Native feel: real-footage or UGC-style preferred

**Aspect ratio is intentionally NOT in the script spec.** Aspect ratio is a production / editing decision. Director doesn't constrain it at script-writing time.

### 13.3 Brief

**Local:** `brands/<slug>/briefs/<id>.md`
**Notion:** row in Briefs DB

| Property | Type | Example |
|---|---|---|
| Title | Title | "Acme Q4 emergency-plumbing" |
| Brand | Relation | → Brand Registry row |
| Offer | Text | "24/7 emergency plumbing, licensed + insured" |
| Context | Text | "Q4 top-funnel, Brooklyn, first-time homeowners" |
| Audience confirmed | Checkbox | true |
| Status | Select | draft / approved / superseded |

### 13.4 Hooks

**Local:** `brands/<slug>/hooks/<id>.json`
**Notion:** row in Hooks DB

| Property | Type | Example |
|---|---|---|
| Brief | Relation | → Briefs row |
| Candidates | Text (JSON) | `[{"id":1, "hook":"...", "rationale":"..."}, ...]` |
| Selected | Multi-select | [1, 4, 7] |
| Voice-match top | Number | 0.92 |
| Status | Select | draft / approved / regenerated |

---

## 14. Routine Research

**No automated routines in v1** (no backend service, no cron).

Routine research is **manually triggered** by the operator:

- `/trend-scan` → Trend-Spotter runs scan, writes to local `data/research-queue/`, Notion Research Queue DB, and Google Doc digest
- `/competitor-digest` → Competitor-Watch scrapes Meta Ad Library + review sites
- `/audience-refresh` → Audience-Insights pulls updated signals
- `/digest` → Director surfaces pending approvals + recent research + stale briefs

### Research is a dump we mine, not a per-task expense

Research artifacts are written once to **local `data/research-queue/` + Notion Research Queue + Google Doc digests** and **reused across many campaigns and many brands**. The first competitor scan for "Acme Plumbing" feeds not just Acme's next brief but also informs the same competitor landscape for any other local-services brand.

The dump persists, accumulates, and gets denser over time. Director pulls relevant rows from the queue at the start of every campaign, surfaces the top matches, and decides what to incorporate.

**Implication:** spend more on research now, benefit forever. Routine sweeps are an investment in the dump, not an expense per campaign.

### Research output schema

| Property | Type |
|---|---|
| Title | Text |
| Source URLs | Text |
| Date collected | Date |
| Relevance tags | Multi-select |
| Brands applicable | Relation (→ Brand Registry) |
| Confidence | Number |
| Suggested action | Select (monitor / incorporate-now / dismiss) |
| TTL | Date |
| Digest doc | URL (Google Doc) |
| Reuse count | Number — incremented every time Director pulls it |

**Automated routines deferred to v2.**

---

## 15. SOP Library

Institutional memory lives in `data/sops/` (local files) + Notion DB mirror.

```
data/sops/
├── _index.md                     # what's where + freshness status
├── hooks/
│   ├── opening-question-pattern.md
│   ├── pattern-interrupt.md
│   ├── social-proof-first.md
│   └── ...
├── scripts/
│   ├── pas-30s.md
│   ├── bab-15s.md
│   ├── ugc-native.md
│   └── ...
├── compliance/
│   ├── regulated-vertical-claims.md
│   └── ...
└── brand-voice/
    ├── voice-score-rubric.md
    └── ...
```

### Notion mirror (SOP Library DB)

| Property | Type |
|---|---|
| Name | Title |
| Description | URL link |
| Category | Select (hooks / scripts / voice / compliance / process) |
| Status | Select (draft / tested / validated / global) |
| Body | Text (or link to local file) |
| Used by brands | Relation (→ Brand Registry) |
| Success count | Number |
| Last used | Date |
| Created | Date |

### Lifecycle

```
draft → tested (used on 1 brand) → validated (used on 3 brands) → global
   │           │                       │                        │
   └─ auto ───┴──── operator flips status in Notion ───────────┘
```

### Freshness

`/sop-freshness` slash-phrase → SOP-Freshness runs Haiku scan:
- Flags SOPs not used in 60+ days
- Detects contradictions with newer winners
- Suggests updates or archival

---

## 16. Operator Experience

Operator lives in Claude Code desktop. The local `ad-agent/` directory is the project.

### 16.1 Opening a session

```bash
cd ~/projects/ad-agent
# Open Claude Code desktop, set working dir to ad-agent/
```

Claude Code auto-loads:
- `CLAUDE.md` (Director personality)
- `.claude/agents/*.md` (sub-agents)
- `.claude/skills/*/SKILL.md` (slash-phrases)
- `.mcp.json` (MCP servers)
- `brands/` (per-brand context)
- `data/sops/` (institutional memory)

### 16.2 Plain-language entry

Operator types in chat:

```
Need a 90s video for Q4 emergency plumbing. Target: first-time
homeowners in Brooklyn who just bought 1920s houses. Top of funnel.
Goal: lead gen.
```

Director structures into a brief, confirms audience + offer, asks for clarification if needed.

### 16.3 Approval cards

When the system needs a decision, Director renders a markdown card in chat:

> **Acme Plumbing — Hypothesis Doc ready** (Google Doc link)
>
> 3 hypotheses for Q4 emergency-plumbing campaign, each with insight, mechanism, proof, and stop-loss.
>
> 🅰 **"Brooklyn-owners-of-1920s-homes" angle** — leverage licensed-insured anxiety. Risk: niche.
> 🅱 **"2am-burst" angle** — speed-of-response proof. Risk: hyperbolic.
> 🅲 **"One-number-to-call" angle** — single-crew-consistency. Risk: less novel.
>
> **My pick:** 🅱 — strongest proof asset available.
>
> 👉 Reply: `A`, `B`, `C`, `tell me more about B`, `let's do A+B`.

### 16.4 Status dashboard

`/show` slash-phrase → Director queries local `state.json` + recent Audit Log rows, returns a chat card:

```
┌─ Acme Plumbing — Q4 emergency-plumbing ─────────────┐
│ Phase: SCRIPT      Operator time this campaign: 14min │
│ Pending: 1 approval (script)                        │
│ Brand-voice match: 92%  Avg critic score: 88/100     │
│                                                       │
│ ▓▓▓▓▓▓▓▓▓▓░░░░░ SCRIPT (50% done)                  │
│                                                       │
│ Next: script doc ready in ~1 turn                    │
└───────────────────────────────────────────────────────┘
```

### 16.5 No-jargon output

All chat output uses business language:
- ✅ "Three hook candidates ready, top one scores 92% voice-match"
- ❌ "Generated 3 hook candidates using Sonnet 4.5"
- ✅ "Script ready for review" (with Google Doc link)
- ❌ "Script-Writer agent completed generation"

### 16.6 Daily digest

`/digest` slash-phrase returns:

> **3 things need your eyes today:**
>
> 1. **Acme Plumbing** — script doc ready for Q4 emergency campaign (3 min to review)
> 2. **Beta Brand** — 2 new competitor ads detected (2 min skim)
> 3. **Gamma Co** — 3 briefs auto-drafted from trend signals (8 min)
>
> **Pending approval:** script for Acme (above).

### 16.7 Pre-flight summary

Before any major action, Director renders a "what happens next" summary:

> **About to: regenerate script for Acme Q4 emergency-plumbing**
> - Will do: discard current script Google Doc, run Script-Writer with new hook seed
> - Won't do: change brief, change hypothesis, modify brand voice, touch other brands
> - Cost: ~$0.30 of API calls
> - Reversible: yes, with `/rollback last`
>
> **Approve?** (`yes` / `show me the plan` / `wait`)

### 16.8 Error messages

Plain language:

> ❌ "Couldn't reach Notion API. **What this means:** I can't write to the State DB right now. **What I'm doing:** waiting 30s and retrying, and writing to local `audit/<id>.jsonl` as backup. **What to do:** nothing — I'll surface again if it still fails."

> ❌ Not: "Error 503 from api.notion.com — Retry-After: 30"

---

## 17. Human-in-the-Loop

The operator is the gate. Director watches multiple surfaces for approval.

### v1 approval gates

| Gate | When | Approval channel |
|---|---|---|
| **New brand** | `/new-brand` wizard finishes | Chat reply |
| **New brief** | After brief auto-draft | Chat reply + Notion Briefs page status |
| **Hypothesis doc** | After hypothesis Google Doc created | Chat reply + Google Doc comment |
| **Script doc** | Final delivery | Chat reply + Google Doc comment + Notion Hooks row status |

### Approval detection — broad surface

Director watches for approvals from any of these signals:

| Signal | Detection |
|---|---|
| **Chat keywords** | `LGTM`, `approve`, `approved`, `yes`, `ship it`, `A`/`B`/`C`, `next`, `proceed` |
| **Google Doc comments** | Director queries the artifact Google Doc via MCP; looks for approval language |
| **Notion page status** | Director queries the related Notion row; checks Status property = "approved" |
| **Local file edit** | If operator directly edits the local mirror (e.g., `scripts/<id>.md`), Director detects on next read |

Operator can approve from any of: chat, Google Doc comments, Notion UI, local file edit. Director detects any of them.

### Approval depth

Driven by `approvals.mode` in `brand.config.yaml`:

- **`judgment-gated`** (default): only business-impact decisions require approval
- **`technical-gated`**: every change requires sign-off
- **`minimal`**: only kickoff + final script require approval

### Async by default

Operator wakes up to a digest of what's pending. Nothing runs silently.

---

## 18. Project Structure

```
ad-agent/
├── CLAUDE.md                    # Director personality (auto-loaded)
├── AGENTS.md                    # operator playbook
├── README.md
├── .claude/
│   ├── settings.json            # permissions, model defaults
│   ├── agents/                  # sub-agent definitions
│   │   ├── director.md
│   │   ├── planner.md
│   │   ├── critic.md
│   │   ├── brief-architect.md
│   │   ├── hypothesis-strategist.md
│   │   ├── hook-writer.md
│   │   ├── script-writer.md
│   │   ├── voice-match.md
│   │   ├── storyboarder.md
│   │   ├── routine-research.md
│   │   ├── trend-spotter.md
│   │   ├── competitor-watch.md
│   │   ├── audience-insights.md
│   │   ├── sop-freshness.md
│   │   └── universal-helper.md
│   └── skills/                  # slash-phrase workflows
│       ├── new-brand/
│       │   └── SKILL.md
│       ├── new-brief/SKILL.md
│       ├── hypothesis-builder/SKILL.md
│       ├── hook-bank/SKILL.md
│       ├── script-writer/SKILL.md
│       ├── storyboard/SKILL.md
│       ├── voice-match/SKILL.md
│       ├── trend-scan/SKILL.md
│       ├── competitor-digest/SKILL.md
│       ├── audience-refresh/SKILL.md
│       ├── sop-author/SKILL.md
│       ├── sop-freshness-check/SKILL.md
│       ├── claim-check/SKILL.md
│       ├── compliance-check/SKILL.md
│       ├── digest/SKILL.md
│       ├── status/SKILL.md
│       └── rollback/SKILL.md
├── .mcp.json                    # MCP server configs
├── brands/                      # per-brand workspaces
│   ├── _templates/              # ship-and-tweak starter configs
│   │   ├── local-services.yaml
│   │   ├── d2c.yaml
│   │   ├── b2b-saas.yaml
│   │   ├── ecommerce.yaml
│   │   ├── personal-brand.yaml
│   │   └── regulated-vertical.yaml
│   └── <slug>/
│       ├── brand.config.yaml    # source of truth
│       ├── state.json
│       ├── memory.md
│       ├── voice.md             # local mirror of Google Doc voice
│       ├── briefs/
│       ├── hypotheses/
│       ├── scripts/
│       ├── hooks/
│       ├── sops/                # brand-specific SOP overrides
│       └── retros/              # v2
├── data/                        # global libraries
│   ├── sops/                    # global SOP library (source of truth)
│   │   ├── _index.md
│   │   ├── hooks/
│   │   ├── scripts/
│   │   ├── compliance/
│   │   └── brand-voice/
│   ├── past-scripts/            # cross-brand past scripts (sample, optional)
│   └── research-queue/          # research dump (local cache)
│       └── YYYY-MM-DD/
├── notion/
│   ├── schemas/                 # DB property definitions (markdown reference)
│   │   ├── brand-registry.md
│   │   ├── state-machine.md
│   │   ├── sops.md
│   │   ├── audit-log.md
│   │   ├── briefs.md
│   │   ├── hooks.md
│   │   ├── research-queue.md
│   │   ├── runs.md
│   │   └── budget.md
│   └── provisioning.py          # one-shot script: creates all DBs
├── google-docs/
│   ├── templates/               # doc templates for artifacts
│   │   ├── hypothesis.md
│   │   ├── script.md
│   │   ├── research-digest.md
│   │   └── brand-voice.md
│   └── folder-structure.md
├── audit/                       # local audit log (fallback)
│   └── <run-id>.jsonl
├── scripts/
│   ├── provision_workspace.py   # creates Notion DBs + Google Drive folders
│   ├── new_brand.py             # wizard: brand.config.yaml + Notion row + Drive folder
│   └── export_kb_to_notion.py   # optional: syncs data/sops/ → Notion SOP Library
└── docs/runbooks/
    ├── new-brand.md
    ├── new-brief.md
    ├── knowledge-sync.md
    └── troubleshooting.md
```

**No `api/` folder. No backend service. No cron jobs.** Pure local + MCP orchestration.

---

## 19. Cost & Performance

### Cost model

Rough order-of-magnitude per campaign in v1 — **these are early estimates, not targets**:

| Task | Typical cost (USD) |
|---|---|
| Brief intake (Sonnet) | ~$0.02 |
| Hypothesis (Opus) | ~$0.30 |
| Hooks (Sonnet, 10 candidates) | ~$0.20 |
| Script (Sonnet) | ~$0.40 |
| Storyboard (Sonnet + image-gen × 6) | ~$0.50 |
| Voice-Match + Critic (Sonnet + Opus) | ~$0.30 |
| **Total per campaign (v1, early estimate)** | **~$1.70** |

These numbers will move as we learn. v1 is the calibration phase.

### Budget: observational, not enforced

We are **trialing and learning what good work costs**:

- `budget.per_campaign_usd` and `budget.monthly_usd` in `brand.config.yaml` are **advisory placeholders**, not enforced caps
- Director logs actual cost to the Notion **Budget** DB on every action
- Director surfaces running cost in chat as informational ("this campaign so far: $1.20")
- Director does **not** halt on cost overruns in v1
- Monthly review: Director's `/budget-review` shows actual cost distribution by brand / phase / agent

### What we *do* track strictly in v1

- Total operator time per brief (target: 15–20 min)
- Quality scores (voice-match, critic, operator satisfaction)
- Reuse of research dump artifacts (amortization health)
- Approval turnaround time

### Cost optimization is v2

- Image-gen batching, prompt caching, etc. — deferred
- We are intentionally not optimizing for cost in v1; quality first

*v2 (adds launch + retro): adds ~$0.30/campaign for performance pulls. ~$2.00 total. Caps to be set based on v1 observed distribution.*

---

## 20. Failure Modes & Recovery

| Failure | Detection | Recovery |
|---|---|---|
| Tool timeout | 30s circuit | swap tool, retry once |
| Model throttle | API response | downgrade one tier, flag in audit |
| Hallucinated stat | Critic + claim-check | cross-check via web search |
| Brand-voice drift | Voice-Match <0.7 | Director pulls live voice doc, retries |
| Cost overrun | budget guard | halt, surface in chat |
| Schema mismatch | validator | Director explains mismatch, retries with explicit error |
| Notion API down | MCP error | write to local `audit/<id>.jsonl` + retry next opportunity |
| Google Docs API down | MCP error | save artifact locally + flag for operator upload |
| Trend signal stale | TTL exceeded | re-pull, flag stale entries |
| Similarity to past script | similarity >0.85 | regenerate script with diff seed |
| Regulated claim unsupported | compliance-check fails | block, route to claim-check |
| Local file write fails | filesystem error | halt, surface diagnostic |

**Cardinal rule:** never lose work. Every phase artifact versioned in Google Docs / Notion + local mirror. Worst case = wasted compute, never lost creative.

---

## 21. Security & Privacy

- **Anthropic API key**: stored in env var (`ANTHROPIC_API_KEY`), referenced in `.mcp.json` via `${ANTHROPIC_API_KEY}`
- **Notion integration token**: stored in env var (`NOTION_API_KEY`)
- **Google service account creds**: stored in env vars (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`)
- **Other API keys**: `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`, `META_ACCESS_TOKEN` — all env vars
- **Brand secrets**: never in committed files; only in env or Google Docs
- **Cross-brand isolation**: each brand lives in its own folder; Director never reads across brands unless operator asks
- **Customer data**: hashed/pseudonymized when surfaced in chat
- **Audit Log**: excludes API keys, customer PII, raw creative drafts
- **`.env` file**: gitignored; operator maintains locally

### `.gitignore` essentials

```
.env
brands/*/state.json
audit/
data/research-queue/
__pycache__/
*.pyc
```

---

## 22. Roadmap to Build

### v1 (script finalization — Claude Code desktop)

Each step independently useful:

1. **Repo scaffold** — directory structure, placeholder agent files, skill stubs, Notion schemas, Google Doc templates
2. **Notion workspace provisioning** — run `notion/provisioning.py` to create all DBs
3. **Google Drive folder structure** — run `scripts/provision_workspace.py` to create top-level folders
4. **MCP config** — `.mcp.json` with all 5 servers, env vars in `.env`
5. **CLAUDE.md** — Director personality (behavior, approval keywords, error tone, slash-phrase list)
6. **Sub-agent files** — all 15 `.claude/agents/*.md` written
7. **Skill files** — all 17 `.claude/skills/*/SKILL.md` written
8. **First brand onboarded** — `/new-brand` wizard runs end-to-end on sandbox brand
9. **Brief → Hypothesis → Script flow validated** — full v1 flow runs end-to-end
10. **Deploy to first real client** — copy repo + run setup on their machine, with their Notion + Google creds

**After step 10, v1 ships.**

### v2 (post-v1, no committed timeline)

11. **Launch automation** — Meta Ads API connector + `/launch` slash-phrase
12. **Retro loop** — Retro-Analyst sub-agent + retro pulls + winners library
13. **Automated routines** — backend service (Lambda + EventBridge) for routine research
14. **Multi-platform expansion** *(if ever needed)* — YouTube / TikTok connectors + per-platform sub-agents
15. **Regulated-vertical pack** — Compliance-Critic + claim-check (deep) + regulated templates
16. **Knowledge auto-sync** — script → GitHub Action → Notion update on push

---

## 23. Open Decisions (v1)

1. **Naming.** "ScriptForge" is a placeholder. Rename?
2. **Brand folder naming convention.** Recommendation: `<slug>` (kebab-case) — `acme-plumbing`, `beta-brand`
3. **Persona model — locked to 1 persona per brand.** No secondary persona. Persona fields capture persona + pain + desired outcome + proof + objection.
4. **Budget — observational, not enforced.** No hard caps in v1. We trial-and-error to learn average allocation.
5. **Universal Helper — added as Sonnet generalist.** For formatting, summaries, one-off validations, ad-hoc assets.
6. **Research as reusable dump — confirmed.** Each artifact persists to local `data/research-queue/` + Notion Research Queue + Google Doc digest. `Reuse count` tracks value.
7. **Approval keywords — final list.** `LGTM`, `approve`, `approved`, `yes`, `ship it`, `A`/`B`/`C`, `next`, `proceed` — add others?
8. **Operator playbook format.** Single `AGENTS.md` or per-role docs? (Recommendation: single `AGENTS.md` for v1.)
9. **MCP server selection** — Notion, Google Drive, Brave, Firecrawl, Meta Ad Library confirmed. Add Image-gen MCP? (Recommendation: yes, for storyboarder.)
10. **Image-gen provider** — which MCP server? (Recommendation: pick the most reliable one available; defer choice until step 7.)
11. **Local-only mode** — should the system work without Notion + Google (degraded mode, all local)? (Recommendation: yes, with graceful degradation — artifacts saved to local only, operator manually uploads later.)

### Resolved during planning (no longer open)

- ~~Test design section in Hypothesis doc~~ — removed
- ~~On-screen text vs. captions in Script doc~~ — merged
- ~~Script duration~~ — 1 min to 5 min
- ~~Hook window~~ — 0:10
- ~~Aspect ratio in script spec~~ — removed (post-production)
- ~~Universal Project~~ — n/a; Claude Code desktop replaces this with single repo + per-brand folders
- ~~Knowledge bundle upload flow~~ — n/a; local files are source of truth, MCP syncs to Notion + Google Docs
- ~~Multiple claude.ai Projects~~ — n/a; single repo, single Claude Code desktop session

---

**Next step:** approve this doc, then I'll scaffold the repo per §18 end-to-end (placeholder agent files, skill stubs, Notion schema references, Google Doc templates, provision scripts). Then run `notion/provisioning.py` against a sandbox Notion workspace and validate the full chat flow on a sandbox brand.