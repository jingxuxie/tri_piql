# Precision/Coverage Frontier Across Regimes

This artifact puts all current support-selection regimes in the same audit space: hidden-positive recall on the x-axis and hidden-bad admission on the y-axis. Endpoint-backed points are larger in the figure; support-only points remain in the table as mechanism evidence.

## Endpoint-Backed Highlights

| regime | method | family | recall | bad admission | purity | endpoint | status |
|---|---|---|---:|---:|---:|---:|---|
| Can 40p/80b | positive-only NN top40 | positive-only | 0.883 | 0.058 | 0.883 | 108/150 (0.720) | complete_3split_endpoint |
| Can 40p/80b | TRIAGE adaptive masscap | TRIAGE | 0.917 | 0.333 | 0.579 | 99/150 (0.660) | complete_3split_endpoint |
| Can 40p/80b | weighted full pool | weighted | 1.000 | 1.000 | 0.333 | 90/150 (0.600) | complete_3split_endpoint |
| Can 20p/80b | positive-only NN top20 | positive-only | 0.817 | 0.046 | 0.817 | 54/100 (0.540) | partial_endpoint |
| Can 20p/80b | TRIAGE adaptive masscap | TRIAGE | 0.900 | 0.287 | 0.439 | 46/100 (0.460) | partial_endpoint |
| Can 20p/80b | weighted full pool | weighted | 1.000 | 1.000 | 0.200 | 18/50 (0.360) | partial_endpoint |
| Can 80p/80b | positive-only NN top80 | positive-only | 0.917 | 0.083 | 0.917 | 49/50 (0.980) | partial_endpoint |
| Can 80p/80b | TRIAGE adaptive masscap | TRIAGE | 0.571 | 0.117 | 0.830 | 43/50 (0.860) | partial_endpoint |
| Lift MG | weighted BC | weighted | 1.000 | 1.000 | 0.194 | 93/150 (0.620) | complete_3split_endpoint |
| Lift MG | positive-only NN top160 | positive-only | 0.413 | 0.040 | 0.713 | 82/150 (0.547) | complete_3split_endpoint |
| Lift MG | TRIAGE-BC / pos-min | TRIAGE | 0.508 | 0.006 | 0.955 | 74/150 (0.493) | complete_3split_endpoint |
| Lift MG | classifier-score top160 | classifier | 0.558 | 0.005 | 0.963 | 68/150 (0.453) | complete_3split_endpoint |
| Can hard-negative/action-conflict | bad-aware hybrid top40 | hybrid | 0.942 | 0.029 | 0.942 | 104/150 (0.693) | complete_3split_endpoint |
| Can hard-negative/action-conflict | positive-NN state-action top40 | positive-only | 0.583 | 0.208 | 0.583 | 91/150 (0.607) | complete_3split_endpoint |
| Can scarce-positive coverage shift | bad-aware hybrid top40 | hybrid | 0.983 | 0.008 | 0.983 | 120/150 (0.800) | complete_3split_endpoint |
| Can scarce-positive coverage shift | positive-NN state-action top40 | positive-only | 0.875 | 0.062 | 0.875 | 103/150 (0.687) | complete_3split_endpoint |
| Can prefix-positive | prefix bad-aware state top80 | bad-aware | 0.812 | 0.188 | 0.812 | 119/150 (0.793) | complete_3split_endpoint |
| Can prefix-positive | prefix positive-NN state-action top80 | positive-only | 0.154 | 0.846 | 0.154 | 6/150 (0.040) | complete_3split_endpoint |

## Matched Comparisons

| regime | bad_aware_or_triage | baseline | recall_delta | bad_admission_delta | endpoint_delta | endpoint | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | TRIAGE adaptive masscap | positive-only NN top40 | 0.034 | 0.275 | -0.060 | 99/150 vs 108/150 | complete_3split_endpoint |
| Can 40p/80b | TRIAGE adaptive masscap | weighted full pool | -0.083 | -0.667 | 0.060 | 99/150 vs 90/150 | complete_3split_endpoint |
| Can 20p/80b | TRIAGE adaptive masscap | positive-only NN top20 | 0.083 | 0.241 | -0.080 | 46/100 vs 54/100 | partial_endpoint |
| Can 80p/80b | TRIAGE adaptive masscap | positive-only NN top80 | -0.346 | 0.034 | -0.120 | 43/50 vs 49/50 | partial_endpoint |
| Hard-negative Can | bad-aware hybrid top40 | positive-NN state-action top40 | 0.359 | -0.179 | 0.087 | 104/150 vs 91/150 | complete_3split_endpoint |
| Coverage-shift Can | bad-aware hybrid top40 | positive-NN state-action top40 | 0.108 | -0.054 | 0.113 | 120/150 vs 103/150 | complete_3split_endpoint |
| Prefix-positive Can | prefix bad-aware state top80 | prefix positive-NN state-action top80 | 0.658 | -0.658 | 0.753 | 119/150 vs 6/150 | complete_3split_endpoint |
| Lift MG | TRIAGE-BC / pos-min | weighted BC | -0.492 | -0.994 | -0.127 | 74/150 vs 93/150 | complete_3split_endpoint |
| Lift MG | TRIAGE-BC / pos-min | positive-only NN top160 | 0.095 | -0.034 | -0.053 | 74/150 vs 82/150 | complete_3split_endpoint |

## Interpretation

- Default Can 40p/80b is a precision/coverage caveat: TRIAGE-BC recovers slightly more hidden-positive support than positive-only NN, but admits far more hidden-bad support and loses the endpoint.
- Generated hard-negative, coverage-shift, and prefix-positive Can probes are the clearest robotics mechanism evidence where bad-aware or hybrid support improves both support quality and endpoint success over matched positive-only retrieval.
- Lift MG shows that support purity alone is insufficient: TRIAGE-BC is much purer, but weighted BC has broad coverage and wins the frozen three-split endpoint.
- Can 20p/80b and Can 80p/80b remain appendix diagnostics because endpoint coverage is partial.

## Evidence Boundary

- Rows in the CSV: `77`.
- Endpoint-backed rows: `18`; complete three-split endpoint rows: `13`.
- Best endpoint-backed row in this frontier: `Can 80p/80b / positive-only NN top80` with `49/50` successes.
- Hidden labels are audit-only in this artifact; they are used to place supports on the precision/coverage plane and to construct generated split diagnostics, not as inputs to the deployed selection rules.

## Outputs

- `results/final_paper/tables/precision_coverage_frontier.csv`
- `results/final_paper/tables/precision_coverage_frontier_REPORT.md`
- `results/final_paper/figures/precision_coverage_frontier.png`
- `results/final_paper/figures/precision_coverage_frontier.pdf`
