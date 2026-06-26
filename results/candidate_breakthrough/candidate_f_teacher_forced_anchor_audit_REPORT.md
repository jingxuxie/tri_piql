# Candidate F Teacher-Forced Anchor Audit

This audit uses only labeled-positive training demonstrations to compare
trained policy actions under teacher forcing. Endpoint first-20 counts
are included only to see whether a train-only anchor rule would have
selected the right baseline policy.

## Per-Split Metrics

| split | method | action L2 | first L2 | support margin | support pos dist | first20 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 101 | positive | 0.3934 | 0.2268 | 2.8926 | 0.9459 | 7/20 |
| 101 | weighted | 0.9286 | 0.8885 | 2.0182 | 1.9213 | 12/20 |
| 101 | triage | 0.3502 | 0.2591 | 2.9175 | 0.9049 | 11/20 |
| 202 | positive | 0.3534 | 0.2152 | 3.0045 | 0.9458 | 17/20 |
| 202 | weighted | 0.3105 | 0.2935 | 3.0627 | 0.8923 | 13/20 |
| 202 | triage | 0.3751 | 0.3045 | 3.0894 | 0.9394 | 12/20 |
| 303 | positive | 0.3486 | 0.1798 | 3.1482 | 0.8727 | 15/20 |
| 303 | weighted | 0.3614 | 0.3063 | 3.0184 | 0.9909 | 10/20 |
| 303 | triage | 0.3069 | 0.4631 | 2.9495 | 1.0521 | 13/20 |
| 404 | positive | 0.3486 | 0.1862 | 3.0988 | 0.8798 | 17/20 |
| 404 | weighted | 0.3526 | 0.1910 | 3.1102 | 0.8952 | 13/20 |
| 404 | triage | 0.4053 | 0.2358 | 3.1193 | 0.8706 | 14/20 |
| 505 | positive | 0.3484 | 0.1753 | 3.2461 | 0.8708 | 15/20 |
| 505 | weighted | 0.3639 | 0.2799 | 3.2831 | 0.8557 | 12/20 |
| 505 | triage | 0.3695 | 0.3073 | 3.1849 | 1.0448 | 14/20 |

## Rule Aggregate

| rule | selected first20 total | oracle baseline total | choices |
| --- | ---: | ---: | --- |
| min_action_l2 | 69/100 | 76/100 | 101:triage, 202:weighted, 303:triage, 404:positive, 505:positive |
| min_first_action_l2 | 71/100 | 76/100 | 101:positive, 202:positive, 303:positive, 404:positive, 505:positive |
| max_support_margin | 64/100 | 76/100 | 101:triage, 202:triage, 303:positive, 404:triage, 505:weighted |
| min_support_pos_dist | 65/100 | 76/100 | 101:triage, 202:weighted, 303:positive, 404:triage, 505:weighted |
| max_first_support_margin | 75/100 | 76/100 | 101:triage, 202:positive, 303:positive, 404:positive, 505:positive |

## Read

- If a rule selects positive-only on split 101, it cannot solve the main
  fixed-threshold failure because weighted BC is the best completed
  first-20 baseline on that split.
- A useful Candidate F anchor rule should approach the per-split baseline
  oracle without using endpoint outcomes.

## Artifacts

- Metrics CSV: `results/candidate_breakthrough/candidate_f_teacher_forced_anchor_metrics.csv`.
- Rule CSV: `results/candidate_breakthrough/candidate_f_teacher_forced_anchor_rules.csv`.
