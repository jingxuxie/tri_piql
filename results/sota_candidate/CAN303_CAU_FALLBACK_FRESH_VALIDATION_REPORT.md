# Can303 CAU Fallback Fresh Validation

This report evaluates the CAU-plus-positive fallback rule frozen from the Can404 post-hoc feature-gate audit.
The split-303 threshold is not refit: route to CAU action-conflict only when
`initial_anchor_pos_dist_mean gt 2.883`, otherwise use positive-only.

## Summary

- Opened split-303 initials: `demo_39`.
- First-20 screen: positive-only `15/20`, CAU alone `17/20`, frozen fallback `15/20`, gains `0`, losses `0`.
- CAU alone improves on this split, but the frozen fallback does not open on the starts where CAU adds successes.
- Because the predeclared first-20 fallback is neutral rather than positive, no 50-episode confirmation is run.

## Checkpoints

| screen | checkpoint | positive | CAU alone | routed | gains | losses | status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| first20 | model_epoch_100 | 15/20 | 14/20 | 15/20 | 0 | 0 | fresh_screen_neutral |
| first20 | model_epoch_200 | 15/20 | 17/20 | 15/20 | 0 | 0 | fresh_screen_neutral |

## Decision

- The frozen fallback preserves the positive-only anchor on split 303, but it does not improve the screen.
- This blocks promotion of the fallback as SOTA-dominance evidence and argues against spending longer evaluations on this unchanged gate.
- The remaining technical signal is that CAU alone can help some starts, but the current hidden-label-free gate does not identify those starts.

## Artifacts

- Summary CSV: `results/sota_candidate/can303_cau_fallback_fresh_validation_summary.csv`.
- Per-episode CSV: `results/sota_candidate/can303_cau_fallback_fresh_validation_per_episode.csv`.
- CAU split-303 preflight: `results/sota_candidate/cau_action_conflict_can303_preflight/cau_preflight_REPORT.md`.
- CAU split-303 first-20 eval: `results/sota_candidate/cau_action_conflict_can303_b005_m05_eval20/REPORT.md`.
