# CAU+v0.2 Fresh606 Endpoint Validation

This is the first fresh endpoint check for the post-hoc CAU+v0.2 portfolio hypothesis.
It uses Can 40p/80b split 606, which was not part of the five-split gate fit.

## Decision

- The post-hoc gate `estimated_positive_mass_gt_47.631032` would select `CAU` on split 606 because estimated positive mass is `56.395` versus threshold `47.631`.
- The selected CAU branch reaches 15/20, below positive-only at 16/20.
- Frozen v0.2 union reaches 14/20; the cleaner risk-fusion diagnostic reaches 15/20.
- Proper expanded-mask CAU, which trains with the full 130-demo transition-weight filter, reaches 12/20.
- Best new branch on this fresh split is `cau_action_conflict` at 15/20, which is -1 versus positive-only.
- This rejects promoting the CAU+v0.2 portfolio as a fresh-validated SOTA method in its current form.

## Endpoint Rows

| method_id | method_role | checkpoint_name | success_count | eval_episodes | endpoint_success | avg_len | train_demo_count | selected_unlabeled | selected_hidden_bad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| positive_only_nn | existing_baseline | model_epoch_200 | 16 | 20 | 0.800 | 163.9 |  |  |  |
| weighted_bc | existing_baseline | model_epoch_200 | 14 | 20 | 0.700 | 197.8 |  |  |  |
| candidate_e_gate | existing_router | router | 16 | 20 | 0.800 | 161.8 |  |  |  |
| cau_action_conflict | posthoc_portfolio_selected_branch | model_epoch_100 | 7 | 20 | 0.350 | 301.6 |  |  |  |
| cau_action_conflict | posthoc_portfolio_selected_branch | model_epoch_200 | 15 | 20 | 0.750 | 176.2 |  |  |  |
| positive_nn_risk_union_top40 | frozen_v02_can_branch | model_epoch_100 | 11 | 20 | 0.550 | 242.8 | 58 | 48 | 10 |
| positive_nn_risk_union_top40 | frozen_v02_can_branch | model_epoch_200 | 14 | 20 | 0.700 | 190.9 | 58 | 48 | 10 |
| positive_nn_risk_fusion_top40 | cleaner_support_diagnostic | model_epoch_100 | 15 | 20 | 0.750 | 185.2 | 50 | 40 | 3 |
| positive_nn_risk_fusion_top40 | cleaner_support_diagnostic | model_epoch_200 | 15 | 20 | 0.750 | 176.8 | 50 | 40 | 3 |
| cau_action_conflict_expanded_mask | expanded_mask_diagnostic | model_epoch_100 | 9 | 20 | 0.450 | 270.0 | 130 |  |  |
| cau_action_conflict_expanded_mask | expanded_mask_diagnostic | model_epoch_200 | 12 | 20 | 0.600 | 223.2 | 130 |  |  |

## Support Read

- Frozen v0.2 union support selected 48 unlabeled demos: 38 hidden positives and 10 hidden bad demos (purity 0.792).
- Risk-fusion support selected 40 unlabeled demos: 37 hidden positives and 3 hidden bad demos (purity 0.925).
- Cleaner support alone did not recover the positive-only anchor on this split.
- Expanding CAU to the full conservative transition-weight mask made the endpoint worse, so the split606 CAU failure is not only a filter/config mismatch.

## References

- Summary CSV: `results/sota_candidate/cau_v02_fresh606_endpoint_validation_summary.csv`.
- CAU eval report: `results/sota_candidate/cau_action_conflict_can606_b005_m05_eval20/REPORT.md`.
- Expanded-mask CAU eval report: `results/sota_candidate/cau_action_conflict_can606_expanded_mask_b005_m05_eval20/REPORT.md`.
- v0.2 union eval report: `results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/eval20/REPORT.md`.
- Risk-fusion eval report: `results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/pnrf40/eval20/REPORT.md`.
- Support preflight: `results/sota_candidate/cau_v02_fresh606707_support_preflight/v02_fresh_router_support_REPORT.md`.
