# Final Matrix Run

- Task: `can_paired`.
- Split type: `pos20_bad80`.
- Split seed: `11`.
- Method: `classifier_topk`.
- Policy/classifier seed: `0`.
- Split path: `results/final_paper/splits/can_paired_pos20_bad80_split11/split_indices.json`.
- Score diagnostics: `results/final_paper/score_diagnostics/can_paired_pos20_bad80_split11_policy0`.
- Setup diagnostics: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_classifier_topk_policy0/setup/diagnostics.json`.
- Train demos: `30`.
- Selected unlabeled demos: `20`.
- Train output dir: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_classifier_topk_policy0/train`.

## Train

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_pos20_bad80_split11_classifier_topk_policy0/setup/config.json
```

## Evaluate

Evaluation output dir: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_classifier_topk_policy0/eval`.
Evaluation episodes: `50`.
Evaluation horizon: `400`.
