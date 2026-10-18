---
name: shopify-build
description: Scaffold a Shopify storefront for an ecommerce WebForge client. Use during the Build phase when cms=shopify, deployment_target=shopify. Reads project.config.yaml and intake.json, sets up the store, theme, products, and apps. Hands off to deploy.
disable-model-invocation: true
---

# /webforge-ecommerce:shopify-build — Shopify scaffold

Run when the operator invokes `/webforge-ecommerce:shopify-build <client-slug>` and `cms = shopify`, `deployment_target = shopify`.

## Pre-flight checks

1. `projects/<slug>/project.config.yaml` exists and validates:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/../webforge-core/scripts/validate_config.py \
     projects/<slug>/project.config.yaml
   ```
2. `projects/<slug>/strategy/keywords.json` exists.
3. Shopify Partner account + development store exists.
4. Shopify CLI is installed locally (`shopify version` should print ≥ 3.x).

## Pre-flight summary

> **About to: scaffold Shopify store for <Client>**
>
> - Theme: <Dawn | Prestige | Motion | custom>
> - Products: <count from intake>
> - Apps to install: <list with monthly cost each>
> - Won't do: configure payments/shipping (separate), publish to live store, charge the client
> - Cost: ~$0.20 of API calls
> - Time: ~2–6 hours depending on catalog size
> - Reversible: yes (development store is isolated)
>
> **Approve?** (yes / show me the plan / wait)

## Build steps

### 1. Initialize dev store

```bash
cd projects/<slug>/build
shopify auth login
shopify theme init --name=<client-slug>-theme
```

### 2. Install theme

Pick per `webforge-ecommerce-frontend-eng` recommendation. If paid theme, operator must purchase separately.

### 3. Install apps

For each app in the recommendation, present cost + benefit, get operator approval, configure. Common stack:

- Judge.me (free / $15/mo) — reviews
- Klaviyo (free up to 250 contacts) — email + SMS
- Searchanise or Algolia (varies) — search
- Inbox (Gorgias, Tidio) — chat support
- ReConvert or Bold Upsell — upsells

**Each paid app is a recurring cost — confirm with operator before install.**

### 4. Import products

For each product in the catalog:
- Title, description (from `content/products/<slug>.md`)
- Images (from operator or stock)
- Variants (size, color, etc.)
- Pricing (from operator)
- Inventory (if known; 3PL sync can come later)
- SEO fields (title, description, alt text)

Import via CSV or via the Shopify Admin API. Surface the CSV template for operator review if doing manual import.

### 5. Configure pages

For each page in `deliverables.website.pages`, create the page in Shopify with content from `content/categories/*.md` or copywriter output.

### 6. Configure collections

For each category from `strategy/keywords.json.category_map`, create a Shopify collection (smart or manual based on catalog).

### 7. Schema + sitemap

Verify the SEO app or built-in settings generate:
- `Product` schema on every PDP
- `CollectionPage` schema on every category
- `Organization` schema on home
- `BreadcrumbList` sitewide
- `sitemap.xml` submitted to GSC

### 8. CHANGELOG entry

```
## <date> — WebForge shopify-build v1.0

Theme: <choice>
Products imported: <count>
Apps installed: <count + list + monthly cost>
Pages created: <count>
Collections: <count>
Cost to scaffold: ~$0.20.
Reversible: development store is isolated.
```

Update `state.json`.

## Rollback

Working on a development store means rollback = delete the dev store. Nothing to undo on production until you push.

For live store changes: Shopify has theme version history (last 20 versions) and one-click rollback.

## What you must NOT do

- Configure payments or shipping. That's backend-eng's job.
- Push to live store without `webforge-ecommerce:shopify-deploy` skill + operator approval.
- Install paid apps without per-app approval.
- Skip the schema verification step.

## Required MCP / CLI

- Shopify CLI installed and authenticated, OR
- The Shopify MCP server (`mcp__shopify__*`)

If neither, stop and surface:
> "I can't reach Shopify — neither the CLI nor MCP is set up. Install Shopify CLI + log in, or add the Shopify MCP, then retry."

## Hand-off

When build is complete:
- **webforge-ecommerce:product-schema** — validate JSON-LD on PDPs and category pages.
- **webforge-ecommerce:review-markup** — confirm review snippets can render in search.
- Then deploy via standard Shopify flow (publish theme).