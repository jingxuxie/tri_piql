# v0.2 Fresh Router Support Audit

This is a support/router preflight for `METHOD_FREEZE_V02.md`.
It uses fresh split and score artifacts only; hidden labels are audit-only.

## Router Decisions

| setting_label | split_seed | router_branch | estimated_positive_mass | count_ge_pos_min | labeled_positive_p10 |
| --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 101 | hard_risk_union | 45.75688739788796 | 15 | 0.8218098402023315 |
| Can 40p/80b | 202 | hard_risk_union | 43.97297203415074 | 7 | 0.806035166978836 |
| Can 40p/80b | 303 | hard_risk_union | 56.15297262124109 | 15 | 0.8702575743198395 |
| Lift MG | 101 | soft_weighted | 619.8186168656348 | 291 | 0.916141825914383 |
| Lift MG | 202 | soft_weighted | 500.230385815632 | 221 | 0.8838746786117554 |
| Lift MG | 303 | soft_weighted | 806.6638563364934 | 375 | 0.9862213671207428 |

## Support Summary

| setting_label | candidate_id | split_count | selected_unlabeled | hidden_positive_selected | hidden_bad_selected | support_purity | hidden_positive_recall | hidden_bad_admission | audit_oracle_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_risk_fusion_top40 | 3 | 120 | 117 | 3 | 0.975 | 0.975 | 0.013 | 0.963 |
| Can 40p/80b | positive_nn_risk_union_top40 | 3 | 138 | 119 | 19 | 0.862 | 0.992 | 0.079 | 0.913 |
| Can 40p/80b | positive_nn_top40 | 3 | 120 | 101 | 19 | 0.842 | 0.842 | 0.079 | 0.762 |
| Lift MG | weighted_bc | 3 | 4260 | 828 | 3432 | 0.194 | 1.000 | 1.000 | 0.000 |

## Read

- If Can fresh splits choose `hard_risk_union`, the corresponding union rows are ready for endpoint setup.
- If Lift fresh splits choose `soft_weighted`, the existing weighted trainer is the v0.2 selected branch for that split.
- This report is not endpoint evidence; it is the cheap preflight before 200-epoch GPU jobs.
