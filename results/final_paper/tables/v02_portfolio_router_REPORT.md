# v0.2 Portfolio Router Audit

This is a development audit for a hidden-label-free portfolio router after the Can 40 union endpoint gate.
The rule uses only router features from labeled score calibration and the unlabeled score distribution.
Hidden labels and endpoints are used only for audit.

## Rule

- Abstain if estimated positive mass is at least `800` and the count above the labeled-positive minimum is at least `400`.
- Otherwise choose the soft weighted branch if estimated positive mass is at least `200` and count above the labeled-positive minimum is at least `80`.
- Otherwise choose the hard positive-NN/risk union branch.

## Primary Development Rows

| analysis | portfolio_branch | selected_method | endpoint_success_rate | comparator_method | comparator_success_rate | v01_success_rate | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| can_paired_40p80b | hard_risk_union | positive_nn_risk_union_top40 | 0.773 | positive_only_nn_top40 | 0.720 | 0.660 | post-hoc development branch; loses split 11 to positive-only NN |
| lift_mg_sparse | soft_weighted | weighted_bc | 0.620 | weighted_bc | 0.620 | 0.493 | matches strongest baseline by selecting weighted branch; not a bad-label policy win |

## Summary

| quantity | value | rate |
| --- | --- | --- |
| primary_portfolio_success | 209/300 | 0.697 |
| primary_strongest_baseline_matched_success | 201/300 | 0.670 |
| primary_v01_success | 173/300 | 0.577 |
| primary_all_positive_oracle_success | 252/300 | 0.840 |
| complete_primary_development_endpoint_rows | 2 |  |
| needs_endpoint_rows | 4 |  |
| stress_abstained_rows | 2 |  |

## Broader Decisions

| analysis | estimated_positive_mass | count_ge_pos_min | portfolio_branch | selected_method | endpoint_success_rate | evidence_status | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| can_paired_80p80b | 82.4 | 32.7 | hard_risk_union | hard_risk_union |  | needs_endpoint | support-only union audit: 240/240 hidden positives and 22/240 hidden bad selected |
| can_paired_40p80b | 49.4 | 17.0 | hard_risk_union | positive_nn_risk_union_top40 | 0.773 | complete_primary_development_endpoint | post-hoc development branch; loses split 11 to positive-only NN |
| can_paired_20p80b | 34.1 | 6.7 | hard_risk_union | hard_risk_union |  | needs_endpoint | support-only union audit: 59/60 hidden positives and 12/240 hidden bad selected |
| lift_mg_sparse | 346.9 | 237.3 | soft_weighted | weighted_bc | 0.620 | complete_primary_development_endpoint | matches strongest baseline by selecting weighted branch; not a bad-label policy win |
| can_mg_sparse | 1947.9 | 1025.7 | stress_abstain | abstain |  | stress_abstained | abstains; best observed stress branch is weighted at 0.333 |

## Read

- The portfolio clears a development endpoint screen on the two primary rows: Can 40 uses the union branch and Lift uses weighted BC.
- Pooled primary development success is `209/300` (`0.697`), versus the strongest pre-union per-task baselines at `201/300` (`0.670`) and v0.1 at `173/300` (`0.577`).
- This is still not a publishable v0.2 result: the rule was written after seeing the Can union endpoint, Lift is won by a baseline branch, Can 20/80 union rows lack endpoints, and fresh split validation is missing.
- The next GPU budget should be a frozen fresh-split test of this router, not additional tuning on split seeds 11/22/33.

## Outputs

- `results/final_paper/tables/v02_portfolio_router_decisions.csv`
- `results/final_paper/tables/v02_portfolio_router_summary.csv`
- `results/final_paper/tables/v02_portfolio_router_REPORT.md`
