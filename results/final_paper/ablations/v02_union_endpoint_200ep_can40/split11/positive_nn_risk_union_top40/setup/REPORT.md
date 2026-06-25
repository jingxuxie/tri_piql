# v0.2 Union Candidate Endpoint Setup

Candidate: `positive_nn_risk_union_top40`.
Split: `results/final_paper/splits/can_paired_pos40_bad80_split11/split_indices.json`.
Train filter key: `v02union200_can40_s11_positive_nn_risk_union_top40_seed0_train`.
Train demos: `55`.
Selected unlabeled demos: `45`.
Selected hidden positives: `40`.
Selected hidden bad: `5`.
Config: `results/final_paper/ablations/v02_union_endpoint_200ep_can40/split11/positive_nn_risk_union_top40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/v02_union_endpoint_200ep_can40/split11/positive_nn_risk_union_top40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/splits/can_paired_pos40_bad80_split11/split_indices.json --out-dir results/final_paper/ablations/v02_union_endpoint_200ep_can40/split11/positive_nn_risk_union_top40/eval_smoke --checkpoint-glob 'results/final_paper/ablations/v02_union_endpoint_200ep_can40/split11/positive_nn_risk_union_top40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```
