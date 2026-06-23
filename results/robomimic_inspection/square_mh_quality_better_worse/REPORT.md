# Robomimic Quality-Mask Split

HDF5 path: `data/robomimic/v1.5/square/mh/low_dim_v15.hdf5`.
Environment: `NutAssemblySquare`.

This split uses Robomimic relative-quality masks, not sparse reward success/failure.
It is useful as a cross-task score-calibration diagnostic, but should not be presented as a failure-demo benchmark.

## Masks

- Positive train mask: `better_train` with `90` demos.
- Negative train mask: `worse_train` with `90` demos.
- Positive valid mask: `better_valid` with `10` demos.
- Negative valid mask: `worse_valid` with `10` demos.

## Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `10`.
- Unlabeled demos: `160`.
- Hidden-positive unlabeled demos: `80`.
- Hidden-negative unlabeled demos: `80`.
- Validation positives: `10`.
- Validation negatives: `10`.

## Files

- `split_indices.json`: split file compatible with selector diagnostics.
