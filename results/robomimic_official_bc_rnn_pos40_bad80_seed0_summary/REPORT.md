# Official Robomimic 40p/80b Seed-0 Selector Check

This report compares the current mass-capped adaptive selector against original coverage-gap and top20 precision on the intermediate Robomimic Can split with 40 hidden-positive and 80 hidden-bad unlabeled demos. This is a seed-0 end-to-end policy check. It is superseded for aggregate claims by `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`.

Protocol:

- Split: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80/split_indices.json`
- Labels: 10 successful demos, 10 failed demos.
- Unlabeled pool: 40 hidden-positive demos, 80 hidden-bad demos.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Selector analysis: `results/robomimic_selector_score_analysis_pos40_bad80/REPORT.md`
- Mass-capped setup/eval:
  - `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_mlphead_eval/REPORT.md`
- Coverage-gap setup/eval:
  - `results/robomimic_official_bc_rnn_gap_posx4_pos40_bad80_seed0_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_gap_posx4_pos40_bad80_seed0_mlphead_eval/REPORT.md`
- Top20 setup/eval:
  - `results/robomimic_official_bc_rnn_top20_pos40_bad80_seed0_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top20_pos40_bad80_seed0_mlphead_eval/REPORT.md`

## Support Selection

| method | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 60 | 50 | 36 | 14 | 0.720 |
| coverage-gap | 83 | 73 | 40 | 33 | 0.548 |
| top20 precision | 30 | 20 | 19 | 1 | 0.950 |

## Rollout Success

| method | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 0.300 | 0.500 | 0.800 | 0.800 | 0.800 |
| coverage-gap | 0.100 | 0.500 | 0.800 | 0.600 | 0.800 |
| top20 precision | 0.000 | 0.600 | 0.700 | 0.700 | 0.700 |

## Interpretation

The seed-0 intermediate split supports the mass-cap refinement. Top20 is very pure but leaves too much positive support unused. Original coverage recovers all 40 hidden positives, but admits 33 hidden-bad demos and loses performance by 20k. The mass-capped selector takes the middle support size, keeps most hidden positives, cuts bad support by more than half relative to coverage, and gives the best 20k result on this seed.

This seed-0 snapshot is retained for provenance. Use the three-seed summary for current aggregate claims.
