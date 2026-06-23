# Robomimic Quality-Mask Split

HDF5 path: `data/robomimic/v1.5/transport/mh/low_dim_v15.hdf5`.
Environment: `TwoArmTransport`.

This split uses Robomimic relative-quality masks, not sparse reward success/failure.
It is useful as a cross-task score-calibration diagnostic, but should not be presented as a failure-demo benchmark.

## Masks

- Positive train mask: `better_train` with `45` demos.
- Negative train mask: `worse_train` with `45` demos.
- Positive valid mask: `better_valid` with `5` demos.
- Negative valid mask: `worse_valid` with `5` demos.

## Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `10`.
- Unlabeled demos: `70`.
- Hidden-positive unlabeled demos: `35`.
- Hidden-negative unlabeled demos: `35`.
- Validation positives: `5`.
- Validation negatives: `5`.

## Files

- `split_indices.json`: split file compatible with selector diagnostics.
