# CAU Sequence Support-Margin Router

This short screen evaluates a per-step support-margin router between positive-only and CAU.
The router starts from positive-only and chooses CAU only when CAU's labeled state-action support margin exceeds the positive anchor by `--switch-threshold`.

## Decision

- On split909, threshold `0.0` is too aggressive: router `11/20` versus positive-only `15/20` and CAU `9/20`.
- On split909, threshold `0.25` reaches `16/20` versus positive-only `15/20`, with `2` gains and `1` loss.
- The same threshold preserves split808: router `17/20` versus positive-only `17/20` and CAU `14/20`, with `0` losses.
- The same threshold misses split707 CAU upside: router `15/20` versus positive-only `15/20` and CAU `20/20`.
- Relaxing split707 to threshold `0.10` is not enough: router `15/20` with `1` gain and `1` loss versus positive-only.
- Fixed threshold `0.05` is the best short-screen setting so far: aggregate router `51/60` versus positive-only `47/60` and CAU `43/60`, with `5` gains and `1` loss versus positive-only.
- Threshold `0.05` reaches split909 `16/20`, split808 `18/20`, and split707 `17/20`; this is promising short-screen evidence, but the 50-episode validations below are mixed.
- The first no-retune held-out guardrail on split606 is neutral: threshold `0.05` reaches `16/20` versus positive-only `16/20` and CAU `15/20`, with `2` gains and `2` losses.
- Including split606, threshold `0.05` is `67/80` versus positive-only `63/80` and CAU `58/80`, with `7` gains and `3` losses.
- The 50-episode split606 no-retune validation is positive: threshold `0.05` reaches `42/50` versus positive-only `38/50` and CAU `41/50`, with `7` gains and `3` losses versus positive-only.
- The 50-episode split101 no-retune validation is mixed-negative: threshold `0.05` reaches `25/50` versus positive-only `19/50` but remains below CAU `33/50`.
- Across the two 50-episode no-retune validations, the router is `67/100` versus positive-only `57/100` and CAU `74/100`, with `15` gains and `5` losses versus positive-only.
- A persistent support-margin variant does not fix split101: k=10 reaches `20/50` versus non-persistent `25/50` and CAU `33/50`.

## Screen Rows

| screen_id | router_score | positive_score | cau_score | delta_vs_positive | gains_vs_positive | losses_vs_positive | choices_positive | choices_cau |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split909_thr0 | 11/20 | 15/20 | 9/20 | -4 | 1 | 5 | 2108 | 2656 |
| split101_thr005_eval50 | 25/50 | 19/50 | 33/50 | 6 | 8 | 2 | 8055 | 4595 |
| split101_persistent_thr005_k10_eval50 | 20/50 | 19/50 | 33/50 | 1 | 3 | 2 | 6845 | 7571 |
| split909_thr005 | 16/20 | 15/20 | 9/20 | 1 | 2 | 1 | 2209 | 1093 |
| split909_thr025 | 16/20 | 15/20 | 9/20 | 1 | 2 | 1 | 3022 | 206 |
| split606_thr005_heldout | 16/20 | 16/20 | 15/20 | 0 | 2 | 2 | 2362 | 873 |
| split606_thr005_eval50 | 42/50 | 38/50 | 41/50 | 4 | 7 | 3 | 5496 | 2005 |
| split808_thr005 | 18/20 | 17/20 | 14/20 | 1 | 1 | 0 | 1909 | 789 |
| split808_thr025 | 17/20 | 17/20 | 14/20 | 0 | 0 | 0 | 2914 | 110 |
| split707_thr025 | 15/20 | 15/20 | 20/20 | 0 | 0 | 0 | 3275 | 316 |
| split707_thr010 | 15/20 | 15/20 | 20/20 | 0 | 1 | 1 | 2826 | 728 |
| split707_thr005 | 17/20 | 15/20 | 20/20 | 2 | 2 | 0 | 2061 | 891 |

## Artifacts

- Summary CSV: `results/sota_candidate/cau_sequence_support_router_summary.csv`.
- split909_thr0 report: `results/sota_candidate/cau_sequence_support_margin_can909_eval20_thr0/REPORT.md`.
- split101_thr005_eval50 report: `results/sota_candidate/cau_sequence_support_margin_can101_eval50_thr005/REPORT.md`.
- split101_persistent_thr005_k10_eval50 report: `results/sota_candidate/cau_sequence_support_margin_persistent_can101_eval50_thr005_k10/REPORT.md`.
- split909_thr005 report: `results/sota_candidate/cau_sequence_support_margin_can909_eval20_thr005/REPORT.md`.
- split909_thr025 report: `results/sota_candidate/cau_sequence_support_margin_can909_eval20_thr025/REPORT.md`.
- split606_thr005_heldout report: `results/sota_candidate/cau_sequence_support_margin_can606_eval20_thr005/REPORT.md`.
- split606_thr005_eval50 report: `results/sota_candidate/cau_sequence_support_margin_can606_eval50_thr005/REPORT.md`.
- split808_thr005 report: `results/sota_candidate/cau_sequence_support_margin_can808_eval20_thr005/REPORT.md`.
- split808_thr025 report: `results/sota_candidate/cau_sequence_support_margin_can808_eval20_thr025/REPORT.md`.
- split707_thr025 report: `results/sota_candidate/cau_sequence_support_margin_can707_eval20_thr025/REPORT.md`.
- split707_thr010 report: `results/sota_candidate/cau_sequence_support_margin_can707_eval20_thr010/REPORT.md`.
- split707_thr005 report: `results/sota_candidate/cau_sequence_support_margin_can707_eval20_thr005/REPORT.md`.
