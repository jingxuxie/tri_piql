# Continuous PointNav Tri-Signal Smoke

Seeds: `[0, 1, 2]`.
Bad fractions: `[0.75, 0.9]`.
Positive prefix steps: `16`.
BC steps: `8000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.75 | bc_all | 3 | 0.411 +/- 0.083 | 0.589 +/- 0.083 | -0.406 +/- 0.141 | 22.9 +/- 2.5 |
| 0.75 | bc_pos_unlabeled | 3 | 0.411 +/- 0.123 | 0.589 +/- 0.123 | -0.413 +/- 0.215 | 23.5 +/- 3.1 |
| 0.75 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.598 +/- 0.008 | 40.2 +/- 0.8 |
| 0.75 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.333 +/- 0.471 | -0.959 +/- 0.366 | 62.5 +/- 10.5 |
| 0.90 | bc_all | 3 | 0.300 +/- 0.027 | 0.700 +/- 0.027 | -0.600 +/- 0.047 | 20.0 +/- 0.7 |
| 0.90 | bc_pos_unlabeled | 3 | 0.344 +/- 0.068 | 0.656 +/- 0.068 | -0.522 +/- 0.119 | 21.1 +/- 1.8 |
| 0.90 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.592 +/- 0.024 | 40.8 +/- 2.4 |
| 0.90 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
