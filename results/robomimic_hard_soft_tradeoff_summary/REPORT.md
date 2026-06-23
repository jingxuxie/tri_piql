# Robomimic Hard-vs-Soft Score Conversion Diagnostic

This support-only diagnostic consolidates the existing selector-score analyses. It does not use new policy training.

The purpose is to turn the weighted-BC baseline result into a method question: when should the classifier score become hard selected support, and when should it remain a soft sampling weight?

## Files

- `diagnostic_summary.csv`: one row per split with support-frontier features and a candidate hard/soft recommendation.
- `rule_summary.csv`: aggregate composition for existing threshold and adaptive rules.
- `policy_anchor_summary.csv`: fixed-20k policy anchors from the current reports.

## Candidate Rule

- Count the mean number of unlabeled demos with trajectory score at least `0.95`.
- Find the largest top-k prefix with mean hidden-positive purity at least `0.70` in the support diagnostic.
- If the high-score plateau is at least `400` demos but the largest clean prefix is less than half of that plateau, mark the split as a soft-weighting candidate.
- Otherwise, if a clean prefix exists, mark the split as a hard-support candidate.

The support purity part uses hidden labels for diagnosis only. A final algorithm should replace it with a hidden-label-free proxy such as score-plateau length, score curvature, validation likelihood on labeled positives, or a predeclared purity model.

## Summary

| analysis | observed policy mode | support candidate | score>=0.95 demos | best clean k | top20 purity | top80 purity | note |
|---|---|---|---:|---:|---:|---:|---|
| can_paired_80p80b | hard_coverage | hard_support_candidate | 0.0 | 80 | 1.000 | 0.900 | coverage-aware score-gap is the best fixed-20k policy row |
| can_paired_40p80b | hard_mass_capped | hard_support_candidate | 0.0 | 50 | 0.983 | 0.500 | mass-capped support is best at fixed 15k/20k |
| can_paired_20p80b | hard_precision | hard_support_candidate | 0.0 | 20 | 0.750 | 0.250 | top20 precision branch is best at fixed 20k |
| lift_mg_sparse | hard_threshold | hard_support_candidate | 85.3 | 320 | 0.983 | 0.967 | pos-min hard support is best at fixed 20k |
| can_mg_sparse | soft_weighting | soft_weighting_candidate | 652.3 | 160 | 0.750 | 0.792 | weighted sampler is the best matched three-seed fixed-20k control but remains diagnostic |

## Interpretation

- Paired Can and Lift have clean enough high-score prefixes to support hard selected training data.
- Can MG has a much larger high-score plateau and purity decays only as support gets broad; the matched three-seed controls make soft weighting the best fixed-20k row, but the absolute success remains modest.
- A hidden-label-free router candidate that removes the diagnostic purity term is summarized in `results/robomimic_hidden_free_router_summary/REPORT.md`.
- This reframes weighted BC as a branch of the method family rather than a weak baseline. The next method step is to freeze and validate the hidden-label-free hard/soft router.
