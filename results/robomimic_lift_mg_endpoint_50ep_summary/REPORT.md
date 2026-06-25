# Lift MG Endpoint 50-Episode Check

This diagnostic re-evaluates the fixed-20k Lift MG endpoint for the core bad-aware, soft-weighted, and no-bad-label controls.

Protocol:

- Task/split: Robomimic Lift MG sparse low-dim, original split.
- Checkpoints: original fixed-20k checkpoints from the three-seed table.
- Evaluation: 50 held-out validation-positive initial-state rollouts per seed and method, horizon 150.
- The split has 30 validation-positive initial states; 50 rollouts cycle through that ordered set, so the first 20 starts are visited twice per seed and the remaining 10 once per seed.

## Seed Results

| method | seed | 10 ep 20k | 50 ep 20k |
|---|---:|---:|---:|
| bad-aware pos-min | 0 | 0.800 | 0.680 |
| bad-aware pos-min | 1 | 0.400 | 0.520 |
| bad-aware pos-min | 2 | 0.800 | 0.600 |
| weighted probability sampler | 0 | 0.500 | 0.540 |
| weighted probability sampler | 1 | 0.700 | 0.560 |
| weighted probability sampler | 2 | 0.400 | 0.500 |
| positive-only NN top160 | 0 | 0.500 | 0.620 |
| positive-only NN top160 | 1 | 0.600 | 0.500 |
| positive-only NN top160 | 2 | 0.600 | 0.560 |

## Aggregate Results

| method | 10 ep mean | 50 ep seed mean | 50 ep pooled | approx 95% CI |
|---|---:|---:|---:|---:|
| bad-aware pos-min | 0.667 | 0.600 +/- 0.065 | 0.600 (90/150) | [0.522, 0.678] |
| weighted probability sampler | 0.533 | 0.533 +/- 0.025 | 0.533 (80/150) | [0.453, 0.613] |
| positive-only NN top160 | 0.567 | 0.560 +/- 0.049 | 0.560 (84/150) | [0.481, 0.639] |

## Per-Initial-State Pattern

| initial state | pos-min | weighted | pos-only | pos-min - weighted | pos-min - pos-only |
|---|---:|---:|---:|---:|---:|
| demo_1023 | 5/6 | 4/6 | 6/6 | 0.167 | -0.167 |
| demo_1035 | 6/6 | 2/6 | 4/6 | 0.667 | 0.333 |
| demo_1161 | 4/6 | 6/6 | 5/6 | -0.333 | -0.167 |
| demo_1202 | 3/6 | 2/6 | 5/6 | 0.167 | -0.333 |
| demo_1229 | 2/6 | 3/6 | 2/6 | -0.167 | 0.000 |
| demo_1240 | 2/6 | 6/6 | 3/6 | -0.667 | -0.167 |
| demo_1242 | 4/6 | 5/6 | 2/6 | -0.167 | 0.333 |
| demo_1249 | 5/6 | 3/6 | 3/6 | 0.333 | 0.333 |
| demo_1260 | 6/6 | 2/6 | 4/6 | 0.667 | 0.333 |
| demo_1277 | 1/6 | 1/6 | 1/6 | 0.000 | 0.000 |
| demo_1280 | 5/6 | 4/6 | 3/6 | 0.167 | 0.333 |
| demo_1281 | 5/6 | 5/6 | 4/6 | 0.000 | 0.167 |
| demo_1295 | 0/6 | 2/6 | 2/6 | -0.333 | -0.333 |
| demo_1297 | 5/6 | 2/6 | 2/6 | 0.500 | 0.500 |
| demo_1303 | 5/6 | 4/6 | 2/6 | 0.167 | 0.500 |
| demo_1311 | 2/6 | 3/6 | 3/6 | -0.167 | -0.167 |
| demo_1316 | 3/6 | 4/6 | 3/6 | -0.167 | 0.000 |
| demo_1343 | 1/3 | 1/3 | 2/3 | 0.000 | -0.333 |
| demo_1386 | 2/3 | 3/3 | 3/3 | -0.333 | -0.333 |
| demo_1391 | 2/3 | 1/3 | 0/3 | 0.333 | 0.667 |
| demo_1392 | 2/3 | 1/3 | 1/3 | 0.333 | 0.333 |
| demo_1401 | 0/3 | 1/3 | 1/3 | -0.333 | -0.333 |
| demo_1415 | 1/3 | 0/3 | 1/3 | 0.333 | 0.000 |
| demo_1439 | 2/3 | 1/3 | 3/3 | 0.333 | -0.333 |
| demo_1475 | 1/3 | 2/3 | 2/3 | -0.333 | -0.333 |
| demo_1481 | 3/3 | 2/3 | 2/3 | 0.333 | 0.333 |
| demo_1488 | 3/3 | 1/3 | 2/3 | 0.667 | 0.333 |
| demo_365 | 3/6 | 4/6 | 5/6 | -0.167 | -0.333 |
| demo_541 | 5/6 | 5/6 | 5/6 | 0.000 | 0.000 |
| demo_965 | 2/6 | 0/6 | 3/6 | 0.333 | -0.167 |

## Interpretation

- Bad-aware pos-min remains ahead of weighted BC at the fixed 20k endpoint: `0.600` versus `0.533`.
- The bad-aware edge over positive-only NN top160 is much smaller: `0.600` versus `0.560`.
- The 50-episode check weakens any strong bad-label-necessity claim on Lift; the better claim is calibrated bad labels improve the fixed-budget coverage-quality tradeoff, while positive-only retrieval remains a strong baseline.
- Approximate pooled binomial intervals overlap, so this is a robustness/caveat check rather than a standalone statistical proof.

## Artifacts

- `endpoint_summary.csv`
- `aggregate_summary.csv`
- `per_initial_state.csv`
- Seed-level evaluator reports: `results/robomimic_lift_mg_seed{0,1,2}_endpoint_50ep_{posmin,weighted,posonly_top160}_eval/REPORT.md`
