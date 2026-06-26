# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `404`.
- Method: `positive_only_nn`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper_v02/splits/lift_mg_mg_sparse_split404/split_indices.json`.
- Setup diagnostics: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/setup/diagnostics.json`.
- Train demos: `170`.
- Selected unlabeled demos: `160`.
- Train output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
