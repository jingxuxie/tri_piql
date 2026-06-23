# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Source transitions: `2412`.
Selected unlabeled transitions: `1214`.
Selected unlabeled demos: `15`.
Selected hidden-positive demos: `5`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.0006987452507019043, 'selected_score_mean': 0.5181714653968811, 'selected_score_min': 0.5164005756378174, 'selected_score_max': 0.5235683917999268, 'selected_demo_count': 15, 'selected_hidden_positive_demos': 5, 'selected_hidden_bad_demos': 10, 'selected_hidden_positive_purity': 0.3333333333333333}`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
Gap max/min demos: `80` / `4`.
Unlabeled threshold: `0.9`.
Components: `2`.
Feature mode: `obs`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `1`.
Evaluation horizon: `20`.
Evaluated checkpoints: `[1]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos | 0.000 | 0.000 | 20.0 |

## Classifier

- Labeled accuracy: `0.469`.
- Positive/negative logit mean: `0.017` / `0.016`.
- Unlabeled probability mean: `0.508`.
- Selected unlabeled transitions: `1214`.
- Selected unlabeled probability mean: `0.518`.
- Selected hidden-positive demos: `5` / `15`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
