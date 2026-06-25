# Can Prefix-Positive Endpoint Setup

Candidate: `prefix_bad_aware_state_top80`.
Split: `results/final_paper/ablations/can_prefix_positive_splits/split303/split_indices.json`.
Train filter key: `prefix_can200_s303_prefix_bad_aware_state_top80_seed0_train`.
Train demos: `90`.
Selected unlabeled demos: `80`.
Selected hidden positives: `77`.
Selected hidden bad: `3`.
Config: `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split303/prefix_bad_aware_state_top80/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split303/prefix_bad_aware_state_top80/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_prefix_positive_splits/split303/split_indices.json --out-dir results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split303/prefix_bad_aware_state_top80/eval_smoke --checkpoint-glob 'results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split303/prefix_bad_aware_state_top80/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```
