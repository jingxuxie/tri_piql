# Robomimic Selector Score Analysis

Split path: `results/robomimic_inspection/can_mg_low_dim_sparse/split_indices.json`.
Seeds: `[0, 1, 2]`.
Gap max demos: `1200`.
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

## Can MG Support Frontier

Mean over seeds 0/1/2:

| k | hidden-positive selected | hidden-bad selected | purity |
|---:|---:|---:|---:|
| 20 | 15.0 | 5.0 | 0.750 |
| 40 | 32.7 | 7.3 | 0.817 |
| 80 | 63.3 | 16.7 | 0.792 |
| 120 | 91.3 | 28.7 | 0.761 |
| 160 | 115.3 | 44.7 | 0.721 |
| 240 | 162.7 | 77.3 | 0.678 |
| 320 | 205.3 | 114.7 | 0.642 |
| 480 | 284.7 | 195.3 | 0.593 |
| 640 | 353.0 | 287.0 | 0.552 |
| 800 | 410.3 | 389.7 | 0.513 |
| 1000 | 481.0 | 519.0 | 0.481 |
| 1200 | 525.3 | 674.7 | 0.438 |
| 1600 | 614.0 | 986.0 | 0.384 |

The top-ranked demos are enriched for hidden positives, but purity decays steadily as coverage increases. The useful policy region appears broader than top160, because top160 reaches only 0.100 best rollout success, while the hidden-label-free pos-p10 threshold selects 714 unlabeled demos on seed 0 and reaches 0.300 at 20k.

The current score-gap and adaptive rules are unreliable here because the classifier's top scores saturate near 1.0, causing small score differences to select either tiny support or broad support with many false positives. Can MG therefore motivates a calibrated score-to-count rule rather than another pure score-gap heuristic.
