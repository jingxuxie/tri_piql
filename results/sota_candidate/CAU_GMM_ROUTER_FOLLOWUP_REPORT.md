# CAU/GMM Router Follow-up

This report follows the fresh split606 CAU failure with one deployable GMM-confidence router screen and fixed-CAU checks on unused validation splits.

## Decision

- Split606 labeled-positive q25 GMM calibration is neutral: `16/20` versus positive-only `16/20` and CAU `15/20`.
- A same-screen split606 GMM threshold can reach `18/20` with `0` losses, but this is post-hoc.
- That frozen threshold does not transfer to split707: the router reaches `15/20` and opens no CAU episodes, while CAU alone reaches `20/20`.
- CAU-alone split707 confirmation is strong: `50/50` versus positive-only `36/50` and weighted BC `39/50`.
- Split808 rejects a consistent fixed-CAU dominance claim: CAU epoch 200 reaches `38/50` versus positive-only `43/50`, weighted BC `25/50`, TRIAGE-BC v0.1 `16/50`, and the older Candidate E gate `42/50`.
- The GMM router is a no-go in this form, and CAU-alone remains a useful but inconsistent method seed rather than a promotable SOTA result.

## Rows

| artifact_id | split | screen | method_id | score | avg_len |
| --- | --- | --- | --- | --- | --- |
| can606_gmm_q25 | 606 | eval20 | gmm_confidence_router_q25 | 16/20 |  |
| can606_gmm_posthoc_best | 606 | eval20 | gmm_confidence_router_posthoc | 18/20 |  |
| can707_positive_eval20 | 707 | eval20 | positive_only_nn | 15/20 | 181.9 |
| can707_weighted_eval20 | 707 | eval20 | weighted_bc | 15/20 | 183.6 |
| can707_cau_eval20 | 707 | eval20 | cau_action_conflict | 20/20 | 104.1 |
| can707_gmm_router_eval20 | 707 | eval20 | gmm_confidence_router_thr15p545 | 15/20 | 181.9 |
| can707_positive_eval50 | 707 | eval50 | positive_only_nn | 36/50 | 188.7 |
| can707_weighted_eval50 | 707 | eval50 | weighted_bc | 39/50 | 174.2 |
| can707_cau_eval50 | 707 | eval50 | cau_action_conflict | 50/50 | 104.7 |
| can808_positive_eval50 | 808 | eval50 | positive_only_nn | 43/50 | 148.4 |
| can808_weighted_eval50 | 808 | eval50 | weighted_bc | 25/50 | 258.3 |
| can808_triage_eval50 | 808 | eval50 | triage_bc_v01 | 16/50 | 306.7 |
| can808_candidate_e_eval50 | 808 | eval50 | candidate_e_gate | 42/50 | 154.7 |
| can808_cau_e100_eval50 | 808 | eval50 | cau_action_conflict_model_epoch_100 | 25/50 | 256.7 |
| can808_cau_e200_eval50 | 808 | eval50 | cau_action_conflict_model_epoch_200 | 38/50 | 178.9 |

## References

- Split606 GMM report: `results/sota_candidate/CAN606_GMM_CONFIDENCE_CAU_ROUTER_REPORT.md`.
- Split707 CAU eval20: `results/sota_candidate/cau_action_conflict_can707_b005_m05_eval20/REPORT.md`.
- Split707 GMM router eval20: `results/sota_candidate/can707_gmm_confidence_cau_router_thr15p545_eval20/REPORT.md`.
- Split707 50-episode confirmation: `results/sota_candidate/can707_positive_weighted_cau_eval50/REPORT.md`.
- Split808 CAU 50-episode validation: `results/sota_candidate/cau_action_conflict_can808_b005_m05_eval50/REPORT.md`.
- Split808 baseline evaluations: `results/candidate_f_can_fresh_validation/per_seed/`.
- Summary CSV: `results/sota_candidate/cau_gmm_router_followup_summary.csv`.
