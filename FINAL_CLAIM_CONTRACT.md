# Final Claim Contract

This file is the paper-facing contract for the current TRIAGE-BC evidence package. It freezes what the manuscript may claim, what it must not claim, and which artifacts support the final story. It is deliberately narrower than a methods-dominance claim.

## Paper Position

TRIAGE-BC should be presented as a precision/coverage study with a frozen portfolio-router method component.

Central claim:

> Offline imitation from scarce trusted successes, scarce known failures, and a mixed unlabeled log is a score-to-support conversion problem. Failure demonstrations can help when they improve the precision/coverage frontier of policy-training support, but strong positive-only retrieval, broad weighted coverage, and abstention remain first-class alternatives.

This is not a validated inverse-Q robotics method. The robotics evidence validates score-calibrated support conversion with official Robomimic BC-RNN-GMM policies, not the full inverse-Q / Tri-PIQL actor-extraction objective.

## Main Claims Allowed

| Claim | Allowed strength | Evidence |
|---|---|---|
| Mixed logs can hurt naive cloning. | Main paper. | PointNav mixed-log degradation; Lift MG all-demo `31/150`; Can 40p/80b all-demo `81/150`. |
| Scarce bad labels can help recover hidden-good support when positives are incomplete. | Main mechanism claim. | PointNav score-gap support reaches `1.000` success with `n_+=n_-=2`; generated Can prefix-positive reaches `119/150` versus `6/150`. |
| Hard support can beat weighted sampling in action-conflict regimes. | Narrow main/diagnostic claim. | Can 40p/80b TRIAGE-BC `99/150` versus weighted BC `90/150`; hard-negative Can `104/150` versus `91/150`. |
| Broad weighted coverage can win when coverage dominates. | Main caveat and mechanism claim. | Lift MG weighted BC is strongest at `93/150`; Can MG stress rows favor weighted BC at `0.333`. |
| Generated Can regime probes identify where failures help. | Main diagnostic claim, not default benchmark claim. | `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`: hard-negative `104/150` versus `91/150`, coverage-shift `120/150` versus `103/150`, prefix-positive `119/150` versus `6/150`. |
| v0.2 portfolio routing is plausible but fragile. | Very cautious method evidence. | Fresh Can+Lift selected branches are barely positive at `340/500` versus `338/500`; router regret `23/500` versus `64/500` for always positive-only NN and `62/500` for always weighted BC. |
| Policy-quality prediction remains open. | Main limitation. | Proxy no-go table, action-risk endpoint no-go, and Can MG abstention diagnostics. |

## Mandatory Caveats

- Positive-only NN is the strongest non-oracle frozen Can 40p/80b row: `108/150` versus TRIAGE-BC `99/150` and weighted BC `90/150`.
- Weighted BC is strongest on frozen Lift MG: `93/150` versus positive-only NN `82/150` and TRIAGE-BC `74/150`.
- The v0.2 fresh gate is not a formal significance claim. Paired-bootstrap intervals cross zero for Can, Lift, and combined.
- The v0.2 fresh gate is a selected-vs-strong-baseline/v0.1 audit; optional fresh all-demo/all-positive diagnostic rows remain unrun and must not be implied as completed fresh leaderboard evidence.
- Endpoint rollouts are not fully independent because they reuse validation-positive start pools within split seeds.
- The correct framing is a score-to-support conversion problem, not a universal algorithmic superiority claim.
- The Lift and Can MG evidence shows broad weighted coverage can beat purer hard support.
- The generated Lift hard-negative endpoint gate is exploratory only: completed splits `101/202/303` are `15/150` versus `5/150`, with selected support of 82 hidden positives and 38 hidden bad demos versus 12 hidden positives and 108 hidden bad demos. Absolute success remains low, so this is non-Can mechanism evidence rather than a primary endpoint claim.

## Claims Forbidden

- Do not claim bad labels are required.
- Do not claim TRIAGE-BC uniformly beats weighted BC.
- Do not claim TRIAGE-BC uniformly beats positive-only retrieval.
- Do not claim hard support always wins.
- Do not claim weighted BC is weak.
- Do not claim support purity alone predicts endpoint policy quality.
- Do not claim best checkpoint proves the method.
- Do not claim the full inverse-Q / Tri-PIQL actor-extraction method is validated on Robomimic.

## Main Evidence Artifacts

- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/REVIEWER_CLAIM_SUMMARY.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/REPRODUCE_PAPER.md`
- `REGIME_PROBE_SUITE.md`
- `METHOD_FREEZE.md`
- `METHOD_FREEZE_V02.md`
- `results/PAPER_CLAIM_PACKAGE.md`
- `results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`
- `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`
- `results/final_paper_v02/tables/v02_router_regret_REPORT.md`
- `results/final_paper/tables/active_abstention_evaluation_REPORT.md`
- `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`
- `results/final_paper/tables/submission_readiness_audit_REPORT.md`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`

## Readiness Status

The package is ready for a careful high-quality empirical submission if the paper remains framed as a precision/coverage study with cautious v0.2 portfolio-router evidence. It is not ready for a top-tier methods/SOTA-style dominance claim unless future evidence establishes stronger fixed-branch wins, a second non-Can endpoint bad-label benefit, or a validated hidden-label-free policy-quality proxy.

The validation gate is:

```bash
make -C paper validate
```
