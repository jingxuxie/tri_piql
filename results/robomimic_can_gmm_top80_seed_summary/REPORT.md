# Robomimic GMM Run Summary

Run directories: `3`.

## Aggregate

| source | method | top demos | feature | runs | seeds | success mean | success values | hidden-positive demos |
|---|---|---:|---|---:|---|---:|---|---:|
| positive_plus_classifier_top_unlabeled_demos | gmm_classifier_rerank_positive_plus_classifier_top_unlabeled_demos | 80 | obs | 3 | 0,1,2 | 0.000 | 0.000,0.000,0.000 | 62.3 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mean_positive_plus_classifier_top_unlabeled_demos | 80 | obs | 3 | 0,1,2 | 0.067 | 0.200,0.000,0.000 | 62.3 |
| positive_plus_classifier_top_unlabeled_demos | gmm_mode_positive_plus_classifier_top_unlabeled_demos | 80 | obs | 3 | 0,1,2 | 0.133 | 0.000,0.000,0.400 | 62.3 |

## Interpretation

- This summary aggregates completed smoke runs only; it does not rerun experiments.
- Treat five-episode rows as triage evidence rather than final benchmark numbers.
