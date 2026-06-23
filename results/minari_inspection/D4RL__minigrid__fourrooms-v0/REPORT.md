# Minari Inspection: `D4RL/minigrid/fourrooms-v0`

## Command

```bash
scripts/inspect_minari_dataset.py D4RL/minigrid/fourrooms-v0 --out-dir results/minari_inspection --top-frac 0.10 --bottom-frac 0.20 --score-mode return --seed 0
```

## Dataset

- Total episodes: `590`.
- Total steps: `10010`.
- Inspected episodes: `590`.
- Observation space: `Dict('direction': Discrete(4), 'image': Box(0, 255, (7, 7, 3), uint8), 'mission': Text(1, 14, charset=                                                              ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''(),,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdeeeffghijklmnnoopqrrssttuvwxyzz{}))`.
- Action space: `Discrete(7)`.

## Return And Length

- Return mean/std: `0.847305` / `0.0695711`.
- Return p10/p50/p90: `0.757` / `0.838` / `0.946`.
- Length mean/std: `16.9661` / `7.73012`.
- Length min/p50/max: `1` / `18` / `34`.

## Score-Based Split

- Score mode: `return`.
- Score mean/std: `0.847305` / `0.0695711`.
- Score p10/p50/p90: `0.757` / `0.838` / `0.946`.
- Positive trajectories: `59`.
- Negative trajectories: `118`.
- Unlabeled trajectories: `413`.
- Unique label scores: `34`.
- Largest exact score tie: `36` trajectories.
- Positive score cutoff: `0.946` with tie count `21`.
- Negative score cutoff: `0.7929999999999999` with tie count `36`.
- Unique trajectory returns: `34`.
- Largest exact return tie: `36` trajectories.

## Terminal Flags

- Terminated: `590`.
- Truncated: `0`.
- Neither: `0`.

## Immediate Use

- Use `episodes.csv` for trajectory-level labels and held-out split debugging.
- Use `split_indices.json` when loading the same Minari dataset for BC, weighted BC, and Tri-PIQL.
- True rewards are used only here to define labels and diagnostics; reward learning should hide them.
