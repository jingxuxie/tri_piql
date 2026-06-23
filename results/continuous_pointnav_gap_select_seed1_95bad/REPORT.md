# Continuous PointNav Tri-Signal Smoke

Status: `complete`.
Completed seed/fraction runs: `1`.
Seeds: `[1]`.
Bad fractions: `[0.95]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fractions: `[0.05, 0.1]`.
Gap selection max fractions: `[0.1]`; min fraction: `0.02`.
Posterior priors: `[0.05, 0.1]`; posterior temperature: `0.02`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.95 | bc_all | 1 | 0.200 +/- 0.000 | 0.800 +/- 0.000 | -0.791 +/- 0.000 | 19.1 +/- 0.0 |
| 0.95 | bc_pos_unlabeled | 1 | 0.067 +/- 0.000 | 0.833 +/- 0.000 | -0.967 +/- 0.000 | 20.0 +/- 0.0 |
| 0.95 | bc_positive_prefix | 1 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 1 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.000 | 39.7 +/- 0.0 |
| 0.95 | tri_signal_gap_demo_bc_max0p1 | 1 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.598 +/- 0.000 | 40.2 +/- 0.0 |
| 0.95 | tri_signal_gap_posterior_bc_max0p1 | 1 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.635 +/- 0.000 | 36.5 +/- 0.0 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 1 | 0.000 +/- 0.000 | 0.433 +/- 0.000 | -0.878 +/- 0.000 | 44.5 +/- 0.0 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 1 | 0.033 +/- 0.000 | 0.533 +/- 0.000 | -0.883 +/- 0.000 | 38.3 +/- 0.0 |
| 0.95 | tri_signal_rerank | 1 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 1 | 0.433 +/- 0.000 | 0.567 +/- 0.000 | -0.363 +/- 0.000 | 23.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 1 | 0.433 +/- 0.000 | 0.567 +/- 0.000 | -0.366 +/- 0.000 | 23.3 +/- 0.0 |
| 0.95 | weighted_bc_state_action | 1 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.95 | 0.05 | 0.556 +/- 0.000 | 0.818 +/- 0.000 | 5.0 | 4.0 |
| 0.95 | 0.10 | 0.278 +/- 0.000 | 0.572 +/- 0.000 | 5.0 | 13.0 |

## Gap Selection Diagnostics

| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.95 | 0.10 | 0.028 +/- 0.000 | 0.369 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 5.0 | 0.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.95 | 0.05 | 0.050 | 0.556 +/- 0.000 | 0.816 +/- 0.000 |
| 0.95 | 0.10 | 0.100 | 0.278 +/- 0.000 | 0.570 +/- 0.000 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
