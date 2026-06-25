# Can 20p/80b Three-Split Support Audit

This diagnostic extends the frozen Can Paired 20 hidden-positive / 80 hidden-bad split-11 endpoint row with split-seed 22 and 33 support/setup audits.
It also includes a bounded split-22 endpoint comparison for TRIAGE-BC and positive-only NN top20.

## Aggregate Support

| support_rule | mean_selected_unlabeled | purity | hidden_positive_recall | hidden_bad_admission | endpoint_success |
| --- | --- | --- | --- | --- | --- |
| classifier_top20 | 20.000 | 0.683 | 0.683 | 0.079 |  |
| triage_adaptive_masscap | 41.000 | 0.439 | 0.900 | 0.287 | 0.460 |
| positive_only_nn_top20 | 20.000 | 0.817 | 0.817 | 0.046 | 0.540 |
| weighted_full_pool | 100.000 | 0.200 | 1.000 | 1.000 | 0.360 |

## TRIAGE Versus Positive-Only By Split

| split_seed | support_rule | selected_unlabeled | hidden_positive | hidden_bad | purity | hidden_positive_recall | endpoint_success |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | triage_adaptive_masscap | 50 | 20 | 30 | 0.400 | 1.000 | 0.660 |
| 11 | positive_only_nn_top20 | 20 | 17 | 3 | 0.850 | 0.850 | 0.680 |
| 22 | triage_adaptive_masscap | 53 | 18 | 35 | 0.340 | 0.900 | 0.260 |
| 22 | positive_only_nn_top20 | 20 | 17 | 3 | 0.850 | 0.850 | 0.400 |
| 33 | triage_adaptive_masscap | 20 | 16 | 4 | 0.800 | 0.800 |  |
| 33 | positive_only_nn_top20 | 20 | 15 | 5 | 0.750 | 0.750 |  |

## Interpretation

- TRIAGE-BC / adaptive masscap recovers more hidden positives than positive-only NN top20 across the three splits (`54/60` versus `49/60`), but admits far more hidden-bad demos (`69/240` versus `11/240`).
- The split behavior is unstable: TRIAGE uses broad contaminated support on splits 11 and 22, then falls back to a cleaner top20-style support on split 33.
- Positive-only NN top20 is cleaner on aggregate and on splits 11/22; split 33 is the case where TRIAGE also becomes clean, but with lower hidden-positive coverage.
- Positive-only NN top20 beats TRIAGE-BC on both completed endpoint splits: `54/100` pooled versus `46/100` pooled.
- Weighted BC has full hidden-positive recall but also full hidden-bad admission, matching the split-11 endpoint failure mode (`18/50`). Weighted split-22 endpoint training was not run.
- The useful paper claim remains a precision/coverage claim, not a bad-label policy-benefit claim: bad labels help calibrate a score, but the current Can 20/80 converter is not clearly better than strong no-bad retrieval.

## Artifacts

- Aggregate CSV: `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split.csv`
- Per-split CSV: `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_per_split.csv`
- Split-11 endpoint diagnostic: `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md`
- Split-22 endpoint reports: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_{positive_only_nn,triage_bc}_policy0/eval_endpoint_200/REPORT.md`
- Source runs: `results/final_paper/per_seed/can_paired_pos20_bad80_split{11,22,33}_*_policy0/`
- Source score diagnostics: `results/final_paper/score_diagnostics/can_paired_pos20_bad80_split{11,22,33}_policy0/`
