# Robomimic Can 40p/80b Checkpoint Selection Rule Summary

## Notes

- Existing checkpoints only; no new policy training.
- Compares mass-capped hard support against classifier-probability weighted BC on the same three seeds.
- Rules use only support, labeled, or held-out labeled masks, not hidden positive/bad labels.

## Fixed Epochs

| method | epoch | mean_success |
| --- | --- | --- |
| masscap | 50 | 0.167 |
| masscap | 100 | 0.500 |
| masscap | 150 | 0.733 |
| masscap | 200 | 0.733 |
| masscap | oracle_best | 0.767 |
| weighted | 50 | 0.267 |
| weighted | 100 | 0.600 |
| weighted | 150 | 0.700 |
| weighted | 200 | 0.567 |
| weighted | oracle_best | 0.700 |

## Rule Aggregate

| rule | method | mean_selected_success | mean_rollout_best_success |
| --- | --- | --- | --- |
| train_support_ll | masscap | 0.733 | 0.767 |
| train_support_ll | weighted | 0.567 | 0.700 |
| valid_positive_ll | masscap | 0.467 | 0.767 |
| valid_positive_ll | weighted | 0.667 | 0.700 |
| valid_negative_ll | masscap | 0.733 | 0.767 |
| valid_negative_ll | weighted | 0.567 | 0.700 |
| labeled_positive_ll | masscap | 0.733 | 0.767 |
| labeled_positive_ll | weighted | 0.567 | 0.700 |
| labeled_negative_ll | masscap | 0.633 | 0.767 |
| labeled_negative_ll | weighted | 0.567 | 0.700 |
| valid_pos_minus_neg_ll | masscap | 0.167 | 0.767 |
| valid_pos_minus_neg_ll | weighted | 0.267 | 0.700 |
| labeled_pos_minus_neg_ll | masscap | 0.467 | 0.767 |
| labeled_pos_minus_neg_ll | weighted | 0.267 | 0.700 |
| valid_joint_pos_neg_ll | masscap | 0.733 | 0.767 |
| valid_joint_pos_neg_ll | weighted | 0.567 | 0.700 |
| labeled_joint_pos_neg_ll | masscap | 0.767 | 0.767 |
| labeled_joint_pos_neg_ll | weighted | 0.567 | 0.700 |

## Per-Run Selections

| run | rule | selected_epoch | selected_rollout_success | rollout_best_epoch | rollout_best_success |
| --- | --- | --- | --- | --- | --- |
| masscap_seed0 | train_support_ll | 200 | 0.800 | 150 | 0.800 |
| masscap_seed0 | valid_positive_ll | 100 | 0.500 | 150 | 0.800 |
| masscap_seed0 | valid_negative_ll | 200 | 0.800 | 150 | 0.800 |
| masscap_seed0 | labeled_positive_ll | 200 | 0.800 | 150 | 0.800 |
| masscap_seed0 | labeled_negative_ll | 100 | 0.500 | 150 | 0.800 |
| masscap_seed0 | valid_pos_minus_neg_ll | 50 | 0.300 | 150 | 0.800 |
| masscap_seed0 | labeled_pos_minus_neg_ll | 200 | 0.800 | 150 | 0.800 |
| masscap_seed0 | valid_joint_pos_neg_ll | 200 | 0.800 | 150 | 0.800 |
| masscap_seed0 | labeled_joint_pos_neg_ll | 200 | 0.800 | 150 | 0.800 |
| masscap_seed1 | train_support_ll | 200 | 0.600 | 150 | 0.700 |
| masscap_seed1 | valid_positive_ll | 50 | 0.200 | 150 | 0.700 |
| masscap_seed1 | valid_negative_ll | 100 | 0.600 | 150 | 0.700 |
| masscap_seed1 | labeled_positive_ll | 200 | 0.600 | 150 | 0.700 |
| masscap_seed1 | labeled_negative_ll | 100 | 0.600 | 150 | 0.700 |
| masscap_seed1 | valid_pos_minus_neg_ll | 50 | 0.200 | 150 | 0.700 |
| masscap_seed1 | labeled_pos_minus_neg_ll | 200 | 0.600 | 150 | 0.700 |
| masscap_seed1 | valid_joint_pos_neg_ll | 100 | 0.600 | 150 | 0.700 |
| masscap_seed1 | labeled_joint_pos_neg_ll | 150 | 0.700 | 150 | 0.700 |
| masscap_seed2 | train_support_ll | 200 | 0.800 | 200 | 0.800 |
| masscap_seed2 | valid_positive_ll | 150 | 0.700 | 200 | 0.800 |
| masscap_seed2 | valid_negative_ll | 200 | 0.800 | 200 | 0.800 |
| masscap_seed2 | labeled_positive_ll | 200 | 0.800 | 200 | 0.800 |
| masscap_seed2 | labeled_negative_ll | 200 | 0.800 | 200 | 0.800 |
| masscap_seed2 | valid_pos_minus_neg_ll | 50 | 0.000 | 200 | 0.800 |
| masscap_seed2 | labeled_pos_minus_neg_ll | 50 | 0.000 | 200 | 0.800 |
| masscap_seed2 | valid_joint_pos_neg_ll | 200 | 0.800 | 200 | 0.800 |
| masscap_seed2 | labeled_joint_pos_neg_ll | 200 | 0.800 | 200 | 0.800 |
| weighted_seed0 | train_support_ll | 200 | 0.500 | 100 | 0.800 |
| weighted_seed0 | valid_positive_ll | 100 | 0.800 | 100 | 0.800 |
| weighted_seed0 | valid_negative_ll | 200 | 0.500 | 100 | 0.800 |
| weighted_seed0 | labeled_positive_ll | 200 | 0.500 | 100 | 0.800 |
| weighted_seed0 | labeled_negative_ll | 200 | 0.500 | 100 | 0.800 |
| weighted_seed0 | valid_pos_minus_neg_ll | 50 | 0.400 | 100 | 0.800 |
| weighted_seed0 | labeled_pos_minus_neg_ll | 50 | 0.400 | 100 | 0.800 |
| weighted_seed0 | valid_joint_pos_neg_ll | 200 | 0.500 | 100 | 0.800 |
| weighted_seed0 | labeled_joint_pos_neg_ll | 200 | 0.500 | 100 | 0.800 |
| weighted_seed1 | train_support_ll | 200 | 0.600 | 100 | 0.600 |
| weighted_seed1 | valid_positive_ll | 150 | 0.600 | 100 | 0.600 |
| weighted_seed1 | valid_negative_ll | 200 | 0.600 | 100 | 0.600 |
| weighted_seed1 | labeled_positive_ll | 200 | 0.600 | 100 | 0.600 |
| weighted_seed1 | labeled_negative_ll | 200 | 0.600 | 100 | 0.600 |
| weighted_seed1 | valid_pos_minus_neg_ll | 50 | 0.300 | 100 | 0.600 |
| weighted_seed1 | labeled_pos_minus_neg_ll | 50 | 0.300 | 100 | 0.600 |
| weighted_seed1 | valid_joint_pos_neg_ll | 200 | 0.600 | 100 | 0.600 |
| weighted_seed1 | labeled_joint_pos_neg_ll | 200 | 0.600 | 100 | 0.600 |
| weighted_seed2 | train_support_ll | 200 | 0.600 | 150 | 0.700 |
| weighted_seed2 | valid_positive_ll | 200 | 0.600 | 150 | 0.700 |
| weighted_seed2 | valid_negative_ll | 200 | 0.600 | 150 | 0.700 |
| weighted_seed2 | labeled_positive_ll | 200 | 0.600 | 150 | 0.700 |
| weighted_seed2 | labeled_negative_ll | 200 | 0.600 | 150 | 0.700 |
| weighted_seed2 | valid_pos_minus_neg_ll | 50 | 0.100 | 150 | 0.700 |
| weighted_seed2 | labeled_pos_minus_neg_ll | 50 | 0.100 | 150 | 0.700 |
| weighted_seed2 | valid_joint_pos_neg_ll | 200 | 0.600 | 150 | 0.700 |
| weighted_seed2 | labeled_joint_pos_neg_ll | 200 | 0.600 | 150 | 0.700 |

## Files

- `selection_rule_summary.csv`: selected checkpoint per run and rule.
- `selection_rule_aggregate.csv`: mean selected rollout success by method and rule.
- `fixed_epoch_summary.csv`: fixed-epoch and oracle-best rollout means.
