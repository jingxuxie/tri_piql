# v0.2 Fresh Router Support Audit

This is a support/router preflight for `METHOD_FREEZE_V02.md`.
It uses fresh split and score artifacts only; hidden labels are audit-only.

## Router Decisions

| setting_label | split_seed | router_branch | estimated_positive_mass | count_ge_pos_min | labeled_positive_p10 |
| --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 101 | hard_risk_union | 45.75688739788796 | 15 | 0.8218098402023315 |
| Can 40p/80b | 202 | hard_risk_union | 43.97297203415074 | 7 | 0.806035166978836 |
| Can 40p/80b | 303 | hard_risk_union | 56.15297262124109 | 15 | 0.8702575743198395 |
| Can 40p/80b | 404 | hard_risk_union | 49.505176377282716 | 10 | 0.8407071709632874 |
| Can 40p/80b | 505 | hard_risk_union | 53.523724875504094 | 19 | 0.7958694338798523 |
| Lift MG | 101 | soft_weighted | 619.8186168656348 | 291 | 0.916141825914383 |
| Lift MG | 202 | soft_weighted | 500.230385815632 | 221 | 0.8838746786117554 |
| Lift MG | 303 | soft_weighted | 806.6638563364934 | 375 | 0.9862213671207428 |
| Lift MG | 404 | soft_weighted | 529.563528416488 | 209 | 0.9621277451515198 |
| Lift MG | 505 | soft_weighted | 414.179010498985 | 205 | 0.9110668182373047 |

## Support Summary

| setting_label | candidate_id | split_count | selected_unlabeled | hidden_positive_selected | hidden_bad_selected | support_purity | hidden_positive_recall | hidden_bad_admission | audit_oracle_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_risk_fusion_top40 | 5 | 200 | 196 | 4 | 0.980 | 0.980 | 0.010 | 0.970 |
| Can 40p/80b | positive_nn_risk_union_top40 | 5 | 226 | 198 | 28 | 0.876 | 0.990 | 0.070 | 0.920 |
| Can 40p/80b | positive_nn_top40 | 5 | 200 | 172 | 28 | 0.860 | 0.860 | 0.070 | 0.790 |
| Lift MG | weighted_bc | 5 | 7100 | 1380 | 5720 | 0.194 | 1.000 | 1.000 | 0.000 |

## Read

- If Can fresh splits choose `hard_risk_union`, the corresponding union rows are ready for endpoint setup.
- If Lift fresh splits choose `soft_weighted`, the existing weighted trainer is the v0.2 selected branch for that split.
- This report is not endpoint evidence; it is the cheap preflight before 200-epoch GPU jobs.
