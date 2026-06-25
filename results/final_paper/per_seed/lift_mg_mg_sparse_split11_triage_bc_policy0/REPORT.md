# Final Matrix Run

- Task: `lift_mg`.
- Split type: `mg_sparse`.
- Split seed: `11`.
- Method: `triage_bc`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper/splits/lift_mg_mg_sparse_split11/split_indices.json`.
- Score diagnostics: `results/final_paper/score_diagnostics/lift_mg_mg_sparse_split11_policy0`.
- Router branch: `hard_pos_min`.
- Router reason: labeled positives are high-scoring and enough unlabeled demos clear pos-min.
- Setup diagnostics: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/setup/diagnostics.json`.
- Train demos: `188`.
- Selected unlabeled demos: `178`.
- Train output dir: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `150`.
