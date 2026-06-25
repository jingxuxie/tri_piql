# v0.2 Action-Risk Feature Screen

This is a support-side screen over the existing hybrid candidate audit.
It uses labeled-positive and labeled-negative demos to compute hidden-label-free action-conflict and bad-neighbor risk features for each unlabeled demo.
Hidden labels are used only for audit columns and winner checks.

## Baseline Positive-NN Rows

| setting_label | candidate_label | selected_unlabeled | hidden_positive_recall | hidden_bad_admission | audit_oracle_score | action_conflict_risk_norm | bad_neighbor_risk_norm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive-NN top40 | 120 | 0.883 | 0.058 | 0.825 | 0.575 | 0.311 |
| Lift MG | positive-NN top160 | 480 | 0.413 | 0.040 | 0.373 | 0.787 | 0.449 |
| Can 20p/80b | positive-NN top20 | 60 | 0.817 | 0.046 | 0.771 | 0.298 | 0.377 |
| Can 80p/80b | positive-NN top80 | 240 | 0.917 | 0.083 | 0.833 | 0.347 | 0.241 |

## Proxy Winners

| setting_label | proxy_label | winner_label | winner_selected | winner_recall | winner_bad_admission | winner_audit_score | matches_audit_winner | dominates_positive_nn_baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | audit oracle | positive-NN top40 | 120 | 0.883 | 0.058 | 0.825 | true | false |
| Can 40p/80b | coverage only | positive-NN top80 | 240 | 0.992 | 0.504 | 0.488 | false | false |
| Can 40p/80b | classifier score only | hybrid filter pos p10 pos40 | 25 | 0.208 | 0.000 | 0.208 | false | false |
| Can 40p/80b | coverage - action risk | positive-NN top80 | 240 | 0.992 | 0.504 | 0.488 | false | false |
| Can 40p/80b | coverage - bad-neighbor risk | hybrid filter mid minpos maxneg pos40 | 97 | 0.800 | 0.004 | 0.796 | false | false |
| Can 40p/80b | coverage + classifier - both risks | hybrid filter pos min pos40 | 33 | 0.275 | 0.000 | 0.275 | false | false |
| Lift MG | audit oracle | classifier top320 | 960 | 0.859 | 0.073 | 0.786 | true | false |
| Lift MG | coverage only | classifier top480 | 1440 | 0.923 | 0.197 | 0.726 | false | false |
| Lift MG | classifier score only | classifier top80 | 240 | 0.286 | 0.001 | 0.285 | false | false |
| Lift MG | coverage - action risk | classifier top480 | 1440 | 0.923 | 0.197 | 0.726 | false | false |
| Lift MG | coverage - bad-neighbor risk | classifier top80 | 240 | 0.286 | 0.001 | 0.285 | false | false |
| Lift MG | coverage + classifier - both risks | hybrid filter pos p10 fill classifier to160 | 480 | 0.558 | 0.005 | 0.553 | false | true |
| Can 20p/80b | audit oracle | hybrid rank fusion equal top20 | 60 | 0.833 | 0.042 | 0.792 | true | true |
| Can 20p/80b | coverage only | hybrid union pos20 triage | 136 | 0.950 | 0.329 | 0.621 | false | false |
| Can 20p/80b | classifier score only | hybrid filter pos p10 pos20 | 15 | 0.250 | 0.000 | 0.250 | false | false |
| Can 20p/80b | coverage - action risk | positive-NN top40 | 120 | 0.983 | 0.254 | 0.729 | false | false |
| Can 20p/80b | coverage - bad-neighbor risk | hybrid filter pos p10 pos20 | 15 | 0.250 | 0.000 | 0.250 | false | false |
| Can 20p/80b | coverage + classifier - both risks | hybrid intersection pos20 classifier20 | 36 | 0.600 | 0.000 | 0.600 | false | false |
| Can 80p/80b | audit oracle | positive-NN top80 | 240 | 0.917 | 0.083 | 0.833 | true | false |
| Can 80p/80b | coverage only | positive-NN top160 | 480 | 1.000 | 1.000 | 0.000 | false | false |
| Can 80p/80b | classifier score only | hybrid filter pos p10 pos80 | 58 | 0.242 | 0.000 | 0.242 | false | false |
| Can 80p/80b | coverage - action risk | positive-NN top160 | 480 | 1.000 | 1.000 | 0.000 | false | false |
| Can 80p/80b | coverage - bad-neighbor risk | hybrid filter mid mean pos80 | 202 | 0.833 | 0.008 | 0.825 | false | false |
| Can 80p/80b | coverage + classifier - both risks | hybrid filter pos p10 pos80 | 58 | 0.242 | 0.000 | 0.242 | false | false |

## Primary Risk Probe Rows

| setting_label | candidate_label | selected_unlabeled | hidden_positive_recall | hidden_bad_admission | action_conflict_risk_norm | bad_neighbor_risk_norm | audit_oracle_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | classifier top40 | 120 | 0.708 | 0.146 | 0.419 | 0.563 | 0.562 |
| Can 40p/80b | TRIAGE-BC current | 190 | 0.917 | 0.333 | 0.286 | 0.818 | 0.583 |
| Can 40p/80b | positive-NN top40 | 120 | 0.883 | 0.058 | 0.575 | 0.311 | 0.825 |
| Lift MG | classifier top160 | 480 | 0.558 | 0.005 | 0.000 | 0.108 | 0.553 |
| Lift MG | classifier top320 | 960 | 0.859 | 0.073 | 0.098 | 0.473 | 0.786 |
| Lift MG | TRIAGE-BC current | 441 | 0.508 | 0.006 | 0.061 | 0.116 | 0.503 |
| Lift MG | positive-NN top160 | 480 | 0.413 | 0.040 | 0.787 | 0.449 | 0.373 |

## Interpretation

- Across `4` settings and `8` deployable action-risk proxy formulas, proxy winners match the audit-support winner in `1/32` setting-proxy cases.
- Proxy winners strictly dominate the positive-NN baseline on hidden support metrics in `2/32` setting-proxy cases.
- The action-conflict and bad-neighbor features are useful diagnostics, but they still do not produce a reliable hidden-label-free selector over the current candidate family.
- Treat this as another no-go for endpoint training a new v0.2 branch from the existing support candidates. The next useful step is to create candidates that optimize these risks directly, or freeze an abstention/router story instead of proxy-selecting among stale candidates.

## Outputs

- `results/final_paper/tables/v02_action_risk_feature_screen_per_split.csv`
- `results/final_paper/tables/v02_action_risk_feature_screen.csv`
- `results/final_paper/tables/v02_action_risk_feature_screen_winners.csv`
- `results/final_paper/tables/v02_action_risk_feature_screen_REPORT.md`
