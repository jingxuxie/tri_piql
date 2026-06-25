# TRIAGE-BC Paper Completion Plan

**Project:** Offline imitation from scarce successes, scarce failures, and mixed unlabeled logs  
**Current draft:** `paper/triage_bc_paper.tex`  
**Current method:** `TRIAGE-BC v0.1`, frozen in `METHOD_FREEZE.md`  
**Goal:** Decide whether the current evidence is enough for a high-impact ICLR / NeurIPS / ICML-style paper, and define the additional experiments and analyses needed for a complete, high-quality submission.

---

## 0. Executive decision

### Current answer

**You do not yet have enough evidence for a high-impact main-conference methods paper if the claim is that TRIAGE-BC is a strong new algorithm that improves over the strongest same-backbone baselines.**

You **do** have enough evidence for a careful, honest paper about the *score-to-support conversion problem* in offline imitation, but the current draft reads more like a diagnostic / problem-framing paper than a decisive algorithmic paper. The current robotics evidence shows that:

- TRIAGE-BC v0.1 beats weighted BC on **Can 40p/80b**, but loses to **positive-only nearest-neighbor retrieval**.
- TRIAGE-BC v0.1 loses to **weighted BC** and **positive-only NN** on **Lift MG**.
- Positive-only NN is a strong baseline on the Can settings.
- Can MG exposes a real router / policy-quality-proxy limitation.
- Controlled PointNav is strong, but synthetic.

This is scientifically valuable, but for ICLR / NeurIPS / ICML you need one of the following:

1. **A stronger method result:** a v0.2 method that consistently matches or beats the best strong baseline across several frozen real robotics splits.
2. **A stronger benchmark / phenomenon paper:** a new, compelling benchmark showing when explicit bad demonstrations are necessary and why current converters fail.
3. **A stronger theory + diagnostic paper:** a principled impossibility / identifiability / precision-coverage analysis with minimal but clean experiments.

My recommended path is **Option 1 + a small piece of Option 2**: develop **TRIAGE-BC v0.2**, a coverage-risk portfolio converter, and evaluate it on fresh frozen splits. Keep v0.1 and the current draft as the honest diagnostic foundation.

---

## 1. What the current evidence supports

### 1.1 Strongly supported claims

These are safe to claim now.

#### Claim A: Contaminated mixed logs hurt naive cloning

Evidence:

- Controlled PointNav: BC-all and positive+unlabeled BC degrade as bad fraction increases.
- Can 40p/80b: all-demo BC is worse than weighted BC, positive-only NN, and TRIAGE-BC.
- Lift MG: all-demo BC is very weak.

Paper wording:

> Mixed-log cloning can be substantially harmed by undesirable behavior in the unlabeled log.

#### Claim B: Score learning alone is not the paper contribution; score-to-support conversion is the bottleneck

Evidence:

- Can 40p/80b favors a cleaner support distribution over soft weighting.
- Lift MG favors broad weighted coverage over purer hard support.
- Can MG shows that likelihood proxies choose the wrong branch or cannot detect weak branches.

Paper wording:

> The central algorithmic problem is not only learning a desirability score, but converting that score into a policy-training distribution.

#### Claim C: Strong no-bad-label retrieval is a necessary baseline

Evidence:

- Positive-only NN beats TRIAGE-BC on the frozen Can 40p/80b primary endpoint.
- Positive-only NN beats TRIAGE-BC on the current Can 20p/80b diagnostics.
- Positive-only NN beats TRIAGE-BC on the Can 80p/80b diagnostic.
- Positive-only NN beats TRIAGE-BC on Lift MG, although weighted BC is best there.

Paper wording:

> Explicit bad labels can improve calibration, but their utility depends on the support converter. Positive-only retrieval can lie on a better precision/coverage frontier and must be treated as a first-class baseline.

#### Claim D: Controlled PointNav shows the mechanism cleanly

Evidence:

- With only two positive route-prefix demonstrations and two bad shortcut demonstrations, TRIAGE gap support reaches perfect success at all tested contamination levels.
- With five positives and as few as one bad shortcut demo, selected support is pure and performance remains perfect in the controlled setting.

Paper wording:

> In controlled settings where positives are incomplete and bad labels mark shortcut failures, explicit failures can be highly label-efficient calibration signal.

---

## 2. What the current evidence does *not* support

Do **not** claim any of the following unless you add new evidence.

### Unsupported claim 1: “TRIAGE-BC is the best non-oracle method on Robomimic.”

False under the current evidence.

- Can 40p/80b: positive-only NN is best non-oracle.
- Lift MG: weighted BC is best non-oracle.

### Unsupported claim 2: “Bad labels are necessary.”

False under the current evidence.

Positive-only NN is strong and often better than TRIAGE-BC. The safer claim is:

> Bad labels can improve calibration, but the current converter does not always translate that calibration into better policy performance.

### Unsupported claim 3: “Hard support is generally better than soft weighting.”

False.

Lift MG and Can MG show that broad weighted coverage can be better than purer hard support.

### Unsupported claim 4: “This validates an inverse-Q / IRL robotics method.”

False under the current robotics evidence.

The policy is official Robomimic BC-RNN-GMM trained on selected or weighted data. That is a score-calibrated imitation pipeline, not a validated inverse-Q robotics method.

---

## 3. Main weaknesses reviewers will notice

### Weakness 1: The method is not the best method in the main table

Your main endpoint table currently makes the story hard to sell as a methods paper:

| Task | Best non-oracle | TRIAGE-BC rank |
|---|---|---|
| Can 40p/80b | positive-only NN | second non-oracle |
| Lift MG | weighted BC | third non-oracle |

This is the biggest issue.

### Weakness 2: The main positive gap is modest and statistically cautious

TRIAGE-BC beats weighted BC on Can 40p/80b by only **+0.060** pooled success, and the paired bootstrap interval crosses zero. This is useful directional evidence, but not a decisive algorithmic win.

### Weakness 3: The current converter is off the precision/coverage frontier on Can

On Can 40p/80b, TRIAGE-BC recovers slightly more hidden-positive demos than positive-only NN, but admits many more hidden-bad demos. This is exactly the kind of result reviewers will use to argue that the negative labels are not being used effectively.

### Weakness 4: Lift MG contradicts a hard-support story

TRIAGE-BC selects very pure Lift support, yet weighted BC performs better. That is valuable analysis, but it weakens a simple “our method wins” story.

### Weakness 5: Can MG is unresolved

Can MG is useful as a stress diagnostic, but it should not be a main positive result unless you solve the policy-quality proxy / branch-selection problem.

---

## 4. Recommended high-impact paper target

### Target title

**TRIAGE-BC: Coverage-Risk Support Conversion for Offline Imitation from Successes, Failures, and Mixed Logs**

### Target thesis after v0.2

> Offline imitation from scarce successes, scarce failures, and mixed logs is limited by score-to-policy conversion. A good converter must balance positive coverage against bad-action admission. TRIAGE-BC v0.2 treats support conversion as a hidden-label-free coverage-risk selection problem over a small candidate portfolio, improving robustness over fixed hard filtering, soft weighting, and positive-only retrieval.

### What v0.2 must achieve

To have a credible high-impact methods paper, v0.2 should satisfy at least this minimum bar:

| Requirement | Minimum acceptable outcome |
|---|---|
| Can 40p/80b | Match or beat positive-only NN and weighted BC on fresh frozen splits |
| Lift MG | Match or beat weighted BC, or correctly choose weighted-like support as part of the method |
| Can MG | Correctly abstain, or choose soft weighting with a proxy that predicts coverage-sensitive quality |
| Controlled PointNav | Preserve current perfect / near-perfect mechanism result |
| Fresh split validation | v0.2 is frozen before final test splits |
| Strong baselines | Same backbone, same budget, same endpoint protocol |

If v0.2 cannot meet this bar, the paper should be reframed as a careful **benchmark / diagnostic paper** rather than an algorithmic methods paper.

---

## 5. Proposed new method: TRIAGE-BC v0.2

### 5.1 Core idea

TRIAGE-BC v0.1 uses a fixed score-shape router. It currently fails because high-purity support is not always the best policy-training data, and positive-only retrieval often lies on a better frontier.

TRIAGE-BC v0.2 should become a **coverage-risk portfolio selector**.

Instead of committing to one hard-support rule, construct a small family of candidate policy-training distributions and choose among them using a hidden-label-free proxy for the precision/coverage tradeoff.

### 5.2 Candidate training distributions

For each split, generate candidates:

#### Positive-only candidates

These use no bad labels and are required both as baselines and as candidate branches.

- `posNN_top20`
- `posNN_top40`
- `posNN_top80`
- `posNN_top160` for Lift-like large pools

#### Bad-aware hard support candidates

These use the positive-vs-negative classifier score.

- `classifier_top20`
- `classifier_top40`
- `classifier_top60`
- `classifier_top80`
- `adaptive_masscap`
- `pos_min`

#### Hybrid positive+bad-aware candidates

These are the most important new candidates.

- **Intersection:** `posNN_k ∩ score_above_q`
- **Bad-filtered positive NN:** `posNN_k` after removing demos below a bad-aware score threshold
- **Coverage-restored bad-aware support:** `adaptive_masscap ∪ posNN_small`
- **Pareto candidate:** select demos that are nondominated by `(positive_similarity, bad_aware_score)`

These candidates are designed to fix the Can failure mode, where positive-only NN is cleaner than TRIAGE-BC but bad-aware scores may still identify additional useful coverage.

#### Soft candidates

These are needed for Lift and Can MG-like coverage-sensitive regimes.

- Weighted BC with original classifier probabilities
- Weighted BC with temperature-scaled scores
- Weighted BC with clipped scores, e.g. `w = clip(score, 0.05, 0.8)`
- Top-mass weighted BC: keep all demos but cap total bad-risk mass

### 5.3 Hidden-label-free proxy for choosing candidates

For each candidate distribution `S` or weight vector `w`, compute a proxy:

```text
Proxy(S) = CoverageProxy(S) - lambda_bad * BadRisk(S) - lambda_conflict * ActionConflict(S)
```

Recommended components:

#### CoverageProxy

Use at least two of these:

1. **Positive leave-one-out action likelihood:**
   Train or fit a cheap nonparametric action model from candidate support and score held-out labeled-positive transitions.

2. **Positive state coverage:**
   Fraction of labeled-positive states whose kNN distance to candidate support is below a threshold.

3. **Candidate effective sample size:**
   For weighted candidates, use `ESS = (sum w)^2 / sum w^2`.

4. **Trajectory diversity:**
   Average pairwise state-embedding diversity or coverage of object pose bins.

#### BadRisk

Use:

1. Mean negative similarity: proximity of selected support to labeled negative state-action support.
2. Mean `1 - classifier_score` over selected demos.
3. Count of selected demos below the labeled-positive p10 score.

#### ActionConflict

This is important for Can-style action-conflicting contamination.

For candidate support near labeled-positive states, measure whether selected actions disagree with positive actions:

```text
action_conflict = mean_{(s,a+) in D+} min_{(s',a') in S near s} ||a' - a+||
```

Also compute proximity to labeled bad actions:

```text
bad_action_conflict = fraction of candidate transitions near D- state-action support
```

### 5.4 Proxy selection protocol

1. Use development splits only: old seeds, `shuffle42`, and existing validation splits.
2. Fit proxy weights on development splits by predicting endpoint ranking among already-trained candidates.
3. Freeze proxy weights in `METHOD_FREEZE_V02.md`.
4. Run fresh final splits not used in development, e.g. `101`, `202`, `303`, or `44`, `55`, `66`.
5. Report v0.1 and v0.2 separately.

### 5.5 Why this is publishable if it works

This turns the current weakness into the method contribution:

- v0.1 showed that fixed hard support fails in some regimes.
- v0.2 explicitly estimates coverage-risk tradeoffs.
- Positive-only NN is no longer merely a baseline that beats the method; it becomes a candidate branch that the method must beat, match, or improve via bad-aware filtering.
- Weighted BC is no longer a counterexample; it becomes the correct branch in coverage-dominated regimes.

---

## 6. Required additional experiments

### Experiment Group A: Finish current v0.1 evidence cleanly

These experiments are needed even if you do not build v0.2.

#### A1. Standardize all endpoint tables

For every endpoint table, report:

- task
- split seed
- policy seed
- method
- selected unlabeled count
- total train demos
- hidden-positive selected count, audit only
- hidden-bad selected count, audit only
- support purity, audit only
- successes / episodes
- endpoint checkpoint
- whether row is primary, diagnostic, oracle, or development

Make sure `train_or_support_count` is unambiguous. Do not mix per-split count, pooled count, and selected-unlabeled count in one column.

Status 2026-06-25:

- Added `scripts/summarize_master_evidence_tables.py`.
- Generated `results/final_paper/tables/endpoint_master_table.csv`,
  `results/final_paper/tables/support_master_table.csv`, and
  `results/final_paper/tables/baseline_strength_REPORT.md`.
- The report normalizes the current staged evidence and marks Can 20p/80b and
  Can 80p/80b as diagnostic/incomplete, while confirming that v0.1 is not best
  non-oracle on either primary robotics task.

#### A2. Complete Can 20p/80b if you mention it in the appendix

Current status:

- Support audit: three splits.
- Endpoint: only two completed TRIAGE-vs-positive-only splits; weighted only on one split.

Recommended completion:

- Finish split 33 endpoints for TRIAGE-BC, positive-only NN, weighted BC, and all-demo BC.
- Finish weighted BC split 22 and 33.
- Keep it diagnostic unless all methods are complete across three splits.

Expected risk:

- Positive-only NN probably remains stronger.
- That is acceptable if framed as a limitation.

#### A3. Complete Can 80p/80b only if you want it as a diagnostic

Current status:

- Support audit: three splits.
- Endpoint: only split 33.

Recommended completion:

- Either complete split 11 and 22 endpoints for TRIAGE-BC, positive-only NN, weighted BC, and all-demo BC, or move Can 80p/80b to a support-only appendix.

Do not leave it halfway in a main-looking table.

#### A4. Add one extra policy seed for the two primary tasks

Current primary matrix uses split seeds 11/22/33 and policy seed 0. This is acceptable but thin.

Minimum robustness extension:

- For Can 40p/80b and Lift MG, rerun the top two non-oracle methods with policy seed 1.
- Can 40p/80b: positive-only NN, TRIAGE-BC, weighted BC.
- Lift MG: weighted BC, positive-only NN, TRIAGE-BC.

Ideal extension:

- 3 split seeds × 2 policy seeds × 50 episodes for primary tasks.

If compute is tight, prioritize **policy-seed robustness for the method and the strongest baseline**, not all baselines.

#### A5. Use independent initial-state units in uncertainty reporting

Continue reporting paired bootstrap by split and initial state. Avoid treating repeated rollouts from the same validation start as independent.

Add:

- split-level success table
- initial-state-level paired deltas
- exact split sign pattern
- bootstrap over split × initial-state units

---

### Experiment Group B: Stronger baselines

These are essential for a high-quality paper.

#### B1. Weighted BC variants

Weighted BC is a strong baseline. Test whether the current weighted baseline is just under-calibrated.

Run on Can 40p/80b and Lift MG first:

- original classifier-probability weighted BC
- temperature-scaled scores: `T ∈ {0.5, 1.0, 2.0}`
- clipped scores: `w ∈ [0.05, 0.5]`, `w ∈ [0.05, 0.8]`
- top-mass weighted sampler: keep total score mass fixed to estimated positive mass
- class-balanced weighted sampler: equal mass from labeled positives and weighted unlabeled

Report whether TRIAGE-BC still beats the strongest weighted variant on Can.

#### B2. Positive-only retrieval variants

Positive-only NN is currently the strongest Can baseline. You need to understand it deeply.

Run support audits for:

- `posNN_top20`, `top40`, `top60`, `top80`
- state-only NN
- state-action NN
- trajectory-mean NN
- kNN with normalized features vs raw features
- one-class density / one-class SVM-style baseline if easy

Train policies for the most promising 2–3 settings on Can 40p/80b and Lift MG.

Key question:

> Is positive-only NN strong because it is genuinely solving the task, or because the current split is easy for nearest-neighbor retrieval?

Status 2026-06-25:

- Added `scripts/summarize_hybrid_candidate_support_audit.py`, which computes
  full positive-NN rankings from the staged HDF5 splits and combines them with
  classifier score diagnostics.
- Generated `results/final_paper/tables/hybrid_candidate_support_per_split.csv`,
  `results/final_paper/tables/hybrid_candidate_support_summary.csv`, and
  `results/final_paper/tables/hybrid_candidate_support_REPORT.md`.
- Positive-only top-k sweeps show the Can support frontier is already strong:
  Can 40 top20 is perfectly clean but low-recall, top40 is the best current
  endpoint baseline, and larger top-k values quickly admit many bad demos.
  Lift top-k confirms that hard support is coverage-limited compared with
  weighted BC.

#### B3. Bad-aware fixed top-k policies

You already have support curves for classifier top-k. Train a small number of endpoint policies:

Can 40p/80b:

- classifier top20
- classifier top40
- classifier top60
- classifier top80

Lift MG:

- classifier top160 already done
- consider top320 or top480 if support audit suggests coverage improvement

This helps answer whether the adaptive masscap rule is really near-optimal among bad-aware hard supports.

#### B4. Oracle and semi-oracle controls

Keep these diagnostic-only:

- all-positive oracle
- hidden-good oracle support
- oracle best hard top-k by hidden labels
- oracle branch chooser among hard, soft, positive-only

The oracle branch chooser is useful because it tells you whether the candidate family contains a strong method at all. If the oracle chooser cannot beat the baselines, the issue is not the router; it is the candidate family.

---

### Experiment Group C: Build a benchmark where bad labels are genuinely useful

The current Robomimic Can splits are too favorable to positive-only NN. To make a high-impact paper about explicit bad demonstrations, add a setting where bad labels provide unique information.

#### C1. Hard-negative / action-conflict split

Construct a split where hidden bad demos are near positives in state space but differ in action or outcome.

Procedure:

1. For each failed demo, compute nearest labeled-positive trajectory distance.
2. Select unlabeled bad demos that are close to labeled positives.
3. Select hidden positives from states under-covered by labeled positives.
4. Compare positive-only NN, bad-aware classifier, hybrid support, and weighted BC.

This tests whether bad labels help reject *confusable* failures.

Status 2026-06-25:

- Implemented a support-only generated Can hard-negative/action-conflict
  diagnostic in `scripts/summarize_hard_negative_can_action_conflict_audit.py`.
- The generator writes three split files under
  `results/final_paper/ablations/hard_negative_can_action_conflict_splits/`
  plus construction, per-split, summary, and Markdown report artifacts.
- Support gate over split seeds 101/202/303: state-action positive-NN top40
  recovers `0.583` hidden-positive recall with `0.208` hidden-bad admission;
  bad-aware proxy top40 recovers `1.000` recall with `0.000` bad admission;
  rank-fusion hybrid top40 recovers `0.875` recall with `0.062` bad
  admission.
- Split-101 endpoint smoke at 50 epochs / 10 valid-positive rollouts:
  rank-fusion hybrid `4/10`, pure bad-aware proxy `1/10`, state-action
  positive-NN top40 `0/10`.
- Split-101 endpoint check at the frozen 200-epoch / 50-rollout budget:
  rank-fusion hybrid `33/50`, state-action positive-NN top40 `30/50`.
- Three-split endpoint check at the frozen 200-epoch / 50-rollout-per-split
  budget:
  rank-fusion hybrid `104/150`, state-action positive-NN top40 `91/150`.
- Interpretation: the hard-negative construction finally produces a setting
  where a bad-aware hybrid beats positive-only support at the endpoint. This is
  now suitable as targeted generated-diagnostic evidence, but it should remain
  separate from the primary Robomimic benchmark rows because the split
  construction is synthetic.

#### C2. Scarce-positive coverage-shift split

Construct labeled positives from a narrow subset of initial conditions, while unlabeled positives cover broader initial states.

Procedure:

1. Cluster successful demos by object pose / initial state.
2. Choose labeled positives from one or two clusters.
3. Put successful demos from other clusters into unlabeled.
4. Add failed demos across all clusters.
5. Evaluate whether bad-aware scoring recovers hidden positives beyond positive-only NN.

This tests the realistic case where trusted successes are not representative.

Status 2026-06-25:

- Added `scripts/summarize_can_coverage_shift_audit.py`.
- Generated `results/final_paper/ablations/can_coverage_shift_REPORT.md`
  plus per-split and summary CSVs over split seeds `101`, `202`, `303`.
- Support audit clears strongly: state-action positive-NN top40 recovers
  `105/120` hidden positives and admits `15/240` hidden bad demos, while
  bad-aware top40 recovers `120/120` with `0/240` bad and the bad-aware-heavy
  hybrid recovers `118/120` with `2/240` bad.
- Split-101 endpoint smoke at 50 epochs / 10 valid-positive starts gives
  hybrid `4/10`, pure bad-aware `2/10`, and state-action positive-NN `0/10`.
- Split-101 frozen-budget check at 200 epochs / 50 valid-positive starts gives
  hybrid `39/50` versus state-action positive-NN `35/50`.
- Three-split frozen-budget check at 200 epochs / 50 valid-positive starts per
  split gives the bad-aware-heavy hybrid `120/150` versus state-action
  positive-NN top40 `103/150`.
- Promoted the diagnostic into the manuscript appendix as
  `tab:coverage-shift-can`, added the coverage-shift artifacts to the
  reproducibility/checklist maps, and extended the paper validators to check
  the endpoint and support counts from the staged CSVs.
- Interpretation: the coverage-shift construction provides a second targeted
  generated robotics diagnostic where explicit bad labels help support
  selection and endpoint transfer. Keep it separate from primary Robomimic
  benchmark rows unless the manuscript explicitly frames it as generated
  diagnostic evidence.

#### C3. Prefix-positive robotics split

This mirrors the controlled PointNav mechanism.

Procedure:

1. Use only early prefixes of successful Robomimic demos as labeled positives for score learning.
2. Use failed demos as labeled negatives.
3. Put full successful and failed trajectories in the unlabeled pool.
4. Train policies on selected full trajectories.

This asks whether the PointNav mechanism transfers to real robot demonstrations.

Caveat:

- This changes the problem setting. Present it as a controlled robotics diagnostic, not the main default setting.

Status 2026-06-25:

- Added `scripts/summarize_can_prefix_positive_audit.py`.
- Generated `results/final_paper/ablations/can_prefix_positive_REPORT.md`
  plus construction, per-split, support-summary CSVs, and split files for
  seeds `101`, `202`, `303`.
- Support audit clears strongly. Across the three prefix-positive splits,
  prefix state-action positive-NN top80 selects only `37/240` hidden positives
  and `203/240` hidden bad demos, while prefix bad-aware state top80 selects
  `195/240` hidden positives and `45/240` hidden bad demos.
- Ran the full endpoint gate over split seeds `101`, `202`, and `303`, using
  official Robomimic BC-RNN-GMM for 200 epochs, 100 gradient steps per epoch,
  and 50 valid-positive starts per split.
- Endpoint result: `prefix_bad_aware_state_top80` reaches `119/150`
  successes (`0.793`) versus matched `prefix_state_action_nn_top80` at `6/150`
  (`0.040`). Per split, bad-aware wins `26/50` vs `1/50`, `43/50` vs `2/50`,
  and `50/50` vs `3/50`.
- Added `scripts/summarize_can_prefix_positive_endpoint.py` and staged
  `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/REPORT.md`
  plus `endpoint_200ep_aggregate_summary.csv`.
- Added the paper-facing diagnostic figure/report via
  `scripts/plot_can_prefix_positive_diagnostic.py`,
  `results/final_paper/figures/can_prefix_positive_diagnostic.{png,pdf}`, and
  `results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`.
- Interpretation: this is the clearest Robomimic transfer of the PointNav
  prefix-positive mechanism so far and is now a strong three-split controlled
  robotics diagnostic. Keep it separate from the primary benchmark rows because
  the split construction changes the default Robomimic setting.

---

### Experiment Group D: v0.2 development and final testing

#### D1. Candidate-family audit

For each development split, build a table:

| Candidate | Hidden-positive recall | Hidden-bad admission | Proxy score | Endpoint success |
|---|---:|---:|---:|---:|

Use hidden labels only for audit, not for selection.

Run this on:

- Can 40p/80b dev split
- Can 20p/80b dev split
- Can 80p/80b dev split
- Lift MG dev split
- Can MG dev split if feasible

Status 2026-06-25:

- Added `scripts/summarize_candidate_family_audit.py`.
- Generated `results/final_paper/tables/candidate_family_audit.csv`,
  `results/final_paper/tables/candidate_family_decision_table.csv`, and
  `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`.
- Current endpoint-evaluated portfolio can only match the strongest baseline
  by selecting that baseline: Can 40p/80b selects positive-only NN, and Lift MG
  selects weighted BC.
- No bad-aware hard branch currently beats the strongest positive-only/weighted
  baseline on an endpoint-evaluated robotics setting, so v0.2 needs new hybrid
  candidates or weighted variants before fresh final runs.
- Follow-up hybrid support audit found that tested hybrid positive-NN /
  classifier hard-support rules do not justify immediate endpoint training:
  clean Can hybrids lose coverage, coverage-restored Can hybrids admit more bad
  demos, and Lift hybrids remain hard-support variants in a coverage-dominated
  setting.

#### D2. Proxy-validation plot

Make a scatter plot:

```text
x-axis: hidden-label-free proxy score
y-axis: endpoint success
color: task / split
shape: candidate family
```

This is one of the most important figures for the final paper. It directly shows whether your proposed proxy predicts policy quality.

Status 2026-06-25:

- Added `scripts/plot_proxy_endpoint_validation.py`.
- Generated `results/final_paper/tables/proxy_endpoint_validation.csv`,
  `results/final_paper/tables/proxy_endpoint_validation_correlations.csv`,
  `results/final_paper/tables/proxy_endpoint_validation_winners.csv`,
  `results/final_paper/tables/proxy_endpoint_validation_REPORT.md`, and
  `results/final_paper/figures/proxy_endpoint_validation.{png,pdf}`.
- Current hidden-label-free coverage-only proxy is not sufficient for v0.2:
  it matches the endpoint winner in `2/4` evaluated settings and only `1/2`
  primary settings.
- Failure pattern: coverage-only selection correctly chooses weighted BC on
  Lift MG, but incorrectly chooses weighted BC on Can 40p/80b and Can 20p/80b,
  where contamination makes positive-only retrieval stronger.
- Audit-only precision-risk scores are also not enough because they fail on
  Lift MG, where high-purity hard support under-covers the policy learner.
- Decision: do not freeze v0.2 around the current coverage-only proxy. Add
  hidden-label-free bad-risk and action-conflict features before spending fresh
  endpoint GPU budget.
- Added `scripts/summarize_v02_proxy_feature_screen.py` as a support-side
  follow-up over the hybrid candidate audit. It generated
  `results/final_paper/tables/v02_proxy_feature_screen.csv`,
  `results/final_paper/tables/v02_proxy_feature_screen_winners.csv`, and
  `results/final_paper/tables/v02_proxy_feature_screen_REPORT.md`.
- Mean classifier-score risk features are also not sufficient: across four
  settings and seven deployable coverage/classifier proxy formulas, proxy
  winners match the audit-support winner in only `1/28` setting-proxy cases and
  strictly dominate the positive-NN baseline in only `2/28` cases.
- Updated decision: the next v0.2 feature should estimate action-conflict or
  bad-neighbor risk explicitly, not just selected-support size or mean
  classifier score.
- Added `scripts/summarize_v02_action_risk_feature_screen.py` as the explicit
  action-conflict / bad-neighbor follow-up. It generated
  `results/final_paper/tables/v02_action_risk_feature_screen_per_split.csv`,
  `results/final_paper/tables/v02_action_risk_feature_screen.csv`,
  `results/final_paper/tables/v02_action_risk_feature_screen_winners.csv`, and
  `results/final_paper/tables/v02_action_risk_feature_screen_REPORT.md`.
- Action-risk features still do not clear the v0.2 selector gate: across four
  settings and eight deployable proxy formulas, proxy winners match the
  audit-support winner in only `1/32` setting-proxy cases and strictly dominate
  the setting-specific positive-NN baseline in only `2/32` cases.
- Updated decision: do not endpoint-train a new v0.2 branch from the current
  hybrid candidate family. The next method step must either create candidates
  that optimize action-risk / bad-neighbor features directly, or freeze an
  abstention/router story instead of proxy-selecting among stale candidates.
- Added `scripts/summarize_v02_action_risk_candidate_audit.py` to create
  candidates directly from action-conflict / bad-neighbor rankings. It generated
  `results/final_paper/tables/v02_action_risk_candidate_support_per_split.csv`,
  `results/final_paper/tables/v02_action_risk_candidate_support_summary.csv`,
  `results/final_paper/tables/v02_action_risk_candidate_support_decision.csv`,
  and `results/final_paper/tables/v02_action_risk_candidate_support_REPORT.md`.
- Direct risk candidates clear the support gate in all four audited settings:
  risk-generated candidates strictly dominate the setting-specific positive-NN
  support baseline in `4/4` settings.
- Endpoint gate result is negative on the first primary split: on Can 40p/80b
  split seed 11, `bad_neighbor_safe_top40` has perfect support audit
  (`40/40` hidden positives, `0/80` hidden bad) but reaches only `0.720` after
  200 epochs / 50 rollouts, below existing positive-NN top40 `0.840` and
  TRIAGE-BC `0.760`.
- A less distribution-shifting `positive_nn_risk_fusion_top40` endpoint gate
  narrows the gap but still does not clear the strongest baseline: it selects
  `39/40` hidden positives with `1/80` hidden bad demo and reaches `0.820` over
  50 rollouts, below existing positive-NN top40 `0.840`.
- Split-22 confirmation is also negative: `positive_nn_risk_fusion_top40`
  has perfect support audit (`40/40` hidden positives, `0` hidden bad) but
  reaches only `0.640`, below existing positive-NN top40 `0.760`.
- Added `scripts/summarize_v02_policy_coverage_diagnostic.py` and generated
  split-11 / split-22 coverage reports. Simple initial-state and
  transition-level nearest-neighbor coverage do not produce a reliable
  policy-quality proxy for the action-risk candidates.
- Updated decision: do not promote either action-risk candidate as v0.2. The
  result shows support purity can improve while endpoint quality stays below a
  strong positive-only baseline. Do not spend split-33 endpoint compute on this
  unchanged candidate family; any next v0.2 attempt needs a stronger
  policy-quality proxy, a different candidate generator, or a shift back to
  abstention/router framing.
- Follow-up union candidate status: a less aggressive candidate that keeps
  positive-only NN support and unions in the risk-fusion demos revives Can
  40p/80b but does not solve v0.2. The support audit selects `119/120` hidden
  positives and `16/240` hidden bad demos across split seeds 11/22/33. The
  bounded 200-epoch / 50-rollout endpoint gate reaches `116/150` pooled
  success, beating positive-only NN `108/150`, TRIAGE-BC v0.1 `99/150`, and
  weighted BC `90/150` on the same frozen Can 40 matrix. It wins split seeds
  22 and 33, but loses split 11 to positive-only NN (`0.760` versus `0.840`),
  and it has not addressed Lift MG or Can MG. Treat this as a promising Can
  development result, not as a frozen cross-task TRIAGE-BC v0.2 method.
- Portfolio-router audit status: adding the union row to the candidate-family
  audit changes Can 40p/80b from a no-go to a positive development branch, but
  the cross-task method remains unfrozen. A simple hidden-label-free router
  using estimated positive mass and the count above the labeled-positive
  minimum chooses hard risk-union for low-mass Can-like rows, soft weighted BC
  for the moderate-coverage Lift row, and abstention for large ambiguous Can MG
  rows. On the two primary development endpoints this portfolio reaches
  `209/300` pooled success, versus `201/300` for the strongest pre-union
  per-task baselines and `173/300` for v0.1. This clears a development
  portfolio screen, but it is post-hoc: the Can branch was designed after the
  split 11/22/33 endpoint matrix, Lift is won by selecting the weighted
  baseline branch, Can 20/80 union rows lack endpoints, and fresh split
  validation is still missing.

#### D3. Freeze v0.2

Create:

- `METHOD_FREEZE_V02.md`
- `configs/final_method_v02.yaml`
- `configs/final_eval_v02.yaml`

Status 2026-06-25:

- Drafted `METHOD_FREEZE_V02.md`,
  `configs/final_method_v02.yaml`, and `configs/final_eval_v02.yaml` for the
  development portfolio router.
- The freeze is intentionally marked as a development freeze, not a final
  paper-method claim.
- Frozen rule: abstain on large ambiguous mass/count, choose soft weighted BC
  on moderate broad mass/count, otherwise choose hard positive-NN/risk union.
- Fresh validation split seeds are predeclared as `101`, `202`, and `303` for
  Can 40p/80b and Lift MG.
- Success gate: best or tied-best non-oracle on fresh Can 40, match or beat
  weighted BC on fresh Lift, and keep Can MG as abstention unless the frozen
  rule says otherwise.

Freeze:

- candidate family
- proxy features
- proxy weights
- branch decisions
- split seeds
- policy seeds
- endpoint checkpoint
- evaluation episodes

#### D4. Fresh final v0.2 splits

Use split seeds that were not used in v0.1 development or v0.2 tuning.

Recommended:

- Can 40p/80b: split seeds `101`, `202`, `303`
- Lift MG: split seeds `101`, `202`, `303`
- Hard-negative Can or prefix-positive Can: split seeds `101`, `202`, `303`
- Optional Can MG: stress / abstention only

Status 2026-06-25:

- Can 40p/80b split seeds `101`, `202`, and `303` have completed fresh endpoint
  gates for the frozen v0.2 router.
- The router preflight chooses hard `positive_nn_risk_union_top40` on all three
  Can splits.
- Split `101`: v0.2 union `45/50`, weighted BC `37/50`, positive-only NN
  `19/50`.
- Split `202`: v0.2 union `45/50`, positive-only NN `40/50`, weighted BC
  `33/50`.
- Split `303`: v0.2 union `39/50`, positive-only NN `36/50`, weighted BC
  `25/50`.
- Pooled completed fresh Can rows: v0.2 union `129/150` versus best completed
  per-split non-oracle baselines `113/150`.
- Lift MG split seeds `101`, `202`, and `303` have also completed the frozen
  selected branch and positive-only NN baseline.
- The router preflight chooses soft `weighted_bc` on all three Lift splits.
- Split `101`: v0.2 selected weighted `31/50`, positive-only NN `28/50`.
- Split `202`: v0.2 selected weighted `30/50`, positive-only NN `25/50`.
- Split `303`: v0.2 selected weighted `19/50`, positive-only NN `21/50`.
- Pooled completed fresh Lift rows: v0.2 selected weighted `80/150` versus best
  completed per-split non-oracle baselines `74/150`.
- Combined completed fresh Can+Lift rows: v0.2 selected branches `209/300`
  versus best completed per-split non-oracle baselines `187/300`.
- This clears the predeclared Can+Lift fresh endpoint gate in a narrow selector
  sense: Can is a real hard-union improvement, while Lift is a modest
  weighted-branch result with one losing split.

#### D5. Final v0.2 main table

The high-impact main table should look like this:

| Method | Can 40p/80b | Lift MG | Hard-negative Can | Mean rank |
|---|---:|---:|---:|---:|
| All-demo BC | | | | |
| Positive-only NN | | | | |
| Weighted BC | | | | |
| Best weighted variant | | | | |
| TRIAGE-BC v0.1 | | | | |
| TRIAGE-BC v0.2 | | | | |
| All-positive oracle | | | | |

Acceptance bar:

- v0.2 should be best or tied-best non-oracle on at least two primary tasks.
- v0.2 should not catastrophically fail on the third.
- v0.2 should have a clear explanation when it chooses hard, soft, hybrid, or abstain.

---

## 7. Analysis and figures needed for a high-quality paper

### Figure 1: Problem and method diagram

Already mostly done.

Improve by explicitly showing:

- positives
- failures
- mixed unlabeled log
- score model
- candidate support distributions
- coverage-risk router
- selected policy-training distribution

### Figure 2: Controlled PointNav mechanism

Show:

- success vs bad fraction
- hidden-good selected count
- hidden-bad selected count
- label-count ablation

### Figure 3: Primary robotics endpoints

For v0.1, be honest:

- Can: positive-only NN > TRIAGE > weighted > all-demo
- Lift: weighted > positive-only > TRIAGE > all-demo

For v0.2, this should become the central win figure if v0.2 works.

### Figure 4: Precision/coverage frontier

For Can 40p/80b, plot:

- hidden-positive recall on x-axis
- hidden-bad admission on y-axis
- marker size / color = endpoint success
- include positive-only NN, classifier top-k, TRIAGE, weighted, oracle

This figure is already conceptually strong.

### Figure 5: Proxy predicts policy quality

For v0.2, this is critical.

Plot candidate proxy score vs endpoint success. If this correlation is weak, do not promote v0.2 as a method.

### Figure 6: Score-shape diagnostics and abstention

Show why Can MG is abstained:

- score histogram / density
- high-score plateau
- branch-proxy failure

### Table 1: Main endpoint table

Use counts and rates:

```text
successes / episodes (rate)
```

Do not report only rates.

### Table 2: Support audit table

Use audit-only hidden labels:

- selected count
- hidden-positive recall
- hidden-bad admission
- purity
- endpoint success

### Table 3: Baseline strength table

Show that the paper is not using weak baselines:

- weighted variants
- positive-only retrieval variants
- fixed top-k
- all-positive oracle

### Appendix tables

- per-split results
- per-initial-state results
- policy-seed robustness
- checkpoint curves
- runtime / compute
- exact configs

---

## 8. Theory / analysis to add

The current precision/coverage analysis is useful but informal. Add one formal proposition.

### Proposition 1: Risk tradeoff under useful/harmful mixture

Assume selected support contains useful samples from distribution `P_g` and harmful samples from `P_b`. Let selected useful recall be `r` and harmful admission be `f`. Under bounded supervised loss and standard finite-sample assumptions, behavior cloning excess risk can be decomposed into:

```text
estimation / coverage term decreasing with n+ + rNg
+
contamination term increasing with fNb / selected_count
```

Then show:

- pure small support is not always optimal;
- broad weighted support is not always optimal;
- the optimal converter depends on the relative coverage and contamination constants.

### Proposition 2: Positive-mass estimate under calibrated scores

If the trajectory score is a calibrated estimate of hidden usefulness probability, then:

```text
E[sum_tau score(tau)] = expected number of useful unlabeled trajectories
```

This justifies the mass-capped selector as a heuristic estimate of useful support size.

### Proposition 3: Why likelihood-only branch selection can fail

Construct a simple example where:

- policy A has better positive likelihood on labeled positives;
- policy B has broader state coverage and better rollout success;
- positive/negative likelihood chooses A but rollout favors B.

This directly supports the Can MG proxy failure and motivates coverage-aware proxies.

---

## 9. Paper rewrite plan

### If you keep v0.1 only

Use a cautious title:

**When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study**

Status 2026-06-25:

- Adopted this cautious diagnostic title in `paper/triage_bc_paper.tex`,
  `paper/iclr2026/main.tex`, `paper/triage_bc_draft.md`,
  `PAPER_DRAFT_OUTLINE.md`, and `tri_piql_paper_completion_plan.md`.
- Reframed the abstract and contributions around when explicit failures help,
  including controlled PointNav plus generated Robomimic Can diagnostics, while
  preserving the frozen Robomimic caveats that positive-only retrieval and
  weighted BC remain strongest in key primary settings.

Contributions:

1. Define the tri-signal mixed-log imitation setting.
2. Show controlled evidence that scarce bad labels can recover hidden good support.
3. Show real robotics evidence that score-to-support conversion is delicate.
4. Establish strong baselines and failure modes.

Tone:

- Honest diagnostic paper.
- Do not oversell method superiority.
- Emphasize lessons for future IRL / imitation work.

Risk:

- May be considered insufficiently algorithmic for main ICLR / NeurIPS / ICML.

### If you add v0.2 and it works

Use a methods title:

**TRIAGE-BC: Coverage-Risk Support Conversion for Offline Imitation from Successes, Failures, and Mixed Logs**

Contributions:

1. Define score-to-support conversion as the bottleneck in tri-signal offline imitation.
2. Propose a hidden-label-free coverage-risk portfolio selector.
3. Show v0.2 matches or beats hard filtering, soft weighting, and positive-only retrieval across real robotics mixed-log splits.
4. Provide controlled mechanism, score-shape diagnostics, and theory explaining when hard vs soft support wins.

Tone:

- Strong method paper.
- v0.1 becomes an ablation / historical diagnostic.
- v0.2 is the main algorithm.

---

## 10. Concrete four-week execution plan

### Week 1: Clean current evidence and finish essential diagnostics

Tasks:

- Standardize all tables and counts.
- Finish Can 20p/80b split 33 endpoints if Can 20 appears in the appendix.
- Decide whether to complete or demote Can 80p/80b.
- Add weighted variants support / cheap runs on Can 40 and Lift.
- Run positive-only NN top-k support sweeps on Can 40 and Lift.

Deliverables:

- `results/final_paper/tables/endpoint_master_table.csv`
- `results/final_paper/tables/support_master_table.csv`
- `results/final_paper/tables/baseline_strength_REPORT.md`
- `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`
- `results/final_paper/tables/hybrid_candidate_support_REPORT.md`

Decision gate:

- If no candidate support family can beat positive-only on Can or weighted on Lift even with oracle branch choice, stop method development and write a diagnostic paper.

### Week 2: Develop v0.2 proxy on dev splits

Tasks:

- Implement candidate generator.
- Implement coverage-risk proxy.
- Use existing and cheap new runs to estimate proxy-vs-endpoint correlation.
- Tune proxy only on development splits.
- Freeze v0.2.

Deliverables:

- `METHOD_FREEZE_V02.md`
- `results/v02_dev/proxy_validation_REPORT.md`
- candidate-family plots

Decision gate:

- Proxy must choose a candidate that is competitive with the best strong baseline on Can and Lift development splits.

### Week 3: Fresh final v0.2 runs

Tasks:

- Run fresh split seeds for Can 40p/80b and Lift MG.
- Run hard-negative or prefix-positive Can if implemented.
- Evaluate endpoint with 50 episodes per split, fixed checkpoint.
- Run top baselines under same protocol.

Deliverables:

- `results/v02_final/primary_endpoint_matrix_REPORT.md`
- `results/v02_final/primary_uncertainty_REPORT.md`
- `results/v02_final/per_initial_state/`

Decision gate:

- v0.2 must be best or tied-best non-oracle on at least two main tasks.

### Week 4: Write paper and finalize reproducibility

Tasks:

- Rewrite abstract and contributions based on v0.2 outcome.
- Add formal propositions.
- Finalize figures.
- Add reproducibility appendix.
- Run paper linter and table validator.

Deliverables:

- complete `paper/triage_bc_paper.tex`
- `paper/REPRODUCE_PAPER.md`
- `results/final_submission/`
- camera-ready-style artifact map

---

## 11. Go / no-go criteria for a top-tier submission

### Current status as of 2026-06-25

The current package is a **yellow-light diagnostic / benchmark paper** and a
**red-light methods paper** if the claimed contribution is TRIAGE-BC v0.2.
v0.1 has complete frozen primary matrices on Can 40p/80b and Lift MG, and the
generated Can diagnostics provide strong mechanism evidence for explicit bad
labels. The newest union candidate is a real Can 40p/80b improvement, reaching
`116/150` pooled success versus positive-only NN `108/150`, TRIAGE-BC v0.1
`99/150`, and weighted BC `90/150`. However, this is still a development
candidate: it loses split 11 to positive-only NN and has not been frozen on
fresh test splits. A follow-up portfolio router can pair the Can union branch
with weighted BC on Lift and abstention on Can MG, reaching `209/300` over the
two primary development endpoints versus `201/300` for the strongest pre-union
per-task baselines. That is promising enough to justify a frozen fresh-split
gate, but not enough to submit as a decisive methods paper.

Fresh-gate update on 2026-06-25: Can 40p/80b and Lift MG split seeds `101`,
`202`, and `303` have now completed the frozen v0.2 endpoint gate. On Can, the
selected hard union row reaches `45/50`, `45/50`, and `39/50`; strongest
completed non-oracle baselines are `37/50`, `40/50`, and `36/50`, so the pooled
fresh Can read is `129/150` for v0.2 versus `113/150` for best per-split
baselines. On Lift, the selected weighted row reaches `31/50`, `30/50`, and
`19/50`; positive-only NN reaches `28/50`, `25/50`, and `21/50`, so the pooled
fresh Lift read is `80/150` for v0.2 versus `74/150` for best per-split
baselines. Combined, the v0.2 selected branches reach `209/300` versus
`187/300` for the best per-split non-oracle baselines. This clears the
predeclared fresh Can+Lift gate, but the
methods-paper gate remains yellow rather than green because the Lift advantage
is modest, one Lift split is negative, and the Lift branch is essentially a
router-selected weighted-BC baseline.

| Gate | Current state | Decision |
|---|---|---|
| v0.2 best or tied-best on at least two real robotics settings | Fresh Can branch is complete and positive (`129/150` vs `113/150` best per-split baselines); fresh Lift selected weighted branch is complete and modestly positive in aggregate (`80/150` vs `74/150`), but loses split `303` and gains novelty mainly from correct branch selection | yellow |
| Strong same-backbone baselines | Positive-only NN, weighted BC, all-demo, and oracle diagnostics staged for primary rows | green |
| Proxy predicts endpoint quality | Coverage-only proxy still fails Can; mass/count portfolio router is fresh-tested on Can+Lift, but Lift's small aggregate margin means proxy strength is still only partial | yellow |
| Mechanism evidence for bad labels | Controlled PointNav plus hard-negative, coverage-shift, and prefix-positive Can diagnostics | green for diagnostic framing |
| Paper honesty and artifact validation | Current manuscript foregrounds positive-only and weighted BC caveats and validates staged artifacts | green |

### Green light for ICLR / NeurIPS / ICML methods submission

Proceed if:

- v0.2 is best or tied-best non-oracle on at least two real robotics settings.
- v0.2 has fresh frozen-split evidence, not post-hoc branch choice.
- Strong positive-only and weighted baselines are included.
- The proxy-vs-endpoint analysis is convincing.
- Controlled PointNav and hard-negative / coverage-shift diagnostics explain why explicit bad labels matter.

### Yellow light

Submit only if reframed carefully if:

- v0.2 matches the best baseline on average but rarely beats it.
- The method mainly abstains on hard cases.
- The strongest result remains synthetic PointNav.

Paper framing:

> A diagnostic and benchmark paper on precision/coverage tradeoffs in tri-signal offline imitation.

### Red light for main-conference methods paper

Do not submit as a methods paper if:

- TRIAGE-BC continues to lose to positive-only NN on Can and weighted BC on Lift.
- Can MG remains unresolved.
- No real robotics setting shows explicit bad labels improving over strong positive-only retrieval.
- The main positive result remains a modest, bootstrap-non-significant Can gap over weighted BC.

In that case, write a workshop paper first, or pivot to the benchmark/theory contribution.

---

## 12. Short checklist before submission

### Method validity

- [ ] Method frozen before final runs.
- [ ] No hidden labels used for threshold / branch / checkpoint / policy training.
- [ ] Baselines use same backbone and budget.
- [ ] Weighted BC and positive-only NN treated as strong baselines.
- [ ] All-positive oracle clearly marked diagnostic.

### Experiment completeness

- [ ] Main tasks have complete split-seed tables.
- [ ] Endpoint is fixed, not best checkpoint.
- [ ] Per-split and per-initial-state results reported.
- [ ] Uncertainty accounts for repeated starts.
- [ ] At least one policy-seed robustness check.

### Claims

- [ ] No claim that bad labels are necessary unless supported by a real benchmark.
- [ ] No claim that hard support always wins.
- [ ] No claim that v0.1 validates inverse-Q robotics.
- [ ] Limitations are explicit.
- [ ] The paper title matches the actual contribution.

### Reproducibility

- [ ] Every figure generated from committed CSVs.
- [ ] Every table has a source report.
- [ ] Run commands are documented.
- [ ] Configs are included.
- [ ] Split IDs and selected demo IDs are saved.

---

## 13. Bottom line

The current project is scientifically interesting, and the draft is much more credible because it does not hide negative evidence. But for a high-impact ICLR / NeurIPS / ICML paper, you need a stronger final algorithmic result or a sharper benchmark/theory contribution.

The fastest path to a strong paper is:

1. Keep v0.1 as the honest diagnostic foundation.
2. Build v0.2 as a hidden-label-free coverage-risk portfolio selector.
3. Add one benchmark split where bad labels are genuinely useful beyond positive-only NN.
4. Freeze v0.2 and run fresh final splits.
5. Submit only if v0.2 is competitive with or better than the strongest same-backbone baseline across multiple real settings.
