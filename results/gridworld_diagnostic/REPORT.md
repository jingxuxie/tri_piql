# GridWorld Diagnostic Report

Tri-PIQL training steps per run: `300`.
Scenario: `shortcut`.
Seeds: `[0, 1, 2]`.
Unlabeled bad fractions: `[0.25, 0.5, 0.75, 0.9]`.
Labeled positive prefix length: `0` (`0` means full trajectories).

## Policy Metrics

| bad_frac | method | success | trap | return |
|---|---|---:|---:|---:|
| 0.25 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.25 | bc_pos_unlabeled | 0.333 +/- 0.471 | 0.667 +/- 0.471 | -0.433 +/- 0.929 |
| 0.25 | bc_positive | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.25 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.25 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.50 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.50 | bc_positive | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_positive | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.75 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_positive | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |

## Latest Run Diagnostics

- Classifier labeled accuracy: `1.000`.
- Tri-PIQL q AUC on hidden unlabeled good/bad tags: `0.849`.
- Tri-PIQL learned return gap R(pos)-R(neg): `8.659`.
- Good transition advantage mean: `2.964`.
- Bad transition advantage mean: `-1.593`.
- Positive-demo transition reward mean: `0.462`.
- Negative-demo transition reward mean: `-0.464`.
- Goal-transition reward mean: `0.044`.
- Trap-transition reward mean: `-0.302`.

### Learned Reward Max Heatmap

```text
+0.49 +0.48 +0.49 +0.44 +0.49 +0.50   G   
+0.46 -0.06 -0.31 -0.90 -0.20 -2.12 -0.00
+0.56 +0.01 +0.00 -0.28 +0.00   T    +0.16
+0.48 +0.00 -0.06 -0.29 -0.20 -0.45 +0.01
+0.48 +0.56 +0.57 +0.35 +0.40 -0.33 +0.18
+0.47 +0.38 +0.60 +0.71 +0.53 -0.07 +0.19
  S    +1.13 +1.20 +1.22 +1.56 +0.45 +0.06
```

### Learned Q Max Heatmap

```text
+6.42 +5.85 +5.55 +5.26 +4.87 +4.56   G   
+10.55 +3.80 +2.74 +2.18 +4.62 -1.64 +0.29
+15.89 +7.58 +5.39 +4.09 +3.36   T    +1.56
+15.81 +10.60 +7.59 +5.43 +3.63 +1.83 +2.64
+15.73 +11.29 +8.76 +6.62 +3.93 +3.57 +4.09
+15.65 +12.26 +10.76 +9.19 +7.24 +5.23 +5.52
  S    +12.94 +11.55 +10.06 +8.52 +6.97 +6.66
```

## Immediate Interpretation

- Stage 1 passes if naive mixed-log cloning fails while Tri-PIQL succeeds.
- Stage 2 signals are promising if the learned positive-negative return gap is positive, good advantages are positive, bad advantages are negative, and negative-demo rewards are below positive-demo rewards.
- The greedy-Q row is diagnostic only; the intended offline policy is the advantage-weighted BC extractor.
