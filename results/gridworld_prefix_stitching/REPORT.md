# GridWorld Diagnostic Report

Tri-PIQL training steps per run: `500`.
Scenario: `shortcut`.
Seeds: `[0, 1, 2]`.
Unlabeled bad fractions: `[0.25, 0.5, 0.75, 0.9]`.
Labeled positive prefix length: `6` (`0` means full trajectories).

## Policy Metrics

| bad_frac | method | success | trap | return |
|---|---|---:|---:|---:|
| 0.25 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.25 | bc_pos_unlabeled | 0.333 +/- 0.471 | 0.667 +/- 0.471 | -0.433 +/- 0.929 |
| 0.25 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.25 | tri_piql_greedy_q_diagnostic | 0.333 +/- 0.471 | 0.000 +/- 0.000 | 0.173 +/- 0.500 |
| 0.25 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.50 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.50 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | tri_piql_greedy_q_diagnostic | 0.333 +/- 0.471 | 0.000 +/- 0.000 | 0.173 +/- 0.500 |
| 0.50 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.75 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | tri_piql_greedy_q_diagnostic | 0.333 +/- 0.471 | 0.000 +/- 0.000 | 0.173 +/- 0.500 |
| 0.75 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | tri_piql_greedy_q_diagnostic | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | weighted_bc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |

## Latest Run Diagnostics

- Classifier labeled accuracy: `1.000`.
- Tri-PIQL q AUC on hidden unlabeled good/bad tags: `1.000`.
- Tri-PIQL learned return gap R(pos)-R(neg): `10.544`.
- Good transition advantage mean: `4.458`.
- Bad transition advantage mean: `-1.891`.
- Positive-demo transition reward mean: `0.815`.
- Negative-demo transition reward mean: `-0.740`.
- Goal-transition reward mean: `1.100`.
- Trap-transition reward mean: `-0.051`.

### Learned Reward Max Heatmap

```text
+2.38 +2.77 +2.30 +2.63 +2.92 +4.99   G   
+0.82 +0.21 +0.39 +0.25 -0.00 -0.11 +1.61
+0.81 -0.30 +0.59 +0.41 +0.00   T    +0.43
+0.83 +0.29 +0.60 -0.04 +0.60 -0.72 +0.37
+0.83 +1.17 +1.38 +1.19 -0.21 -0.38 +0.84
+0.82 +1.02 +1.36 +1.52 +1.20 -0.07 +0.87
  S    +1.14 +1.06 +1.14 +1.60 +0.44 +0.70
```

### Learned Q Max Heatmap

```text
+16.50 +14.56 +12.15 +10.16 +7.76 +4.99   G   
+16.84 +11.80 +9.76 +8.57 +5.78 +3.99 +2.23
+17.32 +11.54 +9.45 +7.60 +5.71   T    +2.25
+17.70 +12.27 +9.54 +7.11 +4.36 +1.87 +2.80
+18.00 +12.23 +10.40 +7.73 +4.07 +3.84 +4.33
+18.27 +13.77 +12.19 +10.30 +7.99 +5.62 +5.81
  S    +14.51 +12.89 +11.15 +9.37 +7.52 +7.25
```

## Immediate Interpretation

- Stage 1 passes if naive mixed-log cloning fails while Tri-PIQL succeeds.
- Stage 2 signals are promising if the learned positive-negative return gap is positive, good advantages are positive, bad advantages are negative, and negative-demo rewards are below positive-demo rewards.
- The greedy-Q row is diagnostic only; the intended offline policy is the advantage-weighted BC extractor.
