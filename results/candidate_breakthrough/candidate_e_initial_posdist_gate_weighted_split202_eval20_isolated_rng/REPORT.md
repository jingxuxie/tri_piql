# Robomimic Router Policy Evaluation

Split path: `results/final_paper_v02/splits/can_paired_pos40_bad80_split202/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `400`.
Router mode: `initial_anchor_pos_dist_force_alt`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Isolated policy RNG: `True`.
Policies: `positive, weighted`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| initial_anchor_pos_dist_force_alt_labeled_thr0_initthr3_positivebias0_weightedbias0 | 0.850 | 0.850 | 175.2 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 3504 |
| weighted | 0 |
