# Robomimic Bad-Label Support Ablation

This support-only diagnostic asks whether explicit bad labels are doing real work in the Robomimic selector. It compares the current positive-vs-negative state-action classifier against controls that do not use labeled bad demos.

Protocol:

- Base split: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`
- Labeled positives / negatives: `10` / `10`
- Hidden-bad unlabeled demos fixed at `80`.
- Hidden-positive unlabeled demos swept over `5, 10, 20, 30, 40, 50, 60, 70, 80`.
- Seeds: `0, 1, 2`.
- Classifier steps: `800`.

Selector families:

- `bad_aware_pos_vs_neg`: current tri-signal scoring, trained on labeled positive versus labeled bad transitions.
- `positive_only_nn`: no-bad-label nearest-neighbor similarity to labeled positive state-action support.
- `positive_vs_unlabeled`: no-bad-label classifier trained to separate labeled positives from the unlabeled pool treated as background.

## Key Support Results

Each cell shows mean selected hidden-positive demos / mean hidden-bad demos / mean purity over the requested seeds.

| hidden pos | bad-aware adaptive | bad-aware top20 | pos-only NN top20 | pos-only NN top40 | pos-vs-unl top20 | pos-vs-unl top40 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 5.0 / 15.0 / 0.250 | 5.0 / 15.0 / 0.250 | 4.0 / 16.0 / 0.200 | 5.0 / 35.0 / 0.125 | 1.0 / 19.0 / 0.050 | 3.3 / 36.7 / 0.083 |
| 10 | 10.0 / 10.0 / 0.500 | 10.0 / 10.0 / 0.500 | 9.0 / 11.0 / 0.450 | 10.0 / 30.0 / 0.250 | 4.3 / 15.7 / 0.217 | 6.7 / 33.3 / 0.167 |
| 20 | 15.0 / 5.0 / 0.750 | 15.0 / 5.0 / 0.750 | 15.0 / 5.0 / 0.750 | 18.0 / 22.0 / 0.450 | 7.0 / 13.0 / 0.350 | 9.0 / 31.0 / 0.225 |
| 30 | 28.3 / 18.0 / 0.616 | 19.0 / 1.0 / 0.950 | 19.0 / 1.0 / 0.950 | 27.0 / 13.0 / 0.675 | 11.0 / 9.0 / 0.550 | 12.7 / 27.3 / 0.317 |
| 40 | 36.3 / 13.7 / 0.728 | 19.7 / 0.3 / 0.983 | 20.0 / 0.0 / 1.000 | 31.0 / 9.0 / 0.775 | 11.3 / 8.7 / 0.567 | 16.0 / 24.0 / 0.400 |
| 50 | 41.0 / 8.3 / 0.833 | 20.0 / 0.0 / 1.000 | 20.0 / 0.0 / 1.000 | 37.0 / 3.0 / 0.925 | 12.7 / 7.3 / 0.633 | 19.3 / 20.7 / 0.483 |
| 60 | 48.7 / 5.0 / 0.910 | 20.0 / 0.0 / 1.000 | 20.0 / 0.0 / 1.000 | 39.0 / 1.0 / 0.975 | 12.7 / 7.3 / 0.633 | 20.3 / 19.7 / 0.508 |
| 70 | 51.7 / 2.3 / 0.963 | 20.0 / 0.0 / 1.000 | 20.0 / 0.0 / 1.000 | 40.0 / 0.0 / 1.000 | 13.7 / 6.3 / 0.683 | 21.3 / 18.7 / 0.533 |
| 80 | 59.0 / 2.3 / 0.968 | 20.0 / 0.0 / 1.000 | 20.0 / 0.0 / 1.000 | 40.0 / 0.0 / 1.000 | 14.3 / 5.7 / 0.717 | 22.0 / 18.0 / 0.550 |

## Interpretation

The no-bad-label controls are ranking controls, not policy results. They test whether scarce positives alone are enough to identify hidden-good Robomimic demos under contamination.

The support-only result is nuanced. Positive-vs-unlabeled scoring is weak, but positive-only nearest-neighbor ranking is a strong no-bad-label control. At 40 hidden-positive / 80 hidden-bad, positive-only NN top40 selects 31 hidden-positive and 9 hidden-bad demos, compared with 36.3 hidden-positive and 13.7 hidden-bad demos for mass-capped adaptive selection.

## Policy Follow-Up

The strongest no-bad-label support control, positive-only NN top40, was trained with the same official BC-RNN-GMM backbone on the 40p/80b split.

| selector | selected unlabeled | hidden-positive | hidden-bad | purity | 5k | 10k | 15k | 20k | best-per-seed mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| positive-only NN top40 | 40.0 | 31.0 | 9.0 | 0.775 | 0.167 | 0.433 | 0.533 | 0.633 | 0.767 |

Positive-only NN top40 ties masscap on best-per-seed mean, but is lower at the fixed 10k/15k/20k checkpoints and has higher variance. This means the paper should not claim that labeled bad demos are strictly necessary on this Robomimic split. The better claim is that the bad-aware adaptive selector gives more stable fixed-budget performance while preserving more hidden-positive coverage.

Artifacts:

- Per-seed CSV: `results/robomimic_bad_label_ablation/per_seed_selection.csv`
- Aggregate CSV: `results/robomimic_bad_label_ablation/aggregate_selection.csv`
- Config: `results/robomimic_bad_label_ablation/config.json`
- Policy control: `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_3seed_summary/REPORT.md`
