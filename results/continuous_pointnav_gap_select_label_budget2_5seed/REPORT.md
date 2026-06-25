# Continuous PointNav Tri-Signal Smoke

Status: `complete`.
Completed seed/fraction runs: `20`.
Seeds: `[0, 1, 2, 3, 4]`.
Bad fractions: `[0.5, 0.75, 0.9, 0.95]`.
Positive prefix steps: `16`.
BC steps: `6000`; classifier steps: `2500`.
Evaluation episodes per row: `30`.
Top unlabeled demo fractions: `[0.05, 0.1]`.
Gap selection max fractions: `[0.1]`; min fraction: `0.02`.
Posterior priors: `[0.05, 0.1]`; posterior temperature: `0.02`.

## Metrics

| bad_frac | method | runs | success | trap | return | length |
|---:|---|---:|---:|---:|---:|---:|
| 0.50 | bc_all | 5 | 0.460 +/- 0.118 | 0.540 +/- 0.118 | -0.329 +/- 0.203 | 24.9 +/- 3.4 |
| 0.50 | bc_pos_unlabeled | 5 | 0.440 +/- 0.025 | 0.560 +/- 0.025 | -0.366 +/- 0.041 | 24.6 +/- 1.0 |
| 0.50 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.200 +/- 0.400 | -0.813 +/- 0.226 | 61.3 +/- 17.4 |
| 0.50 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.607 +/- 0.009 | 39.3 +/- 0.9 |
| 0.50 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.598 +/- 0.005 | 40.2 +/- 0.5 |
| 0.50 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.011 | 40.0 +/- 1.1 |
| 0.50 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.007 | 39.4 +/- 0.7 |
| 0.50 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.009 | 40.1 +/- 0.9 |
| 0.50 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.011 | 39.4 +/- 1.1 |
| 0.50 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.607 +/- 0.009 | 39.3 +/- 0.9 |
| 0.50 | weighted_bc_state_action | 5 | 0.147 +/- 0.293 | 0.200 +/- 0.400 | -0.657 +/- 0.543 | 60.4 +/- 11.8 |
| 0.75 | bc_all | 5 | 0.360 +/- 0.110 | 0.640 +/- 0.110 | -0.495 +/- 0.193 | 21.5 +/- 2.7 |
| 0.75 | bc_pos_unlabeled | 5 | 0.320 +/- 0.069 | 0.680 +/- 0.069 | -0.570 +/- 0.111 | 21.0 +/- 2.6 |
| 0.75 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.007 +/- 0.013 | -0.703 +/- 0.005 | 69.6 +/- 0.8 |
| 0.75 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.010 | 40.1 +/- 1.0 |
| 0.75 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.003 | 40.6 +/- 0.3 |
| 0.75 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.015 | 39.9 +/- 1.5 |
| 0.75 | tri_signal_posterior_bc_prior0p05 | 5 | 0.800 +/- 0.400 | 0.000 +/- 0.000 | 0.337 +/- 0.519 | 46.3 +/- 11.9 |
| 0.75 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.015 | 40.4 +/- 1.5 |
| 0.75 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.005 | 39.8 +/- 0.5 |
| 0.75 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.584 +/- 0.020 | 41.6 +/- 2.0 |
| 0.75 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | bc_all | 5 | 0.180 +/- 0.093 | 0.813 +/- 0.086 | -0.809 +/- 0.156 | 17.6 +/- 2.4 |
| 0.90 | bc_pos_unlabeled | 5 | 0.133 +/- 0.076 | 0.867 +/- 0.076 | -0.883 +/- 0.133 | 15.0 +/- 2.0 |
| 0.90 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.200 +/- 0.400 | -0.811 +/- 0.223 | 61.1 +/- 17.7 |
| 0.90 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.592 +/- 0.024 | 40.8 +/- 2.4 |
| 0.90 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.010 | 39.4 +/- 1.0 |
| 0.90 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.595 +/- 0.008 | 40.5 +/- 0.8 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.595 +/- 0.021 | 40.5 +/- 2.1 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 5 | 0.927 +/- 0.085 | 0.073 +/- 0.085 | 0.483 +/- 0.143 | 37.1 +/- 3.0 |
| 0.90 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.011 | 40.6 +/- 1.1 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.787 +/- 0.278 | 0.107 +/- 0.108 | 0.288 +/- 0.399 | 39.2 +/- 5.9 |
| 0.90 | weighted_bc_state_action | 5 | 0.173 +/- 0.271 | 0.020 +/- 0.027 | -0.481 +/- 0.353 | 63.4 +/- 8.0 |
| 0.95 | bc_all | 5 | 0.140 +/- 0.080 | 0.860 +/- 0.080 | -0.876 +/- 0.138 | 15.6 +/- 2.3 |
| 0.95 | bc_pos_unlabeled | 5 | 0.120 +/- 0.078 | 0.867 +/- 0.073 | -0.907 +/- 0.132 | 16.0 +/- 2.1 |
| 0.95 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.610 +/- 0.019 | 39.0 +/- 1.9 |
| 0.95 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.589 +/- 0.006 | 41.1 +/- 0.6 |
| 0.95 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.021 | 40.1 +/- 2.1 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 5 | 0.633 +/- 0.385 | 0.160 +/- 0.233 | 0.053 +/- 0.525 | 42.0 +/- 15.8 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 5 | 0.607 +/- 0.177 | 0.393 +/- 0.177 | -0.072 +/- 0.307 | 28.5 +/- 4.7 |
| 0.95 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 5 | 0.867 +/- 0.235 | 0.060 +/- 0.120 | 0.404 +/- 0.351 | 40.3 +/- 1.6 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.613 +/- 0.141 | 0.320 +/- 0.189 | -0.033 +/- 0.248 | 32.6 +/- 8.3 |
| 0.95 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.207 +/- 0.289 | -0.784 +/- 0.118 | 57.8 +/- 17.1 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.50 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.75 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.75 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 0.856 +/- 0.147 | 0.945 +/- 0.059 | 15.4 | 2.6 |
| 0.95 | 0.05 | 0.889 +/- 0.172 | 0.955 +/- 0.072 | 8.0 | 1.0 |
| 0.95 | 0.10 | 0.511 +/- 0.163 | 0.760 +/- 0.115 | 9.2 | 8.8 |

## Gap Selection Diagnostics

| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.10 | 0.032 +/- 0.004 | 0.003 +/- 0.001 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 5.8 | 0.0 |
| 0.75 | 0.10 | 0.032 +/- 0.010 | 0.005 +/- 0.002 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 5.8 | 0.0 |
| 0.90 | 0.10 | 0.079 +/- 0.012 | 0.289 +/- 0.233 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 14.2 | 0.0 |
| 0.95 | 0.10 | 0.051 +/- 0.016 | 0.395 +/- 0.106 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.2 | 0.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.50 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 0.856 +/- 0.147 | 0.945 +/- 0.059 |
| 0.95 | 0.05 | 0.050 | 0.889 +/- 0.172 | 0.955 +/- 0.073 |
| 0.95 | 0.10 | 0.100 | 0.511 +/- 0.163 | 0.761 +/- 0.115 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- `tri_signal_gap_demo_bc` and `tri_signal_gap_posterior_bc` choose an unlabeled support size by the largest classifier-score gap within an allowed prefix.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
