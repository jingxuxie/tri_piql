# Official Robomimic 40p/80b Positive-Only NN Control

This report evaluates a no-bad-label support control on the intermediate Robomimic Can split with 40 hidden-positive and 80 hidden-bad unlabeled demos. The control ranks unlabeled demos by nearest-neighbor similarity to labeled positive state-action support, selects the top 40 unlabeled demos, and trains the same official Robomimic BC-RNN-GMM backbone.

Protocol:

- Split: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80/split_indices.json`
- Labels available to this control for support selection: 10 successful demos only.
- Labeled bad demos are not used by the positive-only NN selector.
- Unlabeled pool: 40 hidden-positive demos, 80 hidden-bad demos.
- Seeds: 0, 1, 2.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Support ablation: `results/robomimic_bad_label_ablation/REPORT.md`
- Setup/eval directories: `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_seed{0,1,2}_mlphead_{setup,eval}`
- Main 40p/80b selector summary: `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`

## Support Selection

| method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| positive-only NN top40 | 40.0 | 31.0 | 9.0 | 0.775 |
| mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 |
| coverage-gap | 74.0 | 40.0 | 34.0 | 0.541 |
| top20 precision | 20.0 | 19.7 | 0.3 | 0.983 |

## Rollout Success

Mean over seeds:

| method | 5k | 10k | 15k | 20k | best-per-seed mean |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| positive-only NN top40 | 0.167 | 0.433 | 0.533 | 0.633 | 0.767 |
| coverage-gap | 0.167 | 0.333 | 0.567 | 0.600 | 0.667 |
| top20 precision | 0.033 | 0.567 | 0.667 | 0.700 | 0.700 |

Seed-level positive-only NN top40 details:

| seed | selected | hidden-positive | hidden-bad | purity | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 40 | 31 | 9 | 0.775 | 0.400 | 0.700 | 0.800 | 0.400 | 0.800 |
| 1 | 40 | 31 | 9 | 0.775 | 0.000 | 0.500 | 0.400 | 0.800 | 0.800 |
| 2 | 40 | 31 | 9 | 0.775 | 0.100 | 0.100 | 0.400 | 0.700 | 0.700 |

## Interpretation

This is a strong control, not a strawman. Positive-only nearest-neighbor support finds a useful subset without labeled bad demos, and its best checkpoint per seed ties mass-capped adaptive selection.

However, the fixed-budget picture favors the bad-aware adaptive selector. Positive-only NN top40 is lower at 10k, 15k, and 20k, with especially high variance at 10k/15k. It also leaves more hidden-positive support unused than masscap.

The honest claim is therefore not that bad labels are strictly necessary on this Robomimic split. The better claim is that explicit bad labels enable a more stable adaptive coverage rule: masscap keeps more useful support than top20 or positive-only NN top40 while avoiding the over-expanded bad support of coverage-gap.
