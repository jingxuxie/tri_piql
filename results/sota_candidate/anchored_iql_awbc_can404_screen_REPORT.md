# Anchored IQL-AWBC Can404 Screen

This is a follow-up to the SOTA Candidate 6 IQL-AWBC failure.
It initializes from the positive-only checkpoint and applies output-level anchor-logprob weight `10.0` while training on the selected IQL-AWBC norm-topq transition weights.

## Setup

- Q/V advantage means, pos/neg/unlabeled: `1.232` / `-1.184` / `-0.123`.
- IQL-AWBC selected hidden-bad mass fraction: `0.326`.
- Fine-tune: positive-only initialization, anchor-logprob weight `10.0`, epochs `5/10/15/20`.

## Result

| method | successes | success rate | avg len | delta vs positive |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 17/20 | 0.850 | 148.2 | 0 |
| Weighted BC full pool | 13/20 | 0.650 | 211.5 | -4 |
| Candidate C sequence-mask e200 | 16/20 | 0.800 | 167.7 | -1 |
| CAU action-conflict beta0.05 margin0.5 e200 | 16/20 | 0.800 | 170.3 | -1 |
| Demo-DPO ref-centered w1 e20 | 16/20 | 0.800 | 163.4 | -1 |
| IQL-AWBC norm-topq e100 | 4/20 | 0.200 | 341.3 | -13 |
| Candidate V output-anchor e5 | 15/20 | 0.750 | 180.6 | -2 |
| Candidate V output-anchor e10 | 18/20 | 0.900 | 135.6 | 1 |
| Candidate V output-anchor e15 | 15/20 | 0.750 | 179.1 | -2 |
| Candidate V output-anchor e20 | 16/20 | 0.800 | 164.2 | -1 |
| Anchored IQL-AWBC w10 e5 | 10/20 | 0.500 | 248.2 | -7 |
| Anchored IQL-AWBC w10 e10 | 13/20 | 0.650 | 207.4 | -4 |
| Anchored IQL-AWBC w10 e15 | 11/20 | 0.550 | 235.0 | -6 |
| Anchored IQL-AWBC w10 e20 | 12/20 | 0.600 | 229.8 | -5 |

## Decision

- Best anchored IQL-AWBC checkpoint: `13/20`.
- Positive-only NN matched screen: `17/20`.
- Prior Candidate V output-anchor best on this screen: `18/20`.
- Decision: `reject` for this anchored IQL-AWBC recipe.

Read: output anchoring repairs the total IQL-AWBC collapse but the IQL-derived weights still underperform both the positive-only anchor and the earlier non-IQL output-anchor recipe. Do not scale this combination unchanged.

## Artifacts

- Eval report: `results/sota_candidate/anchored_iql_awbc_can404_w10_e20_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/anchored_iql_awbc_can404_screen_summary.csv`.
- Train directory: `results/sota_candidate/anchored_iql_awbc_can404_w10_e20_train/anchored_iql_awbc_can404_w10_e20_seed0/20260626142620/`.
