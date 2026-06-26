# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `150`.
Router mode: `margin`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Isolated policy RNG: `True`.
Policies: `positive, triage, weighted`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| margin_labeled_thr0_initthr3_positivebias0_triagebias0_weightedbias0 | 0.550 | 0.550 | 84.8 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 798 |
| triage | 524 |
| weighted | 373 |
