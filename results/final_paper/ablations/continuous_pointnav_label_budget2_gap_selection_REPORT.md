# Continuous PointNav Label-Budget-2 Gap-Selection Stress Diagnostic

This diagnostic repeats the controlled PointNav mechanism benchmark with only 2 positive route-prefix demonstrations and 2 bad shortcut trajectories. It is a boundary stress test for the label-efficiency claim.

Protocol:

- Task: 2D continuous PointNav with start in the lower-left, goal in the upper-right, and a trap near the diagonal shortcut.
- Labeled positives: 2 safe-route prefixes, 16 steps each.
- Labeled negatives: 2 full bad shortcut trajectories through the trap.
- Unlabeled pool: 180 mixed trajectories.
- Bad fractions: `0.50`, `0.75`, `0.90`, `0.95`.
- Seeds: `0`, `1`, `2`, `3`, `4`.
- BC steps: 6000; classifier steps: 2500.
- Evaluation: 30 closed-loop rollouts per seed/fraction/method.
- Selection rule: trajectory score-gap demo selection, max fraction `0.10`, min fraction `0.02`.

## Main Success Results

| bad frac | BC-all | pos+unlabeled BC | local weighted BC | TRIAGE gap-demo BC | TRIAGE gap-posterior BC | oracle good BC |
|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.460 | 0.440 | 0.147 | 1.000 | 1.000 | 1.000 |
| 0.75 | 0.360 | 0.320 | 0.000 | 1.000 | 1.000 | 1.000 |
| 0.90 | 0.180 | 0.133 | 0.173 | 1.000 | 1.000 | 1.000 |
| 0.95 | 0.140 | 0.120 | 0.000 | 1.000 | 1.000 | 1.000 |

## Gap Selection Diagnostics

| bad frac | selected frac | selected demo purity | selected transition purity | hidden-good demos | hidden-bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.032 | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.75 | 0.032 | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.90 | 0.079 | 1.000 | 1.000 | 14.2 | 0.0 |
| 0.95 | 0.051 | 1.000 | 1.000 | 9.2 | 0.0 |

## Boundary Checks

| bad frac | fixed top 5% demo BC | fixed top 10% demo BC | posterior prior 0.05 | posterior prior 0.10 |
|---:|---:|---:|---:|---:|
| 0.50 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.75 | 1.000 | 1.000 | 0.800 | 1.000 |
| 0.90 | 1.000 | 0.787 | 1.000 | 0.927 |
| 0.95 | 0.867 | 0.613 | 0.633 | 0.607 |

## Interpretation

- The controlled mechanism survives the extreme equal-label budget: with only 2 positives and 2 bad demonstrations, score-gap demo selection and gap-posterior BC match the hidden-good oracle at every tested contamination level.
- The gap selector chooses small, pure hidden-good support on every row; at 95% bad unlabeled data it selects about 5.1% of the pool, averaging 9.2 hidden-good demos and 0 hidden-bad demos.
- Fixed-fraction top-demo selection and fixed-prior posterior weighting become brittle at the 95% boundary. This is the cleanest evidence so far that adaptive score-to-support conversion matters even when the score is good.
- Local state-action weighted BC remains a poor converter in this setting, reaching 0.000 success at 75% and 95% bad contamination.
- This is controlled mechanism evidence, not a robotics policy-benefit claim. It strengthens the synthetic label-efficiency result and the precision/coverage conversion story.

## Artifacts

- Full report: `results/continuous_pointnav_gap_select_label_budget2_5seed/REPORT.md`
- Metrics CSV: `results/continuous_pointnav_gap_select_label_budget2_5seed/metrics.csv`
- Selection diagnostics: `results/continuous_pointnav_gap_select_label_budget2_5seed/gap_selection_summary.json`
