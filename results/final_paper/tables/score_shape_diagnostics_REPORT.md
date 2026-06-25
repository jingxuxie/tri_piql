# Score-Shape Diagnostics

This report consolidates score-distribution diagnostics for the current Figure 4 candidate.
Can 40p/80b and Lift MG use frozen final split seeds 11/22/33; Can MG uses the original stress diagnostic and is not a final endpoint row.

| analysis | status | positive_count | bad_count | positive_mean | bad_mean | positive_frac_ge_0p95 | bad_frac_ge_0p95 | plotted_threshold | message |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | primary_frozen_3split | 120 | 240 | 0.713 | 0.368 | 0.117 | 0.017 | 0.479 | intermediate overlap; mass-capped hard support |
| Lift MG | primary_frozen_3split | 828 | 3432 | 0.790 | 0.152 | 0.399 | 0.002 | 0.903 | high-purity hard support but endpoint under-covers |
| Can MG | stress_diagnostic_original | 2064 | 9456 | 0.886 | 0.423 | 0.518 | 0.094 | 0.873 | large ambiguous high-score plateau; router-v2 abstains |

## Interpretation

- Can 40p/80b has overlap between hidden-positive and hidden-bad unlabeled demos, motivating a precision/coverage support converter.
- Lift MG scores separate positives from most bad demos, but the endpoint result shows high-purity hard support can still under-cover policy learning.
- Can MG has many positives and bad demos in the high-score plateau, explaining why router-v2 abstains and why simple likelihood proxies fail.

## Figure

- PNG: `results/final_paper/figures/score_shape_diagnostics.png`
- PDF: `results/final_paper/figures/score_shape_diagnostics.pdf`
