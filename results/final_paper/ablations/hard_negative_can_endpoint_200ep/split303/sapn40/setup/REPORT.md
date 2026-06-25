# Hard-Negative Can Endpoint Setup

Candidate: `state_action_positive_nn_top40`.
Split: `/home/eston/tri-piql/results/final_paper/ablations/hard_negative_can_action_conflict_splits/split303/split_indices.json`.
Train filter key: `hn_can_s303_sapn40_seed0_train`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden positives: `32`.
Selected hidden bad: `8`.
Config: `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/sapn40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/sapn40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path /home/eston/tri-piql/results/final_paper/ablations/hard_negative_can_action_conflict_splits/split303/split_indices.json --out-dir results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/sapn40/eval_smoke --checkpoint-glob 'results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/sapn40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```
