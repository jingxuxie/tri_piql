# Dense PointMaze Action-Rerank Two-Seed Summary

Dataset: `D4RL/pointmaze/large-dense-v2`

Artifacts:

- `results/minari_pointmaze_large_dense_action_rerank/REPORT.md`
- `results/minari_pointmaze_large_dense_action_rerank_seed1/REPORT.md`

Both runs used:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_action_rerank_smoke.py \
  D4RL/pointmaze/large-dense-v2 \
  --bc-steps 700 --classifier-steps 500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 10 --eval-horizon 800 \
  --candidate-count 64 \
  --noise-stds 0.10 0.25 \
  --action-penalties 0.05 0.20
```

## Aggregate Metrics

| method | success mean | success values | dense return mean |
|---|---:|---|---:|
| BC-positive | 0.300 | 0.200, 0.400 | 49.848 |
| weighted BC, obs classifier | 0.250 | 0.200, 0.300 | 51.098 |
| state-action rerank, noise 0.10, penalty 0.05 | 0.200 | 0.300, 0.100 | 65.496 |
| state-action rerank, noise 0.10, penalty 0.20 | 0.150 | 0.200, 0.100 | 68.563 |
| state-action rerank, noise 0.25, penalty 0.05 | 0.300 | 0.300, 0.300 | 57.964 |
| state-action rerank, noise 0.25, penalty 0.20 | 0.200 | 0.300, 0.100 | 56.867 |

## Interpretation

- The state-action classifier learns a real labeled distinction: labeled accuracy is 0.825 on seed 0 and 0.809 on seed 1.
- Reranking improves dense return substantially in several settings.
- Success-rate gains are not yet robust. The best two-seed success mean ties BC-positive at 0.300 rather than beating it.
- This is more promising than AWBC on PointMaze, but still not paper-strength. The next useful refinement is to make the reranker more goal-aware and less dense-reward-greedy, or move to a benchmark where dense return and task success align better.
