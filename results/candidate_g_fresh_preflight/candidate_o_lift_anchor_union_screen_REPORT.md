# Candidate O Lift Positive-Anchor Union Screen

**Status: rejected at the Lift606 development gate.** Candidate O is a
training-side attempt to preserve positive-only behavior while admitting
extra triage support at low loss weight.

## Training Recipe

- Train demos: `243`.
- Positive-NN selected unlabeled demos: `160`.
- Triage selected unlabeled demos: `176`.
- Triage-only extra demos: `73`.
- Loss weights: labeled positives and positive-NN selected demos `1.0`,
  triage-only extras `0.25`.
- Training budget: `100` epochs x `100` steps, with epoch `50` and `100`
  checkpoints evaluated.

## Lift606 First-20 Results

| method | successes | avg_len |
| --- | --- | --- |
| positive_only_nn | 14/20 | 70.25 |
| triage_bc | 13/20 | 78.45 |
| weighted_bc | 6/20 | 124.75 |
| initial_confidence_q25 | 18/20 | 44.8 |
| candidate_o_epoch50 | 1/20 | 147.35 |
| candidate_o_epoch100 | 5/20 | 120.5 |

## Read

- Candidate O collapses below every relevant Lift606 baseline.
- The low-weight triage extras do not act like a harmless coverage
  regularizer; the policy loses most positive-only anchor behavior by
  epoch 50 and remains weak by epoch 100.
- Do not continue this constant-demo-weight union recipe to 200 epochs.
  A future training-side attempt needs either stronger anchor protection
  or a different loss, not simply adding triage support at a smaller
  constant weight.

## Artifacts

- Preflight report: `results/candidate_g_fresh_preflight/candidate_o_lift606_positive_anchor_union/candidate_o_lift_anchor_union_preflight_REPORT.md`.
- Summary CSV: `results/candidate_g_fresh_preflight/candidate_o_lift_anchor_union_screen_summary.csv`.
- Epoch 50 eval: `results/candidate_g_fresh_preflight/candidate_o_lift606_positive_anchor_union/eval20_epoch50/REPORT.md`.
- Epoch 100 eval: `results/candidate_g_fresh_preflight/candidate_o_lift606_positive_anchor_union/eval20_epoch100/REPORT.md`.
