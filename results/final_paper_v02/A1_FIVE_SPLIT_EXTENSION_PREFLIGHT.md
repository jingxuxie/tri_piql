# A1 Five-Split v0.2 Fresh-Gate Preflight

Status: A1 draft endpoint extension complete. Can and Lift added split
endpoints are complete for splits `404` and `505`, but the five-split numbers
have not been promoted into canonical paper tables.

This file tracks the Priority A1 extension from
`triage_bc_top_tier_completion_plan.md`: expand the frozen v0.2 fresh Can+Lift
gate from three split seeds (`101`, `202`, `303`) to five split seeds
(`101`, `202`, `303`, `404`, `505`). The goal is to reduce the "only three
split seeds" weakness before making stronger top-tier claims.

## What Was Prepared

Generated or verified split/score artifacts:

- `results/final_paper_v02/splits/can_paired_pos40_bad80_split404/`
- `results/final_paper_v02/splits/can_paired_pos40_bad80_split505/`
- `results/final_paper_v02/splits/lift_mg_mg_sparse_split404/`
- `results/final_paper_v02/splits/lift_mg_mg_sparse_split505/`
- `results/final_paper_v02/score_diagnostics/can_paired_pos40_bad80_split404_policy0/`
- `results/final_paper_v02/score_diagnostics/can_paired_pos40_bad80_split505_policy0/`
- `results/final_paper_v02/score_diagnostics/lift_mg_mg_sparse_split404_policy0/`
- `results/final_paper_v02/score_diagnostics/lift_mg_mg_sparse_split505_policy0/`

Five-split support/router preflight:

- `results/final_paper_v02/tables/a1_preflight_5split/v02_fresh_router_support_REPORT.md`
- `results/final_paper_v02/tables/a1_preflight_5split/v02_fresh_router_support_per_split.csv`
- `results/final_paper_v02/tables/a1_preflight_5split/v02_fresh_router_support_summary.csv`

Prepared endpoint configs for the added seeds:

- Can split `404`: v0.2 hard union, positive-only NN top40, weighted BC.
- Can split `505`: v0.2 hard union, positive-only NN top40, weighted BC.
- Lift split `404`: weighted BC, positive-only NN top160.
- Lift split `505`: weighted BC, positive-only NN top160.

## Preflight Result

Router decisions stay stable on the added seeds.

| Setting | Split | Frozen v0.2 branch | Main support read |
| --- | --- | --- | --- |
| Can 40p/80b | `404` | `hard_risk_union` | union selects `39/40` hidden positives and `5/80` hidden bad demos |
| Can 40p/80b | `505` | `hard_risk_union` | union selects `40/40` hidden positives and `4/80` hidden bad demos |
| Lift MG | `404` | `soft_weighted` | weighted branch uses full mixed pool, as expected for coverage |
| Lift MG | `505` | `soft_weighted` | weighted branch uses full mixed pool, as expected for coverage |

Across five Can splits, the hard-union selected branch selects `198/200`
hidden positives and `28/400` hidden bad demos. This is support-side evidence
only; the paper claim should not change until the endpoint jobs finish.

## Endpoint Progress

| Setting | Split | Method | Role | Success |
| --- | --- | --- | --- | ---: |
| Can 40p/80b | `404` | `positive_nn_risk_union_top40` | v0.2 selected | `27/50` |
| Can 40p/80b | `404` | `positive_only_nn` | strong baseline | `39/50` |
| Can 40p/80b | `404` | `weighted_bc` | strong baseline | `33/50` |
| Can 40p/80b | `505` | `positive_nn_risk_union_top40` | v0.2 selected | `41/50` |
| Can 40p/80b | `505` | `positive_only_nn` | strong baseline | `40/50` |
| Can 40p/80b | `505` | `weighted_bc` | strong baseline | `30/50` |
| Lift MG | `404` | `weighted_bc` | v0.2 selected | `30/50` |
| Lift MG | `404` | `positive_only_nn` | strong baseline | `25/50` |
| Lift MG | `505` | `weighted_bc` | v0.2 selected | `33/50` |
| Lift MG | `505` | `positive_only_nn` | strong baseline | `26/50` |

Progress summary:

- Completed v0.2 selected Can rows are now `197/250` across splits
  `101`/`202`/`303`/`404`/`505`.
- On all five Can splits with completed non-oracle baselines, v0.2 selected is
  `197/250` versus best completed baselines `192/250`.
- Split `404` is a clear selected-branch loss: v0.2 hard union is `27/50`
  while positive-only NN is `39/50` and weighted BC is `33/50`.
- Split `404` strong baselines are now complete; the best completed baseline
  remains positive-only NN.
- Split `505` selected branch is `41/50`, positive-only NN is `40/50`, and
  weighted BC is `30/50`.
- The five-split Can aggregate preserves a small selected-branch edge, but the
  margin remains only `+0.020` and should be framed cautiously.
- Completed v0.2 selected Lift rows are `143/250` versus best completed
  non-oracle baselines `125/250`, margin `+0.072`.
- Combined Can+Lift selected rows are `340/500` versus best per-split
  non-oracle baselines `317/500`, margin `+0.046`.
- Draft progress summary:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_gate_REPORT.md`

## Next GPU Queue

Run these from the repo root with GPU access. Keep
`XLA_PYTHON_CLIENT_PREALLOCATE=false` and `MUJOCO_GL=egl`.

### Can 40p/80b Split 404

Completed:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split404/positive_nn_risk_union_top40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json --out-dir results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split404/positive_nn_risk_union_top40/eval_50ep --checkpoint-glob 'results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split404/positive_nn_risk_union_top40/train/**/models/model_epoch_*.pth' --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/setup/demo_weights.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json --out-dir results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/eval --checkpoint results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/train/can_paired_pos40_bad80_split404_weighted_bc_policy0_official_bc_rnn/20260625143118/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```

Remaining:

```bash
# none
```

### Can 40p/80b Split 505

Completed:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split505/positive_nn_risk_union_top40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper_v02/splits/can_paired_pos40_bad80_split505/split_indices.json --out-dir results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split505/positive_nn_risk_union_top40/eval_50ep --checkpoint results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split505/positive_nn_risk_union_top40/train/v02fresh_can40_s505_positive_nn_risk_union_top40_seed0_bc_rnn_e200/20260625144046/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
```

Remaining:

```bash
# none
```

### Lift MG Splits 404 And 505

Completed with direct train/eval commands. Reports:

- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_weighted_bc_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_weighted_bc_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_positive_only_nn_policy0/eval/REPORT.md`

Remaining:

```bash
# none
```

## Stop Rule

After each split finishes, regenerate task summaries with five split seeds in a
separate draft directory until all endpoints are complete:

```bash
python scripts/summarize_v02_fresh_can_endpoint.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables/a1_endpoint_5split --split-seeds 101 202 303 404 505
python scripts/summarize_v02_fresh_lift_endpoint.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables/a1_endpoint_5split --split-seeds 101 202 303 404 505
```

Only promote five-split numbers into the paper if both task summaries have all
required endpoint rows for seeds `101`, `202`, `303`, `404`, and `505`.
At promotion time, regenerate the canonical task summaries under
`results/final_paper_v02/tables/`, then run `summarize_v02_fresh_gate.py` and
the uncertainty audit. The combined gate script reads the canonical task
summary CSVs from `results/final_paper_v02/tables/`.
