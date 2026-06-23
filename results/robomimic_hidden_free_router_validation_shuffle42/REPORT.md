# Robomimic Hidden-Free Hard/Soft Router

This report turns the hard-vs-soft diagnostic into a candidate hidden-label-free router over existing Robomimic score analyses.

The router uses only labeled positive/negative score calibration and the unlabeled score distribution. Hidden labels appear only in audit columns, not in the decision.

## Rule

- Count unlabeled demos with classifier score at least `0.95`.
- If that saturated plateau is at least `max(400, 40 x labeled_positive_count)`, use soft classifier-probability weighted sampling.
- Otherwise, if labeled-positive score p10 is at least `0.85` and the saturated plateau is at least `4 x labeled_positive_count`, use the calibrated `pos_min` hard threshold.
- Otherwise, use the calibrated adaptive-masscap hard-support selector.

## Decisions

| analysis | branch | training rule | saturated demos | score p10+ | policy 20k | reason |
|---|---|---|---:|---:|---:|---|
| can_paired_80p80b | hard_adaptive_masscap | adaptive_masscap | 0.0 | 0.748 | 0.900 | no large saturated plateau; use calibrated hard support with mass cap |
| can_paired_40p80b | hard_adaptive_masscap | adaptive_masscap | 0.0 | 0.748 | 0.733 | no large saturated plateau; use calibrated hard support with mass cap |
| can_paired_20p80b | hard_adaptive_masscap | adaptive_masscap | 0.0 | 0.749 | 0.667 | no large saturated plateau; use calibrated hard support with mass cap |
| lift_mg_sparse | hard_pos_min_threshold | pos_min_calibrated_threshold | 85.3 | 0.887 | 0.667 | labeled positives are high-scoring and the plateau is modest; use calibrated hard thresholding |
| can_mg_sparse | soft_weighted | classifier_probability_weighted_sampler | 652.3 | 0.943 | 0.333 | large saturated unlabeled score plateau; preserve coverage with soft weights |
| can_paired_40p80b_shuffle42 | hard_adaptive_masscap | adaptive_masscap | 3.0 | 0.853 | 0.633 | no large saturated plateau; use calibrated hard support with mass cap |
| lift_mg_sparse_shuffle42 | hard_pos_min_threshold | pos_min_calibrated_threshold | 159.3 | 0.922 | 0.600 | labeled positives are high-scoring and the plateau is modest; use calibrated hard thresholding |
| can_mg_sparse_shuffle42 | hard_pos_min_threshold | pos_min_calibrated_threshold | 312.7 | 0.957 | 0.100 | labeled positives are high-scoring and the plateau is modest; use calibrated hard thresholding |

## Interpretation

- The router selects hard support for paired Can and Lift, and soft weighting for the original Can MG split.
- On shuffled Can and Lift validation splits, the hard branches transfer but with lower fixed-20k endpoints than the original splits.
- On shuffled Can MG, the current absolute plateau rule flips the branch from soft weighted to hard `pos_min`; a seed-0 hard/soft comparison is weak for both branches (`0.100` fixed-20k for each, best `0.200` hard versus `0.100` soft).
- This means the hidden-free router is useful as a first candidate but too brittle to promote as the central method without a more robust score-shape or validation proxy.
- A follow-up feature audit in `results/robomimic_router_feature_diagnostics/REPORT.md` finds that a mass-only alternative would mark both Can MG splits as soft-like, but still would not solve the weak shuffled policy result.
- Router v2 in `results/robomimic_router_v2_abstention_summary/REPORT.md` takes the safer next step: assign paired Can and Lift hard-support branches, and abstain on both original and shuffled Can MG.
