# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `150`.
Router mode: `temporal_gmm_feature`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Initial feature: `anchor_logp_under_alt`.
Initial feature threshold: `0.0`.
Effective initial feature threshold: `6.1803388595581055`.
Initial feature threshold source: `labeled_positive_quantile`.
Initial feature quantile: `0.25`.
Initial feature direction: `lt`.
Isolated policy RNG: `True`.
Policies: `positive, triage`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| temporal_gmm_feature_labeled_thr0_initthr3_positivebias0_triagebias0 | 0.350 | 0.350 | 112.7 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 107 |
| triage | 2146 |
