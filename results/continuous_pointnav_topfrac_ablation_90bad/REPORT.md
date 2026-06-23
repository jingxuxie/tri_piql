# Continuous PointNav Tri-Signal Smoke

Seeds: `[0, 1, 2, 3, 4]`.
Bad fractions: `[0.9]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fractions: `[0.05, 0.1, 0.15, 0.25, 0.35]`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.90 | bc_all | 5 | 0.260 +/- 0.057 | 0.740 +/- 0.057 | -0.668 +/- 0.099 | 18.8 +/- 1.6 |
| 0.90 | bc_pos_unlabeled | 5 | 0.213 +/- 0.124 | 0.740 +/- 0.065 | -0.731 +/- 0.180 | 20.5 +/- 3.0 |
| 0.90 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.608 +/- 0.007 | 39.2 +/- 0.7 |
| 0.90 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.021 | 39.7 +/- 2.1 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.953 +/- 0.093 | 0.047 +/- 0.093 | 0.508 +/- 0.170 | 39.9 +/- 1.9 |
| 0.90 | tri_signal_top_demo_bc_frac0p15 | 5 | 0.680 +/- 0.069 | 0.320 +/- 0.069 | 0.046 +/- 0.117 | 31.4 +/- 2.1 |
| 0.90 | tri_signal_top_demo_bc_frac0p25 | 5 | 0.467 +/- 0.070 | 0.533 +/- 0.070 | -0.316 +/- 0.116 | 24.9 +/- 2.4 |
| 0.90 | tri_signal_top_demo_bc_frac0p35 | 5 | 0.460 +/- 0.080 | 0.540 +/- 0.080 | -0.328 +/- 0.137 | 24.8 +/- 2.5 |
| 0.90 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Selection Diagnostics

| top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|
| 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.10 | 0.967 +/- 0.067 | 0.989 +/- 0.023 | 17.4 | 0.6 |
| 0.15 | 0.681 +/- 0.073 | 0.878 +/- 0.037 | 18.4 | 8.6 |
| 0.25 | 0.409 +/- 0.044 | 0.701 +/- 0.040 | 18.4 | 26.6 |
| 0.35 | 0.292 +/- 0.031 | 0.584 +/- 0.036 | 18.4 | 44.6 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
