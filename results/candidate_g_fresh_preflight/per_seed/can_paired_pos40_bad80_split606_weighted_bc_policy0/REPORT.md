# Final Matrix Run

- Task: `can_paired`.
- Split type: `pos40_bad80`.
- Split seed: `606`.
- Method: `weighted_bc`.
- Policy/classifier seed: `0`.
- Split path: `results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json`.
- Score diagnostics: `results/candidate_g_fresh_preflight/score_diagnostics/can_paired_pos40_bad80_split606_policy0`.
- Setup diagnostics: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split606_weighted_bc_policy0/setup/diagnostics.json`.
- Train demos: `130`.
- Selected unlabeled demos: `120`.
- Train output dir: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split606_weighted_bc_policy0/train`.

## Train

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split606_weighted_bc_policy0/setup/config.json --demo-weights results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split606_weighted_bc_policy0/setup/demo_weights.json
```

## Evaluate

Evaluation output dir: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split606_weighted_bc_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `400`.
