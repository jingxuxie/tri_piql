# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `303`.
- Method: `weighted_bc`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper_v02/splits/lift_mg_mg_sparse_split303/split_indices.json`.
- Score diagnostics: `results/final_paper_v02/score_diagnostics/lift_mg_mg_sparse_split303_policy0`.
- Setup diagnostics: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_weighted_bc_policy0/setup/diagnostics.json`.
- Train demos: `1430`.
- Selected unlabeled demos: `1420`.
- Train output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_weighted_bc_policy0/train`.

## Train

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_weighted_bc_policy0/setup/demo_weights.json
```

## Evaluate

Evaluation output dir: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_weighted_bc_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
