# Tri-PIQL / TRIAGE-BC Paper Completion Plan

**Project:** Offline imitation / inverse reward learning from scarce successful demonstrations, scarce failure demonstrations, and a large mixed-quality offline log  
**Working paper title:** **When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study**
**Recommended framing:** offline imitation / reward-score learning, not yet full inverse-Q IRL on robotics  
**Date:** 2026-06-26

---

## 0. Executive diagnosis

You are mostly doing the right thing, but the paper should be reframed.

The current evidence supports the following claim:

> Scarce successful and failed demonstrations can calibrate a desirability score over a mixed offline log. The main algorithmic problem is not only learning the score, but converting the score into policy-training data: sometimes high-precision hard support wins, sometimes broader soft weighting is needed, and ambiguous score shapes should be abstained from unless a validated policy-quality proxy is available.

The current evidence **does not yet support** the stronger claim:

> A full inverse-Q / Tri-PIQL actor-extraction method beats all strong baselines on real robotics or continuous-control tasks.

The safest high-impact paper is therefore not “we solved offline IRL with bad demonstrations.” It is:

> **We identify and solve a neglected precision/coverage problem in offline imitation from scarce successes, explicit failures, and mixed logs.**

This is a good paper direction because it is specific, reproducible on one RTX 4090, and directly relevant to real offline data where unlabeled logs are contaminated.

Current status as of 2026-06-26:

- The paper-facing package is now internally consistent as a diagnostic / benchmark-style precision-coverage paper. The current pre-submission gate,
  `make -C paper validate`, regenerates staged artifacts, compiles the standalone
  and provisional ICLR PDFs, and passes the claim, structure, artifact-reference,
  and v0.2 method-freeze validators.
- The submission-readiness audit marks the high-quality empirical submission
  criteria as green (`6` pass, `0` caution), while top-tier methods/SOTA
  dominance remains explicitly not met (`1` caution, `5` not met).
- The latest action-risk v0.2 candidate improves support purity but fails the endpoint gate: positive-NN/risk fusion reaches `0.820` versus positive-only NN `0.840` on Can 40p/80b split 11, and `0.640` versus `0.760` on split 22.
- A follow-up union candidate that keeps positive-only NN support and adds risk-fusion demos improves the pooled Can 40p/80b endpoint row to `116/150`, versus positive-only NN `108/150`, TRIAGE-BC v0.1 `99/150`, and weighted BC `90/150`. This is promising Can-only development evidence, but it is not a frozen v0.2 because it loses split 11 to positive-only NN and does not address Lift MG or Can MG.
- A follow-up mass/count portfolio-router audit chooses hard union for low-mass Can rows, soft weighted BC for Lift, and abstention for Can MG. It reaches `209/300` over the two primary development endpoints versus `201/300` for the strongest pre-union per-task baselines and `173/300` for v0.1. This is the development shape that was frozen into v0.2; after completing all five A3 Lift v0.1 audit rows, the five-split fresh Can+Lift gate now reaches `340/500` versus `338/500`.
- The fresh frozen Can 40p/80b branch is now complete over five splits for the
  predeclared v0.2 router: hard union reaches `197/250` versus `192/250` for
  the strongest completed non-oracle baselines, winning 4/5 splits but losing
  split `404` by `12/50`.
- The fresh frozen Lift MG branch is also complete over five splits for the
  predeclared v0.2 router: selected weighted BC reaches `143/250` versus
  the best completed per-split baseline at `146/250`, winning 2/5 completed
  comparisons after completing all five v0.1 TRIAGE hard-support audit rows.
  This supports cautious branch-selection framing rather than a decisive
  new-method claim because the selected Lift branch is a strong baseline.
- Combined across fresh Can 40p/80b and Lift MG, the selected v0.2 branches
  reach `340/500` versus `338/500` for the best completed non-oracle baseline
  per split.
- The strongest evidence for explicit bad labels is now controlled PointNav plus
  generated Can hard-negative, coverage-shift, and prefix-positive diagnostics.
  The non-Can Lift hard-negative/action-conflict endpoint diagnostic is complete
  over split seeds `101/202/303` and is directionally positive (`15/150` versus
  `5/150`), but absolute success is low, so it remains exploratory C1 mechanism
  evidence rather than a primary endpoint claim.
  The primary frozen Robomimic rows still require strong caveats.
- A follow-up Candidate V output-anchor fine-tune and Candidate W two-feature
  weighted-rescue gate did not create a methods-dominance path. Candidate W
  ties Candidate E at `85/100` over Can splits `404` and `505`, but still loses
  split `505` to positive-only (`39/50` versus `40/50`). The paper should not
  promote another scalar initial support-distance/margin router as a new
  method.
- A follow-up extra-only negative-action hinge also failed the fast gate:
  `14/20` on Can split `404`, below Candidate C sequence-mask `16/20` and
  positive-only `17/20`. This closes the current nearest-negative hinge recipe
  as a methods path.
- The current candidate-breakthrough decision audit should be treated as
  claim-boundary evidence: Candidate F is a scoped Can discovery (`198/250`)
  but failed fresh validation (`81/100` versus `84/100` best completed
  baselines), and later output-anchor, two-feature rescue, and transition-level
  variants did not clear their first validation checks.
- The follow-on SOTA-candidate sweep in
  `triage_bc_sota_candidate_plan.md` is now complete at the short-screen level.
  The aggregate report is
  `results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md`. No branch clears its
  first-stage gate: the best Can404 endpoint branches reach `16/20` versus the
  matched positive-only anchor at `17/20`, CCG transfer reaches `10/20` on
  Lift707 versus positive-only `12/20`, and anchored IQL-AWBC reaches only
  `13/20`.
- A later CAU-alone five-split endpoint follow-up is stronger than the first
  short screen suggested: CAU action-conflict reaches `193/250` on Can, versus
  positive-only `174/250`, weighted BC `158/250`, TRIAGE-BC v0.1 `171/250`,
  best old baseline per split `192/250`, and v0.2 selected union `197/250`.
- A post-hoc CAU-plus-v0.2 portfolio preflight reaches `208/250` by selecting
  CAU on splits `303/404/505` and v0.2 on `101/202`. It was the best
  pre-fresh-validation method-search hypothesis, but it was selected on the
  same five endpoint splits and cannot be a method result by itself.
- The first fresh validation of that CAU-plus-v0.2 setup gate on Can split606
  is negative: the fitted gate selects CAU, but CAU reaches `15/20` versus
  positive-only `16/20`; frozen v0.2 union reaches `14/20`, and the cleaner
  risk-fusion diagnostic reaches `15/20`. A proper expanded-mask CAU check
  that trains on the full 130-demo transition-weight filter reaches only
  `12/20`, closing the hypothesis that the split606 failure was just a
  training-filter mismatch.
- A GMM-confidence CAU router follow-up is not the missing selector: split606
  labeled q25 calibration is neutral (`16/20`), a post-hoc split606 threshold
  reaches `18/20`, but the frozen threshold fails unused split707 (`15/20`,
  opening no CAU episodes). CAU-alone is the important signal on split707:
  `20/20` first-20 and `50/50` at 50 episodes versus positive-only `36/50` and
  weighted BC `39/50`. The next fixed-CAU split808 validation is negative:
  `38/50` versus positive-only `43/50` and Candidate E `42/50`.
- A leave-one-split-out CAU selector feature audit confirms that simple initial
  support-distance features are not the missing selector. Across audited Can
  splits, positive-only is `269/370`, always-CAU is `296/370`, and oracle
  switching is `331/370`, but the safe held-out selector reaches only
  `263/370` while the best-delta selector reaches `277/370` with `23` losses.
- A first-state policy-distribution selector audit is stronger but still not
  deployable. Across the same completed splits, the safe held-out selector
  reaches `276/370` with `29` gains and `22` losses, and the best-delta selector
  reaches `299/370` with `44` gains and `14` losses. Its pooled frozen rule is
  neutral on fresh split909: `15/20` routed versus `15/20` positive-only and
  `9/20` CAU-alone, opening `0` CAU episodes.
- A linear learned router over those policy features is also negative:
  leave-one-split-out safe reaches `277/370` and best-delta `278/370`, both
  with `17` positive-only losses. Freezing the learned router from completed
  splits to split909 opens all CAU starts and falls to `9/20`.
- A per-step support-margin router is the first sequence-aware CAU follow-up
  with a consistent short-screen gain: fixed threshold `0.05` reaches `51/60`
  across splits 909/808/707 versus positive-only `47/60` and CAU-alone
  `43/60`, with `5` gains and `1` loss versus positive-only. The first
  no-retune held-out guardrail on split606 is neutral (`16/20` router versus
  `16/20` positive-only and `15/20` CAU), but the 50-episode split606
  validation is positive (`42/50` router versus `38/50` positive-only and
  `41/50` CAU). The next 50-episode split101 check is mixed-negative (`25/50`
  router versus `19/50` positive-only and `33/50` CAU), so the two 50-episode
  validations aggregate to `67/100` router versus `57/100` positive-only but
  below CAU `74/100`. A naive persistent support-margin variant is worse on
  split101 (`20/50`), so committing harder after repeated support-margin
  evidence is not enough.
- The current support-margin router remains a useful sequence-aware diagnostic,
  not a method claim. The strongest paper path remains the precision/coverage
  study unless a better router captures CAU-dominant splits without losing the
  positive-only anchor.

---

## 1. What your current results already support

### 1.1 Strong supported claims

You can currently defend these claims:

1. **Naively cloning contaminated logs is bad.**  
   Your PointNav all-data BC degrades from 0.460 to 0.153 as bad fraction rises from 50% to 95%, and Robomimic all-demo cloning is weak on Lift MG and Can MG.

2. **Scarce success/failure labels can learn a useful desirability score.**  
   Continuous PointNav score-gap demo BC reaches 1.000 success at 50%, 75%, 90%, and 95% bad unlabeled data. Robomimic Can paired 80p/80b reaches 0.962 purity and 0.900 success at 20k with official BC-RNN-GMM.

3. **Score-to-policy conversion matters.**  
   Fixed top-k, score-gap, mass-capped support, pos-min thresholding, and soft weighted sampling behave differently across contamination and coverage regimes.

4. **Hard support can beat weighted BC, but not always.**  
   Can 40p/80b favors hard support over weighted BC under the frozen endpoint protocol, while fresh frozen Lift MG favors weighted BC and Can MG sparse remains a modest-success weighted/abstention stress case.

5. **Bad labels help calibration/stability, but are not universally necessary.**  
   Positive-only nearest-neighbor is a strong baseline on Can 40p/80b and must remain in the main paper.

6. **The current real-robotics evidence is a selector + strong BC-backbone result.**  
   The official Robomimic BC-RNN-GMM backbone is doing the final policy learning. The novelty is the tri-signal scoring and score-to-support conversion.

7. **Support-side purity is not enough to select a policy-training set.**
   The v0.2 action-risk support candidates can look better under hidden-label audits but still trail positive-only NN endpoints. This should be a visible no-go result, not hidden as failed development work.

### 1.2 Claims to avoid

Do **not** claim:

- “Weighted BC is weak.”
- “Hard filtering always wins.”
- “Bad labels are strictly required.”
- “Full Tri-PIQL / inverse-Q actor extraction is validated on Robomimic.”
- “Best checkpoint proves the method.”
- “Ten rollout episodes are enough for final statistical claims.”
- “The current action-risk candidate is TRIAGE-BC v0.2.”
- “Square/Transport are failure-demo benchmarks.” They are currently relative-quality support diagnostics.

---

## 2. Main paper objective

### 2.1 Problem setting

You observe three offline trajectory sets:

$$
\mathcal D^+ = \{\tau_i^+\}_{i=1}^{n_+}, \qquad
\mathcal D^- = \{\tau_i^-\}_{i=1}^{n_-}, \qquad
\mathcal D^u = \{\tau_i^u\}_{i=1}^{n_u}.
$$

- $\mathcal D^+$: scarce known successful / desirable demonstrations.
- $\mathcal D^-$: scarce known failed / undesirable demonstrations.
- $\mathcal D^u$: large unlabeled mixed-quality log containing hidden useful and harmful behavior.
- No online training interaction is allowed.
- True rewards are not used by the method, except for evaluation or oracle diagnostics.

### 2.2 Paper question

> How should an offline imitation learner use scarce successes and failures to extract useful policy-training support from a contaminated mixed log?

### 2.3 Proposed thesis

> Learning a desirability score is not enough. The bottleneck is converting the score into a policy-training distribution under a precision/coverage tradeoff. We propose a hidden-label-free tri-signal converter that adapts between high-precision support and broader coverage, and abstains on ambiguous score shapes where no reliable policy-quality proxy is available.

---

## 3. Proposed method: TRIAGE-BC

Use a new name for the paper-facing method. I recommend **TRIAGE-BC**:

**TRIAGE-BC = TRI-signal Adaptive Good-support Estimation for Behavior Cloning**

This name is more accurate than “Tri-PIQL” for the current robotics evidence because the final policy learner is BC-RNN-GMM over selected/weighted support.

### 3.1 Method overview

TRIAGE-BC has four stages:

1. **Tri-signal score learning**
2. **Trajectory-score calibration**
3. **Hidden-label-free support conversion**
4. **Support-constrained policy learning**

### 3.2 Stage 1: learn a state-action desirability model

Train a classifier or reward-score model:

$$
c_\theta(s,a) \in [0,1]
$$

with positive transitions labeled 1 and bad transitions labeled 0:

$$
\mathcal L_{\text{score}}
=
-\mathbb E_{(s,a)\sim \mathcal D^+}\log c_\theta(s,a)
-\mathbb E_{(s,a)\sim \mathcal D^-}\log(1-c_\theta(s,a)).
$$

Use held-out labeled positives/negatives only for calibration diagnostics, not for final rollout selection.

Recommended implementation:

- For Robomimic: use the existing state-action classifier, but save logits, probabilities, and per-demo score summaries.
- For PointNav: keep the existing neural score model.
- Save score histograms for $\mathcal D^+$, $\mathcal D^-$, and $\mathcal D^u$.

### 3.3 Stage 2: aggregate to trajectory scores

For each trajectory $\tau$, compute:

$$
g(\tau) = \frac{1}{|\tau|}\sum_t c_\theta(s_t,a_t).
$$

Also log robustness features:

$$
g_{\min}(\tau), \quad g_{p10}(\tau), \quad g_{\text{mean}}(\tau), \quad g_{p90}(\tau).
$$

The paper-facing method should start with mean score because it matches the current results, but diagnostics should report whether p10/min scores better detect trajectories with short failure segments.

### 3.4 Stage 3: estimate positive mass in the unlabeled log

Let

$$
\mu_+ = \frac{1}{|\mathcal D^+|}\sum_{\tau\in \mathcal D^+} g(\tau), \qquad
\mu_- = \frac{1}{|\mathcal D^-|}\sum_{\tau\in \mathcal D^-} g(\tau).
$$

Estimate unlabeled positive mass:

$$
\hat m
=
\sum_{\tau\in\mathcal D^u}
\mathrm{clip}
\left(
\frac{g(\tau)-\mu_-}{\mu_+-\mu_-+\epsilon},
0,
1
\right).
$$

This is already close to your current mass-capped selector. Keep it.

### 3.5 Stage 4: hidden-label-free support conversion

Generate a small set of candidate policy-training distributions.

Let $n_+ = |\mathcal D^+|$.

**Candidate A: precision support**

$$
S_{\text{prec}} = \text{top}_{2n_+}(\mathcal D^u; g).
$$

This is useful under heavy contamination.

**Candidate B: mass-capped adaptive support**

1. Compute a score-gap threshold on sorted $g(\tau)$.
2. Let the selected set be $S_{\text{gap}}$.
3. If $|S_{\text{gap}}| > 1.25\hat m$, replace it by $\text{top}_{\lceil \hat m\rceil}$.
4. If $\hat m < \max(\text{abs\_min}, 4n_+)$, fall back to $S_{\text{prec}}$.

This is the current strongest hard-support rule.

**Candidate C: pos-min support**

Let $q^+_{10}$ be the 10th percentile of labeled-positive trajectory scores.

$$
S_{\text{pos-min}} = \{\tau\in\mathcal D^u: g(\tau)\ge q^+_{10}\}.
$$

This is strong on Lift MG.

**Candidate D: soft weighted sampler**

Train on $\mathcal D^+\cup\mathcal D^u$ with weights:

$$
w(\tau)=
\mathrm{clip}
\left(
\frac{g(\tau)-\mu_-}{\mu_+-\mu_-+\epsilon},
0,
1
\right)^\alpha.
$$

Use $\alpha=1$ as the default. Include $\alpha\in\{0.5,1,2\}$ as an ablation only.

**Candidate E: abstain**

If the score shape is ambiguous and no validated proxy predicts rollout quality, the method should abstain rather than force a branch.

Current router-v2 abstention rule:

- Abstain if calibrated positive mass is very large and the count above labeled-positive minimum is very large.
- Otherwise use `hard_pos_min` if labeled-positive p10 is high and enough unlabeled demos exceed the positive-min threshold.
- Otherwise use `hard_adaptive_masscap`.

This rule is usable as a method candidate, but it looks post-hoc. Freeze it immediately and test it on fresh splits before calling it the final algorithm.

### 3.6 Stage 5: train the policy

For Robomimic:

- Use official Robomimic BC-RNN-GMM.
- Same actor MLP head across methods.
- Same sequence length.
- Same optimizer budget.
- Same checkpoint reporting schedule.
- No hidden labels in training or selection.

Train on:

$$
\mathcal D_{\text{train}} = \mathcal D^+ \cup S
$$

for hard-support branches, or weighted sampling over $\mathcal D^+\cup\mathcal D^u$ for soft branch.

### 3.7 Method pseudocode

```python
def TRIAGE_BC(D_pos, D_neg, D_unlabeled, config):
    # 1. Score learning
    scorer = train_state_action_classifier(D_pos, D_neg)

    # 2. Demo-level scoring
    score_pos = score_demos(scorer, D_pos)
    score_neg = score_demos(scorer, D_neg)
    score_u = score_demos(scorer, D_unlabeled)

    mu_pos = mean(score_pos)
    mu_neg = mean(score_neg)
    q10_pos = percentile(score_pos, 10)

    # 3. Calibrated positive mass
    p_u = clip((score_u - mu_neg) / (mu_pos - mu_neg + 1e-8), 0, 1)
    m_hat = sum(p_u)

    # 4. Candidate branch selection
    count_above_pos_min = count(score_u >= q10_pos)

    if router_v2_abstains(m_hat, count_above_pos_min, len(D_unlabeled)):
        return Abstain(score_report=True)

    if should_use_pos_min(q10_pos, count_above_pos_min):
        S = {tau for tau in D_unlabeled if score(tau) >= q10_pos}
        branch = "hard_pos_min"
    else:
        S = adaptive_masscap(score_u, m_hat, n_pos=len(D_pos))
        branch = "hard_adaptive_masscap"

    # 5. Policy learning
    policy = train_BC_RNN_GMM(D_pos + S)

    return policy, branch, scorer, diagnostics
```

---

## 4. Immediate methodological fixes

### Fix 1: freeze the method

Create a file:

```text
METHOD_FREEZE.md
```

It should include:

- exact score model,
- exact trajectory score aggregation,
- exact mass estimate,
- exact router rule,
- exact policy training budget,
- exact checkpoint schedule,
- exact final evaluation protocol,
- exact random seeds and split seeds,
- exact metrics.

After freezing, do not change the method based on fresh test results. Any later variant becomes an ablation or follow-up.

### Fix 2: separate development, validation, and final test splits

Your current reports are useful, but the selection/router rules appear to have been refined while looking at Can/Lift/CanMG outcomes. That is normal during research, but the paper needs a clean final protocol.

Use three split categories:

| split type | purpose | can influence method? |
|---|---|---|
| Development splits | design and debugging | yes |
| Validation splits | choose among a small number of frozen variants | limited, predeclared |
| Final test splits | paper claims | no |

Recommended final split seeds:

- Existing split: keep as development.
- Existing shuffle42: treat as validation.
- New final split seeds: `11`, `22`, `33`.

For final claims, report only methods frozen before running these splits.

### Fix 3: stop using hidden labels in any decision rule

Hidden labels can be used for audit tables only:

- selected hidden positives,
- selected hidden bads,
- purity,
- recall.

They must not be used for:

- thresholds,
- branch selection,
- checkpoint selection,
- paper-facing hyperparameter tuning.

### Fix 4: increase final evaluation episodes

Ten Robomimic rollouts are too noisy for final claims. Use at least:

- **50 episodes per method per seed** for final tables,
- same held-out initial-state set for all methods,
- paired evaluation where possible,
- bootstrap confidence intervals over seeds and initial states.

Keep 10-episode runs only for cheap screening.

### Fix 5: report fixed-budget checkpoints

Use fixed-budget reporting as the main metric:

- 10k,
- 15k,
- 20k.

Do not report oracle-best checkpoint as the main result unless you implement and freeze a hidden-label-free checkpoint-selection rule.

---

## 5. Main experiments to run

## Experiment A: controlled mechanism benchmark

### Dataset

Use your existing Continuous PointNav setting.

### Purpose

Show the cleanest mechanism:

- positives are route prefixes,
- bads are trap trajectories or trap snippets,
- unlabeled contains hidden safe full routes and hidden traps,
- naive mixed BC imitates traps,
- tri-signal support selection recovers full safe behavior.

### Methods

Run:

1. BC on $\mathcal D^+$
2. BC on $\mathcal D^+\cup\mathcal D^u$
3. BC on all data excluding negatives
4. classifier-probability weighted BC
5. positive-only NN support
6. TRIAGE-BC hard masscap
7. TRIAGE-BC soft weighted
8. oracle hidden-positive support

### Sweep

Bad fraction:

$$
0.50,\;0.75,\;0.90,\;0.95
$$

Label budgets:

$$
n_+=n_- \in \{2,5,10\}
$$

Seeds:

$$
0,1,2,3,4
$$

### Metrics

- success,
- trap rate,
- selected support purity,
- selected support recall,
- score AUC,
- positive-negative score gap,
- policy failure type.

### Acceptance criterion

TRIAGE-BC should beat BC-all and weighted BC under high contamination and remain close to oracle support.

---

## Experiment B: Robomimic Can Paired main benchmark

### Dataset

Use Robomimic Can Paired low-dimensional sparse dataset.

This is the best main robotics benchmark because it has paired good/bad trajectories under identical task initializations.

### Splits

Run the following final splits:

| split | labeled positives | labeled negatives | hidden positive unlabeled | hidden bad unlabeled |
|---|---:|---:|---:|---:|
| balanced | 10 | 10 | 80 | 80 |
| intermediate | 10 | 10 | 40 | 80 |
| heavy contamination | 10 | 10 | 20 | 80 |

For each split, run:

- dev split: existing,
- validation: shuffle42,
- final test: split seeds 11, 22, 33.

### Methods

Main methods:

1. BC-positive only
2. BC-all mixed
3. all train positives oracle support
4. fixed top-20
5. fixed top-80
6. positive-only NN top-k
7. positive-vs-unlabeled classifier control
8. classifier-probability weighted BC
9. adaptive masscap
10. TRIAGE-BC router-v2

Optional but useful:

11. score-gap without mass cap
12. pos-min threshold
13. oracle hidden-positive support

### Evaluation

Use official Robomimic BC-RNN-GMM.

For final paper tables:

- 3 policy seeds per split seed if affordable; otherwise 1 policy seed per split seed but 3 split seeds,
- 50 rollouts per method/seed,
- horizon 400,
- same held-out validation-positive initial states across methods,
- report fixed 20k plus full 5k/10k/15k/20k curves.

### Main table

Report:

| method | branch | selected | purity | recall | 10k success | 15k success | 20k success | 95% CI |
|---|---|---:|---:|---:|---:|---:|---:|---|

### Acceptance criterion

TRIAGE-BC should:

- beat BC-all in all contamination settings,
- beat or match weighted BC at 20k on balanced/intermediate/heavy contamination,
- beat positive-only NN on at least the intermediate or heavy contamination setting at fixed budget,
- avoid claiming superiority where positive-only NN is tied or better.

---

## Experiment C: Robomimic Lift MG transfer benchmark

### Dataset

Use Robomimic Lift MG sparse low-dimensional data.

### Purpose

Show that the method transfers beyond Can Paired to a different manipulation task and a larger, highly contaminated machine-generated pool.

### Development result to contextualize

The original three-seed diagnostic was strong:

- pos-min calibrated threshold: 0.667 success at 20k,
- positive-only NN top160: 0.567,
- weighted BC sampler: 0.533,
- all-demo cloning: 0.200,
- all-positive oracle support: 0.633 at 20k and 0.733 best-per-seed.

The fresh frozen three-split endpoint matrix weakens the Lift policy-benefit claim: weighted BC reaches 93/150, positive-only NN top160 reaches 82/150, TRIAGE-BC / pos-min reaches 74/150, all-demo BC reaches 31/150, and all-positive oracle reaches 105/150.

### Methods

Run:

1. BC-all
2. BC-positive only
3. all train positives oracle support
4. weighted BC
5. positive-only NN top80/top160
6. pos-min threshold
7. adaptive masscap
8. TRIAGE-BC router-v2

### Additional required check

Completed: the frozen Lift rows now use 50-episode endpoint evaluation, and split 33 includes all-demo BC plus all-positive oracle controls.

### Acceptance criterion

The method should beat all-demo cloning and expose the support-purity advantage of bad-label calibration. It should not be claimed as a Lift policy winner unless a new predeclared precision/coverage converter beats weighted BC and positive-only NN on fresh splits.

---

## Experiment D: Can MG stress benchmark

### Current status

Can MG is not ready as a main positive result. Weighted BC is currently best among matched controls at fixed 20k, but success is only 0.333 and shuffled validation is weak.

Use Can MG for one of two roles:

### Option D1: stress/limitation diagnostic

Keep it as a limitation:

> On large ambiguous MG pools, score-shape rules may not identify a reliable hard/soft branch. TRIAGE-BC abstains, and Can MG exposes the need for a coverage-sensitive quality proxy.

This is honest and scientifically useful.

### Option D2: high-impact stretch result

Try to replace abstention with a **coverage-sensitive hidden-label-free branch proxy**.

Candidate proxy:

$$
Q_{\text{proxy}}(S)
=
\underbrace{\mathrm{LL}_{+}(S)}_{\text{positive imitation}}
-
\lambda \underbrace{\mathrm{LL}_{-}(S)}_{\text{negative rejection}}
+
\beta \underbrace{\log(\mathrm{ESS}(S))}_{\text{effective coverage}}
-
\gamma \underbrace{\mathrm{Dist}_{+ \to S}}_{\text{positive coverage gap}}.
$$

Where:

- $\mathrm{LL}_{+}$: log-likelihood of a small validation-positive set,
- $\mathrm{LL}_{-}$: log-likelihood on labeled/validation negatives,
- $\mathrm{ESS}(S)$: effective sample size or selected trajectory count under calibrated score weights,
- $\mathrm{Dist}_{+ \to S}$: kNN distance from labeled-positive state-action embeddings to selected support,
- all terms are hidden-label-free.

The key is that likelihood alone failed because it preferred all-positive support even when weighted sampling had better rollout success. Add a coverage term.

### Candidate branches to score

1. all-positive support
2. top-k hard support
3. pos-p10 hard support
4. adaptive masscap
5. weighted BC

### Acceptance criterion for using Can MG as a main result

Use Can MG as a main result only if the proxy:

- selects the rollout-best branch on original Can MG,
- does not select a weak branch on shuffle42,
- improves or matches weighted BC on fresh final split seeds,
- reaches a respectable absolute success level, preferably above 0.45 at 20k.

If this does not happen, keep Can MG as an abstention/limitation result.

---

## Experiment E: Square and Transport support transfer

### Current status

Square and Transport are support-side relative-quality diagnostics, not failure-demo policy benchmarks.

### What to do

Keep them as appendix support-transfer evidence unless you build a quality-sensitive evaluator.

### Required if promoted to main paper

You need one of:

1. dense return or subtask-completion score,
2. final object pose / distance-to-goal metric,
3. reward shaping metric from environment state,
4. human/heuristic quality score.

Sparse success is unsuitable because the MH demos are all reward-positive.

### Recommended use

Appendix table:

| task | labels | unlabeled mix | selected purity | recall | score gap |
|---|---:|---:|---:|---:|---:|

Do not use Square/Transport as main policy success evidence unless the quality metric is implemented.

---

## 6. Critical ablations

### Ablation 1: Are bad labels useful?

Run on Can 40p/80b and Lift MG.

Methods:

1. positive-only NN top-k
2. positive-vs-unlabeled classifier
3. bad-aware classifier
4. bad-aware classifier with shuffled bad labels
5. bad-aware classifier with random negatives
6. bad-aware classifier with 1, 2, 5, 10, 20 bad demos

Metrics:

- selected purity,
- selected recall,
- rollout success,
- variance across seeds.

Key paper claim should be:

> Bad labels are not universally necessary, but they improve calibration and fixed-budget stability in regimes where positive-only similarity is coverage-limited or admits hidden bad behavior.

### Ablation 2: precision versus coverage

For Can Paired, run a threshold sweep:

- top 10,
- top 20,
- top 40,
- top 60,
- top 80,
- score-gap,
- masscap,
- weighted.

Plot:

- x-axis: selected hidden-good recall,
- y-axis: selected hidden-bad contamination,
- color: rollout success.

This can become one of the paper’s most important figures.

### Ablation 3: label budget

Run:

$$
n_+=n_- \in \{5,10,20\}
$$

on Can 40p/80b and Lift MG.

Report:

- score AUC,
- selected purity/recall,
- success.

This demonstrates whether the method genuinely works in the scarce-label regime.

### Ablation 4: score aggregation

Compare:

1. mean trajectory score,
2. p10 trajectory score,
3. min trajectory score,
4. mean minus variance penalty,
5. transition-level filtering.

This matters because bad segments inside otherwise useful trajectories are exactly where trajectory-level weighting can fail.

### Ablation 5: hard versus soft conversion

Use matched candidate branches with the same score model:

1. hard top-k,
2. hard masscap,
3. hard pos-min,
4. soft probability sampler,
5. soft sampler with temperature.

Do not compare against an under-configured weighted BC baseline.

### Ablation 6: checkpoint selection

Run only as diagnostic unless the rule is frozen.

Candidate checkpoint rules:

1. fixed 20k,
2. train-support likelihood,
3. labeled-positive likelihood,
4. contrastive positive-minus-negative likelihood,
5. coverage-sensitive proxy,
6. oracle best — diagnostic only.

Main paper should use fixed 20k unless a rule generalizes across Can and Lift.

### Ablation 7: split sensitivity

For every main claim, run at least:

- original split,
- shuffle42 validation,
- new split seeds 11, 22, 33.

Report mean and standard deviation across split seeds.

---

## 7. Baselines to include

### 7.1 Required same-backbone baselines

These are non-negotiable:

1. **BC-positive**  
   Train only on scarce positives.

2. **BC-all / mixed-log BC**  
   Train on positives plus unlabeled, optionally excluding labeled bads.

3. **Weighted BC**  
   Classifier-probability weighted sampler with the official Robomimic BC-RNN-GMM backbone.

4. **Positive-only nearest-neighbor support**  
   Strong no-bad-label baseline.

5. **Positive-vs-unlabeled classifier**  
   No explicit bad labels.

6. **Fixed top-k score selection**  
   At least top20 and top80 on Can.

7. **Oracle all-positive support**  
   Upper bound / diagnostic only.

8. **Oracle hidden-positive support**  
   Upper bound / diagnostic only if available.

### 7.2 Algorithmic baselines if feasible

For PointNav or smaller state-based tasks, include:

1. IQ-Learn-style inverse soft-Q imitation
2. SMODICE-style offline distribution correction
3. DemoDICE-style offline imitation
4. SPRINQL-style suboptimal-demonstration offline IL
5. UNIQ / undesirable-demonstration inverse-Q baseline
6. Difference-of-KL expert-versus-bad baseline

For Robomimic, if implementing these is too expensive, be explicit:

> The Robomimic experiments isolate the score-to-training-data conversion problem under a fixed strong sequence-BC backbone.

That is acceptable if the paper’s contribution is framed correctly.

---

## 8. Statistics and reporting

### 8.1 Final metrics

For each method and task:

- success mean,
- standard error across seeds,
- 95% bootstrap confidence interval,
- selected purity,
- selected recall,
- selected count,
- hidden-bad count, audit only,
- score AUC,
- effective sample size,
- fixed-budget success at 10k/15k/20k.

### 8.2 Paired uncertainty

For Robomimic:

- evaluate all methods on the same held-out initial states,
- compute per-initial-state paired differences,
- bootstrap over seeds and initial states,
- include a per-initial-state heatmap for Can 40p/80b.

### 8.3 Avoid misleading statistics

Do not treat repeated rollouts from the same initial states as fully independent. Report both:

1. pooled binomial interval for transparency,
2. seed/initial-state bootstrap interval for robustness.

### 8.4 Final table style

Use this structure:

| task | split | method | branch | selected | purity | recall | 20k success | 95% CI |
|---|---|---|---|---:|---:|---:|---:|---:|

And separate appendix tables for:

- 5k/10k/15k/20k curves,
- per-seed results,
- per-initial-state results,
- support diagnostics.

---

## 9. Diagnostics to produce

For each main experiment, automatically save:

### Score diagnostics

- positive/negative/unlabeled score histograms,
- score calibration curves,
- AUC positive-vs-negative,
- hidden-positive-vs-hidden-bad AUC, audit only,
- unlabeled positive-mass estimate $\hat m$,
- count above pos-min,
- score-gap location.

### Support diagnostics

- selected count,
- selected hidden-positive count, audit only,
- selected hidden-bad count, audit only,
- purity, audit only,
- recall, audit only,
- effective sample size,
- kNN distance to labeled-positive support,
- kNN distance to labeled-negative support.

### Policy diagnostics

- success by checkpoint,
- success by initial state,
- action log-likelihood on labeled positives,
- action log-likelihood on labeled negatives,
- failure type,
- rollout videos for best and worst seeds.

### Branch diagnostics

For each candidate branch:

- proxy score,
- chosen/not chosen,
- rollout success,
- whether proxy ranking matches rollout ranking.

This is essential for Can MG and for defending router/abstention decisions.

---

## 10. Paper figures

### Figure 1: problem setup

Diagram:

$$
\mathcal D^+,\quad \mathcal D^-,\quad \mathcal D^u
\rightarrow
\text{score model}
\rightarrow
\text{support converter}
\rightarrow
\text{BC-RNN-GMM policy}
$$

Show hard support, soft weighting, and abstention.

### Figure 2: precision/coverage tradeoff

On Can 40p/80b:

- x-axis: hidden-positive recall,
- y-axis: hidden-bad contamination,
- marker size/color: rollout success.

Show top20, top40, top80, coverage-gap, masscap, weighted.

Status: generated as `results/final_paper/figures/can40_precision_coverage.png` and `.pdf` from the frozen Can 40p/80b support sweep.

### Figure 3: main Robomimic results

Grouped bar chart:

- Can 40p/80b,
- Lift MG.

Methods:

- BC-all,
- weighted BC,
- positive-only NN,
- TRIAGE-BC,
- all-positive oracle.

Status: current main Figure 3 candidate generated as `results/final_paper/figures/robotics_primary_endpoint_matrix.png` and `.pdf`, with source table `results/final_paper/tables/robotics_primary_endpoint_matrix.csv`. This main figure includes only completed primary frozen three-split aggregates: Can 40p/80b and Lift MG. The broader diagnostic matrix is included appendix-only in `paper/triage_bc_paper.tex` via `results/final_paper/figures/robotics_current_endpoint_matrix.png` and `.pdf`, with Can 20p/80b and Can 80p/80b marked as diagnostic single-split endpoint rows. Descriptive uncertainty for the primary matrix is staged in `results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md`; paired initial-state bootstrap uncertainty is staged in `results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md`. Can 20p/80b now has a three-split support audit and a split-22 endpoint extension for positive-only versus TRIAGE, but not a full three-split endpoint table.

### Figure 4: score histograms

Show why different branches are chosen:

- Can paired: clean score knee → hard support,
- Lift MG: high pos-min separation → pos-min,
- Can MG: large ambiguous plateau → abstention.

Status: generated as `results/final_paper/figures/score_shape_diagnostics.png` and `.pdf`, with source table `results/final_paper/tables/score_shape_diagnostics.csv`. Can 40p/80b and Lift MG use frozen split seeds 11/22/33; Can MG is labeled as a stress diagnostic.

### Figure 5: bad-label ablation

Plot performance versus number of bad labels.

### Figure 6: final evaluation uncertainty

For Can 40p/80b:

- per-initial-state paired success differences,
- bootstrap confidence intervals.

Status: generated as `results/final_paper/figures/primary_endpoint_paired_deltas.png`
and `.pdf`, with source rows in
`results/final_paper/tables/primary_endpoint_paired_initial_deltas.csv` and
report text in
`results/final_paper/tables/primary_endpoint_paired_deltas_REPORT.md`.

---

## 11. Paper table plan

Status: the current figure/table and claim map has been promoted into
`paper/MANUSCRIPT_CHECKLIST.md`, which is included in artifact-reference
validation. Quoted paper numbers are guarded by
`scripts/validate_paper_claim_numbers.py`. The manuscript result order is now
frozen as PointNav-first mechanism evidence followed by Robomimic endpoint
evidence. Square/Transport are kept repository-only for now because they are
support-side relative-quality diagnostics rather than failure-demo policy
benchmarks.

### Main Table 1: controlled PointNav

| bad frac | BC-all | weighted BC | positive-only | TRIAGE-BC | oracle |
|---:|---:|---:|---:|---:|---:|

Status: generated as `results/final_paper/tables/pointnav_controlled_mechanism.csv` and `results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`, with figure outputs `results/final_paper/figures/pointnav_controlled_mechanism.png` and `.pdf`. The current table emphasizes the label-budget-2 stress result and the fixed-5-positive bad-label-count ablation.

### Main Table 2: Robomimic Can Paired

| split | method | selected | purity | recall | 20k success |
|---|---|---:|---:|---:|---:|

### Main Table 3: Robomimic Lift MG

| method | selected | purity | 10k | 15k | 20k | best diagnostic |
|---|---:|---:|---:|---:|---:|---:|

### Main Table 4: bad-label ablation

| task | no-bad baseline | bad-aware method | gap | interpretation |
|---|---:|---:|---:|---|

Status: generated as `results/final_paper/tables/bad_label_control_summary.csv`
and `results/final_paper/tables/bad_label_control_summary_REPORT.md`, then
included as the compiled appendix table `tab:bad-label-controls` in both LaTeX
drafts. The current table is appendix/control evidence: it supports
label-efficient calibration on controlled PointNav and support-purity benefits
on Lift, while showing that positive-only retrieval beats the current bad-aware
converter on the frozen Can diagnostics and frozen Lift endpoint.

### Appendix Table A: Can MG stress

| branch | proxy | selected | purity | 20k success | decision |
|---|---:|---:|---:|---:|---|

### Appendix Table B: Square/Transport support transfer

| task | labels | selected purity | recall | promoted to policy benchmark? |
|---|---:|---:|---:|---|

---

## 12. Theory component for high impact

Status: added to `paper/triage_bc_paper.tex` and
`paper/triage_bc_draft.md` as a simple precision/coverage analysis. It is framed
as an organizing decomposition rather than a formal theorem.

Add a small theoretical section. It does not need to be complex.

### 12.1 Mixture model

Assume unlabeled trajectories come from:

$$
\mathcal D^u \sim \pi_g \cdot P_g + (1-\pi_g)\cdot P_b.
$$

A learned score $g(\tau)$ induces a thresholded selected set $S_t$ with true-positive rate $r_t$ and false-positive rate $f_t$.

### 12.2 BC risk decomposition

For a selected support set $S_t$, a simple bound can look like:

$$
R(\hat \pi_{S_t})
\le
R(\pi_g)
+
O\left(\sqrt{\frac{\mathrm{complexity}}{r_t N_g}}\right)
+
C\cdot f_t N_b.
$$

Interpretation:

- More coverage reduces estimation error.
- More contamination increases imitation of bad actions.
- The optimal threshold is not always the purest threshold.

This justifies the purity/coverage tradeoff.

### 12.3 Weighted versus hard support

For weighted BC:

$$
R(\hat \pi_w)
\le
R(\pi_g)
+
O\left(\sqrt{\frac{\mathrm{complexity}}{\mathrm{ESS}(w)}}\right)
+
C\cdot \frac{\sum_{\tau\in \mathcal D_b^u}w(\tau)}
{\sum_{\tau\in \mathcal D^u}w(\tau)}.
$$

This explains why:

- soft weighting can win when broad coverage is crucial,
- hard support can win when bad actions conflict with good actions,
- a branch rule or abstention is needed.

### 12.4 Theoretical contribution

Present TRIAGE-BC as minimizing an empirical upper bound on imitation risk:

$$
\text{estimated risk}
=
\text{contamination penalty}
+
\text{coverage penalty}.
$$

The mass-capped rule is then not just a heuristic; it is an estimator of the point where marginal coverage stops being worth marginal contamination.

---

## 13. Step-by-step execution plan

## Phase 1: freeze the current method

Create:

```text
METHOD_FREEZE.md
```

Include:

- score model,
- demo aggregation,
- mass estimate,
- router-v2 rule,
- policy config,
- checkpoint schedule,
- final evaluation protocol.

Commit this before running new final splits.

Deliverables:

- `METHOD_FREEZE.md`
- `configs/final_method.yaml`
- `configs/final_eval.yaml`

## Phase 2: build one final runner

Create:

```text
scripts/run_final_matrix.py
```

It should accept:

```bash
python scripts/run_final_matrix.py \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 11 \
  --method triage_bc \
  --policy-seed 0 \
  --eval-episodes 50 \
  --out-dir results/final_matrix
```

The script should write:

- config JSON,
- selected demo IDs,
- score CSV,
- support audit CSV,
- policy checkpoint paths,
- eval CSV,
- report Markdown.

## Phase 3: rerun main Can final matrix

Run for Can Paired:

- 80p/80b,
- 40p/80b,
- 20p/80b,

and split seeds:

- 11,
- 22,
- 33.

Methods:

- BC-positive,
- BC-all,
- weighted BC,
- positive-only NN,
- adaptive masscap,
- TRIAGE-BC,
- oracle all-positive.

Final result decision:

- If TRIAGE-BC is consistently strong, make Can the main result.
- If positive-only NN ties, frame bad-label benefit as stability/coverage, not necessity.

## Phase 4: run Lift final matrix

Status: completed for the frozen split seeds 11, 22, and 33 with 50-episode endpoint evaluation.

Completed methods:

- BC-all,
- weighted BC,
- positive-only NN top160,
- pos-min,
- TRIAGE-BC,
- all-positive oracle,
- classifier-score top160 ablation.

Final result decision:

- Lift weakened as a policy-benefit result: weighted BC is the strongest non-oracle row on the frozen matrix.
- Present Lift as mixed but useful score-calibration evidence: bad labels improve support purity, while the current threshold is coverage-limited.
- A broader classifier-score top160 rule also fails as a simple rescue: it improves split 33 but drops on splits 11 and 22, reaching only 68/150 pooled.

## Phase 5: decide Can MG role

Run only branch-proxy experiments first.

Status: completed as a staged final-paper ablation. The likelihood-proxy attempt fails: on original Can MG, simple positive/negative BC likelihood proxies choose all-positive support even though weighted BC is rollout-best at fixed 20k; on shuffled Can MG, the hard and soft branches are both weak. Keep Can MG as abstention/limitation unless a new coverage-sensitive proxy is proposed and predeclared.

Additional v0.2 status on 2026-06-25: staged support-side proxy screens also
failed to justify a fresh endpoint branch. Simple coverage/classifier-score
proxies match the audit-support winner in only `1/28` setting-proxy cases, and
explicit action-conflict / bad-neighbor proxies match it in only `1/32` cases.
Do not train another endpoint variant from the current hybrid candidate family
unless the candidate generator itself changes.

Consolidated proxy no-go status on 2026-06-25: the paper-facing table in
`results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md` aggregates
likelihood, contrastive likelihood, negative rejection, support-purity,
hidden-positive-recall, coverage, and initial/transition-coverage checks.
Deployable proxy attempts match endpoint winners in only `2/11` rows, and
audit-only support rows match `3/6`; this should be cited as the main
policy-quality proxy no-go artifact.

Follow-up candidate-generator status on 2026-06-25: direct action-risk
candidates do improve hidden support labels, but the first proper endpoint gate
is negative. On Can 40p/80b split seed 11, `bad_neighbor_safe_top40` selects
`40/40` hidden positives with `0` hidden bad demos, yet the 200-epoch BC-RNN-GMM
checkpoint reaches only `0.720` over 50 rollouts, below existing positive-NN
top40 `0.840` and TRIAGE-BC `0.760`. This is evidence that support purity is
not enough. A less distribution-shifting `positive_nn_risk_fusion_top40` variant
selects `39/40` hidden positives with `1` hidden bad demo and reaches `0.820`,
but still does not beat existing positive-NN top40. Do not promote either
action-risk candidate as v0.2. A split-22 confirmation makes this a stronger
no-go: `positive_nn_risk_fusion_top40` has perfect support audit on split 22
but reaches only `0.640`, below positive-NN top40 `0.760`. Non-GPU
policy-coverage diagnostics over initial states and transition nearest
neighbors also fail to explain or rescue this action-risk branch, so do not
spend split-33 endpoint compute unless the candidate generator changes.

Union candidate update on 2026-06-25: changing the candidate from replacement
to complement is the first Can 40p/80b v0.2-style result that beats the strong
positive-only pooled row. The union of `positive_nn_top40` and
`positive_nn_risk_fusion_top40` selects `119/120` hidden positives and `16/240`
hidden bad demos across split seeds `11`, `22`, and `33`. Official BC-RNN-GMM
at the 200-epoch / 50-rollout endpoint reaches `116/150` successes, compared
with positive-only NN `108/150`, TRIAGE-BC v0.1 `99/150`, weighted BC `90/150`,
and all-demo BC `81/150`. It wins split seeds 22 and 33 but loses split 11 to
positive-only NN (`0.760` versus `0.840`). Treat this as a useful Can-only
candidate family, not as TRIAGE-BC v0.2: Lift MG and Can MG remain unresolved,
and any promoted v0.2 still needs a frozen hidden-label-free selection rule and
fresh cross-task validation.

Component-ablation status on 2026-06-25: the paper-facing table in
`results/final_paper/tables/hard_union_component_ablation_REPORT.md` now
separates positive-only NN top40, risk-fusion top40, union top40,
classifier-only top40, weighted BC, and v0.1 adaptive masscap. It shows that
risk-fusion alone improves hidden support labels but loses the two-split
endpoint check to positive-only (`73/100`, `-0.070`), classifier-only top40 is
support-only and dominated, and the union's pooled gain comes from preserving
the positive-only anchor while adding coverage on splits `22` and `33`.

Failure-mode audit status on 2026-06-25:
`results/final_paper/tables/failure_mode_initial_states_REPORT.md` now
compares positive-only NN, weighted BC, v0.2 hard union, and all-demo BC on
three representative paired Can 40p/80b initial states from existing endpoint
rollouts. It includes a hard-union rescue on split `33` / `demo_105`, a
positive-anchor regression on split `11` / `demo_39`, and a soft-pool rescue on
split `33` / `demo_99`. Treat this as appendix intuition only: grasp and
loop/miss columns are metric proxies from success and horizon-length failures,
not video-level annotations.

Portfolio-router update on 2026-06-25: the candidate-family audit now includes
the union branch, and a new mass/count router audit gives the first plausible
cross-task v0.2 shape. The rule uses no hidden labels: low estimated positive
mass selects hard positive-NN/risk union, moderate mass plus a sizable pos-min
pool selects soft weighted BC, and very large ambiguous mass/pool selects
abstention. On the existing primary development endpoints it chooses Can 40
union (`116/150`) and Lift weighted BC (`93/150`), for `209/300` pooled
success. This beats the strongest pre-union per-task baselines (`201/300`) and
v0.1 (`173/300`), but it is still not a final method because the rule was
written after seeing the Can union endpoint and needs fresh split validation.
The development freeze for that fresh-split gate is now drafted in
`METHOD_FREEZE_V02.md`, `configs/final_method_v02.yaml`, and
`configs/final_eval_v02.yaml`.

Fresh-gate update on 2026-06-25: five frozen Can 40p/80b and Lift MG split
seeds completed selected-branch endpoints and the strongest completed
same-backbone baselines. The v0.2 hard union row on Can is `45/50`, `45/50`,
`39/50`, `27/50`, and `41/50` on split seeds `101`, `202`, `303`, `404`, and
`505`; strongest completed non-oracle baselines are `37/50`, `40/50`, `36/50`,
`39/50`, and `40/50`. The v0.2 selected weighted row on Lift is `31/50`,
`30/50`, `19/50`, `30/50`, and `33/50`; positive-only NN is `28/50`, `25/50`,
`21/50`, `25/50`, and `26/50`. All rows use 200-epoch official BC-RNN-GMM and
50 valid-positive-start rollouts. Combined selected rows are `340/500` versus
`338/500` for the best completed non-oracle baseline per split after completing
all five v0.1 TRIAGE hard-support audit rows. This is a
completed fresh Can+Lift gate, but the cross-task v0.2 claim should stay
cautious because Can has a severe split-404 reversal, Lift selects weighted BC,
and the paired-bootstrap intervals cross zero.

Prefix-positive robotics diagnostic status on 2026-06-25: the controlled Can
prefix-positive construction produces a strong bad-label win. Across split
seeds `101`, `202`, and `303`, prefix state-action positive-NN top80 selects
only `37/240` hidden positives and admits `203/240` hidden bad demos, while
prefix bad-aware state top80 selects `195/240` hidden positives and admits
`45/240` hidden bad demos. Official BC-RNN-GMM trained for 200 epochs reaches
`119/150` successes for `prefix_bad_aware_state_top80` versus `6/150` for
matched `prefix_state_action_nn_top80` over the three completed endpoint
splits. Treat this as strong controlled robotics evidence that mirrors the
PointNav prefix-positive mechanism, but keep it separate from primary benchmark
rows because the split construction changes the default Robomimic setting.
Paper-facing summary artifacts are staged as
`results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md` and
`results/final_paper/figures/can_prefix_positive_diagnostic.{png,pdf}`, and the
appendix text/checklist/repro docs now reference the diagnostic without
promoting it to the main benchmark matrix.

Generated regime-probe summary status on 2026-06-25:
`results/final_paper/tables/generated_regime_probe_summary_REPORT.md` now
consolidates the endpoint-backed hard-negative, coverage-shift, and
prefix-positive Can probes for the main-paper `tab:regime-probes` table.
The concise row is hard-negative `104/150` versus `91/150` (`+13/150`,
support `113/7` versus `70/50`), coverage-shift `120/150` versus `103/150`
(`+17/150`, support `118/2` versus `105/15`), and prefix-positive `119/150`
versus `6/150` (`+113/150`, support `195/45` versus `37/203`). Keep this as
generated mechanism evidence, not a default Robomimic benchmark row.

Prefix-length robustness status on 2026-06-25:
`results/final_paper/tables/can_prefix_length_robustness_REPORT.md` varies the
generated Can prefix-positive label length at fixed split seeds `101/202/303`,
label budget, and top80 support size. Bad-aware state top80 clears matched
prefix state-action positive-NN top80 for short/default/long prefixes:
hidden-positive recall deltas are `+0.400`, `+0.658`, and `+0.737`, while
hidden-bad admission deltas are `-0.400`, `-0.658`, and `-0.737`. This is
support-only construction robustness; it strengthens the generated-probe
mechanism story but is not another endpoint result.

Non-Can generated support status on 2026-06-25:
`results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md`
adds the first Lift generated hard-negative/action-conflict support audit. Across
split seeds `101/202/303`, bad-aware proxy top40 selects `82/120` hidden
positives and admits `38/240` hidden bad demos, while state-action positive-NN
top40 selects `12/120` hidden positives and admits `108/240` hidden bad demos.
This clears a support-only C1 gate and suggests the bad-aware support mechanism
can transfer beyond Can, but it is not a policy endpoint result.

Non-Can endpoint-smoke status on 2026-06-25:
`results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/REPORT.md`
adds a bounded Lift hard-negative endpoint smoke. It trains official
BC-RNN-GMM for only 50 epochs on split `101` and evaluates 10 valid-positive
starts. Bad-aware proxy top40 reaches `2/10`, while state-action positive-NN
top40 reaches `1/10`; support on this split is `21` hidden positives and `19`
hidden bad demos for bad-aware proxy top40 versus `7` and `33` for positive-NN.
This is feasibility evidence only. It is too noisy and under-budgeted for a C1
endpoint claim; the next meaningful gate is full 200-epoch / 50-rollout split
`101` before expanding to seeds `202` and `303`.

Non-Can full-budget split-101 status on 2026-06-25:
`results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/REPORT.md`
now runs the same Lift hard-negative pair at 200 epochs and 50 rollouts on split
`101`. Bad-aware proxy top40 reaches `7/50` with average length `137.3`, while
state-action positive-NN top40 reaches `3/50` with average length `143.6`.
This is directionally consistent with the support audit but weak in absolute
success. It should stay exploratory unless the remaining split seeds `202/303`
are run and preserve the margin.

Active-abstention status on 2026-06-25:
`results/final_paper/tables/active_abstention_evaluation_REPORT.md` stages the
C2 Can MG abstention audit. Router-v2 abstains on original and shuffled Can MG
with mass/count `1947.9`/`1025.7` and `1466.3`/`515.7`; assigned router-v2 rows
average `0.700` fixed-20k success with minimum `0.600`, while abstained rows
average `0.217` and top out at `0.333`. Original-MG proxies match best success
in `0/6` cases; shuffled MG gets `6/6` only because both staged forced branches
reach `0.100`. Treat this as stress/limitation evidence that abstention is more
honest than forcing a branch, not as a Can MG success result.

Theory-lite status on 2026-06-25: the paper theory section now names the
existing risk decomposition as `Proposition 1 (coverage-contamination
criterion)`. The proposition states that a hard selector should add an unlabeled
trajectory exactly when its marginal coverage gain exceeds its normalized
marginal contamination cost. This is intentionally an organizing proposition,
not a formal guarantee for nonlinear BC-RNN-GMM policies.

Candidate-breakthrough status on 2026-06-26:
`results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md` is the
strongest new Can-only method evidence. Frozen Candidate F reaches `198/250`
on Can 40p/80b versus positive-only `174/250`, weighted `158/250`, triage
`171/250`, and the completed per-split baseline oracle `192/250`. It should be
scoped as a Can 40p/80b result, not as unchanged Can-to-Lift transfer:
`results/candidate_breakthrough/candidate_f_lift_transfer_audit_REPORT.md`
shows direct transfer at only `145/250` on Lift versus the Lift per-split
baseline oracle `154/250`.

Fresh branch-validation status on 2026-06-26:
the broader Candidate G/H/I tail routers were not safe enough after held-out
preflight. Can 707 exposed task-agnostic mild-tail triage as bad
(`10/20` versus positive-only `15/20`), and Lift 606 exposed retained mild-tail
triage as bad (`23/50` versus positive-only `28/50`). Candidate K's
first-step GMM confidence gate improved tuned Lift 606 (`32/50` versus
positive-only `28/50`) but failed fresh Lift 707 (`10/20` versus positive-only
`12/20`). Candidate L's labeled-positive q25 calibration preserved Lift 606
(`18/20`) but still failed Lift 707 (`10/20`), and its cross-split audit
shows the best Lift606-selected initial one-feature gates reach only `11/20`
on Lift707. Candidate M then tested direct per-step temporal confidence on
Lift606; both initial-q25 and sequence-q25 temporal calibration reached only
`7/20` and heavily over-switched to triage. Candidate N added persistence, but
sequence-q25 k10 reached only `13/20` and k20 only `11/20` on Lift606, below
positive-only `14/20` and the initial confidence gate `18/20`. The current
conclusion is: do not spend more endpoint budget on scalar initial-threshold
routers, raw per-step confidence routers, or simple persistence gates; pursue
policy-training changes, and keep Candidate F as the only clean new branch
result so far.

Policy-training follow-up status on 2026-06-26:
Candidate O tested a simple Lift606 positive-anchored union recipe: full loss
weight for labeled positives and positive-NN selected demos, plus triage-only
extra demos at loss weight `0.25`. This 243-demo training set failed badly:
epoch 50 reached `1/20` and epoch 100 reached `5/20` on the same Lift606
first-20 endpoint screen. Do not continue constant-demo-weight union training;
Candidate P then initialized from the positive-only NN epoch-200 checkpoint and
fine-tuned on the same anchor-union weights for 20 epochs. It recovered some of
Candidate O's collapse (`11/20`) but still degraded positive-only (`14/20`) and
triage (`13/20`). Candidate Q then saved every checkpoint in the first 5
epochs and found no early sweet spot; the best checkpoint was `11/20`.
Candidate R interpolated from the positive-only checkpoint toward the 20-epoch
anchor-union fine-tune and also topped out at `11/20`. Stop anchor-union rescue
attempts. The next Lift training attempt needs a different objective or
selector, not merely lower-weight triage support, positive-only
initialization, shorter fine-tuning, or checkpoint interpolation. Candidate S
then tested a different selector proxy: a balanced logistic initial-risk
classifier trained from labeled positive versus labeled negative initial
features. Its primary policy-feature q25 gate reached only `12/20` on Lift606,
below positive-only `14/20`, and tied positive-only on Lift707 (`12/20`).
This further supports treating Lift as a limitation/abstention case unless a
substantially different policy-quality proxy appears.

Fresh Can606 Candidate F no-tail smoke on 2026-06-26: after training the
missing positive-only and weighted epoch-200 policies, the Candidate E gate
branch tied positive-only at `16/20` and beat weighted (`14/20`) on the first-20
valid-positive screen. This is neutral rather than claim-strengthening: it
does not show a fresh Can no-tail failure, but it also does not add headroom.
Fresh Can707 then tested Candidate F's mild-tail weighted branch: weighted tied
positive-only at `15/20`, while Candidate E reached `13/20` and triage `10/20`.
Across Can606+Can707 first-20 smokes, Candidate F ties positive-only at
`31/40`. Only continue to 50 episodes if running a broader predeclared
fresh Can-only validation matrix; these two held-out smokes are neutral, not a
fresh methods win.

Candidate-breakthrough decision report on 2026-06-26:
`results/candidate_breakthrough/candidate_breakthrough_decision_REPORT.md`
is now the paper-facing stop/continue artifact for this search thread. Its
decision is: keep Candidate F as scoped Can 40p/80b discovery evidence
(`198/250` versus positive-only `174/250`, weighted `158/250`, triage
`171/250`, and per-split baseline oracle `192/250`), but do not promote a
general methods-dominance claim. Fresh Can606+707 smokes are neutral
(`31/40` tie versus positive-only), direct Lift transfer is below the Lift
oracle (`145/250` versus `154/250`), and the tested Lift router/training
variants are rejected. The next endpoint compute, if any, should be a
predeclared fresh Can-only validation matrix; otherwise the paper should move
forward as the precision-coverage study with Lift framed as a limitation or
abstention case.

If proxy works:

- train final Can MG policies on fresh splits,
- include as main or secondary result.

If proxy fails:

- keep Can MG as abstention/limitation,
- do not spend more compute trying to force a weak result.

## Phase 6: complete ablations

Prioritize:

1. positive-only NN versus bad-aware across Can/Lift,
2. label budget,
3. threshold/purity/coverage sweep,
4. score aggregation,
5. checkpoint-selection diagnostics.

## Phase 7: write paper

Current status: a claim-checked standalone draft exists at
`paper/triage_bc_paper.tex`, and a provisional ICLR 2026 conversion exists at
`paper/iclr2026/main.tex`. The ICLR compile is 15 pages total, with references
starting on page 10 and appendix material starting on page 11, so the main text
fits the ICLR 2026 9-page main-text budget. Treat this as a provisional
submission shell until the final venue/year is confirmed.

Recommended section order:

1. Introduction
2. Related Work
3. Problem Setting
4. TRIAGE-BC Method
5. Precision/Coverage Analysis
6. Experiments
7. Diagnostics and Limitations
8. Conclusion

---

## 14. Compute-aware priority list

### Must run

1. Final Can 40p/80b with 50 episodes: completed for split seeds 11/22/33.
2. Final Lift 50-episode endpoint: completed for split seeds 11/22/33.
3. Positive-only NN baseline on every main split: completed for current Can and Lift matrices.
4. Weighted BC official baseline on every main split: completed for current Can and Lift matrices.
5. Fresh split seeds for Can 40p/80b and Lift: completed for the current frozen matrices.
6. Score/support diagnostics for all main runs: completed for current core comparisons; keep adding diagnostics for new variants.

### Should run

1. Can 80p/80b has fresh split-seed support audits and one split-33 endpoint diagnostic; Can 20p/80b has a frozen split-11 endpoint diagnostic, a split-22 endpoint extension for positive-only versus TRIAGE, and a three-split support audit. Neither is a full three-split endpoint table.
2. label-budget ablation: PointNav equal budgets 5 and 2 are complete; budget 10 remains optional if a smoother label-efficiency curve is needed
3. bad-label count ablation: PointNav fixed 5 positives with 1/2/5 bad demos is complete
4. threshold/purity/coverage sweep: Can 40p/80b frozen split support tradeoff is complete; additional policy training for individual top-k points remains optional
5. Can MG branch proxy: completed; simple likelihood proxies fail, so Can MG remains an abstention/stress diagnostic
6. Can prefix-positive robotics diagnostic: support audit and 200-epoch
   endpoint checks are complete for split seeds 101/202/303; bad-aware prefix
   selection reaches 119/150 versus 6/150 for prefix positive-NN. This is now a
   paper-facing controlled robotics result, not a primary benchmark row.
7. Can prefix-positive prefix-length robustness: support-only short/default/long
   prefix sweep is complete; it should remain an appendix construction
   robustness check unless a non-default prefix condition is endpoint-trained.
8. Lift hard-negative/action-conflict diagnostic: support and 200-epoch
   endpoint checks are complete for split seeds `101/202/303`. The bad-aware
   proxy reaches `15/150` versus `5/150` for state-action positive-NN top40 and
   selects 82 hidden positives with 38 hidden bad demos versus 12 hidden
   positives with 108 hidden bad demos. Keep this as exploratory non-Can C1
   mechanism evidence because absolute success remains low.

### Optional

1. Square quality-sensitive evaluator
2. Transport quality-sensitive evaluator
3. D4RL/IQ-Learn-style baselines
4. full Tri-PIQL inverse-Q actor extraction

---

## 15. Acceptance criteria for a strong paper

A paper-ready result should satisfy at least four of these:

1. TRIAGE-BC beats BC-all under heavy contamination.
2. TRIAGE-BC beats official weighted BC at fixed 20k on Can, while Lift is framed as a weighted-BC/coverage counterexample.
3. TRIAGE-BC beats positive-only NN on at least one nontrivial robotics setting. The generated Can diagnostics now satisfy this as targeted mechanism evidence: hard-negative Can reaches `104/150` versus `91/150`, coverage-shift Can reaches `120/150` versus `103/150`, and prefix-positive Can reaches `119/150` versus `6/150`. The default frozen Can 20p/80b and Can 80p/80b diagnostics do not satisfy this and should not be used as primary positive-only wins.
4. The method is hidden-label-free.
5. Final claims hold on fresh split seeds.
6. 50-episode endpoint results agree in direction with 10-episode screening.
7. Router/abstention decisions are predeclared.
8. Can MG is either solved by a validated proxy or honestly presented as abstention.
9. The paper includes a theory/analysis section explaining purity/coverage.
10. All results are reproducible from configs and scripts.

---

## 16. Recommended final claims

Use claims like these:

### Claim 1

> Mixed offline logs are harmful under naive cloning, even when they contain useful hidden demonstrations.

### Claim 2

> Scarce positive and negative labels calibrate a desirability score that identifies useful hidden support.

### Claim 3

> The key design choice is score-to-policy conversion: hard support improves fixed-budget stability when bad contamination is action-conflicting, while soft weighting can help when coverage dominates.

### Claim 4

> A hidden-label-free support converter can improve the precision/coverage tradeoff over soft weighted sampling on paired Can, while Lift MG shows where the current hard threshold under-covers and weighted BC remains a critical baseline.

### Claim 5

> Explicit bad labels improve calibration and fixed-budget stability, but positive-only retrieval is a strong baseline and must be handled carefully.

### Claim 6

> Large ambiguous MG pools expose a failure mode of simple score-shape routers; abstention or coverage-sensitive branch validation is necessary.

### Claim 7

> Support purity is an incomplete proxy for endpoint policy quality: the current action-risk v0.2 candidates improve support audits on Can but fail to beat the strongest positive-only endpoint baseline.

---

## 17. Reproducibility checklist

For every final table row, save:

- git commit hash,
- config YAML/JSON,
- dataset path and version,
- split seed,
- policy seed,
- classifier seed,
- selected demo IDs,
- hidden-label audit file,
- training logs,
- checkpoint paths,
- rollout seeds,
- per-episode success CSV,
- per-initial-state CSV,
- generated report.
- claim-number validator coverage for quoted manuscript counts.

Create:

```text
results/final_paper/
  METHOD_FREEZE.md
  configs/
  tables/
  figures/
  per_seed/
  per_initial_state/
  support_audits/
  score_diagnostics/
  ablations/
```

---

## 18. Recommended abstract draft

> Offline imitation datasets often mix scarce trusted successes, scarce known failures, and larger unlabeled logs. We study when failure demonstrations help as a score-to-support conversion problem: failures can calibrate a desirability score, but policy quality depends on converting scores into behavior-cloning support. TRIAGE-BC learns a tri-signal state-action score, estimates hidden positive mass, and routes unlabeled data into hard support, soft weighting, or abstention. Controlled PointNav and targeted generated Robomimic Can diagnostics show explicit failures help when positives are incomplete, trusted positives under-cover the state distribution, or bad demos are action-conflicting near-neighbors. On the fresh gate, a frozen v0.2 portfolio improves Can 40p/80b (`197/250` versus `192/250`) but is slightly negative on Lift MG (`143/250` versus `146/250`), yielding `340/500` fresh Can+Lift successes versus `338/500` for best per-split non-oracle baselines. The evidence supports a focused conclusion: bad labels can calibrate useful support, but hidden-label-free conversion from scores to policy-training data remains the bottleneck, and strong positive-only and weighted baselines must remain first-class controls.

---

## 19. Bottom line

The project is on a good path, but the high-impact version is narrower and cleaner than the original Tri-PIQL framing.

The complete paper should be about:

> **tri-signal desirability learning plus calibrated score-to-support conversion.**

The key next actions are:

1. keep the current submission around precision versus coverage, not around weak baselines or methods/SOTA dominance,
2. foreground positive-only NN and weighted BC as strong same-backbone baselines,
3. keep generated Can diagnostics separate from primary frozen Robomimic rows while using them as the clearest robotics mechanism evidence,
4. treat Can MG as an abstention/limitation case unless a new coverage-sensitive proxy is predeclared and validated,
5. present the completed fresh Can+Lift gate as a cautious v0.2 portfolio-selector story, not as a decisive win,
6. treat Candidate F/V/W/X and related follow-ups as development-audit evidence that bounds the claims; do not spend more endpoint budget on unchanged scalar gates, nearest-negative hinges, or output-anchor variants.
