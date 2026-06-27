# SafeExpand-BC Can404 Screen

This is the first SOTA Candidate 4 screen from `triage_bc_sota_candidate_plan.md`.
It tests a conservative one-demo expansion of the positive-only NN support.

## Support Change

- Added demos: `demo_103`.
- Added hidden-positive / hidden-bad diagnostic: `1` / `0`.
- Final selected unlabeled support: `36` hidden-positive, `5` hidden-bad out of `41`.

## Result

| method | successes | success rate | avg len | delta vs positive |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 17/20 | 0.850 | 148.2 | 0 |
| Weighted BC full pool | 13/20 | 0.650 | 211.5 | -4 |
| Candidate C sequence-mask e200 | 16/20 | 0.800 | 167.7 | -1 |
| CAU action-conflict beta0.05 margin0.5 e200 | 16/20 | 0.800 | 170.3 | -1 |
| SafeExpand demo103 e100 | 10/20 | 0.500 | 256.9 | -7 |
| SafeExpand demo103 e200 | 12/20 | 0.600 | 225.3 | -5 |

## Decision

- Best SafeExpand checkpoint: `12/20`.
- Positive-only NN matched screen: `17/20`.
- Candidate C and CAU matched screen: `16/20` and `16/20`.
- Decision: `reject` for this one-demo SafeExpand recipe.

Read: adding the single certified-safe hidden-positive demo does not preserve the anchor. Endpoint performance drops below weighted BC, so this recipe should not be scaled.

## Artifacts

- Preflight diagnostics: `results/sota_candidate/safeexpand_can404_demo103_preflight/diagnostics.json`.
- Eval report: `results/sota_candidate/safeexpand_can404_demo103_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/safeexpand_can404_screen_summary.csv`.
