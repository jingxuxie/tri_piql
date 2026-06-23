# Robomimic Adaptive Positive-Mass Selector Summary

This report summarizes a hidden-label-free adaptive support rule for the Robomimic Can paired low-dimensional experiments. The rule is designed to choose between coverage and precision without using hidden positive/bad labels.

Note: this is now the predecessor to the mass-capped adaptive selector in `results/robomimic_adaptive_masscap_selector_summary/REPORT.md`. The endpoint policy decisions are unchanged, but the positive-count sweep found that this original switch can over-expand support in intermediate contamination regimes.

## Rule

For each classifier seed:

1. Score each unlabeled demo by the mean state-action classifier probability.
2. Compute labeled demo score means for the scarce positive and negative sets.
3. Estimate unlabeled positive-demo mass as:

```text
sum_demo clip((score_demo - labeled_negative_mean) / (labeled_positive_mean - labeled_negative_mean), 0, 1)
```

4. Let the coverage floor be `max(abs_min, ceil(4 x labeled_positive_demo_count))`. With 10 labeled-positive demos this is 40.
5. If estimated positive mass is at least the floor, use coverage-aware score-gap posx4. Otherwise use precision mode: top `2 x labeled_positive_demo_count` unlabeled demos.

This uses only labeled positives, labeled negatives, unlabeled classifier scores, and the label budget.

Artifacts:

- Balanced selector analysis: `results/robomimic_selector_score_analysis_balanced_80p80b/REPORT.md`
- Stress selector analysis: `results/robomimic_selector_score_analysis_stress_p20_b80/REPORT.md`
- Balanced policy summary: `results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md`
- Heavy-contamination policy summary: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`

## Selector Decisions

| split | seed | estimated positive mass | coverage floor | adaptive mode | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| balanced 80p/80b | 0 | 82.3 | 40 | coverage-gap | 73 | 67 | 6 | 0.918 |
| balanced 80p/80b | 1 | 84.6 | 40 | coverage-gap | 45 | 45 | 0 | 1.000 |
| balanced 80p/80b | 2 | 80.4 | 40 | coverage-gap | 66 | 65 | 1 | 0.985 |
| stress 20p/80b | 0 | 33.7 | 40 | precision top20 | 20 | 15 | 5 | 0.750 |
| stress 20p/80b | 1 | 35.9 | 40 | precision top20 | 20 | 14 | 6 | 0.700 |
| stress 20p/80b | 2 | 32.6 | 40 | precision top20 | 20 | 16 | 4 | 0.800 |

Aggregate support:

| split | adaptive mode | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---|---:|---:|---:|---:|
| balanced 80p/80b | coverage-gap | 184 | 177 | 7 | 0.962 |
| stress 20p/80b | precision top20 | 60 | 45 | 15 | 0.750 |

## Policy Results Carried Over

The adaptive selector exactly matches already-trained official BC-RNN-GMM policies in both regimes:

- Balanced split: adaptive selects coverage-aware score-gap posx4.
- Stress split: adaptive selects precision-biased top20.

Three-seed mean success:

| split | adaptive selector | 5k | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|
| balanced 80p/80b | coverage-gap | 0.133 | 0.800 | 0.867 | 0.900 |
| stress 20p/80b | precision top20 | 0.000 | 0.367 | 0.433 | 0.667 |

Relevant controls:

| split | control | 5k | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|
| balanced 80p/80b | fixed top80 | 0.233 | 0.700 | 0.733 | 0.833 |
| stress 20p/80b | posx4 | 0.067 | 0.267 | 0.300 | 0.333 |
| stress 20p/80b | fixed top80 | 0.067 | 0.233 | 0.167 | 0.233 |

## Interpretation

The adaptive rule captures the current Robomimic mechanism story. When the unlabeled pool appears to contain enough positive mass, coverage helps and the selector expands beyond a small high-confidence prefix. When estimated positive mass is below the coverage floor, forcing coverage admits too many bad demos, so the selector stays precision-biased.

This is stronger than presenting separate hand-picked rules for balanced and stress settings, but the later positive-count sweep found an intermediate-regime over-expansion issue. Use the mass-capped selector summary as the current paper-facing artifact.
