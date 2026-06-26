# Candidate P Positive-Initialized Anchor-Union Screen

**Status: rejected at the Lift606 development gate.** Candidate P
tests whether starting from the positive-only policy can prevent the
Candidate O anchor-union training collapse.

## Training Recipe

- Initialize BC-RNN-GMM policy weights from the Lift606 positive-only NN
  epoch-200 checkpoint.
- Fine-tune for `20` epochs x `100` steps on the Candidate O
  positive-anchor union training set.
- Loss weights match Candidate O: labeled positives and positive-NN
  selected demos `1.0`, triage-only extras `0.25`.
- Evaluate the epoch-20 checkpoint on the same Lift606 first-20
  valid-positive starts used by the recent router and training-side
  screens.

## Lift606 First-20 Results

| method | successes | avg_len |
| --- | --- | --- |
| positive_only_nn | 14/20 | 70.25 |
| triage_bc | 13/20 | 78.45 |
| weighted_bc | 6/20 | 124.75 |
| initial_confidence_q25 | 18/20 | 44.8 |
| candidate_o_epoch50_from_scratch | 1/20 | 147.35 |
| candidate_o_epoch100_from_scratch | 5/20 | 120.5 |
| candidate_p_epoch20_posinit_finetune | 11/20 | 94.25 |

## Read

- Positive initialization prevents the severe from-scratch Candidate O
  collapse, improving from `5/20` at Candidate O epoch 100 to `11/20`.
- The fine-tune still damages the positive-only anchor behavior:
  Candidate P is below positive-only (`14/20`), triage (`13/20`), and
  the initial confidence q25 router (`18/20`).
- Do not continue this anchor-union fine-tune recipe to a longer run.
  The failure mode is not just random initialization; admitting the
  triage-only extras with a constant positive loss still moves the
  policy in the wrong direction.

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_p_posinit_anchor_union_screen_summary.csv`.
- Candidate P eval: `results/candidate_g_fresh_preflight/candidate_p_lift606_posinit_anchor_union/eval20_epoch20/REPORT.md`.
- Candidate P checkpoint: `results/candidate_g_fresh_preflight/candidate_p_lift606_posinit_anchor_union/train/candidate_p_lift606_posinit_anchor_union_e20_seed0/20260626071736/models/model_epoch_20.pth`.
- Candidate O comparison report: `results/candidate_g_fresh_preflight/candidate_o_lift_anchor_union_screen_REPORT.md`.
