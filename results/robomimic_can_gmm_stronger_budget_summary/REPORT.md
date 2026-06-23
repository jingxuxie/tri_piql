# Robomimic GMM Run Summary

Run directories: `9`.

## Aggregate

| source | method | max steps | ckpt | train transitions | top demos | eval eps | runs | seeds | success mean | success values | hidden-positive demos |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| labeled_positive | gmm_mean_labeled_positive | 3000 | 3000 | 1198 | 40 | 10 | 1 | 0 | 0.000 | 0.000 | 0.0 |
| labeled_positive | gmm_mean_labeled_positive | 3000 | 3000 | 8809 | 40 | 10 | 1 | 0 | 0.200 | 0.200 | 0.0 |
| labeled_positive | gmm_mode_labeled_positive | 3000 | 3000 | 1198 | 40 | 10 | 1 | 0 | 0.000 | 0.000 | 0.0 |
| labeled_positive | gmm_mode_labeled_positive | 50000 | 20000 | 1198 | 40 | 10 | 3 | 0,1,2 | 0.067 | 0.000,0.100,0.100 | 0.0 |
| labeled_positive | gmm_mode_labeled_positive | 50000 | 50000 | 1198 | 40 | 10 | 2 | 1,2 | 0.150 | 0.200,0.100 | 0.0 |
| labeled_positive | gmm_mode_labeled_positive | 3000 | 3000 | 8809 | 40 | 10 | 1 | 0 | 0.500 | 0.500 | 0.0 |
| labeled_positive | gmm_sample_labeled_positive | 3000 | 3000 | 1198 | 40 | 10 | 1 | 0 | 0.000 | 0.000 | 0.0 |
| labeled_positive | gmm_sample_labeled_positive | 3000 | 3000 | 8809 | 40 | 10 | 1 | 0 | 0.600 | 0.600 | 0.0 |
| positive_plus_classifier_top_unlabeled_demos | gmm_classifier_rerank_positive_plus_classifier_top_unlabeled_demos | 3000 | 3000 | 9027 | 80 | 10 | 1 | 0 | 0.100 | 0.100 | 60.0 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mean_positive_plus_classifier_top_unlabeled_demos | 3000 | 3000 | 9027 | 80 | 10 | 1 | 0 | 0.200 | 0.200 | 60.0 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | 3000 | 3000 | 9027 | 80 | 10 | 1 | 0 | 0.300 | 0.300 | 60.0 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | 50000 | 20000 | 9072 | 80 | 10 | 3 | 0,1,2 | 0.300 | 0.400,0.200,0.300 | 61.7 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | 50000 | 50000 | 9095 | 80 | 10 | 2 | 1,2 | 0.150 | 0.200,0.100 | 62.5 |
| positive_plus_classifier_top_unlabeled_demos | gmm_sample_positive_plus_classifier_top_unlabeled_demos | 3000 | 3000 | 9027 | 80 | 10 | 1 | 0 | 0.100 | 0.100 | 60.0 |

## Interpretation

- This summary aggregates completed smoke runs only; it does not rerun experiments.
- Treat low-episode or single-seed rows as triage evidence rather than final benchmark numbers.
