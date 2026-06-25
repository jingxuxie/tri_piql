# v0.2 Union Candidate Support Audit

Generated from the staged action-risk candidate support audit without policy training.
The union candidate keeps the positive-only NN support and adds demos from the risk-fusion support.
It tests whether the risk branch should complement, not replace, the strong positive-only baseline.

## Can 40p/80b Summary

| candidate_id | selected_unlabeled | hidden_positive_selected | hidden_bad_selected | support_purity | hidden_positive_recall | hidden_bad_admission | audit_oracle_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| positive_nn_top40 | 120 | 106 | 14 | 0.883 | 0.883 | 0.058 | 0.825 |
| positive_nn_risk_fusion_top40 | 120 | 117 | 3 | 0.975 | 0.975 | 0.013 | 0.963 |
| positive_nn_risk_union_top40 | 135 | 119 | 16 | 0.881 | 0.992 | 0.067 | 0.925 |

## Can 40p/80b Union Per Split

| split_seed | selected_unlabeled | hidden_positive_selected | hidden_bad_selected | support_purity | hidden_positive_recall | hidden_bad_admission |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | 45 | 40 | 5 | 0.889 | 1.000 | 0.062 |
| 22 | 43 | 40 | 3 | 0.930 | 1.000 | 0.037 |
| 33 | 47 | 39 | 8 | 0.830 | 0.975 | 0.100 |

## Endpoint Gate Recommendation

- The split-22 union is the cleanest first endpoint gate: it recovers 40/40 hidden positives while keeping 3 hidden bad demos, matching positive-only NN's bad count.
- This is still only a support gate. Endpoint training must decide whether the added hidden-positive coverage helps or whether positive-only's exact distribution remains better.
- If split 22 fails, do not spend a full three-split endpoint budget on this union family without a new reason.

## Outputs

- `results/final_paper/tables/v02_union_candidate_support_per_split.csv`
- `results/final_paper/tables/v02_union_candidate_support_summary.csv`
