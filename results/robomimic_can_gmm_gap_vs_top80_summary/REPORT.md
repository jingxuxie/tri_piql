# Robomimic GMM Run Summary

Run directories: `9`.

## Aggregate

| source | method | selector | max steps | ckpt | train transitions | selected demos | eval eps | runs | seeds | success mean | success values | hidden-positive demos |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| labeled_positive | gmm_mode_labeled_positive |  | 50000 | 20000 | 1198 | 0.0 | 10 | 3 | 0,1,2 | 0.067 | 0.000,0.100,0.100 | 0.0 |
| labeled_positive | gmm_mode_labeled_positive |  | 50000 | 50000 | 1198 | 0.0 | 10 | 2 | 1,2 | 0.150 | 0.200,0.100 | 0.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap | 20000 | 5000 | 3670 | 25.0 | 10 | 3 | 0,1,2 | 0.333 | 0.400,0.400,0.200 | 25.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap | 20000 | 10000 | 3470 | 23.0 | 10 | 1 | 0 | 0.200 | 0.200 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap | 20000 | 20000 | 3470 | 23.0 | 10 | 1 | 0 | 0.100 | 0.100 | 23.0 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | fixed_top | 50000 | 20000 | 9072 | 80.0 | 10 | 3 | 0,1,2 | 0.300 | 0.400,0.200,0.300 | 61.7 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | fixed_top | 50000 | 50000 | 9095 | 80.0 | 10 | 2 | 1,2 | 0.150 | 0.200,0.100 | 62.5 |

## Interpretation

- This summary aggregates completed smoke runs only; it does not rerun experiments.
- Treat low-episode or single-seed rows as triage evidence rather than final benchmark numbers.
