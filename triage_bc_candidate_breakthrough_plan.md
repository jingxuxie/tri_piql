# TRIAGE-BC Candidate-Breakthrough Plan

## Goal

The current bottleneck is not score learning. The bottleneck is that the paper-facing candidate does not reliably outperform the strongest baselines: positive-only NN on Can-like settings and weighted BC on Lift-like settings. The next phase should stop tuning thresholds and instead test candidates that can **strictly subsume the strengths of both baselines**:

- keep the clean anchor of positive-only retrieval;
- retain broad weighted coverage when coverage matters;
- use bad demonstrations at the transition/action level, not only at the trajectory-selection level;
- avoid forcing one dataset-level branch when different initial states require different branches.

This plan proposes a concrete path to a much stronger candidate suitable for an ICLR/NeurIPS/ICML-style methods claim.

---

## 1. Current failure diagnosis

### Current evidence pattern

The present evidence is strong enough for a careful empirical paper, but not for a methods-dominance paper.

- v0.2 fresh Can+Lift gate: selected branches reach `340/500` versus `338/500` for best per-split non-oracle baselines.
- Can 40p/80b: v0.2 hard union reaches `197/250` versus `192/250`, but split 404 has a severe reversal: `27/50` versus positive-only `39/50`.
- Lift MG: v0.2 selects weighted BC and reaches `143/250`, below best per-split baselines at `146/250`.
- Router-regret: v0.2 has regret `23/500` on completed Can+Lift rows, but always-hard support also has regret `23/500`; therefore v0.2 is not yet a clearly superior router.
- Proxy no-go: simple policy-quality proxies do not reliably identify endpoint winners.

### Key conclusion

The main problem is **not** that bad labels are useless. The generated regime probes show they can help substantially. The problem is that the current method uses bad labels too coarsely:

- hard support discards coverage;
- soft weighting keeps bad actions;
- dataset-level routing cannot handle initial-state-specific branch differences;
- support purity does not reliably predict endpoint quality.

---

## 2. New target: a candidate that subsumes the baselines

The next candidate should not try to beat positive-only NN by replacing it, or beat weighted BC by replacing it. It should **contain both** and add bad-label information where it helps.

Target claim:

> Bad demonstrations improve offline imitation when they are used to shape transition-level risk or policy-level gating, rather than only to select trajectories. A candidate that combines positive anchors, weighted coverage, and bad-action repulsion can outperform both positive-only retrieval and weighted BC across Can-like and Lift-like regimes.

---

## 3. Candidate A: Transition-Risk Weighted BC, the highest-ROI first attempt

### Name

`TRIAGE-TWBC`: Transition-level risk-weighted behavior cloning.

### Motivation

Current weighted BC uses broad coverage but retains action-conflicting bad behavior. Current hard support removes bad demos but loses useful coverage. A transition-level method should keep coverage while suppressing bad actions.

### Core idea

Train on `D+ ∪ Du`, but weight each transition, not each trajectory:

\[
\mathcal{L}_{\text{TWBC}} =
- \mathbb{E}_{(s,a) \sim D^+ \cup D^u}
\left[w(s,a) \log \pi(a|s)\right]
+ \lambda_{neg} \mathcal{L}_{neg}
+ \lambda_{anchor} \mathcal{L}_{anchor}.
\]

Use

\[
w(s,a) = \operatorname{clip}(p_{good}(s,a), w_{min}, 1)
          \cdot \exp(-\lambda_r r_{bad}(s,a)),
\]

where:

- `p_good(s,a)` is the classifier probability;
- `r_bad(s,a)` is a local bad-action risk score;
- `w_min` preserves coverage instead of collapsing to positive-only support.

### Bad-action risk score

For each transition `(s,a)`, compute:

1. nearest-neighbor distance from `s` to labeled positive states;
2. nearest-neighbor distance from `s` to labeled bad states;
3. action conflict with bad actions in nearby states;
4. optional classifier uncertainty.

A simple risk score:

\[
r_{bad}(s,a) =
\alpha \cdot \operatorname{BadNeighbor}(s)
+ \beta \cdot \operatorname{ActionConflict}(s,a)
+ \gamma \cdot (1 - c_\theta(s,a)).
\]

### Negative unlikelihood loss

For labeled bad transitions, add an explicit repulsion term:

\[
\mathcal{L}_{neg} =
\mathbb{E}_{(s,a^-)\sim D^-}
\left[\max(0, \log \pi(a^-|s) - \log \pi(a^+_{NN}|s) + m)\right],
\]

where `a^+_NN` is the action from the nearest positive state. This says: at bad-like states, the policy should prefer the nearest positive action over the labeled bad action by margin `m`.

For GMM policies, approximate `log π(a|s)` using the GMM log probability already used for BC loss.

### Why this can beat both baselines

- Compared with positive-only NN: it uses more coverage from `Du`.
- Compared with weighted BC: it suppresses bad actions at transition level.
- Compared with hard union: it does not discard full trajectories because of a few risky actions.

### Implementation steps

1. Modify the Robomimic weighted sampler to emit per-transition weights rather than per-demo weights.
2. Add optional negative unlikelihood on `D-` transitions.
3. Add a config block:

```yaml
method: triage_twbc
w_min: [0.02, 0.05, 0.10]
lambda_risk: [0.5, 1.0, 2.0]
lambda_neg: [0.1, 0.3, 1.0]
margin: [0.2, 0.5, 1.0]
normalize_weights: true
ess_floor: 0.25
```

4. Start with Can 40 split 404 and Lift split 101/202, because these are where the current candidate fails.
5. If the small sweep works, freeze the best setting and run the full matrix.

### Fast gate

Run only 10k or 20k endpoint on:

- Can 40p/80b split 404;
- Can 40p/80b split 505;
- Lift MG split 101;
- Lift MG split 303;
- generated hard-negative Can split 101.

Pass condition:

- beats positive-only on Can split 404 by at least `+5/50`, or at least closes half the current gap;
- does not lose to weighted BC on Lift by more than `2/50`;
- beats weighted BC on at least one Can-like contaminated split.

---

## 4. Candidate B: Per-state policy mixture / gated specialist ensemble

### Name

`TRIAGE-MoE`: Mixture of support-specialist policies.

### Motivation

The failure-mode table already shows that different initial states prefer different branches:

- some states are rescued by hard union;
- some are better with positive-only NN;
- some require weighted BC.

A dataset-level router is too coarse. Use a **state-level gate**.

### Specialist policies

Train or reuse:

1. `π_pos`: positive-only NN support policy;
2. `π_union`: hard positive-NN/risk-union policy;
3. `π_weighted`: classifier-probability weighted BC policy;
4. optional `π_all`: all-demo BC as a low-priority fallback only for diagnostics.

### Gate input features

At each timestep, compute cheap hidden-label-free features:

- distance to positive support;
- distance to bad support;
- classifier score `cθ(s, a_i)` for each specialist action;
- specialist action disagreement;
- per-specialist log probability / entropy;
- whether current state is out-of-support for the positive-only policy;
- optional RNN hidden-state uncertainty proxy if available.

### Gate rule, first version

Avoid training a neural gate initially. Use a deterministic rule:

1. If `π_pos` is confident and the state is near positive support, use `π_pos`.
2. Else if `π_union` proposes an action with lower bad-action risk than `π_weighted`, use `π_union`.
3. Else use `π_weighted`.
4. If all branches have high risk or low support, abstain or use the least-risk branch.

### Gate rule, second version

Train a small logistic gate on held-out labeled positives and negatives:

- positive label: choose the specialist whose action has highest positive classifier score and nearest positive support;
- negative label: penalize specialists whose action resembles labeled bad actions.

No rollout labels or hidden unlabeled labels are used.

### Why this can beat baselines

It can preserve positive-only wins on split-specific anchors, use hard union on rescue states, and use weighted BC when broad coverage is needed. This directly targets the split-404 failure and Lift branch-selection weakness.

### Implementation note for RNN policies

Maintain all specialist RNN states during rollout. At each step:

1. query each policy for action and log probability;
2. compute gate features;
3. select or mix actions;
4. advance every policy's RNN state using the executed action if the implementation permits, or advance each with its own proposed action and audit drift.

Hard selection is simpler and safer than averaging continuous actions from GMM policies.

### Fast gate

Run on the same first five splits as Candidate A. Pass condition:

- improves Can 40 split 404 over hard union;
- does not reduce Can 40 splits 101/202/303 below positive-only or hard-union best by more than `2/50`;
- improves Lift split 303 over weighted or positive-only by using state-level fallback.

---

## 5. Candidate C: Sequence-mask BC instead of trajectory support

### Name

`TRIAGE-MaskBC`: risk-aware timestep masking for BC-RNN-GMM.

### Motivation

Robomimic policies are sequence models. Dropping entire trajectories is crude. Bad trajectories may contain useful early approach behavior; good trajectories may contain risky recovery actions. Use sequence masks inside the BC loss.

### Core idea

For each sequence chunk, keep it in training, but mask or downweight risky timesteps:

\[
\mathcal{L}_{MaskBC} =
- \sum_t m_t \log \pi(a_t | h_t, o_t),
\]

where

\[
m_t = \sigma(k(c_\theta(s_t,a_t)-\tau)) \cdot (1-r_{bad}(s_t,a_t)).
\]

Use a sequence-level minimum effective weight so that the RNN still sees temporal context even if some action losses are masked.

### Key ablation

Compare:

- demo-level hard support;
- demo-level weighted BC;
- transition-level weights;
- sequence-mask BC;
- sequence-mask BC + negative unlikelihood.

### Why this may be the strongest candidate

It is closest to the real Robomimic backbone: it changes the supervised loss while preserving recurrent context. It may solve both contamination and coverage without expensive RL.

---

## 6. Candidate D: Counterfactual hard-negative augmentation

### Name

`TRIAGE-CN`: counterfactual negative-action regularization.

### Motivation

Bad demos are most useful when they tell us what not to do in states close to good states. Use them to create counterfactual action negatives.

### Method

For each positive or high-score unlabeled state `s`, retrieve a nearby bad transition `(s^-, a^-)`. Add an unlikelihood or margin loss:

\[
\log \pi(a^+|s) \ge \log \pi(a^-|s) + m.
\]

This turns bad demos into local action constraints rather than trajectory filters.

### Best use

Add this as a regularizer to Candidate A or C, not as a standalone final method.

---

## 7. Experiments to run

### Stage 1: failure-focused fast screen

Run candidates A, B, and C on the hardest diagnostic splits first:

| Split | Reason |
|---|---|
| Can 40 split 404 | current v0.2 severe reversal |
| Can 40 split 505 | marginal win, tests stability |
| Can 40 split 101 | weighted is strong, tests contamination handling |
| Lift 101/202 | weighted loses to v0.1 hard support in current per-split oracle |
| Lift 303 | weighted and positive-only both weak |
| Hard-negative Can 101 | should favor bad-aware candidate |
| Coverage-shift Can 101 | should favor bad-aware candidate |

Use 50 endpoint rollouts per split, fixed epoch 200. If compute is tight, do one policy seed and only 3 candidate variants per method.

### Stage 2: full fresh gate

Promote only the best candidate to:

- Can 40p/80b split seeds `101/202/303/404/505`;
- Lift MG split seeds `101/202/303/404/505`;
- generated hard-negative Can `101/202/303`;
- generated coverage-shift Can `101/202/303`;
- prefix-positive Can `101/202/303` only if the method is applicable.

### Stage 3: stress and abstention

Run the candidate on Can MG original and shuffle42 only if it is naturally designed for high-score plateaus. Otherwise keep abstention.

### Stage 4: optional non-Can mechanism

Try a new Lift hard-negative or Lift coverage-shift split only if you can get absolute success above 25–30%. The current Lift hard-negative result is directionally useful but too low-success for a main claim.

---

## 8. Required baselines

Every promoted candidate must be compared against:

- positive-only NN;
- weighted BC;
- hard union;
- v0.1 TRIAGE-BC;
- all-demo BC where budget allows;
- all-positive oracle where diagnostic labels allow;
- candidate ablations.

For Candidate A / C, include:

- no risk term;
- no negative unlikelihood;
- no positive anchor;
- demo-level instead of transition-level weights;
- transition weights without sequence masks;
- sequence masks without negative unlikelihood.

For Candidate B, include:

- always positive-only;
- always weighted;
- always hard union;
- dataset-level v0.2 router;
- state-level gate without bad-risk features;
- state-level gate with bad-risk features.

---

## 9. Success criteria for a top-tier methods claim

To support a strong method claim, the new candidate should satisfy all of these:

1. **Can 40p/80b**: beats best per-split baseline by at least `+20/250` and wins at least 4/5 splits.
2. **Lift MG**: matches or beats best per-split baseline, with no large negative split.
3. **Combined Can+Lift**: beats best baselines by at least `+25/500`; paired-bootstrap interval should preferably be mostly positive.
4. **Generated probes**: matches or improves current bad-aware winners on hard-negative, coverage-shift, and prefix-positive Can.
5. **Ablation**: removing bad-action risk or negative unlikelihood should reduce performance in at least one action-conflict regime.
6. **Failure analysis**: explains split-level wins/losses with interpretable support, risk, and coverage diagnostics.
7. **No hidden labels**: hidden labels are not used for training, branch selection, checkpoint selection, or policy selection.

If these are not met, the correct submission remains a high-quality empirical precision/coverage study, not a dominance-method paper.

---

## 10. Concrete next two-week schedule

### Days 1–2: split-404 audit

Status as of 2026-06-26: completed a failure-focused preflight audit from
existing endpoint rollouts. The artifact is
`results/candidate_breakthrough/can40_split404_failure_audit_REPORT.md`, with
CSV companions for method summary, pairwise accounting, and per-initial-state
outcomes.

Key read:

- Positive-only NN remains the split-404 endpoint winner at `39/50`.
- v0.2 hard union reaches only `27/50`, despite selecting `39/40` hidden
  positives and `5/80` hidden bad demos versus positive-only `35/40` and
  `5/80`.
- v0.1 hard support reaches `36/50` and weighted BC reaches `33/50`.
- The severe reversal is therefore not explained by worse global support
  purity or hidden-positive recall. It points to sequence/action-distribution
  effects and state-specific branch choice after support is converted into a
  BC-RNN-GMM policy.

Decision:

- Prioritize Candidate A/C next: transition-level weighting or sequence masks
  should preserve the positive-only anchor while allowing risk-aware coverage.
- Candidate B remains relevant because per-initial-state flips show positive
  anchor regressions (`demo_89`, `demo_99`) and weighted-coverage rescue
  behavior (`demo_39`, `demo_189`).
- Do not spend more compute on global hard-support threshold tuning for this
  split.

Status as of 2026-06-26, Candidate A preflight:

- Added `scripts/summarize_candidate_a_transition_weight_preflight.py`.
- Generated transition-level Candidate A loss weights at
  `results/candidate_breakthrough/candidate_a_transition_weight_preflight/candidate_a_loss_weights.hdf5`,
  with audit report
  `results/candidate_breakthrough/candidate_a_transition_weight_preflight/candidate_a_transition_weight_preflight_REPORT.md`.
- The recipe uses the v0.2 split-404 hard-union pool: `54` train demos, `10`
  labeled-positive anchors, and `44` selected unlabeled demos (`39` hidden
  positive, `5` hidden bad). It computes nearest-transition action-conflict and
  bad-neighbor risks against labeled positive/negative transitions, then writes
  per-demo `data/<demo_id>/loss_weight` arrays for a BC-RNN-GMM loss hook.
- Preflight mass check: selected hidden-bad transitions are `0.082` of the
  unweighted selected-unlabeled pool and `0.045` of the weighted selected mass.
  Hidden-positive selected mass remains `2074.8` versus hidden-bad selected
  mass `98.3`, plus `1118.0` labeled-positive anchor mass.
- Caveat: this is not a policy result yet. The next step is a localized trainer
  hook that loads `loss_weight` and changes the GMM/RNN NLL to
  `-(log_probs * loss_weight).sum() / loss_weight.sum()`, followed by a short
  Can split-404 endpoint check.

Status as of 2026-06-26, Candidate A trainer smoke:

- Added `scripts/train_robomimic_official_transition_weighted.py`.
- The trainer wraps the Robomimic `SequenceDataset` to attach
  `loss_weight` sequences from the preflight HDF5 and patches the in-process
  BC GMM loss without editing `external/robomimic`.
- One-step CPU smoke passed on the split-404 union config with
  `--num-epochs 1 --epoch-steps 1 --batch-size 16 --device cpu`.
- Smoke log showed weighted-loss telemetry:
  `Loss_Weight_Mean=0.647809`, `Loss_Weight_Min=0.298574`,
  `Loss_Weight_Max=1.0`, `Loss=5.436787`.
- Smoke output is at
  `results/candidate_breakthrough/candidate_a_transition_weighted_smoke_train/candidate_a_transition_weighted_smoke/20260626015303/`.
  Duplicate `last*.pth` files were removed; `models/model_epoch_1.pth` remains
  as the smoke checkpoint.
- Completed the bounded GPU train/eval on Can split 404. The `50`-epoch
  checkpoint was only `1/20`, confirming that `5k` update steps is not a
  meaningful endpoint test for this policy class.

Status as of 2026-06-26, Candidate A endpoint screen:

- Ran parity `200`-epoch Candidate A training with checkpoints at epochs `100`
  and `200`:
  `results/candidate_breakthrough/candidate_a_tw_can404_e200_train/candidate_a_tw_can404_e200_seed0/20260626020204/`.
- Ran short first-20 evaluations: epoch `100` reached `9/20`, epoch `200`
  reached `12/20`; the `50`-epoch checkpoint reached only `1/20`.
- Ran a comparable `50`-episode endpoint eval for epoch `200`:
  `results/candidate_breakthrough/candidate_a_tw_can404_e200_eval50/REPORT.md`.
- Generated the comparison report
  `results/candidate_breakthrough/candidate_a_endpoint_screen_REPORT.md`.

Decision:

- Current Candidate A is not a breakthrough and should not be scaled unchanged.
  It improves over the v0.2 hard union (`30/50` versus `27/50`) but remains
  below weighted BC (`33/50`), v0.1 (`36/50`), and positive-only NN (`39/50`).
- The per-initial table is still useful: Candidate A recovers union failures on
  `demo_89` and improves `demo_39`/`demo_99`, but it collapses on positive-only
  strengths `demo_45` and `demo_189`. This points back to Candidate C/B:
  preserve strong anchor behavior while selectively borrowing coverage.

Status as of 2026-06-26, Candidate B router screen:

- Added `scripts/evaluate_robomimic_router_policy.py`, a reusable hard-router
  evaluator that loads multiple Robomimic policies, calls all policies every
  timestep to keep RNN states synchronized, and selects one action using
  labeled-support state-action margins.
- Ran three `20`-episode Can split-404 screens over positive-only and weighted
  BC:
  - labeled support with positive bias `0.25`: `15/20`;
  - labeled support with no bias: `16/20`;
  - positive-anchor support with no bias: `16/20`.
- Added `scripts/summarize_candidate_b_router_screen.py` and generated
  `results/candidate_breakthrough/candidate_b_router_screen_REPORT.md`.

Decision:

- Current Candidate B margin gate should not be scaled unchanged. Best
  deployable screen is `16/20`, below positive-only `17/20`.
- The non-deployable per-initial oracle over these rows is `19/20`, so routing
  has real headroom, but the margin gate trades failure modes: it recovers
  `demo_99` and sometimes `demo_39`, while losing `demo_189`.
- Next router attempt needs an initial-state or policy-confidence rule that
  preserves `demo_189` while identifying true coverage gaps. If no clean rule
  emerges quickly, move to Candidate C sequence masks.

Status as of 2026-06-26, Candidate B threshold follow-up:

- Ran two additional positive-anchor switch-threshold router screens over the
  positive-only and weighted BC policies:
  - threshold `0.10`: `16/20`;
  - threshold `0.05`: `14/20`.
- Regenerated
  `results/candidate_breakthrough/candidate_b_router_screen_REPORT.md` with the
  threshold rows and per-initial tradeoff.

Decision:

- Simple thresholding does not solve the router tradeoff. Threshold `0.10`
  recovers one `demo_189` rollout but loses one `demo_5` rollout; threshold
  `0.05` drops further.
- Do not spend a broad sweep on this margin-only router. A useful router needs
  additional confidence or initial-state features, not only a scalar switch
  threshold.

Status as of 2026-06-26, Candidate C sequence-mask screen:

- Added `scripts/summarize_candidate_c_sequence_mask_preflight.py`.
- Generated conservative sequence-mask loss weights at
  `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`
  with report
  `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_preflight_REPORT.md`.
- The preflight keeps the full weighted-pool training context (`130` demos),
  gives `50` positive-anchor demos full loss mass, and admits only high-score,
  positive-margin timesteps from extra weighted-pool demos. Extra selected mass
  is small: `186` positive timestep mass and `36` bad timestep mass, or `0.040`
  of all transitions.
- Trained a parity `200`-epoch BC-RNN-GMM with the mask using
  `scripts/train_robomimic_official_transition_weighted.py`; checkpoints are at
  `results/candidate_breakthrough/candidate_c_mask_can404_e200_train/candidate_c_mask_can404_e200_seed0/20260626023458/models/`.
- Endpoint first-20 results:
  - epoch `100`: `8/20`;
  - epoch `200`: `16/20`.
- Added `scripts/summarize_candidate_c_endpoint_screen.py` and generated
  `results/candidate_breakthrough/candidate_c_endpoint_screen_REPORT.md`.

Decision:

- Candidate C is mechanically plausible but not a breakthrough in this first
  recipe. Epoch `200` ties the best Candidate B router at `16/20`, beats
  weighted BC (`13/20`) and Candidate A (`12/20`), but remains below
  positive-only NN (`17/20`).
- Do not scale this mask recipe unchanged. The next plausible directions are
  explicit action-negative regularization or a richer confidence-preserving
  router; more global hard-support or scalar-threshold tuning is unlikely to
  change the split-404 bottleneck.

Status as of 2026-06-26, Candidate D negative-action screen:

- Added `scripts/summarize_candidate_d_negative_action_preflight.py`.
- Extended `scripts/train_robomimic_official_transition_weighted.py` with an
  optional negative-action hinge loss. The trainer now loads optional
  `negative_action` and `negative_loss_weight` arrays, computes
  `max(0, log pi(a_bad|s) - log pi(a_demo|s) + margin)`, and logs
  negative-hinge telemetry without editing `external/robomimic`.
- Generated the negative-action HDF5 at
  `results/candidate_breakthrough/candidate_d_negative_action_preflight/candidate_d_negative_action_weights.hdf5`.
  It uses the Candidate C mask (`5528` selected timesteps) and assigns each
  selected timestep the nearest labeled-negative action by low-dimensional
  observation distance.
- CPU smoke passed with hinge weight `0.1` and margin `0.5`; telemetry included
  `Negative_Hinge_Loss` and `Negative_Hinge_Active`.
- Trained a bounded `200`-epoch split-404 policy with checkpoints at epochs
  `100` and `200`:
  `results/candidate_breakthrough/candidate_d_neg0p1_can404_e200_train/candidate_d_neg0p1_can404_e200_seed0/20260626030303/models/`.
- First-20 endpoint results:
  - epoch `100`: `14/20`;
  - epoch `200`: `13/20`.
- Added `scripts/summarize_candidate_d_endpoint_screen.py` and generated
  `results/candidate_breakthrough/candidate_d_endpoint_screen_REPORT.md`.

Decision:

- Candidate D is not a breakthrough in this full-anchor form. It is below
  Candidate C (`16/20`) and positive-only NN (`17/20`), and its best checkpoint
  only matches v0.1 hard support (`14/20`).
- The per-initial table shows the hinge still does not recover `demo_39`, while
  it gives up anchor strengths on `demo_29`, `demo_89`, `demo_99`, or
  `demo_189` depending on checkpoint.
- Do not scale this Candidate D recipe unchanged. If revisited, restrict the
  negative-action loss away from full-weight positive-anchor timesteps. The more
  promising next route is a confidence-preserving router or an initial-state
  classifier that uses the observed oracle headroom without sacrificing
  positive-only anchor states.

Status as of 2026-06-26, Candidate E initial support-distance gate:

- Added `scripts/summarize_candidate_e_initial_gate_audit.py` to compare
  first-step support features for positive-only NN, weighted BC, and Candidate
  C on the split-404 endpoint initials.
- Extended `scripts/evaluate_robomimic_router_policy.py` with
  `--router-mode initial_anchor_pos_dist_force_alt` and
  `--initial-gate-threshold`. The rule is intentionally simple and deployable:
  if the positive-only policy's first action is far from labeled positive
  support (`positive_pos_dist > 3.0`), force weighted BC for the whole episode;
  otherwise force positive-only for the whole episode.
- The feature audit showed that `demo_39` is uniquely high under this initial
  positive-support-distance feature (`3.179`), while the other split-404
  initials are at or below roughly `2.586`.
- First-20 endpoint screen with isolated policy RNG: Candidate E reached
  `19/20`, with the gate opening only on the two `demo_39` episodes.
- Follow-up 50-episode endpoint screen with isolated policy RNG: Candidate E
  reached `46/50`, beating positive-only NN (`39/50`), weighted BC (`33/50`),
  v0.1 hard support (`36/50`), v0.2 union (`27/50`), and Candidate A
  (`30/50`).
- In the 50-episode table, the gate opened `5/50` times, all on `demo_39`, and
  recovered full coverage there (`5/5`) while preserving most
  positive-only anchor states.
- Generated
  `results/candidate_breakthrough/candidate_e_initial_gate_audit_REPORT.md`,
  `results/candidate_breakthrough/candidate_e_endpoint_screen_REPORT.md`, and
  CSV companions for feature and per-initial accounting.

Decision:

- Candidate E is the strongest split-404 branch candidate so far. The isolated
  RNG result is `+7/50` over positive-only.
- Do not overclaim yet: the threshold `3.0` was hand-set from the split-404
  audit. A paper-facing version needs hidden-label-free calibration and
  multi-split validation before it can support a methods claim.

Follow-up as of 2026-06-26, Candidate E fixed-threshold multi-split screen:

- Ran fresh first-20 router evals on Can 40p/80b split seeds `101`, `202`,
  `303`, and `505`, and combined them with the existing split-404 first-20
  screen.
- Generated
  `results/candidate_breakthrough/candidate_e_multisplit_screen_REPORT.md` and
  `results/candidate_breakthrough/candidate_e_multisplit_screen_first20_summary.csv`.
- Against corrected first-20 slices of existing baseline eval CSVs and
  isolated-RNG router evals, the aggregate is: positive-only `71/100`, weighted
  BC `60/100`, triage `64/100`, and Candidate E `74/100`.
- Per split, Candidate E is `7/20` on split 101, `17/20` on 202, `15/20` on
  303, `19/20` on 404, and `16/20` on 505. It beats the best first-20 baseline
  on splits 404/505, ties on 202/303, and is down five episodes on 101.
- The fixed gate opens `10/100` episodes. It never opens on splits 202/303,
  opens usefully on split 404, opens with a small net gain on 505, and opens
  on two long split-101 episodes without rescue while that split would prefer
  broader weighted behavior overall.

Revised decision:

- Candidate E should not be promoted unchanged. The useful insight is the
  initial positive-support-distance feature, not the hand-set threshold.
- Next work should calibrate the gate from training-only support statistics
  across splits, or add a second confidence feature that detects when the
  weighted fallback is actually safer than the positive-only anchor.

Status as of 2026-06-26, Candidate F anchor calibration:

- Found and fixed a fairness issue in `scripts/evaluate_robomimic_router_policy.py`:
  all policies must be queried to keep RNN states synchronized, but stochastic
  BC-RNN-GMM action sampling must use isolated per-policy RNG streams so
  non-selected policies do not perturb selected-policy samples.
- Added `scripts/summarize_candidate_f_teacher_forced_anchor_audit.py`. Labeled
  positive teacher-forced action fit does not solve anchor selection: it prefers
  positive/triage on split 101 even though weighted BC is the best completed
  endpoint baseline there.
- Added `scripts/summarize_candidate_f_anchor_calibration_screen.py`. The
  useful train/support statistic is the classifier-probability tail of the
  positive-NN selected support, normalized by the full unlabeled pool's
  classifier-probability scale. Split 101 is uniquely flagged: its selected
  support minimum is `0.125`, while half of its unlabeled-pool mean is `0.203`.
- Candidate F rule: if the positive-NN selected support has any classifier
  probability below `0.5 * unlabeled_prob_mean`, use weighted BC as the
  split-level anchor; otherwise use Candidate E's initial-distance fallback.
- The normalized tail ratio is `0.309` on split 101 versus at least `0.692` on
  the other splits, so the same anchor decision is stable for a broad tail
  fraction range around `0.5`.
- Isolated-RNG first-20 screen: Candidate F reaches `79/100`, versus
  positive-only `71/100`, weighted `60/100`, triage `64/100`, Candidate E
  `74/100`, and the per-split baseline oracle `76/100`.
- Assembled 50-episode estimate: Candidate F reaches `198/250`, versus
  positive-only `174/250`, weighted `158/250`, triage `171/250`, and the
  per-split baseline oracle `192/250`. This uses observed isolated-RNG Candidate
  E 50-episode runs on splits 404 (`46/50`) and 505 (`39/50`), weighted BC on
  split 101 (`37/50`), and positive-only substitution on no-gate splits 202/303.

Candidate F decision:

- This is the best candidate so far for a Can 40p/80b methods result. The tail
  fraction `0.5` is endpoint-free and score-scale normalized, but it remains a
  hyperparameter that should be justified or sensitivity-tested in the paper.
- Ran the single frozen Candidate F matrix and generated
  `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.
- Frozen Candidate F reaches `198/250`, versus positive-only `174/250`,
  weighted `158/250`, triage `171/250`, and the completed per-split baseline
  oracle `192/250`.
- The split-level accounting is: split 101 weighted anchor `37/50` (ties best
  baseline), split 202 Candidate E gate `40/50` (ties best), split 303 Candidate
  E gate `36/50` (ties best), split 404 Candidate E gate `46/50` (`+7/50`), and
  split 505 Candidate E gate `39/50` (`-1/50`).
- A wrong-checkpoint diagnostic using root `last.pth` on split 101 scored only
  `1/50` and is excluded; the frozen split-101 row uses the weighted-sampler
  `model_epoch_200.pth` checkpoint under `external/robomimic/...`, matching the
  paper baseline provenance.
- Added `scripts/summarize_candidate_f_lift_transfer_audit.py` and generated
  `results/candidate_breakthrough/candidate_f_lift_transfer_audit_REPORT.md`.
  The direct Can-style transfer rule, `any low tail -> weighted`, reaches
  `145/250` on completed Lift MG rows. This is only slightly above
  always-weighted and always-triage (`143/250`) and below the Lift per-split
  baseline oracle (`154/250`).
- The same low-tail statistic is still informative on Lift if interpreted by
  severity: no low tail selects positive-only, mild low tail selects
  triage/hard support, and severe low tail selects weighted. This diagnostic
  rule reaches `154/250`, matching the completed Lift baseline oracle.
- Combining frozen Can Candidate F (`198/250`) with this Lift tail-severity
  diagnostic gives `352/500`, versus the combined completed baseline oracle
  `346/500`.
- Do not claim Candidate F transfers unchanged to Lift. The next broader method
  candidate should be a tail-severity router frozen from train/support
  statistics before new endpoint budget is spent.
- Added `scripts/summarize_candidate_g_tail_severity_router.py` as the concrete
  next-candidate assembly. Candidate G uses the same low-tail threshold as
  Candidate F, then routes no-tail cases to the clean positive anchor, mild-tail
  cases to triage/hard support, and severe-tail cases to weighted BC.
- Candidate G reaches `352/500` on completed Can+Lift rows, versus the combined
  completed per-split baseline oracle `346/500`. It is identical to frozen
  Candidate F on Can (`198/250`) and matches the Lift oracle (`154/250`).
- This is still not a paper claim: the mild-tail cutoff `0.03` was discovered
  after inspecting completed Lift rows. Sensitivity is positive only for the
  strict-cutoff band around `0.026` to `0.050`; the next step is to freeze this
  rule before any new endpoint evaluation.
- The freeze document for the next validation attempt is
  `METHOD_FREEZE_CANDIDATE_G.md`.
- Ran a fresh support-only preflight for Candidate G on held-out split seeds
  `606` and `707` for Can 40p/80b and Lift MG. Candidate G selects
  Candidate E on Can 606, triage on Can 707, and triage on both Lift seeds.
- The Can 707 mild-tail case exposed a failure mode: Candidate G routes to
  triage with support `29` hidden positives and `18` hidden bad demos, while
  the positive-only support has `32` hidden positives and `8` hidden bad demos.
- Ran a bounded 20-episode endpoint smoke on Can 707:
  Candidate G's selected triage branch reaches `10/20`, while the clean
  positive-only anchor reaches `15/20`. This argues against task-agnostic
  mild-tail triage on Can.
- Added Candidate H, a task-aware tail router. It keeps Lift mild-tail triage
  but sends Can mild-tail cases to Candidate E's clean anchor and only sends
  severe Can tails (`below_fraction >= 0.03`) to weighted BC.
- Candidate H has the same completed-row assembly as Candidate G
  (`352/500` versus completed oracle `346/500`), but fixes the fresh Can 707
  branch choice. The freeze document is `METHOD_FREEZE_CANDIDATE_H.md`.
- Candidate I replaced Candidate H's Can mild-tail branch with positive-only:
  Can 707 positive-only reaches `15/20` versus Candidate E `13/20` and triage
  `10/20`. Candidate I is rejected as a development candidate because its
  retained Lift mild-tail triage branch loses on fresh Lift 606: positive-only
  `28/50`, triage `23/50`, weighted `16/50`.
- Candidate J tested whether a deployable support-distance router can recover
  the Lift 606 branch-selection headroom. It fails the bounded screen:
  positive-only is `14/20` on the first 20 starts, while per-step
  labeled-support margin routing is `11/20`, anchor-support routing is
  `10/20`, and the initial positive-distance gate ties positive-only only
  because it never opens. The non-deployable oracle over positive, triage, and
  weighted is `17/20`, so future router work needs richer deployable features
  such as temporal confidence or policy self-likelihood, not nearest support
  margin alone.
- Candidate K tested that richer signal. A first-step learned-scale GMM
  confidence gate wins locally on Lift 606: threshold `6.269868` reaches
  `18/20` on the tuned first-20 screen and `32/50` on the broader endpoint,
  versus positive-only `28/50`, triage `23/50`, and weighted `16/50`. But the
  same fixed threshold fails to transfer to fresh Lift 707: router `10/20`
  versus positive-only `12/20` and triage `9/20`. Conclusion: policy
  self-likelihood has real signal, but a globally fixed threshold is not stable
  enough. The next router attempt should calibrate thresholds from labeled
  validation features or use temporal confidence during rollout.
- Candidate L tested the labeled-feature calibration path. The evaluator now
  supports `--initial-feature-threshold-source labeled_positive_quantile`, and
  the q25 labeled-positive calibration preserves the Lift 606 screen result:
  calibrated threshold `6.180339`, router `18/20`. It still fails on fresh
  Lift 707: calibrated threshold `4.164663`, router `10/20`, below
  positive-only `12/20`. A cross-split audit in
  `results/candidate_g_fresh_preflight/candidate_l_calibrated_confidence_router_REPORT.md`
  shows that the best Lift606-selected one-feature initial gates reach only
  `11/20` on Lift 707, while a leaky Lift707-only upper bound is only `13/20`.
  Candidate L is rejected. Do not keep tuning scalar initial thresholds; the
  next useful router direction is temporal confidence during rollout, or a
  policy-training change that removes the need for an initial fixed gate.
- Candidate M tested the direct temporal-confidence path. The evaluator now
  supports `--router-mode temporal_gmm_feature`, which computes the learned GMM
  confidence feature at the current rollout RNN state on every timestep, and
  supports labeled sequence-timestep threshold calibration. This fails at the
  Lift 606 development gate: initial-q25 temporal routing reaches only `7/20`
  and chooses triage for `2146/2253` executed timesteps; sequence-q25 temporal
  routing lowers the threshold to `1.762162` but still reaches only `7/20` and
  chooses triage for `1847/2165` executed timesteps. Candidate M is rejected
  without a fresh Lift 707 eval. The next router attempt, if any, needs a
  predeclared hysteresis/persistence rule; otherwise return to policy-training
  changes rather than more hard routing.
- Candidate N tested that hysteresis path. The evaluator now supports
  `--router-mode temporal_gmm_feature_persistent`: start from positive-only,
  require consecutive low-confidence steps, then switch to triage for the rest
  of the episode. On Lift 606, sequence-q25 persistence `10` reaches `13/20`
  and persistence `20` reaches `11/20`, both below positive-only `14/20` and
  far below the initial confidence gate `18/20`. Candidate N is rejected
  without a fresh Lift 707 eval. The hard-router line should stop unless a
  learned gate gives a much stronger development-split signal; the next
  higher-value path is a policy-training change.
- Candidate O tested the first simple policy-training change on Lift 606:
  positive-NN support remains at full loss weight, while triage-only extra
  demos are added at constant loss weight `0.25`. This created a 243-demo
  positive-anchored union policy-training set, but the trained policy collapsed:
  epoch 50 reaches `1/20` and epoch 100 reaches `5/20` on the Lift 606
  first-20 endpoint screen, below positive-only `14/20`, triage `13/20`,
  weighted `6/20`, and the initial confidence gate `18/20`. Candidate O is
  rejected. Do not continue constant-demo-weight union training; future
  training-side work needs stronger anchor protection or a different loss.
- Candidate P tested whether positive-only initialization fixes that failure.
  Starting from the Lift 606 positive-only NN epoch-200 checkpoint and
  fine-tuning for 20 epochs on the same anchor-union weights reaches `11/20`.
  This prevents Candidate O's severe from-scratch collapse but still degrades
  positive-only (`14/20`) and triage (`13/20`), and remains well below the
  initial confidence gate (`18/20`). Candidate P is rejected. The failure is not
  just initialization; lower-weight triage-only positive BC targets still move
  the policy in the wrong direction.
- Candidate Q/R tested two cheaper anchor-protection rescues. Candidate Q saved
  every checkpoint from a 5-epoch positive-initialized fine-tune and found no
  early sweet spot: epochs 1-5 reached `10/20`, `10/20`, `9/20`, `11/20`, and
  `10/20`. Candidate R interpolated from the positive-only checkpoint toward
  the 20-epoch fine-tuned checkpoint; alphas `0.05`, `0.10`, `0.20`, and
  `0.35` reached `11/20`, `10/20`, `10/20`, and `10/20`. Stop the
  anchor-union rescue line. The next training-side candidate must use a
  genuinely different objective or selector, not lower-weight positive BC on
  triage-only extras.
- Candidate S tested a genuinely different Lift selector proxy: a balanced
  logistic initial-risk classifier trained only from labeled positive versus
  labeled negative initial features. The primary policy-feature q25 gate reaches
  `12/20` on Lift 606, below positive-only `14/20`, and ties positive-only
  `12/20` on Lift 707. Diagnostic obs-only and obs-plus-policy gates do not
  improve fresh Lift 707. Candidate S is rejected; labeled initial-risk is not a
  sufficient policy-quality proxy for choosing between positive-only and triage.
- Fresh Can606 no-tail smoke for Candidate F: trained the missing positive-only
  and weighted epoch-200 policies, then evaluated first-20 positive-only,
  weighted, and Candidate E gate. Positive-only reaches `16/20`, weighted
  `14/20`, and Candidate E gate `16/20` with `2/20` gate openings. This is
  neutral: it does not show a fresh Can no-tail failure, but it also does not
  create new headroom. A 50-episode Can606 continuation should only be run as
  part of a broader predeclared fresh Can-only matrix.
- Fresh Can707 tail-branch smoke for Candidate F: the frozen Can rule selects
  weighted BC on this mild-tail split. Weighted reaches `15/20`, tying
  positive-only `15/20` and beating Candidate E `13/20` and triage `10/20`.
  Across the two fresh Can first-20 smokes, Candidate F ties positive-only at
  `31/40`. This is neutral and weakens the case for broad Candidate F endpoint
  spending unless it is a predeclared Can-only validation matrix.
- Added `scripts/summarize_candidate_breakthrough_decision.py` and generated
  `results/candidate_breakthrough/candidate_breakthrough_decision_REPORT.md`
  plus `candidate_breakthrough_decision_summary.csv`.
- Decision: no general methods-dominance claim yet. Candidate F remains the
  strongest scoped Can discovery (`198/250` versus positive-only `174/250`,
  weighted `158/250`, triage `171/250`, and per-split oracle `192/250`), but
  fresh Can606+707 is neutral (`31/40` tie versus positive-only), direct Lift
  transfer is below oracle (`145/250` versus `154/250`), and the tested Lift
  routers, anchor-union training variants, and labeled initial-risk proxy are
  rejected.
- Follow-up decision after running the predeclared fresh Can-only validation
  matrix: Candidate F failed early. On claim-ready seeds `808` and `909`, the
  frozen selected branch is worse than the best completed non-oracle baseline:
  `42/50` versus positive-only `43/50` on seed `808`, and `39/50` versus
  positive-only `41/50` on seed `909`. The `4/5` no-worse gate allows at most
  one worse row, so the methods-dominance claim is no longer satisfiable before
  seeds `1001/1112/1213`.
- Stop Candidate F endpoint spending for the high-impact breakthrough claim.
  Write the current paper as a precision/coverage study, keep Candidate F as
  scoped/failed-development evidence, and start a genuinely different candidate
  only if it changes the objective or supervision signal rather than tuning the
  rejected router/threshold/anchor-union family.
- Candidate T checked the cheapest distinct composition idea: parameter-space
  interpolation from the Can split-404 positive-only checkpoint toward the
  weighted-BC checkpoint. It is rejected. First-20 endpoint counts are
  positive-only `17/20`, weighted `13/20`, alpha `0.05` interpolation `16/20`,
  alpha `0.10` `13/20`, and alpha `0.20` `3/20`. This suggests that anchor
  preservation needs an explicit objective, not policy weight averaging.
- Candidate U tested the next-cheapest explicit anchor-preservation objective:
  initialize from the Can split-404 positive-only checkpoint, fine-tune on the
  Candidate C sequence-mask weights for 20 epochs, and add normalized
  parameter-space anchor L2 with weight `1000`. The first-20 endpoint counts are
  epoch `5` `17/20`, epoch `10` `16/20`, epoch `15` `14/20`, and epoch `20`
  `16/20`, versus the positive-only anchor at `17/20`. Candidate U is
  neutral/rejected: it matches but does not improve the anchor, and longer
  fine-tuning degrades. If this line is revisited, use a local output or
  distribution anchor on positive states rather than normalized parameter L2.
- Candidate V tested that local output-anchor variant: a frozen copy of the
  initialized positive-only policy scores the batch actions, and the fine-tuned
  policy receives a hinge penalty when it drops below the anchor log-probability
  on high-weight timesteps. With anchor-logprob weight `10`, first-20 Can
  split-404 counts were epoch `5` `15/20`, epoch `10` `18/20`, epoch `15`
  `15/20`, and epoch `20` `16/20`. The epoch-10 checkpoint is the first
  training-side variant here to beat the positive-only first-20 anchor
  (`17/20`), but its 50-episode check is `39/50`, tied with positive-only and
  below the Candidate E router reference (`46/50`). Candidate V is the next
  training-side lead, not a breakthrough claim. It needs frozen hyperparameter,
  seed, and split validation before any scaling or paper promotion.
- Frozen Candidate V split-505 validation failed. The split-505 first-20 check
  passed (`16/20` versus positive-only `15/20`), but the 50-episode check is
  `38/50`, below positive-only `40/50`. This means output anchoring is a useful
  training-side clue but not a scalable method result under the current recipe.
  Do not spend a broad matrix on Candidate V without a new predeclared change.
- Candidate V failure analysis further explains the stop decision. Across
  splits `404` and `505`, Candidate V is `77/100` versus positive-only
  `79/100` and Candidate E `85/100`. A per-initial oracle over positive-only
  and Candidate V reaches only `85/100`, equal to Candidate E alone, while
  Candidate V adds only `2/100` unique wins beyond the positive-plus-Candidate-E
  oracle. It still fails the key split-404 `demo_39` coverage gap (`0/5`) that
  Candidate E solves (`5/5`) and introduces split-505 anchor regressions such
  as `demo_89` (`0/5`). The next method needs a state-specific weighted-rescue
  selector, not another global fine-tune.
- Candidate W tested the cheapest deployable state-specific rescue selector:
  positive-only by default, but force weighted BC for the whole episode when
  the initial positive-policy action has positive-support distance `> 3.0` and
  support margin `> 0.0`. It preserves the split-404 rescue and reaches
  `46/50`, but the frozen split-505 validation remains `39/50` versus
  positive-only `40/50`. Across splits `404` and `505`, Candidate W is
  `85/100`, tying Candidate E and not closing the `93/100` per-initial oracle
  gap from positive-only/Candidate-E/Candidate-V. Stop scalar initial
  support-distance/margin gates; the next viable attempt must introduce a more
  stable state-conditional policy-quality signal or a different training
  objective.
- Candidate X revisited the negative-action objective after Candidate D's
  anchor damage. It keeps Candidate C's sequence-mask BC loss but applies the
  nearest-labeled-negative hinge only on the extra selected timesteps outside
  the full-weight positive-anchor demos (`222` negative-loss timesteps instead
  of `5528`). This still reaches only `10/20` at epoch `100` and `14/20` at
  epoch `200`, below Candidate C (`16/20`) and positive-only (`17/20`) on the
  matched split-404 first-20 gate. Stop nearest-negative hinge variants
  unchanged; a future transition-level objective needs a different bad-action
  target or explicit anchor preservation.

- Compare support and failures for positive-only, weighted, hard union, and v0.1 on Can 40 split 404.
- Produce per-initial-state table like the existing failure-mode audit.
- Determine whether the issue is bad admission, missing coverage, poor sequence support, or over-expanded union.

### Days 3–5: implement Candidate A

- Add per-transition weights to the Robomimic BC-RNN-GMM trainer.
- Add negative unlikelihood / margin loss if feasible.
- Run a small hyperparameter sweep on Can 404 and Lift 101.

### Days 6–8: implement Candidate C

- Add per-timestep sequence masks to the BC loss.
- Compare transition weighting versus sequence masking.
- Run Can 404 and Lift 101/303.

### Days 9–10: implement Candidate B rule-based gate

- Reuse trained positive-only, weighted, and hard-union policies.
- Implement per-timestep hard policy selection with all RNN states maintained.
- Run Can 404, Can 101, Lift 303.

### Days 11–12: choose one candidate to freeze

- Pick the candidate with the best worst-case split behavior.
- Write `METHOD_FREEZE_V03.md`.
- Declare final split matrix before full runs.

### Days 13–14: run full fresh gate for the frozen candidate

- Can 40: 101/202/303/404/505.
- Lift: 101/202/303/404/505.
- Run generated hard-negative and coverage-shift if the candidate looks promising.

---

## 11. How to write the paper if the new candidate succeeds

New title candidate:

> From Bad Demonstrations to Bad-Action Avoidance: Transition-Level Risk for Offline Imitation

Main claim:

> Failure demonstrations help not by filtering whole trajectories, but by defining local action-risk constraints that preserve useful coverage while suppressing action-conflicting behavior.

Main figures:

1. method diagram: transition-level risk + sequence masks;
2. default Can/Lift table versus baselines;
3. generated regime probe table;
4. ablation showing bad-risk and sequence-mask contribution;
5. split-404 failure/rescue analysis;
6. proxy no-go and why the new method avoids proxy selection.

---

## 12. How to write the paper if the new candidate does not succeed

Keep the current paper direction:

> When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study

Promote:

- PointNav mechanism;
- generated Can regime probes;
- default Can/Lift caveats;
- proxy no-go;
- active abstention;
- router regret.

Then frame the failed candidates as evidence that policy-quality prediction and transition-level risk are the next research frontier.

---

## 13. Recommended order of attack

1. **Candidate A: Transition-risk weighted BC** — highest ROI and easiest to integrate.
2. **Candidate C: Sequence-mask BC** — likely strongest if Robomimic code changes are manageable.
3. **Candidate B: State-level policy gate** — potentially powerful but implementation riskier with RNN/GMM policies.
4. **Candidate D: Counterfactual negative regularization** — best used as a regularizer for A or C.

Do not spend more compute on global threshold tuning. The current results already show that threshold tuning cannot solve the fundamental problem.
