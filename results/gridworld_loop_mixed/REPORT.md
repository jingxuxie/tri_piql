# GridWorld Diagnostic Report

Tri-PIQL training steps per run: `600`.
Scenario: `loop_mixed`.
Seeds: `[0, 1, 2]`.
Unlabeled bad fractions: `[0.25, 0.5, 0.75, 0.9]`.
Labeled positive prefix length: `6` (`0` means full trajectories).

## Policy Metrics

| bad_frac | method | success | trap | return |
|---|---|---:|---:|---:|
| 0.25 | bc_all | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | bc_pos_unlabeled | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.25 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | weighted_bc | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | bc_all | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | bc_pos_unlabeled | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | tri_piql_greedy_q_diagnostic | 0.667 +/- 0.471 | 0.000 +/- 0.000 | 0.527 +/- 0.500 |
| 0.50 | weighted_bc | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.75 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.75 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | tri_piql_greedy_q_diagnostic | 0.667 +/- 0.471 | 0.000 +/- 0.000 | 0.527 +/- 0.500 |
| 0.75 | weighted_bc | 0.000 +/- 0.000 | 0.667 +/- 0.471 | -0.787 +/- 0.429 |
| 0.90 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | weighted_bc | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |

## Latest Run Diagnostics

- Classifier labeled accuracy: `1.000`.
- Tri-PIQL q AUC on hidden unlabeled good/bad tags: `0.969`.
- Tri-PIQL learned return gap R(pos)-R(neg): `8.205`.
- Good transition advantage mean: `4.150`.
- Bad transition advantage mean: `-2.271`.
- Positive-demo transition reward mean: `1.030`.
- Negative-demo transition reward mean: `-2.388`.
- Goal-transition reward mean: `0.449`.
- Trap-transition reward mean: `0.153`.

### Learned Reward Max Heatmap

```text
+0.87 +0.24 +0.12 -0.24 -0.38 +2.14   G   
-0.05 +0.02 +0.06 +0.00 -0.00 -0.00 +0.56
+1.24 -0.45 -0.07 +0.04 +0.02   T    +0.57
+1.25 -0.18 -0.05 +0.01 +1.01 +0.66 -0.25
+1.25 -0.18 -0.10 -0.04 -0.02 +0.24 +0.22
+1.24 +0.00 +0.58 +0.66 +0.43 +0.19 +0.31
  S    +0.13 +0.17 +0.13 +0.13 +0.05 +0.17
```

### Learned Q Max Heatmap

```text
+11.44 +10.95 +9.49 +7.72 +5.78 +4.26   G   
+11.19 +7.11 +6.20 +5.73 +4.41 +2.67 +1.50
+12.03 +5.40 +5.93 +6.06 +4.80   T    +1.43
+12.97 +7.29 +7.03 +6.22 +4.34 +1.91 +1.79
+13.76 +8.39 +7.79 +6.39 +4.43 +3.30 +2.61
+14.52 +9.73 +8.93 +7.24 +6.11 +4.68 +3.54
  S    +11.63 +10.09 +8.58 +7.21 +5.88 +4.49
```

## Immediate Interpretation

- Stage 1 passes if naive mixed-log cloning fails while Tri-PIQL succeeds.
- Stage 2 signals are promising if the learned positive-negative return gap is positive, good advantages are positive, bad advantages are negative, and negative-demo rewards are below positive-demo rewards.
- The greedy-Q row is diagnostic only; the intended offline policy is the advantage-weighted BC extractor.
