# Robomimic Router Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `150`.
Router mode: `positive_anchor_margin`.
Support mode: `labeled_plus_positive_anchor`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Isolated policy RNG: `True`.
Policies: `positive, triage, weighted`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| positive_anchor_margin_labeled_plus_positive_anchor_thr0_initthr3_positivebias0_triagebias0_weightedbias0 | 0.500 | 0.500 | 91.2 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 675 |
| triage | 654 |
| weighted | 494 |
