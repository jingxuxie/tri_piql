# Hybrid Candidate Support Audit

Generated from staged final-paper split files, classifier score diagnostics, and full positive-NN support rankings.
This is a support-only audit: hidden labels are used only to decide which candidates are worth endpoint training.

## Setting-Level Takeaways

| setting | positive baseline | cleanest hybrid | coverage hybrid | hybrid frontier rows |
|---|---|---|---|---:|
| Can 40p/80b | positive_nn_top40 recall 0.883, bad 0.058, purity 0.883 | hybrid_filter_pos_min_pos40 recall 0.275, bad 0.000, purity 1.000 | hybrid_union_pos40_triage recall 0.967, bad 0.375, purity 0.563 | 4 |
| Can 20p/80b | positive_nn_top20 recall 0.817, bad 0.046, purity 0.817 | hybrid_intersection_pos20_classifier20 recall 0.600, bad 0.000, purity 1.000 | hybrid_union_pos20_triage recall 0.950, bad 0.329, purity 0.419 | 8 |
| Can 80p/80b | positive_nn_top80 recall 0.917, bad 0.083, purity 0.917 | hybrid_filter_pos_min_pos80 recall 0.283, bad 0.000, purity 1.000 | hybrid_union_pos80_triage recall 0.942, bad 0.200, purity 0.825 | 5 |
| Lift MG | positive_nn_top160 recall 0.413, bad 0.040, purity 0.713 | hybrid_filter_pos_p10_pos160 recall 0.290, bad 0.001, purity 0.992 | hybrid_union_pos160_triage recall 0.610, bad 0.045, purity 0.766 | 4 |

## Primary Hybrid Rows

| setting | candidate | family | selected | recall | bad admission | purity |
|---|---|---|---:|---:|---:|---:|
| Can 40p/80b | positive_nn_top40 | positive-only | 120 | 0.883 | 0.058 | 0.883 |
| Can 40p/80b | classifier_top40 | bad-aware hard | 120 | 0.708 | 0.146 | 0.708 |
| Can 40p/80b | triage_existing | bad-aware hard | 190 | 0.917 | 0.333 | 0.579 |
| Can 40p/80b | hybrid_filter_mid_mean_fill_classifier_to40 | hybrid | 120 | 0.850 | 0.075 | 0.850 |
| Can 40p/80b | hybrid_filter_mid_mean_pos40 | hybrid | 99 | 0.808 | 0.008 | 0.980 |
| Can 40p/80b | hybrid_intersection_pos40_classifier80 | hybrid | 111 | 0.850 | 0.037 | 0.919 |
| Can 40p/80b | hybrid_rank_fusion_equal_top40 | hybrid | 120 | 0.875 | 0.062 | 0.875 |
| Can 40p/80b | hybrid_union_pos40_classifier20 | hybrid | 132 | 0.908 | 0.096 | 0.826 |
| Lift MG | positive_nn_top160 | positive-only | 480 | 0.413 | 0.040 | 0.713 |
| Lift MG | classifier_top160 | bad-aware hard | 480 | 0.558 | 0.005 | 0.963 |
| Lift MG | triage_existing | bad-aware hard | 441 | 0.508 | 0.006 | 0.955 |
| Lift MG | hybrid_filter_mid_mean_fill_classifier_to160 | hybrid | 480 | 0.533 | 0.011 | 0.919 |
| Lift MG | hybrid_intersection_pos160_classifier320 | hybrid | 368 | 0.408 | 0.009 | 0.918 |
| Lift MG | hybrid_rank_fusion_equal_top160 | hybrid | 480 | 0.510 | 0.017 | 0.879 |
| Lift MG | hybrid_union_pos160_classifier80 | hybrid | 532 | 0.473 | 0.041 | 0.737 |

## Interpretation

- On Can 40p/80b, strict bad-filtered positive-NN candidates are much cleaner than positive-only top40 but lose hidden-positive coverage; refill and union variants do not improve the positive-only support frontier.
- On Lift MG, classifier-heavy hybrids become very pure but remain far below weighted BC's broad coverage regime; this supports treating Lift as a soft/coverage branch rather than another hard-filter endpoint run.
- The current hybrid support screen does not justify immediate endpoint training for the tested rules. The next useful method work is a stronger proxy or a genuinely new candidate that improves recall without increasing bad admission on Can.

## Outputs

- `results/final_paper/tables/hybrid_candidate_support_per_split.csv`
- `results/final_paper/tables/hybrid_candidate_support_summary.csv`
- `results/final_paper/tables/hybrid_candidate_support_REPORT.md`

Summary rows: `94`.
