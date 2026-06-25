# Proxy Endpoint Validation

This is Experiment D2 from the high-impact completion plan.
It checks whether the current hidden-label-free coverage proxy predicts endpoint success well enough to justify a v0.2 branch selector.

## Correlation Summary

| analysis_set | num_rows | coverage_proxy_pearson | coverage_proxy_spearman | audit_score_pearson | audit_score_spearman |
| --- | --- | --- | --- | --- | --- |
| all endpoint-evaluated support rows | 13 | -0.043 | 0.160 | 0.454 | 0.414 |
| primary complete rows | 8 | 0.327 | 0.518 | 0.417 | 0.539 |
| Can 40p/80b rows | 4 | -0.887 | -0.800 | 0.947 | 1.000 |
| Lift MG rows | 4 | 0.847 | 0.632 | -0.966 | -1.000 |
| Can 20p/80b rows | 3 | -0.979 | -1.000 | 0.965 | 1.000 |
| Can 80p/80b rows | 2 | 1.000 | 1.000 | 1.000 | 1.000 |

## Winner Check

| setting_label | endpoint_winner | endpoint_winner_success | coverage_proxy_winner | coverage_proxy_winner_success | coverage_proxy_matches_endpoint | audit_score_winner | audit_score_winner_success | audit_score_matches_endpoint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive-NN/risk union top40 | 116/150 | weighted BC full pool | 90/150 | false | positive-NN/risk union top40 | 116/150 | true |
| Lift MG | weighted BC | 93/150 | weighted BC | 93/150 | true | classifier top-k | 68/150 | false |
| Can 20p/80b | positive-only NN top20 | 54/100 | weighted BC full pool | 18/50 | false | positive-only NN top20 | 54/100 | true |
| Can 80p/80b | positive-only NN top80 | 49/50 | positive-only NN top80 | 49/50 | true | positive-only NN top80 | 49/50 | true |

## Interpretation

- Coverage-only proxy matches the endpoint winner in `2/4` evaluated settings and `1/2` primary settings.
- It correctly favors broad weighted support on Lift MG, but it incorrectly favors broad weighted support on the Can 40p/80b and Can 20p/80b contamination settings.
- The audit-only precision-risk score is not deployable and also fails on Lift MG, where high-purity hard support under-covers the policy learner relative to weighted BC.
- This is negative evidence for freezing a v0.2 method around the current coverage-only proxy. A publishable v0.2 needs additional hidden-label-free bad-risk and action-conflict features before spending fresh endpoint GPU budget.

## Outputs

- `results/final_paper/tables/proxy_endpoint_validation.csv`
- `results/final_paper/tables/proxy_endpoint_validation_correlations.csv`
- `results/final_paper/tables/proxy_endpoint_validation_winners.csv`
- `results/final_paper/figures/proxy_endpoint_validation.png`
- `results/final_paper/figures/proxy_endpoint_validation.pdf`

Rows included:

| setting_label | candidate_label | candidate_family | endpoint_status | coverage_proxy_score | audit_oracle_score | endpoint_success_rate |
| --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | TRIAGE-BC adaptive masscap | bad_aware_hard | complete_3split_endpoint | 0.528 | 0.584 | 0.660 |
| Can 40p/80b | positive-only NN top40 | positive_only | complete_3split_endpoint | 0.333 | 0.825 | 0.720 |
| Can 40p/80b | weighted BC full pool | soft_weighted | complete_3split_endpoint | 1.000 | 0.000 | 0.600 |
| Can 40p/80b | positive-NN/risk union top40 | union_hybrid | complete_3split_endpoint | 0.375 | 0.925 | 0.773 |
| Lift MG | TRIAGE-BC | bad_aware_hard | complete_3split_endpoint | 0.104 | 0.502 | 0.493 |
| Lift MG | classifier top-k | bad_aware_hard | complete_3split_endpoint | 0.113 | 0.553 | 0.453 |
| Lift MG | positive-only NN | positive_only | complete_3split_endpoint | 0.113 | 0.373 | 0.547 |
| Lift MG | weighted BC | soft_weighted | complete_3split_endpoint | 1.000 | 0.000 | 0.620 |
| Can 20p/80b | TRIAGE-BC adaptive masscap | bad_aware_hard | partial_endpoint | 0.410 | 0.613 | 0.460 |
| Can 20p/80b | positive-only NN top20 | positive_only | partial_endpoint | 0.200 | 0.771 | 0.540 |
| Can 20p/80b | weighted BC full pool | soft_weighted | partial_endpoint | 1.000 | 0.000 | 0.360 |
| Can 80p/80b | TRIAGE-BC adaptive masscap | bad_aware_hard | partial_endpoint | 0.344 | 0.454 | 0.860 |
| Can 80p/80b | positive-only NN top80 | positive_only | partial_endpoint | 0.500 | 0.834 | 0.980 |
