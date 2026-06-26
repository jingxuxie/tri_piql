# TRIAGE-BC Top-Tier Paper Completion Plan

**Project:** TRIAGE-BC / Tri-Signal Offline Imitation  
**Target venues:** ICLR / NeurIPS / ICML  
**Current question:** Do the latest experiments provide enough evidence for a high-impact, top-tier paper? What remains to do?

---

## 0. Executive assessment

You now have enough evidence for a **credible, honest, high-quality empirical paper** if the paper is framed as:

> **When do bad demonstrations help offline imitation?**
> Scarce failure labels are useful, but their value depends on how a learned score is converted into policy-training support under a precision/coverage tradeoff.

You do **not yet** have enough evidence for a strong top-tier **algorithmic dominance** paper claiming that TRIAGE-BC uniformly beats weighted BC, positive-only retrieval, or full offline imitation baselines. The strongest current paper is an empirical/problem-framing paper with a cautious method contribution, not a universal method-SOTA paper.

The latest evidence improves the project significantly:

- v0.2 has a frozen five-split fresh gate and reaches **340/500** selected-branch successes versus **338/500** best completed non-oracle baselines across fresh Can+Lift splits.
- Fresh Can 40p/80b is a positive but modest method result: v0.2 hard union reaches **197/250** versus **192/250** best per-split baselines, with one severe split-404 reversal.
- Lift MG is still a caveat: v0.2 selects weighted BC and gets **143/250** versus **146/250** best completed per-split baselines, winning only two of five splits after the completed five-split v0.1 audit.
- Generated Can diagnostics now show clear regimes where bad-aware support beats matched positive-only retrieval: hard-negative, coverage-shift, and prefix-positive settings.
- The uncertainty intervals for v0.2 still cross zero, so the result should be reported as **directional branch-selection evidence**, not a formal significance win.

**Bottom line:**

- Current evidence is **borderline but promising** for a top-tier empirical study.
- It is **not yet decisive** for a top-tier methods/SOTA paper.
- With 2–4 targeted additions, the paper can become much stronger without requiring huge compute.

---

## 1. What the paper should be

### Recommended final title

**When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study**

This title is better than a method-first title because your results are nuanced. It lets you turn limitations into the core contribution.

### Recommended central thesis

> Scarce success and failure labels can learn useful desirability scores over contaminated offline logs, but the decisive problem is not score learning alone. The decisive problem is converting scores into policy-training support under a precision/coverage tradeoff. Bad demonstrations help in identifiable regimes—prefix positives, hard negatives, and coverage shift—but strong positive-only retrieval and soft weighted coverage remain first-class baselines.

### Recommended contribution framing

The paper should claim four things:

1. **Problem formulation:** Offline imitation from scarce successes, scarce failures, and mixed logs is a score-to-support conversion problem.
2. **Mechanism evidence:** Controlled PointNav and generated Can probes isolate regimes where failure labels provide useful information beyond positive-only learning.
3. **Benchmark evidence:** Frozen Robomimic Can/Lift endpoints show that no single converter is universally best; hard support, positive-only retrieval, and weighted coverage each win in different regimes.
4. **Method evidence:** TRIAGE-BC v0.2 is a frozen hidden-label-free portfolio router with barely positive fresh Can+Lift branch-selection evidence; it reduces regret versus positive-only and weighted fixed branches, ties the completed always-hard-support branch on Can+Lift, and should not be presented as fixed-branch dominance.

### Claims to avoid

Do not claim:

- Bad labels are always necessary.
- TRIAGE-BC uniformly beats weighted BC.
- TRIAGE-BC uniformly beats positive-only retrieval.
- Full inverse-Q / Tri-PIQL actor extraction is validated on real robotics.
- Support purity alone predicts policy success.
- v0.2 is statistically decisive based on the current five-split fresh gate.

---

## 2. Current evidence audit

### 2.1 Strong evidence already in hand

#### Controlled PointNav mechanism

Status: **strong**.

Use this as the cleanest mechanism figure. With only 2 positive route-prefix demos and 2 bad shortcut demos, TRIAGE gap support reaches perfect success at all tested contamination levels. This cleanly shows why failure labels can help when positives are incomplete.

Main role in paper:

- Figure 2 / Table 1.
- Mechanism demonstration, not final robotics evidence.

What to do next:

- Do not spend more compute here.
- Only polish the figure and make the split construction crystal clear.

#### Primary frozen Robomimic v0.1 matrix

Status: **useful but caveated**.

Key current reading:

- Can 40p/80b: TRIAGE-BC beats weighted BC and all-demo, but loses to positive-only NN.
- Lift MG: weighted BC is strongest non-oracle; TRIAGE-BC is below weighted and positive-only.

Main role in paper:

- Establish precision/coverage tradeoff.
- Show why strong baselines matter.
- Motivate v0.2 portfolio selection.

What to do next:

- Keep this table, but do not use it as the main method-win table.
- Use it as the **evidence that the problem is real and nuanced**.

#### Generated Can diagnostics

Status: **very valuable mechanism evidence**.

You now have three targeted generated diagnostics:

1. **Hard-negative Can:** bad-aware hybrid reaches 104/150 vs positive-only 91/150.
2. **Coverage-shift Can:** bad-aware hybrid reaches 120/150 vs positive-only 103/150.
3. **Prefix-positive Can:** bad-aware prefix support reaches 119/150 vs positive-only 6/150.

Main role in paper:

- These are your strongest robotics-adjacent evidence that bad labels can genuinely help.
- Frame them as **regime probes** or **controlled Robomimic split constructions**, not as default benchmark rows.

What to do next:

- Completed on 2026-06-25: add one concise main-paper table summarizing these three probes. The table is `tab:regime-probes`, backed by `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`.
- Put full split construction details in appendix.
- Make clear that hidden labels are used only to construct/evaluate the split, not to select support inside the method.

#### v0.2 fresh Can+Lift gate

Status: **promising but not decisive**.

Current v0.2 gate:

- Can 40p/80b: selected hard union 197/250 vs 192/250 best per-split baselines.
- Lift MG: selected weighted branch 143/250 vs 146/250 best completed per-split non-oracle baselines.
- Combined: 340/500 vs 338/500.
- Paired-bootstrap intervals cross zero.

Main role in paper:

- Evidence that a hidden-label-free branch selector is plausible.
- Not enough by itself to claim statistically decisive method superiority.

What to do next:

- The five-split fresh gate is now complete; do not describe the current
  weakness as an “only three split seeds” issue.
- If more GPU budget is spent, run optional fresh all-demo/all-positive
  diagnostics or pursue a stronger non-Can endpoint row, but keep those
  separate from the current selected-vs-strong-baseline/v0.1 audit.
- Present v0.2 as **portfolio-regret reduction and risk-control evidence**,
  not as “TRIAGE always wins.”

---

## 3. The biggest current weaknesses

### Weakness 1: v0.2 may look like a router over baselines

On Lift, v0.2 selects weighted BC. Reviewers may say: “Your method picks a baseline on the task where your hard-support method fails.”

Mitigation:

- Present v0.2 as a **portfolio router**, not as a single hard-support algorithm.
- Evaluate it using **router regret** against fixed branch policies.
- Include fixed-branch baselines:
  - always positive-only NN,
  - always weighted BC,
  - always hard union,
  - v0.1 router,
  - v0.2 router,
  - oracle branch selector, audit only.

The key table should ask:

> Across heterogeneous regimes, does the frozen hidden-label-free router achieve lower regret than any fixed branch?

### Weakness 2: five split seeds still leave weak margins

The fresh v0.2 gate is now expanded to five split seeds, but the combined
margin is only `340/500` versus `338/500` and all paired-bootstrap intervals
cross zero. This does not invalidate the result, but it weakens a top-tier
methods claim.

Mitigation:

- Keep the five-split audit as directional branch-selection evidence rather
  than a significance claim.
- Report split-level signs, paired initial-state bootstrap, and exact endpoint
  counts.
- Treat additional compute as optional diagnostics unless it targets a concrete
  weakness: fresh all-demo/all-positive controls, a higher-success non-Can
  bad-label win, or a better policy-quality proxy.

Completed A1 run set:

- Can 40p/80b split seeds 404 and 505:
  - v0.2 selected hard union,
  - positive-only NN,
  - weighted BC.
- Lift MG split seeds 404 and 505:
  - weighted BC,
  - positive-only NN.

Optional if compute remains:

- Fresh all-demo BC, clearly labeled as diagnostic.
- Fresh all-positive oracle, clearly labeled as audit-only diagnostic.
- Additional non-Can endpoint evidence if it can improve absolute success
  beyond the low-success Lift hard-negative probe.

### Weakness 3: generated diagnostics are strong but may be seen as hand-designed

Hard-negative, coverage-shift, and prefix-positive Can are highly useful, but they are generated split constructions. Reviewers may worry that they were designed after seeing failures.

Mitigation:

Create a clear **TRI-Signal Regime Probe Suite** section:

- Define each split generator formally.
- State the hypothesis before reporting results.
- Use fresh split seeds.
- Include a negative-control regime where bad labels should not help much.
- Separate these probes from default Robomimic benchmark rows.

Recommended wording:

> These generated split constructions are not intended to replace default benchmark rows. They isolate causal regimes in which failure labels should or should not add information beyond positive-only retrieval.

### Weakness 4: support purity is not enough

You already show this well. Lift MG and Can 80p/80b show that purer support can underperform broader support.

Mitigation:

Make this a central result:

- Plot endpoint success against hidden-positive recall and hidden-bad admission.
- Include both success and average trajectory length / failure mode summaries.
- Add a “purity is insufficient” table:
  - Lift classifier top160: high purity but low success.
  - Can 80 split 33: TRIAGE higher purity but lower success than positive-only NN.
  - Can MG: likelihood proxy picks all-positive, but weighted is rollout-best.

### Weakness 5: the paper could be perceived as underclaiming novelty

The honest framing is scientifically good, but top-tier papers still need a sharp contribution.

Mitigation:

The novelty should be:

- the **problem setting**: scarce successes + scarce failures + mixed offline logs;
- the **precision/coverage decomposition**;
- the **regime-probe suite**;
- the **portfolio-router evaluation** with abstention;
- the strong negative results showing why naïve score filtering fails.

Do not rely solely on endpoint SOTA.

---

## 4. Additional experiments to run

### Priority A: Minimal must-do experiments for a top-tier submission

These are the highest return experiments under a one-4090 budget.

#### A1. Expand the v0.2 fresh gate to five split seeds

Goal:

- Completed: remove the original “only three split seeds” weakness.
- Current question: whether the resulting five-split evidence is strong enough
  for a methods claim. It is not; the margin is barely positive and intervals
  cross zero.

Status as of 2026-06-26:

- Complete. The fresh gate now covers split seeds `101/202/303/404/505`.
- Can 40p/80b selected hard union reaches `197/250` versus `192/250` best
  completed per-split baselines.
- Lift MG selected weighted BC reaches `143/250` versus `146/250` best
  completed per-split baselines.
- Combined Can+Lift selected branches reach `340/500` versus `338/500`.
- The combined paired-bootstrap interval is `[-0.074, 0.120]`, so this is
  directional evidence rather than statistical significance.

Report:

- Pooled success over 250 Can rollouts and 250 Lift rollouts.
- Split-level deltas.
- Paired initial-state bootstrap.
- Router regret relative to best branch.

Success criterion:

- Can selected branch is best or tied-best on enough splits to support a
  cautious Can result, but split `404` is a severe reversal.
- Combined Can+Lift v0.2 is barely positive over the best per-split completed
  baseline, but it ties the completed always-hard-support branch on Can+Lift.
- Lift remains weak: frame it as “router selects broad coverage, but Lift
  remains a caveat.”

#### A2. Build the router-regret table

Goal:

Make v0.2 look like a principled portfolio method rather than a post-hoc combination of baselines.

Status as of 2026-06-26:

- First A2 artifact is staged in `results/final_paper_v02/tables/v02_router_regret_REPORT.md`.
- Completed Can+Lift regret to the audit-only oracle branch selector is `23/500` for v0.2, versus `64/500` for always positive-only NN and `62/500` for always weighted BC.
- Generated Can probes show zero regret for bad-aware hard support on hard-negative, coverage-shift, and prefix-positive settings.
- This table is still not a complete fixed-branch leaderboard because some fixed
  branches remain unrun outside their relevant regimes. Fresh Lift v0.1 is
  complete; fresh Can v0.1 is now complete across split seeds
  `101/202/303/404/505` at `171/250`, with regret `38/250` to the completed
  Can oracle. Combined fresh Can+Lift v0.1 is `314/500`, with regret `49/500`.

Rows:

- Always positive-only NN.
- Always weighted BC.
- Always hard union / hard support.
- v0.1 TRIAGE-BC.
- v0.2 router.
- Oracle branch selector, audit only.

Columns:

- Can 40p/80b.
- Lift MG.
- Hard-negative Can.
- Coverage-shift Can.
- Prefix-positive Can.
- Can MG abstention/stress.
- Combined success.
- Regret to oracle branch.

Important:

- If a branch is not applicable, mark it as N/A and explain why.
- If v0.2 abstains, count abstention separately from failure.
- The table should reward “knowing when not to choose” on Can MG.

#### A3. Complete the main baseline matrix for v0.2 fresh splits

Goal:

Avoid reviewer objections that the fresh v0.2 gate is missing easy baselines.

Status as of 2026-06-26:

- Fresh Can v0.1 TRIAGE-BC splits `101`, `202`, `303`, `404`, and `505` are
  now trained and evaluated with the same official BC-RNN-GMM 200-epoch /
  50-rollout endpoint budget.
- Per-split v0.1 endpoint counts are `28/50`, `36/50`, `35/50`, `36/50`, and
  `36/50`; the completed fresh Can v0.1 row is `171/250`.
- The A2 router-regret table now records this as a complete Can v0.1 row:
  `171/250` with regret `38/250` to the completed Can oracle.
- There are no remaining fresh Can v0.1 A3 gaps.
- The fresh baseline coverage audit
  `results/final_paper_v02/tables/v02_fresh_baseline_coverage_REPORT.md`
  records required branch-selection rows as `7/7` complete and optional
  fresh all-demo/all-positive diagnostic rows as `0/4` run. Do not imply those
  optional diagnostics are completed fresh-gate evidence unless they are run.

Minimum baselines:

- all-demo BC,
- positive-only NN,
- weighted BC,
- v0.1 TRIAGE branch,
- v0.2 selected branch,
- all-positive oracle, diagnostic only.

If compute is tight:

- all-demo BC can be run only on the 3 original fresh seeds if already absent.
- all-positive oracle can be run on fewer splits but should be clearly diagnostic.

#### A4. Pre-register generated regime probes

Goal:

Convert generated diagnostics from “interesting ablations” into a coherent empirical contribution.

Status as of 2026-06-25:

- Created `REGIME_PROBE_SUITE.md` as a paper-facing registry for completed
  generated diagnostics and negative-control regimes.
- The registry is intentionally honest: completed probes are marked as
  completed evidence, not retroactive fresh pre-registration, and future
  variants must be added before endpoint training to support new fresh claims.

Create a file:

```text
REGIME_PROBE_SUITE.md
```

For each probe, write:

- motivation,
- split construction,
- hidden labels used only for split construction/evaluation,
- expected winner,
- methods compared,
- split seeds,
- endpoint budget,
- claim allowed if result passes.

Probes:

1. Prefix-positive regime.
2. Hard-negative regime.
3. Coverage-shift regime.
4. Default Can contamination regime.
5. Lift broad-coverage regime.
6. Can MG ambiguous plateau / abstention regime.

This will make the paper feel like a systematic study rather than a list of post-hoc diagnostics.

---

### Priority B: Strongly recommended analyses

#### B1. Precision/coverage frontier across all regimes

Status: **staged as a paper artifact** in
`results/final_paper/tables/precision_coverage_frontier_REPORT.md` and
`results/final_paper/figures/precision_coverage_frontier.pdf`. The current
artifact includes the requested regimes plus the prefix-positive Can probe.

For each regime, plot candidate supports in a common space:

- x-axis: hidden-positive recall,
- y-axis: hidden-bad admission,
- point size or label: endpoint success,
- marker shape: method family.

Regimes to include:

- Can 40p/80b,
- Can 20p/80b,
- Can 80p/80b,
- hard-negative Can,
- coverage-shift Can,
- Lift MG.

Purpose:

Show that the same support statistics explain when bad-aware support helps and when it fails.

#### B2. Policy-quality proxy no-go table

Status: **staged as a paper artifact** in
`results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md` and
`results/final_paper/tables/policy_quality_proxy_no_go.csv`. The consolidated
table has 17 rows across likelihood, contrastive likelihood, negative
rejection, support-purity, hidden-positive-recall, coverage, and
initial/transition-coverage proxies; deployable proxy attempts match endpoint
winners in `2/11` rows, audit-only support rows match `3/6`, and original Can
MG likelihood-style proxies match `0/6`.

You already have evidence that simple proxies fail. Make it a main appendix table.

Include:

- positive likelihood,
- positive-minus-negative likelihood,
- negative rejection,
- support purity,
- hidden-positive recall, audit only,
- coverage proxy,
- actual endpoint winner.

Message:

> Policy-quality prediction is the unsolved problem. A score that separates positives and negatives is not enough.

#### B3. Component ablation of hard union

Status: **staged as a paper artifact** in
`results/final_paper/tables/hard_union_component_ablation_REPORT.md`,
`results/final_paper/tables/hard_union_component_ablation.csv`, and
`results/final_paper/tables/hard_union_component_ablation_per_split.csv`.
The table reports the requested components. The union reaches `116/150`, versus
positive-only NN top40 `108/150`, risk-fusion top40 `73/100` on its two
evaluated splits, weighted BC `90/150`, and v0.1 adaptive masscap `99/150`;
classifier-only top40 is support-only and dominated by positive-only support.
The current answer is that the union helps by preserving the positive-only
anchor while adding risk-derived coverage, with the pooled gain coming from
split 22 and split 33 rather than uniform dominance.

For the v0.2 Can hard union, report:

- positive-only NN top40,
- risk-fusion top40,
- union top40,
- classifier-only top40,
- weighted BC,
- v0.1 adaptive masscap.

You do not need to train every candidate on every new seed if support-only results are clear, but endpoint evidence for the main candidates is important.

Key question:

> Does the union help because it adds coverage, because it removes bad actions, or because it combines both?

#### B4. Failure-mode rollouts

Status: **staged as a lightweight appendix artifact** in
`results/final_paper/tables/failure_mode_initial_states_REPORT.md`,
`results/final_paper/tables/failure_mode_initial_states_cases.csv`, and
`results/final_paper/tables/failure_mode_initial_states.csv`. The audit reuses
existing paired Can 40p/80b endpoint rollouts and selects three representative
initial states: split `33` / `demo_105` is a hard-union rescue (`5/5` union
versus `0/5` positive-only and `0/5` all-demo), split `11` / `demo_39` is a
positive-anchor regression (`5/5` positive-only versus `0/5` union), and split
`33` / `demo_99` is a soft-pool rescue (`5/5` weighted versus `1/5` union).
The object-grasp and loop/miss fields are clearly marked as success and
horizon-length proxies, not video-level labels.

For 2–3 representative initial states, compare:

- positive-only NN,
- weighted BC,
- v0.2 hard union,
- all-demo BC.

Report simple qualitative metrics:

- success/failure,
- average trajectory length,
- whether object was grasped,
- whether policy loops or misses can,
- whether failure resembles bad demos.

This can be lightweight and appendix-only, but it improves reviewer intuition.

#### B5. Split-construction robustness

Status: **staged as a support-only appendix artifact** in
`results/final_paper/tables/can_prefix_length_robustness_REPORT.md`,
`results/final_paper/tables/can_prefix_length_robustness.csv`, and
`results/final_paper/tables/can_prefix_length_robustness_all_candidates.csv`.
This varies the generated Can prefix-positive label length while holding split
seeds `101/202/303`, label budget, and top80 support size fixed. Bad-aware
state top80 clears matched prefix positive-NN top80 for short/default/long
prefixes: hidden-positive recall deltas are `+0.400`, `+0.658`, and `+0.737`,
while hidden-bad admission deltas are `-0.400`, `-0.658`, and `-0.737`. This is
support-only construction robustness, not a new endpoint result.

For generated probes, vary one design parameter:

- hard-negative ratio,
- positive-prefix length,
- coverage-shift severity,
- number of bad labels.

Do support-only sweeps first. Run endpoint only for one or two informative settings.

---

### Priority C: Optional if you want a stronger methods submission

#### C1. Add one non-Can manipulation task where bad labels help

Status: **support-only plus three full-budget endpoint splits staged** in
`results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md`,
`results/final_paper/ablations/lift_hard_negative_action_conflict_summary.csv`,
`results/final_paper/ablations/lift_hard_negative_action_conflict_support_per_split.csv`,
`results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/REPORT.md`,
`results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/REPORT.md`,
`results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/REPORT.md`,
`results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303/REPORT.md`,
and `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.
This generated Lift MG hard-negative/action-conflict audit is the first non-Can
transfer check. Across split seeds `101/202/303`, state-action positive-NN
top40 selects `12/120` hidden positives and admits `108/240` hidden bad demos,
while bad-aware proxy top40 selects `82/120` hidden positives and admits
`38/240` hidden bad demos. A split-101 50-epoch, 10-rollout endpoint smoke is
directionally consistent but weak: bad-aware proxy top40 reaches `2/10`, versus
state-action positive-NN top40 `1/10`. The full-budget split-101/202/303 gate
is directionally positive but weak in absolute terms: bad-aware proxy top40
reaches `15/150`, versus state-action positive-NN top40 `5/150`, with selected
support of `82` hidden positives and `38` hidden bad demos versus `12` hidden
positives and `108` hidden bad demos. This is completed three-split non-Can
mechanism evidence, but it remains a low-success exploratory diagnostic rather
than a primary Robomimic benchmark claim.

The strongest completed generated bad-label wins are still Can-based. For a stronger top-tier methods paper, improve one task family beyond Can.

Candidates:

- Lift generated hard-negative / coverage-shift probe.
- Square or Transport with a quality-sensitive evaluator, not sparse success.
- A simpler low-dimensional manipulation or navigation task where endpoint training is cheap.

Minimum acceptable version:

- Three low-success endpoint splits are not enough for a main result.
- Aim for a non-Can task or evaluator where the endpoint margin has stronger absolute policy quality.

If compute is tight, skip this and frame the paper as a study centered on Can/Lift regime probes.

Next decision:

- The three-split frozen-budget result is positive but weak (`15/150` versus
  `5/150`). Treat it as completed non-Can mechanism evidence, not as a primary
  endpoint win. A stronger methods paper still needs either a higher-success
  non-Can row or a better endpoint-quality proxy.

#### C2. Add active abstention evaluation

Status: **staged as a stress/limitation artifact** in
`results/final_paper/tables/active_abstention_evaluation_REPORT.md`,
`results/final_paper/tables/active_abstention_evaluation.csv`, and
`results/final_paper/tables/active_abstention_assignment_summary.csv`.
Router-v2 abstains on original and shuffled Can MG, where mass/count are
`1947.9`/`1025.7` and `1466.3`/`515.7`. Across the router-v2 audit, assigned
rows average `0.700` fixed-20k success with minimum `0.600`, while abstained
rows average `0.217` and top out at `0.333`. Original-MG proxies match best
success in `0/6` cases; shuffled MG gets `6/6` only because both staged forced
branches reach `0.100`. This supports abstention as risk control, not endpoint
dominance.

For Can MG and other ambiguous score shapes, evaluate whether abstention is useful:

- Does the router abstain on cases where all branches are weak or unstable?
- What is the cost of forcing a branch?
- Does abstention correlate with high estimated mass and high score-plateau ambiguity?

Add a table:

| Setting | Router decision | Best branch | Worst branch | Abstention justified? |

This makes abstention feel intentional rather than evasive.

#### C3. Add theory-lite proposition

Status: **staged in the manuscript theory section** as
`Proposition 1 (coverage-contamination criterion)` in
`paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
`paper/triage_bc_draft.md`. The proposition keeps the existing
precision/coverage equations but names the key condition: add unlabeled support
only when marginal coverage gain exceeds normalized marginal contamination
cost. This is theory-lite framing, not a formal guarantee.

You already have a precision/coverage risk decomposition. Strengthen it with a simple proposition:

> Under a mixed useful/harmful support model, a hard selector improves over weighted cloning when the decrease in harmful imitation mass exceeds the increase in coverage error; soft weighting improves when coverage dominates and harmful actions are weakly conflicting.

This does not need to be a deep theorem. It should explain the empirical reversals.

---

## 5. Recommended final paper structure

### Main paper

1. **Introduction**
   - Offline imitation data is scarce-labeled and mixed.
   - Bad demonstrations may help, but not always.
   - The central problem is score-to-support conversion.

2. **Problem Setting**
   - `D+`, `D-`, `Du`.
   - Offline only.
   - Hidden labels are audit-only.
   - Distinguish default benchmarks from generated regime probes.

3. **TRIAGE-BC and Portfolio Routing**
   - Score model.
   - Trajectory aggregation.
   - Candidate supports.
   - v0.1 and v0.2 routers.
   - Policy backbone: official BC-RNN-GMM.

4. **A Precision/Coverage View**
   - Hidden-good recall vs hidden-bad admission.
   - Weighted effective sample size vs weighted bad mass.
   - Why no single converter wins everywhere.

5. **Controlled Mechanism: PointNav**
   - Prefix positives + bad shortcuts.
   - Perfect success under heavy contamination.

6. **Default Robomimic Results**
   - v0.1 Can/Lift matrix.
   - Strong baselines.
   - Show cross-task reversal.

7. **When Bad Labels Help: Generated Regime Probes**
   - Hard-negative Can.
   - Coverage-shift Can.
   - Prefix-positive Can.
   - Use as the positive evidence that bad labels can add information.

8. **v0.2 Portfolio Router**
   - Fresh Can+Lift gate.
   - Router-regret table.
   - Uncertainty.
   - Abstention on Can MG.

9. **Limitations**
   - Positive-only retrieval is strong.
   - Weighted BC wins broad-coverage settings.
   - Generated probes are targeted constructions.
   - Full inverse-Q remains unvalidated.
   - More tasks/seeds would strengthen the claim.

### Appendix

- Full method freeze contracts.
- Split-generation details.
- All endpoint counts.
- Per-split and per-initial-state bootstrap.
- Support audits.
- Proxy no-go diagnostics.
- Reproducibility map.

---

## 6. What should be main vs appendix

### Main paper

Use these as main:

- PointNav controlled mechanism.
- Primary v0.1 Can/Lift matrix as problem evidence.
- Generated Can regime probes as “when bad labels help.”
- v0.2 fresh gate as portfolio-router evidence.
- Precision/coverage frontier figure.
- Score-shape/abstention figure.

### Appendix only

Keep these appendix-only unless expanded:

- Can 20p/80b partial endpoint diagnostics.
- Can 80p/80b single endpoint diagnostic.
- Can MG branch-proxy failure details.
- Square/Transport support-side results.
- Full checkpoint-selection diagnostics.
- Minari / Tri-PIQL inverse-Q negative results.

---

## 7. Acceptance-readiness criteria

### Ready for a high-quality empirical submission if all are true

- v0.2 fresh gate is complete and documented.
- Generated regime probes are formalized and clearly separated from default benchmark rows.
- Strong baselines are included everywhere:
  - all-demo BC,
  - positive-only NN,
  - weighted BC,
  - v0.1,
  - v0.2,
  - oracle support, audit only.
- The paper reports uncertainty and does not overclaim significance.
- The paper title and abstract emphasize “when bad demos help,” not universal dominance.
- Reproducibility scripts validate all quoted numbers.

### Ready for a top-tier methods/SOTA-style claim only if stronger conditions hold

At least one of these should become true:

1. v0.2 beats every fixed branch across at least 4–5 regimes with stable split-level margins.
2. v0.2 fresh gate remains positive over 5+ split seeds and uncertainty intervals are mostly above zero.
3. A second non-Can task family shows a bad-label benefit over positive-only retrieval.
4. The router learns a validated hidden-label-free policy-quality proxy that predicts hard vs soft winners better than current mass/count heuristics.

If none of these become true, submit as a careful empirical study rather than a methods-dominance paper.

---

## 8. Four-week execution schedule

### Week 1: Freeze and organize

Deliverables:

- `FINAL_CLAIM_CONTRACT.md`. Status: staged and validator-covered.
- `REGIME_PROBE_SUITE.md`. Status: staged and artifact-reference covered.
- Updated `METHOD_FREEZE_V02.md` if no changes are needed, or
  `METHOD_FREEZE_V03.md` if you change the router. Status:
  `METHOD_FREEZE_V02.md` is staged and checked by
  `scripts/validate_method_freeze_v02.py`.
- One master evidence spreadsheet/table generated from artifacts. Status: staged
  as `results/final_paper/tables/submission_readiness_audit_REPORT.md` and
  `results/final_paper/tables/submission_readiness_audit.csv`.
- Updated manuscript outline with exact main/appendix placement.

Rules:

- Do not change the method after looking at new fresh-split endpoint results.
- If you change anything, rename it as a new variant and keep previous results separate.

### Week 2: Fresh-gate extensions

Status: complete as of 2026-06-26.

Completed:

- Can 40p/80b seeds `404/505`:
  - v0.2 selected hard union,
  - positive-only NN,
  - weighted BC.
- Lift MG seeds `404/505`:
  - weighted BC,
  - positive-only NN.
- Fresh Can and Lift v0.1 TRIAGE-BC audits across all five split seeds.
- Updated fresh-gate table, paired bootstrap, baseline-coverage audit, and
  router-regret table.

Decision after the completed runs:

- Do not promote v0.2 as methods/SOTA dominance.
- Use v0.2 as cautious portfolio-router evidence inside the broader
  empirical precision/coverage study.
- Optional fresh all-demo/all-positive rows may improve reviewer comfort, but
  they do not change the current claim boundary unless run and reported as
  diagnostics.

### Week 3: Complete regime-probe analysis

Do not run many new policies unless necessary. Focus on organizing evidence.

Deliverables:

- Main table for hard-negative, coverage-shift, prefix-positive Can. Status: staged as `tab:regime-probes` and `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`.
- Split construction definitions.
- Precision/coverage plots for each regime.
- Support/purity/coverage statistics.
- Optional two extra seeds only if one generated diagnostic looks unstable.

### Week 4: Paper polish and validation

Deliverables:

- Final ICLR/NeurIPS/ICML-format paper.
- All figures regenerated from scripts.
- All numeric claims validated by script.
- Artifact map and reproduction commands.
- One-page reviewer-facing summary of claims and limitations. Status: staged
  as `paper/REVIEWER_CLAIM_SUMMARY.md`.

Final sanity checks:

- Does the abstract avoid “uniformly beats” language?
- Is positive-only NN treated as a serious baseline?
- Is weighted BC treated as a serious baseline?
- Are generated diagnostics clearly labeled as generated regime probes?
- Are hidden labels never used for method decisions?
- Are confidence intervals and split-level variability reported?

---

## 9. Recommended final abstract wording

> Offline imitation datasets often contain scarce trusted successes, scarce known failures, and larger unlabeled logs with mixed behavior. We study when failure demonstrations help policy learning from such logs. Our results show that the key bottleneck is not score learning alone, but converting learned desirability scores into policy-training support under a precision/coverage tradeoff. In controlled PointNav and generated Robomimic Can regime probes, explicit failures help recover useful support when positives are incomplete, hard negatives are action-conflicting, or scarce positives under-cover task variations. In default Robomimic Can and Lift endpoints, however, strong positive-only retrieval and soft weighted BC remain competitive or superior in different regimes. We propose TRIAGE-BC, a score-calibrated support-conversion framework with a frozen portfolio router, and show positive fresh-split branch-selection evidence while highlighting abstention and policy-quality prediction as open challenges. These results argue that future offline imitation methods should treat failure labels, positive-only retrieval, weighted coverage, and abstention as components of a precision/coverage decision rather than as one-size-fits-all alternatives.

---

## 10. Final recommendation

For a top-tier submission, I would pursue the paper as a **high-quality empirical study with a method component**, not as a pure algorithmic SOTA paper.

The safest final message is:

> Bad demonstrations can help offline imitation, but only in regimes where they improve the precision/coverage frontier of the policy-training support. TRIAGE-BC makes this tradeoff explicit, shows where bad labels help, shows where positive-only or weighted coverage wins, and provides a frozen portfolio-router baseline for future work.

That is honest, novel, and much more defensible than claiming universal superiority.
