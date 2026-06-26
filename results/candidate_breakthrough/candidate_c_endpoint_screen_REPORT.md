# Candidate C Sequence-Mask Endpoint Screen

This screen evaluates the conservative sequence-mask recipe on the Can 40p/80b split-404 failure case.
The implementation keeps the full weighted training pool for recurrent context, gives positive-anchor demos full loss mass,
and admits only high-score, positive-margin timesteps from extra weighted-pool demos.

## Preflight Mask Audit

| field | value |
| --- | ---: |
| train demos | 130 |
| full-weight anchor demos | 50 |
| extra demos in weighted pool | 80 |
| extra positive demos with selected mass | 5 |
| extra bad demos with selected mass | 8 |
| extra positive selected mass | 186 |
| extra bad selected mass | 36 |
| extra bad masked fraction | 0.162 |
| extra selected mass fraction of all transitions | 0.040 |

## First-20 Endpoint Summary

| method | kind | epochs | success | rate | avg len |
| --- | --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | baseline | 200 | 17/20 | 0.850 | 148.2 |
| Weighted BC full pool | baseline | 200 | 13/20 | 0.650 | 211.5 |
| TRIAGE-BC v0.1 hard support | baseline | 200 | 14/20 | 0.700 | 195.4 |
| v0.2 positive-NN/risk union top40 | baseline | 200 | 7/20 | 0.350 | 299.6 |
| Candidate A transition-weighted e200 | candidate_a | 200 | 12/20 | 0.600 | 222.5 |
| Candidate B router labeled support, no bias | candidate_b | 200 | 16/20 | 0.800 | 162.2 |
| Candidate B router positive-anchor support, no bias | candidate_b | 200 | 16/20 | 0.800 | 164.6 |
| Candidate C sequence-mask e100 | candidate_c | 100 | 8/20 | 0.400 | 290.6 |
| Candidate C sequence-mask e200 | candidate_c | 200 | 16/20 | 0.800 | 167.7 |

## Read

- Best Candidate C checkpoint is `Candidate C sequence-mask e200` at `16/20`, versus positive-only `17/20` and weighted BC `13/20`.
- The best non-C row in this first-20 table is `Positive-only NN top40` at `17/20`.
- The conservative mask preserves broad context but does not beat the positive-only anchor on this split.
- Do not scale this Candidate C recipe unchanged. The remaining headroom is more likely in explicit action-negative regularization or a better confidence-preserving router than in this mask alone.

## Per-Initial Counts

| initial | positive | weighted | v0.1 | union | cand A | router no-bias | router anchor | cand C e100 | cand C e200 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| demo_5 | 2 | 0 | 2 | 1 | 1 | 2 | 2 | 2 | 2 |
| demo_29 | 2 | 1 | 2 | 0 | 1 | 2 | 1 | 0 | 1 |
| demo_39 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| demo_45 | 2 | 1 | 2 | 0 | 0 | 2 | 2 | 1 | 2 |
| demo_53 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_81 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_89 | 2 | 1 | 2 | 0 | 2 | 2 | 2 | 0 | 2 |
| demo_99 | 1 | 1 | 1 | 0 | 1 | 2 | 2 | 0 | 1 |
| demo_105 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 2 |
| demo_189 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_c_endpoint_screen_summary.csv`.
- Per-initial CSV: `results/candidate_breakthrough/candidate_c_endpoint_screen_per_initial.csv`.
- Epoch-100 eval report: `results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch100/REPORT.md`.
- Epoch-200 eval report: `results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch200/REPORT.md`.
- Preflight report: `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_preflight_REPORT.md`.
