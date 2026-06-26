# Final Matrix Run

- Task: `can_paired`.
- Split type: `pos40_bad80`.
- Split seed: `707`.
- Method: `triage_bc`.
- Policy/classifier seed: `0`.
- Split path: `results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split707/split_indices.json`.
- Score diagnostics: `results/candidate_g_fresh_preflight/score_diagnostics/can_paired_pos40_bad80_split707_policy0`.
- Router branch: `hard_adaptive_masscap`.
- Router reason: score shape is not a large ambiguous pool; use calibrated mass-capped hard support.
- Setup diagnostics: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/setup/diagnostics.json`.
- Train demos: `57`.
- Selected unlabeled demos: `47`.
- Train output dir: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `400`.
