# v0.2 Router-Regret Table

This table is the current A2 portfolio-regret artifact. It compares fixed branches, the frozen v0.2 router, and an audit-only oracle selector over the endpoint rows that are currently completed.

Important scope notes:

- `N/A` means that branch was not part of that completed endpoint probe; it is excluded from counted combined success and regret.
- `N/A not run` means the branch is conceptually relevant but missing from the current completed matrix; A3 should fill these cells if the paper needs a complete leaderboard.
- Can MG is a stress/abstention diagnostic with rate-only reused branch summaries, so it is shown but excluded from counted endpoint totals.
- Regret is measured against the best completed branch per split or aggregate probe; the oracle row is audit-only and can use endpoint outcomes.

## Summary

| row_label | can40_fresh | lift_mg_fresh | hard_negative_can | coverage_shift_can | prefix_positive_can | can_mg_stress | counted_success | counted_regret_to_oracle | abstentions | missing_or_na_cells | partial_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Always positive-only NN | 174/250; regret 35 | 125/250; regret 29 | 91/150; regret 13 | 103/150; regret 17 | 6/150; regret 113 | N/A not run | 499/950 | 207 | 0 | 1 | 0 |
| Always weighted BC | 158/250; regret 51 | 143/250; regret 11 | N/A | N/A | N/A | 0.333 | 301/500 | 62 | 0 | 3 | 0 |
| Always hard support | 197/250; regret 12 | 143/250; regret 11 | 104/150 | 120/150 | 119/150 | 0.167; regret 0.166 | 683/950 | 23 | 0 | 0 | 0 |
| v0.1 TRIAGE-BC | 171/250; regret 38 | 143/250; regret 11 | N/A | N/A | N/A | N/A not run | 314/500 | 49 | 0 | 4 | 0 |
| v0.2 router | 197/250; regret 12 | 143/250; regret 11 | N/A | N/A | N/A | abstain | 340/500 | 23 | 1 | 3 | 0 |
| Oracle branch selector | 209/250 | 154/250 | 104/150 | 120/150 | 119/150 | 0.333 | 706/950 | 0 | 0 | 0 | 0 |

## Per-Regime Detail

| regime_label | row_label | status | successes | episodes | success_rate | oracle_successes | oracle_episodes | regret_successes | source_method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | Always positive-only NN | complete | 174 | 250 | 0.696 | 209 | 250 | 35 | positive_only_nn |
| Can 40p/80b | Always weighted BC | complete | 158 | 250 | 0.632 | 209 | 250 | 51 | weighted_bc |
| Can 40p/80b | Always hard support | complete | 197 | 250 | 0.788 | 209 | 250 | 12 | positive_nn_risk_union_top40 |
| Can 40p/80b | v0.1 TRIAGE-BC | complete | 171 | 250 | 0.684 | 209 | 250 | 38 | triage_bc |
| Can 40p/80b | v0.2 router | complete | 197 | 250 | 0.788 | 209 | 250 | 12 | hard_risk_union |
| Can 40p/80b | Oracle branch selector | oracle | 209 | 250 | 0.836 | 209 | 250 | 0 | per_split_best_completed_branch |
| Lift MG | Always positive-only NN | complete | 125 | 250 | 0.500 | 154 | 250 | 29 | positive_only_nn |
| Lift MG | Always weighted BC | complete | 143 | 250 | 0.572 | 154 | 250 | 11 | weighted_bc |
| Lift MG | Always hard support | complete | 143 | 250 | 0.572 | 154 | 250 | 11 | triage_bc |
| Lift MG | v0.1 TRIAGE-BC | complete | 143 | 250 | 0.572 | 154 | 250 | 11 | triage_bc |
| Lift MG | v0.2 router | complete | 143 | 250 | 0.572 | 154 | 250 | 11 | soft_weighted |
| Lift MG | Oracle branch selector | oracle | 154 | 250 | 0.616 | 154 | 250 | 0 | per_split_best_completed_branch |
| Hard-negative Can | Always positive-only NN | complete | 91 | 150 | 0.607 | 104 | 150 | 13 | state_action_positive_nn_top40 |
| Hard-negative Can | Always weighted BC | not_applicable |  |  |  | 104 | 150 |  |  |
| Hard-negative Can | Always hard support | complete | 104 | 150 | 0.693 | 104 | 150 | 0 | hybrid_rank_fusion_badaware_heavy_top40 |
| Hard-negative Can | v0.1 TRIAGE-BC | not_applicable |  |  |  | 104 | 150 |  |  |
| Hard-negative Can | v0.2 router | not_applicable |  |  |  | 104 | 150 |  |  |
| Hard-negative Can | Oracle branch selector | oracle | 104 | 150 | 0.693 | 104 | 150 | 0 | per_split_best_completed_probe_branch |
| Coverage-shift Can | Always positive-only NN | complete | 103 | 150 | 0.687 | 120 | 150 | 17 | state_action_positive_nn_top40 |
| Coverage-shift Can | Always weighted BC | not_applicable |  |  |  | 120 | 150 |  |  |
| Coverage-shift Can | Always hard support | complete | 120 | 150 | 0.800 | 120 | 150 | 0 | hybrid_rank_fusion_badaware_heavy_top40 |
| Coverage-shift Can | v0.1 TRIAGE-BC | not_applicable |  |  |  | 120 | 150 |  |  |
| Coverage-shift Can | v0.2 router | not_applicable |  |  |  | 120 | 150 |  |  |
| Coverage-shift Can | Oracle branch selector | oracle | 120 | 150 | 0.800 | 120 | 150 | 0 | per_split_best_completed_probe_branch |
| Prefix-positive Can | Always positive-only NN | complete | 6 | 150 | 0.040 | 119 | 150 | 113 | prefix_state_action_nn_top80 |
| Prefix-positive Can | Always weighted BC | not_applicable |  |  |  | 119 | 150 |  |  |
| Prefix-positive Can | Always hard support | complete | 119 | 150 | 0.793 | 119 | 150 | 0 | prefix_bad_aware_state_top80 |
| Prefix-positive Can | v0.1 TRIAGE-BC | not_applicable |  |  |  | 119 | 150 |  |  |
| Prefix-positive Can | v0.2 router | not_applicable |  |  |  | 119 | 150 |  |  |
| Prefix-positive Can | Oracle branch selector | oracle | 119 | 150 | 0.793 | 119 | 150 | 0 | best_completed_probe_branch |
| Can MG abstention/stress | Always positive-only NN | not_run |  |  |  |  |  |  |  |
| Can MG abstention/stress | Always weighted BC | rate_only |  |  | 0.333 |  |  |  | weighted |
| Can MG abstention/stress | Always hard support | rate_only |  |  | 0.167 |  |  |  | posp10 |
| Can MG abstention/stress | v0.1 TRIAGE-BC | not_run |  |  |  |  |  |  |  |
| Can MG abstention/stress | v0.2 router | abstained |  |  |  |  |  |  | stress_abstain |
| Can MG abstention/stress | Oracle branch selector | oracle_rate_only |  |  | 0.333 |  |  |  | weighted |

## Interpretation

- On completed Can+Lift rows, current regret to the completed oracle selector is `23/500` for v0.2, versus `64/500` for always positive-only and `62/500` for always weighted BC.
- A3 has completed the fresh Lift v0.1 hard-support audit and the fresh Can v0.1 audit: completed v0.1 Can/Lift cells currently total `314/500` with regret `49/500` to the same completed-split oracle. Fresh Can v0.1 now covers all current split seeds.
- The generated Can probes show the complementary regime: bad-aware hard support has zero regret on hard-negative, coverage-shift, and prefix-positive probes, while matched positive-only retrieval has large regret.
- Can MG remains an abstention/stress case; forcing a branch is not yet justified by the current hidden-label-free proxies.
- This is not yet a fully complete fixed-branch matrix; remaining missing or not-applicable cells are tracked in the per-regime CSV notes.
