# Can 40p/80b Score-Support Tradeoff

This analysis aggregates the frozen Can Paired 40 hidden-positive / 80 hidden-bad split seeds 11, 22, and 33.
It reuses existing score diagnostics and endpoint evaluations; no new policy training is included.

## Aggregate Support Sweep

| support_rule | mean_selected | purity | hidden_positive_recall | hidden_bad_admission | endpoint_success |
| --- | --- | --- | --- | --- | --- |
| classifier_top10 | 10.000 | 0.867 | 0.217 | 0.017 |  |
| classifier_top20 | 20.000 | 0.850 | 0.425 | 0.037 |  |
| classifier_top40 | 40.000 | 0.708 | 0.708 | 0.146 |  |
| classifier_top60 | 60.000 | 0.600 | 0.900 | 0.300 |  |
| classifier_top80 | 80.000 | 0.483 | 0.967 | 0.517 |  |
| triage_adaptive_masscap | 63.333 | 0.579 | 0.917 | 0.333 | 0.660 |
| weighted_full_pool | 120.000 | 0.333 | 1.000 | 1.000 | 0.600 |
| positive_only_nn_top40 | 40.000 | 0.883 | 0.883 | 0.058 | 0.720 |

## Interpretation

- Classifier-score top-k support traces the precision/coverage curve: small top-k rules are purer but under-cover hidden positives, while broader top-k rules recover more positives and admit more hidden bad demos.
- TRIAGE-BC adaptive masscap recovers `110/120` hidden-positive demos across the three splits, but it also admits `80/240` hidden-bad demos. Its endpoint success is `99/150`.
- Positive-only NN top40 recovers slightly fewer hidden positives (`106/120`) but admits far fewer hidden-bad demos (`14/240`), and it has the best non-oracle endpoint success on this matrix (`108/150`).
- Weighted BC has full hidden-positive recall but also full hidden-bad admission, reaching `90/150` endpoint successes.
- This supports the paper's precision/coverage framing but not a bad-label benefit claim on Can 40p/80b: the bad-aware converter improves over weighted and all-demo cloning, yet the no-bad positive-only support point sits on a better precision/coverage frontier.

## Artifacts

- Aggregate CSV: `results/final_paper/ablations/can40_score_support_tradeoff.csv`
- Per-split CSV: `results/final_paper/ablations/can40_score_support_tradeoff_per_split.csv`
- Source endpoint table: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`
- Source score diagnostics: `results/final_paper/score_diagnostics/can_paired_pos40_bad80_split{11,22,33}_policy0/`
