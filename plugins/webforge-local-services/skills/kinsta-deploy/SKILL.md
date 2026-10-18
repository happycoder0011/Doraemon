---
name: kinsta-deploy
description: Deploy a local-services WebForge site to Kinsta (or another WP host). Use during the Launch phase when deployment_target=wp-hosting. Handles git push to host, database sync, and post-deploy smoke tests. Requires operator approval for production deploys.
disable-model-invocation: true
---

# /webforge-local-services:kinsta-deploy — WP host deploy

Run when the operator invokes `/webforge-local-services:kinsta-deploy <client-slug> [production]`. Defaults to staging; pass `production` (or `prod`) to deploy to the live site.

## Pre-flight checks

1. `projects/<slug>/build/` is a git repo with at least one commit on `main`.
2. `infrastructure.deployment_target: wp-hosting` in `project.config.yaml`.
3. Kinsta SSH details configured locally.
4. A snapshot exists at `projects/<slug>/build/SNAPSHOTS.md` from the wordpress-build phase.

If any check fails, **stop** with a plain-language message.

## Pre-flight summary

> **About to: deploy <Client> to <Kinsta | host>**
>
> - Branch: `main` (staging default, or production alias)
> - Domain: <infrastructure.domain>
> - Will do: git push to host, run WP-CLI migrations, flush cache, smoke test
> - Won't do: change billing, delete snapshots, touch other sites
> - Cost: ~$0.05 (no paid services)
> - Time: ~5 min
> - Reversible: yes, host snapshot + git revert
>
> **Approve?** (yes / staging only / wait)

## Deploy steps

### 1. Push to host

```bash
cd projects/<slug>/build
git push kinsta main
```

(Adjust remote name as configured. Kinsta typically uses `kinsta` as the remote name.)

### 2. Run migrations on host

```bash
ssh <host> "cd ~/public && wp db check && wp search-replace '<staging-url>' '<production-url>' --dry-run"
```

Show the dry-run output to the operator. If sane, run without `--dry-run`.

### 3. Flush cache

```bash
ssh <host> "wp cache flush"
ssh <host> "wp rank-math option update sitemap_cache 1"  # invalidate sitemap cache
```

### 4. Smoke tests

After deploy:
- `curl -I <production-url>` → expect 200
- `curl <production-url>/sitemap.xml` → expect valid XML
- `curl <production-url>/robots.txt` → expect valid txt
- Optional: open in browser, take screenshot if operator requests

If any smoke test fails, halt and surface. Do NOT promote to a known-broken state.

### 5. Domain attach (first production deploy only)

If `infrastructure.domain` is set and not yet pointed:
- Tell the operator to set DNS A + CNAME records per Kinsta's instructions
- Wait for SSL provisioning
- Verify with `curl -I https://<domain>`

### 6. Post-deploy

- Submit sitemap to Google Search Console if not yet
- Append to `projects/<slug>/build/CHANGELOG.md` with the deployment URL, timestamp, and SHA
- Update `state.json` with `phase: launch`, `last_step: kinsta-deploy`, `last_url: <url>`

## Rollback

Two layers:

1. **Host-level:** restore the snapshot via the host dashboard (Kinsta: "Restore site to this snapshot")
2. **Git-level:** `git revert <sha>` and re-deploy

If the rollback is urgent and a snapshot is recent, use the host-level path — it's faster and doesn't require a rebuild.

## What you must NOT do

- Promote to production without explicit `production` argument AND operator `yes`.
- Skip the smoke tests. A deploy that 404s on `/sitemap.xml` is not a deploy.
- Skip the search-replace dry-run. URLs in the DB that don't get replaced break every internal link.
- Touch `projects/<slug>/build/` outside of deploy-related changes.

## Hand-off

After launch:
- Trigger `webforge-local-services:site-audit` 7 days post-launch to verify SEO health.
- Hand off to `webforge-ops` plugins (if installed) for ongoing SEO + monthly reporting.