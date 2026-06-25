# Primary Endpoint Uncertainty Summary

This report adds descriptive uncertainty summaries to the primary frozen Robomimic endpoint matrix.
Wilson intervals treat the pooled 150 rollouts as Bernoulli trials, while split means and standard deviations summarize variation across the three frozen split seeds.
Because rollouts reuse validation-positive start pools within each split, these intervals should be read as descriptive error bars, not as fully independent statistical tests.

## Pooled Rates And Split Variation

| task | method | successes | episodes | pooled_success_rate | wilson95_low | wilson95_high | split_mean | split_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | all-demo BC | 81 | 150 | 0.540 | 0.460 | 0.618 | 0.540 | 0.035 |
| Can 40p/80b | weighted BC | 90 | 150 | 0.600 | 0.520 | 0.675 | 0.600 | 0.144 |
| Can 40p/80b | positive-only NN | 108 | 150 | 0.720 | 0.643 | 0.786 | 0.720 | 0.144 |
| Can 40p/80b | TRIAGE-BC | 99 | 150 | 0.660 | 0.581 | 0.731 | 0.660 | 0.125 |
| Can 40p/80b | all-positive oracle | 147 | 150 | 0.980 | 0.943 | 0.993 | 0.980 | 0.000 |
| Lift MG | all-demo BC | 31 | 150 | 0.207 | 0.150 | 0.278 | 0.207 | 0.050 |
| Lift MG | weighted BC | 93 | 150 | 0.620 | 0.540 | 0.694 | 0.620 | 0.125 |
| Lift MG | positive-only NN | 82 | 150 | 0.547 | 0.467 | 0.624 | 0.547 | 0.117 |
| Lift MG | TRIAGE-BC | 74 | 150 | 0.493 | 0.414 | 0.573 | 0.493 | 0.050 |
| Lift MG | all-positive oracle | 105 | 150 | 0.700 | 0.622 | 0.768 | 0.700 | 0.053 |

## Paired Split Deltas

| task | comparison | pooled_delta | split_mean_delta | split_std_delta | direction_consistent |
| --- | --- | --- | --- | --- | --- |
| Can 40p/80b | TRIAGE-BC - weighted BC | 0.060 | 0.060 | 0.020 | true |
| Can 40p/80b | TRIAGE-BC - all-demo BC | 0.120 | 0.120 | 0.151 | false |
| Can 40p/80b | TRIAGE-BC - positive-only NN | -0.060 | -0.060 | 0.191 | false |
| Lift MG | weighted BC - TRIAGE-BC | 0.127 | 0.127 | 0.172 | false |
| Lift MG | weighted BC - positive-only NN | 0.073 | 0.073 | 0.129 | false |
| Lift MG | TRIAGE-BC - all-demo BC | 0.287 | 0.287 | 0.012 | true |

## Interpretation

- Can 40p/80b favors TRIAGE-BC over weighted BC on every split, but the pooled gap is small (`+0.060`) and the rollout-level Wilson intervals overlap.
- Can 40p/80b does not support a TRIAGE-over-positive-only claim: positive-only NN is higher pooled and the split deltas change sign.
- Lift MG favors weighted BC over TRIAGE-BC pooled (`+0.127`) and on two of three splits, while all-demo BC remains consistently weak.
- These summaries support cautious wording: report counts, split context, and direction of paired split deltas rather than making strong significance claims.
