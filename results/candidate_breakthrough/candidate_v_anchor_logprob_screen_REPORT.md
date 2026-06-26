# Candidate V Output-Anchor Fine-Tuning Screen

**Status: failed first frozen validation.** Candidate V
uses positive-only initialization, Candidate C sequence-mask weights, and
a frozen-policy output anchor: the fine-tuned policy is penalized when it
assigns lower log-probability than the initialized policy on high-weight
timesteps.

## Can Split Results

| split | protocol | group | method | train_epochs | successes | avg_len | delta_vs_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 404 | first20 | baseline | positive_only_nn_top40 |  | 17/20 | 148.2 | 0 |
| 404 | first20 | candidate_v_anchor_logprob | model_epoch_5 | 5 | 15/20 | 180.6 | -2 |
| 404 | first20 | candidate_v_anchor_logprob | model_epoch_10 | 10 | 18/20 | 135.6 | 1 |
| 404 | first20 | candidate_v_anchor_logprob | model_epoch_15 | 15 | 15/20 | 179.1 | -2 |
| 404 | first20 | candidate_v_anchor_logprob | model_epoch_20 | 20 | 16/20 | 164.2 | -1 |
| 404 | eval50 | baseline | positive_only_nn_top40 |  | 39/50 | 169.3 | 0 |
| 404 | eval50 | baseline | weighted_bc_full_pool |  | 33/50 | 208.9 | -6 |
| 404 | eval50 | router_reference | candidate_e_initial_gate_weighted_e200 |  | 46/50 | 130.3 | 7 |
| 404 | eval50 | candidate_v_anchor_logprob | model_epoch_10 | 10 | 39/50 | 170.2 | 0 |
| 505 | first20 | baseline | positive_only_nn_top40 |  | 15/20 |  | 0 |
| 505 | first20 | baseline | weighted_bc_full_pool |  | 12/20 |  | -3 |
| 505 | first20 | router_reference | candidate_e_initial_gate_weighted_e200 |  | 16/20 |  | 1 |
| 505 | first20 | candidate_v_anchor_logprob | model_epoch_10 | 10 | 16/20 | 170.2 | 1 |
| 505 | eval50 | baseline | positive_only_nn_top40 |  | 40/50 |  | 0 |
| 505 | eval50 | baseline | weighted_bc_full_pool |  | 30/50 |  | -10 |
| 505 | eval50 | router_reference | candidate_e_initial_gate_weighted_e200 |  | 39/50 |  | -1 |
| 505 | eval50 | candidate_v_anchor_logprob | model_epoch_10 | 10 | 38/50 | 180.4 | -2 |

## Read

- Best first-20 Candidate V checkpoint: epoch `10` at `18/20`,
  which is `+1/20` over the positive-only anchor and above previous
  training-side screens on this gate.
- The split-404 50-episode check for that checkpoint is `39/50`,
  exactly tied with positive-only `39/50` and below the Candidate E router
  reference `46/50`.
- Frozen split-505 validation reaches `38/50`,
  below positive-only `40/50` despite passing the first-20 stability check
  (`16/20` versus positive-only `15/20`).
- Candidate V is therefore not a scalable breakthrough. It remains useful
  evidence that output anchoring is a better direction than parameter L2,
  but it fails the first non-404 validation gate.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_v_anchor_logprob_screen_summary.csv`.
- Split-404 first-20 eval report: `results/candidate_breakthrough/candidate_v_anchor_logprob_can404_w10_e20_eval20/REPORT.md`.
- Split-404 50-episode eval report: `results/candidate_breakthrough/candidate_v_anchor_logprob_can404_w10_e10_eval50/REPORT.md`.
- Split-505 first-20 eval report: `results/candidate_breakthrough/candidate_v_anchor_logprob_can505_w10_e10_eval20/REPORT.md`.
- Split-505 50-episode eval report: `results/candidate_breakthrough/candidate_v_anchor_logprob_can505_w10_e10_eval50/REPORT.md`.
- Failure analysis: `results/candidate_breakthrough/candidate_v_failure_analysis_REPORT.md`.
- Split-404 train directory: `results/candidate_breakthrough/candidate_v_anchor_logprob_can404_w10_e20_train/candidate_v_anchor_logprob_can404_w10_e20/20260626100527`.
- Split-505 train directory: `results/candidate_breakthrough/candidate_v_anchor_logprob_can505_w10_e20_train/candidate_v_anchor_logprob_can505_w10_e20/20260626101921`.
- Validation freeze: `METHOD_FREEZE_CANDIDATE_V.md`.
- Split-404 init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`.
- Split-404 transition weights: `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.
- Split-505 init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/train/can_paired_pos40_bad80_split505_positive_only_nn_policy0_official_bc_rnn/20260625144918/models/model_epoch_200.pth`.
- Split-505 transition weights: `results/candidate_breakthrough/candidate_v_split505_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.
