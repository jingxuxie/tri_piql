# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `150`.
Router mode: `initial_gmm_feature_force_alt`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Initial feature: `anchor_logp_under_alt`.
Initial feature threshold: `6.269868`.
Initial feature direction: `lt`.
Isolated policy RNG: `True`.
Policies: `positive, triage`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| initial_gmm_feature_force_alt_labeled_thr0_initthr3_positivebias0_triagebias0 | 0.640 | 0.640 | 78.1 | 50 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 2717 |
| triage | 1189 |
