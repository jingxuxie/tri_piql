# Candidate U Anchor-L2 Fine-Tuning Screen

**Status: neutral/rejected at the Can split-404 first-20 gate.** Candidate U
tests whether positive-only initialization plus explicit parameter-space
anchor regularization can preserve the positive-only policy while adding
Candidate C sequence-mask coverage.

## Can Split-404 First-20 Results

| group | method | train_epochs | successes | avg_len | delta_vs_positive |
| --- | --- | --- | --- | --- | --- |
| baseline | positive_only_nn_top40 | 200 | 17/20 | 148.2 | 0 |
| baseline | weighted_bc_full_pool | 200 | 13/20 | 211.5 | -4 |
| previous_candidate | candidate_c_sequence_mask_e200 | 200 | 16/20 | 167.7 | -1 |
| candidate_u_anchor_l2 | model_epoch_5 | 5 | 17/20 | 149.2 | 0 |
| candidate_u_anchor_l2 | model_epoch_10 | 10 | 16/20 | 163.9 | -1 |
| candidate_u_anchor_l2 | model_epoch_15 | 15 | 14/20 | 194.2 | -3 |
| candidate_u_anchor_l2 | model_epoch_20 | 20 | 16/20 | 160.8 | -1 |

## Read

- The positive-only anchor is `17/20` on the matched first-20 protocol.
- The best Candidate U checkpoint is epoch `5` at `17/20`, matching but
  not improving over the positive-only anchor.
- Later checkpoints degrade to `16/20`, `14/20`, and `16/20`, so the
  extra sequence-mask fine-tuning does not create robust endpoint gain.
- This rejects normalized parameter-L2 anchoring as the needed
  preservation mechanism. If this line is revisited, it should use a
  local output/distribution anchor on positive states, not only parameter
  drift.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_u_anchor_l2_screen_summary.csv`.
- Eval report: `results/candidate_breakthrough/candidate_u_anchor_l2_can404_w1000_e20_eval20/REPORT.md`.
- Train directory: `results/candidate_breakthrough/candidate_u_anchor_l2_can404_w1000_e20_train/candidate_u_anchor_l2_can404_w1000_e20/20260626095223`.
- Init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`.
- Transition weights: `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.
