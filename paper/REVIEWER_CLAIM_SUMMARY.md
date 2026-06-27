# Reviewer-Facing Claim Summary

This is the compact claim contract for the current TRIAGE-BC paper package. It is meant to help a reviewer separate the main empirical claim from diagnostics, negative results, and future work.

## Central Claim

Offline imitation with scarce trusted successes, scarce known failures, and a large mixed log is a score-to-support conversion problem. Failure demonstrations can help when they improve the precision/coverage frontier of the policy-training support, but they are not automatically better than positive-only retrieval or broad weighted coverage.

The current paper should be read as a precision/coverage study with a frozen portfolio-router method component. It is not a validated inverse-Q robotics method and it is not a universal dominance claim.

## Evidence Map

| Evidence block | What it supports | Key numbers | Boundary |
|---|---|---|---|
| Controlled PointNav | Scarce bad labels can calibrate hidden-good support when positives are incomplete prefixes. | With `n_+=n_-=2`, score-gap support reaches `1.000` success at all reported bad fractions. | Mechanism evidence, not robotics endpoint evidence. |
| Primary Robomimic Can/Lift matrix | Default benchmark rows show a precision/coverage tradeoff, not one universal winner. | Can 40p/80b: TRIAGE-BC `99/150`, weighted BC `90/150`, positive-only NN `108/150`. Lift MG: weighted BC `93/150`, TRIAGE-BC `74/150`, positive-only NN `82/150`. | Positive-only NN is the strongest non-oracle Can row; Weighted BC is strongest on Lift MG. |
| Generated Can regime probes | Bad-aware support helps in targeted action-conflict, coverage-shift, and prefix-positive regimes. | Hard-negative `104/150` vs `91/150`; coverage-shift `120/150` vs `103/150`; prefix-positive `119/150` vs `6/150`. | Generated split constructions, not default benchmark rows. |
| v0.2 fresh Can+Lift gate | A frozen hidden-label-free portfolio router is plausible but barely positive overall. | Selected branches `340/500` vs `338/500` best per-split baselines; Can `197/250` vs `192/250`; Lift `143/250` vs `146/250`. | Paired-bootstrap intervals cross zero; this is not a formal significance claim, rollout starts are not fully independent, and optional fresh all-demo/all-positive diagnostic categories are represented but remain partial-by-split controls (`4/4` categories, not a full five-split diagnostic leaderboard). |
| Router regret | Portfolio framing is more defensible than a single hard-support story. | v0.2 regret is `23/500` versus `64/500` for always positive-only NN and `62/500` for always weighted BC on completed Can+Lift rows. | Current table is a cautious completed-row regret audit, not a complete SOTA leaderboard. |
| Abstention and proxy no-go | Policy-quality prediction remains open; abstention is a risk-control branch. | Can MG original proxies match best success in `0/6` cases; assigned router rows average `0.700`, while abstained rows top out at `0.333`. | Can MG is a stress diagnostic, not a main success row. |
| Non-Can Lift hard-negative probe | Bad-aware support transfers at the support-audit level, but endpoint evidence is weak. | Support audit: `82/120` hidden positives and `38/240` hidden bad versus `12/120` and `108/240`; split-101/202/303 endpoint `15/150` vs `5/150`, selecting 82 hidden positives and 38 hidden bad versus 12 hidden positives and 108 hidden bad. | Completed exploratory C1 evidence only; absolute success is too low for a primary non-Can endpoint claim. |
| Candidate-breakthrough search | The recent method-development search does not justify a stronger dominance claim. | Candidate F discovery reaches `198/250` on Can but fails fresh validation at `81/100` versus `84/100`; transition-level objectives top out at `16/20` and nearest-negative hinge at `14/20` versus positive-only `17/20`; Candidate W reaches `85/100`, tying Candidate E while split 505 is `39/50` versus positive-only `40/50`. | Failed-development evidence only. Do not promote Candidate F, output anchoring, scalar rescue gates, or nearest-negative hinge variants as paper-facing methods. |
| Focused SOTA-candidate sweep | The follow-on six-family search improves the CAU story but still does not justify methods/SOTA dominance. | `results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md`: SM-RWBC, SafeExpand, Demo-DPO, and IQL-AWBC fail Can404; best Can404 short-screen candidates reach `16/20` versus positive-only `17/20`, CCG transfer reaches `10/20` versus `12/20`, and anchored IQL-AWBC reaches `13/20`. The Can404 anchor-overlap audit shows CAU gains 2 starts but loses 3 positive-only starts, and Demo-DPO gains 1 but loses 2. A post-hoc CAU-plus-positive feature gate reaches `18/20` on the same screen. With that threshold frozen, split 505 reaches `16/20` routed versus positive-only `15/20` and `41/50` routed versus positive-only `40/50`; split 303 is neutral for the deployable fallback. A two-feature CAU gate reaches `24/50` routed versus `19/50` positive-only on split101 and is neutral on split202 despite CAU alone reaching `42/50`. CAU-alone reaches `193/250` over five Can splits, beating positive-only `174/250`, weighted BC `158/250`, TRIAGE-BC v0.1 `171/250`, and best old baseline per split `192/250`, but trailing v0.2 selected union `197/250`. Fresh split606 rejects the post-hoc CAU-plus-v0.2 setup gate: CAU reaches `15/20` versus positive-only `16/20`, and proper expanded-mask CAU reaches `12/20`. The GMM-router follow-up also fails as a selector; CAU-alone is strong on split707 (`50/50` versus positive-only `36/50` and weighted BC `39/50`) but loses split808 to positive-only (`38/50` versus `43/50`). `results/sota_candidate/CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md` shows oracle-switch headroom (`331/370`) but no deployable support-distance selector: safe LOO selection reaches `263/370` versus positive-only `269/370`, while best-delta selection reaches `277/370` with `23` losses. | Claim-boundary evidence only. CAU action-conflict is useful but inconsistent, and the hidden-label-free router needed to select it while preserving anchors is still unresolved. |

## Claims To Make

- The central bottleneck is score-to-support conversion under a precision/coverage tradeoff.
- Bad labels help in identifiable regimes where they add information beyond scarce positives.
- Strong positive-only retrieval and broad weighted coverage are first-class baselines.
- TRIAGE-BC v0.2 is best framed as a frozen portfolio router with barely positive fresh-split evidence, explicit abstention, and no claim to a complete fresh SOTA leaderboard.

## Claims To Avoid

- Do not claim bad labels are required.
- Do not claim TRIAGE-BC uniformly beats weighted BC.
- Do not claim TRIAGE-BC uniformly beats positive-only retrieval.
- Do not claim support purity alone predicts endpoint policy quality.
- Do not claim the full inverse-Q / Tri-PIQL actor-extraction objective is validated on Robomimic.
- Do not claim best-checkpoint selection proves the method.

## Reviewer Objections And Direct Answers

| Objection | Direct answer |
|---|---|
| "Is this just a router over baselines?" | The paper should embrace the portfolio framing. The contribution is identifying when hard support, soft weighting, positive-only retrieval, and abstention are appropriate under scarce labels and mixed logs. |
| "Why not just positive-only NN?" | Positive-only NN is the strongest Can 40p/80b baseline, but generated hard-negative, coverage-shift, and prefix-positive probes show regimes where failure labels add information beyond positive-only retrieval. |
| "Why not just weighted BC?" | Weighted BC is strongest on Lift MG and useful when broad weighted coverage dominates, but it trails hard support in the Can 40p/80b primary row and in generated action-conflict regimes. |
| "Why not promote Candidate F or the later rescue variants?" | The scoped Can discovery did not survive the predeclared fresh gate, and later output-anchor, two-feature rescue, and transition-objective variants either tied or trailed positive-only on the first validation checks. These stay in the development audit, not the paper's method claim. |
| "Did the later SOTA-candidate sweep find a stronger method?" | Not enough for the paper method. Over five 50-episode Can splits CAU reaches `193/250`, beating positive-only, weighted BC, v0.1 TRIAGE-BC, and the best old baseline per split by `1/250`. A post-hoc CAU-plus-v0.2 portfolio reaches `208/250`, but fresh split606 is negative: gate-selected CAU is `15/20` versus positive-only `16/20`, and proper expanded-mask CAU is `12/20`. Fresh split707 is strongly positive for CAU-alone (`50/50` versus positive-only `36/50` and weighted `39/50`), but the GMM router selected from split606 does not transfer, and fixed CAU loses split808 to positive-only (`38/50` versus `43/50`). A LOO selector-feature audit confirms that simple initial-distance routing is not enough: safe selection is `263/370` versus positive-only `269/370`, while the more aggressive selector has `23` losses. This remains development evidence until a robust selector or broader fresh confirmation is available. |
| "Are the generated probes cherry-picked?" | They are presented as generated regime probes with explicit construction rules and allowed claims in `../REGIME_PROBE_SUITE.md`, not as default Robomimic benchmark rows. |
| "Is the v0.2 result statistically decisive?" | No. The correct claim is barely positive branch-selection evidence with split-level counts and paired-bootstrap context, not significance. |
| "Are fresh all-demo and all-positive oracle rows complete?" | No, not as full five-split rows. The fresh v0.2 gate is a selected-vs-strong-baseline/v0.1 audit; optional fresh all-demo/all-positive diagnostic categories are represented (`4/4` with at least one split each) but should not be implied as completed leaderboard evidence. |

## Paper Positioning

Submit this as a careful empirical study with a method component:

> Failure labels are valuable when they improve policy-training support under a precision/coverage tradeoff, but they should be evaluated against strong positive-only retrieval, soft weighted coverage, and abstention rather than treated as a one-size-fits-all advantage.
