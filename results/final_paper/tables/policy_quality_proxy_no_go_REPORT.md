# Policy-Quality Proxy No-Go Table

This artifact consolidates the current negative evidence for simple hidden-label-free policy-quality proxies. The table is not a new endpoint experiment; it normalizes existing staged reports into the proxy categories needed for the paper appendix.

## Summary

- Coverage-only winner matches endpoint winner in `2/4` evaluated settings.
- On all endpoint-evaluated support rows, coverage-proxy Pearson/Spearman correlations with endpoint success are `-0.043`/`0.160`.
- On primary complete rows, coverage-proxy Pearson/Spearman correlations are `0.327`/`0.518`.
- Original Can MG likelihood-style proxies match the rollout-best method in `0/6` checks.
- Deployable proxy attempts match endpoint winners in `2/11` rows.
- Audit-only support rows match endpoint winners in `3/6` rows.
- Total mismatching proxy rows in this consolidated table: `12/17`.

## Proxy Family Match Counts

| proxy family | matches | total |
|---|---:|---:|
| audit-only support score | 3 | 4 |
| coverage proxy | 2 | 4 |
| initial-state and transition coverage | 0 | 1 |
| negative rejection | 0 | 2 |
| positive likelihood | 0 | 2 |
| positive-minus-negative likelihood | 0 | 2 |
| support purity plus action-risk | 0 | 1 |
| support purity plus hidden-positive recall | 0 | 1 |

## Consolidated Evidence

| setting | proxy_family | proxy_selected_method | proxy_selected_endpoint | endpoint_winner | endpoint_winner_endpoint | proxy_matches_endpoint | deployable_proxy | audit_only | support_purity | hidden_positive_recall | hidden_bad_admission |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | coverage proxy | weighted BC full pool | 90/150 | positive-NN/risk union top40 | 116/150 | false | true | false | 0.333 | 1.000 | 1.000 |
| Lift MG | coverage proxy | weighted BC | 93/150 | weighted BC | 93/150 | true | true | false | 0.194 | 1.000 | 1.000 |
| Can 20p/80b | coverage proxy | weighted BC full pool | 18/50 | positive-only NN top20 | 54/100 | false | true | false | 0.200 | 1.000 | 1.000 |
| Can 80p/80b | coverage proxy | positive-only NN top80 | 49/50 | positive-only NN top80 | 49/50 | true | true | false | 0.917 | 0.917 | 0.083 |
| Can 40p/80b | audit-only support score | positive-NN/risk union top40 | 116/150 | positive-NN/risk union top40 | 116/150 | true | false | true | 0.881 | 0.992 | 0.067 |
| Lift MG | audit-only support score | classifier top-k | 68/150 | weighted BC | 93/150 | false | false | true | 0.963 | 0.558 | 0.005 |
| Can 20p/80b | audit-only support score | positive-only NN top20 | 54/100 | positive-only NN top20 | 54/100 | true | false | true | 0.817 | 0.817 | 0.046 |
| Can 80p/80b | audit-only support score | positive-only NN top80 | 49/50 | positive-only NN top80 | 49/50 | true | false | true | 0.917 | 0.917 | 0.083 |
| Can MG original | positive likelihood | allpositive | 0.200 | weighted | 0.333 | false | true | false |  |  |  |
| Can MG original | positive likelihood | allpositive | 0.200 | weighted | 0.333 | false | true | false |  |  |  |
| Can MG original | positive-minus-negative likelihood | allpositive | 0.200 | weighted | 0.333 | false | true | false |  |  |  |
| Can MG original | positive-minus-negative likelihood | allpositive | 0.200 | weighted | 0.333 | false | true | false |  |  |  |
| Can MG original | negative rejection | allpositive | 0.200 | weighted | 0.333 | false | true | false |  |  |  |
| Can MG original | negative rejection | allpositive | 0.200 | weighted | 0.333 | false | true | false |  |  |  |
| Can 40p/80b split 11+22 | support purity plus action-risk | positive-NN/risk fusion top40 | 73/100 | positive-only NN top40 | 80/100 | false | false | true | 0.988 | 0.988 | 0.006 |
| Lift MG | support purity plus hidden-positive recall | classifier-score top160 | 68/150 | weighted BC | 93/150 | false | false | true | 0.963 | 0.558 | 0.005 |
| Can 40p/80b split 22 | initial-state and transition coverage | positive-NN/risk fusion top40 | 32/50 | positive-only NN top40 | 38/50 | false | true | false | 1.000 | 1.000 | 0.000 |

## Interpretation

- Positive likelihood, positive-minus-negative likelihood, and negative rejection fail on original Can MG: all select all-positive hard support, while weighted BC is rollout-best.
- Coverage-only selection is useful for Lift but over-selects broad weighted support in contaminated Can settings.
- Support purity and hidden-positive recall are not sufficient: action-risk Can support and Lift classifier top-k look strong in audit space but lose endpoint comparisons.
- Initial-state and transition nearest-neighbor coverage is descriptive but not enough to decide between high-purity support candidates.

## Paper Claim

> Policy-quality prediction remains an open problem: a score that separates positives and negatives, a pure selected support set, or a simple coverage proxy is not enough to choose the best policy-training branch.

## Outputs

- `results/final_paper/tables/policy_quality_proxy_no_go.csv`
- `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`
