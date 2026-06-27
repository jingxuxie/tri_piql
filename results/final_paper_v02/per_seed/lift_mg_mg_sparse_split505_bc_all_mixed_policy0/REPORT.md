# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `505`.
- Method: `bc_all_mixed`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper_v02/splits/lift_mg_mg_sparse_split505/split_indices.json`.
- Setup diagnostics: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_bc_all_mixed_policy0/setup/diagnostics.json`.
- Train demos: `1440`.
- Selected unlabeled demos: `0`.
- Train output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_bc_all_mixed_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_bc_all_mixed_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_bc_all_mixed_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
