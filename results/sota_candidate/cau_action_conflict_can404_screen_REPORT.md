# CAU-BC Can404 Screen

This is the first SOTA Candidate 2 screen from `triage_bc_sota_candidate_plan.md`.
It reuses the Candidate C sequence mask but swaps the rejected nearest-state negative action for an action-conflict target.

## Result

| method | successes | success rate | avg len | delta vs positive |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 17/20 | 0.850 | 148.2 | 0 |
| Weighted BC full pool | 13/20 | 0.650 | 211.5 | -4 |
| Candidate C sequence-mask e200 | 16/20 | 0.800 | 167.7 | -1 |
| Candidate D negative-action e100 | 14/20 | 0.700 | 198.8 | -3 |
| Candidate D negative-action e200 | 13/20 | 0.650 | 205.4 | -4 |
| Candidate X extra-only negative-action e100 | 10/20 | 0.500 | 256.4 | -7 |
| Candidate X extra-only negative-action e200 | 14/20 | 0.700 | 201.5 | -3 |
| CAU action-conflict beta0.05 margin0.5 e100 | 6/20 | 0.300 | 319.0 | -11 |
| CAU action-conflict beta0.05 margin0.5 e200 | 16/20 | 0.800 | 170.3 | -1 |

## Decision

- Best CAU checkpoint: `16/20`.
- Positive-only NN matched screen: `17/20`.
- Previous Candidate C sequence mask: `16/20`.
- Previous best nearest-negative hinge screen: `14/20`.
- Decision: `reject` for this action-conflict `beta=0.05`, `margin=0.5`, selected-scope recipe.

Read: action-conflict retrieval fixes the worst nearest-negative hinge regression and ties Candidate C, but it still does not beat the positive-only anchor on split 404. Do not promote or scale this recipe unchanged.

## Artifacts

- Preflight report: `results/sota_candidate/cau_action_conflict_can404_preflight/cau_preflight_REPORT.md`.
- Eval report: `results/sota_candidate/cau_action_conflict_can404_b005_m05_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/cau_action_conflict_can404_screen_summary.csv`.
