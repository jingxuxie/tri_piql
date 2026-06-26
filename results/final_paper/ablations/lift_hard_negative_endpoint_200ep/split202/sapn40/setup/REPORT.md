# Lift Hard-Negative 200-Epoch Endpoint Setup

Candidate: `state_action_positive_nn_top40`.
Split: `results/final_paper/ablations/lift_hard_negative_action_conflict_splits/split202/split_indices.json`.
Train filter key: `lift_hn200_s202_sapn40_seed0_train`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden positives: `0`.
Selected hidden bad: `40`.
Config: `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/sapn40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/sapn40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/lift_hard_negative_action_conflict_splits/split202/split_indices.json --out-dir results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/sapn40/eval_smoke --checkpoint-glob 'results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/sapn40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 150 --eval-init-mode valid_positive_states --device cuda --seed 0
```
