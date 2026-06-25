# Bad-Label Control Summary

This report consolidates the paper-facing bad-label evidence from staged final-paper artifacts.
It is a claim guardrail: explicit bad labels can help score calibration and support purity, but the current bad-aware converter is not uniformly better than strong no-bad-label retrieval.

## Endpoint Comparisons

| setting | bad_aware_method | comparison_baseline | bad_aware_endpoint | baseline_endpoint | endpoint_delta_bad_aware_minus_baseline |
| --- | --- | --- | --- | --- | --- |
| Controlled PointNav n+=5, n- in {1,2,5} | score-gap support with explicit bad labels | mixed-log / local weighted BC | min 0.973, mean 0.997 | BC-all mean 0.292; local weighted mean 0.131 |  |
| Can 40p/80b primary frozen 3-split | TRIAGE-BC adaptive masscap | positive-only NN top40 | 99/150 | 108/150 | -0.060 |
| Can 20p/80b diagnostic support audit + two endpoints | TRIAGE-BC adaptive masscap | positive-only NN top20 | 46/100 | 54/100 | -0.080 |
| Can 80p/80b balanced diagnostic | TRIAGE-BC adaptive masscap | positive-only NN top80 | 43/50 | 49/50 | -0.120 |
| Lift MG primary frozen 3-split | TRIAGE-BC pos-min | positive-only NN top160 | 74/150 | 82/150 | -0.053 |

## Support And Interpretation

| setting | bad_aware_support | baseline_support | interpretation |
| --- | --- | --- | --- |
| Controlled PointNav n+=5, n- in {1,2,5} | min purity 1.000; max hidden-bad demos 0.0 |  | In the controlled mechanism, even one labeled bad shortcut is enough for pure hidden-good support; this supports label-efficient calibration, not Can bad-label necessity. |
| Can 40p/80b primary frozen 3-split | 110 pos, 80 bad / 190 selected (purity 0.579) | 106 pos, 14 bad / 120 selected (purity 0.883) | Bad-aware scoring recovers slightly more hidden-positive demos, but the converter admits much more hidden-bad support; positive-only retrieval is the stronger endpoint baseline. |
| Can 20p/80b diagnostic support audit + two endpoints | 54 pos, 69 bad / 123 selected (purity 0.439) | 49 pos, 11 bad / 60 selected (purity 0.817) | TRIAGE-BC recovers more hidden positives under heavier contamination, but positive-only retrieval admits far fewer bad demos and wins the completed endpoints. |
| Can 80p/80b balanced diagnostic | 137 pos, 28 bad / 165 selected (purity 0.830) | 220 pos, 20 bad / 240 selected (purity 0.917) | The balanced diagnostic also favors positive-only retrieval; even the split where TRIAGE-BC has purer support has lower endpoint success. |
| Lift MG primary frozen 3-split | 421 pos, 20 bad / 441 selected (purity 0.955) | 342 pos, 138 bad / 480 selected (purity 0.713) | Bad-aware pos-min support is much purer and recovers more hidden positives, but the fixed endpoint still trails the broader positive-only baseline. |

## Paper Wording

- Use this table to support: bad labels improve calibration and sometimes recover hidden support.
- Do not use this table to claim: bad labels are necessary, TRIAGE-BC uniformly beats positive-only retrieval, or hard support always wins.
- The strongest current wording is that explicit failures are calibration signal whose value depends on score-to-support conversion and task coverage.
