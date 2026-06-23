# Robomimic Lift MG Official BC-RNN-GMM Three-Seed Controls

Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.

Split: `results/robomimic_inspection/lift_mg_low_dim_sparse/split_indices.json`.

Protocol:

- Official Robomimic BC-RNN-GMM backbone.
- `1024,1024` actor head, 2-layer LSTM with hidden size `400`, 5 GMM modes.
- `20,000` optimizer steps, saved at `5k / 10k / 15k / 20k`.
- Evaluation uses `10` held-out reward-positive Lift initial states and horizon `150`.

## Support

| source | train demos | train positive | train negative | selected unlabeled | selected hidden positive | selected hidden bad | purity |
|---|---:|---:|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 247.3 | 215.0 | 32.3 | 237.3 | 205.0 | 32.3 | 0.864 |
| classifier probability weighted sampler | 1430.0 | 286.0 | 1144.0 | 1420.0 | 276.0 | 1144.0 | 0.194 |
| all train positives | 286.0 | 286.0 | 0.0 | 276.0 | 276.0 | 0.0 | 1.000 |
| all train demos | 1440.0 | 286.0 | 1154.0 | 1420.0 | 276.0 | 1144.0 | 0.194 |

## Policy Results

Success rate over 10 held-out reward-positive starts:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |
| classifier probability weighted sampler | 0.067 | 0.300 | 0.500 | 0.533 | 0.633 |
| all train positives | 0.167 | 0.433 | 0.700 | 0.633 | 0.733 |
| all train demos | 0.067 | 0.033 | 0.167 | 0.200 | 0.267 |

Per-seed policy results:

| source | seed | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 0 | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |
| pos-min calibrated threshold | 1 | 0.200 | 0.200 | 0.500 | 0.400 | 0.500 |
| pos-min calibrated threshold | 2 | 0.000 | 0.200 | 0.500 | 0.800 | 0.800 |
| classifier probability weighted sampler | 0 | 0.000 | 0.000 | 0.600 | 0.500 | 0.600 |
| classifier probability weighted sampler | 1 | 0.100 | 0.400 | 0.300 | 0.700 | 0.700 |
| classifier probability weighted sampler | 2 | 0.100 | 0.500 | 0.600 | 0.400 | 0.600 |
| all train positives | 0 | 0.200 | 0.300 | 0.700 | 0.800 | 0.800 |
| all train positives | 1 | 0.100 | 0.400 | 0.700 | 0.500 | 0.700 |
| all train positives | 2 | 0.200 | 0.600 | 0.700 | 0.600 | 0.700 |
| all train demos | 0 | 0.100 | 0.100 | 0.300 | 0.100 | 0.300 |
| all train demos | 1 | 0.000 | 0.000 | 0.200 | 0.300 | 0.300 |
| all train demos | 2 | 0.100 | 0.000 | 0.000 | 0.200 | 0.200 |

## Interpretation

The same-seed controls make the Lift story much more defensible.

All-demo cloning is consistently poor despite using `1440` train demos. Its three-seed mean is `0.200` at 20k and `0.267` best-per-seed, confirming that the bad-dominated mixed log is a real failure mode for the same official BC-RNN-GMM backbone.

Classifier-probability weighted BC is a much stronger mixed-log baseline than all-demo cloning. It excludes known negatives, keeps all `1420` unlabeled demos, and samples hidden-positive demos with much higher mean weight than hidden-bad demos (`0.757` vs `0.162`). It reaches `0.533` mean success at 20k and `0.633` best-per-seed, so it should be used as the honest soft-weighted BC control.

The `pos_min` selector recovers most of the oracle-support performance while using a hidden-label-free threshold. It reaches `0.667` mean success at 20k and `0.700` best-per-seed, close to all-positive oracle support at `0.633` and `0.733`. It is lower than oracle at 15k (`0.533` versus `0.700`), which shows the remaining cost of selected bad demos and missing some positive coverage.

The weighted baseline narrows the gap but does not erase it. The fixed-20k comparison is `0.667` for hard `pos_min`, `0.533` for soft weighted BC, and `0.200` for all-demo cloning. This supports a more precise claim: classifier scores help soft weighting, but calibrated hard support selection better removes conflicting hidden-bad sequences for this official sequence BC backbone.

Seed 1 confirms the checkpoint-timing issue: all-positive oracle support also peaks at 15k (`0.700`) and drops at 20k (`0.500`), so the `pos_min` seed-1 20k drop is not purely a selector failure. A support-validation or checkpoint-selection rule is now a reasonable next mechanism if we want fixed-budget reporting to be less brittle.

Follow-up checkpoint-selection analysis is in `results/robomimic_lift_mg_checkpoint_selection_posmin_oracle_alltrain/REPORT.md`. Simple offline likelihood does not solve the seed-1 timing issue. Train-support and labeled-positive likelihood mostly pick the 20k checkpoint, preserving the fixed-budget comparison, while random `valid_all` likelihood prefers early checkpoints for selected-support runs because the validation holdout is failure-heavy. This argues against best-checkpoint reporting unless a stronger predeclared rule is added.

Paper-facing claim boundary: this supports cross-task transfer of hidden-label-free support selection on Lift MG. It should be written as strong support purification plus large improvement over all-demo cloning, with near-oracle policy performance, not as exact oracle matching at every checkpoint.

Artifacts:

- Pos-min three-seed summary: `results/robomimic_lift_mg_official_bc_rnn_posmin_3seed_summary/REPORT.md`
- Weighted BC three-seed summary: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_3seed_summary/REPORT.md`
- All-positive seed 1/2 evals: `results/robomimic_lift_mg_official_bc_rnn_allpositive_seed1_eval/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_allpositive_seed2_eval/REPORT.md`
- All-demo seed 1/2 evals: `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed1_eval/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed2_eval/REPORT.md`
- Checkpoint-selection diagnostic: `results/robomimic_lift_mg_checkpoint_selection_posmin_oracle_alltrain/REPORT.md`
