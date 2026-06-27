# v0.2 Fresh Router Support Audit

This is a support/router preflight for `METHOD_FREEZE_V02.md`.
It uses fresh split and score artifacts only; hidden labels are audit-only.

## Router Decisions

| setting_label | split_seed | router_branch | estimated_positive_mass | count_ge_pos_min | labeled_positive_p10 |
| --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 606 | hard_risk_union | 56.39483996101834 | 20 | 0.8810502231121063 |
| Can 40p/80b | 707 | hard_risk_union | 46.864140936249164 | 8 | 0.8888590633869171 |

## Support Summary

| setting_label | candidate_id | split_count | selected_unlabeled | hidden_positive_selected | hidden_bad_selected | support_purity | hidden_positive_recall | hidden_bad_admission | audit_oracle_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_risk_fusion_top40 | 2 | 80 | 73 | 7 | 0.912 | 0.912 | 0.044 | 0.869 |
| Can 40p/80b | positive_nn_risk_union_top40 | 2 | 95 | 75 | 20 | 0.789 | 0.938 | 0.125 | 0.812 |
| Can 40p/80b | positive_nn_top40 | 2 | 80 | 63 | 17 | 0.787 | 0.787 | 0.106 | 0.681 |

## Read

- If Can fresh splits choose `hard_risk_union`, the corresponding union rows are ready for endpoint setup.
- If Lift fresh splits choose `soft_weighted`, the existing weighted trainer is the v0.2 selected branch for that split.
- This report is not endpoint evidence; it is the cheap preflight before 200-epoch GPU jobs.
