# Robomimic Can MG Weighted BC Three-Seed Follow-Up

This report summarizes the three-seed official Robomimic BC-RNN-GMM weighted-sampler follow-up on the Can MG sparse stress split.

Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.

Split: `results/robomimic_inspection/can_mg_low_dim_sparse/split_indices.json`.

Protocol:

- 10 labeled reward-positive demos, 10 labeled reward-negative demos.
- 3,840 unlabeled train demos: 688 hidden-positive and 3,152 hidden-bad.
- Official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Weighted sampler keeps all unlabeled demos but weights them by classifier probability with floor `0.05`.
- 20,000 optimizer steps, saved at 5k / 10k / 15k / 20k.
- Evaluation uses 10 held-out reward-positive Can initial states and horizon 400.

Artifacts:

- Seed 0 setup/eval: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_eval/REPORT.md`
- Seed 1 setup/eval: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed1_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed1_eval/REPORT.md`
- Seed 2 setup/eval: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed2_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed2_eval/REPORT.md`

## Support And Weights

| seed | train demos | weighted unlabeled | hidden positive | hidden bad | hidden-positive mean weight | hidden-bad mean weight |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3850 | 3840 | 688 | 3152 | 0.885 | 0.432 |
| 1 | 3850 | 3840 | 688 | 3152 | 0.871 | 0.410 |
| 2 | 3850 | 3840 | 688 | 3152 | 0.878 | 0.416 |
| mean | 3850 | 3840 | 688 | 3152 | 0.878 | 0.419 |

The classifier consistently gives hidden-positive unlabeled demos about twice the mean weight of hidden-bad demos.

## Policy Results

Success over 10 held-out reward-positive starts:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.000 | 0.300 | 0.200 | 0.400 | 0.400 |
| 1 | 0.000 | 0.100 | 0.400 | 0.300 | 0.400 |
| 2 | 0.000 | 0.000 | 0.000 | 0.300 | 0.300 |
| mean | 0.000 | 0.133 | 0.200 | 0.333 | 0.367 |

## Interpretation

The three-seed follow-up weakens the seed-0-only Can MG story, but the later matched controls show that weighted sampling is still the best Can MG stress-diagnostic row at fixed 20k:

- Fixed 20k mean is `0.333`, lower than the seed-0 value `0.400`.
- Best-per-seed mean is `0.367`.
- Seed 2 only becomes successful at 20k, while seed 1 peaks at 15k.
- Matched three-seed controls reach `0.200` for all-positive support, `0.167` for pos-p10 hard support, and `0.100` for all-demo cloning at fixed 20k.

This still supports the mechanism that classifier scores carry useful signal under broad bad-dominated coverage: hidden positives get much higher weights than hidden bad demos, and every seed reaches nonzero success by 20k. But Can MG should remain a calibration stress diagnostic because absolute success is modest.

Updated claim boundary:

- Paired Can and Lift MG remain the paper-facing robotics evidence for hard support selection.
- Can MG should be written as evidence that large bad-dominated pools may require soft weighting or a better hard/soft converter, not as proof that soft weighting already solves the setting.
- Matched controls are summarized in `results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`.
