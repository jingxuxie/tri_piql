# Robomimic Router Feature Diagnostics

This report audits hidden-label-free score-shape features for the hard/soft router.
Hidden labels are used only in audit columns inherited from selector analyses, not in branch decisions.

## Candidate Branch Rules

- `current_abs_plateau`: current router; soft if the unlabeled count with score >= 0.95 reaches `max(400, 40 x labeled positives)`.
- `mass_only`: soft if calibrated estimated positive mass is at least 800 demos.
- `large_posmin`: soft if the count above the labeled-positive minimum score is at least 800 demos.
- `stress_abstain`: abstain from choosing hard or soft when calibrated mass is at least 800 and the pos-min count is at least 400; otherwise choose hard support.

## Score-Shape Features

| analysis | observed mode | policy 20k | mass | >=0.95 | >=pos_min | pos_min purity | current | mass_only | large_posmin | stress_abstain |
|---|---|---:|---:|---:|---:|---:|---|---|---|---|
| can_paired_80p80b | hard | 0.900 | 82.4 | 0.0 | 32.7 | 1.000 | hard_adaptive_masscap | hard_adaptive_masscap | hard_adaptive_masscap | hard_adaptive_masscap |
| can_paired_40p80b | hard | 0.733 | 49.4 | 0.0 | 17.0 | 1.000 | hard_adaptive_masscap | hard_adaptive_masscap | hard_adaptive_masscap | hard_adaptive_masscap |
| can_paired_20p80b | hard | 0.667 | 34.1 | 0.0 | 6.7 | 1.000 | hard_adaptive_masscap | hard_adaptive_masscap | hard_adaptive_masscap | hard_adaptive_masscap |
| lift_mg_sparse | hard | 0.667 | 346.9 | 85.3 | 237.3 | 0.864 | hard_pos_min | hard_pos_min | hard_pos_min | hard_pos_min |
| can_mg_sparse | soft | 0.333 | 1947.9 | 652.3 | 1025.7 | 0.475 | soft_weighted | soft_weighted | soft_weighted | stress_abstain |
| can_paired_40p80b_shuffle42 | hard_validation | 0.633 | 60.2 | 3.0 | 26.0 | 0.881 | hard_adaptive_masscap | hard_pos_min | hard_adaptive_masscap | hard_adaptive_masscap |
| lift_mg_sparse_shuffle42 | hard_validation | 0.600 | 461.7 | 159.3 | 190.7 | 0.928 | hard_pos_min | hard_pos_min | hard_pos_min | hard_pos_min |
| can_mg_sparse_shuffle42 | fragile | 0.100 | 1466.3 | 312.7 | 515.7 | 0.651 | hard_pos_min | soft_weighted | hard_pos_min | stress_abstain |

## Interpretation

- The current absolute-plateau trigger fits the original Can MG row but flips on the shuffled Can MG split.
- A mass-only alternative would mark both Can MG splits as soft-like, but the shuffled seed-0 soft policy is still weak; a large-pos-min alternative keeps the same Can MG branch flip as the current rule.
- The most defensible next method direction is not another fixed threshold; it is an abstention or validation-proxy branch for large bad-dominated MG pools until a stronger policy anchor exists.
- Paired Can and Lift remain the cleaner hard-support evidence. Can MG remains a stress diagnostic for score-to-policy conversion.
