# v0.2 Action-Risk Can40 Endpoint Smoke

This is a 50-epoch / 10-rollout smoke on frozen Can 40p/80b split seed 11.
It is a cheap endpoint sanity check, not a final policy claim.

All policies use official Robomimic BC-RNN-GMM with 100 gradient steps per
epoch and valid-positive initial states.

| candidate | support recall | bad admission | train demos | success | eval episodes |
|---|---:|---:|---:|---:|---:|
| `positive_nn_top40` | 0.900 | 0.050 | 50 | 0.400 | 10 |
| `bad_neighbor_safe_top40` | 1.000 | 0.000 | 50 | 0.100 | 10 |
| `positive_nn_risk_fusion_top40` | 0.975 | 0.013 | 50 | 0.200 | 10 |

Interpretation:

- The short 5k-step smoke does not favor the new action-risk candidates.
- The smoke is undertrained relative to the final 20k-step protocol; the same
  positive-NN baseline reaches 0.840 under the existing 200-epoch / 50-rollout
  split-11 final run.
- Use this only as a triage result. The proper gate is the 200-epoch endpoint
  check in `results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40`.

Outputs:

- `split11/bns40/eval_smoke/REPORT.md`
- `split11/pnn40/eval_smoke/REPORT.md`
- `split11/pnrf40/eval_smoke/REPORT.md`
