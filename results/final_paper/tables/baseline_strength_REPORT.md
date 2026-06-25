# Baseline Strength And Completeness Report

Generated from final-paper per-seed manifests, support audits, hidden-label audits, and endpoint metrics.
Hidden labels are audit-only; this report is for evidence accounting and v0.2 planning.

## Primary Endpoint Ranking

| task | method | endpoint | support | status |
|---|---|---:|---|---|
| Can 40p/80b | positive-only NN | 108/150 (0.720) | 106 pos, 14 bad / 120 selected (purity 0.883) | complete_3split_endpoint |
| Can 40p/80b | TRIAGE-BC | 99/150 (0.660) | 110 pos, 80 bad / 190 selected (purity 0.579) | complete_3split_endpoint |
| Can 40p/80b | weighted BC | 90/150 (0.600) | 120 pos, 240 bad / 360 selected (purity 0.333) | complete_3split_endpoint |
| Can 40p/80b | all-demo BC | 81/150 (0.540) | 0 pos, 0 bad / 0 selected (purity 0.000) | complete_3split_endpoint |
| Lift MG | weighted BC | 93/150 (0.620) | 828 pos, 3432 bad / 4260 selected (purity 0.194) | complete_3split_endpoint |
| Lift MG | positive-only NN | 82/150 (0.547) | 342 pos, 138 bad / 480 selected (purity 0.713) | complete_3split_endpoint |
| Lift MG | TRIAGE-BC | 74/150 (0.493) | 421 pos, 20 bad / 441 selected (purity 0.955) | complete_3split_endpoint |
| Lift MG | classifier top-k | 68/150 (0.453) | 462 pos, 18 bad / 480 selected (purity 0.963) | complete_3split_endpoint |
| Lift MG | all-demo BC | 31/150 (0.207) | 0 pos, 0 bad / 0 selected (purity 0.000) | complete_3split_endpoint |

Interpretation: the current v0.1 primary matrix does not yet clear the high-impact methods bar. Can 40p/80b is led by positive-only NN, and Lift MG is led by weighted BC.

## Diagnostic Endpoint Coverage

| task | method | endpoint splits | endpoint | support splits | status |
|---|---|---|---:|---|---|
| Can 20p/80b | TRIAGE-BC | 11/22 | 46/100 (0.460) | 11/22/33 | partial_endpoint |
| Can 20p/80b | classifier top-k | none |  | 11 | support_only |
| Can 20p/80b | positive-only NN | 11/22 | 54/100 (0.540) | 11/22/33 | partial_endpoint |
| Can 20p/80b | weighted BC | 11 | 18/50 (0.360) | 11/22/33 | partial_endpoint |
| Can 80p/80b | TRIAGE-BC | 33 | 43/50 (0.860) | 11/22/33 | partial_endpoint |
| Can 80p/80b | classifier top-k | none |  | 11/22/33 | support_only |
| Can 80p/80b | positive-only NN | 33 | 49/50 (0.980) | 11/22/33 | partial_endpoint |
| Can 80p/80b | weighted BC | none |  | 11 | support_only |

## Missing Or Incomplete Rows

- Can 20p/80b / classifier top-k: support_only (endpoint splits none, support splits 11)
- Can 20p/80b / positive-only NN: partial_endpoint (endpoint splits 11/22, support splits 11/22/33)
- Can 20p/80b / TRIAGE-BC: partial_endpoint (endpoint splits 11/22, support splits 11/22/33)
- Can 20p/80b / weighted BC: partial_endpoint (endpoint splits 11, support splits 11/22/33)
- Can 80p/80b / classifier top-k: support_only (endpoint splits none, support splits 11/22/33)
- Can 80p/80b / positive-only NN: partial_endpoint (endpoint splits 33, support splits 11/22/33)
- Can 80p/80b / TRIAGE-BC: partial_endpoint (endpoint splits 33, support splits 11/22/33)
- Can 80p/80b / weighted BC: support_only (endpoint splits none, support splits 11)

## v0.2 Decision Gate

- Current candidate family is not yet enough for a top-tier methods claim: v0.1 is not best non-oracle on either primary task.
- Before GPU-heavy v0.2 final runs, the next useful cheap artifact is a candidate-family oracle/proxy audit using these master tables.
- Can 20p/80b and Can 80p/80b should remain diagnostic unless their endpoint rows are completed across the same split/method grid.

## Outputs

- `results/final_paper/tables/endpoint_master_table.csv`
- `results/final_paper/tables/support_master_table.csv`
- `results/final_paper/tables/baseline_strength_REPORT.md`

Support rows normalized: `53`.
Endpoint rows with metrics: `40`.
