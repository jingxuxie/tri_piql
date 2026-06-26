# TRIAGE-BC v0.2 Fresh-Split Artifacts

This directory contains the fresh-split validation artifacts for the
development-frozen v0.2 portfolio router in `METHOD_FREEZE_V02.md`.

Current status: Can 40p/80b and Lift MG split seeds `101`, `202`, `303`,
`404`, and `505`
have completed selected endpoints plus the strongest completed same-backbone
baselines for the frozen v0.2 gate. This is a completed fresh-gate artifact
package, but not by itself a decisive high-impact methods claim.

## Key Reports

- Combined Can+Lift endpoint gate:
  `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- Fresh baseline coverage audit:
  `results/final_paper_v02/tables/v02_fresh_baseline_coverage_REPORT.md`
- Router-regret table:
  `results/final_paper_v02/tables/v02_router_regret_REPORT.md`
- A1 five-split extension preflight:
  `results/final_paper_v02/A1_FIVE_SPLIT_EXTENSION_PREFLIGHT.md`
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
| `404` | `positive_nn_risk_union_top40` | v0.2 selected | `27/50` |
| `404` | `positive_only_nn` | strong baseline | `39/50` |
| `404` | `weighted_bc` | strong baseline | `31/50` |
| `505` | `positive_nn_risk_union_top40` | v0.2 selected | `41/50` |
| `505` | `positive_only_nn` | strong baseline | `40/50` |
| `505` | `weighted_bc` | strong baseline | `30/50` |

Pooled completed fresh Can rows: v0.2 selected union `197/250`, best completed
per-split non-oracle baselines `192/250`.

## Completed Fresh Lift MG Splits

Lift MG sparse, official Robomimic BC-RNN-GMM, 200 epochs,
50 valid-positive-start rollouts:

| Split | Method | Role | Success |
| --- | --- | --- | ---: |
| `101` | `weighted_bc` | v0.2 selected | `31/50` |
| `101` | `positive_only_nn` | strong baseline | `28/50` |
| `101` | `triage_bc` | v0.1 hard-support audit | `36/50` |
| `202` | `weighted_bc` | v0.2 selected | `30/50` |
| `202` | `positive_only_nn` | strong baseline | `25/50` |
| `202` | `triage_bc` | v0.1 hard-support audit | `34/50` |
| `303` | `weighted_bc` | v0.2 selected | `19/50` |
| `303` | `positive_only_nn` | strong baseline | `21/50` |
| `303` | `triage_bc` | v0.1 hard-support audit | `20/50` |
| `404` | `weighted_bc` | v0.2 selected | `30/50` |
| `404` | `positive_only_nn` | strong baseline | `25/50` |
| `404` | `triage_bc` | v0.1 hard-support audit | `29/50` |
| `505` | `weighted_bc` | v0.2 selected | `33/50` |
| `505` | `positive_only_nn` | strong baseline | `26/50` |
| `505` | `triage_bc` | v0.1 hard-support audit | `24/50` |

Pooled completed fresh Lift rows: v0.2 selected weighted branch `143/250`, best
completed per-split non-oracle baselines `146/250`.

Interpretation: the frozen router correctly switches away from hard support on
Lift-like broad-coverage rows, but Lift remains a caveat rather than a method
win: v0.2 wins two of five splits and trails the completed per-split baseline
oracle by `3/250`.

## Combined Fresh Gate

Across completed Can 40p/80b and Lift MG fresh rows, the v0.2 selected branches
reach `340/500` versus `338/500` for the best completed non-oracle baseline per
split. This is directional branch-selection evidence, with the strongest
support coming from the router choosing different branches across regimes and
the main caveats coming from Can split `404`, Lift's negative per-split-baseline
margin, and zero-crossing paired-bootstrap intervals.

## Router-Regret Read

The A2 router-regret artifact is staged in
`results/final_paper_v02/tables/v02_router_regret_REPORT.md`.

Current completed Can+Lift regret to the audit-only oracle branch selector:

- v0.2 router: `340/500`, regret `23/500`.
- Always positive-only NN: `299/500`, regret `64/500`.
- Always weighted BC: `301/500`, regret `62/500`.

The same report includes generated Can hard-negative, coverage-shift, and
prefix-positive probes, where bad-aware hard support has zero regret to the
completed probe oracle, and Can MG as an abstained stress case. Fresh Can v0.1
is now complete across the five current split seeds at `171/250`, with
per-split endpoint counts `28/50`, `36/50`, `35/50`, `36/50`, and `36/50`.
The table is still not a fully complete fixed-branch leaderboard outside the
main Can+Lift regimes because some generated-probe rows are intentionally
marked not-applicable.
