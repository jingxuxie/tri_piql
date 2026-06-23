# Can 40p/80b Seed-0 Endpoint 50-Episode Check

This diagnostic estimates evaluation noise for the original Can 40 positive / 80 bad seed-0 fixed-20k comparison.

Protocol:

- Task/split: Robomimic Can paired low-dim, 40 labeled positives / 80 labeled bads.
- Checkpoints: original seed-0 fixed-20k checkpoints from the three-seed table.
- Evaluation: 50 held-out validation-positive initial-state rollouts, horizon 400.
- The 50 rollouts cycle over the same 10 validation-positive initial states five times.

## Endpoint Results

| method | 20k success | episodes | approximate SE | approximate 95% CI |
|---|---:|---:|---:|---:|
| adaptive masscap | 0.700 | 50 | 0.065 | [0.573, 0.827] |
| weighted probability sampler | 0.560 | 50 | 0.070 | [0.422, 0.698] |

The original 10-episode seed-0 endpoint results were `0.800` for masscap and `0.500` for weighted BC. With 50 episodes, the gap narrows to `0.140`.

## Per-Initial-State Pattern

| initial state | masscap | weighted | difference |
|---|---:|---:|---:|
| demo_5 | 0/5 | 0/5 | 0.000 |
| demo_29 | 5/5 | 5/5 | 0.000 |
| demo_39 | 0/5 | 0/5 | 0.000 |
| demo_45 | 5/5 | 3/5 | 0.400 |
| demo_53 | 2/5 | 0/5 | 0.400 |
| demo_81 | 5/5 | 2/5 | 0.600 |
| demo_89 | 5/5 | 5/5 | 0.000 |
| demo_99 | 4/5 | 3/5 | 0.200 |
| demo_105 | 5/5 | 5/5 | 0.000 |
| demo_189 | 4/5 | 5/5 | -0.200 |

## Interpretation

- The direction remains favorable to masscap on seed 0, but the 50-episode estimate is less dramatic than the original 10-episode estimate.
- The gap is concentrated on a few initial states rather than being uniform across all starts.
- The approximate binomial confidence intervals overlap, so this should be treated as an evaluation-noise caveat, not a standalone statistical proof.
- The main Can 40p/80b claim should continue to rely on the three-seed fixed-budget table and the checkpoint/long-budget diagnostics, while noting that 10-episode per-checkpoint evaluations are noisy.

## Artifacts

- Masscap eval: `results/robomimic_can40_seed0_endpoint_50ep_masscap_eval/REPORT.md`
- Weighted eval: `results/robomimic_can40_seed0_endpoint_50ep_weighted_eval/REPORT.md`
- Endpoint CSV: `endpoint_summary.csv`
- Per-initial-state CSV: `per_initial_state.csv`
