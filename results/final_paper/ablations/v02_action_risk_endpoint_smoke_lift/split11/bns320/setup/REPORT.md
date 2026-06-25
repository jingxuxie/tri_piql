# v0.2 Action-Risk Lift Endpoint Smoke Setup

Candidate: `bad_neighbor_safe_top320`.
Split: `results/final_paper/splits/lift_mg_mg_sparse_split11/split_indices.json`.
Train filter key: `v02risk_lift_s11_bns320_seed0_train`.
Train demos: `330`.
Selected unlabeled demos: `320`.
Selected hidden positives: `240`.
Selected hidden bad: `80`.
Config: `results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/bns320/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/bns320/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/splits/lift_mg_mg_sparse_split11/split_indices.json --out-dir results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/bns320/eval_smoke --checkpoint-glob 'results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/bns320/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 150 --eval-init-mode valid_positive_states --device cuda --seed 0
```
