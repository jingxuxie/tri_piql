# CAU Action-Conflict Can Five-Split Endpoint

This report aggregates the epoch-200, 50-episode Can evaluations for the fixed CAU action-conflict recipe.
It is a follow-up to the original first-20 Can404 screen, not a new frozen paper method.

## Aggregate Read

- CAU action-conflict: `193/250`.
- Positive-only NN: `174/250`.
- Weighted BC: `158/250`.
- TRIAGE-BC v0.1: `171/250`.
- Best old baseline per split: `192/250`.
- v0.2 selected union branch: `197/250`.
- Best non-oracle per split including v0.2: `209/250`.

## Per-Split Results

| split | CAU | positive | weighted | v0.1 | v0.2 selected | delta vs best old | delta vs v0.2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 101 | 33/50 | 19/50 | 37/50 | 28/50 | 45/50 | -4 | -12 |
| 202 | 42/50 | 40/50 | 33/50 | 36/50 | 45/50 | +2 | -3 |
| 303 | 40/50 | 36/50 | 25/50 | 35/50 | 39/50 | +4 | +1 |
| 404 | 35/50 | 39/50 | 33/50 | 36/50 | 27/50 | -4 | +8 |
| 505 | 43/50 | 40/50 | 30/50 | 36/50 | 41/50 | +3 | +2 |

## Decision

- The first-20 Can404 rejection was too pessimistic for CAU as a broad Can follow-up: over five 50-episode Can splits, CAU edges the best old non-oracle baseline per split by `1/250` and beats every fixed old branch in aggregate.
- CAU is still not SOTA-dominance evidence: it loses split404 to positive-only by `4/50`, loses split101 to weighted by `4/50`, and remains `4/250` below the v0.2 selected union branch in aggregate.
- The useful next research direction is not the current CAU gate; it is either a CAU-plus-v0.2 portfolio that avoids the split101/v0.2 gap and the split404 CAU loss, or a stronger state-conditional policy-quality signal.

## Artifacts

- Per-split CSV: `results/sota_candidate/cau_action_conflict_can_five_split_endpoint.csv`.
- Summary CSV: `results/sota_candidate/cau_action_conflict_can_five_split_endpoint_summary.csv`.
- Split101 CAU eval: `results/sota_candidate/cau_action_conflict_can101_b005_m05_eval50/REPORT.md`.
- Split202 CAU eval: `results/sota_candidate/cau_action_conflict_can202_b005_m05_eval50/REPORT.md`.
- Split303 CAU eval: `results/sota_candidate/cau_action_conflict_can303_b005_m05_eval50/REPORT.md`.
- Split404 CAU eval: `results/sota_candidate/cau_action_conflict_can404_b005_m05_eval50/REPORT.md`.
- Split505 CAU eval: `results/sota_candidate/cau_action_conflict_can505_b005_m05_eval50/REPORT.md`.
