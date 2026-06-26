# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `707`.
- Method: `triage_bc`.
- Policy/classifier seed: `0`.
- Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split707/split_indices.json`.
- Score diagnostics: `results/candidate_g_fresh_preflight/score_diagnostics/lift_mg_mg_sparse_split707_policy0`.
- Router branch: `hard_pos_min`.
- Router reason: labeled positives are high-scoring and enough unlabeled demos clear pos-min.
- Setup diagnostics: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/setup/diagnostics.json`.
- Train demos: `182`.
- Selected unlabeled demos: `172`.
- Train output dir: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
