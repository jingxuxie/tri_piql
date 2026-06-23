# Robomimic Can KNN Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json`.
Source: `all_train_positive`.
Source demos: `90`.
Source transitions: `9826`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `5`.
Evaluation horizon: `400`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| knn_positive_k1_all_train_positive | 0.200 | 0.200 | 343.6 |
| knn_positive_k3_all_train_positive | 0.400 | 0.400 | 286.2 |
| knn_positive_k5_all_train_positive | 0.200 | 0.200 | 346.2 |

## Interpretation

- This is a nonparametric sanity check for low-dimensional state support.
- If KNN succeeds while the MLP BC fails, the immediate issue is the actor parameterization.
- If KNN also fails, Robomimic Can likely needs a sequence-aware or official Robomimic imitation backbone before testing Tri-PIQL.
