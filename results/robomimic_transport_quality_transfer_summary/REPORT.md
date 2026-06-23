# Robomimic Transport Quality Transfer

This is a support-side transfer diagnostic on a new Robomimic task family, TwoArmTransport.
Transport MH contains relative-quality masks (`better`, `okay`, `worse`) but no reward-failure demonstrations, so it is not a bad-demo benchmark.

## Dataset

- HDF5: `data/robomimic/v1.5/transport/mh/low_dim_v15.hdf5`.
- Environment: `TwoArmTransport`.
- Demos: `300`.
- Reward-positive demos: `300`.
- Reward-negative demos: `0`.
- Return p10 / p50 / p90: `5.000` / `5.000` / `6.000`.

## Quality Split

- Positive labels: scarce `better_train` demos.
- Negative labels: scarce `worse_train` demos.
- Unlabeled mix: remaining `better_train` and `worse_train` demos; `okay` demos are excluded from this audit to keep hidden labels well-defined.
- Labeled positives / negatives: `10` / `10`.
- Hidden-positive / hidden-negative unlabeled: `35` / `35`.
- Validation positives / negatives: `5` / `5`.

## Score Calibration

- Labeled-positive mean score: `0.988`.
- Labeled-positive p10 score: `0.979`.
- Labeled-negative mean score: `0.014`.
- Labeled-negative max score: `0.041`.

## Selection Rules

| rule | selected | hidden positive | hidden bad | purity |
|---|---:|---:|---:|---:|
| top_posx2 | 20.0 | 20.0 | 0.0 | 1.000 |
| top_posx3 | 30.0 | 30.0 | 0.0 | 1.000 |
| top_posx4 | 40.0 | 35.0 | 5.0 | 0.875 |
| pos_p10 | 16.3 | 16.3 | 0.0 | 1.000 |
| pos_min | 19.3 | 19.3 | 0.0 | 1.000 |
| adaptive_masscap | 36.0 | 35.0 | 1.0 | 0.972 |
| mid_mean | 38.7 | 35.0 | 3.7 | 0.905 |
| neg_max | 59.7 | 35.0 | 24.7 | 0.587 |

## Interpretation

- Scarce relative-quality labels transfer cleanly to Transport MH and produce a strong state-action score.
- The score almost perfectly recovers the hidden `better` unlabeled support: adaptive masscap selects all 35 hidden-better unlabeled demos while admitting only 1 hidden-worse demo on average.
- This strengthens the cross-task score-calibration mechanism across another manipulation task family.
- It should remain support-side evidence. Since all recorded Transport MH demos are reward-positive, this does not validate failure-demo avoidance or policy success under bad demonstrations.

## Artifacts

- Reward-success inspection: `results/robomimic_inspection/transport_mh_low_dim/REPORT.md`
- Quality split: `results/robomimic_inspection/transport_mh_quality_better_worse/REPORT.md`
- Selector analysis: `results/robomimic_selector_score_analysis_transport_mh_quality_better_worse/REPORT.md`
- Selection CSV: `selection_summary.csv`
- Score summary: `score_summary.json`
