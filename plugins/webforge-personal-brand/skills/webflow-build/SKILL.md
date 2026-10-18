---
name: webflow-build
description: Scaffold a Webflow site for a personal-brand WebForge client. Use during the Build phase when cms=webflow, deployment_target=webflow. Reads project.config.yaml + sitemap.yaml, configures the Webflow project, builds pages from intake + design system, and wires the calendar embed + lead-magnet form.
disable-model-invocation: true
---

# /webforge-personal-brand:webflow-build — Webflow scaffold

Run when the operator invokes `/webforge-personal-brand:webflow-build <client-slug>` and `cms = webflow`, `deployment_target = webflow`.

## Pre-flight checks

1. `projects/<slug>/project.config.yaml` exists and validates.
2. `projects/<slug>/strategy/sitemap.yaml` exists (Strategy phase complete).
3. Webflow account exists with permission to create projects.
4. Webflow Designer access (browser-based) — operator must be present for the visual portion.

## Pre-flight summary

> **About to: scaffold Webflow site for <Client>**
>
> - Pages: <list from sitemap>
> - Components: <list from design system>
> - Integrations: <calendar tool from intake> + <email tool>
> - Won't do: configure email sequences (separate), publish to production (separate)
> - Cost: ~$0.10
> - Time: ~4–8 hours
> - Reversible: yes, Webflow backup + page history
>
> **Approve?** (yes / show me the plan / wait)

## Build steps

### 1. Create the Webflow project

In Webflow Designer:
- New project → blank
- Connect custom domain (operator provides DNS access)
- Set site settings (timezone, language, fonts loaded)

### 2. Apply design tokens

From `projects/<slug>/brand/design-system.json`:
- Color variables (primary, accent, neutrals)
- Typography (display + body fonts via Google Fonts or Adobe Fonts)
- Spacing scale
- Apply globally via Webflow Variables

### 3. Build component library

Create reusable components (Webflow Symbols):
- Header
- Footer
- Button (primary, secondary)
- Card (testimonial, blog post, framework step)
- FAQ accordion
- CTA strip
- Form (lead magnet opt-in)

### 4. Build pages

For each page in `sitemap.yaml`:

- **Home** — hero, about, framework, testimonials, lead magnet CTA
- **About** — origin story, credentials, who-not-for, CTA
- **Offer / Work With Me** — offer details, who it's for, investment, CTA
- **Lead magnet landing** — headline, subhead, form, social proof
- **Resources / Blog** — collection with CMS
- **Contact** — calendar embed + form
- **Legal** — privacy, terms (use Webflow's generator or operator's own)

### 5. Wire integrations

- **Calendar embed:** from `intake.json.calendar_tool` (Cal.com / Calendly / SavvyCal)
- **Lead magnet form:** webhook → email tool (ConvertKit, Beehiiv, Mailchimp)
- **Analytics:** GA4 + GSC via Webflow integrations

### 6. SEO + accessibility

- Per-page title, meta description, OG image
- Sitemap.xml (Webflow generates automatically)
- Alt text on all images
- Color contrast verified
- Skip-to-content link

### 7. CHANGELOG

```
## <date> — WebForge webflow-build v1.0

Pages built: <count>
Components: <count>
Integrations: <list>
Domain: <configured | pending DNS>
Cost: ~$0.10.
Reversible: Webflow backup.
```

Update `state.json`.

## Rollback

Webflow has full site backups (Settings → Backups → restore point). Each page also has version history.

## What you must NOT do

- Configure email sequences. That's a separate skill.
- Publish to production without operator approval.
- Skip alt text. Accessibility matters.
- Use Webflow's default fonts as-is. Custom typography is part of the brand.

## Required MCP / CLI

- Webflow Designer (browser-based) — operator must be present
- OR the Webflow MCP server (`mcp__webflow__*`) — for API-driven builds

If neither, stop and surface:
> "I can't reach Webflow. The build needs the Webflow Designer (you in a browser) or the Webflow MCP. Open the Webflow Designer and grant me API access, then retry."

## Hand-off

When the build is complete:
- **webforge-personal-brand:calendar-embed** — verify calendar wiring.
- **webforge-personal-brand:lead-magnet** — verify form → email flow.
- Then publish to staging for operator review.