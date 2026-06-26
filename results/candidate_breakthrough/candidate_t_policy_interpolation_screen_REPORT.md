# Candidate T Policy-Interpolation Screen

**Status: rejected at the Can split-404 first-20 gate.** Candidate T
tests whether a small policy-space move from the positive-only checkpoint
toward the weighted-BC checkpoint can preserve anchor behavior while
absorbing broad-coverage behavior, without a rollout-time router.

## Can Split-404 First-20 Results

| group | method | alpha | successes | avg_len | delta_vs_positive |
| --- | --- | --- | --- | --- | --- |
| baseline | positive_only_nn_top40 |  | 17/20 | 148.2 | 0 |
| baseline | weighted_bc_full_pool | 1.00 | 13/20 | 211.5 | -4 |
| candidate_t_interpolation | pos_to_weighted_alpha_0p05 | 0.05 | 16/20 | 168.0 | -1 |
| candidate_t_interpolation | pos_to_weighted_alpha_0p10 | 0.10 | 13/20 | 211.7 | -4 |
| candidate_t_interpolation | pos_to_weighted_alpha_0p20 | 0.20 | 3/20 | 358.8 | -14 |

## Read

- The positive-only anchor is `17/20` on the matched first-20 protocol.
- The best interpolation is alpha `0.05` at `16/20`; alpha `0.10` falls
  to `13/20`, and alpha `0.20` collapses to `3/20`.
- This rejects naive policy-space interpolation as an anchor-preserving
  way to combine positive-only and weighted-coverage behavior on the
  known split-404 bottleneck.
- A future training-side candidate needs an explicit objective that
  preserves the anchor policy locally; simple parameter averaging is not
  enough.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_t_policy_interpolation_screen_summary.csv`.
- Eval report: `results/candidate_breakthrough/candidate_t_policy_interpolation_can404/eval20/REPORT.md`.
- Interpolation manifest: `results/candidate_breakthrough/candidate_t_policy_interpolation_can404/pos_to_weighted_manifest.json`.
- Base checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`.
- Target checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/train/can_paired_pos40_bad80_split404_weighted_bc_policy0_official_bc_rnn/20260625143118/models/model_epoch_200.pth`.
