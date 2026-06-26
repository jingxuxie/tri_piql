# v0.2 Fresh Gate Uncertainty Audit

This report adds descriptive uncertainty checks to the frozen `METHOD_FREEZE_V02.md` fresh Can+Lift gate.
Rows compare the router-selected branch against the best completed non-oracle baseline within each split.
Wilson intervals describe pooled endpoint rates; paired bootstrap intervals average repeated rollouts by `initial_demo_id`, then resample split units and paired validation initial states.
The intervals are wording guardrails rather than formal independent tests because there are only 5 split seeds per setting.

## Aggregate And Paired-Bootstrap Read

| scope | selected_success | selected_episodes | selected_rate | best_baseline_success | best_baseline_episodes | best_baseline_rate | pooled_delta | paired_bootstrap95_low | paired_bootstrap95_high | split_signs | split_sign_p_two_sided |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 197 | 250 | 0.788 | 192 | 250 | 0.768 | 0.020 | -0.144 | 0.168 | +++-+ | 0.375 |
| Lift MG | 143 | 250 | 0.572 | 146 | 250 | 0.584 | -0.012 | -0.083 | 0.140 | +---+ | 1.000 |
| Combined Can+Lift | 340 | 500 | 0.680 | 338 | 500 | 0.676 | 0.004 | -0.074 | 0.120 | +++-++---+ | 0.754 |

## Split Margins

| setting_label | split_seed | selected_method | selected_success | best_baseline_method | best_baseline_success | margin |
| --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 101 | positive_nn_risk_union_top40 | 45 | weighted_bc | 37 | +0.160 |
| Can 40p/80b | 202 | positive_nn_risk_union_top40 | 45 | positive_only_nn | 40 | +0.100 |
| Can 40p/80b | 303 | positive_nn_risk_union_top40 | 39 | positive_only_nn | 36 | +0.060 |
| Can 40p/80b | 404 | positive_nn_risk_union_top40 | 27 | positive_only_nn | 39 | -0.240 |
| Can 40p/80b | 505 | positive_nn_risk_union_top40 | 41 | positive_only_nn | 40 | +0.020 |
| Lift MG | 101 | weighted_bc | 31 | triage_bc | 36 | -0.100 |
| Lift MG | 202 | weighted_bc | 30 | triage_bc | 34 | -0.080 |
| Lift MG | 303 | weighted_bc | 19 | positive_only_nn | 21 | -0.040 |
| Lift MG | 404 | weighted_bc | 30 | triage_bc | 29 | +0.020 |
| Lift MG | 505 | weighted_bc | 33 | positive_only_nn | 26 | +0.140 |

## Interpretation

- Can 40p/80b remains a hard-union result: the selected branch wins 4/5 fresh splits and loses 1.
- Lift MG remains a weighted-coverage result: the selected weighted branch wins 2/5 fresh splits and loses 3.
- The combined Can+Lift gate is positive (+0.004) over 10 split-task units, but the paired-bootstrap interval crosses zero; frame it as branch-selection evidence rather than formal significance.
