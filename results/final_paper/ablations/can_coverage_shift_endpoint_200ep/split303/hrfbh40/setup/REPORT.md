# Can Coverage-Shift Endpoint Setup

Candidate: `hybrid_rank_fusion_badaware_heavy_top40`.
Split: `results/final_paper/ablations/can_coverage_shift_splits/split303/split_indices.json`.
Train filter key: `cov_can200_s303_hrfbh40_seed0_train`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden positives: `40`.
Selected hidden bad: `0`.
Config: `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/hrfbh40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/hrfbh40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_coverage_shift_splits/split303/split_indices.json --out-dir results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/hrfbh40/eval_smoke --checkpoint-glob 'results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/hrfbh40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```
