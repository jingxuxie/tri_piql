# Candidate Family Oracle/Proxy Audit

Generated from staged final-paper endpoint, support, and proxy artifacts.
Hidden labels are audit-only; endpoint-oracle and audit-oracle rows are diagnostics, not deployable selection rules.

## Decision Summary

| setting | endpoint oracle | strongest baseline | best bad-aware | bad-aware gap | coverage proxy winner | audit-support winner | decision |
|---|---|---|---|---:|---|---|---|
| Can 40p/80b | positive-NN/risk union top40 116/150 (0.773) | positive-only NN top40 108/150 (0.720) | positive-NN/risk union top40 116/150 (0.773) | 0.053 | weighted BC full pool 90/150 (0.600) | positive-NN/risk union top40 116/150 (0.773) | portfolio contains an endpoint branch above the strongest baseline |
| Lift MG | weighted BC 93/150 (0.620) | weighted BC 93/150 (0.620) | TRIAGE-BC 74/150 (0.493) | -0.127 | weighted BC 93/150 (0.620) | classifier top-k 68/150 (0.453) | portfolio can only match the strongest baseline by selecting that baseline |
| Can 20p/80b | positive-only NN top20 54/100 (0.540) | positive-only NN top20 54/100 (0.540) | TRIAGE-BC adaptive masscap 46/100 (0.460) | -0.080 | weighted BC full pool 18/50 (0.360) | positive-only NN top20 54/100 (0.540) | portfolio can only match the strongest baseline by selecting that baseline |
| Can 80p/80b | positive-only NN top80 49/50 (0.980) | positive-only NN top80 49/50 (0.980) | TRIAGE-BC adaptive masscap 43/50 (0.860) | -0.120 | positive-only NN top80 49/50 (0.980) | positive-only NN top80 49/50 (0.980) | portfolio can only match the strongest baseline by selecting that baseline |

## Primary Candidate Audit

| setting | candidate | family | recall | bad admission | support purity | coverage proxy | audit score | endpoint |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Can 40p/80b | TRIAGE-BC adaptive masscap | bad-aware hard | 0.917 | 0.333 | 0.579 | 0.528 | 0.584 | 99/150 (0.660) |
| Can 40p/80b | classifier top10 | bad-aware hard | 0.217 | 0.017 | 0.867 | 0.083 | 0.200 |  |
| Can 40p/80b | classifier top20 | bad-aware hard | 0.425 | 0.037 | 0.850 | 0.167 | 0.388 |  |
| Can 40p/80b | classifier top40 | bad-aware hard | 0.708 | 0.146 | 0.708 | 0.333 | 0.562 |  |
| Can 40p/80b | classifier top60 | bad-aware hard | 0.900 | 0.300 | 0.600 | 0.500 | 0.600 |  |
| Can 40p/80b | classifier top80 | bad-aware hard | 0.967 | 0.517 | 0.483 | 0.667 | 0.450 |  |
| Can 40p/80b | all-positive oracle | diagnostic oracle |  |  |  |  |  | 147/150 (0.980) |
| Can 40p/80b | positive-only NN top40 | positive-only | 0.883 | 0.058 | 0.883 | 0.333 | 0.825 | 108/150 (0.720) |
| Can 40p/80b | weighted BC full pool | soft weighted | 1.000 | 1.000 | 0.333 | 1.000 | 0.000 | 90/150 (0.600) |
| Can 40p/80b | positive-NN/risk union top40 | union hybrid | 0.992 | 0.067 | 0.881 | 0.375 | 0.925 | 116/150 (0.773) |
| Lift MG | TRIAGE-BC | bad-aware hard | 0.508 | 0.006 | 0.955 | 0.104 | 0.502 | 74/150 (0.493) |
| Lift MG | classifier top-k | bad-aware hard | 0.558 | 0.005 | 0.963 | 0.113 | 0.553 | 68/150 (0.453) |
| Lift MG | all-positive oracle | diagnostic oracle |  |  |  |  |  | 105/150 (0.700) |
| Lift MG | positive-only NN | positive-only | 0.413 | 0.040 | 0.713 | 0.113 | 0.373 | 82/150 (0.547) |
| Lift MG | weighted BC | soft weighted | 1.000 | 1.000 | 0.194 | 1.000 | 0.000 | 93/150 (0.620) |

## Can MG Proxy Stress

| split | rollout-best branch | proxy winners | proxy-best matches |
|---|---|---|---:|
| can_mg_original | weighted (0.333) | allpositive | 0/6 |
| can_mg_shuffle42 | hard_posmin (0.100) | hard_posmin/soft_weighted | 6/6 |

## Interpretation

- The new Can 40p/80b union branch is the first endpoint-evaluated bad-aware candidate in this audit that exceeds the strongest positive-only/weighted baseline.
- This does not solve v0.2 by itself: Lift MG is still won by the weighted branch, and Can MG remains an abstention/stress case.
- The all-positive oracle remains well above non-oracle methods on Can 40p/80b and Lift MG, so there is backbone/headroom, but the current support-conversion family does not capture it.
- Coverage-only selection picks broad weighted support, which explains Lift MG but fails Can-style contamination even after adding the union branch; audit-only precision/coverage scores are not deployable.
- Can MG confirms that simple positive/negative likelihood proxies can pick the wrong branch or miss that all branches are weak.

## v0.2 Gate

- Do not promote the union branch as TRIAGE-BC v0.2 until a hidden-label-free selector is frozen and validated on fresh cross-task splits.
- The next cheap v0.2 step is a portfolio-router audit: choose union-style hard support for low-mass Can-like contamination, weighted support for Lift-like coverage, and abstention for ambiguous Can MG-style pools.
- Fresh GPU endpoint budget should be reserved for a frozen rule that has this complete cross-task story, not for more post-hoc Can-only tuning.

## Outputs

- `results/final_paper/tables/candidate_family_audit.csv`
- `results/final_paper/tables/candidate_family_decision_table.csv`
- `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`

Candidate rows audited: `25`.
