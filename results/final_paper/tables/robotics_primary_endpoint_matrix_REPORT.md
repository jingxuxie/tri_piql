# Primary Robomimic Endpoint Matrix

This table contains only the current primary frozen three-split endpoint evidence.
Diagnostic Can 20p/80b and Can 80p/80b rows remain in `robotics_current_endpoint_matrix.csv` and the corresponding report.

| task | evidence_status | method | success_rate | successes | episodes | train_or_support_count | support_purity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | primary_frozen_3split | all-demo BC | 0.540 | 81 | 150 |  |  |
| Can 40p/80b | primary_frozen_3split | weighted BC | 0.600 | 90 | 150 | 360 | 0.333 |
| Can 40p/80b | primary_frozen_3split | positive-only NN | 0.720 | 108 | 150 | 120 | 0.883 |
| Can 40p/80b | primary_frozen_3split | TRIAGE-BC | 0.660 | 99 | 150 | 190 | 0.579 |
| Can 40p/80b | primary_frozen_3split_diagnostic_oracle | all-positive oracle | 0.980 | 147 | 150 | 270 | 1.000 |
| Lift MG | primary_frozen_3split | all-demo BC | 0.207 | 31 | 150 |  |  |
| Lift MG | primary_frozen_3split | weighted BC | 0.620 | 93 | 150 | 4260 | 0.194 |
| Lift MG | primary_frozen_3split | positive-only NN | 0.547 | 82 | 150 | 480 | 0.713 |
| Lift MG | primary_frozen_3split | TRIAGE-BC | 0.493 | 74 | 150 | 441 | 0.955 |
| Lift MG | primary_frozen_3split_diagnostic_oracle | all-positive oracle | 0.700 | 105 | 150 |  |  |

## Interpretation

- Can 40p/80b supports the claim that TRIAGE-BC can beat weighted BC and all-demo cloning under action-conflicting contamination.
- Can 40p/80b does not support a bad-label necessity claim because positive-only NN is the strongest non-oracle row.
- Lift MG supports the coverage caveat: weighted BC is the best non-oracle row despite lower support purity.
- The all-positive oracle rows are diagnostic upper bounds that use hidden labels and are not deployable methods.

## Figure

- PNG: `results/final_paper/figures/robotics_primary_endpoint_matrix.png`
- PDF: `results/final_paper/figures/robotics_primary_endpoint_matrix.pdf`
