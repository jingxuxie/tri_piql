# Robomimic Adaptive Selector Positive-Mass Sweep

This support-only sweep fixes the Robomimic Can scarce labels and keeps 80 hidden-bad unlabeled demos, then varies how many hidden-positive demos are present in the unlabeled pool. The adaptive rules are fixed before the sweep and use no hidden labels for their decisions.

Main rule: estimate unlabeled positive-demo mass from classifier scores calibrated by labeled positive and negative demo-score means. If the estimated mass is below the `4 x labeled-positive` coverage floor, use top20 precision mode. Otherwise use coverage-gap unless the gap cut selects more than the configured multiple of estimated positive mass; in that case use the top estimated-positive-mass demos.

## Files

- `per_seed_selection.csv`: every seed, mixture, and selector.
- `aggregate_selection.csv`: mean support statistics by mixture and selector.
- `config.json`: sweep arguments.

## Mass-Capped Adaptive Decisions

| hidden pos | hidden bad | bad frac | mass mean | adaptive mode | selected | hidden pos | hidden bad | purity | recall |
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

## Controls at Representative Mixtures

| hidden pos | method | mode | selected | hidden pos | hidden bad | purity | recall |
|---:|---|---|---:|---:|---:|---:|---:|
| 20 | adaptive_masscap | precision_top20 | 20.000 | 15.000 | 5.000 | 0.750 | 0.750 |
| 20 | adaptive_posmass | precision_top20 | 20.000 | 15.000 | 5.000 | 0.750 | 0.750 |
| 20 | coverage_gap | coverage_gap | 52.333 | 20.000 | 32.333 | 0.384 | 1.000 |
| 20 | top20 | top20 | 20.000 | 15.000 | 5.000 | 0.750 | 0.750 |
| 20 | top80 | top80 | 80.000 | 20.000 | 60.000 | 0.250 | 1.000 |
| 40 | adaptive_masscap | top_estimated_mass | 50.000 | 36.333 | 13.667 | 0.728 | 0.908 |
| 40 | adaptive_posmass | coverage_gap | 74.000 | 40.000 | 34.000 | 0.541 | 1.000 |
| 40 | coverage_gap | coverage_gap | 74.000 | 40.000 | 34.000 | 0.541 | 1.000 |
| 40 | top20 | top20 | 20.000 | 19.667 | 0.333 | 0.983 | 0.492 |
| 40 | top80 | top80 | 80.000 | 40.000 | 40.000 | 0.500 | 1.000 |
| 80 | adaptive_masscap | coverage_gap | 61.333 | 59.000 | 2.333 | 0.968 | 0.737 |
| 80 | adaptive_posmass | coverage_gap | 61.333 | 59.000 | 2.333 | 0.968 | 0.737 |
| 80 | coverage_gap | coverage_gap | 61.333 | 59.000 | 2.333 | 0.968 | 0.737 |
| 80 | top20 | top20 | 20.000 | 20.000 | 0.000 | 1.000 | 0.250 |
| 80 | top80 | top80 | 80.000 | 72.000 | 8.000 | 0.900 | 0.900 |

## Interpretation

The sweep tests the selector decision rule itself rather than policy performance at every mixture. The already-trained endpoint policies anchor two modes that the mass-capped rule preserves: balanced 80p/80b uses coverage-gap and reaches 0.900 mean success at 20k, while heavy contamination 20p/80b uses precision top20 and reaches 0.667 mean success at 20k.

The mass cap is important in the intermediate 30-40 hidden-positive regime: the original positive-mass switch would move to coverage, but the score-gap cut can select substantially more demos than the calibrated positive-mass estimate. The capped rule keeps the decision hidden-label-free while avoiding an oversized gap cut.

A paper claim should describe this as mechanism evidence for an adaptive purity/coverage rule. Intermediate mixtures still need policy rollouts before claiming end-to-end performance there.
