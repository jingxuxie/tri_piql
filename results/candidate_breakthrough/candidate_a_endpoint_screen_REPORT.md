# Candidate A Endpoint Screen

This report summarizes the transition-weighted Candidate A screen on the Can 40p/80b split-404 failure case.

## 50-Episode Comparison

| method | support hidden pos/bad | success | rate | avg len |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 35/5 | 39/50 | 0.780 | 169.3 |
| Weighted BC full pool | 40/80 | 33/50 | 0.660 | 208.9 |
| TRIAGE-BC v0.1 hard support | 33/26 | 36/50 | 0.720 | 190.8 |
| v0.2 positive-NN/risk union top40 | 39/5 | 27/50 | 0.540 | 248.4 |
| Candidate A transition-weighted | 39/5 | 30/50 | 0.600 | 224.2 |

## Read

- Candidate A reaches `30/50`, which is `+3` versus the v0.2 hard union but `-3` versus weighted BC, `-6` versus v0.1, and `-9` versus positive-only NN.
- The current transition-weight recipe is therefore an improvement over hard union, not a breakthrough.
- The result argues against scaling this Candidate A recipe unchanged; the next attempt should change the recipe or move to Candidate C/B.

## First-20 Training-Length Screen

| method | epochs | success | rate |
| --- | ---: | ---: | ---: |
| Positive-only NN top40 | 200 | 17/20 | 0.850 |
| Weighted BC full pool | 200 | 13/20 | 0.650 |
| TRIAGE-BC v0.1 hard support | 200 | 14/20 | 0.700 |
| v0.2 positive-NN/risk union top40 | 200 | 7/20 | 0.350 |
| Candidate A transition-weighted e50 | 50 | 1/20 | 0.050 |
| Candidate A transition-weighted e100 | 100 | 9/20 | 0.450 |
| Candidate A transition-weighted e200 | 200 | 12/20 | 0.600 |

## Per-Initial 50-Episode Counts

| initial | positive-only | weighted | v0.1 | union | candidate A |
| --- | ---: | ---: | ---: | ---: | ---: |
| demo_5 | 5 | 1 | 5 | 4 | 4 |
| demo_29 | 4 | 4 | 4 | 2 | 1 |
| demo_39 | 0 | 3 | 1 | 1 | 3 |
| demo_45 | 5 | 1 | 3 | 2 | 0 |
| demo_53 | 5 | 5 | 5 | 5 | 5 |
| demo_81 | 4 | 5 | 5 | 5 | 5 |
| demo_89 | 4 | 3 | 4 | 0 | 4 |
| demo_99 | 4 | 2 | 4 | 1 | 3 |
| demo_105 | 5 | 5 | 4 | 4 | 5 |
| demo_189 | 3 | 4 | 1 | 3 | 0 |

## Artifacts

- 50-episode summary CSV: `results/candidate_breakthrough/candidate_a_endpoint_screen_summary.csv`.
- First-20 screen CSV: `results/candidate_breakthrough/candidate_a_endpoint_screen_first20.csv`.
- Per-initial CSV: `results/candidate_breakthrough/candidate_a_endpoint_screen_per_initial.csv`.
- Candidate A 50-episode eval report: `results/candidate_breakthrough/candidate_a_tw_can404_e200_eval50/REPORT.md`.
