# Robomimic Can MG Branch-Proxy Summary

This report tests whether hidden-label-free BC likelihood scores can replace router-v2 abstention on Can MG.
It reuses existing final-20k official Robomimic BC-RNN-GMM checkpoints; no new policy training is included.

The tested proxies score each trained policy on labeled and held-out positive/negative masks.
Higher positive log-likelihood, higher positive-minus-negative likelihood gap, or stronger negative rejection are treated as candidate branch-quality signals.

## Method Means

| split | method | num_runs | rollout_success_20k | valid_positive_ll | valid_contrastive_gap | valid_negative_rejection |
| --- | --- | --- | --- | --- | --- | --- |
| can_mg_original | allpositive | 3 | 0.200 | -39995254.667 | 147031693.600 | 187026948.267 |
| can_mg_original | alltrain | 3 | 0.100 | -41332625.533 | 33560461.133 | 74893086.667 |
| can_mg_original | posp10 | 3 | 0.167 | -45557884.178 | 101496491.067 | 147054375.245 |
| can_mg_original | weighted | 3 | 0.333 | -40054130.867 | 39934926.244 | 79989057.111 |
| can_mg_shuffle42 | hard_posmin | 1 | 0.100 | -42532609.667 | 99066174.733 | 141598784.400 |
| can_mg_shuffle42 | soft_weighted | 1 | 0.100 | -38082416.600 | 35150932.600 | 73233349.200 |

## Proxy Winners

| split | proxy | proxy_winner | proxy_winner_rollout_20k | rollout_best_method | rollout_best_20k | proxy_matches_best_success |
| --- | --- | --- | --- | --- | --- | --- |
| can_mg_original | valid_positive_ll | allpositive | 0.200 | weighted | 0.333 | false |
| can_mg_original | labeled_positive_ll | allpositive | 0.200 | weighted | 0.333 | false |
| can_mg_original | valid_contrastive_gap | allpositive | 0.200 | weighted | 0.333 | false |
| can_mg_original | labeled_contrastive_gap | allpositive | 0.200 | weighted | 0.333 | false |
| can_mg_original | valid_negative_rejection | allpositive | 0.200 | weighted | 0.333 | false |
| can_mg_original | labeled_negative_rejection | allpositive | 0.200 | weighted | 0.333 | false |
| can_mg_shuffle42 | valid_positive_ll | soft_weighted | 0.100 | hard_posmin | 0.100 | true |
| can_mg_shuffle42 | labeled_positive_ll | hard_posmin | 0.100 | hard_posmin | 0.100 | true |
| can_mg_shuffle42 | valid_contrastive_gap | hard_posmin | 0.100 | hard_posmin | 0.100 | true |
| can_mg_shuffle42 | labeled_contrastive_gap | hard_posmin | 0.100 | hard_posmin | 0.100 | true |
| can_mg_shuffle42 | valid_negative_rejection | hard_posmin | 0.100 | hard_posmin | 0.100 | true |
| can_mg_shuffle42 | labeled_negative_rejection | hard_posmin | 0.100 | hard_posmin | 0.100 | true |

## Interpretation

- On original Can MG, the rollout-best final-20k method is `weighted`, but the likelihood proxies prefer `allpositive` because it fits positives tightly and rejects negatives strongly.
- Those hard-support policies lose coverage and underperform the broad weighted sampler at fixed 20k, so simple positive/negative likelihood is not a valid replacement for abstention.
- On shuffled Can MG, final-20k hard and soft branches tie at `0.100`; the proxies can select a branch but cannot detect that both branches are weak.
- Router v2 should keep abstaining on Can MG until we have a proxy that predicts rollout-quality coverage, not just positive imitation or negative rejection.
