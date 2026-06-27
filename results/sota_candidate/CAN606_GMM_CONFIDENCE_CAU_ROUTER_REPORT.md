# Can606 GMM-Confidence CAU Router

This audit tests a deployable first-step policy-quality signal on the fresh Can split606 screen.
The router anchors to positive-only and switches to CAU when the positive policy's top-mode action has low learned GMM log-likelihood under the CAU policy.

## Decision

- Labeled-positive q25 calibration routes to `16/20` versus positive-only `16/20` and CAU alone `15/20`.
- The calibrated gate opens `4` episodes (demo_39;demo_53;demo_39;demo_53), with `0` gains and `0` losses.
- Best post-hoc threshold on this same screen reaches `18/20` with `2` gains and `0` losses.
- A post-hoc zero-loss gain threshold exists at `lt 15.545226`, reaching `18/20`. This is hypothesis-only.
- This feature should not be promoted as a Can CAU router unless it earns a fresh positive split.

## Calibrated Gate

| gate | routed | positive | CAU | gains | losses | opened | threshold |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| labeled-positive q25 | 16/20 | 16/20 | 15/20 | 0 | 0 | 4 | 15.074509 |

## References

- Live router eval: `results/sota_candidate/can606_gmm_confidence_cau_router_q25_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/can606_gmm_confidence_cau_router_summary.csv`.
- Per-episode CSV: `results/sota_candidate/can606_gmm_confidence_cau_router_per_episode.csv`.
