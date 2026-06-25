# Controlled PointNav Mechanism Summary

This report consolidates the current controlled PointNav evidence staged under `results/final_paper/ablations/`.
The strongest paper-facing rows use route-prefix positives, explicit bad shortcut trajectories, and unlabeled logs with hidden safe routes plus hidden trap trajectories.

## Equal Label Budget Stress: n+=n-=2

| bad_frac | method | success | selected_demo_purity | hidden_good_demos | hidden_bad_demos |
| --- | --- | --- | --- | --- | --- |
| 0.50 | BC-all | 0.460 |  |  |  |
| 0.50 | pos+unlabeled BC | 0.440 |  |  |  |
| 0.50 | local weighted BC | 0.147 |  |  |  |
| 0.50 | TRIAGE-BC gap support | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.50 | hidden-good oracle | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.75 | BC-all | 0.360 |  |  |  |
| 0.75 | pos+unlabeled BC | 0.320 |  |  |  |
| 0.75 | local weighted BC | 0.000 |  |  |  |
| 0.75 | TRIAGE-BC gap support | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.75 | hidden-good oracle | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.90 | BC-all | 0.180 |  |  |  |
| 0.90 | pos+unlabeled BC | 0.133 |  |  |  |
| 0.90 | local weighted BC | 0.173 |  |  |  |
| 0.90 | TRIAGE-BC gap support | 1.000 | 1.000 | 14.2 | 0.0 |
| 0.90 | hidden-good oracle | 1.000 | 1.000 | 14.2 | 0.0 |
| 0.95 | BC-all | 0.140 |  |  |  |
| 0.95 | pos+unlabeled BC | 0.120 |  |  |  |
| 0.95 | local weighted BC | 0.000 |  |  |  |
| 0.95 | TRIAGE-BC gap support | 1.000 | 1.000 | 9.2 | 0.0 |
| 0.95 | hidden-good oracle | 1.000 | 1.000 | 9.2 | 0.0 |

## Bad-Label Count: n+=5

| n_neg | bad_frac | method | success | selected_demo_purity | hidden_good_demos | hidden_bad_demos |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.50 | TRIAGE-BC gap support | 1.000 | 1.000 | 5.6 | 0.0 |
| 1 | 0.75 | TRIAGE-BC gap support | 1.000 | 1.000 | 8.8 | 0.0 |
| 1 | 0.90 | TRIAGE-BC gap support | 1.000 | 1.000 | 14.4 | 0.0 |
| 1 | 0.95 | TRIAGE-BC gap support | 1.000 | 1.000 | 10.2 | 0.0 |
| 2 | 0.50 | TRIAGE-BC gap support | 1.000 | 1.000 | 7.0 | 0.0 |
| 2 | 0.75 | TRIAGE-BC gap support | 1.000 | 1.000 | 6.6 | 0.0 |
| 2 | 0.90 | TRIAGE-BC gap support | 0.973 | 1.000 | 16.0 | 0.0 |
| 2 | 0.95 | TRIAGE-BC gap support | 0.993 | 1.000 | 10.2 | 0.0 |
| 5 | 0.50 | TRIAGE-BC gap support | 1.000 | 1.000 | 6.2 | 0.0 |
| 5 | 0.75 | TRIAGE-BC gap support | 1.000 | 1.000 | 11.2 | 0.0 |
| 5 | 0.90 | TRIAGE-BC gap support | 1.000 | 1.000 | 16.0 | 0.0 |
| 5 | 0.95 | TRIAGE-BC gap support | 1.000 | 1.000 | 10.2 | 0.0 |

## Interpretation

- With only two positive prefixes and two bad shortcut demos, TRIAGE gap support reaches `1.000` success at every tested contamination level, matching the hidden-good oracle.
- BC-all, positive+unlabeled BC, and local weighted BC degrade sharply as the unlabeled bad fraction rises.
- With five positives, even one explicit bad shortcut demo is enough for gap support to select pure hidden-good support and reach `1.000` success at all tested bad fractions.
- This is the cleanest controlled mechanism evidence for the paper: explicit bad labels calibrate support recovery when positives are scarce and incomplete.

## Figure

- PNG: `results/final_paper/figures/pointnav_controlled_mechanism.png`
- PDF: `results/final_paper/figures/pointnav_controlled_mechanism.pdf`
