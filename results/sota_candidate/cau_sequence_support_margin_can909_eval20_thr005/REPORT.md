# Robomimic Router Policy Evaluation

Split path: `results/candidate_f_can_fresh_validation/splits/can_paired_pos40_bad80_split909/split_indices.json`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `400`.
Router mode: `positive_anchor_margin`.
Support mode: `labeled`.
Switch threshold: `0.05`.
Initial gate threshold: `3.0`.
Initial gate margin threshold: `0.0`.
Initial feature: `anchor_logp_under_alt`.
Initial feature threshold: `0.0`.
Effective initial feature threshold: `0.0`.
Initial feature threshold source: `literal`.
Initial feature quantile: `0.25`.
Initial feature direction: `lt`.
Initial policy feature: `alt_logp_margin_vs_anchor`.
Initial policy feature threshold: `0.0`.
Initial policy feature direction: `gt`.
Initial policy feature 2: ``.
Initial policy feature threshold 2: `0.0`.
Initial policy feature direction 2: `gt`.
Initial policy feature operator: `and`.
Temporal persistence steps: `10`.
Isolated policy RNG: `True`.
Policies: `positive, cau`.

## Metrics

| router | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| positive_anchor_margin_labeled_thr0.05_initthr3_initmarginthr0_positivebias0_caubias0 | 0.800 | 0.800 | 165.1 | 20 |

## Action Choice Counts

| policy | count |
| --- | ---: |
| positive | 2209 |
| cau | 1093 |
