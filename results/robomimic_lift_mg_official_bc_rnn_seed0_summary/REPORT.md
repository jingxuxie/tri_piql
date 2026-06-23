# Robomimic Lift MG Official BC-RNN-GMM Seed-0 Summary

Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.

Split: `results/robomimic_inspection/lift_mg_low_dim_sparse/split_indices.json`.

Protocol:

- Official Robomimic BC-RNN-GMM backbone.
- `1024,1024` actor head, 2-layer LSTM with hidden size `400`, 5 GMM modes.
- `20,000` optimizer steps, saved at `5k / 10k / 15k / 20k`.
- Evaluation uses `10` held-out reward-positive initial states and horizon `150`, matching the Lift MG trajectory length.

## Dataset And Support

Lift MG sparse has `1500` trajectories: `316` reward-positive and `1184` zero-return. Because it has no built-in Robomimic train/valid mask, the inspector created a deterministic stratified holdout with `30` reward-positive and `30` zero-return validation demos.

The unlabeled training pool is strongly bad-dominated: `276` hidden reward-positive demos and `1144` hidden zero-return demos.

| source | train demos | train positive | train negative | selected unlabeled | selected hidden positive | selected hidden bad | selected purity |
|---|---:|---:|---:|---:|---:|---:|---:|
| labeled positives | 10 | 10 | 0 | 0 | 0 | 0 | n/a |
| top-80 selected support | 90 | 87 | 3 | 80 | 77 | 3 | 0.963 |
| top-160 selected support | 170 | 164 | 6 | 160 | 154 | 6 | 0.963 |
| pos-min calibrated threshold | 240 | 213 | 27 | 230 | 203 | 27 | 0.883 |
| adaptive masscap | 289 | 233 | 56 | 279 | 223 | 56 | 0.799 |
| all train demos | 1440 | 286 | 1154 | 1420 | 276 | 1144 | 0.194 |
| all train positives | 286 | 286 | 0 | 276 | 276 | 0 | 1.000 |

## Policy Results

Success rate over 10 held-out reward-positive starts:

| source | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| labeled positives | 0.100 | 0.000 | 0.000 | 0.200 | 0.200 |
| top-80 selected support | 0.000 | 0.300 | 0.100 | 0.200 | 0.300 |
| top-160 selected support | 0.000 | 0.500 | 0.300 | 0.700 | 0.700 |
| pos-min calibrated threshold | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |
| adaptive masscap | 0.100 | 0.400 | 0.600 | 0.600 | 0.600 |
| all train demos | 0.100 | 0.100 | 0.300 | 0.100 | 0.300 |
| all train positives | 0.200 | 0.300 | 0.700 | 0.800 | 0.800 |

## Interpretation

This is a useful but not claim-complete cross-task result.

The selector generalizes as a support-purification mechanism: top-160 ranking turns a `19.4%` reward-positive unlabeled pool into `96.3%` reward-positive selected support.

The policy result is budget-sensitive. Top-80 selected support learns earlier than scarce positives, reaching `0.300` at 10k while scarce positives are at `0.000`, but it is coverage-limited at 20k. Expanding to top-160 preserves `0.963` selected purity, doubles hidden-positive coverage from 77 to 154 demos, and improves 20k success from `0.200` to `0.700`.

The hidden-label-free adaptive masscap rule selects broader support: 223 hidden positives and 56 hidden bad demos. It reaches `0.600` at 15k/20k, which is below manual top-160 at 20k but still far above all-demo cloning at 20k.

The new hidden-label-free `pos_min` threshold uses the minimum labeled-positive demo score as the unlabeled-demo cutoff. It selects 203 hidden positives and 27 hidden bad demos, a cleaner support set than adaptive masscap while covering more positives than top-160. It reaches `0.800` success at 20k, matching the oracle positive-support row on this seed. This removes the earlier selected-support gap for Lift: the gap was a budget/calibration issue, not a task-capability failure.

Naive all-demo cloning is not a clean failure at every checkpoint, but it is much weaker at 20k (`0.100`) than top-160 selected support (`0.700`), adaptive masscap (`0.600`), and the calibrated `pos_min` automatic rule (`0.800`) despite using far more data.

The honest takeaway is that Lift MG now supports a stronger cross-task story: classifier-ranked support can recover positive coverage from a bad-dominated mixed log, and a simple labeled-score-calibrated threshold can match oracle positive-support performance on this one-seed screen. This is still not a final benchmark row without more seeds, but it is the strongest Lift evidence so far.

Artifacts:

- Inspection: `results/robomimic_inspection/lift_mg_low_dim_sparse/REPORT.md`
- Selector support analysis: `results/robomimic_lift_mg_selector_score_analysis/REPORT.md`
- Scarce setup/eval: `results/robomimic_lift_mg_official_bc_rnn_scarce_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_scarce_seed0_eval/REPORT.md`
- Top-80 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_top80_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_top80_seed0_eval/REPORT.md`
- Top-160 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_top160_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_top160_seed0_eval/REPORT.md`
- Pos-min threshold setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_eval/REPORT.md`
- Pos-min three-seed follow-up: `results/robomimic_lift_mg_official_bc_rnn_posmin_3seed_summary/REPORT.md`
- Adaptive masscap setup/eval: `results/robomimic_lift_mg_official_bc_rnn_adaptive_masscap_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_adaptive_masscap_seed0_eval/REPORT.md`
- All-train setup/eval: `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed0_eval/REPORT.md`
- All-positive setup/eval: `results/robomimic_lift_mg_official_bc_rnn_allpositive_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_allpositive_seed0_eval/REPORT.md`
