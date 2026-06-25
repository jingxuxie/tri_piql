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
| 0.50 | bc_all | 5 | 0.400 +/- 0.179 | 0.600 +/- 0.179 | -0.431 +/- 0.307 | 23.1 +/- 5.1 |
| 0.50 | bc_pos_unlabeled | 5 | 0.467 +/- 0.125 | 0.533 +/- 0.125 | -0.312 +/- 0.211 | 24.5 +/- 3.9 |
| 0.50 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.005 | 40.4 +/- 0.5 |
| 0.50 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.603 +/- 0.007 | 39.7 +/- 0.7 |
| 0.50 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.006 | 39.9 +/- 0.6 |
| 0.50 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.010 | 39.4 +/- 1.0 |
| 0.50 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.010 | 40.0 +/- 1.0 |
| 0.50 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.50 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.599 +/- 0.009 | 40.1 +/- 0.9 |
| 0.50 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.593 +/- 0.012 | 40.7 +/- 1.2 |
| 0.50 | weighted_bc_state_action | 5 | 0.200 +/- 0.400 | 0.000 +/- 0.000 | -0.440 +/- 0.520 | 64.0 +/- 12.0 |
| 0.75 | bc_all | 5 | 0.340 +/- 0.080 | 0.660 +/- 0.080 | -0.534 +/- 0.138 | 21.4 +/- 2.3 |
| 0.75 | bc_pos_unlabeled | 5 | 0.293 +/- 0.077 | 0.707 +/- 0.077 | -0.614 +/- 0.126 | 20.0 +/- 2.9 |
| 0.75 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.596 +/- 0.017 | 40.4 +/- 1.7 |
| 0.75 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.600 +/- 0.005 | 40.0 +/- 0.5 |
| 0.75 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.013 | 39.9 +/- 1.3 |
| 0.75 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.601 +/- 0.013 | 39.9 +/- 1.3 |
| 0.75 | tri_signal_posterior_bc_prior0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.593 +/- 0.017 | 40.7 +/- 1.7 |
| 0.75 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.75 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.009 | 39.4 +/- 0.9 |
| 0.75 | tri_signal_top_demo_bc_frac0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.011 | 39.4 +/- 1.1 |
| 0.75 | weighted_bc_state_action | 5 | 0.200 +/- 0.400 | 0.000 +/- 0.000 | -0.439 +/- 0.521 | 63.9 +/- 12.1 |
| 0.90 | bc_all | 5 | 0.240 +/- 0.106 | 0.760 +/- 0.106 | -0.702 +/- 0.183 | 18.2 +/- 3.0 |
| 0.90 | bc_pos_unlabeled | 5 | 0.147 +/- 0.117 | 0.827 +/- 0.093 | -0.856 +/- 0.189 | 17.6 +/- 2.8 |
| 0.90 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.608 +/- 0.014 | 39.2 +/- 1.4 |
| 0.90 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.605 +/- 0.016 | 39.5 +/- 1.6 |
| 0.90 | tri_signal_gap_posterior_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.606 +/- 0.013 | 39.4 +/- 1.3 |
| 0.90 | tri_signal_posterior_bc_prior0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.586 +/- 0.027 | 41.4 +/- 2.7 |
| 0.90 | tri_signal_posterior_bc_prior0p1 | 5 | 0.727 +/- 0.376 | 0.073 +/- 0.104 | 0.217 +/- 0.489 | 43.7 +/- 13.5 |
| 0.90 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p05 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.604 +/- 0.010 | 39.6 +/- 1.0 |
| 0.90 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.907 +/- 0.116 | 0.093 +/- 0.116 | 0.437 +/- 0.202 | 37.7 +/- 3.1 |
| 0.90 | weighted_bc_state_action | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | bc_all | 5 | 0.100 +/- 0.056 | 0.853 +/- 0.034 | -0.925 +/- 0.078 | 17.1 +/- 2.6 |
| 0.95 | bc_pos_unlabeled | 5 | 0.113 +/- 0.088 | 0.833 +/- 0.084 | -0.898 +/- 0.129 | 17.8 +/- 5.1 |
| 0.95 | bc_positive_prefix | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | oracle_good_bc | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.605 +/- 0.014 | 39.5 +/- 1.4 |
| 0.95 | tri_signal_gap_demo_bc_max0p1 | 5 | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.595 +/- 0.005 | 40.5 +/- 0.5 |
| 0.95 | tri_signal_gap_posterior_bc_max0p1 | 5 | 0.573 +/- 0.471 | 0.000 +/- 0.000 | 0.063 +/- 0.627 | 51.0 +/- 15.7 |
| 0.95 | tri_signal_posterior_bc_prior0p05 | 5 | 0.647 +/- 0.340 | 0.120 +/- 0.240 | 0.096 +/- 0.497 | 43.0 +/- 13.8 |
| 0.95 | tri_signal_posterior_bc_prior0p1 | 5 | 0.567 +/- 0.156 | 0.433 +/- 0.156 | -0.141 +/- 0.273 | 27.4 +/- 4.1 |
| 0.95 | tri_signal_rerank | 5 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.700 +/- 0.000 | 70.0 +/- 0.0 |
| 0.95 | tri_signal_top_demo_bc_frac0p05 | 5 | 0.900 +/- 0.200 | 0.033 +/- 0.067 | 0.463 +/- 0.288 | 40.4 +/- 2.4 |
| 0.95 | tri_signal_top_demo_bc_frac0p1 | 5 | 0.600 +/- 0.213 | 0.400 +/- 0.213 | -0.077 +/- 0.367 | 27.7 +/- 5.9 |
| 0.95 | weighted_bc_state_action | 5 | 0.140 +/- 0.280 | 0.147 +/- 0.185 | -0.577 +/- 0.338 | 57.1 +/- 16.3 |

## Selection Diagnostics

| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.50 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.75 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.75 | 0.10 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 18.0 | 0.0 |
| 0.90 | 0.05 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 9.0 | 0.0 |
| 0.90 | 0.10 | 0.956 +/- 0.065 | 0.985 +/- 0.021 | 17.2 | 0.8 |
| 0.95 | 0.05 | 0.911 +/- 0.178 | 0.963 +/- 0.074 | 8.2 | 0.8 |
| 0.95 | 0.10 | 0.567 +/- 0.163 | 0.798 +/- 0.121 | 10.2 | 7.8 |

## Gap Selection Diagnostics

| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.10 | 0.034 +/- 0.007 | 0.002 +/- 0.001 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 6.2 | 0.0 |
| 0.75 | 0.10 | 0.062 +/- 0.024 | 0.003 +/- 0.002 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 11.2 | 0.0 |
| 0.90 | 0.10 | 0.089 +/- 0.005 | 0.219 +/- 0.253 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 16.0 | 0.0 |
| 0.95 | 0.10 | 0.057 +/- 0.016 | 0.413 +/- 0.087 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 10.2 | 0.0 |

## Posterior Diagnostics

| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |
|---:|---:|---:|---:|---:|
| 0.50 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.50 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.75 | 0.10 | 0.100 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.05 | 0.050 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| 0.90 | 0.10 | 0.100 | 0.956 +/- 0.065 | 0.985 +/- 0.022 |
| 0.95 | 0.05 | 0.050 | 0.911 +/- 0.178 | 0.963 +/- 0.075 |
| 0.95 | 0.10 | 0.100 | 0.567 +/- 0.163 | 0.798 +/- 0.122 |

## Interpretation

- This is a controlled continuous-action bridge task between GridWorld and Robomimic.
- Positive labels are route prefixes, so positive-only BC lacks full-route support.
- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.
- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.
- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.
- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.
- `tri_signal_gap_demo_bc` and `tri_signal_gap_posterior_bc` choose an unlabeled support size by the largest classifier-score gap within an allowed prefix.
- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.
