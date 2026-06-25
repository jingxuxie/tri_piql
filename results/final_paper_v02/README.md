# TRIAGE-BC v0.2 Fresh-Split Artifacts

This directory contains the fresh-split validation artifacts for the
development-frozen v0.2 portfolio router in `METHOD_FREEZE_V02.md`.

Current status: Can 40p/80b and Lift MG split seeds `101`, `202`, and `303`
have completed selected endpoints plus the strongest completed same-backbone
baselines for the frozen v0.2 gate. This is a completed fresh-gate artifact
package, but not by itself a decisive high-impact methods claim.

## Key Reports

- Combined Can+Lift endpoint gate:
  `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- Router/support preflight:
  `results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md`
- Can 40 endpoint summary:
  `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
- Lift MG endpoint summary:
  `results/final_paper_v02/tables/v02_fresh_lift_endpoint_REPORT.md`

## Completed Fresh Can 40 Splits

Can 40p/80b, official Robomimic BC-RNN-GMM, 200 epochs,
50 valid-positive-start rollouts:

| Split | Method | Role | Success |
| --- | --- | --- | ---: |
| `101` | `positive_nn_risk_union_top40` | v0.2 selected | `45/50` |
| `101` | `weighted_bc` | strong baseline | `37/50` |
| `101` | `positive_only_nn` | strong baseline | `19/50` |
| `202` | `positive_nn_risk_union_top40` | v0.2 selected | `45/50` |
| `202` | `positive_only_nn` | strong baseline | `40/50` |
| `202` | `weighted_bc` | strong baseline | `33/50` |
| `303` | `positive_nn_risk_union_top40` | v0.2 selected | `39/50` |
| `303` | `positive_only_nn` | strong baseline | `36/50` |
| `303` | `weighted_bc` | strong baseline | `25/50` |

Pooled completed fresh Can rows: v0.2 selected union `129/150`, best completed
per-split non-oracle baselines `113/150`.

## Completed Fresh Lift MG Splits

Lift MG sparse, official Robomimic BC-RNN-GMM, 200 epochs,
50 valid-positive-start rollouts:

| Split | Method | Role | Success |
| --- | --- | --- | ---: |
| `101` | `weighted_bc` | v0.2 selected | `31/50` |
| `101` | `positive_only_nn` | strong baseline | `28/50` |
| `202` | `weighted_bc` | v0.2 selected | `30/50` |
| `202` | `positive_only_nn` | strong baseline | `25/50` |
| `303` | `weighted_bc` | v0.2 selected | `19/50` |
| `303` | `positive_only_nn` | strong baseline | `21/50` |

Pooled completed fresh Lift rows: v0.2 selected weighted branch `80/150`, best
completed per-split non-oracle baselines `74/150`.

Interpretation: the frozen router correctly switches away from hard support on
Lift-like broad-coverage rows, but the Lift endpoint advantage is modest and
not uniform across splits. Split `303` favors positive-only NN by `2/50`.

## Combined Fresh Gate

Across completed Can 40p/80b and Lift MG fresh rows, the v0.2 selected branches
reach `209/300` versus `187/300` for the best completed non-oracle baseline per
split. This is positive branch-selection evidence, with the strongest support
coming from Can hard union and the main caveat coming from the modest Lift
weighted-branch margin.
