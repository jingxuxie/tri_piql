# Continuous PointNav Label-Budget-5 Gap-Selection Diagnostic

This diagnostic tests the controlled mechanism benchmark with equal scarce labels: 5 positive route-prefix demonstrations and 5 bad shortcut trajectories. It keeps the same continuous closed-loop PointNav setup used in the main contamination sweep.

Protocol:

- Task: 2D continuous PointNav with start in the lower-left, goal in the upper-right, and a trap near the diagonal shortcut.
- Labeled positives: 5 safe-route prefixes, 16 steps each.
- Labeled negatives: 5 full bad shortcut trajectories through the trap.
- Unlabeled pool: 180 mixed trajectories.
- Bad fractions: `0.50`, `0.75`, `0.90`, `0.95`.
- Seeds: `0`, `1`, `2`, `3`, `4`.
- BC steps: 6000; classifier steps: 2500.
- Evaluation: 30 closed-loop rollouts per seed/fraction/method.
- Selection rule: trajectory score-gap demo selection, max fraction `0.10`, min fraction `0.02`.

## Main Success Results

| bad frac | BC-all | pos+unlabeled BC | local weighted BC | TRIAGE gap-demo BC | oracle good BC |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.400 | 0.467 | 0.200 | 1.000 | 1.000 |
| 0.75 | 0.340 | 0.293 | 0.200 | 1.000 | 1.000 |
| 0.90 | 0.240 | 0.147 | 0.000 | 1.000 | 1.000 |
| 0.95 | 0.100 | 0.113 | 0.140 | 1.000 | 1.000 |

## Gap Selection Diagnostics

| bad frac | selected frac | selected demo purity | selected transition purity | hidden-good demos | hidden-bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.034 | 1.000 | 1.000 | 6.2 | 0.0 |
| 0.75 | 0.062 | 1.000 | 1.000 | 11.2 | 0.0 |
| 0.90 | 0.089 | 1.000 | 1.000 | 16.0 | 0.0 |
| 0.95 | 0.057 | 1.000 | 1.000 | 10.2 | 0.0 |

## Interpretation

- The controlled mechanism result survives a smaller equal label budget: with only 5 positives and 5 bad demonstrations, score-gap demo selection matches the hidden-good oracle at every tested contamination level.
- Positive-prefix BC still fails by construction because labeled positives contain only route prefixes, not the full safe route.
- Local state-action weighting remains unreliable: it does not recover the full safe route even though it uses the explicit positive-vs-negative classifier.
- The useful mechanism is trajectory-level support recovery from mixed logs, not local action reranking or local weighted BC.
- This result strengthens the paper's controlled benchmark table and supports a label-efficiency claim for the mechanism. It does not change the Robomimic conclusion that positive-only retrieval is a hard baseline there.

## Artifacts

- Full report: `results/continuous_pointnav_gap_select_label_budget5_5seed/REPORT.md`
- Metrics CSV: `results/continuous_pointnav_gap_select_label_budget5_5seed/metrics.csv`
- Selection diagnostics: `results/continuous_pointnav_gap_select_label_budget5_5seed/gap_selection_summary.json`
