---
name: review-markup
description: Add and validate review markup (AggregateRating + individual Review JSON-LD) across an ecommerce site. Use during the Build phase (post-reviews-app install) and whenever the reviews platform is swapped. Goal: rich snippet eligibility in Google Search.
disable-model-invocation: true
---

# /webforge-ecommerce:review-markup — Review markup

Run when the operator invokes `/webforge-ecommerce:review-markup <client-slug>`.

## What you do

1. **Read `project.config.yaml`** + `intake.json` for `reviews_platform`.
2. **Verify the reviews platform is installed** (Judge.me, Yotpo, Shopify native, etc.) and configured to surface review data via:
   - DOM injection (visible star rating + count)
   - JSON-LD injection (for search engines)
   - API endpoint (for programmatic access)
3. **Validate schema**:
   - On every PDP, JSON-LD should include either:
     - `aggregateRating` (preferred for product-level rating), OR
     - Array of `review` objects (if no aggregate)
   - Rating values must be on the 1–5 scale
   - Review count must match what's visible on the page (don't show 5 stars to users but 50 in schema — Google penalties)
4. **Spot-check 10 random PDPs** with the Rich Results Test API. Document results.
5. **Configure review-request flow** if not yet set up:
   - Email trigger (post-purchase, day 14)
   - Photo upload prompt
   - Incentive policy (don't offer incentives for positive reviews — Google penalizes this)

## Output

Write `projects/<slug>/audit/review-markup-report-<date>.md`:

```yaml
products_audited: 0
products_with_aggregate_rating: 0
products_with_review_array: 0
products_missing_markup: 0
average_rating_visible_match_schema: true | false
spot_check_results:
  - url: <PDP URL>
    rich_result_test: pass | fail
    issues: [<list>]
fix_pr_opened: <branch or PR URL>
```

## Common issues

| Issue | Fix |
|---|---|
| Star rating visible, no JSON-LD | Reviews app needs JSON-LD injection enabled |
| Schema says 50 reviews, page shows 5 | Review count sync issue — clear app cache |
| `aggregateRating` missing `ratingCount` or `reviewCount` | Add both; Google requires both |
| Reviews all dated within 1 day | Review velocity is suspicious — flag for review |
| No reviews at all | Don't fabricate; flag as content gap |

## What you must NOT do

- Fabricate reviews. Ever.
- Use schema markup that doesn't match visible page content.
- Offer incentives for positive reviews (Google penalizes this).
- Edit reviews directly. Reviews belong to customers.