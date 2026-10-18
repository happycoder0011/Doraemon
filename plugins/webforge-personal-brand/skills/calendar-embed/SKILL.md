---
name: calendar-embed
description: Embed and verify a calendar booking widget (Cal.com, Calendly, SavvyCal) on a personal-brand site. Use during the Build phase and after any calendar tool change. Verifies the embed renders, the booking flow works end-to-end, and the lead notification fires.
disable-model-invocation: true
---

# /webforge-personal-brand:calendar-embed — Booking widget

Run when the operator invokes `/webforge-personal-brand:calendar-embed <client-slug>`.

## Pre-flight checks

1. `projects/<slug>/intake.json.calendar_tool` is set.
2. The booking tool account is created and active.
3. The site page that embeds the calendar exists (`/contact` or `/book`).

## What you do

1. **Read `intake.json.calendar_tool`** (cal.com / calendly / savvycal / other).
2. **Generate the embed code** per the tool's docs:
   - **Cal.com:** `<iframe src="https://cal.com/<username>/<event>" ...>`
   - **Calendly:** inline embed script `<div class="calendly-inline-widget" data-url="..."></div>` + script tag
   - **SavvyCal:** inline embed script
3. **Configure the embed**:
   - Default duration (15 / 30 / 60 min)
   - Availability windows
   - Pre-call questions (1–3 max — name, what they want to discuss, budget if relevant)
   - Confirmation email template
   - Reminder email template
   - Notification webhook to email tool or CRM
4. **Verify the booking flow end-to-end**:
   - Open the embed on mobile + desktop
   - Submit a test booking
   - Confirm operator receives email notification
   - Confirm the calendar event appears on operator's calendar
   - Confirm the lead is in the connected CRM (if any)
5. **Append to changelog**:
   ```
   ## <date> — WebForge calendar-embed v1.0
   Tool: <cal.com | etc.>
   Embed verified on: <pages>
   Test booking: <confirmed email fired? Y/N>
   ```

## Common issues

| Issue | Fix |
|---|---|
| Embed shows blank on mobile | Use a different embed style (popup → inline, or inline → popup) |
| Notification email not received | Check notification settings in the booking tool |
| Time zone confusion | Set explicit time zone in the embed config (operator's) |
| Calendar sync delays | Allow 5–10 min; many providers sync asynchronously |
| Spam bookings | Add CAPTCHA via the booking tool's settings |

## What you must NOT do

- Use the embed without testing the full booking flow.
- Configure pre-call questions that ask for sensitive data (SSN, payment info).
- Disable notifications. Silent bookings lose leads.
- Touch `project.config.yaml`.

## Hand-off

When the embed is verified, hand off to **webforge-personal-brand:lead-magnet** if also being built, or to deploy.