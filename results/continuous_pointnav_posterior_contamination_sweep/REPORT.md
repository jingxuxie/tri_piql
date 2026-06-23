# Continuous PointNav Tri-Signal Smoke

Status: `interrupted_partial`.
Completed seed/fraction runs: `10`.
Seeds: `[0, 1, 2]`.
Bad fractions: `[0.5, 0.75, 0.9, 0.95]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fractions: `[0.05, 0.1]`.
Posterior priors: `[0.05, 0.1]`; posterior temperature: `0.02`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.50 | bc_all | 3 | 0.444 +/- 0.129 | 0.556 +/- 0.129 | -0.356 +/- 0.210 | 24.4 +/- 4.7 |
| 0.50 | bc_pos_unlabeled | 3 | 0.367 +/- 0.027 | 0.633 +/- 0.027 | -0.484 +/- 0.048 | 21.7 +/- 0.7 |
| 0.50 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | oracle_good_bc | 3 | 0.933 +/- 0.094 | 0.033 +/- 0.047 | 0.505 +/- 0.147 | 39.5 +/- 1.2 |
| 0.50 | tri_signal_posterior_bc_prior0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.611 +/- 0.003 | 38.9 +/- 0.3 |
| 0.50 | tri_signal_posterior_bc_prior0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.013 | 39.7 +/- 1.3 |
| 0.50 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | tri_signal_top_demo_bc_frac0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.006 | 39.8 +/- 0.6 |
| 0.50 | tri_signal_top_demo_bc_frac0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.016 | 40.1 +/- 1.6 |
| 0.50 | weighted_bc_state_action | 3 | 0.311 +/- 0.440 | 0.022 +/- 0.031 | -0.330 +/- 0.524 | 61.9 +/- 11.5 |
| 0.75 | bc_all | 3 | 0.400 +/- 0.047 | 0.600 +/- 0.047 | -0.431 +/- 0.085 | 23.1 +/- 1.0 |
| 0.75 | bc_pos_unlabeled | 3 | 0.356 +/- 0.096 | 0.644 +/- 0.096 | -0.509 +/- 0.168 | 22.0 +/- 2.3 |
| 0.75 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.592 +/- 0.008 | 40.8 +/- 0.8 |
| 0.75 | tri_signal_posterior_bc_prior0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.006 | 39.8 +/- 0.6 |
| 0.75 | tri_signal_posterior_bc_prior0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.589 +/- 0.010 | 41.1 +/- 1.0 |
| 0.75 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc_frac0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.011 | 40.0 +/- 1.1 |
| 0.75 | tri_signal_top_demo_bc_frac0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.020 | 40.4 +/- 2.0 |
| 0.75 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.333 +/- 0.471 | -0.940 +/- 0.340 | 60.7 +/- 13.2 |
| 0.90 | bc_all | 3 | 0.278 +/- 0.068 | 0.722 +/- 0.068 | -0.636 +/- 0.117 | 19.1 +/- 2.0 |
| 0.90 | bc_pos_unlabeled | 3 | 0.244 +/- 0.068 | 0.756 +/- 0.068 | -0.697 +/- 0.117 | 18.6 +/- 2.0 |
| 0.90 | bc_positive_prefix | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.607 +/- 0.009 | 39.3 +/- 0.9 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 3 | 0.667 +/- 0.471 | 0.000 +/- 0.000 | 0.179 +/- 0.622 | 48.7 +/- 15.1 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.587 +/- 0.025 | 41.3 +/- 2.5 |
| 0.90 | tri_signal_rerank | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.611 +/- 0.012 | 38.9 +/- 1.2 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 3 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.591 +/- 0.011 | 40.9 +/- 1.1 |
| 0.90 | weighted_bc_state_action | 3 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | bc_all | 1 | 0.300 +/- 0.000 | 0.700 +/- 0.000 | -0.600 +/- 0.000 | 20.0 +/- 0.0 |
| 0.95 | bc_pos_unlabeled | 1 | 0.133 +/- 0.000 | 0.867 +/- 0.000 | -0.884 +/- 0.000 | 15.0 +/- 0.0 |
| 0.95 | bc_positive_prefix | 1 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 1 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.571 +/- 0.000 | 42.9 +/- 0.0 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 1 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.592 +/- 0.000 | 40.8 +/- 0.0 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 1 | 0.667 +/- 0.000 | 0.333 +/- 0.000 | 0.042 +/- 0.000 | 29.1 +/- 0.0 |
| 0.95 | tri_signal_rerank | 1 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 1 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.615 +/- 0.000 | 38.5 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 1 | 0.767 +/- 0.000 | 0.233 +/- 0.000 | 0.201 +/- 0.000 | 33.2 +/- 0.0 |
| 0.95 | weighted_bc_state_action | 1 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.50 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.75 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.75 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.95 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.95 | 0.10 | 0.611 +/- 0.000 | 0.842 +/- 0.000 | 11.0 | 7.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.50 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.95 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.95 | 0.10 | 0.100 | 0.611 +/- 0.000 | 0.842 +/- 0.000 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
