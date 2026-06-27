# Demo Preference Can404 Screen

This is the first SOTA Candidate 5 screen from `triage_bc_sota_candidate_plan.md`.
It fine-tunes the positive-only policy with BC on the positive-NN support and a reference-centered demo preference term over labeled positives versus labeled negatives.

## Setup

- Positive-NN BC support train demos: `50`.
- Labeled positive / negative preference demos: `10` / `10`.
- Labeled positive / negative preference transitions: `1118` / `848`.
- Non-reference preference smoke was saturated at initialization: the positive-only checkpoint already assigned labeled negatives far lower likelihood than labeled positives.
- The screened recipe therefore uses reference-centered DPO with preference weight `1.0`, temperature `1.0`, margin `0.0`, and output anchor weight `10.0`.

## Result

| method | successes | success rate | avg len | delta vs positive |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 17/20 | 0.850 | 148.2 | 0 |
| Weighted BC full pool | 13/20 | 0.650 | 211.5 | -4 |
| Candidate C sequence-mask e200 | 16/20 | 0.800 | 167.7 | -1 |
| CAU action-conflict beta0.05 margin0.5 e200 | 16/20 | 0.800 | 170.3 | -1 |
| SafeExpand demo103 e200 | 12/20 | 0.600 | 225.3 | -5 |
| Demo-DPO ref-centered w1 e5 | 16/20 | 0.800 | 163.7 | -1 |
| Demo-DPO ref-centered w1 e10 | 2/20 | 0.100 | 372.4 | -15 |
| Demo-DPO ref-centered w1 e15 | 16/20 | 0.800 | 162.8 | -1 |
| Demo-DPO ref-centered w1 e20 | 16/20 | 0.800 | 163.4 | -1 |

## Decision

- Best Demo-DPO checkpoint: `16/20`.
- Positive-only NN matched screen: `17/20`.
- Candidate C and CAU matched screen: `16/20` and `16/20`.
- Decision: `reject` for this reference-centered labeled-demo preference recipe.

Read: the preference term is active, but it does not improve the endpoint anchor and has an unstable checkpoint at epoch 10. Do not scale this recipe unchanged.

## Artifacts

- Preflight diagnostics: `results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/diagnostics.json`.
- Eval report: `results/sota_candidate/demo_pref_refcenter_can404_w1_e20_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/demo_preference_can404_screen_summary.csv`.
