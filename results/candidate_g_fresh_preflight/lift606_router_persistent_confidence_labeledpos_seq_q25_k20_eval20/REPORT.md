# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `150`.
Router mode: `temporal_gmm_feature_persistent`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Initial feature: `anchor_logp_under_alt`.
Initial feature threshold: `0.0`.
Effective initial feature threshold: `1.7621623277664185`.
Initial feature threshold source: `labeled_positive_sequence_quantile`.
Initial feature quantile: `0.25`.
Initial feature direction: `lt`.
Temporal persistence steps: `20`.
Isolated policy RNG: `True`.
Policies: `positive, triage`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| temporal_gmm_feature_persistent_labeled_thr0_initthr3_positivebias0_triagebias0 | 0.550 | 0.550 | 85.2 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 731 |
| triage | 974 |
