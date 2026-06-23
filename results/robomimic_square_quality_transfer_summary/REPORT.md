# Robomimic Square Quality Transfer

This is a support-side transfer diagnostic on a new Robomimic task family.
Square MH contains relative-quality masks (`better`, `okay`, `worse`) but no reward-failure demonstrations, so it is not a bad-demo benchmark.

## Dataset

- HDF5: `data/robomimic/v1.5/square/mh/low_dim_v15.hdf5`.
- Environment: `NutAssemblySquare`.
- Demos: `300`.
- Reward-positive demos: `300`.
- Reward-negative demos: `0`.

## Quality Split

- Positive labels: scarce `better_train` demos.
- Negative labels: scarce `worse_train` demos.
- Unlabeled mix: remaining `better_train` and `worse_train` demos; `okay` demos are excluded from this audit to keep hidden labels well-defined.
- Labeled positives / negatives: `10` / `10`.
- Hidden-positive / hidden-negative unlabeled: `80` / `80`.

## Score Calibration

- Labeled-positive mean score: `0.939`.
- Labeled-positive p10 score: `0.893`.
- Labeled-negative mean score: `0.053`.
- Labeled-negative max score: `0.115`.

## Selection Rules

| rule | selected | hidden positive | hidden bad | purity |
|---|---:|---:|---:|---:|
| top_posx2 | 20.0 | 16.0 | 4.0 | 0.800 |
| top_posx4 | 40.0 | 29.7 | 10.3 | 0.742 |
| pos_min | 28.7 | 23.0 | 5.7 | 0.803 |
| adaptive_masscap | 64.7 | 46.0 | 18.7 | 0.712 |

## Router

- Hidden-label-free router branch: `hard_adaptive_masscap`.
- Training rule: `adaptive_masscap`.
- Saturated unlabeled count >= 0.95: `5.3`.

## Interpretation

- Scarce positive/negative quality labels produce a strong state-action score on Square MH.
- The score improves support purity over the 50/50 unlabeled quality mix: `pos_min` reaches about `0.803` purity and adaptive masscap reaches about `0.712` purity.
- This extends the score-calibration story to a new task family, but only as a relative-quality support diagnostic.
- It should not be used as a main policy claim unless we add a quality-sensitive Square policy evaluation; sparse success alone is not enough because all recorded demos are successful.
