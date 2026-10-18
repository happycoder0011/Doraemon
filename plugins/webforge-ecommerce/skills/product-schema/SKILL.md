---
name: product-schema
description: Validate and fix Product and Offer JSON-LD schema markup across an ecommerce site's product pages. Use during the Build phase (post-theme, pre-launch) and after any catalog change. Catches missing fields, invalid values, and Google's Structured Data penalties before they impact Shopping visibility.
disable-model-invocation: true
---

# /webforge-ecommerce:product-schema — Product schema validation

Run when the operator invokes `/webforge-ecommerce:product-schema <client-slug>`.

## What you check

For every product page (or a sample of 20 if the catalog is large), validate the JSON-LD against Google's Product schema requirements:

### Required fields

- `@context`: `https://schema.org`
- `@type`: `Product`
- `name`: product title
- `image`: at least one product image URL
- `description`: product description
- `sku` or `mpn` (or both)
- `brand`: at least `{ "@type": "Brand", "name": "..." }`
- `offers`: nested `Offer` with:
  - `@type`: `Offer`
  - `price`: numeric, no currency symbol
  - `priceCurrency`: ISO 4217 code (USD, EUR, etc.)
  - `availability`: `InStock`, `OutOfStock`, `PreOrder`, etc.
  - `url`: PDP URL

### Recommended fields (boost rich result eligibility)

- `aggregateRating`: from review platform
- `review`: array of individual reviews
- `gtin` or `isbn`: if applicable (helps Google Shopping match)
- `weight`, `size`, `color`, `material`: variant data
- `shippingDetails`: shipping destinations + costs
- `hasMerchantReturnPolicy`: return policy URL + days

### Common errors you fix

- `price` as a string with currency symbol (`"$29.99"` → `29.99` + `priceCurrency: "USD"`)
- `availability` not in Google's enum
- Missing `aggregateRating` when reviews exist
- `image` pointing at a Shopify CDN URL that's blocked by robots
- Multiple `Product` blocks on one page (Google may ignore all)
- `Offer` without `url` field

## Output

Write `projects/<slug>/audit/product-schema-report-<date>.md`:

```yaml
products_audited: 0
products_passing: 0
products_with_errors: 0
error_categories:
  - schema: <description>
    affected_count: 0
    severity: blocker | high | medium
    fix_skill: <webforge-ecommerce:product-schema>
    sample_products: [<slug1>, <slug2>]
fix_pr_opened: <branch or PR URL>
```

Then open a fix PR (or hand off to the SEO-Tech agent for batch fixes):
- `fix/schema-product`: missing required fields
- `fix/schema-offers`: Offer block normalization
- `fix/schema-reviews`: aggregateRating + review arrays
- `fix/schema-shipping`: shippingDetails + hasMerchantReturnPolicy

## Validation tools

Use Google's Rich Results Test API or the Schema.org validator. If neither is reachable, surface as a gap and proceed with manual schema review.

## What you must NOT do

- Edit products directly. Schema fixes go through the storefront theme or app config.
- Mark a product as fixed without re-running the validator.
- Skip Google Shopping requirements (`gtin`/`mpn`, `shipping`, `availability`). Shopping visibility drops without them.
- Approve schema that contains fabricated reviews.