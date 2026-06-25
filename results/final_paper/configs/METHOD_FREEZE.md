# METHOD FREEZE: TRIAGE-BC v0.1

Frozen on: 2026-06-24
Repository HEAD at freeze time: `bafffccf4d551f8d39c0e78e0d9fbc17d54dfe11`

This file freezes the paper-facing method for fresh final-split runs. Existing
results remain development or validation evidence unless explicitly rerun under
this contract.

## Scope

The frozen method is **TRIAGE-BC: Tri-Signal Support Calibration for Offline
Imitation from Success, Failure, and Mixed Logs**.

It is an offline imitation method, not a full inverse-Q robotics method. The
policy learner for Robomimic is official Robomimic BC-RNN-GMM trained on support
chosen or weighted by a tri-signal score model.

No hidden unlabeled labels may be used for score training, branch selection,
threshold selection, checkpoint selection, or policy training. Hidden labels are
audit-only fields for purity, recall, and post-hoc diagnostics.

## Data Interface

Each split contains:

- labeled positives: `split["labeled_positive_ids"]`
- labeled negatives: `split["labeled_negative_ids"]`
- unlabeled mixed demos: `split["unlabeled_ids"]`
- held-out positive eval starts: `split["valid_positive_ids"]`

Development splits may be used for debugging. Existing `shuffle42` splits are
validation splits. Fresh final test split seeds are frozen as `11`, `22`, and
`33`.

Primary final Robomimic policy seed is `0` for each fresh split seed. Extra
policy seeds `1` and `2` are optional robustness extensions, not required for the
primary final matrix.

## Score Model

The score model is the current state-action binary classifier used by
`scripts/prepare_robomimic_official_bc_rnn.py` and
`scripts/analyze_robomimic_selector_scores.py`.

Inputs:

- observation feature mode: `obs`
- action: dataset action at the same timestep
- state-action feature function: `state_action_features` from
  `scripts/run_minari_action_rerank_smoke.py`

Labels:

- transitions from `D+` have label `1`
- transitions from `D-` have label `0`
- unlabeled transitions are not used in score-model training

Frozen score-model hyperparameters:

- classifier steps: `800`
- classifier batch size: `512` for final score diagnostics and final support
  conversion
- hidden dimension: `128`
- depth: `2`
- learning rate: `1e-4`
- classifier seed: `policy_seed + 77`

Classifier output is converted to probability with sigmoid.

## Trajectory Score Aggregation

For each unlabeled demo, compute the mean transition probability:

```text
g(tau) = mean_t sigmoid(c_theta(s_t, a_t))
```

For diagnostics only, also record min, p10, p50, p90, max, and score histograms
for labeled-positive, labeled-negative, and unlabeled demos.

The final method uses mean demo score for branch decisions and support
conversion.

## Positive-Mass Estimate

Let:

```text
mu_pos = mean demo score over labeled positives
mu_neg = mean demo score over labeled negatives
p_u(tau) = clip((g(tau) - mu_neg) / (mu_pos - mu_neg + 1e-8), 0, 1)
m_hat = sum_tau p_u(tau)
```

`m_hat` is the hidden-label-free estimated positive mass in the unlabeled pool.

## Candidate Support Rules

### Adaptive Masscap

This is the default hard-support converter for paired Can-style score shapes.

Parameters:

- `gap_select_max_unlabeled_demos = 80`
- `gap_select_min_unlabeled_demos = 4`
- `gap_select_min_labeled_positive_multiplier = 4.0`
- `adaptive_mass_cap_ratio = 1.25`
- precision fallback count: `ceil(2 * n_labeled_positive)`

Procedure:

1. Sort unlabeled demos by `g(tau)` descending.
2. Compute the effective gap minimum:

   ```text
   gap_min = max(4, ceil(4.0 * n_labeled_positive))
   ```

3. Compute score-gap support with max count `80` and min count `gap_min`.
4. Compute `m_hat`.
5. If `m_hat < gap_min`, use top `ceil(2 * n_labeled_positive)` demos.
6. Else if score-gap support count exceeds `ceil(1.25 * m_hat)`, use top
   `ceil(m_hat)` demos, floored at `gap_min`.
7. Else use the score-gap support.

### Pos-Min Threshold

This is the default hard-support converter for Lift-style score shapes.

Threshold:

```text
q_pos_min = min_tau_in_D+ g(tau)
```

Selected support:

```text
S = {tau in D^u : g(tau) >= q_pos_min}
```

If the selected set is empty, select the single highest-scoring unlabeled demo
and record the fallback.

### Weighted Sampler

This is a baseline and optional soft branch, not the primary router-v2 output.

Train on `D+ union D^u` with demo weights:

```text
w(tau in D+) = 1
w(tau in D^u) = max(0.05, g(tau))
```

The weighted trainer is `scripts/train_robomimic_official_weighted_sampler.py`
with `num_samples_multiplier = 1.0`.

### Positive-Only NN Control

This is a required no-bad-label baseline, not TRIAGE-BC.

Use `positive_plus_positive_nn_top_unlabeled_demos` with top-k set by the split:

- Can 40p/80b: top40
- Lift MG: top160
- other final splits: predeclare top-k in the run config before rollout

## Router V2

Router v2 is the frozen paper-facing branch rule.

Hidden-label-free features:

- `estimated_positive_mass = m_hat`
- `count_ge_pos_min = count(g(tau) >= min g(D+))`
- `labeled_positive_p10 = percentile_10(g(D+))`

Frozen thresholds:

- `stress_mass_floor = 800`
- `stress_pos_min_count_floor = 400`
- `hard_positive_p10 = 0.85`
- `hard_pos_min_count_floor = 80`

Decision:

1. If `estimated_positive_mass >= 800` and `count_ge_pos_min >= 400`, abstain.
   Do not train a main TRIAGE-BC branch for that split. Report score/support
   diagnostics and route the split to the stress/limitation table.
2. Else if `labeled_positive_p10 >= 0.85` and `count_ge_pos_min >= 80`, use
   `hard_pos_min`.
3. Else use `hard_adaptive_masscap`.

The router does not choose weighted BC as a main method branch in v0.1. Weighted
BC remains a required same-backbone baseline and a diagnostic branch for
abstained Can MG-style splits.

## Robomimic Policy Training

Use official Robomimic BC-RNN-GMM with the following frozen config:

- algorithm: `bc`
- observations: low-dimensional `robot0_eef_pos`, `robot0_eef_quat`,
  `robot0_gripper_qpos`, `object`
- sequence length: `10`
- frame stack: `1`
- actor MLP dims: `1024,1024`
- RNN: LSTM
- RNN hidden dim: `400`
- RNN layers: `2`
- GMM enabled: `true`
- GMM modes: `5`
- GMM min std: `0.0001`
- GMM std activation: `softplus`
- low-noise eval: `true`
- policy learning rate: `1e-4`
- L2 loss weight: `1.0`
- train batch size: `100`
- num data workers: `0`
- HDF5 cache mode: `all`
- normalize obs: `false`
- CUDA: `true`
- epoch steps: `100`
- num epochs: `200`
- checkpoints: epochs `50`, `100`, `150`, `200`
- no rollout during training
- no validation checkpoint selection
- no best-checkpoint reporting in main tables

Fixed-budget mapping:

- epoch 50 = 5k optimizer steps
- epoch 100 = 10k optimizer steps
- epoch 150 = 15k optimizer steps
- epoch 200 = 20k optimizer steps

## Final Evaluation Protocol

Use `scripts/evaluate_robomimic_official_policy.py`.

Common settings:

- device: `cuda`
- eval init mode: `valid_positive_states`
- eval episodes: `50`
- checkpoint list: epochs `50`, `100`, `150`, `200` for final curves
- final main endpoint: epoch `200`
- same split `valid_positive_ids` and same rollout seed across all methods on
  the same split

Task horizons:

- Can paired and Can MG: `400`
- Lift MG: `150`
- Square policy smokes, if repeated: `500`

Report:

- fixed 10k, 15k, 20k success
- 5k in appendix curves
- per-episode CSV
- per-initial-state CSV
- seed/split mean and standard deviation
- bootstrap confidence interval when enough split/initial-state units exist

Do not use oracle-best checkpoints as main results unless a checkpoint rule is
separately frozen before evaluation.

## Final Split Contract

Fresh final test split seeds:

- `11`
- `22`
- `33`

Primary final Can paired splits:

- balanced: 10 labeled positives, 10 labeled negatives, 80 hidden-positive
  unlabeled, 80 hidden-bad unlabeled
- intermediate: 10 labeled positives, 10 labeled negatives, 40 hidden-positive
  unlabeled, 80 hidden-bad unlabeled
- heavy contamination: 10 labeled positives, 10 labeled negatives,
  20 hidden-positive unlabeled, 80 hidden-bad unlabeled

Primary final Lift MG split:

- 10 labeled positives
- 10 labeled negatives
- remaining train demos as unlabeled, with hidden labels used only for audit

## Required Baselines For Main Tables

For any split promoted to a main table, run the same backbone and fixed budget
for:

- BC-positive only
- BC-all / mixed-log cloning
- classifier-probability weighted BC
- positive-only NN support
- TRIAGE-BC router-v2 output, unless router abstains
- all train positives / oracle support, diagnostic only

For Can paired also include fixed top20 and fixed top80 support controls in the
appendix or main support-conversion table.

## Reproducibility Artifacts

For every final run, save:

- config JSON/YAML
- split path and split seed
- policy seed
- classifier seed
- selected demo IDs or demo weights
- score CSV
- support audit CSV
- hidden-label audit CSV, audit only
- training log
- checkpoint paths
- rollout metrics CSV
- per-episode CSV
- per-initial-state CSV
- report Markdown

Final paper artifacts should live under:

```text
results/final_paper/
  configs/
  tables/
  figures/
  per_seed/
  per_initial_state/
  support_audits/
  score_diagnostics/
  ablations/
```

## Change Control

After this freeze, changes to score model, branch thresholds, policy config,
checkpoint schedule, or final evaluation protocol must be logged as a new method
variant or ablation. They must not replace TRIAGE-BC v0.1 in final test claims.
