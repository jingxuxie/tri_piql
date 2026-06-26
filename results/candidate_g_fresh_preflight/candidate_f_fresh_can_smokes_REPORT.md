# Candidate F Fresh Can Smoke Checks

**Status: neutral.** These first-20 held-out Can checks are useful for
stress-testing the Can-only Candidate F story, but they do not yet
strengthen it into a fresh validation claim.

Candidate F choices under the frozen Can rule:

- Can606 no-tail: Candidate E gate.
- Can707 mild-tail: weighted BC.

## Per-Split Rows

| split | method | candidate_f_selected | successes | avg_len | artifact |
| --- | --- | --- | --- | --- | --- |
| 606 | positive_only_nn | 0 | 16/20 | 163.95 | results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20 |
| 606 | weighted_bc | 0 | 14/20 | 197.75 | results/candidate_g_fresh_preflight/can606_weighted_epoch200_eval20 |
| 606 | candidate_e_gate | 1 | 16/20 | 161.85 | results/candidate_g_fresh_preflight/can606_candidate_e_gate_eval20 |
| 707 | positive_only_nn | 0 | 15/20 | 181.9 | results/candidate_g_fresh_preflight/can707_positive_epoch200_eval20 |
| 707 | weighted_bc | 1 | 15/20 | 183.55 | results/candidate_g_fresh_preflight/can707_weighted_epoch200_eval20 |
| 707 | triage_bc | 0 | 10/20 | 251.85 | results/candidate_g_fresh_preflight/can707_triage_epoch200_eval20 |
| 707 | candidate_e_gate | 0 | 13/20 | 209.55 | results/candidate_g_fresh_preflight/can707_candidate_e_gate_eval20 |

## Two-Split First-20 Aggregate

| method | successes |
| --- | --- |
| candidate_f | 31/40 |
| positive_only_nn | 31/40 |
| candidate_e_gate | 29/40 |
| weighted_bc | 29/40 |
| triage_bc | 10/20 |

## Read

- Candidate F ties positive-only over the two fresh Can first-20 smokes:
  both are `31/40`.
- The Can606 no-tail branch is neutral: Candidate E gate and positive-only
  both reach `16/20`.
- The Can707 mild-tail branch is also neutral: weighted BC and
  positive-only both reach `15/20`; Candidate E is worse at `13/20` and
  triage is worse at `10/20`.
- This weakens the case for spending broad endpoint budget on Candidate F
  as a high-impact fresh Can method. If continued, it should be a
  predeclared Can-only validation matrix, not another ad hoc split.

## Artifacts

- Row CSV: `results/candidate_g_fresh_preflight/candidate_f_fresh_can_smokes_rows.csv`.
- Summary CSV: `results/candidate_g_fresh_preflight/candidate_f_fresh_can_smokes_summary.csv`.
- Can606 report: `results/candidate_g_fresh_preflight/candidate_f_can606_fresh_smoke_REPORT.md`.
- Can707 weighted eval: `results/candidate_g_fresh_preflight/can707_weighted_epoch200_eval20/REPORT.md`.
- Can707 branch comparison: `results/candidate_g_fresh_preflight/candidate_i_can_mild_positive_REPORT.md`.
