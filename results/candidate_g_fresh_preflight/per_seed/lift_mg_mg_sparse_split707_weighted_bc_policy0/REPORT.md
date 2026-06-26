# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `707`.
- Method: `weighted_bc`.
- Policy/classifier seed: `0`.
- Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split707/split_indices.json`.
- Score diagnostics: `results/candidate_g_fresh_preflight/score_diagnostics/lift_mg_mg_sparse_split707_policy0`.
- Setup diagnostics: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_weighted_bc_policy0/setup/diagnostics.json`.
- Train demos: `1430`.
- Selected unlabeled demos: `1420`.
- Train output dir: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_weighted_bc_policy0/train`.

## Train

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_weighted_bc_policy0/setup/config.json --demo-weights results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_weighted_bc_policy0/setup/demo_weights.json
```

## Evaluate

Evaluation output dir: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_weighted_bc_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
