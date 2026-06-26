# Generated Regime-Probe Summary

This is the concise generated-regime probe summary requested by the top-tier plan.
It combines the endpoint-backed hard-negative, coverage-shift, and prefix-positive Can probes into one paper-facing artifact.

## Summary

| Probe | Bad-aware endpoint | Positive-only endpoint | Delta | Bad-aware support pos/bad | Positive-only support pos/bad |
| --- | --- | --- | --- | --- | --- |
| Hard-negative Can | 104/150 | 91/150 | +13/150 | 113/7 | 70/50 |
| Coverage-shift Can | 120/150 | 103/150 | +17/150 | 118/2 | 105/15 |
| Prefix-positive Can | 119/150 | 6/150 | +113/150 | 195/45 | 37/203 |

## Interpretation

- All rows are generated split constructions, not default Robomimic benchmark rows.
- They isolate settings where explicit bad labels help beyond matched positive-only retrieval.
- Hidden labels are used to construct and audit the splits; the support rules themselves use only trusted positive labels, trusted bad labels, and unlabeled observations/actions.
- The default benchmark rows remain the primary Can/Lift endpoint matrix and the fresh v0.2 Can+Lift gate.

## Source Artifacts

- `Hard-negative Can`: `results/final_paper/ablations/hard_negative_can_endpoint_200ep/endpoint_200ep_3split_summary.csv`
- `Coverage-shift Can`: `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/endpoint_200ep_3split_summary.csv`
- `Prefix-positive Can`: `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/endpoint_200ep_aggregate_summary.csv`

## Outputs

- `results/final_paper/tables/generated_regime_probe_summary.csv`
- `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`
