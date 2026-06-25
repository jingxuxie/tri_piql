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
| 0.50 | bc_all | 5 | 0.460 +/- 0.114 | 0.540 +/- 0.114 | -0.332 +/- 0.191 | 25.2 +/- 3.8 |
| 0.50 | bc_pos_unlabeled | 5 | 0.453 +/- 0.113 | 0.547 +/- 0.113 | -0.335 +/- 0.192 | 24.2 +/- 3.4 |
| 0.50 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.006 | 40.1 +/- 0.6 |
| 0.50 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.009 | 40.0 +/- 0.9 |
| 0.50 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.013 | 39.6 +/- 1.3 |
| 0.50 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.010 | 39.8 +/- 1.0 |
| 0.50 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.610 +/- 0.007 | 39.0 +/- 0.7 |
| 0.50 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.593 +/- 0.014 | 40.7 +/- 1.4 |
| 0.50 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.007 | 39.8 +/- 0.7 |
| 0.50 | weighted_bc_state_action | 5 | 0.187 +/- 0.373 | 0.000 +/- 0.000 | -0.457 +/- 0.486 | 64.4 +/- 11.2 |
| 0.75 | bc_all | 5 | 0.360 +/- 0.044 | 0.640 +/- 0.044 | -0.499 +/- 0.076 | 21.9 +/- 1.3 |
| 0.75 | bc_pos_unlabeled | 5 | 0.333 +/- 0.082 | 0.667 +/- 0.082 | -0.544 +/- 0.139 | 21.1 +/- 2.4 |
| 0.75 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.013 | 40.6 +/- 1.3 |
| 0.75 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.012 | 40.1 +/- 1.2 |
| 0.75 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.593 +/- 0.020 | 40.7 +/- 2.0 |
| 0.75 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.010 | 39.6 +/- 1.0 |
| 0.75 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.010 | 39.8 +/- 1.0 |
| 0.75 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.017 | 40.0 +/- 1.7 |
| 0.75 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.607 +/- 0.008 | 39.3 +/- 0.8 |
| 0.75 | weighted_bc_state_action | 5 | 0.180 +/- 0.360 | 0.013 +/- 0.027 | -0.472 +/- 0.470 | 63.9 +/- 10.4 |
| 0.90 | bc_all | 5 | 0.240 +/- 0.065 | 0.760 +/- 0.065 | -0.706 +/- 0.111 | 18.6 +/- 1.9 |
| 0.90 | bc_pos_unlabeled | 5 | 0.140 +/- 0.025 | 0.833 +/- 0.056 | -0.863 +/- 0.046 | 16.9 +/- 3.0 |
| 0.90 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.015 | 39.6 +/- 1.5 |
| 0.90 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.590 +/- 0.021 | 41.0 +/- 2.1 |
| 0.90 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.605 +/- 0.012 | 39.5 +/- 1.2 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.605 +/- 0.021 | 39.5 +/- 2.1 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 5 | 0.980 +/- 0.040 | 0.020 +/- 0.040 | 0.552 +/- 0.072 | 40.8 +/- 3.2 |
| 0.90 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.012 | 40.1 +/- 1.2 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.987 +/- 0.027 | 0.013 +/- 0.027 | 0.577 +/- 0.045 | 39.7 +/- 1.3 |
| 0.90 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.187 +/- 0.284 | -0.777 +/- 0.116 | 59.0 +/- 16.8 |
| 0.95 | bc_all | 5 | 0.153 +/- 0.069 | 0.847 +/- 0.069 | -0.849 +/- 0.120 | 15.6 +/- 1.8 |
| 0.95 | bc_pos_unlabeled | 5 | 0.080 +/- 0.065 | 0.893 +/- 0.049 | -0.966 +/- 0.103 | 15.3 +/- 1.7 |
| 0.95 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 5 | 0.800 +/- 0.400 | 0.000 +/- 0.000 | 0.337 +/- 0.518 | 46.3 +/- 11.9 |
| 0.95 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.020 | 39.8 +/- 2.0 |
| 0.95 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.611 +/- 0.008 | 38.9 +/- 0.8 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 5 | 0.987 +/- 0.027 | 0.013 +/- 0.027 | 0.577 +/- 0.046 | 39.7 +/- 2.3 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 5 | 0.567 +/- 0.349 | 0.267 +/- 0.210 | -0.078 +/- 0.490 | 37.8 +/- 12.9 |
| 0.95 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 5 | 0.960 +/- 0.080 | 0.040 +/- 0.080 | 0.536 +/- 0.140 | 38.4 +/- 2.4 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.700 +/- 0.179 | 0.300 +/- 0.179 | 0.086 +/- 0.307 | 31.4 +/- 5.2 |
| 0.95 | weighted_bc_state_action | 5 | 0.320 +/- 0.412 | 0.180 +/- 0.360 | -0.364 +/- 0.599 | 50.4 +/- 19.7 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.50 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.75 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.75 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 0.956 +/- 0.065 | 0.985 +/- 0.022 | 17.2 | 0.8 |
| 0.95 | 0.05 | 0.978 +/- 0.044 | 0.993 +/- 0.015 | 8.8 | 0.2 |
| 0.95 | 0.10 | 0.567 +/- 0.089 | 0.812 +/- 0.054 | 10.2 | 7.8 |

## Gap Selection Diagnostics

| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.10 | 0.031 +/- 0.018 | 0.004 +/- 0.001 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 5.6 | 0.0 |
| 0.75 | 0.10 | 0.049 +/- 0.021 | 0.003 +/- 0.002 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 8.8 | 0.0 |
| 0.90 | 0.10 | 0.080 +/- 0.021 | 0.201 +/- 0.237 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 14.4 | 0.0 |
| 0.95 | 0.10 | 0.057 +/- 0.009 | 0.396 +/- 0.054 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 10.2 | 0.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.50 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 0.956 +/- 0.065 | 0.985 +/- 0.022 |
| 0.95 | 0.05 | 0.050 | 0.978 +/- 0.044 | 0.993 +/- 0.015 |
| 0.95 | 0.10 | 0.100 | 0.567 +/- 0.089 | 0.812 +/- 0.055 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- `tri_signal_gap_demo_bc` and `tri_signal_gap_posterior_bc` choose an unlabeled support size by the largest classifier-score gap within an allowed prefix.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
