# Robomimic Adaptive Mass-Capped Selector Summary

This report summarizes the current paper-facing Robomimic support selector. It refines the earlier positive-mass adaptive rule with a hidden-label-free mass cap so that coverage mode cannot select far more demos than the calibrated unlabeled positive-mass estimate.

## Rule

For each classifier seed:

1. Score each unlabeled demo by the mean state-action classifier probability.
2. Compute labeled demo score means for the scarce positive and negative sets.
3. Estimate unlabeled positive-demo mass:

```text
sum_demo clip((score_demo - labeled_negative_mean) / (labeled_positive_mean - labeled_negative_mean), 0, 1)
```

4. Let the coverage floor be `max(abs_min, ceil(4 x labeled_positive_demo_count))`. With 10 labeled-positive demos this is 40.
5. If estimated positive mass is below the floor, use precision mode: top `2 x labeled_positive_demo_count` unlabeled demos.
6. Otherwise use coverage-aware score-gap, unless the gap cut selects more than `1.25 x estimated_positive_mass` demos. If it does, use the top `ceil(estimated_positive_mass)` demos.

This uses only labeled positives, labeled negatives, unlabeled classifier scores, and the label budget.

Artifacts:

- Sweep: `results/robomimic_adaptive_selector_sweep_pos_count/REPORT.md`
- Intermediate 40p/80b three-seed policy check: `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`
- No-bad-label positive-only NN policy control: `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_3seed_summary/REPORT.md`
- Bad-label support ablation: `results/robomimic_bad_label_ablation/REPORT.md`
- Balanced selector analysis: `results/robomimic_selector_score_analysis_balanced_80p80b/REPORT.md`
- Stress selector analysis: `results/robomimic_selector_score_analysis_stress_p20_b80/REPORT.md`
- Balanced policy summary: `results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md`
- Heavy-contamination policy summary: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`
- Earlier positive-mass rule: `results/robomimic_adaptive_posmass_selector_summary/REPORT.md`

## Endpoint Policy Anchors

The mass-capped rule exactly matches the already-trained official BC-RNN-GMM policies at the two policy-evaluated endpoints:

| split | mass-capped mode | selected unlabeled | hidden-positive | hidden-bad | purity | 20k mean success |
|---|---|---:|---:|---:|---:|---:|
| balanced 80p/80b | coverage-gap | 184 | 177 | 7 | 0.962 | 0.900 |
| stress 20p/80b | precision top20 | 60 | 45 | 15 | 0.750 | 0.667 |

Relevant endpoint controls:

| split | control | 20k mean success |
|---|---|---:|
| balanced 80p/80b | fixed top80 | 0.833 |
| stress 20p/80b | posx4 coverage-gap | 0.333 |
| stress 20p/80b | fixed top80 | 0.233 |

## Positive-Count Sweep

This support-only sweep fixes 80 hidden-bad unlabeled demos and varies hidden-positive unlabeled demos. It validates selector behavior without claiming policy performance for untrained intermediate mixtures.

| hidden pos | hidden bad | bad frac | mass mean | mass-capped mode | selected | hidden pos | hidden bad | purity | recall |
|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 5 | 80 | 0.941 | 23.032 | precision_top20 | 20.000 | 5.000 | 15.000 | 0.250 | 1.000 |
| 10 | 80 | 0.889 | 27.452 | precision_top20 | 20.000 | 10.000 | 10.000 | 0.500 | 1.000 |
| 20 | 80 | 0.800 | 34.061 | precision_top20 | 20.000 | 15.000 | 5.000 | 0.750 | 0.750 |
| 30 | 80 | 0.727 | 42.192 | coverage_gap,top_estimated_mass | 46.333 | 28.333 | 18.000 | 0.616 | 0.944 |
| 40 | 80 | 0.667 | 49.427 | top_estimated_mass | 50.000 | 36.333 | 13.667 | 0.728 | 0.908 |
| 50 | 80 | 0.615 | 57.903 | coverage_gap,top_estimated_mass | 49.333 | 41.000 | 8.333 | 0.833 | 0.820 |
| 60 | 80 | 0.571 | 66.178 | coverage_gap | 53.667 | 48.667 | 5.000 | 0.910 | 0.811 |
| 70 | 80 | 0.533 | 74.573 | coverage_gap | 54.000 | 51.667 | 2.333 | 0.963 | 0.738 |
| 80 | 80 | 0.500 | 82.426 | coverage_gap | 61.333 | 59.000 | 2.333 | 0.968 | 0.737 |

Key comparison at 40 hidden-positive / 80 hidden-bad:

| selector | selected | hidden-positive | hidden-bad | purity | recall |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 50.000 | 36.333 | 13.667 | 0.728 | 0.908 |
| original positive-mass switch | 74.000 | 40.000 | 34.000 | 0.541 | 1.000 |
| top20 precision | 20.000 | 19.667 | 0.333 | 0.983 | 0.492 |
| fixed top80 | 80.000 | 40.000 | 40.000 | 0.500 | 1.000 |

## Intermediate Policy Check

Three-seed official BC-RNN-GMM on the 40p/80b split gives:

| selector | selected unlabeled mean | hidden-positive mean | hidden-bad mean | purity mean | 5k | 10k | 15k | 20k | best-per-seed mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| original coverage-gap | 74.0 | 40.0 | 34.0 | 0.541 | 0.167 | 0.333 | 0.567 | 0.600 | 0.667 |
| top20 precision | 20.0 | 19.7 | 0.3 | 0.983 | 0.033 | 0.567 | 0.667 | 0.700 | 0.700 |
| positive-only NN top40 | 40.0 | 31.0 | 9.0 | 0.775 | 0.167 | 0.433 | 0.533 | 0.633 | 0.767 |

Top20 precision remains a strong control and has the best 10k mean, but it leaves about half of the available hidden-positive support unused. Positive-only NN top40 is a strong no-bad-label control and ties masscap on best-per-seed mean, but it is lower at fixed 10k/15k/20k checkpoints. Coverage-gap recovers all hidden positives but admits too many hidden-bad demos. Mass-capped support keeps the intended middle ground and gives the best 15k and 20k mean success on this intermediate split.

## Interpretation

The mass-capped rule preserves the two validated policy endpoints while addressing the main failure revealed by the sweep: an estimated positive mass just above the coverage floor can still produce an oversized score-gap cut. The cap keeps the decision hidden-label-free and trades a small amount of positive recall for much less hidden-bad support in intermediate contamination regimes.

The current Robomimic selector story is therefore not that one fixed support size is always best, nor that bad labels are strictly necessary on every split. It is that scarce labels plus bad demonstrations can drive a hidden-label-free precision/coverage tradeoff with better fixed-budget stability: coverage for balanced pools, top20-style precision for heavy contamination, and mass-capped coverage for the intermediate regime.
