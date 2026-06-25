# Primary Endpoint Paired Initial-State Delta Figure

This report stages the final-evaluation uncertainty figure requested by the paper plan.
Each plotted point is a per-initial-state paired endpoint-success delta after averaging repeated rollouts from the same validation-positive start.
Black intervals are the existing bootstrap intervals that resample split seeds and paired initial states.

| task | comparison | point_delta | bootstrap95_low | bootstrap95_high | split_signs | paired_initial_rows |
| --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | TRIAGE-BC - weighted BC | 0.060 | -0.113 | 0.240 | +++ | 30 |
| Can 40p/80b | TRIAGE-BC - all-demo BC | 0.120 | -0.133 | 0.380 | +-+ | 30 |
| Can 40p/80b | TRIAGE-BC - positive-only NN | -0.060 | -0.313 | 0.200 | --+ | 30 |
| Lift MG | weighted BC - TRIAGE-BC | 0.122 | -0.100 | 0.317 | -++ | 90 |
| Lift MG | weighted BC - positive-only NN | 0.050 | -0.111 | 0.222 | --+ | 90 |
| Lift MG | TRIAGE-BC - all-demo BC | 0.306 | 0.211 | 0.400 | +++ | 90 |

## Artifacts

- CSV: `results/final_paper/tables/primary_endpoint_paired_initial_deltas.csv`
- PNG: `results/final_paper/figures/primary_endpoint_paired_deltas.png`
- PDF: `results/final_paper/figures/primary_endpoint_paired_deltas.pdf`

## Interpretation Guardrail

The figure is a descriptive uncertainty visualization, not a formal independent significance test.
It makes the repeated-start structure visible and reinforces the paper wording that primary endpoint gaps are directional and split-sensitive.
