# Continuous PointNav Tri-Signal Smoke

Status: `complete_merged_from_partial_and_95bad`.
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
| 0.50 | bc_all | 5 | 0.460 +/- 0.124 | 0.540 +/- 0.124 | -0.324 +/- 0.210 | 24.4 +/- 3.7 |
| 0.50 | bc_pos_unlabeled | 5 | 0.453 +/- 0.122 | 0.547 +/- 0.122 | -0.341 +/- 0.205 | 24.8 +/- 4.0 |
| 0.50 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.595 +/- 0.009 | 40.5 +/- 0.9 |
| 0.50 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.005 | 40.0 +/- 0.5 |
| 0.50 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.610 +/- 0.006 | 39.0 +/- 0.6 |
| 0.50 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.003 | 40.4 +/- 0.3 |
| 0.50 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.602 +/- 0.011 | 39.8 +/- 1.1 |
| 0.50 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.007 | 39.7 +/- 0.7 |
| 0.50 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.006 | 39.4 +/- 0.6 |
| 0.50 | weighted_bc_state_action | 5 | 0.400 +/- 0.490 | 0.000 +/- 0.000 | -0.174 +/- 0.644 | 57.4 +/- 15.4 |
| 0.75 | bc_all | 5 | 0.367 +/- 0.060 | 0.633 +/- 0.060 | -0.493 +/- 0.099 | 22.7 +/- 2.0 |
| 0.75 | bc_pos_unlabeled | 5 | 0.300 +/- 0.079 | 0.700 +/- 0.079 | -0.597 +/- 0.134 | 19.7 +/- 2.5 |
| 0.75 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.010 | 40.6 +/- 1.0 |
| 0.75 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.003 | 39.4 +/- 0.3 |
| 0.75 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.009 | 39.9 +/- 0.9 |
| 0.75 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.595 +/- 0.018 | 40.5 +/- 1.8 |
| 0.75 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.594 +/- 0.014 | 40.6 +/- 1.4 |
| 0.75 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.609 +/- 0.011 | 39.1 +/- 1.1 |
| 0.75 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.608 +/- 0.006 | 39.2 +/- 0.6 |
| 0.75 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | bc_all | 5 | 0.233 +/- 0.128 | 0.767 +/- 0.128 | -0.716 +/- 0.220 | 18.2 +/- 3.7 |
| 0.90 | bc_pos_unlabeled | 5 | 0.247 +/- 0.105 | 0.753 +/- 0.105 | -0.690 +/- 0.183 | 18.4 +/- 2.7 |
| 0.90 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.614 +/- 0.007 | 38.6 +/- 0.7 |
| 0.90 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.610 +/- 0.012 | 39.0 +/- 1.2 |
| 0.90 | tri_signal_gap_posterior_bc_max0p1 | 5 | 0.800 +/- 0.400 | 0.000 +/- 0.000 | 0.331 +/- 0.516 | 46.9 +/- 11.7 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.017 | 39.7 +/- 1.7 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 5 | 0.953 +/- 0.093 | 0.047 +/- 0.093 | 0.500 +/- 0.180 | 40.6 +/- 1.7 |
| 0.90 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.010 | 40.1 +/- 1.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.947 +/- 0.107 | 0.053 +/- 0.107 | 0.506 +/- 0.181 | 38.7 +/- 3.4 |
| 0.90 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.200 +/- 0.400 | -0.833 +/- 0.265 | 63.3 +/- 13.5 |
| 0.95 | bc_all | 5 | 0.153 +/- 0.054 | 0.847 +/- 0.054 | -0.857 +/- 0.092 | 16.3 +/- 1.8 |
| 0.95 | bc_pos_unlabeled | 5 | 0.060 +/- 0.053 | 0.853 +/- 0.034 | -0.980 +/- 0.060 | 18.7 +/- 3.1 |
| 0.95 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.579 +/- 0.025 | 42.1 +/- 2.5 |
| 0.95 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.012 | 39.4 +/- 1.2 |
| 0.95 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.605 +/- 0.021 | 39.5 +/- 2.1 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 5 | 0.800 +/- 0.400 | 0.087 +/- 0.173 | 0.311 +/- 0.595 | 40.3 +/- 2.8 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 5 | 0.527 +/- 0.255 | 0.387 +/- 0.098 | -0.169 +/- 0.375 | 30.9 +/- 4.2 |
| 0.95 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 5 | 0.887 +/- 0.227 | 0.113 +/- 0.227 | 0.414 +/- 0.389 | 35.9 +/- 6.5 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.673 +/- 0.254 | 0.320 +/- 0.260 | 0.053 +/- 0.438 | 30.1 +/- 7.6 |
| 0.95 | weighted_bc_state_action | 5 | 0.200 +/- 0.400 | 0.000 +/- 0.000 | -0.449 +/- 0.502 | 64.9 +/- 10.2 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.50 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.75 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.75 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 0.967 +/- 0.067 | 0.989 +/- 0.023 | 17.4 | 0.6 |
| 0.95 | 0.05 | 0.911 +/- 0.178 | 0.964 +/- 0.073 | 8.2 | 0.8 |
| 0.95 | 0.10 | 0.556 +/- 0.149 | 0.793 +/- 0.114 | 10.0 | 8.0 |

## Gap Selection Diagnostics

| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.10 | 0.048 +/- 0.027 | 0.004 +/- 0.001 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 8.6 | 0.0 |
| 0.75 | 0.10 | 0.040 +/- 0.009 | 0.003 +/- 0.001 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 7.2 | 0.0 |
| 0.90 | 0.10 | 0.089 +/- 0.005 | 0.106 +/- 0.191 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 16.0 | 0.0 |
| 0.95 | 0.10 | 0.056 +/- 0.015 | 0.398 +/- 0.079 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 10.0 | 0.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.50 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 0.967 +/- 0.067 | 0.989 +/- 0.022 |
| 0.95 | 0.05 | 0.050 | 0.911 +/- 0.178 | 0.963 +/- 0.074 |
| 0.95 | 0.10 | 0.100 | 0.556 +/- 0.149 | 0.793 +/- 0.114 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- `tri_signal_gap_demo_bc` and `tri_signal_gap_posterior_bc` choose an unlabeled support size by the largest classifier-score gap within an allowed prefix.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
