---
name: ab-test
description: Design, run, and analyze an A/B test for a WebForge client site. Use during the Iterate phase. Reads project.config.yaml + GA4, frames a test hypothesis, calculates required sample size, runs the test, and produces a verdict with statistical confidence.
disable-model-invocation: true
---

# A/B test — WebForge universal skill

Run when the operator invokes `/<plugin>:ab-test <client-slug>` (where `<plugin>` is the niche plugin in use). This skill lives in `webforge-ecommerce` for v1.0 because ecommerce has the highest A/B test frequency; reuse from other niches by copy.

## What you do

1. **Read `project.config.yaml`** + any `analytics.monthly_reporting: true` config.
2. **Verify GA4 is connected.** If not, stop: "A/B testing without analytics is guessing. Set up GA4 + GSC first."
3. **Frame the hypothesis** with the operator:
   - **Because** [observation from GA4]
   - **We believe** [change]
   - **For** [audience segment]
   - **Will result in** [metric movement]
   - **We measure** [primary metric]

Example:
> Because mobile bounce rate on PDP is 67%, we believe adding a sticky add-to-cart button will reduce bounce by 10%. We measure scroll depth past the fold on mobile PDPs.

4. **Calculate sample size.** Use this rough calculator:
   - Baseline conversion rate (from GA4)
   - Minimum detectable effect (MDE): typically 5–10% relative lift
   - Statistical power: 80%
   - Significance: 95%
   - Use a free online calculator (Optimizely, Evan Miller) for the exact number
   - Estimate test duration at current traffic

5. **Set up the test**:
   - Use the niche's A/B tool (Shopify: Shoplift, Convert.com; WP: Google Optimize alternative — Nelio, Thrive; Next.js: Vercel Edge Config, GrowthBook).
   - Random unit: user-id hash (not session — sticky)
   - Traffic split: 50/50 default; 90/10 if low traffic
   - Run for full weeks to control for day-of-week effects (no partial weeks)

6. **Mid-test check** (after 50% of required sample size):
   - Is the test going to hit sample size in a reasonable time? If not, stop and surface.
   - Are there obvious SRM (Sample Ratio Mismatch) issues? If so, halt.

7. **Final verdict**:
   - **Winner / Loser / Inconclusive**, with p-value, lift %, confidence interval
   - If winner: roll out to 100%
   - If loser: roll back, document the learning
   - If inconclusive: extend or kill, document why

## Output

Write `projects/<slug>/iterate/ab-tests/<test-id>.md` with:

```yaml
test_id: <uuid>
hypothesis: <sentence>
primary_metric: <e.g. add-to-cart rate>
baseline: <e.g. 4.2%>
mde: <e.g. 10% relative lift>
sample_size_required: <n>
sample_size_achieved: <n>
duration_days: <d>
variant_change: <description>
results:
  winner: A | B | inconclusive
  p_value: 0.0
  lift_percent: 0.0
  confidence_interval: [low, high]
action: roll_out | roll_back | extend | kill
learning: <one paragraph for the operator>
```

## Approval gates

A/B tests that affect revenue (checkout flow, pricing display, add-to-cart) require operator approval before launch.

## What you must NOT do

- Run a test without a hypothesis. "Let's see what happens" is not science.
- Stop a test early because "we see a winner". p-hacking produces false positives.
- Run concurrent tests on the same surface. Interactions invalidate results.
- Touch code that the niche's frontend-eng owns. Test config goes through the niche's A/B tool.
- Skip sample size calculation. "Just run it for a week" usually under-powers tests.