# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `505`.
- Method: `all_train_positive_oracle`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper_v02/splits/lift_mg_mg_sparse_split505/split_indices.json`.
- Setup diagnostics: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/setup/diagnostics.json`.
- Train demos: `286`.
- Selected unlabeled demos: `0`.
- Train output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
