# SOTA Candidate 1 SM-RWBC Preflight

This preflight builds broad-pool per-timestep weights for Sequence-Masked Risk-Weighted BC.
It uses the weighted-BC train pool, keeps labeled positives at full weight, and downweights
unlabeled timesteps by classifier score and local bad-action risk.

## Selected Recipe

- `m_min`: `0.050`.
- `lambda_risk`: `2.000`.
- Risk feature: `combined`.
- Train demos: `130`.
- Hidden-positive / hidden-bad demos in broad pool: `40` / `80`.
- Hidden-bad unweighted transition fraction: `0.620`.
- Hidden-bad weighted mass fraction: `0.379`.
- Hidden-positive mass: `1967.0`.
- Hidden-bad mass: `1199.1`.
- Transition ESS: `7529.9`.

## Lowest Hidden-Bad Mass Grid Rows

| m_min | lambda | risk | hidden-positive mass | hidden-bad mass | bad mass frac | ESS |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 0.030000 | 4.000000 | bad_neighbor_state_action | 970.609591 | 380.820158 | 0.281791 | 4167.823221 |
| 0.050000 | 4.000000 | bad_neighbor_state_action | 970.609591 | 384.981580 | 0.283995 | 4181.726456 |
| 0.100000 | 4.000000 | bad_neighbor_state_action | 970.609591 | 398.452938 | 0.291041 | 4226.428238 |
| 0.030000 | 4.000000 | combined | 1327.237218 | 679.672222 | 0.338666 | 5706.149272 |
| 0.050000 | 4.000000 | combined | 1327.237218 | 687.392862 | 0.341201 | 5733.732587 |
| 0.100000 | 4.000000 | combined | 1327.237218 | 712.203770 | 0.349215 | 5820.928645 |
| 0.030000 | 2.000000 | bad_neighbor_state_action | 1642.071680 | 891.451884 | 0.351862 | 6561.917638 |
| 0.050000 | 2.000000 | bad_neighbor_state_action | 1642.071680 | 902.015636 | 0.354554 | 6598.838448 |

## Read

- This is not a policy result. It only checks whether the SOTA Candidate 1 recipe creates a trainable broad-coverage distribution with less hidden-bad transition mass than unweighted broad cloning.
- The next gate is a bounded Can404 train/eval with the existing transition-weighted trainer, because previous union-only and hard-mask variants did not beat positive-only.

## Outputs

- Selected weights HDF5: `results/sota_candidate/sm_rwbc_can404_preflight/sm_rwbc_loss_weights.hdf5`.
- Selected per-demo CSV: `results/sota_candidate/sm_rwbc_can404_preflight/sm_rwbc_selected_demo_summary.csv`.
- Grid CSV: `results/sota_candidate/sm_rwbc_can404_preflight/sm_rwbc_grid_summary.csv`.
- Recipe JSON: `results/sota_candidate/sm_rwbc_can404_preflight/sm_rwbc_recipe.json`.
