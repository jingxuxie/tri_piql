# TRI-Signal Regime Probe Suite

Status: paper-facing registry frozen on 2026-06-25.

This file turns the generated diagnostics into a coherent empirical suite. It is
not a claim that every completed diagnostic was pre-registered before initial
exploration. Completed rows are marked as completed evidence. Future variants
must be added here before endpoint training if they are to support new main
claims.

## Suite Contract

The suite tests when scarce explicit failures add information beyond strong
positive-only retrieval and when they do not. Each probe must state the split
construction, expected winner, compared methods, split seeds, endpoint budget,
and allowed claim before interpreting endpoint results.

Rules:

- Hidden labels may be used to construct generated split families and to audit
  selected support. They may not be used for score training, branch selection,
  checkpoint selection, or policy training.
- Completed endpoint rows use official Robomimic BC-RNN-GMM, epoch 200, and 50
  valid-positive-start rollouts per split unless explicitly marked otherwise.
- Generated probes are mechanism evidence. They do not replace default
  Robomimic benchmark rows.
- A probe supports a bad-label benefit only if the bad-aware candidate improves
  endpoint success over the matched positive-only candidate and the support
  audit shows the intended mechanism.
- A negative-control probe is successful if it shows bad-aware hard support is
  not universally necessary or not universally better.

## Probe Summary

| Probe | Status | Split Seeds | Expected Winner | Completed Read | Allowed Claim |
|---|---|---:|---|---|---|
| Prefix-positive Can | completed endpoint | 101/202/303 | bad-aware prefix support | bad-aware `119/150`, positive-only `6/150` | Explicit failures help when trusted positives are only successful-demo prefixes. |
| Hard-negative Can | completed endpoint | 101/202/303 | bad-aware hard support | bad-aware `104/150`, positive-only `91/150` | Explicit failures help when bad demos are action-conflicting near-positive neighbors. |
| Coverage-shift Can | completed endpoint | 101/202/303 | bad-aware hard support | bad-aware `120/150`, positive-only `103/150` | Explicit failures help when scarce positives under-cover successful state support. |
| Default Can 40p/80b | completed benchmark gate | 101/202/303/404/505 | no universal bad-label winner | v0.2 hard union `197/250`, best baselines `192/250`; original positive-only `108/150` beats v0.1 `99/150` | Bad-aware support can help as a portfolio branch, but strong positive-only retrieval remains first-class. |
| Lift MG broad coverage | completed benchmark gate | 101/202/303/404/505 | weighted coverage / no hard-support dominance | v0.2 weighted `143/250`, best baselines `146/250`; v0.1 hard support `143/250` | Broad coverage can beat or tie purer hard support; support purity is insufficient. |
| Can MG score plateau | completed abstention diagnostic | original + shuffle42 checks | abstention | weighted reaches `0.333` on original Can MG, while likelihood proxies select weaker hard-support policies | Abstention is justified when score shapes are ambiguous and hidden-label-free proxies do not predict rollout quality. |
| Lift hard-negative/action-conflict | completed exploratory endpoint | 101/202/303 | bad-aware hard support | support clears: bad-aware `82/120` positives and `38/240` bad versus positive-only `12/120` and `108/240`; three-split endpoint aggregate is `15/150` versus `5/150` | Directional but low-success. This is completed non-Can mechanism evidence, not a primary benchmark endpoint claim. |

## Probe Definitions

### 1. Prefix-Positive Can

Motivation: Mirror the controlled PointNav prefix-positive mechanism in
Robomimic. Trusted positives are incomplete prefixes of successful
demonstrations, so positive-only retrieval can match partial behavior while
missing full successful support.

Split construction:

- Use Can low-dimensional demonstrations.
- Labeled positives are early prefixes from successful demos.
- Labeled negatives are explicit failed demos.
- The unlabeled pool contains full successful and failed demonstrations.
- Hidden labels are used only to construct the diagnostic and audit selected
  support.

Compared methods:

- `prefix_bad_aware_state_top80`
- `prefix_state_action_nn_top80`

Endpoint budget:

- split seeds `101`, `202`, `303`
- official BC-RNN-GMM, 200 epochs, 100 epoch steps
- 50 valid-positive-start rollouts per split
- Can horizon `400`

Expected winner:

`prefix_bad_aware_state_top80`, because negative labels identify failed full
trajectories while prefix positives alone do not cover successful continuations.

Completed evidence:

- Support: bad-aware selects `195` hidden positives and `45` hidden bad demos;
  positive-only selects `37` hidden positives and `203` hidden bad demos.
- Endpoint: bad-aware `119/150`; positive-only `6/150`.
- Report: `results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`.

Allowed claim:

Explicit failures can be highly valuable when trusted positives are only
prefixes. This is a generated diagnostic claim, not a default Can benchmark
claim.

### 2. Hard-Negative Can

Motivation: Test the regime where bad demos are near positives in state space
but differ in action. Positive-only nearest-neighbor support should admit
action-conflicting bad demos; bad-aware action risk should reject them.

Split construction:

- Generate compact-positive Can splits.
- Place hidden positives far from the labeled-positive cluster.
- Rank bad demos by near-positive state distance plus action conflict.
- Hidden labels are audit-only after split generation.

Compared methods:

- `hybrid_rank_fusion_badaware_heavy_top40`
- `state_action_positive_nn_top40`

Endpoint budget:

- split seeds `101`, `202`, `303`
- official BC-RNN-GMM, 200 epochs, 100 epoch steps
- 50 valid-positive-start rollouts per split
- Can horizon `400`

Expected winner:

`hybrid_rank_fusion_badaware_heavy_top40`, because it preserves near-positive
coverage while suppressing action-conflicting bad demos.

Completed evidence:

- Support: hybrid selects `113` hidden positives and `7` hidden bad demos;
  positive-only selects `70` hidden positives and `50` hidden bad demos.
- Endpoint: hybrid `104/150`; positive-only `91/150`.
- Reports:
  `results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md`
  and `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`.

Allowed claim:

Explicit failures help when bad demonstrations are action-conflicting
near-neighbors. Keep this as targeted generated diagnostic evidence.

### 3. Coverage-Shift Can

Motivation: Test scarce-positive state-coverage shift. Labeled positives come
from one compact initial-object-pose cluster, while hidden successes and bad
demos span broader clusters.

Split construction:

- Generate Can splits by initial-object-pose clusters.
- Label successes from one compact cluster.
- Hide successes from other clusters.
- Spread bad demos across all clusters.
- Hidden labels are audit-only after split generation.

Compared methods:

- `hybrid_rank_fusion_badaware_heavy_top40`
- `state_action_positive_nn_top40`

Endpoint budget:

- split seeds `101`, `202`, `303`
- official BC-RNN-GMM, 200 epochs, 100 epoch steps
- 50 valid-positive-start rollouts per split
- Can horizon `400`

Expected winner:

`hybrid_rank_fusion_badaware_heavy_top40`, because negative labels reduce bad
admission while retaining hidden-positive coverage outside the labeled-positive
cluster.

Completed evidence:

- Support: hybrid selects `118` hidden positives and `2` hidden bad demos;
  positive-only selects `105` hidden positives and `15` hidden bad demos.
- Endpoint: hybrid `120/150`; positive-only `103/150`.
- Reports:
  `results/final_paper/ablations/can_coverage_shift_REPORT.md` and
  `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`.

Allowed claim:

Explicit failures help under scarce-positive coverage shift. Keep this as
targeted generated diagnostic evidence.

### 4. Default Can 40p/80b

Motivation: Negative-control/default-contamination regime. This tests whether
bad-aware support is necessary on standard paired Can contamination, where
positive-only retrieval is already strong.

Split construction:

- Paired Can 40 labeled positives / 80 labeled bad demos.
- Mixed unlabeled pool contains hidden successes and hidden failures.
- Fresh v0.2 gate uses split seeds `101`, `202`, `303`, `404`, and `505`.

Compared methods:

- v0.2 `positive_nn_risk_union_top40`
- `positive_only_nn`
- `weighted_bc`
- v0.1 rows when run
- audit-only oracle branch selector

Endpoint budget:

- official BC-RNN-GMM, 200 epochs, 100 epoch steps
- 50 valid-positive-start rollouts per split
- Can horizon `400`

Expected winner:

No universal bad-label winner. The portfolio branch may help by complementing
positive-only support, but positive-only retrieval should remain a strong
baseline and may win individual splits.

Completed evidence:

- Fresh v0.2 Can: selected hard union `197/250`; best completed baselines
  `192/250`; split signs `+++-+`.
- Original frozen v0.1 Can 40p/80b: positive-only NN `108/150`, TRIAGE-BC
  `99/150`, weighted BC `90/150`, all-demo BC `81/150`.
- Reports:
  `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md` and
  `results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`.

Allowed claim:

Bad-aware support can be useful as a portfolio branch, but default Can does not
show that bad labels are necessary or that TRIAGE uniformly beats positive-only
retrieval.

### 5. Lift MG Broad-Coverage Regime

Motivation: Negative-control/broad-coverage regime. This tests whether purer
hard support is enough when a sequence policy needs broad mixed-log coverage.

Split construction:

- Robomimic Lift MG sparse low-dimensional splits.
- Fresh v0.2 gate uses split seeds `101`, `202`, `303`, `404`, and `505`.
- v0.2 router selects soft weighted BC from score-shape mass/count features.

Compared methods:

- v0.2 `weighted_bc`
- v0.1 `triage_bc` hard support
- `positive_only_nn`
- audit-only oracle branch selector

Endpoint budget:

- official BC-RNN-GMM, 200 epochs, 100 epoch steps
- 50 valid-positive-start rollouts per split
- Lift horizon `150`

Expected winner:

Weighted coverage or no clear hard-support winner. This probe should reveal
whether high-purity hard support loses necessary coverage.

Completed evidence:

- v0.2 weighted `143/250`.
- v0.1 hard support `143/250`.
- positive-only NN `125/250`.
- best completed per-split baseline `146/250`; oracle branch selector
  `154/250`.
- Report: `results/final_paper_v02/tables/v02_fresh_lift_endpoint_REPORT.md`.

Allowed claim:

Support purity alone is insufficient. Broad weighted coverage can tie or beat
hard support, and the portfolio claim on Lift is a cautious coverage-selection
claim rather than a bad-label win.

### 6. Can MG Ambiguous Score Plateau

Motivation: Stress-test abstention. Some score shapes contain a large high-score
plateau where hard support and simple likelihood proxies are unreliable.

Split construction:

- Robomimic Can MG sparse diagnostics.
- Original and shuffled score/router checks.
- Hidden labels are audit-only.

Compared methods/proxies:

- `weighted`
- `allpositive`
- `alltrain`
- `posp10`
- hard/soft shuffled branches
- likelihood proxies: positive likelihood, positive-minus-negative gap, and
  negative rejection on labeled/valid masks

Endpoint budget:

- Reuses existing final-20k official BC-RNN-GMM checkpoints.
- No new endpoint training in the branch-proxy summary.

Expected winner:

Abstention. A hidden-label-free router should not force a main claim until a
proxy predicts rollout-quality coverage rather than just positive imitation or
negative rejection.

Completed evidence:

- Original Can MG rollout-best method is `weighted` at `0.333`.
- Likelihood proxies choose `allpositive`, which reaches only `0.200`.
- Shuffled Can MG branches tie weakly at `0.100`.
- Report: `results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`.

Allowed claim:

Abstention is justified on ambiguous MG-style score plateaus. Do not promote a
forced branch as a main v0.2 success on Can MG.

### 7. Lift Hard-Negative / Action-Conflict Extension

Motivation: Test whether the generated hard-negative mechanism transfers beyond
Can. This is an exploratory C1 extension, not part of the completed main
benchmark gate.

Split construction:

- Robomimic Lift MG sparse low-dimensional splits.
- Labeled positives are compact successful demos.
- Labeled negatives are explicit action-conflicting failures.
- The unlabeled pool contains hidden successful and hard-negative demos.
- Hidden labels are used only for construction and support/end-point audits.

Compared methods:

- `bad_aware_proxy_top40`
- `state_action_positive_nn_top40`

Endpoint budget:

- Support audit: split seeds `101`, `202`, `303`.
- Endpoint check completed on split seeds `101`, `202`, and `303`.
- The completed endpoint checks use official BC-RNN-GMM, 200 epochs, 100 epoch
  steps, and 50 valid-positive-start rollouts per split.
- Full C1 endpoint bar remains official BC-RNN-GMM, 200 epochs, 100 epoch
  steps, and 50 valid-positive-start rollouts over split seeds `101`, `202`,
  and `303`.

Expected winner:

Bad-aware hard support should beat matched positive-only support if the support
advantage converts into policy quality.

Completed evidence:

- Support audit: state-action positive-NN top40 selects `12/120` hidden
  positives and admits `108/240` hidden bad demos; bad-aware proxy top40 selects
  `82/120` hidden positives and admits `38/240` hidden bad demos.
- Split-101/202/303 endpoint aggregate: bad-aware proxy top40 reaches `15/150`
  successes and selects `82` hidden positives with `38` hidden bad demos;
  state-action positive-NN top40 reaches `5/150` successes and selects `12`
  hidden positives with `108` hidden bad demos.
- Report:
  `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.

Allowed claim:

The support mechanism transfers beyond Can and the three full-budget endpoint
splits are directionally consistent, but weak in absolute success. Claim this as
completed non-Can mechanism evidence, not as a primary benchmark endpoint win.

## Future Probe Rules

Future regime-probe variants should be added with:

1. split family and seed list,
2. methods to compare,
3. endpoint budget,
4. expected winner or expected abstention,
5. support-side pass/fail condition,
6. endpoint-side pass/fail condition,
7. maximum allowed claim if the probe passes.

If a future probe is designed after seeing endpoint outcomes, it must be marked
as exploratory and cannot be used as fresh validation without a new held-out
split family.
