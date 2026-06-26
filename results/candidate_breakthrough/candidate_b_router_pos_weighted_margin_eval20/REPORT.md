# Robomimic Router Policy Evaluation

Split path: `results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `400`.
Router mode: `positive_anchor_margin`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Policies: `positive, weighted`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| positive_anchor_margin_labeled_thr0_positivebias0.25_weightedbias0 | 0.750 | 0.750 | 176.7 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 2894 |
| weighted | 640 |
