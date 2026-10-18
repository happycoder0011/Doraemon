---
name: link-outreach
description: Run the link-outreach workflow for a WebForge client. Reads strategy/keywords.json, identifies link prospects, drafts personalized emails, and tracks responses. Operator reviews and sends.
disable-model-invocation: true
---

# /webforge-ops:link-outreach — Backlink acquisition workflow

Run when the operator invokes `/webforge-ops:link-outreach <client-slug>`.

## Pre-flight checks

1. `deliverables.outreach.backlink_campaign: true` in `project.config.yaml`.
2. `strategy/keywords.json` exists with a niche pillar to anchor outreach around.
3. The operator's email-sending setup is in place (Gmail, Outlook, or via an email tool).

## What you do

1. **Read `project.config.yaml`** + `strategy/keywords.json`.
2. **Build a prospect list** of 25 sites in the niche with editorial standards:
   - Use the `webforge-ops-outreach` agent's framework
   - Diversify across: blogs, news sites, industry publications, podcast directories
   - Don't include obvious competitors (you won't get links from them)
3. **For each prospect, draft a personalized email**:
   - Subject line (under 50 chars)
   - Body (under 200 words)
   - Specific compliment referencing their work
   - One ask (link to your content, guest post, or partnership)
4. **Batch by week**: send 5–10 emails per week max. Sending 50/week triggers spam filters.
5. **Track responses**:
   - Reply within 24 hours when possible
   - Follow up once 7 days after first send
   - Move to "lost" after 14 days no reply
6. **Report weekly**: prospects contacted, replies received, links earned.

## Output

`projects/<slug>/outreach/link-outreach-<date>.md` with the prospect list and current state.

## Approval

Every email requires operator review before send. The skill produces drafts; the operator (or an authorized VA) sends.

## What you must NOT do

- Send emails without operator approval per email.
- Use templates that aren't personalized.
- Buy links. Paid links violate Google's guidelines and will get the site penalized.
- Send more than 10 outreach emails per week per client.
- Use scraped emails. Use the prospect's published contact info or a verified email-finding tool (Hunter.io, Apollo) where the address is publicly listed.