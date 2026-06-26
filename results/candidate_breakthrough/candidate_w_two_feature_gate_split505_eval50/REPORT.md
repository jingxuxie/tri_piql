# Robomimic Router Policy Evaluation

Split path: `results/final_paper_v02/splits/can_paired_pos40_bad80_split505/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `400`.
Router mode: `initial_anchor_pos_dist_margin_force_alt`.
Support mode: `labeled`.
Switch threshold: `0.0`.
Initial gate threshold: `3.0`.
Initial gate margin threshold: `0.0`.
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
| initial_anchor_pos_dist_margin_force_alt_labeled_thr0_initthr3_initmarginthr0_positivebias0_weightedbias0 | 0.780 | 0.780 | 176.3 | 50 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 8053 |
| weighted | 762 |
