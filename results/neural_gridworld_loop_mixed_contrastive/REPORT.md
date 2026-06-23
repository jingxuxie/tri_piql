# Neural GridWorld Loop-Mixed Report

Training steps per run: `1200`.
Seeds: `[0, 1, 2]`.
Unlabeled bad fractions: `[0.25, 0.5, 0.75, 0.9]`.
Labeled positive prefix length: `6`.
Feature mode: `coords`.
Negative shortcut fraction in labeled bad set: `0.5`.
MLP: depth `2`, hidden dim `64`, lr `0.003`.

## Policy Metrics

| bad_frac | method | success | trap | return |
|---|---|---:|---:|---:|
| 0.25 | bc_all | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | bc_pos_unlabeled | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.25 | neural_tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.25 | neural_tri_piql_greedy_q_diagnostic | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.25 | weighted_bc | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | bc_all | 0.000 +/- 0.000 | 0.333 +/- 0.471 | -0.483 +/- 0.429 |
| 0.50 | bc_pos_unlabeled | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.50 | neural_tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.50 | neural_tri_piql_greedy_q_diagnostic | 0.667 +/- 0.471 | 0.000 +/- 0.000 | 0.527 +/- 0.500 |
| 0.50 | weighted_bc | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.75 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.75 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.75 | neural_tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | neural_tri_piql_greedy_q_diagnostic | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.75 | weighted_bc | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | bc_all | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_pos_unlabeled | 0.000 +/- 0.000 | 1.000 +/- 0.000 | -1.090 +/- 0.000 |
| 0.90 | bc_positive | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |
| 0.90 | neural_tri_piql_awbc | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | neural_tri_piql_greedy_q_diagnostic | 1.000 +/- 0.000 | 0.000 +/- 0.000 | 0.880 +/- 0.000 |
| 0.90 | weighted_bc | 0.000 +/- 0.000 | 0.000 +/- 0.000 | -0.180 +/- 0.000 |

## Latest Run Diagnostics

- Neural Tri-PIQL q AUC on hidden unlabeled tags: `1.000`.
- Learned return gap R(pos)-R(neg): `51.190`.
- Good transition advantage mean: `3.480`.
- Bad transition advantage mean: `-2.163`.
- Positive-demo transition reward mean: `7.257`.
- Negative-demo transition reward mean: `-2.182`.

### Learned Reward Max Heatmap

```text
-0.78 -1.31 -1.32 -1.26 -1.19 -1.15   G   
+5.48 +0.19 -0.87 -1.03 -1.06 -1.06 -1.06
+7.42 +3.30 -0.62 -0.99 -1.04   T    -1.04
+8.04 +5.06 +1.40 -0.91 -1.02 -1.04 -1.03
+7.92 +5.60 +3.32 +0.17 -0.99 -1.02 -1.02
+7.74 +5.56 +3.58 +2.60 -0.55 -1.01 -1.02
  S    +5.62 +3.58 +2.80 +1.81 -0.85 -1.02
```

### Learned Q Max Heatmap

```text
-18.91 -11.68 -7.56 -5.03 -3.03 -1.31   G   
-12.78 -11.14 -7.18 -4.94 -3.27 -1.78 -0.85
-4.98 -7.00 -2.52 -1.22 -0.31   T    +1.25
+3.22 +0.40 +2.79 +2.90 +2.80 +3.10 +3.29
+11.04 +7.83 +8.01 +7.08 +6.12 +5.59 +5.29
+18.44 +14.93 +13.08 +11.11 +9.41 +8.16 +7.27
  S    +21.44 +17.91 +14.97 +12.64 +10.89 +9.38
```

## Immediate Interpretation

- This run tests whether the loop-mixed tabular mechanism survives a neural reward parameterization.
- A useful result requires neural Tri-PIQL AWBC to beat weighted BC while preserving positive good/bad advantage separation.
