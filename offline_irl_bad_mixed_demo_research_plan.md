# Research Plan: Offline IRL from Bad and Mixed Demonstrations

**Working title:** *Tri-PIQL: Tri-Signal Preference-Weighted Inverse Q-Learning for Offline IRL from Good, Bad, and Mixed Demonstrations*  
**Version:** 0.1  
**Date:** 2026-06-22  
**Compute assumption:** one NVIDIA RTX 4090; prioritize state-based environments, cached datasets, compact MLPs, and fixed offline data.

---

## 0. One-sentence paper idea

Real offline logs contain a small amount of known good behavior, a small amount of known bad behavior, and a large unlabeled mixture. We propose a non-adversarial offline IRL method that learns a calibrated latent desirability score for unlabeled trajectories, uses explicit bad demonstrations as anti-preference constraints, and trains a conservative inverse-Q reward/policy that imitates likely-good behavior while avoiding bad behavior.

---

## 1. Motivation and gap

### Problem setting

Most offline imitation / IRL work assumes one of the following:

1. **Expert-only demonstrations**: learn from scarce high-quality demonstrations.
2. **Expert + imperfect demonstrations**: learn from a small expert set and a larger lower-quality set.
3. **Bad-only demonstrations**: learn what to avoid from explicitly undesirable demonstrations.
4. **Expert + bad demonstrations**: learn from contrasting positive and negative data.

The practical setting you should target is slightly richer:

$$
\mathcal D = \mathcal D^+ \cup \mathcal D^- \cup \mathcal D^u
$$

where:

- $\mathcal D^+$: small set of desirable / expert / successful trajectories.
- $\mathcal D^-$: small set of undesirable / failure / unsafe trajectories.
- $\mathcal D^u$: large unlabeled mixed-quality trajectory log.
- Environment reward is hidden during training.
- Online environment interaction is not allowed during training.
- Evaluation uses true simulator reward, success, or cost only after training.

### Why this can be high-impact

The recent literature has moved directly toward this area:

- **IQ-Learn** showed that inverse soft-Q learning can avoid adversarial training and learn rewards/policies from demonstrations.
- **DemoDICE** uses supplementary imperfect demonstrations to stabilize offline imitation.
- **SMODICE** formulates offline imitation as state-occupancy matching.
- **SPRINQL** targets offline imitation from expert plus suboptimal demonstrations.
- **No Experts, No Problem** studies avoidance learning from undesirable demonstrations.
- **Learning What to Do and What Not To Do** studies expert + undesirable demonstrations through a difference-of-KL formulation.

Your gap:

> Existing methods usually do not fully exploit the tri-signal setting: scarce positives, scarce explicit negatives, and a large contaminated unlabeled log with unknown quality. The key research opportunity is to make unlabeled data useful without accidentally imitating hidden bad behavior.

---

## 2. Target contribution

### Main contribution

Propose **Tri-PIQL**: **Tri-Signal Preference-Weighted Inverse Q-Learning**.

Tri-PIQL jointly learns:

1. A **desirability posterior** $q_\eta(\tau)\in[0,1]$ for each unlabeled trajectory.
2. A **signed state-action confidence** $c_\eta(s,a)\in[-1,1]$ indicating whether a transition looks good-like or bad-like.
3. An **implicit inverse-Q reward** $r_\psi(s,a,s')$ and Q-function $Q_\theta(s,a)$.
4. A policy $\pi_\omega(a|s)$ trained by advantage-weighted cloning on likely-good data and avoidance penalties on bad data.

### The core novelty

The method does **not** merely throw bad demonstrations away. It uses them in three ways:

1. **Ranking signal:** good trajectories should receive higher inferred return than unlabeled-likely-good trajectories, which should receive higher inferred return than bad trajectories.
2. **Advantage sign signal:** known good actions should have positive advantage; known bad actions should have negative advantage.
3. **Conservative reward shaping:** the learned reward/Q should not assign high value to bad or unsupported actions.

### Paper claim to aim for

> Explicit bad demonstrations are most useful when treated as anti-preference constraints and combined with a calibrated latent-quality model for the unlabeled log. This prevents the common failure mode where offline IRL imitates the large mixed dataset, including its hidden failures.

---

## 3. Formal problem statement

Let the MDP be:

$$
\mathcal M=(\mathcal S,\mathcal A,P,\gamma,r^\star,\rho_0)
$$

where $r^\star$ is unknown during training. You observe fixed offline trajectories:

$$
\tau_i = (s_0,a_0,s_1,a_1,\dots,s_T)
$$

partitioned into:

$$
\mathcal D^+,\quad \mathcal D^-,\quad \mathcal D^u
$$

with trajectory-level labels:

$$
y(\tau)=
\begin{cases}
+1 & \tau\in\mathcal D^+\\
-1 & \tau\in\mathcal D^-\\
\text{latent} & \tau\in\mathcal D^u
\end{cases}
$$

Goal:

$$
\text{learn } r_\psi \text{ and } \pi_\omega \text{ such that } \pi_\omega
$$

1. achieves high true return under $r^\star$,
2. avoids the state-action occupancy of $\mathcal D^-$,
3. uses $\mathcal D^u$ for support and stitching,
4. does not require online interaction or true rewards.

A suitable optimization target is:

$$
\max_\pi \; J_{r_\psi}(\pi)
-
\lambda_- D_{\text{sim}}(d_\pi, d^-)
-
\lambda_{\text{ood}}\operatorname{OOD}(\pi,\mathcal D)
$$

where $d_\pi$ is the policy occupancy, $d^-$ is the bad-demo occupancy, and $r_\psi$ is inferred from positive, negative, and unlabeled demonstrations.

---

## 4. Proposed method: Tri-PIQL

### 4.1 Method overview

Tri-PIQL has four modules:

1. **Trajectory desirability model**
   - Learns $q_\eta(\tau)$, the probability that an unlabeled trajectory is desirable.
   - Trained from positive-vs-negative ranking plus unlabeled calibration.

2. **Signed transition confidence model**
   - Learns $c_\eta(s,a)\in[-1,1]$, a dense good-like / bad-like score.
   - Used to weight transition-level inverse-Q losses.

3. **Inverse-Q reward learner**
   - Learns $Q_\theta,V_\theta,r_\psi$ from Bellman consistency plus signed advantage constraints.
   - Good actions are pushed to positive advantage.
   - Bad actions are pushed to negative advantage.
   - Unlabeled actions are weighted by latent desirability.

4. **Offline policy extractor**
   - Uses advantage-weighted behavior cloning on positive and likely-positive samples.
   - Avoids cloning known bad samples.
   - Optionally includes a conservative penalty to reduce unsupported action optimism.

---

## 5. Loss functions

### 5.1 Trajectory return under learned reward

For a trajectory $\tau$:

$$
R_\psi(\tau)=\sum_{t=0}^{T-1}\gamma^t r_\psi(s_t,a_t,s_{t+1})
$$

Use normalized returns during training:

$$
\tilde R_\psi(\tau)=\frac{R_\psi(\tau)-\mu_R}{\sigma_R+\epsilon}
$$

where $\mu_R,\sigma_R$ are moving averages over recent minibatches.

---

### 5.2 Positive-vs-negative ranking loss

Known good trajectories should outrank known bad trajectories:

$$
\mathcal L_{\text{pn-rank}}
=
\mathbb E_{\tau^+\sim\mathcal D^+,\tau^-\sim\mathcal D^-}
\left[
\operatorname{softplus}
\left(
m - \tilde R_\psi(\tau^+) + \tilde R_\psi(\tau^-)
\right)
\right]
$$

where $m>0$ is a margin.

---

### 5.3 Unlabeled latent desirability

Define:

$$
q_\eta(\tau)=\sigma\left(\frac{\tilde R_\psi(\tau)-b_\eta}{T_q}\right)
$$

where $b_\eta$ is a learned or moving-threshold bias and $T_q$ is a temperature.

Use stop-gradient on $q_\eta$ in the Q/reward update to avoid collapse:

$$
\bar q(\tau)=\operatorname{stopgrad}(q_\eta(\tau))
$$

A simple unlabeled calibration regularizer:

$$
\mathcal L_{\text{prior}}
=
\left(
\frac{1}{|\mathcal B^u|}
\sum_{\tau\in\mathcal B^u}
q_\eta(\tau)
-
\pi_u
\right)^2
$$

where $\pi_u$ is the assumed good fraction in the unlabeled log. In experiments, sweep $\pi_u\in\{0.25,0.5,0.75\}$. If unknown, set $\pi_u=0.5$ and report sensitivity.

Entropy regularization prevents early hard assignments:

$$
\mathcal L_{\text{entropy}}
=
-
\mathbb E_{\tau^u}
\left[
q_\eta(\tau^u)\log q_\eta(\tau^u)
+
(1-q_\eta(\tau^u))\log(1-q_\eta(\tau^u))
\right]
$$

Use this only during warm-up, then anneal it down.

---

### 5.4 Signed transition confidence

Train a transition classifier:

$$
p_\eta(y=+1|s,a)=\sigma(f_\eta(s,a))
$$

and define:

$$
c_\eta(s,a)=2p_\eta(y=+1|s,a)-1
$$

Supervised loss:

$$
\mathcal L_{\text{cls}}
=
-
\mathbb E_{(s,a)\sim\mathcal D^+}\log p_\eta(+|s,a)
-
\mathbb E_{(s,a)\sim\mathcal D^-}\log (1-p_\eta(+|s,a))
$$

Unlabeled regularizer:

$$
\mathcal L_{\text{u-cls}}
=
\mathbb E_{(s,a)\sim\mathcal D^u}
\left[
\bar q(\tau)\cdot CE(1,p_\eta(+|s,a))
+
(1-\bar q(\tau))\cdot CE(0,p_\eta(+|s,a))
\right]
$$

This gives dense transition-level weights while the trajectory posterior supplies coarse latent labels.

---

### 5.5 Inverse-Q Bellman consistency

Use an IQL-style value function:

$$
V_\theta(s)
=
\operatorname{Expectile}_\tau
\left[
Q_\theta(s,a),\; a\sim \mathcal D(\cdot|s)
\right]
$$

Then enforce:

$$
Q_\theta(s,a)
\approx
r_\psi(s,a,s')+\gamma V_\theta(s')
$$

with:

$$
\mathcal L_{\text{td}}
=
\mathbb E_{(s,a,s')\sim\mathcal D}
\left[
\left(
Q_\theta(s,a)
-
r_\psi(s,a,s')
-
\gamma V_\theta(s')
\right)^2
\right]
$$

This lets $r_\psi$ be explicit and inspectable while $Q_\theta$ remains useful for policy extraction.

---

### 5.6 Signed advantage constraints

Define:

$$
A_\theta(s,a)=Q_\theta(s,a)-V_\theta(s)
$$

Good actions should have positive advantage:

$$
\mathcal L_{\text{good-adv}}
=
\mathbb E_{(s,a)\sim \mathcal D^+}
\left[
\operatorname{softplus}(m_+ - A_\theta(s,a))
\right]
$$

Bad actions should have negative advantage:

$$
\mathcal L_{\text{bad-adv}}
=
\mathbb E_{(s,a)\sim \mathcal D^-}
\left[
\operatorname{softplus}(m_- + A_\theta(s,a))
\right]
$$

Unlabeled actions are weighted by latent desirability:

$$
\mathcal L_{\text{u-adv}}
=
\mathbb E_{(s,a,\tau)\sim \mathcal D^u}
\left[
\bar q(\tau)\operatorname{softplus}(m_+ - A_\theta(s,a))
+
(1-\bar q(\tau))\operatorname{softplus}(m_- + A_\theta(s,a))
\right]
$$

Total signed advantage loss:

$$
\mathcal L_{\text{adv}}
=
\mathcal L_{\text{good-adv}}
+
\mathcal L_{\text{bad-adv}}
+
\lambda_u\mathcal L_{\text{u-adv}}
$$

---

### 5.7 Conservative anti-bad regularization

Use a CQL-like penalty, but target it at unsupported and bad actions:

$$
\mathcal L_{\text{cons}}
=
\mathbb E_{s\sim\mathcal D}
\left[
\log \sum_{a\in\mathcal A_{\text{sample}}(s)}
\exp(Q_\theta(s,a))
\right]
-
\mathbb E_{(s,a)\sim\mathcal D^+ \cup \mathcal D^u_{\text{likely+}}}
\left[
Q_\theta(s,a)
\right]
+
\lambda_b\mathbb E_{(s,a)\sim\mathcal D^-}
\left[
Q_\theta(s,a)
\right]
$$

For continuous actions, $\mathcal A_{\text{sample}}(s)$ contains:

- the dataset action,
- actions sampled from the current policy,
- random actions from a uniform or Gaussian proposal,
- optional actions from a behavior VAE.

This discourages high Q-values for unsupported actions and directly lowers Q on bad demonstrations.

---

### 5.8 Actor / policy extraction

Use advantage-weighted regression, but only clone samples believed to be good:

$$
w(s,a,\tau)=
\begin{cases}
1 & (s,a)\in\mathcal D^+\\
0 & (s,a)\in\mathcal D^-\\
\operatorname{clip}(\bar q(\tau),w_{\min},1) & (s,a)\in\mathcal D^u
\end{cases}
$$

Actor loss:

$$
\mathcal L_\pi
=
-
\mathbb E_{(s,a,\tau)\sim\mathcal D}
\left[
w(s,a,\tau)
\cdot
\exp(A_\theta(s,a)/\beta)
\cdot
\log \pi_\omega(a|s)
\right]
$$

For continuous control, implement this as weighted Gaussian negative log likelihood or MSE behavioral cloning.

Optional bad-action unlikelihood loss:

$$
\mathcal L_{\text{unlike}}
=
\mathbb E_{(s,a^-)\sim\mathcal D^-}
\left[
\max(0,\log \pi_\omega(a^-|s)-\kappa)
\right]
$$

In continuous actions, use this cautiously. It can destabilize training if the action density is poorly calibrated. Start without it.

---

### 5.9 Full objective

$$
\mathcal L
=
\mathcal L_{\text{td}}
+
\lambda_{\text{rank}}\mathcal L_{\text{pn-rank}}
+
\lambda_{\text{adv}}\mathcal L_{\text{adv}}
+
\lambda_{\text{cls}}\left(\mathcal L_{\text{cls}}+\mathcal L_{\text{u-cls}}\right)
+
\lambda_{\text{cons}}\mathcal L_{\text{cons}}
+
\lambda_{\text{prior}}\mathcal L_{\text{prior}}
-
\lambda_H \mathcal L_{\text{entropy}}
+
\lambda_{\text{reg}}\|r_\psi\|_2^2
$$

Actor objective:

$$
\min_\omega \mathcal L_\pi
$$

Train critic/reward and actor either alternating or with actor delayed until critic warm-up.

---

## 6. Algorithm pseudocode

```text
Algorithm: Tri-PIQL

Input:
    D+ : small desirable trajectory set
    D- : small undesirable trajectory set
    Du : large unlabeled mixed trajectory set
    gamma, expectile tau, margins m+, m-, lambdas

Initialize:
    reward r_psi
    Q_theta, V_theta
    actor pi_omega
    transition confidence model c_eta
    trajectory quality threshold b_eta

Step 1: Preprocess
    normalize observations and actions
    split each dataset into train / validation trajectories
    hide true environment rewards from training
    compute trajectory lengths and terminal flags

Step 2: Warm-up desirability model
    for K_warmup updates:
        sample trajectories tau+ from D+, tau- from D-, tauu from Du
        compute R_psi(tau)
        update r_psi and c_eta using:
            positive-vs-negative ranking
            transition classifier
            unlabeled prior + entropy
        update q_eta(tauu)

Step 3: Joint inverse-Q reward learning
    for K_Q updates:
        sample balanced minibatch:
            B+ from D+
            B- from D-
            Bu from Du
        compute q_bar(tauu) = stopgrad(q_eta(tauu))
        update V by expectile regression over dataset actions
        update Q and r with:
            Bellman consistency
            signed advantage constraints
            ranking loss
            conservative anti-bad penalty
        periodically update q_eta and c_eta

Step 4: Policy extraction
    for K_pi updates:
        sample transitions from D+, D-, Du
        compute advantage A = Q - V
        compute weights:
            1 for D+
            0 for D-
            q_bar for Du
        update actor by weighted advantage regression

Step 5: Model selection
    choose checkpoint by:
        validation positive-vs-negative ranking AUC
        validation bad-action advantage separation
        q calibration on held-out labeled data
        no use of environment return for selection

Output:
    learned reward r_psi
    policy pi_omega
    diagnostics: q calibration, reward maps, Q separation, bad occupancy
```

---

## 7. Datasets

Use a three-tier dataset plan. Do not start with image-based robotics.

### Tier 1: custom diagnostic environments

These are essential. They are cheap and give clear proof-of-concept.

#### 7.1 GridWorld: Good path vs bad shortcut

Environment:

- 2D grid.
- Start in bottom-left.
- Goal in top-right.
- Trap/reward-hacking area near the goal.
- Bad trajectories reach trap or exploit shortcut that fails OOD.
- Good trajectories reach goal safely.
- Unlabeled trajectories are a mixture.

Why this matters:

- You can visualize learned reward.
- You can verify whether bad demos are assigned negative advantage.
- You can show failure of BC-all, DemoDICE-style imperfect imitation, and naive filtering.

Metrics:

- success rate,
- trap rate,
- reward correlation with true reward,
- occupancy KL to good and bad,
- learned reward heatmap.

#### 7.2 PointMaze / MiniGrid

Use these before MuJoCo if debugging is hard.

Suggested tasks:

- PointMaze U-Maze.
- PointMaze Medium.
- MiniGrid FourRooms.

Construct labels:

- $\mathcal D^+$: trajectories that reach the goal quickly.
- $\mathcal D^-$: trajectories that terminate far from the goal, hit trap zones, or follow deliberately wrong goals.
- $\mathcal D^u$: all remaining trajectories.

---

### Tier 2: D4RL / Minari state-based benchmarks

Use Minari’s D4RL group where possible because it provides current dataset handling around Gymnasium-style APIs.

Suggested first tasks:

1. `hopper-medium-replay`
2. `walker2d-medium-replay`
3. `halfcheetah-medium-replay`
4. `hopper-medium-expert`
5. `walker2d-medium-expert`

Construct labels using true trajectory return only for dataset tagging and evaluation, not for reward learning:

- $\mathcal D^+$: top 5–10% trajectories by return.
- $\mathcal D^-$: bottom 5–20% trajectories by return.
- $\mathcal D^u$: middle 70–90%.

Report label budget sweeps:

- positives: 5, 10, 20, 50 trajectories.
- negatives: 5, 10, 20, 50 trajectories.
- unlabeled: 10%, 25%, 50%, 100% of remaining dataset.

Important: keep labels trajectory-level, not transition-level, except when using all transitions inside labeled trajectories.

---

### Tier 3: Robomimic low-dimensional mixed-quality data

Use Robomimic **low-dimensional** datasets, not images.

Recommended:

1. `Can Paired`
   - It contains paired good and bad demonstrations under identical initializations.
   - This is almost perfect for your problem.
2. `Lift MG` or `Can MG`
   - Machine-generated mixed-quality rollouts from SAC checkpoints.
3. `Can MH`
   - Human demonstrations from operators with mixed proficiency.

Construct:

- $\mathcal D^+$: good paired trajectories or successful high-quality trajectories.
- $\mathcal D^-$: bad paired trajectories or failures.
- $\mathcal D^u$: mixed human/machine trajectories.

Metrics:

- task success rate,
- bad-bin/toss-out rate for Can,
- action smoothness,
- recovery from similar initial states.

This tier gives robotics relevance without needing image training.

---

### Optional Tier 4: offline safe RL / Safety Gymnasium / DSRL

Use as a safety extension if the main method works.

Construct:

- $\mathcal D^+$: high-return low-cost trajectories.
- $\mathcal D^-$: high-cost / constraint-violating trajectories.
- $\mathcal D^u$: mixed safe and unsafe logs.

Metrics:

- normalized return,
- cumulative cost,
- violation rate,
- safe success rate.

This tier supports the story that “bad demonstrations are useful for learning what not to do.”

---

## 8. Baselines

Use baselines in increasing order of difficulty. Do not implement every baseline before you have the main method working.

### 8.1 Required baselines

1. **BC-positive**
   - Behavioral cloning only on $\mathcal D^+$.
   - Tests whether positive demos alone are enough.

2. **BC-all**
   - Behavioral cloning on $\mathcal D^+\cup\mathcal D^u$.
   - Should fail when unlabeled contains hidden bad behavior.

3. **BC-filter**
   - Train a classifier using $\mathcal D^+$ and $\mathcal D^-$, score $\mathcal D^u$, clone top-scoring samples.
   - Strong simple baseline.

4. **Weighted BC**
   - Same as BC-filter but uses soft weights instead of hard filtering.
   - Important because your actor resembles weighted BC; your Q/reward component must add value.

5. **IQ-Learn**
   - Train from $\mathcal D^+$ only.
   - Optionally add a variant that treats $\mathcal D^u$ as imperfect demos.

6. **DemoDICE**
   - Expert + imperfect demonstrations.
   - Natural baseline for $\mathcal D^+$ plus $\mathcal D^u$.

7. **SPRINQL**
   - Expert + suboptimal demonstrations.
   - Strong recent baseline for positive + suboptimal data.

8. **UNIQ / No Experts, No Problem**
   - Bad + unlabeled avoidance baseline.
   - Important when testing whether positives add value.

9. **Expert+Bad difference-of-KL baseline**
   - Implement a ContraDICE-style objective or use available code if released.
   - Uses $\mathcal D^+$ and $\mathcal D^-$, optionally ignoring $\mathcal D^u$.

10. **IQL-oracle**
    - Offline RL using true environment reward.
    - This is an upper bound, not a fair IRL baseline.

11. **CQL-oracle**
    - Another true-reward upper bound.
    - Useful for sanity checking dataset quality.

---

## 9. Experimental design

### 9.1 Main research questions

**RQ1.** Can explicit bad demonstrations improve offline IRL when positive demos are scarce?

**RQ2.** Can Tri-PIQL use unlabeled mixed logs without imitating hidden bad behavior?

**RQ3.** Does the learned reward generalize better than pure filtering or weighted BC?

**RQ4.** Is the method robust to label scarcity, bad-label noise, and unlabeled contamination?

**RQ5.** Does the inverse-Q component add value beyond a supervised classifier?

---

### 9.2 Main tables

#### Table 1: Main performance

Rows:

- BC-positive
- BC-all
- BC-filter
- Weighted BC
- IQ-Learn
- DemoDICE
- SPRINQL
- UNIQ / No Experts
- Expert+Bad KL baseline
- Tri-PIQL
- IQL-oracle
- CQL-oracle

Columns:

- Hopper medium-replay
- Walker2d medium-replay
- HalfCheetah medium-replay
- PointMaze medium
- Robomimic Can Paired
- Safety task if included

Metrics:

- normalized return,
- success rate if available,
- bad occupancy / failure rate,
- mean ± standard error across seeds.

#### Table 2: Label budget sweep

Vary:

- $n_+ \in \{5,10,20,50\}$
- $n_- \in \{0,5,10,20,50\}$

Show:

- performance improves most when adding first few bad demonstrations,
- diminishing returns after enough bad labels,
- method remains useful with very few positives.

#### Table 3: Unlabeled contamination sweep

Construct unlabeled dataset with bad fraction:

$$
p_{\text{bad}}\in \{0,0.1,0.25,0.5,0.75\}
$$

Expected result:

- BC-all degrades monotonically as bad fraction rises.
- DemoDICE / SPRINQL degrade when unlabeled is heavily contaminated.
- Tri-PIQL should be more robust because it estimates $q(\tau)$ and uses explicit anti-bad constraints.

#### Table 4: Ablations

Ablations:

1. no bad advantage loss,
2. no latent $q(\tau)$,
3. no ranking loss,
4. no conservative penalty,
5. no transition classifier,
6. no unlabeled data,
7. hard filtering instead of soft $q$,
8. actor-only weighted BC using same $q$,
9. reward-only no actor advantage weighting.

Goal:

- show each component matters,
- especially show the Q/reward component beats classifier-only filtering.

---

## 10. Evaluation metrics

### 10.1 Policy metrics

Use true environment reward only at evaluation time.

1. **Normalized return**
   - D4RL-style normalized score where applicable.

2. **Success rate**
   - Maze/Robomimic.

3. **Bad event rate**
   - trap rate,
   - failure terminal rate,
   - unsafe cost violation,
   - bad-bin rate in Robomimic Can.

4. **Good-vs-bad occupancy ratio**

$$
\Delta_{\text{occ}}
=
D(d_\pi,d^-)
-
D(d_\pi,d^+)
$$

A good policy should be close to $d^+$ and far from $d^-$.

5. **Behavior support**
   - average log likelihood under a behavior density model,
   - nearest-neighbor action distance to dataset support.

---

### 10.2 Reward metrics

Where ground-truth reward exists:

1. **Reward correlation**
   - Spearman correlation between $r_\psi$ and $r^\star$ on held-out transitions.
   - Also compute trajectory-return rank correlation.

2. **Positive-vs-negative AUC**
   - AUC of $R_\psi(\tau)$ separating held-out $\mathcal D^+$ and $\mathcal D^-$.

3. **OOD reward sanity**
   - Generate random or policy-sampled actions.
   - Check whether $r_\psi$ assigns unreasonable high reward to unsupported actions.

4. **Reward heatmaps**
   - GridWorld / PointMaze.
   - Visualize whether traps are negative and goals are positive.

---

### 10.3 Latent quality metrics

For unlabeled data where synthetic labels are known but hidden during training:

1. **Trajectory $q(\tau)$ AUC**
2. **Brier score**
3. **Expected calibration error**
4. **Distribution of $q$ for true good, medium, and bad trajectories**
5. **Stability of $q$ across random seeds**

---

### 10.4 Q-function diagnostics

1. Mean $A(s,a)$ on $\mathcal D^+$, $\mathcal D^u$, $\mathcal D^-$.
2. Histogram of Q-values for:
   - positive actions,
   - bad actions,
   - policy-sampled actions,
   - random actions.
3. Bellman residual on held-out transitions.
4. Advantage separation:

$$
\Delta_A =
\mathbb E_{\mathcal D^+}[A(s,a)]
-
\mathbb E_{\mathcal D^-}[A(s,a)]
$$

This should be positive and large.

---

## 11. Diagnostic experiments

### Diagnostic 1: Does bad data help beyond positive demos?

Run with fixed $n_+=10$ and vary $n_-$.

Plot:

- normalized return vs $n_-$,
- bad event rate vs $n_-$,
- advantage separation vs $n_-$.

Expected:

- adding a few bad demos should sharply reduce bad event rate.
- too many bad demos should not hurt if weighting is calibrated.

---

### Diagnostic 2: Is the unlabeled posterior meaningful?

On D4RL synthetic labels:

- hide labels during training,
- after training compare $q(\tau)$ to true return quantiles.

Expected:

- $q$ should increase monotonically with true return quantile.
- If not, ranking/reward is unstable.

---

### Diagnostic 3: Is the method merely doing filtering?

Compare:

- BC-filter,
- Weighted BC with same $q$,
- Tri-PIQL.

Expected:

- Tri-PIQL should win on long-horizon and stitching tasks.
- If not, your method is not adding enough beyond supervised filtering.

---

### Diagnostic 4: Does conservative penalty prevent reward hacking?

Generate candidate actions from:

- current actor,
- random Gaussian,
- behavior VAE,
- adversarial action search maximizing $Q$.

Measure:

- Q-values,
- reward values,
- nearest-neighbor distance to dataset action support.

Expected:

- without conservative penalty, OOD actions may get high Q.
- with penalty, OOD high-Q actions should decrease.

---

### Diagnostic 5: Label noise robustness

Flip a fraction of labels:

$$
p_{\text{flip}}\in\{0,0.05,0.1,0.2\}
$$

Expected:

- hard-filtering baselines degrade faster.
- Tri-PIQL should be more robust if $q$, margins, and conservative penalties are not too brittle.

---

## 12. Implementation plan

### 12.1 Repository structure

```text
tri_piql/
  README.md
  configs/
    gridworld.yaml
    d4rl_hopper.yaml
    d4rl_walker2d.yaml
    robomimic_can_paired.yaml
  tri_piql/
    algos/
      tri_piql.py
      bc.py
      weighted_bc.py
      iql_oracle.py
      cql_oracle.py
    datasets/
      minari_loader.py
      d4rl_loader.py
      robomimic_loader.py
      label_splits.py
    envs/
      gridworld.py
      wrappers.py
    networks/
      mlp.py
      actor.py
      critic.py
      reward.py
      classifier.py
    eval/
      rollout.py
      reward_diagnostics.py
      calibration.py
      occupancy.py
    utils/
      replay_buffer.py
      normalization.py
      logging.py
      seeds.py
  scripts/
    make_splits.py
    train_tri_piql.py
    train_baseline.py
    eval_policy.py
    plot_tables.py
  tests/
    test_gridworld.py
    test_losses.py
```

---

### 12.2 Minimal configuration

Start with:

```yaml
seed: 0
gamma: 0.99
batch_size: 256
batch_pos: 64
batch_neg: 64
batch_unlabeled: 128

network:
  hidden_dims: [256, 256]
  activation: relu
  layer_norm: false

optimizer:
  lr_actor: 3.0e-4
  lr_critic: 3.0e-4
  lr_reward: 3.0e-4
  lr_classifier: 3.0e-4

iql:
  expectile: 0.7
  actor_temperature: 3.0
  advantage_clip: 100.0

tri_piql:
  margin_pos: 0.5
  margin_neg: 0.5
  lambda_rank: 1.0
  lambda_adv: 1.0
  lambda_cls: 0.5
  lambda_cons: 0.1
  lambda_prior: 0.1
  lambda_entropy: 0.01
  lambda_reward_l2: 1.0e-4
  q_clip_min: 0.05
  q_temperature: 1.0
  unlabeled_good_prior: 0.5

training:
  warmup_steps: 20000
  critic_steps: 300000
  actor_delay_steps: 50000
  eval_every: 10000
  save_every: 25000
```

For D4RL/Minari state-based locomotion, this should fit easily on one 4090. For Robomimic low-dimensional, use the same MLP size first.

---

## 13. Step-by-step project roadmap

### Stage 1: build the diagnostic environment

Deliverables:

- GridWorld environment.
- Script to generate:
  - good trajectories,
  - bad trajectories,
  - unlabeled mixed trajectories.
- Visualization of true reward, true occupancy, learned reward.
- BC-positive, BC-all, Weighted BC baselines.

Pass criterion:

- BC-all fails when unlabeled has many bad trajectories.
- A simple classifier can separate obvious good and bad data.
- Tri-PIQL learns negative reward around trap states and positive reward near goal.

---

### Stage 2: implement Tri-PIQL core losses

Deliverables:

- trajectory ranking loss,
- latent $q(\tau)$,
- transition confidence $c(s,a)$,
- Q/V/reward losses,
- actor extraction,
- logging for all diagnostics.

Pass criterion:

- On GridWorld:
  - $R_\psi(\tau^+) > R_\psi(\tau^-)$,
  - $A(s,a)$ positive on good actions,
  - $A(s,a)$ negative on bad actions,
  - policy reaches goal and avoids trap.

---

### Stage 3: D4RL/Minari locomotion experiments

Deliverables:

- data loader,
- trajectory-level return tagging,
- split generation saved to disk,
- main baseline runs:
  - BC-positive,
  - BC-all,
  - Weighted BC,
  - IQ-Learn,
  - IQL-oracle,
  - Tri-PIQL.

Pass criterion:

- Tri-PIQL beats BC-positive and BC-all under scarce positive labels.
- Tri-PIQL is competitive with or better than Weighted BC.
- $q(\tau)$ correlates with hidden true return quantiles.

---

### Stage 4: add stronger offline imitation baselines

Deliverables:

- DemoDICE baseline,
- SPRINQL baseline,
- UNIQ/No Experts baseline,
- Expert+Bad KL baseline if possible.

Pass criterion:

- Main table includes at least 5 strong baselines.
- Tri-PIQL wins clearly in at least:
  - high unlabeled contamination,
  - scarce positive labels,
  - explicit bad-label settings.

---

### Stage 5: Robomimic Can Paired

Deliverables:

- Robomimic low-dim loader.
- Can Paired split:
  - good paired demos as $\mathcal D^+$,
  - bad paired demos as $\mathcal D^-$,
  - optionally add mixed MG/MH as $\mathcal D^u$.
- Success and bad-outcome evaluation.

Pass criterion:

- Tri-PIQL avoids bad paired behavior better than BC-all and DemoDICE-style imperfect imitation.
- Weighted BC is strong; Tri-PIQL should beat it through better long-horizon recovery or robustness.

---

### Stage 6: ablations and diagnosis

Deliverables:

- label budget sweep,
- unlabeled contamination sweep,
- label noise sweep,
- conservative penalty ablation,
- reward heatmaps / Q histograms / q calibration plots.

Pass criterion:

- The method’s improvement is explainable.
- Removing bad advantage loss increases bad occupancy.
- Removing $q(\tau)$ makes the method imitate too much unlabeled bad data.
- Removing conservative penalty increases OOD high-Q actions.

---

### Stage 7: write the paper

Paper structure:

1. Introduction
   - Real logs contain good, bad, and unlabeled mixed behavior.
   - Offline IRL should learn both what to do and what not to do.

2. Related Work
   - offline IRL / imitation,
   - inverse Q-learning,
   - DICE / occupancy matching,
   - learning from suboptimal and undesirable demos,
   - offline RL conservatism.

3. Problem Formulation
   - tri-signal offline IRL.

4. Method
   - latent desirability posterior,
   - signed advantage constraints,
   - conservative inverse-Q learning,
   - actor extraction.

5. Experiments
   - diagnostic tasks,
   - D4RL/Minari,
   - Robomimic,
   - optional safety.

6. Diagnostics / Ablations
   - why the method works.

7. Limitations
   - depends on some reliable positive/negative labels,
   - latent $q$ can collapse if labels are too noisy,
   - continuous-action unlikelihood is hard,
   - image-based robotics not tested unless using cached features.

---

## 14. Expected outcomes

### Strong outcome

You can claim:

- Tri-PIQL consistently improves over BC, weighted BC, IQ-Learn, and DemoDICE/SPRINQL-style baselines in settings with scarce positives, explicit negatives, and contaminated unlabeled logs.
- Bad demonstrations reduce bad-event rates and improve learned reward identifiability.
- The learned $q(\tau)$ is calibrated and interpretable.
- Conservative anti-bad regularization prevents reward/Q overestimation on unsupported bad-like actions.

This is a plausible ICLR/ICML/NeurIPS-style story if experiments are clean.

### Medium outcome

You can claim:

- Tri-PIQL does not always improve final return, but substantially reduces bad event rate at similar return.
- It works best in safety-sensitive or failure-heavy datasets.
- The contribution becomes “offline IRL for safe behavior selection from mixed logs.”

This can still be a strong paper if safety metrics are compelling.

### Weak outcome

If Tri-PIQL is no better than Weighted BC:

- Pivot the paper toward a negative result:
  - “When does Q-based offline IRL add value beyond filtering?”
- Focus on diagnostics:
  - long-horizon stitching,
  - support mismatch,
  - reward identifiability.
- Add environments where filtering cannot solve the task because good partial trajectories must be stitched.

---

## 15. The most important plots

1. **Main performance bar chart**
   - return and bad event rate side by side.

2. **Unlabeled contamination curve**
   - x-axis: bad fraction in unlabeled data.
   - y-axis: normalized return and bad event rate.

3. **Label budget curve**
   - x-axis: number of negative demonstrations.
   - y-axis: bad event rate.

4. **Reward heatmap**
   - GridWorld / PointMaze.
   - Show good goal positive, trap negative.

5. **Advantage histograms**
   - $A(s,a)$ for good, unlabeled, bad.

6. **q calibration plot**
   - predicted $q$ vs true fraction good by bin.

7. **OOD Q histogram**
   - dataset actions vs random actions vs actor actions.

---

## 16. Practical tips for one 4090

1. Use **state observations only**.
2. Cache all datasets to disk as `.npz` or replay buffers.
3. Run image-based Robomimic only after the low-dimensional version works.
4. Use 2-layer MLPs with 256 hidden units.
5. Use 3 seeds while developing; use 5 seeds for final tables.
6. Start with one task and one split; never debug across all tasks at once.
7. Keep true rewards completely hidden during training and model selection.
8. Use validation ranking AUC and advantage separation for checkpoint selection.
9. Log every scalar needed to diagnose collapse:
   - $q$ mean,
   - $q$ entropy,
   - ranking loss,
   - good/bad advantage means,
   - conservative penalty,
   - actor loss,
   - reward scale.

---

## 17. Common failure modes and fixes

### Failure: $q(\tau)$ collapses to all 1 or all 0

Fixes:

- increase entropy warm-up,
- lower ranking loss weight,
- add prior $\pi_u$,
- clip $q\in[0.05,0.95]$,
- use delayed $q$ updates.

### Failure: learned reward becomes unbounded

Fixes:

- reward L2 penalty,
- reward clipping,
- moving normalization of trajectory returns,
- stronger conservative penalty.

### Failure: policy clones bad behavior

Fixes:

- set bad actor weights to zero,
- increase bad advantage loss,
- improve transition classifier,
- reduce unlabeled prior $\pi_u$,
- raise threshold for likely-good unlabeled samples.

### Failure: method underperforms Weighted BC

Fixes:

- test long-horizon/stitching tasks,
- strengthen Bellman consistency,
- use IQL-style actor extraction,
- add OOD/action support diagnostics,
- verify Q advantages are meaningful.

### Failure: D4RL results are noisy

Fixes:

- first validate on GridWorld and PointMaze,
- use trajectory-level splits with fixed seeds,
- reduce network size,
- check observation/action normalization,
- compare against oracle IQL to ensure dataset is learnable.

---

## 18. Initial experiment matrix

Start small:

| Stage | Environment | Baselines | Seeds | Goal |
|---|---:|---:|---:|---|
| 1 | GridWorld | BC+, BC-all, WBC, Tri-PIQL | 5 | prove mechanism |
| 2 | PointMaze U-Maze | BC+, BC-all, WBC, IQ-Learn, Tri-PIQL | 3 | debug continuous state/action if used |
| 3 | Hopper medium-replay | BC+, BC-all, WBC, IQ-Learn, IQL-oracle, Tri-PIQL | 3 | first D4RL result |
| 4 | Walker2d medium-replay | same | 3 | robustness |
| 5 | HalfCheetah medium-replay | same | 3 | robustness |
| 6 | Robomimic Can Paired low-dim | BC+, BC-all, WBC, DemoDICE, Tri-PIQL | 3 | robotics relevance |
| 7 | Full table | all feasible baselines | 5 | final paper |

---

## 19. Paper positioning

### Suggested abstract skeleton

> Offline inverse reinforcement learning usually assumes access to expert demonstrations, yet real logs often contain scarce successes, explicit failures, and large unlabeled mixtures of unknown quality. We study offline IRL from tri-signal demonstrations: a small desirable set, a small undesirable set, and a large unlabeled mixed set. We introduce Tri-PIQL, a non-adversarial inverse-Q learning method that estimates latent trajectory desirability, imposes signed advantage constraints to imitate good actions and avoid bad actions, and uses a conservative anti-bad regularizer to prevent reward overestimation on unsupported behavior. Across diagnostic environments, D4RL/Minari locomotion and maze tasks, and low-dimensional Robomimic mixed-quality manipulation, Tri-PIQL improves return and reduces bad-event occupancy under scarce positive labels and heavy unlabeled contamination. Diagnostics show that explicit negative demonstrations improve reward identifiability and reduce hidden failure imitation.

### Suggested title variants

1. **Offline IRL from What to Do, What Not to Do, and Mixed Logs**
2. **Tri-Signal Inverse Q-Learning from Good, Bad, and Unlabeled Demonstrations**
3. **Learning to Imitate and Avoid from Mixed-Quality Offline Demonstrations**
4. **Bad Demonstrations Are Useful: Offline IRL with Contrastive Mixed Logs**

---

## 20. Theory package to attempt

A full theory result is not necessary at first, but one compact theorem can strengthen the paper.

### Theorem idea 1: calibrated latent weighting recovers signed occupancy preference

Assume:

- finite MDP,
- known calibrated $q(\tau)=P(y=+|\tau)$,
- sufficient support in $\mathcal D^u$.

Show that minimizing the weighted signed occupancy objective:

$$
D_f(d_\pi || d^+) - \lambda D_f(d_\pi || d^-)
$$

with weights from $q$ is equivalent to optimizing a lower bound on the expected preference utility of $\pi$ under the latent mixture model.

### Theorem idea 2: signed advantage constraints separate good and bad occupancies

If:

$$
A(s,a)\ge m_+ \quad \forall (s,a)\in\operatorname{supp}(d^+)
$$

and

$$
A(s,a)\le -m_- \quad \forall (s,a)\in\operatorname{supp}(d^-)
$$

then any policy extracted by advantage-weighted regression assigns exponentially larger likelihood to good-supported actions than bad-supported actions, with ratio controlled by:

$$
\exp((m_+ + m_-)/\beta)
$$

This is simple and useful because it connects the loss to the actor behavior.

### Theorem idea 3: conservative penalty bounds bad-action optimism

In tabular MDPs, show that adding:

$$
\lambda_b\mathbb E_{d^-}[Q(s,a)]
$$

plus CQL-style log-sum-exp regularization reduces the maximum Q assigned to bad-supported actions relative to good-supported actions, under fixed Bellman residual.

Keep theory modest. A clean proposition plus diagnostic experiments may be enough.

---

## 21. References and starting links

Core methods:

- IQ-Learn: Inverse soft-Q Learning for Imitation — https://openreview.net/forum?id=Aeo-xqtb5p
- DemoDICE: Offline Imitation Learning with Supplementary Imperfect Demonstrations — https://openreview.net/forum?id=BrPdX1bDZkQ
- SMODICE: Versatile Offline Imitation from Observations and Examples via Regularized State-Occupancy Matching — https://proceedings.mlr.press/v162/ma22a.html
- SPRINQL: Sub-optimal Demonstrations driven Offline Imitation Learning — https://arxiv.org/abs/2402.13147
- No Experts, No Problem: Avoidance Learning from Bad Demonstrations — https://openreview.net/forum?id=MYe8FiahWi
- Learning What to Do and What Not To Do: Offline Imitation from Expert and Undesirable Demonstrations — https://arxiv.org/abs/2505.21182

Offline RL baselines:

- Conservative Q-Learning — https://proceedings.neurips.cc/paper_files/paper/2020/hash/0d2b2061826a5df3221116a5085a6052-Abstract.html
- Implicit Q-Learning — https://arxiv.org/abs/2110.06169
- Should I Run Offline Reinforcement Learning or Behavioral Cloning? — https://openreview.net/forum?id=AP1MKT37rJ

Datasets:

- Minari documentation — https://minari.farama.org/
- Minari D4RL group — https://minari.farama.org/datasets/D4RL/
- D4RL project page — https://sites.google.com/view/d4rl-anonymous/
- Robomimic — https://robomimic.github.io/
- Robomimic dataset documentation — https://github.com/ARISE-Initiative/robomimic/blob/master/docs/datasets/robomimic_v0.1.md
- Safety Gymnasium — https://proceedings.neurips.cc/paper_files/paper/2023/hash/3c557a3d6a48cc99444f85e924c66753-Abstract-Datasets_and_Benchmarks.html
- DSRL / Offline Safe RL datasets — https://hhlin.info/publication/osrl/

---

## 22. Immediate next actions

1. Implement GridWorld and data splits.
2. Implement BC-positive, BC-all, and Weighted BC.
3. Implement Tri-PIQL losses without conservative penalty first.
4. Verify reward heatmap and advantage histograms.
5. Add conservative penalty.
6. Move to one D4RL/Minari locomotion task.
7. Add baselines only after Tri-PIQL beats simple baselines on at least one nontrivial task.
8. Keep a living experiment table with every run, seed, git commit, and config hash.
