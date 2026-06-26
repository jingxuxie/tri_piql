# Candidate D Negative-Action Preflight

This preflight extends the Candidate C sequence mask with a counterfactual bad-action target.
Training labels use only labeled positive demos, labeled negative demos, classifier scores,
and support distances; hidden labels below are audit-only.

## Rule

- Demo classifier threshold: `0.2`.
- Transition safety margin threshold: `2.0`.
- BC loss weight is the Candidate C positive-anchor/safe-transition mask.
- For each selected timestep, `negative_action` is the action from the nearest labeled-negative state by low-dimensional observation distance.
- The trainer can add a hinge loss so the demo action is more likely than this nearest bad action.

## Mass

- Train demos: `130`.
- Full-weight anchor demos: `50`.
- Extra demos considered: `80`.
- Extra hidden-positive demos with selected transitions: `5`.
- Extra hidden-bad demos with selected transitions: `8`.
- Extra hidden-positive transition mass: `186`.
- Extra hidden-bad transition mass: `36`.
- Total selected / negative-loss mass: `5528`.
- Selected mass fraction from extra demos: `0.040`.
- Mean selected nearest-negative obs distance: `3.494`.

## Read

- This is a trainable Candidate D input, not a policy result.
- It tests whether bad demos are more useful as local action repulsion than as trajectory or timestep filtering alone.

## Outputs

- Weight HDF5: `results/candidate_breakthrough/candidate_d_negative_action_preflight/candidate_d_negative_action_weights.hdf5`.
- Per-demo summary CSV: `results/candidate_breakthrough/candidate_d_negative_action_preflight/candidate_d_negative_action_summary.csv`.
- Recipe JSON: `results/candidate_breakthrough/candidate_d_negative_action_preflight/candidate_d_negative_action_recipe.json`.
