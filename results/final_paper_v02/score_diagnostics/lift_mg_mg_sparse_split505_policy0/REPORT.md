# Robomimic Selector Score Analysis

Split path: `results/final_paper_v02/splits/lift_mg_mg_sparse_split505/split_indices.json`.
Seeds: `[0]`.
Gap max demos: `80`.
Gap min demos: `4`.
Gap min labeled-positive multiplier: `4.0`.
Adaptive mass-cap ratio: `1.25`.

## Files

- `demo_rankings.csv`: full unlabeled demo score rankings by seed.
- `score_summary.csv`: labeled positive / negative score calibration summary.
- `precision_at_k.csv`: hidden support composition for fixed top-k prefixes.
- `selection_rules.csv`: hidden support composition for score-gap, calibrated candidate rules, `adaptive_posmass`, and `adaptive_masscap`.

## Adaptive Rule

`adaptive_posmass` estimates unlabeled positive-demo mass from classifier scores calibrated by labeled positive and negative demo means. If the estimated mass is at least the effective score-gap coverage floor, it uses coverage-aware score-gap. Otherwise, it switches to precision mode with top `2 x labeled-positive demo count` unlabeled demos.

`adaptive_masscap` uses the same precision/coverage decision, but caps coverage when the score-gap cut selects more than the configured multiple of estimated positive mass. In that case it takes the top estimated-positive-mass demos rather than trusting an oversized gap cut.
