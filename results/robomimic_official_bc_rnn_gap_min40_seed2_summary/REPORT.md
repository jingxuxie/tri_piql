# Official Robomimic Coverage-Floor Score-Gap Seed-2

This run tests a coverage-aware score-gap variant on the seed-2 failure case. The original largest-gap cutoff selected only 9 unlabeled demos and failed; this variant keeps the same score-gap rule but requires at least 40 selected unlabeled demos before searching for a gap.

Common setup:

- Dataset split: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
- Environment: `PickPlaceCan` version `1.5.1`.
- Policy backbone: official Robomimic `BC_RNN_GMM`.
- Actor head: Robomimic default MLP head, `1024,1024`.
- RNN: 2-layer LSTM, hidden dim 400, sequence length 10.
- GMM modes: 5.
- Optimization budget: 200 epochs x 100 steps = 20k gradient steps.
- Evaluation: 10 held-out positive initial states, horizon 400, CUDA policy inference.

## Support Sets

| source | train demos | selected unlabeled demos | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|
| original score-gap | 19 | 9 | 9 | 0 | 1.000 |
| score-gap min40 | 76 | 66 | 65 | 1 | 0.985 |
| fixed top-80 | 90 | 80 | 74 | 6 | 0.925 |

The min40 coverage floor keeps most of the top-ranked hidden-positive support while excluding most of the hidden-bad demos added by fixed top-80.

## Rollout Metrics

| source | checkpoint epoch | approx gradient steps | success | avg return | avg length |
|---|---:|---:|---:|---:|---:|
| original score-gap | 50 | 5k | 0.000 | 0.000 | 400.0 |
| original score-gap | 100 | 10k | 0.000 | 0.000 | 400.0 |
| original score-gap | 150 | 15k | 0.100 | 0.100 | 372.0 |
| original score-gap | 200 | 20k | 0.000 | 0.000 | 400.0 |
| score-gap min40 | 50 | 5k | 0.100 | 0.100 | 370.8 |
| score-gap min40 | 100 | 10k | 0.900 | 0.900 | 149.3 |
| score-gap min40 | 150 | 15k | 0.900 | 0.900 | 140.4 |
| score-gap min40 | 200 | 20k | 0.900 | 0.900 | 140.5 |
| fixed top-80 | 50 | 5k | 0.200 | 0.200 | 343.7 |
| fixed top-80 | 100 | 10k | 0.600 | 0.600 | 223.6 |
| fixed top-80 | 150 | 15k | 0.700 | 0.700 | 198.9 |
| fixed top-80 | 200 | 20k | 0.900 | 0.900 | 137.0 |

## Artifacts

- Coverage-floor setup: `results/robomimic_official_bc_rnn_gap_min40_seed2_mlphead_setup/REPORT.md`.
- Coverage-floor evaluation: `results/robomimic_official_bc_rnn_gap_min40_seed2_mlphead_eval/REPORT.md`.
- Original score-gap setup/eval:
  - `results/robomimic_official_bc_rnn_gap_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_gap_seed2_mlphead_eval/REPORT.md`
- Fixed top-80 setup/eval:
  - `results/robomimic_official_bc_rnn_top80_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top80_seed2_mlphead_eval/REPORT.md`

## Interpretation

- The coverage floor fixes the seed-2 score-gap failure: success improves from 0.100 best to 0.900 at 10k/15k/20k.
- Compared with fixed top-80, min40 reaches the same best success while using cleaner support: 1 hidden-bad selected demo instead of 6.
- This is a better candidate method than the original largest-gap cutoff: it explicitly trades off purity and coverage using only labeled positives, labeled negatives, and unlabeled classifier scores.
- It still needs more seeds and ideally a rule for choosing the minimum support floor without peeking at hidden labels or rollout success.
