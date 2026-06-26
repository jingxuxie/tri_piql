# Candidate F Frozen Matrix

Candidate F uses the endpoint-free calibrated anchor rule from
`candidate_f_anchor_calibration_screen_REPORT.md`: if the positive-NN
selected support has a classifier-probability tail below
`0.5 * unlabeled_prob_mean`, use weighted BC as the split-level anchor;
otherwise use the isolated-RNG Candidate E initial-distance gate.

| split | source | positive | weighted | triage | best base | cand F | delta | gate opens | artifact |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | weighted_anchor | 19/50 | 37/50 | 28/50 | 37/50 | 37/50 | +0 |  | results/candidate_breakthrough/candidate_f_frozen_split101_weighted_sampler_anchor_eval50 |
| 202 | candidate_e_gate | 40/50 | 33/50 | 36/50 | 40/50 | 40/50 | +0 | 0 | results/candidate_breakthrough/candidate_f_frozen_split202_candidate_e_gate_eval50 |
| 303 | candidate_e_gate | 36/50 | 25/50 | 35/50 | 36/50 | 36/50 | +0 | 0 | results/candidate_breakthrough/candidate_f_frozen_split303_candidate_e_gate_eval50 |
| 404 | candidate_e_gate | 39/50 | 33/50 | 36/50 | 39/50 | 46/50 | +7 | 5 | results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng |
| 505 | candidate_e_gate | 40/50 | 30/50 | 36/50 | 40/50 | 39/50 | -1 | 15 | results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split505_eval50_isolated_rng |
| total |  | 174/250 | 158/250 | 171/250 | 192/250 | 198/250 | +6 | 20 |  |

## Read

- Frozen Candidate F reaches `198/250`, versus positive-only `174/250`,
  weighted `158/250`, triage `171/250`, and the per-split baseline
  oracle `192/250`.
- It improves over the best completed baseline on split 404 by `+7/50`,
  loses split 505 by `-1/50`, and ties the best baseline on splits
  101/202/303.
- The incorrect root `last.pth` split-101 diagnostic is intentionally
  excluded; the frozen split-101 row uses the weighted-sampler
  `model_epoch_200.pth` checkpoint that produced the paper baseline.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_f_frozen_matrix_summary.csv`.
