# Active Abstention Evaluation

This report stages the C2 abstention check from existing router-v2 and Can MG branch-proxy artifacts.
It does not add new policy training. The claim is risk control under ambiguous score shapes, not endpoint dominance.

## Abstained Can MG Rows

| setting_label | router_decision | estimated_positive_mass | count_ge_pos_min | best_forced_branch | best_forced_success_20k | worst_forced_branch | worst_forced_success_20k | proxy_matches_best_success | abstention_justified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can MG original | stress_abstain | 1947.9 | 1025.7 | weighted | 0.333 | alltrain | 0.100 | 0/6 | yes_proxy_miss_and_low_ceiling |
| Can MG shuffle42 | stress_abstain | 1466.3 | 515.7 | hard_posmin=soft_weighted | 0.100 | hard_posmin=soft_weighted | 0.100 | 6/6 | yes_all_forced_branches_weak |

## Assignment Summary

| assignment_status | num_rows | mean_policy_20k | min_policy_20k | max_policy_20k | mean_estimated_positive_mass | mean_count_ge_pos_min |
| --- | --- | --- | --- | --- | --- | --- |
| assigned | 6 | 0.700 | 0.600 | 0.900 | 172.450 | 85.067 |
| abstained | 2 | 0.217 | 0.100 | 0.333 | 1707.100 | 770.700 |

## Interpretation

- Router v2 abstains on the two large-MG score shapes: original Can MG has estimated positive mass `1947.9` and `1025.7` trajectories above the labeled-positive minimum; shuffled Can MG has mass `1466.3` and count `515.7`.
- On original Can MG, forcing a branch leaves only a modest best fixed-20k result: weighted BC is best at `0.333`, all-demo is worst at `0.100`, and likelihood-style proxies match the best-success branch in `0/6` cases.
- On shuffled Can MG, proxy winners can match best success in `6/6` cases only because the staged hard and soft forced branches both reach `0.100`; this does not validate a useful branch.
- Across the router-v2 audit, assigned rows have mean fixed-20k success `0.700` and minimum `0.600`; abstained rows have mean `0.217` and maximum `0.333`.

Conclusion: abstention is justified as a stress/limitation decision for large ambiguous score plateaus until a coverage-sensitive policy-quality proxy is validated.

## Source Artifacts

- `results/robomimic_router_v2_abstention_summary/router_v2_summary.csv`
- `results/final_paper/ablations/can_mg_branch_proxy_summary/method_proxy_scores.csv`
- `results/final_paper/ablations/can_mg_branch_proxy_summary/proxy_winners.csv`
