# Candidate W Two-Feature Gate

Candidate W is a frozen deploy-time variant of Candidate E. It uses
positive-only by default and forces weighted BC for the full episode only
when the initial positive-policy action has positive-support distance
`> 3.0` and positive margin over negative support `> 0.0`.

## Aggregate

| split | positive | weighted | triage | candidate_e | candidate_v | candidate_w | candidate_w_delta_vs_positive | candidate_w_delta_vs_candidate_e | candidate_w_unique_gain_over_positive | candidate_w_unique_gain_over_pos_e | candidate_w_gate_opens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 404 | 39/50 | 33/50 | 36/50 | 46/50 | 39/50 | 46/50 | 7 | 0 | 7 | 0 | 5 |
| 505 | 40/50 | 30/50 | 36/50 | 39/50 | 38/50 | 39/50 | -1 | 0 | 2 | 1 | 5 |
| total | 79/100 | 63/100 | 72/100 | 85/100 | 77/100 | 85/100 | 6 | 0 | 9 | 1 | 10 |

## Gate Open Initials

| split | initial_demo_id | positive | weighted | candidate_e | candidate_w | candidate_w_gate_opens | initial_anchor_pos_dist_mean | initial_anchor_margin_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 404 | demo_39 | 0/5 | 3/5 | 5/5 | 5/5 | 5 | 3.180 | 0.119 |
| 505 | demo_39 | 4/5 | 5/5 | 4/5 | 5/5 | 5 | 3.426 | 0.258 |

## Candidate W Regressions

| split | initial_demo_id | positive | candidate_e | candidate_w | candidate_w_delta_vs_positive | candidate_w_delta_vs_candidate_e | candidate_w_gate_opens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 505 | demo_5 | 4/5 | 5/5 | 3/5 | -1 | -2 | 0 |
| 505 | demo_89 | 2/5 | 3/5 | 1/5 | -1 | -2 | 0 |
| 505 | demo_45 | 5/5 | 4/5 | 4/5 | -1 | 0 | 0 |
| 404 | demo_5 | 5/5 | 5/5 | 5/5 | 0 | 0 | 0 |
| 404 | demo_45 | 5/5 | 5/5 | 5/5 | 0 | 0 | 0 |
| 404 | demo_53 | 5/5 | 5/5 | 5/5 | 0 | 0 | 0 |
| 404 | demo_89 | 4/5 | 4/5 | 4/5 | 0 | 0 | 0 |
| 404 | demo_99 | 4/5 | 4/5 | 4/5 | 0 | 0 | 0 |

## Candidate W Gains Over Positive

| split | initial_demo_id | positive | candidate_e | candidate_w | candidate_w_unique_gain_over_positive | candidate_w_unique_gain_over_pos_e | candidate_w_gate_opens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 404 | demo_39 | 0/5 | 5/5 | 5/5 | 5 | 0 | 5 |
| 404 | demo_29 | 4/5 | 5/5 | 5/5 | 1 | 0 | 0 |
| 404 | demo_81 | 4/5 | 5/5 | 5/5 | 1 | 0 | 0 |
| 505 | demo_39 | 4/5 | 4/5 | 5/5 | 1 | 1 | 5 |
| 505 | demo_189 | 0/5 | 3/5 | 1/5 | 1 | 0 | 0 |

## Read

- Candidate W keeps the split-404 `demo_39` rescue and improves split 404
  to `46/50`, matching Candidate E on that split.
- Candidate W closes Candidate E's harmful split-505 `demo_29` gate, but
  still reaches only `39/50` on split 505, below positive-only `40/50`.
- Aggregate Candidate W is `85/100`, tying Candidate E and staying below
  the positive-or-Candidate-E-or-Candidate-V per-initial oracle `93/100`.
- The two-feature gate is therefore a useful diagnostic but not a new
  paper-facing method. The remaining gap requires a more stable
  state-conditional policy-quality signal, not another scalar initial
  support threshold.

## Artifacts

- Per-initial CSV: `results/candidate_breakthrough/candidate_w_two_feature_gate_per_initial.csv`.
- Summary CSV: `results/candidate_breakthrough/candidate_w_two_feature_gate_summary.csv`.
- Split-404 eval: `results/candidate_breakthrough/candidate_w_two_feature_gate_split404_eval50/REPORT.md`.
- Split-505 eval: `results/candidate_breakthrough/candidate_w_two_feature_gate_split505_eval50/REPORT.md`.
