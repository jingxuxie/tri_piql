# v0.2 Action-Risk Lift Endpoint Smoke Setup

Candidate: `classifier_risk_fusion_top160`.
Split: `results/final_paper/splits/lift_mg_mg_sparse_split11/split_indices.json`.
Train filter key: `v02risk_lift_s11_crf160_seed0_train`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden positives: `156`.
Selected hidden bad: `4`.
Config: `results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/crf160/setup/config.json`.

## Train

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/crf160/setup/config.json
```

## Evaluate

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/splits/lift_mg_mg_sparse_split11/split_indices.json --out-dir results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/crf160/eval_smoke --checkpoint-glob 'results/final_paper/ablations/v02_action_risk_endpoint_smoke_lift/split11/crf160/train/**/models/model_epoch_*.pth' --eval-episodes 10 --eval-horizon 150 --eval-init-mode valid_positive_states --device cuda --seed 0
```
