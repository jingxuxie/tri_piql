# TRIAGE-BC: Candidate Breakthrough Plan for a Top-Tier Methods Paper

## Executive diagnosis

The current project is strong as an empirical precision/coverage study, but it is not yet a top-tier methods-dominance paper. The central gap is that the paper-facing candidate does not consistently beat the strongest baselines:

- Positive-only NN is often the strongest Can baseline.
- Weighted BC is often strongest on Lift-like broad-coverage settings.
- v0.2 portfolio routing is only barely positive on the five-split Can+Lift gate.
- Recent candidate-development attempts show local signals but fail fresh validation.

To turn this into a high-impact methods paper, the next method must **subsume** the baselines rather than merely choose between them:

1. keep the clean anchor of positive-only retrieval;
2. keep broad coverage when it is needed;
3. use bad demonstrations at the **transition/action level**, not just for trajectory filtering;
4. avoid unstable global task/split thresholds;
5. show consistent improvement on fresh splits, not just development splits.

---

## What the latest evidence implies

### Current evidence is not SOTA-dominance evidence

The current reviewer-facing claim summary correctly states that the paper should be read as a precision/coverage study, not as a universal dominance claim. The current fresh v0.2 gate is only barely positive: selected branches reach 340/500 versus 338/500 for the best completed per-split baselines.

### Recent candidate-development attempts are informative but not promotable

- Candidate I improved one Can mild-tail case but failed fresh Lift validation.
- Candidate J showed there is router headroom, but nearest-support-margin features did not expose it.
- Candidate K found a useful Lift606 GMM-confidence signal, but the fixed threshold failed on Lift707.
- Candidate 1 SM-RWBC broad-pool weighting reduced hidden-bad transition mass in preflight, but failed the Can404 endpoint screen.
- The focused SOTA-candidate sweep over SM-RWBC, CAU-BC, CCG-Distill,
  SafeExpand, Demo-DPO, and IQL-AWBC is now complete at the short-screen
  level. No branch clears its first-stage gate. The aggregate report is
  `results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md`.
- A later CAU-alone 50-episode follow-up changes CAU from a hard rejection to a
  useful method seed on Can: `193/250` over five splits, versus positive-only
  `174/250`, weighted BC `158/250`, TRIAGE-BC v0.1 `171/250`, and best old
  baseline per split `192/250`. It still trails the v0.2 selected union branch
  at `197/250` and loses split 404 to positive-only by `4/50`.
- A post-hoc CAU-plus-v0.2 portfolio preflight was the strongest pre-fresh
  hypothesis: `estimated_positive_mass > 47.631032` chooses CAU on splits
  `303/404/505` and v0.2 on `101/202`, reaching `208/250`. This is not fresh
  evidence because the rule is selected on the same five endpoint splits.
- The first fresh endpoint validation of that portfolio on Can split606 is
  negative: the fitted gate selects CAU, but CAU reaches `15/20` versus
  positive-only `16/20`; frozen v0.2 union reaches `14/20`, and the cleaner
  risk-fusion diagnostic reaches `15/20`. A proper expanded-mask CAU check
  that trains on the full 130-demo transition-weight filter reaches only
  `12/20`, so this failure is not only a training-filter mismatch.
- A follow-up GMM-confidence router audit found a split606 same-screen threshold
  that would route to `18/20` with zero losses, but the frozen threshold fails
  on unused split707 (`15/20`, opening no CAU episodes). CAU-alone itself is
  strong on split707: `20/20` first-20 and `50/50` in a 50-episode confirmation
  versus positive-only `36/50` and weighted BC `39/50`.
- The next fixed-CAU validation on split808 is negative against the strongest
  baseline: CAU epoch 200 reaches `38/50` versus positive-only `43/50`, weighted
  BC `25/50`, TRIAGE-BC v0.1 `16/50`, and the older Candidate E gate `42/50`.
- A leave-one-split-out support-distance selector audit confirms that simple
  initial features are not the missing CAU router: positive-only is `269/370`,
  always-CAU is `296/370`, and oracle switching is `331/370`, but the safe
  held-out selector falls to `263/370` while best-delta selection reaches
  `277/370` with `23` positive-only losses.
- A first-state policy-distribution selector audit is a stronger diagnostic but
  still not a deployable router: over the same completed splits, positive-only
  is `269/370`, always-CAU is `296/370`, and oracle switching is `331/370`;
  the leave-one-split-out safe selector reaches `276/370` with `29` gains and
  `22` losses, while the best-delta selector reaches `299/370` with `44` gains
  and `14` losses. The pooled frozen rule
  `alt_logp_margin_vs_anchor > 0.757864 or alt_support_margin > 0.837440`
  transfers neutrally on fresh split909: `15/20` routed versus `15/20`
  positive-only and `9/20` CAU-alone, opening `0` CAU episodes.
- A linear learned router over the same first-state policy features is also
  negative: leave-one-split-out safe reaches only `277/370` and best-delta
  `278/370`, both with `17` positive-only losses. Training on completed splits
  and freezing to split909 opens all CAU starts, dropping to `9/20` versus the
  `15/20` positive-only anchor. Even the same-screen split909 upper bound is
  only `16/20`, so this fresh screen has little first-state routing headroom.
- A per-step sequence support-margin router is the strongest current follow-up,
  but not yet a method result. Fixed threshold `0.05` reaches `51/60` across
  splits 909/808/707 versus positive-only `47/60` and CAU-alone `43/60`, with
  `5` gains and `1` loss versus positive-only. The first no-retune held-out
  guardrail on split606 is neutral (`16/20` router versus `16/20`
  positive-only and `15/20` CAU), but the 50-episode split606 validation is
  positive (`42/50` router versus `38/50` positive-only and `41/50` CAU). The
  next 50-episode split101 check is mixed-negative: `25/50` router versus
  `19/50` positive-only but below CAU at `33/50`. Across these two 50-episode
  no-retune validations, the router is `67/100` versus positive-only `57/100`
  and CAU `74/100`, so it is not yet a paper claim. A persistent
  support-margin variant also fails to capture split101 CAU upside (`20/50`
  persistent versus `25/50` non-persistent and `33/50` CAU).
- The reviewer summary also notes that Candidate F, output anchoring, scalar rescue gates, Candidate W, and nearest-negative hinge variants should not be promoted.

The key lesson is that **global branch rules, fixed first-state thresholds,
simple support-distance routers, first-state policy-feature gates, and simple
transition-level reweighting are too brittle**.
The next attempt should only be
launched if it introduces a genuinely stronger state-conditional policy-quality
signal, sequence-aware critic, or policy-level objective. Otherwise the paper
should stay framed as a precision/coverage empirical study.

---

# Main recommendation

The focused candidate search has now been run and should be treated as a
negative development audit rather than an open SOTA path. It covered six method
families:

1. **Sequence-Masked Risk-Weighted BC**: one policy, broad coverage, per-timestep weights, bad-action suppression.
2. **Contrastive Action-Unlikelihood BC**: explicitly penalize bad actions near similar states.
3. **Conformal Confidence-Gated Specialist Distillation**: use positive-only / weighted / hard-union specialists, but distill them into one gated student with calibrated confidence rather than fixed global thresholds.
4. **Safe Support Expansion**: start with positive-only support and add only risk-certified, coverage-improving demos.
5. **Preference-Style Sequence Objective**: use labeled positive/negative
   demos as trajectory-level preference pairs.
6. **Offline RL / IQL-AWBC Revisit**: learn classifier-reward Q/V values and
   extract a BC-RNN-GMM policy through advantage weights.

None produced promotable SOTA-dominance evidence. The best Can404 endpoint
branches in this sweep reached `16/20`, below the matched positive-only anchor
at `17/20`; the CCG transfer gate reached `10/20` on Lift707 versus
positive-only `12/20`. The matched-start Can404 anchor-overlap audit
(`results/sota_candidate/CAN404_ANCHOR_OVERLAP_REPORT.md`) shows that the
near misses do not cleanly preserve the positive-only anchor: CAU gains 2
starts over positive-only but loses 3 positive-only starts, while Demo-DPO gains
1 and loses 2. A post-hoc initial-feature fallback audit reaches `18/20` for a
CAU-plus-positive route with zero same-screen anchor losses, but the threshold is
selected on the same Can404 endpoint outcomes. The first predeclared fresh
validation of that frozen fallback on split 505 is positive: the first-20
screen routes to `16/20` versus positive-only `15/20`, and the 50-episode
confirmation routes to `41/50` versus positive-only `40/50`, both with zero
anchor losses. The next predeclared fresh split 303 screen is neutral for the
deployable fallback: CAU alone reaches `17/20`, but the frozen gate opens only
`demo_39`, so the routed fallback remains `15/20` versus positive-only `15/20`
with zero anchor losses. This blocks promotion of the unchanged fallback as
SOTA-dominance evidence. A two-feature gate selected on completed 303/404/505
screens is stronger: `initial_anchor_pos_dist_mean <= 1.273665 or
initial_anchor_neg_dist_mean > 3.131861`. On the fresh split-101 validation it
routes to `24/50` versus positive-only `19/50`, with `5` gains and `0` anchor
losses; on fresh split 202 the 50-episode confirmation is neutral (`40/50`
routed versus `40/50` positive-only) even though CAU alone reaches `42/50`.
This is the best current follow-up, but it is still not SOTA-dominance evidence
because the gate is selected on earlier completed screens and has only one
positive fresh routed confirmation. A separate CAU-alone five-split endpoint
follow-up is stronger than the original first-20 Can404 rejection suggested:
CAU reaches `193/250`, beating positive-only (`174/250`), weighted BC
(`158/250`), TRIAGE-BC v0.1 (`171/250`), and the best old baseline per split
(`192/250`). It remains below v0.2 selected union (`197/250`) and the
non-oracle per-split ceiling including v0.2 (`209/250`). A post-hoc
CAU-plus-v0.2 portfolio preflight reaches `208/250` by selecting CAU on
`303/404/505` and v0.2 on `101/202`; this is the best current hypothesis but
not claim-bearing evidence because it was selected after seeing these five
endpoint splits. The first fresh split606 validation rejects promoting it
unchanged: the gate-selected CAU branch reaches `15/20`, frozen v0.2 union
reaches `14/20`, risk-fusion reaches `15/20`, and the proper 130-demo
expanded-mask CAU diagnostic reaches `12/20`, all below positive-only at
`16/20`. A GMM-confidence router follow-up then finds one post-hoc split606
threshold with `18/20` and zero losses, but that threshold does not transfer to
split707 (`15/20`, no CAU opens). CAU-alone on split707 is strongly positive:
`20/20` first-20 and `50/50` at 50 episodes versus positive-only `36/50` and
weighted BC `39/50`. The next fixed-CAU validation on split808 is negative:
CAU reaches `38/50`, below positive-only `43/50` and Candidate E `42/50`.
The leave-one-split-out support-distance selector audit shows remaining oracle
headroom (`331/370`) but no deployable simple feature rule: safe selection is
`263/370` versus positive-only `269/370`, and best-delta selection reaches
`277/370` only by accepting `23` losses.
First-state policy-distribution features improve the offline threshold-selector
audit (`276/370` safe and `299/370` best-delta), but the pooled frozen rule is
neutral on fresh split909 (`15/20` routed versus `15/20` positive-only and
`9/20` CAU-alone, with `0` CAU opens). A linear learned router over the same
features is worse: LOO totals fall to `277/370`/`278/370`, and the frozen
split909 router opens all CAU starts, reaching `9/20`. This keeps CAU as a
useful method seed while leaving the deployable router unresolved.
A per-step support-margin router is the first sequence-aware CAU follow-up with
a consistent short-screen gain: fixed threshold `0.05` reaches `51/60` across
splits 909/808/707 versus positive-only `47/60` and CAU-alone `43/60`, with
`5` gains and `1` loss versus positive-only. The first no-retune held-out
split606 guardrail is neutral (`16/20` router versus `16/20` positive-only),
but the 50-episode split606 validation is positive (`42/50` router versus
`38/50` positive-only and `41/50` CAU). The next 50-episode split101 check is
mixed-negative (`25/50` router versus `19/50` positive-only and `33/50` CAU).
Across the two 50-episode no-retune validations the router is `67/100` versus
positive-only `57/100`, but below CAU `74/100`; this keeps it as a useful
sequence-aware diagnostic rather than a promotable method. A naive persistent
switching variant is worse on split101 (`20/50`), so the missing ingredient is
not simply committing harder after support-margin evidence.

Use the sweep as claim-boundary evidence. Do not start longer versions of these
recipes unchanged. The frozen CAU-plus-positive fallback found a useful
split-505 signal, but split 303 shows the current gate misses CAU-helped starts.
Do not scale the unchanged fallback. CAU action-conflict is useful but
inconsistent, while the two-feature CAU gate, GMM-confidence gate, and simple
support-distance/policy-feature selectors remain weaker routing follow-ups. Any renewed
SOTA-candidate path should replace the
unchanged CAU-plus-v0.2 portfolio with a genuinely stronger state-conditional
policy-quality signal, with a hard stop on anchor loss.

---

# Candidate 1: Sequence-Masked Risk-Weighted BC (SM-RWBC)

## Idea

Current weighted BC keeps too many bad transitions. Current hard support throws away coverage. SM-RWBC keeps broad trajectories for sequence context but masks or downweights risky timesteps.

For a trajectory \(\tau = (o_t, a_t)\), train BC-RNN-GMM with a per-timestep loss:

\[
\mathcal{L}_{\text{SM-RWBC}} = -\sum_{t} m_t \log \pi_\theta(a_t \mid h_t, o_t),
\]

where

\[
m_t = \operatorname{clip}(p_{\text{good}}(o_t,a_t), m_{\min}, 1)
      \cdot \exp(-\lambda r_{\text{bad}}(o_t,a_t)).
\]

Here:

- \(p_{\text{good}}\) is the existing tri-signal classifier probability.
- \(r_{\text{bad}}\) is a nearest-negative action-conflict score.
- \(m_t\) downweights bad-like local actions but does not discard the whole sequence.

## Why this could beat baselines

It can beat positive-only NN because it keeps hidden-positive coverage. It can beat weighted BC because it suppresses local bad actions. It can beat hard support because it does not throw away useful trajectory context.

## Implementation

Modify the official Robomimic BC-RNN-GMM training data loader or loss wrapper so each timestep has a scalar weight.

For each transition in `D+ ∪ Du`:

1. compute classifier probability `p_good_t`;
2. compute nearest-negative action conflict:
   - find K nearest labeled-negative states in observation space;
   - measure action similarity / conflict relative to those negatives;
   - normalize to `[0, 1]` using labeled-positive and labeled-negative calibration;
3. set timestep weight:
   - positives: `m_t = 1`;
   - unlabeled: `m_t = max(m_min, p_good_t) * exp(-lambda * risk_t)`;
4. train BC-RNN-GMM normally, but multiply NLL by `m_t`.

## Minimal hyperparameter grid

Use a small grid only:

- `m_min ∈ {0.03, 0.05, 0.10}`
- `lambda ∈ {1, 2, 4}`
- risk feature: `{bad_neighbor_action, bad_neighbor_state_action, combined}`

Screen on 20 episodes first. Promote only if it beats the best baseline on at least 4/5 screened splits.

## First validation splits

Run in this order:

1. Can 40 split 404: must fix the severe v0.2 hard-union regression.
2. Can 40 split 505: must improve the near-tie case.
3. Lift 606 and 707: must not collapse on Lift.
4. Hard-negative Can 101: must preserve generated-probe win.
5. Coverage-shift Can 101: must preserve generated-probe win.

## Go/no-go criteria

Promote to full five-split training only if:

- Can 404 improves over positive-only by at least +4/50, or at minimum closes the -12/50 hard-union gap;
- Can 505 improves over positive-only by at least +3/50;
- Lift screens match or beat positive-only and weighted on average;
- no generated-probe regression larger than -2/50.

## Status as of 2026-06-26

Implemented the broad-pool SM-RWBC preflight and first Can404 endpoint screen.

Artifacts:

- Preflight generator: `scripts/summarize_sota_sm_rwbc_preflight.py`.
- Screen summarizer: `scripts/summarize_sota_sm_rwbc_screen.py`.
- Preflight report: `results/sota_candidate/sm_rwbc_can404_m003_lam2_combined_preflight/sm_rwbc_preflight_REPORT.md`.
- Endpoint screen report: `results/sota_candidate/sm_rwbc_can404_screen_REPORT.md`.

Result:

- The selected recipe `m_min=0.03`, `lambda=2`, `combined` uses the full weighted-BC train pool (`130` demos), keeps labeled positives at full weight, and reduces hidden-bad transition mass from an unweighted fraction of `0.620` to a weighted mass fraction of `0.376`.
- The endpoint policy still fails the first gate: epoch 100 and epoch 200 both reach only `10/20` on Can404, versus positive-only NN `17/20`, weighted BC `13/20`, Candidate C sequence mask `16/20`, and Candidate X extra-only negative-action `14/20`.

Decision:

- Reject this broad-pool SM-RWBC recipe and do not scale it unchanged to Can505, Lift, or generated probes.
- The failure reinforces the split-404 diagnosis: reducing bad-transition mass is not enough if broad-pool training disrupts the positive-only anchor. Any future Candidate 1 variant needs explicit anchor preservation or a different local objective rather than only smoother per-timestep weights.

---

# Candidate 2: Contrastive Action-Unlikelihood BC (CAU-BC)

## Idea

Bad demonstrations should not only remove trajectories; they should teach the policy which actions are unsafe in nearby states. Add a contrastive continuous-action unlikelihood term.

For each positive or selected/unlabeled transition \((o,a^+)\), retrieve a nearby negative transition \((o^-,a^-)\). Penalize the policy if it gives the negative action high likelihood at the current observation:

\[
\mathcal{L}_{\text{CAU}} =
\max(0, \log \pi_\theta(a^- \mid o) - \log \pi_\theta(a^+ \mid o) + \gamma).
\]

Final loss:

\[
\mathcal{L} = \mathcal{L}_{\text{BC}} + \beta \mathcal{L}_{\text{CAU}}.
\]

## Why this could beat baselines

Positive-only NN never sees what not to do. Weighted BC sees bad actions but may clone them. CAU-BC teaches explicit local action rejection.

## Implementation

Use the official BC-RNN-GMM policy. During training:

1. sample a normal BC sequence;
2. for each timestep or first few timesteps, retrieve nearest bad-action candidates;
3. compute current policy log-probability of the demonstrated action and bad candidate action;
4. add hinge/unlikelihood penalty.

For RNNs, use the same hidden state produced by the sequence context, then evaluate log-probability for both `a_good` and `a_bad` at the same observation timestep.

## Minimal hyperparameter grid

- margin `gamma ∈ {0.5, 1.0, 2.0}`
- penalty `beta ∈ {0.05, 0.10, 0.20}`
- negative retrieval: `{nearest_state, nearest_state_action, action_conflict}`

## Go/no-go criteria

Promote if it improves Can 404 and hard-negative Can without hurting Lift by more than 2/50.

## Status as of 2026-06-26

Implemented the action-conflict CAU-BC preflight and first Can404 endpoint screen.

Artifacts:

- Preflight generator: `scripts/summarize_sota_cau_preflight.py`.
- Screen summarizer: `scripts/summarize_sota_cau_screen.py`.
- Preflight report: `results/sota_candidate/cau_action_conflict_can404_preflight/cau_preflight_REPORT.md`.
- Endpoint screen report: `results/sota_candidate/cau_action_conflict_can404_screen_REPORT.md`.

Result:

- The preflight reuses Candidate C's sequence-mask train support and compares negative-action retrieval modes.
- The selected `action_conflict` retrieval keeps the selected negative-loss mass at `5528` transitions, with hidden-positive mass `5113`, hidden-bad mass `415`, and mean negative-action distance `3.683328`.
- This is materially different from the rejected nearest-state hinge target, whose mean negative-action distance was `2.669399` in the same preflight.
- The endpoint screen used `beta=0.05`, `margin=0.5`, selected-scope negative loss, `200` epochs, `100` gradient steps per epoch, and checkpoints at epochs `100` and `200`.
- Can404 valid-positive-start results:
  - epoch `100`: `6/20`;
  - epoch `200`: `16/20`.
- Matched references:
  - positive-only NN: `17/20`;
  - weighted BC: `13/20`;
  - Candidate C sequence mask: `16/20`;
  - Candidate D nearest-negative hinge: `14/20` at epoch `100`, `13/20` at epoch `200`;
  - Candidate X extra-only nearest-negative hinge: `10/20` at epoch `100`, `14/20` at epoch `200`.

Decision:

- The original first-20 screen rejected this action-conflict `beta=0.05`,
  `margin=0.5` CAU recipe as a SOTA candidate because it fixed the worst
  nearest-negative hinge regression and tied Candidate C, but still did not
  beat the positive-only anchor on split 404.
- A later 50-episode five-split follow-up shows the original rejection was too
  pessimistic for CAU as a broad Can method seed: CAU reaches `193/250` versus
  positive-only `174/250`, weighted BC `158/250`, TRIAGE-BC v0.1 `171/250`,
  and best old baseline per split `192/250`.
- Do not promote CAU alone as SOTA-dominance evidence: it still loses split 404
  to positive-only by `4/50`, loses split 101 to weighted by `4/50`, and trails
  v0.2 selected union by `4/250`.
- A separate frozen
  CAU-plus-positive fallback rule, with the Can404 feature threshold fixed
  before split-505 evaluation, reaches `16/20` versus positive-only `15/20` on
  the first-20 screen and `41/50` versus positive-only `40/50` on the 50-episode
  confirmation, both with zero anchor losses. The next split-303 fresh screen is
  neutral for the deployable fallback (`15/20` versus positive-only `15/20`)
  despite CAU alone reaching `17/20`, so the unchanged gate should not be scaled
  or promoted as a method result.
- A two-feature follow-up gate selected on completed 303/404/505 screens
  (`initial_anchor_pos_dist_mean <= 1.273665 or initial_anchor_neg_dist_mean >
  3.131861`) is stronger but still not promotable: split101 confirms at
  `24/50` routed versus positive-only `19/50` with `0` losses, while split202
  50-episode confirmation is neutral at `40/50` routed versus positive-only
  `40/50` despite CAU alone reaching `42/50`.
- A post-hoc CAU-plus-v0.2 portfolio preflight was the next best pre-fresh hypothesis:
  `estimated_positive_mass > 47.631032` selects CAU on `303/404/505` and v0.2
  on `101/202`, reaching `208/250` versus always-v0.2 `197/250` and always-CAU
  `193/250`. Its first fresh split606 endpoint validation is negative:
  gate-selected CAU reaches `15/20` versus positive-only `16/20`, frozen v0.2
  union reaches `14/20`, risk-fusion reaches `15/20`, and a full 130-demo
  expanded-mask CAU sanity check reaches only `12/20`; do not promote the
  unchanged portfolio as a method result.
- A GMM-confidence CAU router follow-up is mixed: labeled q25 calibration is
  neutral on split606 (`16/20`), a post-hoc split606 threshold reaches `18/20`
  with zero losses, but the frozen threshold fails split707 (`15/20`) because
  it opens no CAU episodes. CAU-alone split707 is the useful result: `20/20`
  first-20 and `50/50` at 50 episodes versus positive-only `36/50` and weighted
  BC `39/50`. The next fixed-CAU split808 validation is negative: `38/50`
  versus positive-only `43/50` and Candidate E `42/50`.
- A broader LOO audit over completed Can CAU splits shows that simple initial
  support-distance features do not safely select CAU: positive-only totals
  `269/370`, always-CAU totals `296/370`, and oracle switching totals
  `331/370`, but safe held-out selection reaches only `263/370`, while
  best-delta selection reaches `277/370` with `23` losses.

---

# Candidate 3: Conformal Confidence-Gated Specialist Distillation (CCG-Distill)

## Idea

Current evidence shows different policies win on different initial states. Direct per-step switching may be unstable. Instead, train a student policy from specialist teachers with a confidence gate.

Specialists:

- positive-only NN BC policy;
- hard-union / bad-aware support policy;
- weighted BC policy.

Gate features:

- GMM learned scale / entropy / top-mode confidence;
- cross-policy log-likelihood of candidate actions;
- policy disagreement;
- classifier score at chosen action;
- nearest-positive and nearest-negative support distances;
- temporal confidence over the first `T=5` steps, not only first-step threshold.

The gate does not directly choose actions during rollout. It produces weights for distillation:

\[
\mathcal{L}_{\text{distill}} = \sum_j \alpha_j(o,h) \, \mathrm{KL}(\pi_j(\cdot\mid o,h) \| \pi_{\text{student}}(\cdot\mid o,h)).
\]

Then deploy one student policy.

## Why this could beat baselines

Candidate J showed oracle branch-selection headroom, but support-margin gates failed. Candidate K showed GMM confidence has local signal, but fixed thresholds do not transfer. CCG-Distill keeps the useful confidence idea but calibrates it and avoids hard online policy switching.

## Calibration rule

Avoid post-hoc hidden labels. Calibrate using only labeled positives and labeled negatives:

- choose thresholds so labeled-positive demos keep high confidence under positive-only / hard-union teachers;
- choose rejection thresholds so labeled-negative demos are not assigned high confidence to the same teacher;
- use conformal quantiles rather than fixed numeric thresholds.

## Screen

Run first on Lift 606/707, because Candidate K and J showed there is router headroom but fixed gates failed.

## Go/no-go criteria

Promote if it beats positive-only on Lift 606 and Lift 707, and does not fall below weighted by more than 1/20 in first-20 screens.

## Status as of 2026-06-26

Ran a bounded preflight over the existing Lift router/confidence and
training-side anchor-union evidence instead of launching a fresh distillation
train/eval cycle.

Artifacts:

- Preflight summarizer: `scripts/summarize_sota_ccg_distill_preflight.py`.
- Preflight report: `results/sota_candidate/ccg_distill_lift_preflight_REPORT.md`.
- Preflight CSV: `results/sota_candidate/ccg_distill_lift_preflight_summary.csv`.

Result:

- Candidate K's tuned first-step confidence router has real Lift606 headroom:
  `18/20` versus positive-only `14/20`.
- The same fixed router fails Lift707: `10/20` versus positive-only `12/20`.
- Candidate L's best Lift606-selected threshold transfers to only `11/20` on
  Lift707, and even the leaky Lift707 one-feature upper bound reaches only
  `13/20`.
- Direct temporal/persistent confidence gates do not repair the signal on
  Lift606; the best reaches `13/20` versus positive-only `14/20`.
- The closest prior single-policy training proxies, Candidate O/P/Q/R
  positive-anchor union and checkpoint interpolation, all damage the
  positive-only anchor; the best reaches `11/20` on Lift606.

Decision:

- Treat CCG-Distill as a preflight no-go for this candidate sweep.
- Do not spend a fresh CCG-Distill train/eval cycle until the teacher-selection
  signal improves on both Lift606 and Lift707.
- Move next to a genuinely different objective, most likely the Offline
  RL/IQL revisit, rather than distilling the current weak/non-transferring
  confidence gate.

---

# Candidate 4: Safe Support Expansion (SafeExpand-BC)

## Idea

The hard-union candidate improves Can but can regress badly on split 404. Make expansion conservative and data-dependent.

Start with positive-only NN support. Add a demo from a bad-aware/risk-fusion ranking only if it satisfies both:

1. **risk certificate**: its bad-risk score is below a conformal threshold calibrated from labeled positives;
2. **coverage novelty**: it adds state coverage not already covered by positive-only support.

## Procedure

1. Build positive-only support `S_pos`.
2. Build risk-fusion candidate list `C_risk`.
3. For each candidate demo `tau`:
   - compute demo-level risk quantiles, not only mean risk;
   - compute coverage novelty relative to `S_pos`;
   - add `tau` only if `risk_q90 <= pos_calibrated_risk_q90 + delta` and `novelty >= novelty_min`.
4. Stop when either risk fails, novelty fails, or support reaches a mass cap.

## Why this could beat current hard union

The current union mechanically adds risk-fusion support. SafeExpand adds only if it is both safe and useful. This is aimed directly at split 404.

## Go/no-go criteria

Must outperform positive-only on Can 404 or at least avoid the -12/50 union regression while keeping gains on 101/202/303.

## Status as of 2026-06-26

Implemented the first conservative SafeExpand preflight and Can404 endpoint screen.

Artifacts:

- Preflight/setup script: `scripts/summarize_sota_safeexpand_preflight.py`.
- Screen summarizer: `scripts/summarize_sota_safeexpand_screen.py`.
- Preflight report: `results/sota_candidate/safeexpand_can404_demo103_preflight/safeexpand_preflight_REPORT.md`.
- Endpoint screen report: `results/sota_candidate/safeexpand_can404_screen_REPORT.md`.

Result:

- The preflight starts from the positive-only NN top40 support.
- The selected hidden-label-free certificate is classifier score at least the labeled-positive minimum (`0.830569`) and local risk no higher than the positive-NN anchor support's 75th percentile (`0.221187`).
- This certificate adds exactly one unlabeled demo, `demo_103`.
- Diagnostic hidden labels:
  - positive-only anchor support: `35` hidden-positive, `5` hidden-bad out of `40`;
  - SafeExpand support: `36` hidden-positive, `5` hidden-bad out of `41`.
- Relaxing the classifier or risk certificate admits hidden-bad demos immediately, so the safe branch is a one-demo expansion rather than a broad support rescue.
- Endpoint screen used official BC-RNN-GMM, `200` epochs, `100` gradient steps per epoch, and checkpoints at epochs `100` and `200`.
- Can404 valid-positive-start results:
  - epoch `100`: `10/20`;
  - epoch `200`: `12/20`.
- Matched references:
  - positive-only NN: `17/20`;
  - weighted BC: `13/20`;
  - Candidate C sequence mask: `16/20`;
  - CAU action-conflict: `16/20`.

Decision:

- Reject this one-demo SafeExpand recipe as a SOTA candidate.
- It improves the hidden-label support audit slightly, but endpoint behavior drops below weighted BC and far below the positive-only anchor.
- Do not scale this recipe unchanged. The failure suggests that merely adding a certified-safe support demo can disrupt the learned anchor; future support-expansion work needs an explicit policy-output anchor or a different training objective, not only a cleaner support set.

---

# Candidate 5: Preference-Style Sequence Objective (Demo-DPO / Demo-IPO)

## Idea

Use positive and negative demonstrations as preference pairs over trajectories or prefixes. Instead of only selecting support, train a policy to assign higher likelihood to positive sequences than negative sequences.

For a positive trajectory segment `tau+` and negative segment `tau-`:

\[
\mathcal{L}_{\text{pref}} = -\log \sigma\left(\eta\left[\log \pi(\tau^+) - \log \pi(\tau^-)\right]\right).
\]

Use this as a fine-tuning term on top of positive-only or SM-RWBC.

## Why this may help

This turns bad demonstrations into a direct training signal even when trajectory filtering is imperfect.

## Risk

It may overfit scarce labels and degrade coverage. Treat this as second priority after SM-RWBC and CAU-BC.

## Status as of 2026-06-26

Implemented a reference-centered Demo-DPO preflight and first Can404 endpoint screen.

Artifacts:

- Preflight/setup script: `scripts/summarize_sota_demo_preference_preflight.py`.
- Screen summarizer: `scripts/summarize_sota_demo_preference_screen.py`.
- Trainer extension: `scripts/train_robomimic_official_transition_weighted.py` now supports disabled-by-default `sample_weight`, `preference_label`, and `--demo-preference-*` arguments.
- Preflight report: `results/sota_candidate/demo_pref_can404_lpos_lneg_preflight/demo_preference_preflight_REPORT.md`.
- Endpoint screen report: `results/sota_candidate/demo_preference_can404_screen_REPORT.md`.

Result:

- The setup initializes from the positive-only NN epoch-200 policy.
- BC remains on the positive-NN support (`50` train demos).
- The preference term compares the `10` labeled positives against the `10` labeled negatives; labeled negatives have `loss_weight=0` so they do not receive imitation loss.
- Non-reference preference was saturated at initialization: the positive-only checkpoint already assigned labeled negatives far lower likelihood than labeled positives, so the ordinary positive-minus-negative likelihood preference had zero loss in the smoke test.
- The screened recipe therefore used reference-centered DPO:
  - preference weight `1.0`;
  - temperature `1.0`;
  - margin `0.0`;
  - output anchor weight `10.0`;
  - `20` fine-tuning epochs, `100` gradient steps per epoch, checkpoints at epochs `5/10/15/20`.
- Can404 valid-positive-start results:
  - epoch `5`: `16/20`;
  - epoch `10`: `2/20`;
  - epoch `15`: `16/20`;
  - epoch `20`: `16/20`.
- Matched references:
  - positive-only NN: `17/20`;
  - weighted BC: `13/20`;
  - Candidate C sequence mask: `16/20`;
  - CAU action-conflict: `16/20`;
  - SafeExpand: `12/20`.

Decision:

- Reject this reference-centered labeled-demo preference recipe as a SOTA candidate.
- The preference term is active, but it does not improve the positive-only endpoint anchor and introduces an unstable checkpoint at epoch `10`.
- Do not scale this recipe unchanged. If preference learning is revisited, it needs harder hidden-label-free preference pairs or a stronger local action/state construction; labeled negatives alone are too easy for the positive-only reference and do not expose the split-404 failure mode.

---

# Candidate 6: Offline RL / IQL Revisit With Strong BC-RNN Policy Extraction

## Idea

Original Tri-PIQL/IQL-style extraction was unstable. A safer revisit is:

1. learn classifier reward `r = logit(c_theta)`;
2. train conservative Q/V on offline data with strong pessimism;
3. extract policy by advantage-weighted BC-RNN, not feed-forward actor;
4. combine with transition-risk masks.

## Why this might be publishable if it works

It reconnects the project to inverse RL. However, it is more engineering-heavy and less likely to work quickly than SM-RWBC or CAU-BC.

## Priority

Run only after Candidates 1--4 are exhausted.

## Status as of 2026-06-26

Implemented and screened a bounded classifier-reward IQL-AWBC version on the
hard Can404 split.

Artifacts:

- Preflight/setup script: `scripts/summarize_sota_iql_awbc_preflight.py`.
- Screen summarizer: `scripts/summarize_sota_iql_awbc_screen.py`.
- Anchor follow-up summarizer: `scripts/summarize_sota_anchored_iql_awbc_screen.py`.
- Preflight report: `results/sota_candidate/iql_awbc_can404_preflight/iql_awbc_preflight_REPORT.md`.
- Endpoint screen report: `results/sota_candidate/iql_awbc_can404_screen_REPORT.md`.
- Anchor follow-up report: `results/sota_candidate/anchored_iql_awbc_can404_screen_REPORT.md`.

Result:

- The preflight trained a small state-action classifier and Q/V model over the
  weighted-BC broad pool.
- Offline diagnostics looked promising:
  - state-action classifier labeled accuracy: `0.997`;
  - learned advantage means, positive / negative / unlabeled: `1.232` /
    `-1.184` / `-0.123`;
  - selected norm-topq hidden-bad weighted mass fraction: `0.326`, below the
    already rejected SM-RWBC broad-pool reference `0.376`.
- The endpoint policy collapsed despite the better offline diagnostic:
  - epoch `50`: `0/20`;
  - epoch `100`: `4/20`.
- A positive-initialized, output-anchored follow-up repaired the total collapse
  but still failed the Can404 gate:
  - epoch `5`: `10/20`;
  - epoch `10`: `13/20`;
  - epoch `15`: `11/20`;
  - epoch `20`: `12/20`.
- Matched Can404 references:
  - positive-only NN: `17/20`;
  - weighted BC: `13/20`;
  - Candidate C sequence mask: `16/20`;
  - CAU action-conflict: `16/20`;
  - Demo-DPO ref-centered: `16/20`.

Decision:

- Reject this classifier-reward IQL-AWBC norm-topq recipe as a SOTA candidate.
- Also reject the positive-initialized / output-anchored IQL-AWBC follow-up.
- The Q/V module can separate positive and negative advantages offline, but
  advantage-weighted extraction still does not preserve the positive-only
  control anchor.
- Do not scale this recipe unchanged. A future Offline RL revisit would need a
  different sequence-aware critic or policy-quality objective; simple
  advantage weighting, even with positive initialization and output anchoring,
  is not enough.

---

# Experimental protocol

## Stage 0: freeze the development matrix

Use the following screen splits:

| Purpose | Splits |
|---|---|
| severe Can regression | Can 40 split 404 |
| near-tie Can case | Can 40 split 505 |
| Can normal winners | Can 40 splits 101/202/303 |
| Lift instability | Lift 606/707, then fresh Lift 101/202/303/404/505 |
| bad-label benefit | hard-negative Can 101/202/303 |
| coverage-shift benefit | coverage-shift Can 101/202/303 |
| prefix-positive mechanism | prefix-positive Can 101/202/303 |

## Stage 1: cheap screens

Run 20 endpoint starts first, not 50.

Promotion criteria:

- candidate beats the best baseline on at least 70% of screened split-task units;
- no catastrophic regression larger than -4/20;
- candidate improves Can 404 or explicitly abstains / falls back to positive-only;
- candidate does not reduce Lift below the best simple branch by more than -2/20.

## Stage 2: full endpoint matrix

For candidates passing Stage 1:

- 5 fresh Can 40 splits: 101/202/303/404/505;
- 5 fresh Lift MG splits: 101/202/303/404/505;
- 3 generated probes: hard-negative, coverage-shift, prefix-positive;
- 50 valid-positive-start rollouts per split;
- epoch 200 fixed endpoint only;
- no best-checkpoint reporting.

## Stage 3: submission threshold

For a top-tier methods claim, require:

| Criterion | Minimum target |
|---|---:|
| Can 40p/80b over best per-split baseline | at least +20/250 |
| Lift MG over best per-split baseline | non-negative, ideally +10/250 |
| Combined Can+Lift | at least +25/500 |
| Generated probes | no worse than current bad-aware winners by more than -3/150 each |
| Paired bootstrap | interval need not be strictly positive, but lower bound should be much closer to 0 than current `-0.074` combined |
| Split stability | no single catastrophic split like Can 404 `-12/50` |

If these are not met, keep the paper as a precision/coverage empirical study.

---

# Implementation order

## Week 1: SM-RWBC

1. Add timestep weights to Robomimic BC-RNN-GMM loss.
2. Add scripts to precompute per-timestep classifier score and bad-action risk.
3. Run Can 404 / Can 505 / Lift 606 / Lift 707 first-20 screens.
4. If promising, run Can 101/202/303 first-20 screens.

## Week 2: CAU-BC

1. Add nearest-negative action retrieval cache.
2. Add action-unlikelihood hinge loss to BC-RNN-GMM.
3. Screen on the same split list.
4. Compare against SM-RWBC; keep only the stronger candidate.

## Week 3: SafeExpand and CCG-Distill

1. Implement SafeExpand support selection.
2. Implement CCG-Distill only if Candidate K-style confidence remains promising after split-calibrated thresholds.
3. Run 20-start screens.

## Week 4: full validation of the best candidate

1. Freeze a new method file, e.g. `METHOD_FREEZE_V03.md`.
2. Run full 50-start endpoint matrix.
3. Regenerate router-regret and precision/coverage tables.
4. Decide whether the new result supports a methods claim or stays a diagnostic.

---

# What to stop doing

Do not spend more time on:

- fixed global thresholds;
- support-margin-only routing;
- purity-only support selection;
- more post-hoc Can-only candidate tuning;
- best-checkpoint reporting;
- claiming full inverse-Q / Tri-PIQL validation before the actor extraction actually beats BC baselines.

---

# Paper decision tree

## If a new candidate clears the method threshold

Reframe the paper around the new method:

> Bad demonstrations improve offline imitation when used as transition-level action-risk constraints, not merely as trajectory labels.

Main paper becomes:

1. problem setting;
2. transition-risk method;
3. controlled PointNav;
4. default Can+Lift SOTA matrix;
5. generated regime probes;
6. ablations proving bad-risk terms matter.

## If no candidate clears the threshold

Submit the current paper as:

> A precision/coverage empirical study of when bad demonstrations help offline imitation.

Do not force a SOTA claim. The current study is still valuable if the claims remain disciplined.
