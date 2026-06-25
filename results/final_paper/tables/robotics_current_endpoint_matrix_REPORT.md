# Current Robomimic Endpoint Matrix

This table consolidates the current endpoint evidence staged under `results/final_paper/`.
It intentionally separates primary frozen three-split rows from diagnostic single-split rows.

| task | evidence_status | method | success_rate | successes | episodes | train_or_support_count | support_purity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Can 80p/80b | diagnostic_single_split | positive-only NN | 0.980 | 49 | 50 | 80 | 0.900 |
| Can 80p/80b | diagnostic_single_split | TRIAGE-BC | 0.860 | 43 | 50 | 40 | 0.975 |
| Can 40p/80b | primary_frozen_3split | all-demo BC | 0.540 | 81 | 150 |  |  |
| Can 40p/80b | primary_frozen_3split | weighted BC | 0.600 | 90 | 150 | 360 | 0.333 |
| Can 40p/80b | primary_frozen_3split | positive-only NN | 0.720 | 108 | 150 | 120 | 0.883 |
| Can 40p/80b | primary_frozen_3split | TRIAGE-BC | 0.660 | 99 | 150 | 190 | 0.579 |
| Can 40p/80b | primary_frozen_3split_diagnostic_oracle | all-positive oracle | 0.980 | 147 | 150 | 270 | 1.000 |
| Can 20p/80b | diagnostic_single_split | weighted BC | 0.360 | 18 | 50 | 100 | 0.200 |
| Can 20p/80b | diagnostic_single_split | positive-only NN | 0.680 | 34 | 50 | 20 | 0.850 |
| Can 20p/80b | diagnostic_single_split | TRIAGE-BC | 0.660 | 33 | 50 | 50 | 0.400 |
| Lift MG | primary_frozen_3split | all-demo BC | 0.207 | 31 | 150 |  |  |
| Lift MG | primary_frozen_3split | weighted BC | 0.620 | 93 | 150 | 4260 | 0.194 |
| Lift MG | primary_frozen_3split | positive-only NN | 0.547 | 82 | 150 | 480 | 0.713 |
| Lift MG | primary_frozen_3split | TRIAGE-BC | 0.493 | 74 | 150 | 441 | 0.955 |
| Lift MG | primary_frozen_3split_diagnostic_oracle | all-positive oracle | 0.700 | 105 | 150 |  |  |

## Interpretation

- Can 40p/80b and Lift MG are the current primary frozen three-split endpoint tables.
- Can 20p/80b and Can 80p/80b are useful diagnostics but are not complete three-split endpoint tables.
- Positive-only NN is the strongest non-oracle Can row in all staged Can endpoint checks so far.
- Lift MG is the strongest counterexample to a hard-support-only story: weighted BC is the best non-oracle row on the frozen endpoint aggregate.

## Figure

- PNG: `results/final_paper/figures/robotics_current_endpoint_matrix.png`
- PDF: `results/final_paper/figures/robotics_current_endpoint_matrix.pdf`
