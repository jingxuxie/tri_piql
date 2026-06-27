# Final Matrix Run

- Task: `can_paired`.
- Split type: `pos40_bad80`.
- Split seed: `404`.
- Method: `bc_all_mixed`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json`.
- Setup diagnostics: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_bc_all_mixed_policy0/setup/diagnostics.json`.
- Train demos: `180`.
- Selected unlabeled demos: `0`.
- Train output dir: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_bc_all_mixed_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_bc_all_mixed_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_bc_all_mixed_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `400`.
