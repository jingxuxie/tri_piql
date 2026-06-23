# Continuous PointNav Tri-Signal Smoke

Status: `complete`.
Completed seed/fraction runs: `6`.
Seeds: `[0, 1, 2]`.
Bad fractions: `[0.9, 0.95]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fractions: `[0.05, 0.1]`.
Posterior priors: `[0.05, 0.1]`; posterior temperature: `0.02`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.90 | bc_all | 3 | 0.300 +/- 0.125 | 0.700 +/- 0.125 | -0.602 +/- 0.214 | 20.2 +/- 3.6 |
| 0.90 | bc_pos_unlabeled | 3 | 0.322 +/- 0.057 | 0.678 +/- 0.057 | -0.558 +/- 0.101 | 20.2 +/- 1.2 |
| 0.90 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.611 +/- 0.007 | 38.9 +/- 0.7 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.615 +/- 0.008 | 38.5 +/- 0.8 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.587 +/- 0.018 | 41.3 +/- 1.8 |
| 0.90 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.007 | 40.4 +/- 0.7 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.013 | 40.6 +/- 1.3 |
| 0.90 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.333 +/- 0.471 | -0.921 +/- 0.313 | 58.8 +/- 15.9 |
| 0.95 | bc_all | 3 | 0.189 +/- 0.042 | 0.811 +/- 0.042 | -0.795 +/- 0.068 | 17.3 +/- 1.8 |
| 0.95 | bc_pos_unlabeled | 3 | 0.022 +/- 0.031 | 0.833 +/- 0.027 | -1.020 +/- 0.039 | 20.9 +/- 1.8 |
| 0.95 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.019 | 40.6 +/- 1.9 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 3 | 0.667 +/- 0.471 | 0.144 +/- 0.204 | 0.116 +/- 0.703 | 40.7 +/- 2.9 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 3 | 0.411 +/- 0.273 | 0.444 +/- 0.083 | -0.341 +/- 0.396 | 30.8 +/- 5.4 |
| 0.95 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 3 | 0.811 +/- 0.267 | 0.189 +/- 0.267 | 0.283 +/- 0.457 | 34.0 +/- 7.8 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 3 | 0.722 +/- 0.204 | 0.278 +/- 0.204 | 0.130 +/- 0.351 | 31.4 +/- 5.8 |
| 0.95 | weighted_bc_state_action | 3 | 0.333 +/- 0.471 | 0.000 +/- 0.000 | -0.282 +/- 0.592 | 61.5 +/- 12.0 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.95 | 0.05 | 0.852 +/- 0.210 | 0.939 +/- 0.086 | 7.7 | 1.3 |
| 0.95 | 0.10 | 0.481 +/- 0.146 | 0.743 +/- 0.121 | 8.7 | 9.3 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.95 | 0.05 | 0.050 | 0.852 +/- 0.210 | 0.939 +/- 0.087 |
| 0.95 | 0.10 | 0.100 | 0.481 +/- 0.146 | 0.742 +/- 0.122 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
