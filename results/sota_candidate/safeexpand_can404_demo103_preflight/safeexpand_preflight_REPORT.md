# SafeExpand-BC Can404 Preflight

This preflight tests Candidate 4 from `triage_bc_sota_candidate_plan.md`.
It starts from the positive-only NN top40 support and only adds demos that pass a calibrated classifier certificate and an anchor-risk cap.

## Selected Recipe

- Score threshold: `pos_min` = `0.830569`.
- Risk cap: `anchor_q75` = `0.221187`.
- Added demos: `demo_103`.
- Added hidden-positive / hidden-bad diagnostic: `1` / `0`.
- Final selected unlabeled support: `36` hidden-positive, `5` hidden-bad out of `41`.
- Positive-only anchor support: `35` hidden-positive, `5` hidden-bad out of `40`.

## Read

Relaxing the classifier certificate admits hidden-bad demos immediately on this split.
The safe recipe is therefore a one-demo anchor-preserving expansion, not a broad support rescue.

## Outputs

- Config: `results/sota_candidate/safeexpand_can404_demo103_preflight/config.json`.
- Diagnostics: `results/sota_candidate/safeexpand_can404_demo103_preflight/diagnostics.json`.
- Support audit: `results/sota_candidate/safeexpand_can404_demo103_preflight/safeexpand_support_audit.csv`.
- Grid summary: `results/sota_candidate/safeexpand_can404_demo103_preflight/safeexpand_grid_summary.csv`.
