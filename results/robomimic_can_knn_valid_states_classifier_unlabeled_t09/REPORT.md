# Robomimic Can KNN Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Source: `positive_plus_classifier_unlabeled`.
Source demos: `10`.
Source transitions: `7652`.
Selected unlabeled transitions: `6454`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `5`.
Evaluation horizon: `400`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| knn_positive_k1_positive_plus_classifier_unlabeled | 0.000 | 0.000 | 400.0 |
| knn_positive_k3_positive_plus_classifier_unlabeled | 0.200 | 0.200 | 341.0 |
| knn_positive_k5_positive_plus_classifier_unlabeled | 0.200 | 0.200 | 342.0 |

## Classifier

- Labeled accuracy: `0.981`.
- Positive/negative logit mean: `12.396` / `-15.081`.
- Unlabeled probability mean: `0.526`.
- Selected unlabeled transitions: `6454`.

## Interpretation

- This is a nonparametric sanity check for low-dimensional state support.
- If KNN succeeds while the MLP BC fails, the immediate issue is the actor parameterization.
- If KNN also fails, Robomimic Can likely needs a sequence-aware or official Robomimic imitation backbone before testing Tri-PIQL.
