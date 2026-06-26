# Hard-Union Component Ablation

This artifact consolidates the v0.2 Can 40p/80b hard-union component evidence.
It does not add new policy training; it normalizes existing support audits and endpoint gates.

## Aggregate Component Table

| method_label | component_role | selected_unlabeled | hidden_positive_selected | hidden_bad_selected | hidden_positive_recall | hidden_bad_admission | endpoint_success_count | endpoint_delta_vs_positive_same_splits | endpoint_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| positive-only NN top40 | positive-only anchor | 120 | 106 | 14 | 0.883 | 0.058 | 108/150 | +0.000 | complete_3split_endpoint |
| risk-fusion top40 | risk branch alone | 120 | 117 | 3 | 0.975 | 0.013 | 73/100 | -0.070 | partial_2split_endpoint |
| positive-NN/risk union top40 | union candidate | 135 | 119 | 16 | 0.992 | 0.067 | 116/150 | +0.053 | complete_3split_endpoint |
| classifier-only top40 | classifier-only hard support | 120 | 85 | 35 | 0.708 | 0.146 |  |  | support_only |
| weighted BC full pool | soft coverage baseline | 360 | 120 | 240 | 1.000 | 1.000 | 90/150 | -0.120 | complete_3split_endpoint |
| v0.1 adaptive masscap | v0.1 hard support | 190 | 110 | 80 | 0.917 | 0.333 | 99/150 | -0.060 | complete_3split_endpoint |

## Per-Split Endpoint Table

| split_seed | method_label | hidden_positive_selected | hidden_bad_selected | endpoint_success_count | endpoint_delta_vs_positive | endpoint_status |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | positive-only NN top40 | 36 | 4 | 42/50 | +0.000 | endpoint |
| 11 | risk-fusion top40 | 39 | 1 | 41/50 | -0.020 | endpoint |
| 11 | positive-NN/risk union top40 | 40 | 5 | 38/50 | -0.080 | endpoint |
| 11 | weighted BC full pool | 40 | 80 | 36/50 | -0.120 | endpoint |
| 11 | v0.1 adaptive masscap | 40 | 30 | 38/50 | -0.080 | endpoint |
| 22 | positive-only NN top40 | 37 | 3 | 38/50 | +0.000 | endpoint |
| 22 | risk-fusion top40 | 40 | 0 | 32/50 | -0.120 | endpoint |
| 22 | positive-NN/risk union top40 | 40 | 3 | 39/50 | +0.020 | endpoint |
| 22 | weighted BC full pool | 40 | 80 | 22/50 | -0.320 | endpoint |
| 22 | v0.1 adaptive masscap | 36 | 37 | 26/50 | -0.240 | endpoint |
| 33 | positive-only NN top40 | 33 | 7 | 28/50 | +0.000 | endpoint |
| 33 | risk-fusion top40 | 38 | 2 |  |  | support_only |
| 33 | positive-NN/risk union top40 | 39 | 8 | 39/50 | +0.220 | endpoint |
| 33 | weighted BC full pool | 40 | 80 | 32/50 | +0.080 | endpoint |
| 33 | v0.1 adaptive masscap | 34 | 13 | 35/50 | +0.140 | endpoint |

## Interpretation

- Positive-only NN top40 is the required baseline: it selects `106/120` hidden positives and `14/240` hidden bad demos, then reaches `108/150`.
- Risk-fusion top40 improves the support audit to `117/120` hidden positives and `3/240` hidden bad demos, but its two-split endpoint is `73/100`, `-0.070` versus positive-only on the same split seeds.
- The union keeps the positive-only anchor and adds risk-fusion coverage, selecting `119/120` hidden positives and `16/240` hidden bad demos. It reaches `116/150`, `+0.053` versus positive-only over all three splits.
- Classifier-only top40 is support-only and is dominated by positive-only top40: `85/120` hidden positives and `35/240` hidden bad demos.
- Weighted BC has full coverage but full hidden-bad admission (`240/240`) and reaches `90/150`. v0.1 adaptive masscap reaches `99/150` while admitting `80/240` bad demos.

## Answer

The union helps because it combines both mechanisms: it preserves the strong positive-only anchor while adding risk-derived coverage. Risk-fusion alone gives the cleanest hidden-label support but is not endpoint-best on its evaluated splits, and classifier-only hard support is not competitive. The pooled union gain comes mainly from split 22 and split 33; split 11 still favors positive-only NN.

## Outputs

- `results/final_paper/tables/hard_union_component_ablation.csv`
- `results/final_paper/tables/hard_union_component_ablation_per_split.csv`
- `results/final_paper/tables/hard_union_component_ablation_REPORT.md`
