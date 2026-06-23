# Minari Inspection: `D4RL/pointmaze/large-v2`

## Command

```bash
scripts/inspect_minari_dataset.py D4RL/pointmaze/large-v2 --out-dir results/minari_inspection --top-frac 0.10 --bottom-frac 0.20 --score-mode return_length --seed 0
```

## Dataset

- Total episodes: `3360`.
- Total steps: `1000000`.
- Inspected episodes: `3360`.
- Observation space: `Dict('achieved_goal': Box(-inf, inf, (2,), float64), 'desired_goal': Box(-inf, inf, (2,), float64), 'observation': Box(-inf, inf, (4,), float64))`.
- Action space: `Box(-1.0, 1.0, (2,), float32)`.

## Return And Length

- Return mean/std: `0.998512` / `0.0385471`.
- Return p10/p50/p90: `1` / `1` / `1`.
- Length mean/std: `297.619` / `166.04`.
- Length min/p50/max: `1` / `290` / `797`.

## Score-Based Split

- Score mode: `return_length`.
- Score mean/std: `998214` / `38540.1`.
- Score p10/p50/p90: `999471` / `999709` / `999922`.
- Positive trajectories: `336`.
- Negative trajectories: `672`.
- Unlabeled trajectories: `2352`.
- Unique label scores: `686`.
- Largest exact score tie: `16` trajectories.
- Positive score cutoff: `999922.0` with tie count `7`.
- Negative score cutoff: `999554.0` with tie count `5`.
- Unique trajectory returns: `2`.
- Largest exact return tie: `3355` trajectories.

## Terminal Flags

- Terminated: `0`.
- Truncated: `3360`.
- Neither: `0`.

## Immediate Use

- Use `episodes.csv` for trajectory-level labels and held-out split debugging.
- Use `split_indices.json` when loading the same Minari dataset for BC, weighted BC, and Tri-PIQL.
- True rewards are used only here to define labels and diagnostics; reward learning should hide them.
