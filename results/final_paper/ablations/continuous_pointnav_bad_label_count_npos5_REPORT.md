# Continuous PointNav Bad-Label-Count Diagnostic

This diagnostic fixes the positive label budget at 5 route-prefix demonstrations and varies the number of labeled bad shortcut trajectories. It tests how much explicit negative supervision is needed for the controlled PointNav mechanism.

Protocol:

- Task: 2D continuous PointNav with start in the lower-left, goal in the upper-right, and a trap near the diagonal shortcut.
- Labeled positives: 5 safe-route prefixes, 16 steps each.
- Labeled negatives: 1, 2, or 5 full bad shortcut trajectories.
- Unlabeled pool: 180 mixed trajectories.
- Bad fractions: `0.50`, `0.75`, `0.90`, `0.95`.
- Seeds: `0`, `1`, `2`, `3`, `4`.
- BC steps: 6000; classifier steps: 2500.
- Evaluation: 30 closed-loop rollouts per seed/fraction/method.
- Selection rule: trajectory score-gap demo selection, max fraction `0.10`, min fraction `0.02`.

## Main Success Results

| n_neg | bad frac | BC-all | pos+unlabeled BC | local weighted BC | TRIAGE gap-demo BC | TRIAGE gap-posterior BC | oracle good BC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.50 | 0.460 | 0.453 | 0.187 | 1.000 | 1.000 | 1.000 |
| 1 | 0.75 | 0.360 | 0.333 | 0.180 | 1.000 | 1.000 | 1.000 |
| 1 | 0.90 | 0.240 | 0.140 | 0.000 | 1.000 | 1.000 | 1.000 |
| 1 | 0.95 | 0.153 | 0.080 | 0.320 | 1.000 | 1.000 | 0.800 |
| 2 | 0.50 | 0.487 | 0.440 | 0.200 | 1.000 | 1.000 | 1.000 |
| 2 | 0.75 | 0.353 | 0.287 | 0.147 | 1.000 | 1.000 | 1.000 |
| 2 | 0.90 | 0.220 | 0.220 | 0.000 | 0.973 | 1.000 | 1.000 |
| 2 | 0.95 | 0.147 | 0.113 | 0.000 | 0.993 | 0.600 | 1.000 |
| 5 | 0.50 | 0.400 | 0.467 | 0.200 | 1.000 | 1.000 | 1.000 |
| 5 | 0.75 | 0.340 | 0.293 | 0.200 | 1.000 | 1.000 | 1.000 |
| 5 | 0.90 | 0.240 | 0.147 | 0.000 | 1.000 | 1.000 | 1.000 |
| 5 | 0.95 | 0.100 | 0.113 | 0.140 | 1.000 | 0.573 | 1.000 |

## Gap Selection Diagnostics

| n_neg | bad frac | selected frac | selected demo purity | selected transition purity | hidden-good demos | hidden-bad demos |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.50 | 0.031 | 1.000 | 1.000 | 5.6 | 0.0 |
| 1 | 0.75 | 0.049 | 1.000 | 1.000 | 8.8 | 0.0 |
| 1 | 0.90 | 0.080 | 1.000 | 1.000 | 14.4 | 0.0 |
| 1 | 0.95 | 0.057 | 1.000 | 1.000 | 10.2 | 0.0 |
| 2 | 0.50 | 0.039 | 1.000 | 1.000 | 7.0 | 0.0 |
| 2 | 0.75 | 0.037 | 1.000 | 1.000 | 6.6 | 0.0 |
| 2 | 0.90 | 0.089 | 1.000 | 1.000 | 16.0 | 0.0 |
| 2 | 0.95 | 0.057 | 1.000 | 1.000 | 10.2 | 0.0 |
| 5 | 0.50 | 0.034 | 1.000 | 1.000 | 6.2 | 0.0 |
| 5 | 0.75 | 0.062 | 1.000 | 1.000 | 11.2 | 0.0 |
| 5 | 0.90 | 0.089 | 1.000 | 1.000 | 16.0 | 0.0 |
| 5 | 0.95 | 0.057 | 1.000 | 1.000 | 10.2 | 0.0 |

## Interpretation

- The controlled mechanism is not fragile to the number of bad labels in this range. With 5 positive prefixes, even 1 labeled bad shortcut trajectory is enough for score-gap demo BC to reach `1.000` success at all four contamination levels.
- The support-side result is very clean: gap selection chooses pure hidden-good unlabeled support in all 12 rows and admits 0 hidden-bad demos on average.
- The policy-side result still exposes converter variance. With 2 bad labels, hard gap-demo BC dips slightly at 90% and 95% bad contamination (`0.973` and `0.993`), while gap-posterior BC fails on one 95% seed and averages `0.600`. With 5 bad labels, gap-demo BC is again `1.000` at every contamination level, while gap-posterior remains brittle at 95%.
- Mixed-log and local weighted baselines remain weak at high contamination: across the three bad-label counts, BC-all is at most `0.240` at 90% and `0.153` at 95%, and local weighted BC is at most `0.320` at 95%.
- This ablation supports a label-efficiency claim for explicit bad labels in the controlled benchmark, but it does not test the zero-negative case because the tri-signal classifier requires at least one negative demonstration.

## Artifacts

- `n_neg=1` full report: `results/continuous_pointnav_bad_label_count_npos5_nneg1_5seed/REPORT.md`
- `n_neg=2` full report: `results/continuous_pointnav_bad_label_count_npos5_nneg2_5seed/REPORT.md`
- `n_neg=5` full report: `results/continuous_pointnav_gap_select_label_budget5_5seed/REPORT.md`
