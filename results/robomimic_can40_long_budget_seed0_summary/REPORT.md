# Can 40p/80b Seed-0 Long-Budget Diagnostic

This diagnostic tests whether the Can 40 positive / 80 bad weighted-BC baseline is simply under-trained at the existing 20k-step budget.

Protocol:

- Task/split: Robomimic Can paired low-dim, 40 labeled positives / 80 labeled bads.
- Policy: official Robomimic BC-RNN-GMM.
- Seed: policy seed 0 only.
- Training budget: 50k optimizer steps from scratch, checkpoints every 10k steps.
- Evaluation: 10 held-out validation-positive initial states, horizon 400.
- Fairness detail: the 50k configs preserve the original 20k train mask keys and weighted sampler weights. A regenerated selector config was not used because the current selector script selected a different masscap support set.

## Budget Curve

| method | 10k | 20k | 30k | 40k | 50k | best |
|---|---:|---:|---:|---:|---:|---:|
| adaptive masscap | 0.300 | 0.800 | 0.800 | 0.700 | 0.600 | 0.800 |
| weighted probability sampler | 0.700 | 0.500 | 0.300 | 0.500 | 0.300 | 0.700 |

## Interpretation

- This seed-0 budget check does not support the explanation that weighted BC only needed more optimization. Weighted BC peaks early at 10k and is worse at 20k/30k/40k/50k.
- Masscap is not monotonically improved by longer training either: it is strongest at 20k/30k and degrades at 40k/50k.
- This strengthens fixed-budget reporting around 20k and argues against running much longer Robomimic BC training by default.
- Because this is a one-seed diagnostic, it should be used as a budget/optimization sanity check, not as a replacement for the existing three-seed Can 40p/80b table.

## Artifacts

- Masscap config: `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_existingmask_50k_setup/config.json`
- Masscap eval: `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_existingmask_50k_eval/REPORT.md`
- Weighted config: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_existingmask_50k_setup/config.json`
- Weighted eval: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_existingmask_50k_eval/REPORT.md`
