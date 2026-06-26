# Candidate V Failure Analysis

This report compares Candidate V against positive-only, weighted BC, triage,
and the Candidate E router by held-out initial state on Can splits 404 and
505. Counts are successes over the 5 repeated rollouts for each validation
initial.

## Aggregate

| split | positive | weighted | triage | candidate_e | candidate_v | oracle_positive_v | oracle_positive_e_v | candidate_v_delta_vs_positive | candidate_v_unique_gain_over_positive | candidate_v_unique_gain_over_pos_e |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 404 | 39/50 | 33/50 | 36/50 | 46/50 | 39/50 | 42/50 | 48/50 | 0 | 3 | 2 |
| 505 | 40/50 | 30/50 | 36/50 | 39/50 | 38/50 | 43/50 | 45/50 | -2 | 3 | 0 |
| total | 79/100 | 63/100 | 72/100 | 85/100 | 77/100 | 85/100 | 93/100 | -2 | 6 | 2 |

## Worst Candidate V Regressions

| split | initial_demo_id | positive | candidate_e | candidate_v | candidate_v_delta_vs_positive | initial_anchor_pos_dist_mean | candidate_e_gate_opens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 404 | demo_189 | 3/5 | 3/5 | 1/5 | -2 | 1.675 | 0 |
| 505 | demo_45 | 5/5 | 4/5 | 3/5 | -2 | 0.984 | 0 |
| 505 | demo_89 | 2/5 | 3/5 | 0/5 | -2 | 2.007 | 0 |
| 404 | demo_29 | 4/5 | 5/5 | 3/5 | -1 | 1.338 | 0 |
| 505 | demo_53 | 5/5 | 5/5 | 4/5 | -1 | 3.087 | 5 |
| 404 | demo_5 | 5/5 | 5/5 | 5/5 | 0 | 1.382 | 0 |

## Candidate V Unique Gains Over Positive

| split | initial_demo_id | positive | candidate_e | candidate_v | candidate_v_unique_gain_over_positive | candidate_v_unique_gain_over_pos_e | initial_anchor_pos_dist_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 505 | demo_189 | 0/5 | 3/5 | 2/5 | 2 | 0 | 1.716 |
| 404 | demo_81 | 4/5 | 5/5 | 5/5 | 1 | 0 | 0.804 |
| 404 | demo_89 | 4/5 | 4/5 | 5/5 | 1 | 1 | 2.586 |
| 404 | demo_99 | 4/5 | 4/5 | 5/5 | 1 | 1 | 1.251 |
| 505 | demo_5 | 4/5 | 5/5 | 5/5 | 1 | 0 | 1.297 |

## Read

- Candidate V does not solve the split-404 `demo_39` coverage gap: it is
  `0/5`, while Candidate E routes that initial to weighted BC and reaches
  `5/5`.
- Candidate V's aggregate unique gain over positive-only is small and is
  not unique once Candidate E is available.
- The split-505 validation failure is concentrated in recurring anchor
  regressions, especially `demo_89`, where Candidate V is `0/5`.
- This supports stopping Candidate V unchanged. The core unsolved problem
  is not just preserving log-probability on high-weight training timesteps;
  it is identifying state-specific weighted-coverage rescue cases without
  damaging strong positive anchors.

## Artifacts

- Per-initial CSV: `results/candidate_breakthrough/candidate_v_failure_analysis_per_initial.csv`.
- Summary CSV: `results/candidate_breakthrough/candidate_v_failure_analysis_summary.csv`.
