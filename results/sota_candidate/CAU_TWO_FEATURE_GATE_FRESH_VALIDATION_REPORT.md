# CAU Two-Feature Gate Fresh Validation

This report validates the two-feature CAU-plus-positive gate selected on completed split 303 / 404 / 505 screens.
The split-101 and split-202 thresholds are frozen before evaluation:
`initial_anchor_pos_dist_mean le 1.273665 or initial_anchor_neg_dist_mean gt 3.131861`.

## Summary

- Split101 first20: positive-only `7/20`, CAU alone `15/20`, routed `9/20`, gains `2`, losses `0`.
- Split101 50-episode confirmation: positive-only `19/50`, CAU alone `33/50`, routed `24/50`, gains `5`, losses `0`.
- Split202 first20: positive-only `17/20`, CAU alone `16/20`, routed `17/20`, gains `0`, losses `0`.
- Split202 50-episode confirmation: positive-only `40/50`, CAU alone `42/50`, routed `40/50`, gains `0`, losses `0`.

## Checkpoints

| split | screen | checkpoint | positive | CAU alone | routed | gains | losses | opened initials | status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 101 | eval50 | model_epoch_200 | 19/50 | 33/50 | 24/50 | 5 | 0 | demo_39 demo_105 | fresh_screen_positive |
| 101 | first20 | model_epoch_100 | 7/20 | 11/20 | 7/20 | 0 | 0 | demo_39 demo_105 | fresh_screen_neutral |
| 101 | first20 | model_epoch_200 | 7/20 | 15/20 | 9/20 | 2 | 0 | demo_39 demo_105 | fresh_screen_positive |
| 202 | eval50 | model_epoch_200 | 40/50 | 42/50 | 40/50 | 0 | 0 | demo_5 demo_189 | fresh_screen_neutral |
| 202 | first20 | model_epoch_100 | 17/20 | 13/20 | 15/20 | 0 | 2 | demo_5 demo_189 | fresh_screen_mixed |
| 202 | first20 | model_epoch_200 | 17/20 | 16/20 | 17/20 | 0 | 0 | demo_5 demo_189 | fresh_screen_neutral |

## Decision

- The frozen two-feature gate has one positive fresh split with 50-episode confirmation and one neutral 50-episode fresh split.
- Split202 shows CAU-alone signal at 50 episodes, but the frozen gate does not route to the repaired starts; this exposes gate recall as the remaining bottleneck.
- This is stronger than the one-feature fallback, but it is still not SOTA-dominance evidence because the gate was selected on earlier completed screens and split202 adds no routed gain.

## Artifacts

- Summary CSV: `results/sota_candidate/cau_two_feature_gate_fresh_validation_summary.csv`.
- Per-episode CSV: `results/sota_candidate/cau_two_feature_gate_fresh_validation_per_episode.csv`.
- Gate audit: `results/sota_candidate/CAU_GATE_FEATURE_AUDIT_REPORT.md`.
- Split101 first20 eval: `results/sota_candidate/cau_action_conflict_can101_b005_m05_eval20/REPORT.md`.
- Split101 50-episode eval: `results/sota_candidate/cau_action_conflict_can101_b005_m05_eval50/REPORT.md`.
- Split202 first20 eval: `results/sota_candidate/cau_action_conflict_can202_b005_m05_eval20/REPORT.md`.
- Split202 50-episode eval: `results/sota_candidate/cau_action_conflict_can202_b005_m05_eval50/REPORT.md`.
