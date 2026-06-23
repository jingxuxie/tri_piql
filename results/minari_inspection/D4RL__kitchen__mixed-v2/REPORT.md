# Minari Inspection: `D4RL/kitchen/mixed-v2`

## Command

```bash
scripts/inspect_minari_dataset.py D4RL/kitchen/mixed-v2 --out-dir results/minari_inspection --top-frac 0.10 --bottom-frac 0.20 --score-mode return --seed 0
```

## Dataset

- Total episodes: `621`.
- Total steps: `156560`.
- Inspected episodes: `621`.
- Observation space: `Dict('achieved_goal': Dict('bottom burner': Box(-inf, inf, (2,), float64), 'kettle': Box(-inf, inf, (7,), float64), 'light switch': Box(-inf, inf, (2,), float64), 'microwave': Box(-inf, inf, (1,), float64)), 'desired_goal': Dict('bottom burner': Box(-inf, inf, (2,), float64), 'kettle': Box(-inf, inf, (7,), float64), 'light switch': Box(-inf, inf, (2,), float64), 'microwave': Box(-inf, inf, (1,), float64)), 'observation': Box(-inf, inf, (59,), float64))`.
- Action space: `Box(-1.0, 1.0, (9,), float64)`.

## Return And Length

- Return mean/std: `342.767` / `92.2887`.
- Return p10/p50/p90: `230` / `357` / `444`.
- Length mean/std: `252.11` / `52.3438`.
- Length min/p50/max: `1` / `256` / `450`.

## Score-Based Split

- Score mode: `return`.
- Score mean/std: `342.767` / `92.2887`.
- Score p10/p50/p90: `230` / `357` / `444`.
- Positive trajectories: `63`.
- Negative trajectories: `125`.
- Unlabeled trajectories: `433`.
- Unique label scores: `245`.
- Largest exact score tie: `18` trajectories.
- Positive score cutoff: `444.0` with tie count `2`.
- Negative score cutoff: `282.0` with tie count `3`.
- Unique trajectory returns: `245`.
- Largest exact return tie: `18` trajectories.

## Terminal Flags

- Terminated: `0`.
- Truncated: `621`.
- Neither: `0`.

## Immediate Use

- Use `episodes.csv` for trajectory-level labels and held-out split debugging.
- Use `split_indices.json` when loading the same Minari dataset for BC, weighted BC, and Tri-PIQL.
- True rewards are used only here to define labels and diagnostics; reward learning should hide them.
