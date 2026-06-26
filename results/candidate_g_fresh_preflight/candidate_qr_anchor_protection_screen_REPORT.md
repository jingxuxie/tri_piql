# Candidate Q/R Anchor-Protection Screens

**Status: rejected at the Lift606 development gate.** These screens
test whether the failed positive-anchor union can be rescued by either
very short fine-tuning or post-hoc interpolation back toward the
positive-only anchor.

## Lift606 First-20 Results

| group | method | successes | avg_len |
| --- | --- | --- | --- |
| baseline | positive_only_nn | 14/20 | 70.25 |
| baseline | triage_bc | 13/20 | 78.45 |
| baseline | weighted_bc | 6/20 | 124.75 |
| baseline | initial_confidence_q25 | 18/20 | 44.8 |
| baseline | candidate_p_epoch20_posinit_finetune | 11/20 | 94.25 |
| candidate_q_short_finetune | model_epoch_1 | 10/20 | 90.4 |
| candidate_q_short_finetune | model_epoch_2 | 10/20 | 89.8 |
| candidate_q_short_finetune | model_epoch_3 | 9/20 | 96.3 |
| candidate_q_short_finetune | model_epoch_4 | 11/20 | 84.4 |
| candidate_q_short_finetune | model_epoch_5 | 10/20 | 91.7 |
| candidate_r_interpolation | pos_to_anchor_union_p20_alpha_0p05 | 11/20 | 86.45 |
| candidate_r_interpolation | pos_to_anchor_union_p20_alpha_0p10 | 10/20 | 89.35 |
| candidate_r_interpolation | pos_to_anchor_union_p20_alpha_0p20 | 10/20 | 92.45 |
| candidate_r_interpolation | pos_to_anchor_union_p20_alpha_0p35 | 10/20 | 93.8 |

## Read

- Candidate Q finds no early fine-tuning sweet spot. Epochs `1` through
  `5` reach `10/20`, `10/20`, `9/20`, `11/20`, and `10/20`.
- Candidate R finds no useful small parameter move from the positive-only
  checkpoint toward the 20-epoch anchor-union fine-tune. Alphas `0.05`,
  `0.10`, `0.20`, and `0.35` reach `11/20`, `10/20`, `10/20`, and
  `10/20`.
- The anchor-union line should stop. Positive initialization, shorter
  fine-tuning, and checkpoint interpolation all fail to beat the
  positive-only NN baseline (`14/20`).

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_qr_anchor_protection_screen_summary.csv`.
- Candidate Q eval: `results/candidate_g_fresh_preflight/candidate_q_lift606_short_anchor_union/eval20_epochs1to5/REPORT.md`.
- Candidate R eval: `results/candidate_g_fresh_preflight/candidate_r_lift606_checkpoint_interpolation/eval20_p20_alphas/REPORT.md`.
- Candidate R interpolation manifest: `results/candidate_g_fresh_preflight/candidate_r_lift606_checkpoint_interpolation/checkpoints/pos_to_anchor_union_p20_manifest.json`.
