# CAU plus v0.2 Portfolio Preflight

This is a post-hoc preflight over the same five completed Can endpoint splits.
It does not add fresh evidence and must not be promoted as a frozen paper result.
The gate scan uses only hidden-label-free setup diagnostics from the v0.2 support audit.

## Aggregate Read

- Always v0.2 selected union: `197/250`.
- Always CAU action-conflict: `193/250`.
- Best old baseline per split: `192/250`.
- Best CAU/v0.2 per split: `208/250`.
- Best non-oracle per split including old baselines, v0.2, and CAU: `212/250`.
- Best one-feature deployable preflight gate: `estimated_positive_mass_gt_47.631032` selects `208/250`, +11 versus always-v0.2 and +15 versus always-CAU.

## Best Gate Per Split

| split | selected | selected score | v0.2 | CAU | best old | estimated positive mass |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 101 | v0.2 | 45/50 | 45/50 | 33/50 | 37/50 | 45.756887 |
| 202 | v0.2 | 45/50 | 45/50 | 42/50 | 40/50 | 43.972972 |
| 303 | cau_action_conflict | 40/50 | 39/50 | 40/50 | 36/50 | 56.152973 |
| 404 | cau_action_conflict | 35/50 | 27/50 | 35/50 | 39/50 | 49.505176 |
| 505 | cau_action_conflict | 43/50 | 41/50 | 43/50 | 40/50 | 53.523725 |

## Interpretation

- The strongest simple rule is an estimated-positive-mass split gate: choose CAU on `303`, `404`, and `505`, and choose v0.2 on `101` and `202`.
- This recovers the CAU/v0.2 per-split oracle on these five splits, but only post-hoc.
- It still does not solve the split404 positive-only anchor loss: the all-method non-oracle oracle remains `4/250` higher because positive-only beats CAU on split404.
- Treat this as the next fresh-validation hypothesis, not as a claim-bearing method.

## Artifacts

- Per-split portfolio CSV: `results/sota_candidate/cau_v02_portfolio_preflight.csv`.
- Gate scan CSV: `results/sota_candidate/cau_v02_portfolio_preflight_gate_scan.csv`.
