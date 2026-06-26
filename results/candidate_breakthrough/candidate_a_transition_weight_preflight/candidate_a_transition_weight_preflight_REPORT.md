# Candidate A Transition-Weight Preflight

This preflight builds transition-level loss weights for the Can split-404 failure case.
It does not train a policy; it creates the artifact needed for a weighted BC-RNN-GMM loss hook.

## Pool

- Train demos: `54`.
- Labeled positive anchors: `10`.
- Selected unlabeled demos: `44` (`39` hidden positive, `5` hidden bad).
- Positive-only anchor demos inside selected pool: `40`; union-only additions: `4` (`4` hidden positive, `0` hidden bad).

## Weight Mass

- Hidden-bad unweighted transition fraction: `0.082`.
- Hidden-bad weighted mass fraction: `0.045`.
- Labeled-positive mass: `1118.0`.
- Hidden-positive selected mass: `2074.8`.
- Hidden-bad selected mass: `98.3`.

## Lowest-Weight Selected Bad Demos

| demo | mean weight | safe factor | action conflict | bad-neighbor risk |
| --- | ---: | ---: | ---: | ---: |
| demo_70 | 0.228820 | 0.524500 | 2.426061 | 0.724685 |
| demo_142 | 0.236313 | 0.545313 | 2.085877 | 0.877937 |
| demo_2 | 0.254433 | 0.595647 | 1.720717 | 0.179155 |
| demo_110 | 0.263212 | 0.551315 | 2.074156 | 0.720255 |
| demo_184 | 0.329528 | 0.541565 | 2.365008 | 0.341092 |

## Outputs

- Loss weights HDF5: `results/candidate_breakthrough/candidate_a_transition_weight_preflight/candidate_a_loss_weights.hdf5`.
- Per-demo summary CSV: `results/candidate_breakthrough/candidate_a_transition_weight_preflight/candidate_a_transition_weight_summary.csv`.
- Recipe JSON: `results/candidate_breakthrough/candidate_a_transition_weight_preflight/candidate_a_transition_weight_recipe.json`.

Next trainer hook: load `data/<demo_id>/loss_weight` and multiply the BC-RNN-GMM per-timestep NLL as
`-(log_probs * loss_weight).sum() / loss_weight.sum()` after sequence padding is handled.
