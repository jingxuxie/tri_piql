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

## Interpretation

- The router selects hard support for paired Can and Lift, and soft weighting for Can MG.
- This matches the current fixed-20k policy anchors without looking at hidden unlabeled labels.
- The rule is intentionally simple and should be treated as a first method candidate; the next empirical step is to train any missing router-selected policy rows and then increase rollout episodes for the final table.
