# Robomimic Router Policy Evaluation

Split path: `results/candidate_f_can_fresh_validation/splits/can_paired_pos40_bad80_split909/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `400`.
Router mode: `initial_anchor_pos_dist_force_alt`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Initial feature: `anchor_logp_under_alt`.
Initial feature threshold: `0.0`.
Effective initial feature threshold: `0.0`.
Initial feature threshold source: `literal`.
Initial feature quantile: `0.25`.
Initial feature direction: `lt`.
Temporal persistence steps: `10`.
Isolated policy RNG: `True`.
Policies: `positive, weighted`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| initial_anchor_pos_dist_force_alt_labeled_thr0_initthr3_positivebias0_weightedbias0 | 0.780 | 0.780 | 168.9 | 50 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 7246 |
| weighted | 1200 |
