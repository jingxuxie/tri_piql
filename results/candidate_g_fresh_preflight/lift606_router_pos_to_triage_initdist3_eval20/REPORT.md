# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `150`.
Router mode: `initial_anchor_pos_dist_force_alt`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Isolated policy RNG: `True`.
Policies: `positive, triage`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| initial_anchor_pos_dist_force_alt_labeled_thr0_initthr3_positivebias0_triagebias0 | 0.700 | 0.700 | 70.2 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 1405 |
| triage | 0 |
