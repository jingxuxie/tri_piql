# IQL-AWBC Can404 Screen

This is the first SOTA Candidate 6 endpoint screen from `triage_bc_sota_candidate_plan.md`.
It uses a classifier-reward Q/V preflight to build advantage weights, then trains the official BC-RNN-GMM extractor on the selected norm-topq weights.

## Offline Preflight Signal

- State-action classifier labeled accuracy: `0.997`.
- Learned advantage means, pos/neg/unlabeled: `1.232` / `-1.184` / `-0.123`.
- Selected hidden-bad weighted mass fraction: `0.326`.
- Rejected SM-RWBC hidden-bad weighted mass fraction: `0.376`.
- Selected hidden-positive mass: `1100.7`.

## Endpoint Result

| method | successes | success rate | avg len | delta vs positive |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 17/20 | 0.850 | 148.2 | 0 |
| Weighted BC full pool | 13/20 | 0.650 | 211.5 | -4 |
| Candidate C sequence-mask e200 | 16/20 | 0.800 | 167.7 | -1 |
| CAU action-conflict beta0.05 margin0.5 e200 | 16/20 | 0.800 | 170.3 | -1 |
| Demo-DPO ref-centered w1 e20 | 16/20 | 0.800 | 163.4 | -1 |
| IQL-AWBC norm-topq e50 | 0/20 | 0.000 | 400.0 | -17 |
| IQL-AWBC norm-topq e100 | 4/20 | 0.200 | 341.3 | -13 |

## Decision

- Best IQL-AWBC checkpoint: `4/20`.
- Positive-only NN matched screen: `17/20`.
- Candidate C / CAU / Demo-DPO matched screen: `16/20`, `16/20`, `16/20`.
- Decision: `reject` for this classifier-reward IQL-AWBC norm-topq recipe.

Read: the Q/V preflight separates positive and negative advantages and improves the hidden-bad mass diagnostic, but the endpoint policy collapses. Do not scale this recipe unchanged.

## Artifacts

- Preflight report: `results/sota_candidate/iql_awbc_can404_preflight/iql_awbc_preflight_REPORT.md`.
- Eval report: `results/sota_candidate/iql_awbc_can404_norm_topq_e100_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/iql_awbc_can404_screen_summary.csv`.
