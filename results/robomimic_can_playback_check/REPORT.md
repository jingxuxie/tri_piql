# Robomimic Playback Check

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Demo source: `valid_positive`.
Environment: `PickPlaceCan` version `1.5.1`.
Demos replayed: `10`.
Playback success rate: `1.000`.

| demo | success | replay return | replay length | stored return | stored length |
|---|---:|---:|---:|---:|---:|
| demo_5 | 1 | 1.000 | 112 | 5.000 | 115 |
| demo_29 | 1 | 1.000 | 125 | 5.000 | 128 |
| demo_39 | 1 | 1.000 | 129 | 5.000 | 133 |
| demo_45 | 1 | 1.000 | 108 | 5.000 | 111 |
| demo_53 | 1 | 1.000 | 116 | 5.000 | 118 |
| demo_81 | 1 | 1.000 | 118 | 5.000 | 121 |
| demo_89 | 1 | 1.000 | 92 | 5.000 | 95 |
| demo_99 | 1 | 1.000 | 118 | 5.000 | 121 |
| demo_105 | 1 | 1.000 | 96 | 5.000 | 99 |
| demo_189 | 1 | 1.000 | 83 | 5.000 | 86 |

## Interpretation

- Stored simulator XML/state plus stored actions replay successfully when this rate is high.
- If learned policy rollouts fail while playback succeeds, the issue is policy strength or closed-loop imitation, not basic simulator reconstruction.
