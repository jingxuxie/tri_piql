# Continuous PointNav Tri-Signal Smoke

Status: `complete`.
Completed seed/fraction runs: `4`.
Seeds: `[3, 4]`.
Bad fractions: `[0.9, 0.95]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fractions: `[0.05, 0.1]`.
Posterior priors: `[0.05, 0.1]`; posterior temperature: `0.02`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.90 | bc_all | 2 | 0.133 +/- 0.033 | 0.867 +/- 0.033 | -0.887 +/- 0.056 | 15.4 +/- 1.1 |
| 0.90 | bc_pos_unlabeled | 2 | 0.133 +/- 0.033 | 0.867 +/- 0.033 | -0.889 +/- 0.051 | 15.6 +/- 1.6 |
| 0.90 | bc_positive_prefix | 2 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 2 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.618 +/- 0.004 | 38.2 +/- 0.4 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 2 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.584 +/- 0.008 | 41.5 +/- 0.8 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 2 | 0.883 +/- 0.117 | 0.117 +/- 0.117 | 0.370 +/- 0.228 | 39.6 +/- 0.5 |
| 0.90 | tri_signal_rerank | 2 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 2 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.011 | 39.7 +/- 1.1 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 2 | 0.867 +/- 0.133 | 0.133 +/- 0.133 | 0.374 +/- 0.230 | 35.9 +/- 3.7 |
| 0.90 | weighted_bc_state_action | 2 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | bc_all | 2 | 0.100 +/- 0.000 | 0.900 +/- 0.000 | -0.949 +/- 0.001 | 14.9 +/- 0.1 |
| 0.95 | bc_pos_unlabeled | 2 | 0.117 +/- 0.017 | 0.883 +/- 0.017 | -0.920 +/- 0.030 | 15.3 +/- 0.3 |
| 0.95 | bc_positive_prefix | 2 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 2 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.557 +/- 0.012 | 44.3 +/- 1.2 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 2 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.024 | 39.7 +/- 2.4 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 2 | 0.700 +/- 0.033 | 0.300 +/- 0.033 | 0.090 +/- 0.068 | 31.0 +/- 0.1 |
| 0.95 | tri_signal_rerank | 2 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 2 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.611 +/- 0.005 | 38.9 +/- 0.4 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 2 | 0.600 +/- 0.300 | 0.383 +/- 0.317 | -0.063 +/- 0.522 | 28.0 +/- 9.4 |
| 0.95 | weighted_bc_state_action | 2 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 0.917 +/- 0.083 | 0.972 +/- 0.028 | 16.5 | 1.5 |
| 0.95 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.95 | 0.10 | 0.667 +/- 0.056 | 0.868 +/- 0.028 | 12.0 | 6.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 0.917 +/- 0.083 | 0.972 +/- 0.028 |
| 0.95 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.95 | 0.10 | 0.100 | 0.667 +/- 0.056 | 0.869 +/- 0.027 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
