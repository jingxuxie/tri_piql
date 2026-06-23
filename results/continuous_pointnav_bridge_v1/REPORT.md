# Continuous PointNav Tri-Signal Smoke

Seeds: `[0, 1, 2]`.
Bad fractions: `[0.75, 0.9]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fraction: `0.25`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.75 | bc_all | 3 | 0.400 +/- 0.047 | 0.600 +/- 0.047 | -0.431 +/- 0.085 | 23.1 +/- 1.0 |
| 0.75 | bc_pos_unlabeled | 3 | 0.356 +/- 0.096 | 0.644 +/- 0.096 | -0.509 +/- 0.168 | 22.0 +/- 2.3 |
| 0.75 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.011 | 39.6 +/- 1.1 |
| 0.75 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc | 3 | 0.956 +/- 0.063 | 0.044 +/- 0.063 | 0.515 +/- 0.119 | 39.6 +/- 1.2 |
| 0.75 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.333 +/- 0.471 | -0.940 +/- 0.340 | 60.7 +/- 13.2 |
| 0.90 | bc_all | 3 | 0.278 +/- 0.068 | 0.722 +/- 0.068 | -0.636 +/- 0.117 | 19.1 +/- 2.0 |
| 0.90 | bc_pos_unlabeled | 3 | 0.244 +/- 0.068 | 0.756 +/- 0.068 | -0.697 +/- 0.117 | 18.6 +/- 2.0 |
| 0.90 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.619 +/- 0.008 | 38.1 +/- 0.8 |
| 0.90 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc | 3 | 0.522 +/- 0.166 | 0.478 +/- 0.166 | -0.224 +/- 0.283 | 26.9 +/- 5.0 |
| 0.90 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
