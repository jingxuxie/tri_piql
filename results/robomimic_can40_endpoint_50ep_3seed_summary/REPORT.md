# Can 40p/80b Three-Seed Endpoint 50-Episode Check

This diagnostic extends the seed-0 higher-episode endpoint check to all three seeds for the original Can 40 positive / 80 bad fixed-20k masscap-vs-weighted comparison.

Protocol:

- Task/split: Robomimic Can paired low-dim, 40 labeled positives / 80 labeled bads.
- Checkpoints: original fixed-20k checkpoints from the three-seed table.
- Evaluation: 50 held-out validation-positive initial-state rollouts per seed and method, horizon 400.
- The 50 rollouts cycle over the same 10 validation-positive initial states five times.

## Seed Results

| seed | masscap 10 ep | weighted 10 ep | gap 10 ep | masscap 50 ep | weighted 50 ep | gap 50 ep |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.800 | 0.500 | 0.300 | 0.700 | 0.560 | 0.140 |
| 1 | 0.600 | 0.600 | 0.000 | 0.620 | 0.500 | 0.120 |
| 2 | 0.800 | 0.600 | 0.200 | 0.720 | 0.660 | 0.060 |

## Aggregate Results

| method | 10 ep mean | 50 ep seed mean | 50 ep pooled | approx 95% CI |
|---|---:|---:|---:|---:|
| adaptive masscap | 0.733 | 0.680 +/- 0.043 | 0.680 (102/150) | [0.605, 0.755] |
| weighted probability sampler | 0.567 | 0.573 +/- 0.066 | 0.573 (86/150) | [0.494, 0.652] |

The 10-episode mean gap was `0.167`. The 50-episode mean-by-seed gap is `0.107`.

## Per-Initial-State Pattern

| initial state | masscap | weighted | difference |
|---|---:|---:|---:|
| demo_105 | 15/15 | 15/15 | 0.000 |
| demo_189 | 13/15 | 11/15 | 0.133 |
| demo_29 | 7/15 | 14/15 | -0.467 |
| demo_39 | 3/15 | 8/15 | -0.333 |
| demo_45 | 15/15 | 7/15 | 0.533 |
| demo_5 | 1/15 | 0/15 | 0.067 |
| demo_53 | 7/15 | 0/15 | 0.467 |
| demo_81 | 14/15 | 6/15 | 0.533 |
| demo_89 | 15/15 | 12/15 | 0.200 |
| demo_99 | 12/15 | 13/15 | -0.067 |

## Interpretation

- The higher-episode direction favors masscap on every seed: gaps are `0.140`, `0.120`, and `0.060`.
- The aggregate gap shrinks relative to the original 10-episode table, from `0.167` to `0.107` by seed mean.
- The approximate pooled binomial intervals still overlap, so this is not a standalone statistical proof.
- The result strengthens the main fixed-budget story because the masscap edge persists under a less noisy endpoint estimate, while also forcing the paper to describe the endpoint gap as modest.

## Artifacts

- `endpoint_summary.csv`
- `aggregate_summary.csv`
- `paired_seed_gaps.csv`
- `per_initial_state.csv`
- Seed-level evaluator reports: `results/robomimic_can40_seed{0,1,2}_endpoint_50ep_{masscap,weighted}_eval/REPORT.md`
