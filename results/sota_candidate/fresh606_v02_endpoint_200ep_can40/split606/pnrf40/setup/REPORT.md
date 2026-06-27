# Fresh606 v0.2 Endpoint Setup

Candidate: `positive_nn_risk_fusion_top40`.
Split: `results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json`.
Train filter key: `sota_v02fresh_can40_s606_pnrf40_seed0_train`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden positives: `37`.
Selected hidden bad: `3`.
Config: `results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/pnrf40/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/pnrf40/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json --out-dir results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/pnrf40/eval_smoke --checkpoint-glob 'results/sota_candidate/fresh606_v02_endpoint_200ep_can40/split606/pnrf40/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```
