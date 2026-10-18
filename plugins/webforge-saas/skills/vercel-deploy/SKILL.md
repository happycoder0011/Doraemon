---
name: vercel-deploy
description: Deploy a SaaS WebForge site to Vercel. Use during the Launch phase when deployment_target=vercel. Handles preview deployments, environment variable wiring, domain attachment via DNS, and post-deploy smoke tests. Requires operator approval for production deploys.
disable-model-invocation: true
---

# /webforge-saas:vercel-deploy — Vercel deploy

Run when the operator invokes `/webforge-saas:vercel-deploy <client-slug> [production]`. Defaults to preview deploy; pass `production` (or `prod`) to deploy to the production alias.

## Pre-flight checks

1. `projects/<slug>/build/` exists and contains a Next.js app (look for `package.json` + `next.config.*`).
2. `projects/<slug>/build/` is a git repo with at least one commit on `main`.
3. `infrastructure.deployment_target: vercel` in `project.config.yaml`.
4. Vercel credentials available. If the Vercel MCP server is connected, use it. Otherwise shell out to `vercel` CLI.

If any check fails, **stop** with a plain-language message.

## Pre-flight summary

> **About to: deploy <Client> to Vercel**
>
> - Project: <slug> → Vercel project `<slug>` (will be created if missing)
> - Branch: `main` (preview deploy default, or production alias)
> - Domain: <infrastructure.domain> (will be attached after DNS check)
> - Will do: build, upload, alias, run smoke test, submit sitemap to GSC
> - Won't do: change billing, delete anything, touch other Vercel projects
> - Cost: ~$0.05 (Vercel free tier covers it)
> - Time: ~5 min
> - Reversible: yes, `vercel rollback` + git revert
>
> **Approve?** (yes / preview only / wait)

## Deploy steps

### 1. Link project (one-time)

```bash
cd projects/<slug>/build
vercel link --yes
```

This writes `.vercel/project.json`. Commit it for reproducibility.

### 2. Set environment variables

For each variable the Next.js app expects (read from `.env.example` if present), ask the operator to provide or confirm. Never log secrets.

### 3. Preview deploy

```bash
vercel deploy --yes
```

Capture the preview URL. Render in plain language: "Preview live at `<url>`. Test it; reply `production` when ready."

### 4. Smoke tests

After preview deploy, run:
- `curl -I <preview-url>` → expect 200
- `curl <preview-url>/sitemap.xml` → expect valid XML
- `curl <preview-url>/robots.txt` → expect valid txt
- Optional: open in browser, take screenshot if operator requests

If any smoke test fails, halt before promotion.

### 5. Production deploy (requires explicit `production` arg)

```bash
vercel deploy --prod --yes
```

Capture the production URL.

### 6. Domain attach

If `infrastructure.domain` is set:
- Add the domain via Vercel API or CLI
- Tell the operator to set the DNS records Vercel prints (typically an A record + CNAME for www)
- Wait for SSL provisioning before declaring done

### 7. Post-deploy

- Submit sitemap to Google Search Console (via GSC MCP if connected, else surface the URL for operator to paste)
- Append to `projects/<slug>/build/CHANGELOG.md` with the deployment URL, timestamp, and SHA
- Update `state.json` with `phase: launch`, `last_step: vercel-deploy`, `last_url: <url>`

## Rollback

Two layers:

1. **Vercel-level:** `vercel rollback` reverts to the previous deployment instantly. No code change.
2. **Git-level:** revert the offending commit and redeploy. Slower, but fixes the bug for next deploy.

## What you must NOT do

- Promote to production without explicit `production` argument AND operator `yes`.
- Log any secret to the terminal or audit log. Audit log schema (`ARCHITECTURE.md §12`) excludes secret fields.
- Skip the smoke tests. A deploy that 404s on `/sitemap.xml` is not a deploy.
- Touch `projects/<slug>/build/` outside of build-related changes (no doc edits, no config edits) — those are separate steps.

## Required MCP / CLI

This skill requires either:
- The Vercel MCP server (`mcp__vercel__*`), OR
- `vercel` CLI installed and authenticated locally

If neither, stop and surface:
> "I can't reach Vercel — neither the MCP nor the CLI is set up. Run `vercel login` or add the Vercel MCP, then retry."