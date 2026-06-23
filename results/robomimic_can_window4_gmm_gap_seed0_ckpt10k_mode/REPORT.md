# Robomimic Can Window-GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Context length: `4`.
Include time: `False`.
Window feature dimension: `256`.
Source transitions: `3470`.
Selected unlabeled transitions: `2272`.
Selected unlabeled demos: `23`.
Selected hidden-positive demos: `23`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.0378037691116333, 'selected_score_mean': 0.9071355306583903, 'selected_score_min': 0.8311644792556763, 'selected_score_max': 0.9692974090576172, 'selected_demo_count': 23, 'selected_hidden_positive_demos': 23, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Components: `5`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `10`.
Evaluation horizon: `400`.
Evaluated checkpoints: `[2500, 5000, 10000]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| window4_gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step2500 | 0.000 | 0.000 | 400.0 |
| window4_gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step5000 | 0.000 | 0.000 | 400.0 |
| window4_gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step10000 | 0.000 | 0.000 | 400.0 |

## Classifier

- Labeled accuracy: `0.981`.
- Positive/negative logit mean: `12.396` / `-15.081`.
- Unlabeled probability mean: `0.526`.
- Selected unlabeled transitions: `2272`.
- Selected unlabeled probability mean: `0.907`.
- Selected hidden-positive demos: `23` / `23`.

## Interpretation

- This tests whether fixed-length observation/action history improves the local GMM extractor while keeping the same score-gap selected support.
- It is a fast local substitute for a full recurrent Robomimic BC backbone.
