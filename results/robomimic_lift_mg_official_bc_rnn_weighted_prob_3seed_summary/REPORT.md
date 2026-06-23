# Robomimic Lift MG Official BC-RNN-GMM Weighted BC Baseline

Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.

Split: `results/robomimic_inspection/lift_mg_low_dim_sparse/split_indices.json`.

Protocol:

- Official Robomimic BC-RNN-GMM backbone.
- `1024,1024` actor head, 2-layer LSTM with hidden size `400`, 5 GMM modes.
- `20,000` optimizer steps, saved at `5k / 10k / 15k / 20k`.
- Evaluation uses `10` held-out reward-positive Lift initial states and horizon `150`.
- Training support is `10` labeled-positive demos plus all `1420` unlabeled demos.
- Demo-level sampler weights are classifier probabilities, clipped at floor `0.05`; labeled positives have weight `1.0`.

## Demo Weights

| seed | demo weight mean | hidden-positive weight mean | hidden-bad weight mean |
|---:|---:|---:|---:|
| 0 | 0.283 | 0.755 | 0.163 |
| 1 | 0.285 | 0.761 | 0.164 |
| 2 | 0.280 | 0.754 | 0.159 |
| mean | 0.283 | 0.757 | 0.162 |

The classifier assigns substantially higher sampling mass to hidden-positive unlabeled demos than hidden-bad demos, but it keeps every unlabeled demo in the training support.

## Policy Results

Success rate over 10 held-out reward-positive starts:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| classifier probability weighted sampler | 0.067 | 0.300 | 0.500 | 0.533 | 0.633 |

Per-seed policy results:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.000 | 0.000 | 0.600 | 0.500 | 0.600 |
| 1 | 0.100 | 0.400 | 0.300 | 0.700 | 0.700 |
| 2 | 0.100 | 0.500 | 0.600 | 0.400 | 0.600 |
| mean | 0.067 | 0.300 | 0.500 | 0.533 | 0.633 |

## Comparison To Existing Lift Controls

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| pos-min hard support | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |
| classifier probability weighted sampler | 0.067 | 0.300 | 0.500 | 0.533 | 0.633 |
| all train positives | 0.167 | 0.433 | 0.700 | 0.633 | 0.733 |
| all train demos | 0.067 | 0.033 | 0.167 | 0.200 | 0.267 |

## Interpretation

Soft weighted BC is not the broken baseline. It is a meaningful classifier-only baseline: it improves strongly over bad-dominated all-demo cloning, especially at `10k` to `20k`, and reaches `0.633` best-per-seed mean.

Hard selected support is still better at the clean fixed endpoint on this Lift split. `pos_min` reaches `0.667` mean success at 20k versus `0.533` for weighted BC, while also using a much smaller support set. The likely reason is that keeping all `1144` hidden-bad unlabeled demos, even at low sampling weight, still injects conflicting actions into sequence BC.

Paper-facing claim boundary: the robotics result should compare hard support selection against this stronger soft-weighted BC baseline, not only against all-demo cloning. The honest claim is that bad-aware classifier scores help both soft weighting and hard selection, but calibrated hard support selection gives the cleaner fixed-budget Lift result.

Artifacts:

- Seed 0 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_eval/REPORT.md`
- Seed 1 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed1_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed1_eval/REPORT.md`
- Seed 2 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed2_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed2_eval/REPORT.md`
- CSV: `summary.csv`
