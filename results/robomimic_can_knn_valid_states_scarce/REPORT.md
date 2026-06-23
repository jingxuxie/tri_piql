# Robomimic Can KNN Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Source: `labeled_positive`.
Source demos: `10`.
Source transitions: `1198`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `5`.
Evaluation horizon: `400`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| knn_positive_k1_labeled_positive | 0.000 | 0.000 | 400.0 |
| knn_positive_k3_labeled_positive | 0.000 | 0.000 | 400.0 |
| knn_positive_k5_labeled_positive | 0.000 | 0.000 | 400.0 |

## Interpretation

- This is a nonparametric sanity check for low-dimensional state support.
- If KNN succeeds while the MLP BC fails, the immediate issue is the actor parameterization.
- If KNN also fails, Robomimic Can likely needs a sequence-aware or official Robomimic imitation backbone before testing Tri-PIQL.
