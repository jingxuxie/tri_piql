# Robomimic GMM Run Summary

Run directories: `5`.

## Aggregate

| source | method | max steps | ckpt | train transitions | top demos | eval eps | runs | seeds | success mean | success values | hidden-positive demos |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| labeled_positive | gmm_mode_labeled_positive | 20000 | 20000 | 1198 | 40 | 10 | 1 | 0 | 0.000 | 0.000 | 0.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | 20000 | 5000 | 3670 | 40 | 10 | 3 | 0,1,2 | 0.333 | 0.400,0.400,0.200 | 25.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | 20000 | 10000 | 3470 | 40 | 10 | 1 | 0 | 0.200 | 0.200 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | 20000 | 20000 | 3470 | 40 | 10 | 1 | 0 | 0.100 | 0.100 | 23.0 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | 20000 | 20000 | 9027 | 80 | 10 | 1 | 0 | 0.400 | 0.400 | 60.0 |

## Interpretation

- This summary aggregates completed smoke runs only; it does not rerun experiments.
- Treat low-episode or single-seed rows as triage evidence rather than final benchmark numbers.
