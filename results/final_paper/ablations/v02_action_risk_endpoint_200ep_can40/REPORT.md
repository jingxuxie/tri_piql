# v0.2 Action-Risk Can40 200-Epoch Endpoint Checks

This is a targeted endpoint gate for the strongest support-side action-risk
candidates on frozen Can 40p/80b development split seeds.

Protocol:

- Candidates: `bad_neighbor_safe_top40` and `positive_nn_risk_fusion_top40`
  on split 11; `positive_nn_risk_fusion_top40` follow-up on split 22.
- Policy: official Robomimic BC-RNN-GMM.
- Training: 200 epochs x 100 steps, policy seed 0.
- Evaluation: 50 valid-positive rollouts, horizon 400, rollout seed 0.

Support audit:

| candidate | selected unlabeled | hidden positive | hidden bad | support recall | bad admission | purity |
|---|---:|---:|---:|---:|---:|---:|
| `bad_neighbor_safe_top40` | 40 | 40 | 0 | 1.000 | 0.000 | 1.000 |
| `positive_nn_risk_fusion_top40` | 40 | 39 | 1 | 0.975 | 0.013 | 0.975 |
| existing `positive_nn_top40` | 40 | 36 | 4 | 0.900 | 0.050 | 0.900 |

Split-22 support audit:

| candidate | selected unlabeled | hidden positive | hidden bad | support recall | bad admission | purity |
|---|---:|---:|---:|---:|---:|---:|
| `positive_nn_risk_fusion_top40` | 40 | 40 | 0 | 1.000 | 0.000 | 1.000 |
| existing `positive_nn_top40` | 40 | 37 | 3 | 0.925 | 0.037 | 0.925 |

Endpoint comparison:

| split | method | checkpoint | success | eval episodes | note |
|---|---|---|---:|---:|---|
| 11 | existing `positive_nn_top40` | model_epoch_200 | 0.840 | 50 | strongest same-split baseline |
| 11 | `positive_nn_risk_fusion_top40` | model_epoch_200 | 0.820 | 50 | less distribution-shifting action-risk hybrid |
| 11 | existing TRIAGE-BC | model_epoch_200 | 0.760 | 50 | frozen split-11 baseline |
| 11 | `bad_neighbor_safe_top40` | model_epoch_200 | 0.720 | 50 | pure risk-support candidate |
| 11 | existing weighted BC | model_epoch_200 | 0.720 | 50 | frozen split-11 baseline |
| 22 | existing `positive_nn_top40` | model_epoch_200 | 0.760 | 50 | strongest same-split baseline |
| 22 | `positive_nn_risk_fusion_top40` | model_epoch_200 | 0.640 | 50 | perfect support audit, endpoint miss |
| 22 | existing TRIAGE-BC | model_epoch_200 | 0.520 | 50 | frozen split-22 baseline |
| 22 | existing weighted BC | model_epoch_200 | 0.440 | 50 | frozen split-22 baseline |

Two-split comparison:

| method | successes / rollouts | success |
|---|---:|---:|
| existing `positive_nn_top40` | 80 / 100 | 0.800 |
| `positive_nn_risk_fusion_top40` | 73 / 100 | 0.730 |
| existing TRIAGE-BC | 64 / 100 | 0.640 |
| existing weighted BC | 58 / 100 | 0.580 |

Decision:

- The pure action-risk candidate clears the split-11 support gate but does not
  beat the strongest same-split endpoint baseline.
- The less distribution-shifting risk hybrid is a near miss on split 11
  (`0.820` versus positive-NN `0.840`) but fails the split-22 confirmation
  (`0.640` versus positive-NN `0.760`).
- Do not promote either action-risk candidate as TRIAGE-BC v0.2.
- Do not spend split-33 endpoint compute on this unchanged candidate family
  unless a new policy-quality hypothesis is added. The two-split result is
  enough to reject the current action-risk support-purity story.
- Policy-coverage diagnostics in
  `results/final_paper/tables/v02_policy_coverage_diagnostic_REPORT.md` and
  `results/final_paper/tables/v02_policy_coverage_diagnostic_split22_REPORT.md`
  show that simple initial-state or transition nearest-neighbor coverage also
  does not rescue the proxy.

Outputs:

- `split11/endpoint_setup_summary.csv`
- `split11/bns40/setup/config.json`
- `split11/bns40/train/v02risk200_can40_s11_bns40_seed0_bc_rnn_e200/20260625052835/models/model_epoch_200.pth`
- `split11/bns40/eval/REPORT.md`
- `split11/bns40/eval/metrics.csv`
- `split11/pnrf40/setup/config.json`
- `split11/pnrf40/train/v02risk200_can40_s11_pnrf40_seed0_bc_rnn_e200/20260625054130/models/model_epoch_200.pth`
- `split11/pnrf40/eval/REPORT.md`
- `split11/pnrf40/eval/metrics.csv`
- `split22/endpoint_setup_summary.csv`
- `split22/pnrf40/setup/config.json`
- `split22/pnrf40/train/v02risk200_can40_s22_pnrf40_seed0_bc_rnn_e200/20260625060043/models/model_epoch_200.pth`
- `split22/pnrf40/eval/REPORT.md`
- `split22/pnrf40/eval/metrics.csv`
