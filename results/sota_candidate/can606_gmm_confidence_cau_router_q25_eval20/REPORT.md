# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `400`.
Router mode: `initial_gmm_feature_force_alt`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Initial gate margin threshold: `0.0`.
Initial feature: `anchor_logp_under_alt`.
Initial feature threshold: `0.0`.
Effective initial feature threshold: `15.074508666992188`.
Initial feature threshold source: `labeled_positive_quantile`.
Initial feature quantile: `0.25`.
Initial feature direction: `lt`.
Temporal persistence steps: `10`.
Isolated policy RNG: `True`.
Policies: `positive, cau`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| initial_gmm_feature_force_alt_labeled_thr0_initthr3_initmarginthr0_positivebias0_caubias0 | 0.800 | 0.800 | 163.9 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 2270 |
| cau | 1009 |
