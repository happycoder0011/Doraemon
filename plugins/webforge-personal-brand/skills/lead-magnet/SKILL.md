---
name: lead-magnet
description: Design, build, and wire a lead magnet for a personal-brand client. Use during the Build phase when type=personal-brand and a lead capture flow exists. Reads intake.json, proposes 3 lead-magnet formats, builds the chosen one, and wires the form → email → nurture sequence.
disable-model-invocation: true
---

# /webforge-personal-brand:lead-magnet — Lead magnet + opt-in flow

Run when the operator invokes `/webforge-personal-brand:lead-magnet <client-slug>`.

## What you do

1. **Read `intake.json`** for `transformation_promise`, `niche_specificity`, `lead_magnet_idea`.
2. **Propose 3 lead-magnet formats** if not already chosen:
   - **PDF guide** — 5–15 pages on one specific outcome. Most common. Easy to consume.
   - **Template / toolkit** — spreadsheet, swipe file, or checklist. High perceived value.
   - **Mini-course** — 3–5 email sequence teaching one specific thing. Best for coaches.
   - **Quiz / assessment** — interactive; captures more zero-party data. Higher friction.
3. **Build the chosen lead magnet**:
   - For PDF: write content via the copywriter, format with brand system
   - For template: build the spreadsheet/tool, document usage
   - For mini-course: write 3–5 emails (delivered via ConvertKit / Beehiiv / Mailchimp)
   - For quiz: write the questions, scoring, result pages
4. **Build the opt-in form**:
   - Embed on the chosen page (landing page or modal)
   - Form fields: name + email (minimum). Add company / role if B2B.
   - Submit button copy: action-oriented ("Send me the guide", not "Submit")
6. **Wire the post-submit flow**:
   - Email 1 (immediate): deliver the lead magnet + quick context
   - Email 2 (3 days): one related insight, soft CTA to book a call
   - Email 3 (7 days): a longer story, harder CTA to book a call
7. **Verify end-to-end**:
   - Submit the form with operator's test email
   - Confirm lead magnet arrives in inbox
   - Confirm all 3 emails are queued correctly
   - Confirm the lead is in the email tool's audience

## Output

- Lead magnet content in `projects/<slug>/content/lead-magnet/`
- Landing page in the site (built via the niche's build skill)
- Email sequence content in `projects/<slug>/content/email/lead-magnet/`
- Setup verification in `projects/<slug>/build/CHANGELOG.md`

## Plain-language rules

Default operator is non-technical. Translate jargon: "lead magnet" → "the free thing you give away to start a conversation", "opt-in form" → "the form people fill out to get the free thing", "nurture sequence" → "the few emails that follow them up after they get it".

## What you must NOT do

- Promise a lead magnet result you can't deliver (e.g., "raise your seed round in 30 days" when the guide is 5 pages).
- Use a third-party form builder that doesn't pipe to the operator's email tool. Lost leads.
- Skip the verification flow. A broken opt-in = a broken business.
- Build a lead magnet without reading `intake.json.transformation_promise`. The offer and the magnet must align.