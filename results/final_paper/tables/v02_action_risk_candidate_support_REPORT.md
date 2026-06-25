# v0.2 Action-Risk Candidate Support Audit

Generated from final-paper split files without policy training.
Unlike the feature screen, this audit directly constructs candidate supports from action-conflict and bad-neighbor risk rankings, then uses hidden labels only for support audit.

## Decision Rows

| setting_label | baseline_id | baseline_recall | baseline_bad_admission | best_id | best_family | best_recall | best_bad_admission | best_risk_id | best_risk_family | best_risk_recall | best_risk_bad_admission | risk_candidates_dominate_baseline | risk_dominating_candidate_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_top40 | 0.883 | 0.058 | bad_neighbor_safe_top40 | risk-only | 1.000 | 0.000 | bad_neighbor_safe_top40 | risk-only | 1.000 | 0.000 | true | 8 |
| Can 20p/80b | positive_nn_top20 | 0.817 | 0.046 | bad_neighbor_safe_top20 | risk-only | 1.000 | 0.000 | bad_neighbor_safe_top20 | risk-only | 1.000 | 0.000 | true | 8 |
| Can 80p/80b | positive_nn_top80 | 0.917 | 0.083 | bad_neighbor_safe_top80 | risk-only | 1.000 | 0.000 | bad_neighbor_safe_top80 | risk-only | 1.000 | 0.000 | true | 8 |
| Lift MG | positive_nn_top160 | 0.413 | 0.040 | classifier_top320 | bad-aware hard | 0.859 | 0.073 | bad_neighbor_safe_top320 | risk-only | 0.855 | 0.073 | true | 8 |

## Primary Candidate Rows

| setting_label | candidate_id | candidate_family | selected_unlabeled | hidden_positive_recall | hidden_bad_admission | support_purity | audit_oracle_score | combined_risk_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_top40 | positive-only | 120 | 0.883 | 0.058 | 0.883 | 0.825 | -0.960 |
| Can 40p/80b | combined_risk_safe_top40 | risk-only | 120 | 0.967 | 0.017 | 0.967 | 0.950 | -1.328 |
| Can 40p/80b | classifier_risk_fusion_top40 | risk-hybrid | 120 | 0.908 | 0.046 | 0.908 | 0.863 | -1.236 |
| Can 40p/80b | positive_nn_risk_fusion_top40 | risk-hybrid | 120 | 0.975 | 0.013 | 0.975 | 0.963 | -1.295 |
| Can 40p/80b | positive_nn_top80_risk_refine_top40 | risk-hybrid | 120 | 0.967 | 0.017 | 0.967 | 0.950 | -1.303 |
| Can 40p/80b | triple_fusion_top40 | risk-hybrid | 120 | 0.975 | 0.013 | 0.975 | 0.963 | -1.299 |
| Lift MG | positive_nn_top160 | positive-only | 480 | 0.413 | 0.040 | 0.713 | 0.373 | -1.222 |
| Lift MG | combined_risk_safe_top160 | risk-only | 480 | 0.459 | 0.029 | 0.792 | 0.430 | -2.708 |
| Lift MG | classifier_risk_fusion_top160 | risk-hybrid | 480 | 0.570 | 0.002 | 0.983 | 0.568 | -2.525 |
| Lift MG | positive_nn_risk_fusion_top160 | risk-hybrid | 480 | 0.521 | 0.014 | 0.898 | 0.506 | -2.079 |
| Lift MG | positive_nn_top320_risk_refine_top160 | risk-hybrid | 480 | 0.484 | 0.023 | 0.835 | 0.461 | -1.850 |
| Lift MG | triple_fusion_top160 | risk-hybrid | 480 | 0.557 | 0.006 | 0.960 | 0.551 | -2.261 |

## Interpretation

- Risk-generated candidates strictly dominate the setting-specific positive-NN baseline in `4/4` settings.
- Use this only as a support gate. A candidate that clears support still needs endpoint training before it becomes a policy claim.
- Endpoint results supersede this support audit: a support-clearing candidate can still fail if it shifts the policy-learning distribution.

## Outputs

- `results/final_paper/tables/v02_action_risk_candidate_support_per_split.csv`
- `results/final_paper/tables/v02_action_risk_candidate_support_summary.csv`
- `results/final_paper/tables/v02_action_risk_candidate_support_decision.csv`
- `results/final_paper/tables/v02_action_risk_candidate_support_REPORT.md`
