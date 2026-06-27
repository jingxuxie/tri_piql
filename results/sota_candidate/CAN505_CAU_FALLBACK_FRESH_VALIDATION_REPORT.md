# Can505 CAU Fallback Fresh Validation

This report evaluates the CAU-plus-positive fallback rule frozen from the Can404 post-hoc feature-gate audit.
The split-505 threshold is not refit: route to CAU action-conflict only when
`initial_anchor_pos_dist_mean gt 2.883`, otherwise use positive-only.

## Summary

- Opened split-505 initials: `demo_29, demo_39, demo_53`.
- First-20 screen: positive-only `15/20`, CAU alone `15/20`, frozen fallback `16/20`, gains `1`, losses `0`.
- 50-episode confirmation: positive-only `40/50`, CAU alone `43/50`, frozen fallback `41/50`, gains `1`, losses `0`.
- This is one fresh split, not yet a methods-dominance result.

## Checkpoints

| screen | checkpoint | positive | CAU alone | routed | gains | losses | status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| first20 | model_epoch_100 | 15/20 | 12/20 | 15/20 | 1 | 1 | fresh_screen_mixed |
| first20 | model_epoch_200 | 15/20 | 15/20 | 16/20 | 1 | 0 | fresh_screen_positive |
| eval50 | model_epoch_200 | 40/50 | 43/50 | 41/50 | 1 | 0 | fresh_screen_positive |

## Decision

- The frozen fallback passes the first-20 screen and the 50-episode confirmation: both add one success without losing any positive-only successes.
- CAU alone is stronger on the 50-episode check, but the fallback remains the anchor-safe deployable rule because it preserves positive-only starts by construction.
- This is enough to justify another predeclared fresh split, but not enough to change the paper to a SOTA-dominance claim.

## Artifacts

- Summary CSV: `results/sota_candidate/can505_cau_fallback_fresh_validation_summary.csv`.
- Per-episode CSV: `results/sota_candidate/can505_cau_fallback_fresh_validation_per_episode.csv`.
- CAU split-505 preflight: `results/sota_candidate/cau_action_conflict_can505_preflight/cau_preflight_REPORT.md`.
- CAU split-505 first-20 eval: `results/sota_candidate/cau_action_conflict_can505_b005_m05_eval20/REPORT.md`.
- CAU split-505 50-episode eval: `results/sota_candidate/cau_action_conflict_can505_b005_m05_eval50/REPORT.md`.
