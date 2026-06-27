# When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study

Draft status: working Markdown manuscript scaffold. This draft is intentionally conservative: it follows the current frozen evidence package and does not claim a validated full inverse-Q robotics method.

## Abstract

Offline imitation datasets often contain a few trusted successes, a few known failures, and a larger unlabeled log with mixed behavior. When do the failure demonstrations help? We study this as a score-to-support conversion problem: scarce successes and failures can train a desirability score, but policy quality depends on how that score is converted into behavior-cloning data. TRIAGE-BC learns a tri-signal state-action score, aggregates it to trajectory scores, estimates hidden positive mass, and routes the unlabeled log into hard support, soft weighting, or abstention. Controlled PointNav and targeted generated Robomimic Can diagnostics show that explicit failures are valuable when positives are incomplete, trusted positives under-cover the state distribution, or bad demos are action-conflicting near-neighbors. A frozen v0.2 portfolio router improves fresh Can 40p/80b by selecting hard union support, while fresh Lift MG remains a caveat: the router selects weighted coverage but trails the best completed per-split baseline (`143/250` versus `146/250`). The evidence supports a focused conclusion: bad labels can calibrate useful support, but the bottleneck is hidden-label-free conversion from scores to policy-training data, and strong positive-only and weighted baselines must remain first-class controls.

## 1. Introduction

Offline imitation learning is often presented as a problem of cloning desirable demonstrations. In many practical settings, however, the available data is not a clean demonstration set. A user may have a handful of trusted successes, a handful of known failures, and a much larger log whose behavior is unlabeled and mixed. Some of that log may contain useful recoveries, alternate strategies, or broader state coverage; some may contain shortcuts, failed attempts, or actions that conflict with the desired behavior.

The simplest responses are unsatisfactory. Cloning all available trajectories can reproduce harmful behavior. Cloning only the scarce successes can be high precision but low coverage. Softly weighting unlabeled trajectories by a learned desirability score can preserve coverage, but it can also keep too much action-conflicting bad behavior in the policy-training distribution. Hard filtering can remove bad trajectories, but it can also discard coverage that a sequence policy needs to solve the task.

This paper studies the conversion step between score learning and policy learning. Given scarce successes, scarce failures, and a mixed unlabeled log, the central question is not merely whether a classifier can separate good from bad transitions. The central question is how its scores should become a policy-training distribution.

We propose TRIAGE-BC, a score-calibrated behavior cloning framework. TRIAGE-BC trains a state-action desirability classifier from labeled successes and failures, aggregates classifier probabilities into trajectory scores, estimates positive mass in the unlabeled log from labeled score anchors, and then routes the unlabeled data through a hidden-label-free support converter. The frozen v0.1 method uses hard adaptive mass-capped support, positive-minimum threshold support, and abstention for ambiguous high-mass score shapes. The frozen v0.2 portfolio adds an explicit hard-risk-union branch, a soft weighted branch, and stress abstention, chosen by score-derived mass and coverage features.

Our results support a narrower story than a full inverse-reward or inverse-Q claim. In controlled PointNav, where positive labels are only route prefixes and the unlabeled log contains hidden full routes mixed with trap shortcuts, adaptive score-gap support recovers useful hidden support and reaches perfect success under heavy contamination. In Robomimic, v0.1 reveals the precision/coverage failure modes: positive-only retrieval is strongest on the original Can 40p/80b matrix, while weighted BC is strongest on the original Lift MG matrix. The frozen v0.2 router remains barely positive on a five-split fresh Can+Lift gate, reaching `340/500` selected-branch successes versus `338/500` for the best per-split non-oracle baselines. Can carries the cleaner hard-union improvement but has one large losing split; Lift is negative against the completed per-split oracle after all five v0.1 TRIAGE audit rows.

Contributions:

1. We formalize offline imitation from scarce successes, scarce failures, and a contaminated unlabeled log as a score-to-support conversion problem.
2. We introduce TRIAGE-BC v0.1, a hidden-label-free tri-signal support calibration baseline, and a frozen v0.2 portfolio router over hard union, soft weighting, and abstention.
3. We provide controlled PointNav and generated Robomimic Can diagnostics showing when explicit failures help: incomplete positives, action-conflicting near-neighbor failures, and scarce-positive coverage shift.
4. We provide frozen Robomimic endpoint evidence showing both sides of the precision/coverage tradeoff: Can 40p/80b shows hard selected support beating weighted and all-demo controls, Lift MG favors broader weighted coverage, and positive-only retrieval remains stronger on Can.
5. We establish caveats through positive-only NN, weighted BC, all-positive oracle, score-shape diagnostics, Can MG branch-proxy failure, and claim-checked artifact maps.

## 2. Related Work

Behavior cloning is the standard supervised baseline for imitation learning, but it is sensitive to distribution shift and dataset coverage. DAgger-style interactive imitation addresses this by querying an expert on states induced by the learner, while TRIAGE-BC stays strictly offline and cannot request new labels or rollouts during training.

Classical inverse reinforcement learning learns rewards that explain expert behavior, including apprenticeship-learning and maximum-entropy formulations. Adversarial imitation methods such as GAIL match expert occupancy through a learned discriminator. TRIAGE-BC is intentionally narrower: it does not claim a validated reward-to-policy or inverse-Q robotics method. The current robotics method uses a discriminative desirability score only to choose the behavior-cloning support.

Offline RL and advantage-weighted imitation study policy improvement from static datasets, often using task rewards to learn values or advantages. CQL regularizes value learning under unsupported actions; IQL, AWR, and AWAC extract policies through weighted behavior-cloning style updates. TRIAGE-BC instead uses scarce positive and failure labels to calibrate which parts of an unlabeled mixed log should enter policy training.

The setting is also related to positive-unlabeled learning and data-quality work in imitation learning. The difference is that TRIAGE-BC has explicit scarce negatives and evaluates the downstream policy-training distribution, not just classifier accuracy or a trajectory-quality score. The empirical message is that score learning, support purity, and policy coverage must be treated together.

Robomimic-style sequence imitation provides the robotics backbone and evaluation discipline. The paper's robotics contribution is not a new sequence policy architecture; it is the support-conversion layer placed before the official BC-RNN-GMM learner, with positive-only retrieval and all-positive oracle controls kept in the main evidence.

## 3. Problem Setting

We consider an offline imitation setting with three trajectory sets:

```text
D+ = {tau_i+}: scarce trusted successful or desirable demonstrations
D- = {tau_i-}: scarce known failed or undesirable demonstrations
Du = {tau_iu}: a larger unlabeled mixed-quality log
```

No online training interaction is allowed. The learner may use membership in `D+` and `D-`, but it may not use hidden labels inside `Du` for score training, threshold selection, branch selection, checkpoint selection, or policy training. Hidden labels and environment rewards are reserved for audits, oracle diagnostics, and evaluation.

The objective is to train a policy that behaves like the desirable behavior represented by `D+`, while using `Du` when it contains useful state-action coverage and avoiding imitation of undesirable behavior represented by `D-`. The main method output is a policy-training distribution, not a reward function used for online reinforcement learning.

This framing differs from standard behavior cloning in two ways. First, the unlabeled log is not assumed to be uniformly expert. Second, the small failure set is not used as a dataset to avoid by itself; it is used to calibrate a desirability score over the mixed log.

## 4. Method

Figure 1 shows the TRIAGE-BC pipeline:

- `../results/final_paper/figures/triage_bc_method_diagram.png`

### 4.1 Tri-Signal Score Learning

TRIAGE-BC trains a binary state-action classifier:

```text
c_theta(s, a) -> [0, 1]
```

Transitions from `D+` are labeled `1`, transitions from `D-` are labeled `0`, and unlabeled transitions from `Du` are not used to train the score model. The robotics implementation uses observation-action features and the frozen classifier hyperparameters in `../METHOD_FREEZE.md`: 800 classifier steps, batch size 512, hidden dimension 128, depth 2, learning rate `1e-4`, and sigmoid output probabilities.

### 4.2 Trajectory Score Calibration

For each trajectory, TRIAGE-BC computes a mean trajectory score:

```text
g(tau) = mean_t sigmoid(c_theta(s_t, a_t)).
```

Diagnostics also record score minima, percentiles, and histograms, but the frozen method uses mean score for support conversion. Let `mu+` and `mu-` be the mean trajectory scores over labeled positives and labeled negatives. TRIAGE-BC estimates the positive mass in the unlabeled log by:

```text
p_u(tau) = clip((g(tau) - mu-) / (mu+ - mu- + 1e-8), 0, 1)
m_hat = sum_tau p_u(tau).
```

This gives a hidden-label-free estimate of how much useful support may exist in `Du`.

### 4.3 Support Conversion

TRIAGE-BC v0.1 uses a small family of support converters.

Adaptive mass-capped hard support sorts unlabeled trajectories by score, computes a score-gap support set subject to a minimum coverage floor, estimates positive mass, and caps the selected support when the gap-selected set is too broad relative to `m_hat`. If estimated positive mass is too small, it falls back to a precision-oriented top-`2n+` support.

Positive-minimum support selects unlabeled trajectories whose score exceeds the minimum labeled-positive trajectory score. This branch is intended for score shapes where labeled positives have high scores and many unlabeled trajectories exceed the positive minimum.

The weighted sampler trains on `D+ union Du` with labeled positives weighted as `1` and unlabeled demos weighted by `max(0.05, g(tau))`. In TRIAGE-BC v0.1, this is a required baseline and diagnostic branch rather than the main router output.

Positive-only nearest-neighbor support is a required no-bad-label baseline. It selects unlabeled demos nearest to labeled positives and does not use `D-`.

### 4.4 Hidden-Label-Free Router

Router v2 chooses the main TRIAGE-BC hard-support branch using only score-shape features:

```text
if estimated_positive_mass >= 800 and count_ge_pos_min >= 400:
    abstain
elif labeled_positive_p10 >= 0.85 and count_ge_pos_min >= 80:
    use hard pos-min support
else:
    use hard adaptive masscap support
```

The abstention branch is important. Can MG-style score shapes can contain a large high-score plateau where simple hard support and simple branch proxies are unreliable. In those cases, TRIAGE-BC reports diagnostics rather than forcing a main positive claim.

### 4.5 Frozen v0.2 Portfolio Router

After the v0.1 diagnostics, we froze a small v0.2 portfolio router before fresh Can 40p/80b and Lift MG split seeds `101`, `202`, `303`, `404`, and `505`. The v0.2 router uses the same score model and computes only two branch features from the unlabeled score shape: estimated positive mass `m_hat` and the number of unlabeled trajectories above the labeled-positive minimum score. If both are very large, the split is treated as a stress abstention. If mass and count are moderate, the router selects the soft weighted branch. Otherwise it selects hard positive-NN/risk-union support. This rule uses no hidden unlabeled labels for branch selection.

The v0.2 hard branch unions positive-only nearest-neighbor support with a rank-fusion support set that combines positive-neighbor rank and bad-aware action-risk rank. The soft branch is classifier-probability weighted BC on `D+ union Du` with weights clipped below by `0.05`. We treat this as a portfolio support converter, not as evidence that one fixed hard threshold or one fixed weighting rule is universally best.

### 4.6 Algorithmic Summary

The frozen TRIAGE-BC v0.1 procedure is:

1. Split the offline data into scarce labeled positives `D+`, scarce labeled negatives `D-`, unlabeled mixed trajectories `Du`, and held-out positive evaluation starts.
2. Train `c_theta(s, a)` only on transitions from `D+` and `D-`.
3. Score every trajectory with `g(tau)`, compute labeled score anchors `mu+` and `mu-`, and estimate unlabeled positive mass `m_hat`.
4. Compute hidden-label-free score-shape features: `m_hat`, the count of unlabeled trajectories above the minimum labeled-positive score, and the tenth percentile of labeled-positive trajectory scores.
5. Route the split. Large high-mass plateaus are abstained from; high positive-minimum score shapes use positive-minimum hard support; all other non-abstained splits use adaptive mass-capped hard support.
6. Train the policy with the frozen BC backbone on the selected support. For Robomimic this is official BC-RNN-GMM at a fixed 20k optimizer-step endpoint.
7. Report endpoint rollouts without best-checkpoint selection. Hidden labels are used only afterward for audit metrics such as selected-support purity, hidden-positive recall, and hidden-bad admission.

### 4.7 Policy Learning

For Robomimic, policies are trained with the official BC-RNN-GMM backbone: sequence length 10, two-layer LSTM with hidden dimension 400, actor MLP dimensions 1024/1024, five GMM modes, 200 epochs with 100 steps per epoch, and fixed endpoint reporting at epoch 200. This is 20k optimizer steps. No rollout is used during training, and no best-checkpoint selection is used for main claims.

For controlled PointNav, the policy learner is a lightweight behavior cloning policy trained on the selected or weighted support. The controlled task is used to isolate the support-recovery mechanism, not to claim robotics-scale policy learning.

## 5. Experiments

### 5.1 Controlled Continuous PointNav

The controlled PointNav task is designed so that positive labels alone are incomplete. Labeled positives are safe-route prefixes, while unlabeled trajectories contain hidden safe full routes and hidden shortcut failures. The method must recover useful hidden trajectories from the mixed log to solve the full route.

Primary artifacts:

- `../results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`
- `../results/final_paper/figures/pointnav_controlled_mechanism.png`

The strongest controlled setting uses only two positive prefixes and two bad shortcut trajectories. Score-gap support reaches `1.000` success at 50%, 75%, 90%, and 95% bad unlabeled data. All-demo cloning, positive-plus-unlabeled cloning, and local weighted BC degrade as contamination rises.

This result supports the mechanism claim: scarce explicit bad labels can calibrate hidden-good support recovery when positive labels do not cover the complete desired behavior.

### 5.2 Robomimic Frozen Endpoint Matrix

Robomimic experiments use low-dimensional official BC-RNN-GMM policies trained under the frozen method contract. Final endpoint evaluation uses 50 held-out validation-positive rollouts per split and fixed epoch-200 checkpoints.

Primary artifacts:

- `../results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`
- `../results/final_paper/figures/robotics_primary_endpoint_matrix.png`

Primary frozen rows:

- Can 40p/80b: split seeds 11, 22, and 33.
- Lift MG: split seeds 11, 22, and 33.

Diagnostic appendix rows:

- `../results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md` keeps the broader diagnostic endpoint matrix.
- Can 20p/80b: split-11 endpoint row plus split-22 positive-only versus TRIAGE endpoint extension.
- Can 80p/80b: split-33 endpoint comparison plus support audits.

### 5.3 Baselines

The key baselines are:

- all-demo BC: clone the full contaminated train log;
- classifier-probability weighted BC: train on positives and unlabeled demos with classifier-score weights;
- positive-only NN: no-bad-label nearest-neighbor support from labeled positives;
- all-positive oracle: diagnostic upper bound using hidden labels;
- classifier top-k and broader hard-support ablations for precision/coverage analysis.

Weighted BC is treated as a strong baseline, not as a strawman. Positive-only NN is also a strong baseline and is often the best non-oracle method on Can.

## 6. Results

### 6.1 Controlled PointNav Validates The Mechanism

In the hardest equal-label-budget PointNav setting, with only two positive route-prefix demos and two bad shortcut demos, score-gap support reaches perfect success at all tested bad fractions. This is the cleanest evidence that the tri-signal score can recover hidden-good support from a contaminated log.

The result should be interpreted as mechanism evidence. It shows that explicit bad labels can calibrate support recovery when positives are incomplete. It does not by itself prove that bad labels beat all positive-only retrieval methods on robotics datasets.

### 6.2 Can 40p/80b: Hard Support Beats Weighted BC, But Not Positive-Only NN

The completed frozen Can 40p/80b endpoint aggregate is:

```text
all-positive oracle: 147/150
positive-only NN top40: 108/150
TRIAGE-BC: 99/150
weighted BC: 90/150
all-demo BC: 81/150
```

TRIAGE-BC improves over weighted BC and all-demo cloning at the fixed 20k endpoint. This supports the claim that hard support can beat soft weighted sampling under action-conflicting contamination. However, positive-only NN top40 is the best non-oracle row, so Can 40p/80b does not support a claim that bad labels are necessary or that TRIAGE-BC beats strong no-bad-label retrieval.

### 6.3 Lift MG: Coverage Can Beat Purity

The completed frozen Lift MG endpoint aggregate is:

```text
all-positive oracle: 105/150
weighted BC: 93/150
positive-only NN top160: 82/150
TRIAGE-BC: 74/150
all-demo BC: 31/150
```

All-demo cloning is weak, confirming that contaminated logs can hurt. But weighted BC is strongest among non-oracle rows. TRIAGE-BC improves support purity, yet fixed endpoint policy performance trails broader coverage-sensitive baselines. This is a useful counterexample: high-purity hard support is not automatically the best policy-training distribution.

The primary uncertainty summary is:

- `../results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md`
- `../results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md`
- `../results/final_paper/figures/primary_endpoint_paired_deltas.png`

It should be used for final wording. On Can 40p/80b, TRIAGE-BC beats weighted BC on all three splits, but the pooled gap is modest (`+0.060`) and descriptive rollout-level Wilson intervals overlap. A paired bootstrap that averages repeated rollouts by validation initial state and resamples split seeds and initial states gives the same Can point delta (`+0.060`) with interval `[-0.113, 0.240]`. Positive-only NN is higher pooled. On Lift MG, weighted BC is higher pooled than TRIAGE-BC, and the paired bootstrap delta for weighted BC minus TRIAGE-BC is `+0.122` with interval `[-0.100, 0.317]`. The endpoint evidence should therefore be written as directional and coverage-sensitive rather than as a formal significance claim. The only primary paired-bootstrap comparison whose interval is strictly above zero is TRIAGE-BC over all-demo BC on Lift MG, `[0.211, 0.400]`.

### 6.4 Fresh v0.2 Portfolio Gate

The frozen v0.2 fresh gate uses split seeds `101`, `202`, `303`, `404`, and `505` for Can 40p/80b and Lift MG:

```text
Can 40p/80b selected hard union: 197/250
Can 40p/80b best baseline per split: 192/250
Lift MG selected weighted branch: 143/250
Lift MG best baseline per split: 146/250
Combined selected branches: 340/500
Combined best baselines per split: 338/500
```

On Can 40p/80b, the router chooses hard positive-NN/risk-union support and wins four of five fresh splits with margins `+8/50`, `+5/50`, `+3/50`, `-12/50`, and `+1/50`. On Lift MG, the router chooses soft weighted BC and wins two of five completed comparisons, with margins `-5/50`, `-4/50`, `-2/50`, `+1/50`, and `+7/50`. Paired initial-state bootstraps remain descriptive and cross zero for Can (`[-0.144, 0.168]`), Lift (`[-0.083, 0.140]`), and the combined gate (`[-0.074, 0.120]`). This is therefore a cautious fresh-gate result, not a green-light dominance claim or formal significance claim: Can provides a hard-union improvement with one severe reversal, while Lift shows that broad weighted coverage and hard support tie in aggregate but neither dominates per split.

Primary artifact:

- `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`

### 6.5 Precision/Coverage Tradeoff On Can

The Can 40p/80b support sweep shows why support conversion matters:

```text
TRIAGE adaptive masscap: 110/120 hidden positives, 80/240 hidden bad, endpoint 99/150
positive-only NN top40: 106/120 hidden positives, 14/240 hidden bad, endpoint 108/150
weighted full pool: full hidden-positive recall, full hidden-bad admission, endpoint 90/150
```

The Can 20p/80b diagnostic sharpens the same caveat:

```text
TRIAGE adaptive masscap: 54/60 hidden positives, 69/240 hidden bad, endpoints 46/100
positive-only NN top20: 49/60 hidden positives, 11/240 hidden bad, endpoints 54/100
weighted full pool: 18/50 on split 11 only
```

Bad labels help calibrate a score, but the current bad-aware converter can select too much contaminated support. Positive-only retrieval is cleaner on these Can diagnostics.

### 6.6 Score Shape And Abstention

Score-shape diagnostics explain why no single converter works everywhere. Can 40p/80b has moderate positive/bad overlap, motivating adaptive mass-capped hard support. Lift MG has stronger score separation, but policy performance still favors weighted coverage. Can MG has a high-score plateau containing both positives and bad demos, which motivates router abstention.

The Can MG branch-proxy diagnostic shows that simple positive and negative likelihood proxies are not enough. On original Can MG, the rollout-best fixed-20k method is weighted BC, but the tested likelihood proxies choose all-positive support. On shuffled Can MG, proxy selection cannot detect that both hard and soft branches are weak. The active-abstention audit quantifies the stress case: original/shuffled Can MG have estimated mass/count `1947.9`/`1025.7` and `1466.3`/`515.7`, original MG proxies match best success in `0/6` cases, and shuffled MG gets `6/6` only because both staged forced branches reach `0.100`. This supports abstention rather than overconfident branch choice.

### 6.7 Precision/Coverage View

The empirical results can be summarized by two support-side quantities that are only available for audit: hidden-positive recall and hidden-bad admission. For a selected unlabeled support set `S` and hidden positive set `G`, recall is `|S intersect G| / |G|` and bad admission is `|S \ G| / |Du \ G|`. A hard selector improves behavior cloning when it removes action-conflicting bad support faster than it loses useful coverage. It fails when the removed trajectories contain state-action coverage that the sequence policy needs.

The frozen mass-capped rule is a hidden-label-free approximation to this tradeoff. The positive-mass estimate `m_hat` prevents a score-gap rule from expanding far beyond the inferred useful mass, while the positive-minimum branch allows broader coverage when labeled positives have consistently high scores and many unlabeled trajectories clear that threshold. The abstention branch handles large high-score plateaus where the score shape does not provide a reliable hard/soft decision.

This view explains the main reversals. Can 40p/80b contains action-conflicting contamination, so TRIAGE-BC can beat weighted BC by selecting less of the mixed log, although positive-only NN finds an even cleaner support frontier. Lift MG shows the opposite failure mode: TRIAGE-BC selects very pure support, but the policy endpoint favors broader weighted coverage. The target for future work is therefore not a universal hard filter, but a hidden-label-free policy-quality proxy that predicts when additional coverage is worth additional contamination.

## 7. Simple Precision/Coverage Analysis

This section gives a lightweight model for the empirical precision/coverage tradeoff. It is not a formal guarantee for nonlinear sequence BC; it is an organizing decomposition that explains why neither the purest support nor the broadest weighted support is uniformly optimal.

Assume the unlabeled log is a mixture of hidden useful and harmful trajectories:

```text
Du ~ pi_g * P_g + (1 - pi_g) * P_b
```

Here `P_g` denotes desirable hidden support and `P_b` denotes harmful or action-conflicting support. A threshold or support rule induces a selected set `S_t` with hidden-good recall `r_t` and hidden-bad admission `f_t`. If `N_g` and `N_b` are the hidden-good and hidden-bad counts in `Du`, then `r_t N_g` useful trajectories reduce estimation and coverage error, while `f_t N_b` harmful trajectories create an imitation-contamination penalty.

A schematic excess-risk decomposition for behavior cloning on `D+ union S_t` is:

```text
R(pi_hat_t) - R(pi_g)
  <= coverage_penalty(n+ + r_t N_g)
   + contamination_penalty(f_t N_b / (n+ + |S_t|)).
```

The first term favors larger selected support when useful state-action coverage is scarce. The second term favors more selective support when admitted bad trajectories contain actions that conflict with the desired behavior. The optimal support threshold is therefore not necessarily the purest threshold: when the coverage term dominates, admitting additional imperfect trajectories can still improve policy learning.

**Proposition 1 (coverage-contamination criterion).** Under the mixture model above, adding an unlabeled trajectory should improve the hard-selector bound exactly when its marginal coverage gain exceeds its normalized marginal contamination cost. Let `m_t = |S_t|`, `g_t = r_t N_g`, and `b_t = f_t N_b`. If a candidate unlabeled trajectory is useful with score-implied probability `q` and harmful with probability `1-q`, then the hard-support bound decreases whenever:

```text
A * (1 / sqrt(n+ + g_t) - 1 / sqrt(n+ + g_t + q))
  >
C * ((b_t + 1 - q) / (n+ + m_t + 1) - b_t / (n+ + m_t)).
```

The left side is the expected coverage gain; the right side is the expected increase in bad-action mass after normalizing by the enlarged training set. This proposition explains why neither maximum purity nor maximum coverage is uniformly correct. A pure but tiny support can be suboptimal when the coverage gain remains large for moderately risky trajectories, while hard filtering wins when extra trajectories mostly add action-conflicting failures.

For a weighted sampler with trajectory weights `w(tau)`, the analogous view replaces selected count with effective sample size and bad count with bad weight mass:

```text
R(pi_hat_w) - R(pi_g)
  <= coverage_penalty(n+ + ESS(w))
   + contamination_penalty(sum_{bad tau} w(tau) / (n+ + sum_tau w(tau))).
```

Soft weighting can win when broad coverage is essential and bad-action mass is low or weakly conflicting. Hard support can win when bad-action mass is high and score rankings can remove it without losing too much useful coverage.

TRIAGE-BC v0.1 can be read as a hidden-label-free approximation to these two terms. The positive-mass estimate `m_hat` limits selected support when the score shape suggests that additional trajectories are more likely to add contamination than coverage. The positive-minimum branch broadens support when labeled positives occupy a high-score region with many unlabeled neighbors. The abstention branch handles score shapes where the method cannot reliably estimate the balance between the two terms. This analysis also explains why positive-only retrieval is a critical baseline: it can lie on a better precision/coverage frontier even without negative labels.

## 8. Discussion

The main empirical lesson is that tri-signal labels are useful, but their value is mediated by support conversion. A classifier score is not the policy. A high-purity selected set is not always enough. A broad weighted set is not always safe. Different tasks occupy different parts of the precision/coverage landscape.

The strongest positive result for TRIAGE-BC as a method is not universal dominance. It is a conditional pattern: hard selected support can improve over weighted BC and all-demo cloning on Can contamination and generated action-conflict or coverage-shift probes, while frozen v0.2 is only barely positive overall by choosing hard union on fresh Can and weighted coverage on fresh Lift. Controlled PointNav and generated Can diagnostics explain why scarce bad labels can be mechanistically valuable. The strongest limitation is equally important: positive-only NN is often stronger on Can, weighted BC remains the right branch on Lift-like broad-coverage rows, and generated split constructions are not intended to replace default benchmark rows.

These findings suggest that future work should focus on hidden-label-free policy-quality prediction, task-aware coverage criteria, and better support conversion. The problem should not be framed as hard filtering versus soft weighting in the abstract. It should be framed as choosing a policy-training distribution under uncertainty about support quality and coverage.

## 9. Limitations

TRIAGE-BC is not a validated inverse-Q robotics method. It is a score-calibrated imitation method using a strong BC-RNN-GMM backbone.

Positive-only NN is the strongest non-oracle row on frozen Can 40p/80b and on the completed Can 20p/80b diagnostic endpoint splits. Therefore, bad labels are not strictly necessary in the current Can results.

Weighted BC is strongest on the original frozen Lift MG matrix and is the selected v0.2 branch on fresh Lift. Therefore, hard support is not uniformly better than soft weighting.

The fresh v0.2 gate is a selected-vs-strong-baseline/v0.1 audit. Optional fresh all-demo/all-positive diagnostic rows remain incomplete and are not part of the claimed fresh leaderboard.

Can MG remains a stress diagnostic. Router v2 abstention is more honest than claiming success on ambiguous high-score plateaus.

Square and Transport are currently support-side relative-quality diagnostics, not failure-demo policy benchmarks.

The evaluation uses 50 endpoint rollouts per split. This is stronger than earlier 10-episode screens, but repeated rollouts from the same validation-positive start pool are not fully independent. Claims should report split-level and endpoint-count context.

## 10. Conclusion

TRIAGE-BC reframes offline imitation from scarce successes, scarce failures, and mixed logs as a score-to-support conversion problem. The results show that tri-signal scores can recover useful hidden support, that hard support can beat soft weighting in some contaminated settings, and that a frozen portfolio router is barely positive on a fresh Can+Lift gate by selecting different support conversions in different regimes. They also show that strong no-bad-label retrieval and broad weighted coverage are essential baselines. The central claim is therefore precise: support calibration is the bottleneck, and reliable hidden-label-free conversion from scores to policy-training data is the next algorithmic step.

## Appendix A. Diagnostic Endpoint And Support Evidence

The broader diagnostic endpoint matrix is staged as:

- `../results/final_paper/figures/robotics_current_endpoint_matrix.png`
- `../results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md`

This appendix includes Can 20p/80b and Can 80p/80b as diagnostic rows only. They are not promoted to main claims because they are not complete three-split endpoint tables.

Bad-label control summary:

This is the Bad-label versus positive-only control summary. On Can 40p/80b,
TRIAGE-BC recovers 110 versus 106 hidden positives but admits 80 versus 14
hidden bad demos, so the endpoint caveat remains essential.

| setting | bad-aware endpoint | no-bad/control endpoint | support-side interpretation |
|---|---|---|---|
| PointNav `n+=5`, `n- in {1,2,5}` | gap support min/mean `0.973/0.997` | BC-all `0.292`; local weighted `0.131` | Pure selected support in every row: demo purity `1.000` and `0 hidden-bad` demos. This supports label-efficient calibration, not Can bad-label necessity. |
| Can 40p/80b | TRIAGE-BC `99/150` | positive-only NN `108/150` | TRIAGE-BC recovers slightly more hidden positives, `110` versus `106`, but admits many more hidden bad demos, `80` versus `14`. |
| Can 20p/80b | TRIAGE-BC `46/100` | positive-only NN `54/100` | TRIAGE-BC recovers `54/60` hidden positives versus `49/60`, but admits `69/240` hidden bad versus `11/240`. |
| Can 80p/80b | TRIAGE-BC `43/50` | positive-only NN `49/50` | The balanced diagnostic also favors positive-only retrieval; broader coverage wins despite the bad-aware score. |
| Lift MG | TRIAGE-BC `74/150` | positive-only NN `82/150` | Bad-aware pos-min support is much purer, `421` hidden positives and `20` hidden bad versus `342` and `138`, but the fixed endpoint still trails. |

Hard-negative Can targeted diagnostic:

The generated hard-negative split makes some bad demos close in state space to
labeled positives while disagreeing in action. This reverses the usual Can
positive-only caveat: the bad-aware hybrid reaches `104/150` endpoint successes
and selects `113` hidden positives with only `7` hidden bad demos, while
state-action positive-NN top40 reaches `91/150` and selects `70` hidden
positives with `50` hidden bad demos. This is targeted generated-diagnostic
evidence for explicit bad-label utility under near-neighbor action conflict,
not a primary benchmark row. In prose form, this is 113 hidden positives and 7
hidden bad for the hybrid versus 70 hidden positives and 50 hidden bad for
state-action positive-NN top40. Equivalently, the hard-negative diagnostic
selects 113 hidden positives and 7 hidden bad for the hybrid versus 70 hidden
positives and 50 hidden bad for state-action positive-NN top40.

| support rule | hidden pos | hidden bad | endpoint | avg len |
|---|---:|---:|---:|---:|
| bad-aware hybrid top40 | `113` | `7` | `104/150` | `198.9` |
| state-action positive-NN top40 | `70` | `50` | `91/150` | `223.3` |

Coverage-shift Can targeted diagnostic:

The generated coverage-shift split chooses labeled positives from a narrow
initial-object-pose cluster while hidden positives cover other successful
clusters and hidden bad demos are spread across initial conditions. The
bad-aware-heavy hybrid reaches `120/150` endpoint successes and selects `118`
hidden positives with only `2` hidden bad demos, while state-action
positive-NN top40 reaches `103/150` and selects `105` hidden positives with
`15` hidden bad demos. This is targeted generated-diagnostic evidence for
explicit bad-label utility when trusted positives under-cover initial
conditions, not a primary benchmark row. In prose form, this is 118 hidden
positives and 2 hidden bad for the hybrid versus 105 hidden positives and 15
hidden bad for state-action positive-NN top40. Equivalently, the coverage-shift
diagnostic selects 118 hidden positives and 2 hidden bad for the hybrid versus
105 hidden positives and 15 hidden bad for state-action positive-NN top40.

| support rule | hidden pos | hidden bad | endpoint | avg len |
|---|---:|---:|---:|---:|
| bad-aware-heavy hybrid top40 | `118` | `2` | `120/150` | `182.7` |
| state-action positive-NN top40 | `105` | `15` | `103/150` | `207.5` |

Prefix-positive Can targeted diagnostic:

The generated prefix-positive split mirrors the controlled PointNav mechanism in
Robomimic. Trusted positives are only early prefixes from successful Can demos,
failed demos are explicit negatives, and full successful and failed demos are
hidden in the unlabeled pool. Prefix bad-aware state top80 reaches `119/150`
endpoint successes and selects `195` hidden positives with `45` hidden bad
demos, while prefix state-action positive-NN top80 reaches `6/150` and selects
`37` hidden positives with `203` hidden bad demos. This is targeted
generated-diagnostic evidence for explicit bad-label utility when trusted
positives are incomplete, not a primary benchmark row. In prose form, this is
195 hidden positives and 45 hidden bad for the bad-aware prefix selector versus
37 hidden positives and 203 hidden bad for prefix state-action positive-NN.

| support rule | hidden pos | hidden bad | endpoint | avg len |
|---|---:|---:|---:|---:|
| prefix bad-aware state top80 | `195` | `45` | `119/150` | `171.3` |
| prefix state-action positive-NN top80 | `37` | `203` | `6/150` | `388.3` |

Generated regime-probe summary:

`results/final_paper/tables/generated_regime_probe_summary_REPORT.md` stages the
concise main-paper table for the three endpoint-backed generated Can probes.
These are controlled split constructions, not default Robomimic benchmark rows.

| probe | bad-aware endpoint | positive-only endpoint | delta | support selected (pos/bad) |
|---|---:|---:|---:|---|
| Hard-negative Can | `104/150` | `91/150` | `+13/150` | `113/7` vs `70/50` |
| Coverage-shift Can | `120/150` | `103/150` | `+17/150` | `118/2` vs `105/15` |
| Prefix-positive Can | `119/150` | `6/150` | `+113/150` | `195/45` vs `37/203` |

Diagnostic summary:

| diagnostic | evidence | endpoint | takeaway |
|---|---|---|---|
| PointNav bad-label count | Fixed 5 positives with `1/2/5` labeled bad shortcuts | `1 labeled bad shortcut` and 5 labeled bad shortcuts both reach `1.000` gap-demo success at every tested contamination level; the 2-bad setting dips to `0.973` and `0.993` at 90% and 95% bad data | Selected support has `1.000` demo purity, `1.000` transition purity, and `0 hidden-bad` demos in every row; this is label-efficiency evidence for the controlled mechanism, not a Can bad-label-necessity claim. |
| Can 20p/80b | Three-split support audit plus two completed endpoint splits | positive-only `54/100`, TRIAGE-BC `46/100`, weighted split-11 `18/50` | TRIAGE-BC recovers more hidden positives, `54/60` versus `49/60`, but admits more hidden bad demos, `69/240` versus `11/240`. |
| Can 80p/80b | Three-split support audit plus split-33 endpoint | positive-only `49/50`, TRIAGE-BC `43/50` | Even when TRIAGE-BC selects purer split-33 support, positive-only retrieval keeps better coverage and wins the endpoint. |
| Can MG | Branch-proxy diagnostic on original and shuffled MG | original weighted `0.333` is rollout-best; simple proxies choose all-positive at `0.200` | Positive/negative likelihood proxies do not replace abstention because they miss coverage-sensitive rollout quality. |
| Active abstention | Router-v2 stress audit over original and shuffled Can MG | assigned rows average `0.700`; abstained rows average `0.217` and top out at `0.333` | Abstention is justified as risk control for ambiguous high-mass score plateaus, not as endpoint dominance. |
| Policy-quality proxy no-go | Consolidated likelihood, rejection, purity, recall, coverage, and initial/transition coverage checks | deployable proxy attempts match endpoint winners in only `2/11` rows; audit-only support rows match `3/6` rows | Policy-quality prediction remains open: no tested simple support score replaces endpoint validation or abstention. |
| Hard-union component ablation | Can 40p/80b positive-only, risk-fusion, union, classifier-only, weighted, and v0.1 support components | union `119/120` hidden positives, `16/240` hidden bad demos, and `116/150` endpoint successes; positive-only `108/150`, risk-fusion `73/100`, weighted `90/150`, v0.1 masscap `99/150`; classifier-only is support-only | The union works by preserving the positive-only anchor and adding risk-derived coverage; its pooled gain comes from splits 22 and 33, not uniform dominance. |
| Failure-mode initial-state audit | Three paired Can 40p/80b initial states comparing positive-only, weighted, hard-union, and all-demo policies | union rescue split `33` / `demo_105`: union `5/5` versus positive-only `0/5` and all-demo `0/5`; positive-anchor regression split `11` / `demo_39`: positive-only `5/5` versus union `0/5`; soft-pool rescue split `33` / `demo_99`: weighted `5/5` versus union `1/5` | This is qualitative appendix intuition from existing endpoint metrics. Grasp and loop/miss fields are success and horizon-length proxies, not video-level labels. |
| Hard-negative Can | Generated three-split action-conflict diagnostic | bad-aware hybrid `104/150`, state-action positive-NN top40 `91/150` | Explicit bad labels help when bad demos are near-neighbor action conflicts; keep this separate from the primary benchmark rows. |
| Hard-negative Lift | Generated three-split non-Can action-conflict diagnostic | bad-aware proxy top40 `15/150`, state-action positive-NN top40 `5/150` | The endpoint effect is directionally consistent with the support audit: bad-aware selects `82/120` hidden positives with `38/240` hidden bad demos versus `12/120` and `108/240` for positive-NN. Equivalently, the endpoint aggregate selects 82 hidden positives and 38 hidden bad demos versus 12 hidden positives and 108 hidden bad demos. Absolute success is low, so this is exploratory mechanism evidence, not a primary benchmark endpoint claim. |
| Coverage-shift Can | Generated three-split scarce-positive coverage-shift diagnostic | bad-aware-heavy hybrid `120/150`, state-action positive-NN top40 `103/150` | Explicit bad labels help when trusted positives under-cover initial conditions; keep this separate from the primary benchmark rows. |
| Prefix-positive Can | Generated three-split prefix-positive diagnostic | prefix bad-aware state top80 `119/150`, prefix state-action positive-NN top80 `6/150` | Explicit bad labels help when trusted positives are only incomplete successful-demo prefixes; keep this separate from the primary benchmark rows. |
| Prefix-length robustness | Support-only sweep varying generated Can prefix-positive label length | bad-aware state top80 beats matched prefix positive-NN top80 at short/default/long prefixes with recall deltas `+0.400`/`+0.658`/`+0.737` and bad-admission deltas `-0.400`/`-0.658`/`-0.737` | The prefix-positive mechanism is not a one-point artifact of the default prefix length, but this is not a new endpoint result. |
| Action-risk v0.2 no-go | Can 40p/80b split-11/22 endpoint gate for support-clearing action-risk candidates | positive-NN/risk fusion `0.820` versus positive-only NN `0.840` on split 11; `0.640` versus `0.760` on split 22 | The candidate selects 39 hidden positives with 1 hidden bad on split 11 and 40 hidden positives with 0 hidden bad on split 22, but it does not beat the endpoint baseline; support purity alone is not a deployable policy-quality proxy. |
| SOTA-candidate sweep no-go | Focused six-family short-screen sweep in `results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md` | best Can404 candidates `16/20` versus positive-only `17/20`; CCG transfer `10/20` versus positive-only `12/20`; anchored IQL-AWBC `13/20` | SM-RWBC, CAU-BC, CCG-Distill, SafeExpand, Demo-DPO, and simple IQL-AWBC should not be promoted or scaled unchanged; this is claim-boundary evidence. |
| Lift MG top160 | Fixed classifier-score top160 ablation over three splits | classifier top160 `68/150`, TRIAGE-BC `74/150`, positive-only `82/150`, weighted `93/150` | A broader high-purity classifier top-k rule does not rescue Lift; policy quality needs more than support purity. |

The diagnostic rows are consistent with the main claim. Bad labels can improve score calibration and hard support can beat soft weighting on the completed Can 40p/80b matrix, but the current converter is not on the best Can precision/coverage frontier. Positive-only retrieval is cleaner on Can 20p/80b and stronger on the Can 80p/80b endpoint diagnostic. The generated hard-negative, coverage-shift, and prefix-positive diagnostics show settings where explicit failures help beyond positive-only retrieval; the Lift hard-negative extension shows directional non-Can transfer but with low absolute success. Can MG, the action-risk v0.2 no-go, and the SOTA-candidate sweep no-go show that simple branch-quality proxies and short-screen transition objectives are inadequate, and Lift MG shows that high-purity support can still under-cover the policy learner.

## Artifact Map

Main plan and claim files:

- `../tri_piql_paper_completion_plan.md`
- `../PAPER_DRAFT_OUTLINE.md`
- `../METHOD_FREEZE.md`
- `../METHOD_FREEZE_V02.md`
- `../results/PAPER_CLAIM_PACKAGE.md`
- `../results/paper_tables/claim_matrix.csv`

Main figures:

- `../results/final_paper/figures/triage_bc_method_diagram.png`
- `../results/final_paper/figures/pointnav_controlled_mechanism.png`
- `../results/final_paper/figures/robotics_primary_endpoint_matrix.png`
- `../results/final_paper/figures/can40_precision_coverage.png`
- `../results/final_paper/figures/score_shape_diagnostics.png`
- `../results/final_paper/figures/primary_endpoint_paired_deltas.png`
- `../results/final_paper/figures/can_prefix_positive_diagnostic.png`

Main tables and reports:

- `../results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`
- `../results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`
- `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`
- `../results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md`
- `../results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md`
- `../results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md`
- `../results/final_paper/tables/primary_endpoint_paired_deltas_REPORT.md`
- `../results/final_paper/tables/bad_label_control_summary_REPORT.md`
- `../results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`
- `../results/final_paper/tables/active_abstention_evaluation_REPORT.md`
- `../results/final_paper/tables/hard_union_component_ablation_REPORT.md`
- `../results/final_paper/tables/failure_mode_initial_states_REPORT.md`
- `../results/final_paper/tables/can_prefix_length_robustness_REPORT.md`
- `../results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md`
- `../results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md`
- `../results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`
- `../results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`
- `../results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md`
- `../results/final_paper/ablations/can40_score_support_tradeoff_REPORT.md`
- `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`
- `../results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`
- `../results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`
- `../results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md`
- `../results/final_paper/tables/v02_policy_coverage_diagnostic_REPORT.md`
- `../results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`
- `../results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`

## Remaining Draft TODOs

1. Confirm the final venue/year and refresh the provisional ICLR 2026 style files if needed.
2. Add formal statistical tests only if the target venue expects them; the current draft has descriptive uncertainty language.
3. Copy-edit the ICLR source for compression and readability without changing the claim contract.

Resolved: result ordering is PointNav-first mechanism evidence, followed by
Robomimic endpoint evidence and caveats. A provisional ICLR-format source exists
at `../paper/iclr2026/main.tex`.
