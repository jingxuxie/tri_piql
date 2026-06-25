# v0.2 Proxy Feature Screen

This is a support-side screen over the existing hybrid candidate audit.
It uses hidden labels only for audit columns; candidate selection scores use selected support size and classifier-score means.

## Baseline Positive-NN Rows

| setting_label | candidate_label | selected_unlabeled | hidden_positive_recall | hidden_bad_admission | audit_oracle_score | classifier_score_mean |
| --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive-NN top20 | 60 | 0.500 | 0.000 | 0.500 | 0.750 |
| Can 40p/80b | positive-NN top40 | 120 | 0.883 | 0.058 | 0.825 | 0.684 |
| Can 40p/80b | positive-NN top80 | 240 | 0.992 | 0.504 | 0.488 | 0.538 |
| Lift MG | positive-NN top160 | 480 | 0.413 | 0.040 | 0.373 | 0.762 |
| Lift MG | positive-NN top80 | 240 | 0.269 | 0.005 | 0.264 | 0.933 |
| Can 20p/80b | positive-NN top20 | 60 | 0.817 | 0.046 | 0.771 | 0.679 |
| Can 20p/80b | positive-NN top40 | 120 | 0.983 | 0.254 | 0.729 | 0.543 |
| Can 80p/80b | positive-NN top160 | 480 | 1.000 | 1.000 | 0.000 | 0.546 |
| Can 80p/80b | positive-NN top40 | 120 | 0.500 | 0.000 | 0.500 | 0.758 |
| Can 80p/80b | positive-NN top80 | 240 | 0.917 | 0.083 | 0.833 | 0.696 |

## Proxy Winners

| setting_label | proxy_label | winner_label | winner_selected | winner_recall | winner_bad_admission | winner_audit_score | matches_audit_winner | dominates_positive_nn_baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | audit oracle | positive-NN top40 | 120 | 0.883 | 0.058 | 0.825 | true | false |
| Can 40p/80b | coverage only | classifier top80 | 240 | 0.967 | 0.517 | 0.450 | false | false |
| Can 40p/80b | classifier score only | hybrid filter pos p10 pos40 | 25 | 0.208 | 0.000 | 0.208 | false | false |
| Can 40p/80b | coverage x classifier | classifier top60 | 180 | 0.900 | 0.300 | 0.600 | false | false |
| Can 40p/80b | coverage/classifier harmonic | classifier top60 | 180 | 0.900 | 0.300 | 0.600 | false | false |
| Lift MG | audit oracle | classifier top320 | 960 | 0.859 | 0.073 | 0.786 | true | false |
| Lift MG | coverage only | classifier top480 | 1440 | 0.923 | 0.197 | 0.726 | false | false |
| Lift MG | classifier score only | classifier top80 | 240 | 0.286 | 0.001 | 0.285 | false | false |
| Lift MG | coverage x classifier | classifier top320 | 960 | 0.859 | 0.073 | 0.786 | true | false |
| Lift MG | coverage/classifier harmonic | classifier top480 | 1440 | 0.923 | 0.197 | 0.726 | false | false |
| Can 20p/80b | audit oracle | hybrid filter mid mean fill classifier to20 | 60 | 0.833 | 0.042 | 0.792 | true | true |
| Can 20p/80b | coverage only | hybrid union pos20 triage | 136 | 0.950 | 0.329 | 0.621 | false | false |
| Can 20p/80b | classifier score only | hybrid filter pos p10 pos20 | 15 | 0.250 | 0.000 | 0.250 | false | false |
| Can 20p/80b | coverage x classifier | TRIAGE-BC current | 123 | 0.900 | 0.287 | 0.613 | false | false |
| Can 20p/80b | coverage/classifier harmonic | TRIAGE-BC current | 123 | 0.900 | 0.287 | 0.613 | false | false |
| Can 80p/80b | audit oracle | hybrid intersection pos80 classifier160 | 240 | 0.917 | 0.083 | 0.833 | true | false |
| Can 80p/80b | coverage only | classifier top160 | 480 | 1.000 | 1.000 | 0.000 | false | false |
| Can 80p/80b | classifier score only | hybrid filter pos p10 pos80 | 58 | 0.242 | 0.000 | 0.242 | false | false |
| Can 80p/80b | coverage x classifier | classifier top80 | 240 | 0.792 | 0.208 | 0.583 | false | false |
| Can 80p/80b | coverage/classifier harmonic | classifier top80 | 240 | 0.792 | 0.208 | 0.583 | false | false |

## Interpretation

- Across `4` settings and `7` deployable proxy formulas, proxy winners match the audit-support winner in `1/28` setting-proxy cases.
- Proxy winners strictly dominate the positive-NN baseline on hidden support metrics in `2/28` setting-proxy cases.
- Coverage-only proxies over-select broad supports; classifier-only proxies under-cover. Simple coverage/classifier combinations do not reliably recover the audit frontier.
- The best support-audit rows are setting-specific: positive-NN top40 on Can 40p/80b, a small fill hybrid on Can 20p/80b, an intersection hybrid on Can 80p/80b, and classifier top320 on Lift MG.
- This does not justify endpoint training a new branch yet. The next v0.2 feature should explicitly estimate action-conflict or bad-neighbor risk, not just mean classifier score.

## Outputs

- `results/final_paper/tables/v02_proxy_feature_screen.csv`
- `results/final_paper/tables/v02_proxy_feature_screen_winners.csv`
- `results/final_paper/tables/v02_proxy_feature_screen_REPORT.md`
