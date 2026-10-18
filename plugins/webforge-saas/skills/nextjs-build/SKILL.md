---
name: nextjs-build
description: Scaffold a Next.js marketing site for a SaaS WebForge client. Use during the Build phase when type=saas, template=nextjs-marketing, deployment_target=vercel. Reads project.config.yaml and strategy/keywords.json, scaffolds the repo, generates the pages declared in deliverables.website.pages, and writes the Blog + Auth wiring.
disable-model-invocation: true
---

# /webforge-saas:nextjs-build — SaaS Next.js build

Run when the operator invokes `/webforge-saas:nextjs-build <client-slug>` and `project.type = saas`, `deliverables.website.template = nextjs-marketing`, `infrastructure.deployment_target = vercel`.

## Pre-flight checks

Before any mutation, verify:

1. `projects/<slug>/project.config.yaml` exists and validates:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/../webforge-core/scripts/validate_config.py \
     projects/<slug>/project.config.yaml
   ```
2. `projects/<slug>/strategy/keywords.json` exists (Strategy phase must be complete).
3. `projects/<slug>/state.json` shows the current phase is `build` or you've been explicitly told to skip ahead.

If any check fails, **stop** and surface the issue. Never silently proceed.

## Pre-flight summary to operator

Before mutating files, render a summary card (per ARCHITECTURE.md §13.6):

> **About to: scaffold Next.js site for <Client>**
>
> - Stack: Next.js (App Router) + TypeScript + Tailwind + shadcn/ui
> - Pages to scaffold: <list from config>
> - Blog: MDX-based (via `contentlayer` or `next-mdx-remote`)
> - CMS: <from config — sanity / contentful / markdown>
> - Deploy target: Vercel (via separate `/webforge-saas:vercel-deploy` skill)
> - Won't do: send any email, change billing, touch other clients
> - Cost: ~$0.10 of API calls (no MCP fetches beyond what config tells us)
> - Reversible: yes, git reverts cleanly
>
> **Approve?** (yes / show me the plan / wait)

## Build steps

### 1. Scaffold

Use `create-next-app` with these flags:

```bash
npx create-next-app@latest projects/<slug>/build \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --no-turbopack --use-npm
```

Non-interactive: pass `--yes` if flags above don't cover all prompts.

### 2. Configure for the client

Replace boilerplate with values from `project.config.yaml`:

- `src/app/layout.tsx` — title, description, OG tags from `brand.tone[]` + `project.goals.primary`
- `src/app/page.tsx` — hero with the inferred value prop from `intake.json`
- `tailwind.config.ts` — colors pulled from any existing brand kit; otherwise default to a clean SaaS palette

### 3. Generate pages

For each page in `deliverables.website.pages`:

```
home          → src/app/page.tsx (already overwritten in step 2)
pricing       → src/app/pricing/page.tsx
features      → src/app/features/page.tsx
docs          → src/app/docs/[[...slug]]/page.tsx (MDX)
blog          → src/app/blog/page.tsx + src/app/blog/[slug]/page.tsx
about         → src/app/about/page.tsx
contact       → src/app/contact/page.tsx
changelog     → src/app/changelog/page.tsx
```

If the page list doesn't include a common SaaS page (pricing, features), surface it: "Most SaaS sites convert better with a pricing page. Want me to add one?"

### 4. Wire content sources

For each CMS option from config:

- `cms: sanity` — install `@sanity/client`, `next-sanity`, generate `sanity.cli.ts` + `sanity.config.ts`, point to schema in `src/sanity/schemas/`
- `cms: contentful` — install `contentful` + `@contentful/rich-text-react-renderer`, generate a client
- `cms: markdown` — no install; create `content/posts/*.mdx` and wire `contentlayer.config.ts`

### 5. SEO hygiene

- Add `sitemap.ts` (App Router) reading from posts directory
- Add `robots.ts` allowing all, pointing at sitemap
- Generate `JSON-LD` for Organization schema (always), SoftwareApplication (if SaaS product), Article (for blog posts)
- Add OG image route at `src/app/og/route.tsx` using `@vercel/og`

### 6. Write the changelog

Append to `projects/<slug>/build/CHANGELOG.md`:

```
## <date> — WebForge nextjs-build v0.1

Scaffolded Next.js 14 App Router site with TypeScript, Tailwind, shadcn/ui.
Pages: <list>
CMS: <choice from config>
Blog: MDX via <library>
Cost to scaffold: ~$0.10 of compute.
Reversible: git revert.
```

## Outputs

- `projects/<slug>/build/` — the Next.js app, ready for `npm run dev`
- `projects/<slug>/build/CHANGELOG.md`
- Update `projects/<slug>/state.json` with `phase: build`, `last_step: nextjs-build`, `confidence: 0.85` (or whatever you actually observed)

## Approval gate

Before scaffolding, require the operator to reply `yes` or `approve` to the pre-flight card. ARCHITECTURE.md §13.6 — never auto-launch.

## Rollback

Every change is in git. The skill commits before each major step:
```
feat(scaffold): next.js 14 init
feat(pages): home, pricing, features
feat(cms): sanity integration
feat(seo): sitemap, robots, json-ld
```

`/webforge-saas:rollback <slug> last` reverts the last commit. `/webforge-saas:rollback <slug> <n>` reverts `n` commits.

## What you must NOT do

- Run `vercel deploy` or any deploy command — that's the `vercel-deploy` skill's job.
- Edit `project.config.yaml` or `state.json` outside the documented keys.
- Install paid tooling or paid assets without `webforge-director` approval.
- Skip the pre-flight summary. Skipping is a §13.6 violation.