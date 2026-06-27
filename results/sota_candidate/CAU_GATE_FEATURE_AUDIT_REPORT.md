# CAU Gate Feature Audit

This audit asks whether existing hidden-label-free initial-state features can decide when to use CAU action-conflict instead of positive-only NN.
It uses completed split 303 / 404 / 505 first-20 screens and is development evidence only.

## Per-Split Headroom

| split | positive | CAU alone | positive/CAU oracle | CAU gains | CAU losses |
| --- | ---: | ---: | ---: | ---: | ---: |
| 303 | 15/20 | 17/20 | 17/20 | 2 | 0 |
| 404 | 17/20 | 16/20 | 19/20 | 2 | 3 |
| 505 | 15/20 | 15/20 | 16/20 | 1 | 1 |

## Best Pooled Development Gate

- Gate: `initial_anchor_pos_dist_mean le 1.273665 or initial_anchor_neg_dist_mean gt 3.131861`.
- Pooled development result: routed `51/60` versus positive-only `47/60`, CAU alone `48/60`, gains `4`, losses `0`.

## Leave-One-Split-Out Check

| held-out split | train routed | train losses | held-out routed | held-out losses | gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 303 | 35/40 | 0 | 16/20 | 0 | `initial_anchor_pos_dist_mean le 1.273665 or initial_anchor_neg_dist_mean gt 2.939165` |
| 404 | 33/40 | 0 | 17/20 | 1 | `initial_anchor_pos_dist_mean le 0.895210 or initial_anchor_neg_dist_mean gt 2.270789` |
| 505 | 35/40 | 0 | 16/20 | 0 | `initial_anchor_pos_dist_mean le 1.273665 or initial_anchor_neg_dist_mean gt 3.131861` |

## Decision

- The pooled gate is promising enough for one frozen fresh validation, but it is not paper evidence because it is selected on completed screens.
- Leave-one-split-out is fragile: the held-out split-404 check preserves total successes but incurs an anchor loss.
- Freeze the pooled two-feature gate for the next unused split only; stop immediately if the fresh screen has any anchor loss or no gain.

## Outputs

- Per-split CSV: `results/sota_candidate/cau_gate_feature_audit_per_split.csv`.
- Leave-one-split-out CSV: `results/sota_candidate/cau_gate_feature_audit_loso.csv`.
- Pooled gate CSV: `results/sota_candidate/cau_gate_feature_audit_pooled_gate.csv`.
