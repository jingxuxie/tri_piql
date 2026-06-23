# Robomimic Can Window-GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Context length: `4`.
Include time: `False`.
Window feature dimension: `256`.
Source transitions: `1552`.
Selected unlabeled transitions: `354`.
Selected unlabeled demos: `4`.
Selected hidden-positive demos: `4`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 20, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.0005297064781188965, 'selected_score_mean': 0.5104244202375412, 'selected_score_min': 0.5093724131584167, 'selected_score_max': 0.5118085145950317, 'selected_demo_count': 4, 'selected_hidden_positive_demos': 4, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Components: `2`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `1`.
Evaluation horizon: `1`.
Evaluated checkpoints: `[5, 10]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| window4_gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step5 | 0.000 | 0.000 | 1.0 |
| window4_gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step10 | 0.000 | 0.000 | 1.0 |

## Classifier

- Labeled accuracy: `0.609`.
- Positive/negative logit mean: `0.010` / `-0.042`.
- Unlabeled probability mean: `0.497`.
- Selected unlabeled transitions: `354`.
- Selected unlabeled probability mean: `0.510`.
- Selected hidden-positive demos: `4` / `4`.

## Interpretation

- This tests whether fixed-length observation/action history improves the local GMM extractor while keeping the same score-gap selected support.
- It is a fast local substitute for a full recurrent Robomimic BC backbone.
