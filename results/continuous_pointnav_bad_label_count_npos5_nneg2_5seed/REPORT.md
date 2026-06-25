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
| 0.50 | bc_all | 5 | 0.487 +/- 0.034 | 0.513 +/- 0.034 | -0.279 +/- 0.054 | 25.2 +/- 1.4 |
| 0.50 | bc_pos_unlabeled | 5 | 0.440 +/- 0.085 | 0.560 +/- 0.085 | -0.358 +/- 0.146 | 23.8 +/- 2.5 |
| 0.50 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.607 +/- 0.012 | 39.3 +/- 1.2 |
| 0.50 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.009 | 39.7 +/- 0.9 |
| 0.50 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.011 | 39.9 +/- 1.1 |
| 0.50 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.611 +/- 0.009 | 38.9 +/- 0.9 |
| 0.50 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.009 | 39.6 +/- 0.9 |
| 0.50 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.612 +/- 0.008 | 38.8 +/- 0.8 |
| 0.50 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.612 +/- 0.011 | 38.8 +/- 1.1 |
| 0.50 | weighted_bc_state_action | 5 | 0.200 +/- 0.400 | 0.000 +/- 0.000 | -0.439 +/- 0.522 | 63.9 +/- 12.2 |
| 0.75 | bc_all | 5 | 0.353 +/- 0.040 | 0.647 +/- 0.040 | -0.515 +/- 0.065 | 22.1 +/- 1.6 |
| 0.75 | bc_pos_unlabeled | 5 | 0.287 +/- 0.159 | 0.660 +/- 0.077 | -0.601 +/- 0.232 | 22.7 +/- 2.9 |
| 0.75 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.008 | 39.9 +/- 0.8 |
| 0.75 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.010 | 39.6 +/- 1.0 |
| 0.75 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.607 +/- 0.015 | 39.3 +/- 1.5 |
| 0.75 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.014 | 39.8 +/- 1.4 |
| 0.75 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.008 | 39.6 +/- 0.8 |
| 0.75 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.597 +/- 0.014 | 40.3 +/- 1.4 |
| 0.75 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.018 | 40.4 +/- 1.8 |
| 0.75 | weighted_bc_state_action | 5 | 0.147 +/- 0.293 | 0.000 +/- 0.000 | -0.510 +/- 0.380 | 65.7 +/- 8.6 |
| 0.90 | bc_all | 5 | 0.220 +/- 0.120 | 0.780 +/- 0.120 | -0.735 +/- 0.205 | 17.5 +/- 3.5 |
| 0.90 | bc_pos_unlabeled | 5 | 0.220 +/- 0.083 | 0.780 +/- 0.083 | -0.740 +/- 0.139 | 18.0 +/- 2.9 |
| 0.90 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.023 | 40.4 +/- 2.3 |
| 0.90 | tri_signal_gap_demo_bc_max0p1 | 5 | 0.973 +/- 0.053 | 0.027 +/- 0.053 | 0.561 +/- 0.092 | 38.6 +/- 2.1 |
| 0.90 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.612 +/- 0.014 | 38.8 +/- 1.4 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.012 | 39.9 +/- 1.2 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 5 | 0.840 +/- 0.162 | 0.160 +/- 0.162 | 0.312 +/- 0.289 | 36.8 +/- 3.8 |
| 0.90 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.609 +/- 0.016 | 39.1 +/- 1.6 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.827 +/- 0.150 | 0.147 +/- 0.129 | 0.320 +/- 0.247 | 36.0 +/- 3.6 |
| 0.90 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.020 +/- 0.040 | -0.708 +/- 0.015 | 68.8 +/- 2.5 |
| 0.95 | bc_all | 5 | 0.147 +/- 0.096 | 0.847 +/- 0.093 | -0.862 +/- 0.164 | 16.2 +/- 2.6 |
| 0.95 | bc_pos_unlabeled | 5 | 0.113 +/- 0.096 | 0.887 +/- 0.096 | -0.921 +/- 0.162 | 14.7 +/- 3.0 |
| 0.95 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.595 +/- 0.006 | 40.5 +/- 0.6 |
| 0.95 | tri_signal_gap_demo_bc_max0p1 | 5 | 0.993 +/- 0.013 | 0.000 +/- 0.000 | 0.590 +/- 0.012 | 40.4 +/- 1.4 |
| 0.95 | tri_signal_gap_posterior_bc_max0p1 | 5 | 0.600 +/- 0.490 | 0.000 +/- 0.000 | 0.083 +/- 0.640 | 51.7 +/- 15.0 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 5 | 0.973 +/- 0.053 | 0.027 +/- 0.053 | 0.557 +/- 0.080 | 39.0 +/- 4.1 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 5 | 0.600 +/- 0.180 | 0.400 +/- 0.180 | -0.089 +/- 0.305 | 28.9 +/- 5.9 |
| 0.95 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 5 | 0.900 +/- 0.200 | 0.100 +/- 0.200 | 0.431 +/- 0.344 | 36.9 +/- 5.9 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.607 +/- 0.187 | 0.393 +/- 0.187 | -0.079 +/- 0.323 | 29.2 +/- 5.1 |
| 0.95 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.50 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.75 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.75 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 0.922 +/- 0.083 | 0.974 +/- 0.029 | 16.6 | 1.4 |
| 0.95 | 0.05 | 0.911 +/- 0.178 | 0.963 +/- 0.075 | 8.2 | 0.8 |
| 0.95 | 0.10 | 0.567 +/- 0.163 | 0.795 +/- 0.120 | 10.2 | 7.8 |

## Gap Selection Diagnostics

| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.10 | 0.039 +/- 0.012 | 0.003 +/- 0.001 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 7.0 | 0.0 |
| 0.75 | 0.10 | 0.037 +/- 0.018 | 0.003 +/- 0.002 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 6.6 | 0.0 |
| 0.90 | 0.10 | 0.089 +/- 0.006 | 0.253 +/- 0.217 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 16.0 | 0.0 |
| 0.95 | 0.10 | 0.057 +/- 0.016 | 0.477 +/- 0.070 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 10.2 | 0.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.50 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 0.922 +/- 0.083 | 0.974 +/- 0.029 |
| 0.95 | 0.05 | 0.050 | 0.911 +/- 0.178 | 0.963 +/- 0.075 |
| 0.95 | 0.10 | 0.100 | 0.567 +/- 0.163 | 0.796 +/- 0.121 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- `tri_signal_gap_demo_bc` and `tri_signal_gap_posterior_bc` choose an unlabeled support size by the largest classifier-score gap within an allowed prefix.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
