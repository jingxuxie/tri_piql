# Can404 Anchor-Overlap Diagnostic

This report compares the focused SOTA-candidate Can404 screens on the same first `20` valid-positive-start episodes.
It asks whether a candidate preserves the positive-only anchor or trades away starts that positive-only already solves.

## Summary

- Positive-only NN top40 solves `17/20`; the all-positive oracle solves `19/20`.
- The best focused SOTA candidates reach `16/20`; they do not beat the positive-only anchor.
- The near-miss candidates mainly fail by losing positive-only successes, not by discovering many new solvable starts.
- This supports the stop rule in `triage_bc_sota_candidate_plan.md`: do not scale another candidate unless a preflight shows explicit anchor preservation plus new-start gains.

## Matched-Start Table

| method | role | score | gains vs positive | losses vs positive | oracle-solved losses |
| --- | --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | anchor_baseline | 17/20 | 0 | 0 | 0 |
| Weighted BC full pool | baseline | 13/20 | 2 | 6 | 6 |
| v0.1 TRIAGE-BC | baseline | 14/20 | 1 | 4 | 3 |
| All-demo BC | diagnostic_control | 10/20 | 2 | 9 | 9 |
| All-positive oracle | oracle_control | 19/20 | 3 | 1 | 0 |
| Candidate C sequence mask | previous_candidate | 16/20 | 0 | 1 | 1 |
| SM-RWBC m0.03 lambda2 combined | sota_candidate | 10/20 | 2 | 9 | 8 |
| CAU action-conflict | sota_candidate | 16/20 | 2 | 3 | 3 |
| SafeExpand demo103 | sota_candidate | 12/20 | 1 | 6 | 5 |
| Demo-DPO ref-centered | sota_candidate | 16/20 | 1 | 2 | 1 |
| IQL-AWBC norm-topq | sota_candidate_diagnostic | 4/20 | 0 | 13 | 12 |
| Anchored IQL-AWBC | sota_candidate | 13/20 | 1 | 5 | 4 |

## Readout

- `CAU action-conflict` reaches `16/20`, with `2` gains over positive-only but `3` positive-only losses.
- `Demo-DPO ref-centered` reaches `16/20`, with `1` gains over positive-only but `2` positive-only losses.
- `Weighted BC full pool` reaches `13/20` and loses `6` positive-only successes.
- `All-demo BC` reaches `10/20` and loses `9` positive-only successes.
- `SM-RWBC m0.03 lambda2 combined` reaches `10/20` and loses `9` positive-only successes.
- `SafeExpand demo103` reaches `12/20` and loses `6` positive-only successes.

Interpretation: the failed candidates are not simply missing a little extra coverage. The common failure mode is anchor damage: objectives that add broad coverage, risk weighting, support expansion, or auxiliary losses often break starts the positive-only policy already solves. A future method should be screened first for `losses_vs_positive = 0` or an explicit abstain/fallback rule before any longer endpoint matrix.

## Artifacts

- Summary CSV: `results/sota_candidate/can404_anchor_overlap_summary.csv`.
- Report: `results/sota_candidate/CAN404_ANCHOR_OVERLAP_REPORT.md`.
