# v0.2 Fresh Gate Uncertainty Audit

This report adds descriptive uncertainty checks to the frozen `METHOD_FREEZE_V02.md` fresh Can+Lift gate.
Rows compare the router-selected branch against the best completed non-oracle baseline within each split.
Wilson intervals describe pooled endpoint rates; paired bootstrap intervals average repeated rollouts by `initial_demo_id`, then resample split units and paired validation initial states.
The intervals are wording guardrails rather than formal independent tests because there are only three split seeds per setting.

## Aggregate And Paired-Bootstrap Read

| scope | selected_success | selected_episodes | selected_rate | best_baseline_success | best_baseline_episodes | best_baseline_rate | pooled_delta | paired_bootstrap95_low | paired_bootstrap95_high | split_signs | split_sign_p_two_sided |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 129 | 150 | 0.860 | 113 | 150 | 0.753 | 0.107 | -0.033 | 0.260 | +++ | 0.250 |
| Lift MG | 80 | 150 | 0.533 | 74 | 150 | 0.493 | 0.040 | -0.083 | 0.178 | ++- | 1.000 |
| Combined Can+Lift | 209 | 300 | 0.697 | 187 | 300 | 0.623 | 0.073 | -0.022 | 0.179 | +++++- | 0.219 |

## Split Margins

| setting_label | split_seed | selected_method | selected_success | best_baseline_method | best_baseline_success | margin |
| --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 101 | positive_nn_risk_union_top40 | 45 | weighted_bc | 37 | +0.160 |
| Can 40p/80b | 202 | positive_nn_risk_union_top40 | 45 | positive_only_nn | 40 | +0.100 |
| Can 40p/80b | 303 | positive_nn_risk_union_top40 | 39 | positive_only_nn | 36 | +0.060 |
| Lift MG | 101 | weighted_bc | 31 | positive_only_nn | 28 | +0.060 |
| Lift MG | 202 | weighted_bc | 30 | positive_only_nn | 25 | +0.100 |
| Lift MG | 303 | weighted_bc | 19 | positive_only_nn | 21 | -0.040 |

## Interpretation

- Can 40p/80b remains the clean v0.2 result: the selected hard-union branch wins all three fresh splits.
- Lift MG remains modest: the selected weighted branch wins two splits, loses one, and has a paired-bootstrap interval that crosses zero.
- The combined Can+Lift gate is positive, but it should still be framed as branch-selection evidence because the Lift gain is small and uses the weighted branch.
