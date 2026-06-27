# Fresh606 v0.2 Endpoint Setup

Candidate: `positive_nn_risk_union_top40`.
Split: `results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json`.
Train filter key: `sota_v02fresh_can40_s606_positive_nn_risk_union_top40_seed0_train`.
Train demos: `58`.
Selected unlabeled demos: `48`.
Selected hidden positives: `38`.
Selected hidden bad: `10`.
Config: `results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json --out-dir results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/eval_smoke --checkpoint-glob 'results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```
