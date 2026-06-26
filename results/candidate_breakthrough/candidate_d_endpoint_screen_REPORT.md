# Candidate D Negative-Action Endpoint Screen

This screen evaluates a conservative action-negative regularizer on the Can 40p/80b split-404 failure case.
The BC loss uses the Candidate C sequence mask, and the hinge penalizes likelihood of the nearest labeled-negative action.

## Preflight Audit

| field | value |
| --- | ---: |
| train demos | 130 |
| full-weight anchor demos | 50 |
| full-anchor negative-loss scope | selected |
| full-anchor negative-loss mass | 5528 |
| extra-only negative-loss scope | extra_selected |
| extra-only negative-loss mass | 222 |
| extra positive selected mass | 186 |
| extra bad selected mass | 36 |
| mean selected nearest-negative obs distance | 3.494 |
| hinge weight | 0.1 |
| hinge margin | 0.5 |

## First-20 Endpoint Summary

| method | kind | epochs | success | rate | avg len |
| --- | --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | baseline | 200 | 17/20 | 0.850 | 148.2 |
| Weighted BC full pool | baseline | 200 | 13/20 | 0.650 | 211.5 |
| TRIAGE-BC v0.1 hard support | baseline | 200 | 14/20 | 0.700 | 195.4 |
| Candidate C sequence-mask e200 | candidate_c | 200 | 16/20 | 0.800 | 167.7 |
| Candidate D negative-action e100 | candidate_d | 100 | 14/20 | 0.700 | 198.8 |
| Candidate D negative-action e200 | candidate_d | 200 | 13/20 | 0.650 | 205.4 |
| Candidate X extra-only negative-action e100 | candidate_x | 100 | 10/20 | 0.500 | 256.4 |
| Candidate X extra-only negative-action e200 | candidate_x | 200 | 14/20 | 0.700 | 201.5 |

## Read

- Best Candidate D checkpoint is `Candidate D negative-action e100` at `14/20`, versus Candidate C `16/20` and positive-only `17/20`.
- Moving the hinge off the full-weight positive-anchor demos does not rescue the objective: the extra-only variant reaches only `14/20` at epoch 200.
- Per-initial counts show neither hinge scope recovers `demo_39`; both remain below the Candidate C mask and positive-only anchor.
- Do not scale negative-action hinge variants unchanged. The remaining transition-level route needs a different bad-action target or an explicit anchor-preserving objective.

## Per-Initial Counts

| initial | positive | weighted | v0.1 | cand C e200 | cand D e100 | cand D e200 | cand X e100 | cand X e200 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| demo_5 | 2 | 0 | 2 | 2 | 2 | 2 | 1 | 2 |
| demo_29 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 1 |
| demo_39 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| demo_45 | 2 | 1 | 2 | 2 | 2 | 2 | 0 | 2 |
| demo_53 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_81 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 |
| demo_89 | 2 | 1 | 2 | 2 | 1 | 2 | 1 | 0 |
| demo_99 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 2 |
| demo_105 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 |
| demo_189 | 2 | 2 | 0 | 2 | 1 | 0 | 1 | 1 |

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_d_endpoint_screen_summary.csv`.
- Per-initial CSV: `results/candidate_breakthrough/candidate_d_endpoint_screen_per_initial.csv`.
- Preflight report: `results/candidate_breakthrough/candidate_d_negative_action_preflight/candidate_d_negative_action_preflight_REPORT.md`.
- Endpoint eval report: `results/candidate_breakthrough/candidate_d_neg0p1_can404_e200_eval20/REPORT.md`.
- Extra-only preflight report: `results/candidate_breakthrough/candidate_x_extra_negative_action_preflight/candidate_d_negative_action_preflight_REPORT.md`.
- Extra-only endpoint eval report: `results/candidate_breakthrough/candidate_x_extra_neg0p1_can404_e200_eval20/REPORT.md`.
