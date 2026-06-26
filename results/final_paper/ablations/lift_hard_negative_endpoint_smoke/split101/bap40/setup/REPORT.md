# Lift Hard-Negative Endpoint Setup

Candidate: `bad_aware_proxy_top40`.
Split: `results/final_paper/ablations/lift_hard_negative_action_conflict_splits/split101/split_indices.json`.
Train filter key: `lift_hn_s101_bap40_seed0_train`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden positives: `21`.
Selected hidden bad: `19`.
Config: `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/bap40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/bap40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/lift_hard_negative_action_conflict_splits/split101/split_indices.json --out-dir results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/bap40/eval_smoke --checkpoint-glob 'results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/bap40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 150 --eval-init-mode valid_positive_states --device cuda --seed 0
```
