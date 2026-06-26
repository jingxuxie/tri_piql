# Candidate F Can606 Fresh Smoke

**Status: neutral fresh Can no-tail check.** Candidate F would use the
Candidate E initial-distance gate on Can606 because the positive-NN
selected support has no classifier-probability tail in the fresh
preflight.

Split seed: `606`. Eval protocol: `20` valid-positive
starts, horizon `400`, policy seed `0`, epoch `200` checkpoints.

## Results

| method | successes | avg_len | gate_opens | artifact |
| --- | --- | --- | --- | --- |
| positive_only_nn | 16/20 | 163.95 |  | results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20 |
| weighted_bc | 14/20 | 197.75 |  | results/candidate_g_fresh_preflight/can606_weighted_epoch200_eval20 |
| candidate_e_gate | 16/20 | 161.85 | 2 | results/candidate_g_fresh_preflight/can606_candidate_e_gate_eval20 |

## Read

- Candidate E gate ties positive-only on this fresh no-tail Can split:
  both reach `16/20`.
- Weighted BC is weaker at `14/20`.
- The gate opens on `2/20` episodes, both for the repeated `demo_39`
  initial state. This does not create a net first-20 improvement.
- This is not a Candidate F validation win, but it is also not a fresh
  Can no-tail failure. A 50-episode continuation is only worth running
  as part of a broader fresh Can-only matrix.

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_f_can606_fresh_smoke_summary.csv`.
- Positive-only eval: `results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20/REPORT.md`.
- Weighted eval: `results/candidate_g_fresh_preflight/can606_weighted_epoch200_eval20/REPORT.md`.
- Candidate E gate eval: `results/candidate_g_fresh_preflight/can606_candidate_e_gate_eval20/REPORT.md`.
