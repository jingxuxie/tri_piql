# Robomimic Square Quality Policy Smoke

This is a bounded one-seed policy smoke for the Square MH relative-quality split.
It tests whether the support-side Square score diagnostic can already produce a usable policy comparison with the same official Robomimic BC-RNN-GMM backbone used in the Can/Lift results.

## Protocol

- Split: `results/robomimic_inspection/square_mh_quality_better_worse/split_indices.json`.
- Evaluation initial states: `valid_positive_states`.
- Checkpoints: epoch 50 and epoch 100, corresponding to 5k and 10k optimizer steps under this config.
- Evaluation: `10` episodes per checkpoint, horizon `500`.
- Seed: `0`.

## Training Support

| method | source | train demos | selected unlabeled | hidden positive | hidden bad | selected purity |
|---|---|---:|---:|---:|---:|---:|
| better-only BC | `all_train_positive` | 90 | 0 | 0 | 0 | n/a |
| mixed better+worse BC | `all_train_demos` | 180 | 0 | 0 | 0 | n/a |
| adaptive-masscap support BC | `positive_plus_classifier_adaptive_masscap_unlabeled_demos` | 69 | 59 | 42 | 17 | 0.712 |

## Policy Results

| method | epoch | success | return | avg len | episodes |
|---|---:|---:|---:|---:|---:|
| better-only BC | 50 | 0.000 | 0.000 | 500.0 | 10 |
| better-only BC | 100 | 0.000 | 0.000 | 500.0 | 10 |
| mixed better+worse BC | 50 | 0.000 | 0.000 | 500.0 | 10 |
| mixed better+worse BC | 100 | 0.000 | 0.000 | 500.0 | 10 |
| adaptive-masscap support BC | 50 | 0.000 | 0.000 | 500.0 | 10 |
| adaptive-masscap support BC | 100 | 0.000 | 0.000 | 500.0 | 10 |

## Interpretation

- All evaluated Square policies failed all held-out `better_valid` initial-state rollouts at both checkpoints.
- The failures run to the full 500-step horizon, so the smoke does not reveal a quality-sensitive policy ordering.
- This should be treated as a negative/inconclusive policy result, not evidence against the score-calibration diagnostic.
- Square MH should remain support-side transfer evidence unless a stronger Square policy setup or a direct quality-sensitive evaluator is added.
