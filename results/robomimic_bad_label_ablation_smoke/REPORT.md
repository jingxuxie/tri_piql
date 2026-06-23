# Robomimic Bad-Label Support Ablation

This support-only diagnostic asks whether explicit bad labels are doing real work in the Robomimic selector. It compares the current positive-vs-negative state-action classifier against controls that do not use labeled bad demos.

Protocol:

- Base split: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`
- Labeled positives / negatives: `10` / `10`
- Hidden-bad unlabeled demos fixed at `80`.
- Hidden-positive unlabeled demos swept over `40`.
- Seeds: `0`.
- Classifier steps: `50`.

Selector families:

- `bad_aware_pos_vs_neg`: current tri-signal scoring, trained on labeled positive versus labeled bad transitions.
- `positive_only_nn`: no-bad-label nearest-neighbor similarity to labeled positive state-action support.
- `positive_vs_unlabeled`: no-bad-label classifier trained to separate labeled positives from the unlabeled pool treated as background.

## Key Support Results

Each cell shows mean selected hidden-positive demos / mean hidden-bad demos / mean purity over the requested seeds.

| hidden pos | bad-aware adaptive | bad-aware top20 | pos-only NN top20 | pos-only NN top40 | pos-vs-unl top20 | pos-vs-unl top40 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 40 | 40.0 / 0.0 / 1.000 | 20.0 / 0.0 / 1.000 | 20.0 / 0.0 / 1.000 | 31.0 / 9.0 / 0.775 | 20.0 / 0.0 / 1.000 | 31.0 / 9.0 / 0.775 |

## Interpretation

The no-bad-label controls are ranking controls, not policy results. They test whether scarce positives alone are enough to identify hidden-good Robomimic demos under contamination.

Use this report to decide whether a no-bad-label official BC-RNN policy control is worth running. If a no-bad support rule is close to the bad-aware adaptive selector in the target regime, the paper claim should emphasize adaptive support selection rather than bad-label necessity. If it is substantially worse, the next GPU run should train official BC-RNN on the strongest no-bad support control for an end-to-end policy ablation.

Artifacts:

- Per-seed CSV: `results/robomimic_bad_label_ablation_smoke/per_seed_selection.csv`
- Aggregate CSV: `results/robomimic_bad_label_ablation_smoke/aggregate_selection.csv`
- Config: `results/robomimic_bad_label_ablation_smoke/config.json`
