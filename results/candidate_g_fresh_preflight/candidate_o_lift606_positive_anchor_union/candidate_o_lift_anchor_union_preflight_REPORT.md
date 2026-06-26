# Candidate O Lift606 Positive-Anchor Union Preflight

Candidate O is a policy-training change for the Lift branch: keep the
positive-only selected support at full loss weight and add triage-only
extra demos at loss weight `0.25`.

## Support

- Labeled positives: `10`.
- Positive-NN selected unlabeled demos: `160`.
- Triage selected unlabeled demos: `176`.
- Overlap selected demos: `103`.
- Positive-only extra demos: `57`.
- Triage-only extra demos: `73`.
- Candidate O train demos: `243`.

## Artifacts

- Config: `results/candidate_g_fresh_preflight/candidate_o_lift606_positive_anchor_union/config.json`.
- Loss weights: `results/candidate_g_fresh_preflight/candidate_o_lift606_positive_anchor_union/candidate_o_loss_weights.hdf5`.
- Diagnostics: `results/candidate_g_fresh_preflight/candidate_o_lift606_positive_anchor_union/diagnostics.json`.
- HDF5 train mask: `candidate_o_lift606_positive_anchor_union_train`.
- HDF5 valid-positive mask: `candidate_o_lift606_positive_anchor_union_valid_positive`.
