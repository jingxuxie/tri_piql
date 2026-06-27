# Candidate C Sequence-Mask Preflight

This preflight keeps the positive-only NN train pool at full weight and adds only
locally safe transitions from the broader weighted-BC pool.

## Rule

- Demo classifier threshold: `0.2`.
- Transition safety margin threshold: `2.0`.
- Margin is nearest labeled-negative state-action distance minus nearest labeled-positive state-action distance.

## Mass

- Anchor demos: `50`.
- Extra demos considered: `80`.
- Extra hidden-positive demos with selected transitions: `1`.
- Extra hidden-bad demos with selected transitions: `10`.
- Extra hidden-positive transition mass: `60`.
- Extra hidden-bad transition mass: `55`.
- Extra hidden-bad masked fraction: `0.478`.
- Total masked mass fraction from extra demos: `0.021`.

## Read

- The broad pool is highly contaminated outside the positive-only anchor, so this mask is deliberately conservative.
- This is a trainable Candidate C input, but the preflight does not by itself prove policy improvement.

## Outputs

- Mask HDF5: `results/sota_candidate/candidate_c_split909_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.
- Per-demo summary CSV: `results/sota_candidate/candidate_c_split909_sequence_mask_preflight/candidate_c_sequence_mask_summary.csv`.
- Recipe JSON: `results/sota_candidate/candidate_c_split909_sequence_mask_preflight/candidate_c_sequence_mask_recipe.json`.
