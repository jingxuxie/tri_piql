# Primary Endpoint Paired Bootstrap Audit

This report summarizes paired endpoint success deltas using the staged per-episode metrics.
For each split and method pair, episode successes are first averaged by held-out `initial_demo_id`; bootstrap samples then resample split seeds and paired initial states.
This avoids treating repeated rollouts from the same validation-positive starts as fully independent.

| task | comparison | point_delta | bootstrap95_low | bootstrap95_high | split_signs | split_sign_p_two_sided | initial_states_per_split |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | TRIAGE-BC - weighted BC | 0.060 | -0.113 | 0.240 | +++ | 0.250 | 10/10/10 |
| Can 40p/80b | TRIAGE-BC - all-demo BC | 0.120 | -0.133 | 0.380 | +-+ | 1.000 | 10/10/10 |
| Can 40p/80b | TRIAGE-BC - positive-only NN | -0.060 | -0.313 | 0.200 | --+ | 1.000 | 10/10/10 |
| Lift MG | weighted BC - TRIAGE-BC | 0.122 | -0.100 | 0.317 | -++ | 1.000 | 30/30/30 |
| Lift MG | weighted BC - positive-only NN | 0.050 | -0.111 | 0.222 | --+ | 1.000 | 30/30/30 |
| Lift MG | TRIAGE-BC - all-demo BC | 0.306 | 0.211 | 0.400 | +++ | 0.250 | 30/30/30 |

## Interpretation

- Can 40p/80b keeps a directionally consistent TRIAGE-BC over weighted-BC split signal, but the paired bootstrap interval still crosses zero.
- Can 40p/80b does not support TRIAGE-BC over positive-only retrieval; the point estimate is negative and split signs are mixed.
- Lift MG supports the coverage caveat: weighted BC has a positive pooled paired delta over TRIAGE-BC, but the split signs are mixed.
- With only three split seeds, exact split-level sign tests are low power; the audit is a robustness and wording guardrail rather than a decisive significance claim.
