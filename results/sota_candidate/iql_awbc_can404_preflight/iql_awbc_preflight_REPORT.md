# SOTA Candidate 6 IQL-AWBC Can404 Preflight

This is a bounded Offline RL / IQL revisit preflight from `triage_bc_sota_candidate_plan.md`.
It trains a small classifier-reward Q/V model on the Can404 broad pool, then converts Q-V advantages into transition weights for the existing Robomimic BC-RNN-GMM extractor.

## Setup

- Split: `/home/eston/tri-piql/results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json`.
- IQL/QV steps: `800`.
- State-action classifier steps: `800`.
- Selected extraction recipe: `norm_topq`.
- Top-q score threshold for `norm_topq`: `0.592417`.

## Q/V Diagnostics

- State-action classifier labeled accuracy: `0.997`.
- Classifier logit means, pos/neg/unlabeled: `10.415` / `-9.306` / `-0.880`.
- Learned advantage means, pos/neg/unlabeled: `1.232` / `-1.184` / `-0.123`.
- Learned Q means, pos/neg/unlabeled: `20.154` / `-6.410` / `4.248`.

## Weight Summary

| recipe | hidden-positive mass | hidden-bad mass | bad mass frac | pos mean w | bad mean w | ESS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw | 1673.573301 | 3071.130312 | 0.647275 | 0.384288 | 0.432188 | 8327.307547 |
| norm | 1725.179712 | 3510.336685 | 0.670485 | 0.396138 | 0.493996 | 9091.154796 |
| norm_topq | 1100.652676 | 532.651466 | 0.326119 | 0.252733 | 0.074958 | 3542.238997 |

## Decision

- Decision: `candidate_for_short_endpoint`.
- Read: the selected recipe improves the hidden-bad mass diagnostic enough to justify a bounded Can404 endpoint screen.
- Rejected SM-RWBC reference bad mass fraction: `0.376`.
- Selected IQL-AWBC bad mass fraction: `0.326`.
- Selected IQL-AWBC hidden-positive mass: `1100.7`.

## Artifacts

- Selected weights HDF5: `/home/eston/tri-piql/results/sota_candidate/iql_awbc_can404_preflight/iql_awbc_loss_weights.hdf5`.
- Selected per-demo CSV: `/home/eston/tri-piql/results/sota_candidate/iql_awbc_can404_preflight/iql_awbc_selected_demo_summary.csv`.
- Recipe summary CSV: `/home/eston/tri-piql/results/sota_candidate/iql_awbc_can404_preflight/iql_awbc_recipe_summary.csv`.
- Diagnostics JSON: `/home/eston/tri-piql/results/sota_candidate/iql_awbc_can404_preflight/diagnostics.json`.
