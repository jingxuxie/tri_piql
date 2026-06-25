# METHOD FREEZE: TRIAGE-BC v0.2 Development Portfolio Router

Frozen for fresh-split validation on: 2026-06-25

This is a **development freeze**, not a final paper-method claim. It
predeclares the next v0.2 candidate to test on fresh splits after the Can 40
union endpoint gate. If the rule is changed after fresh-split results, the
changed rule becomes a new v0.2 variant and must not be mixed with this freeze.

## Scope

TRIAGE-BC v0.2 is a hidden-label-free portfolio router over three branches:

1. hard positive-NN/risk-union support,
2. soft classifier-probability weighted BC,
3. stress abstention for large ambiguous MG-style pools.

The method remains an offline imitation pipeline with official Robomimic
BC-RNN-GMM as the policy learner. Hidden unlabeled labels are forbidden for
score training, branch selection, candidate selection, checkpoint selection, or
policy training. Hidden labels are audit-only.

## Inputs

Each split contains:

- labeled positives: `split["labeled_positive_ids"]`
- labeled negatives: `split["labeled_negative_ids"]`
- unlabeled mixed demos: `split["unlabeled_ids"]`
- held-out positive eval starts: `split["valid_positive_ids"]`

Development split seeds `11`, `22`, and `33` were used to design this freeze.
Fresh validation split seeds for this v0.2 candidate are `101`, `202`, and
`303` for Can 40p/80b and Lift MG.

## Score Model

Use the v0.1 state-action binary classifier:

- positive transitions label: `1`
- negative transitions label: `0`
- unlabeled transitions: unused in score training
- classifier steps: `800`
- classifier batch size: `512`
- hidden dimension: `128`
- depth: `2`
- learning rate: `1e-4`
- classifier seed: `policy_seed + 77`
- trajectory score: mean sigmoid probability over transitions

Compute:

```text
mu_pos = mean trajectory score over labeled positives
mu_neg = mean trajectory score over labeled negatives
p_u(tau) = clip((g(tau) - mu_neg) / (mu_pos - mu_neg + 1e-8), 0, 1)
estimated_positive_mass = sum_tau p_u(tau)
count_ge_pos_min = count_tau(g(tau) >= min_{tau+ in D+} g(tau+))
```

## Router Rule

The v0.2 router uses only `estimated_positive_mass` and `count_ge_pos_min`.

1. If `estimated_positive_mass >= 800` and `count_ge_pos_min >= 400`, use
   `stress_abstain`.
2. Else if `estimated_positive_mass >= 200` and `count_ge_pos_min >= 80`, use
   `soft_weighted`.
3. Else use `hard_risk_union`.

Rationale from development artifacts:

- Can 40p/80b has low mass/count and benefits from hard union support.
- Lift MG has moderate broad mass/count and the weighted branch is the strongest
  endpoint row.
- Can MG has very large mass/count and remains a stress/abstention setting.

## Branch Definitions

### hard_risk_union

Construct two candidate sets over unlabeled demos:

1. `positive_nn_topK`: nearest-neighbor retrieval from labeled-positive
   state-action trajectories.
2. `positive_nn_risk_fusion_topK`: rank fusion of positive-NN rank and
   combined action-risk rank with equal weights.

The selected unlabeled support is:

```text
S_union = ordered_union(positive_nn_topK, positive_nn_risk_fusion_topK)
```

Top-k is task/split predeclared:

- Can 40p/80b: `K = 40`
- Can 20p/80b diagnostic, if run: `K = 20`
- Can 80p/80b diagnostic, if run: `K = 80`
- Lift MG fallback, if the router ever selects hard union: `K = 160`

`positive_nn_risk_fusion_topK` uses the risk features implemented in
`scripts/summarize_v02_action_risk_candidate_audit.py`:

```text
combined_risk = action_conflict_risk + bad_neighbor_risk
fusion_score = 0.5 * normalized_positive_nn_rank_score
             + 0.5 * normalized_combined_risk_rank_score
```

Policy training data is `D+ union S_union`.

### soft_weighted

Train on `D+ union D^u` with demo weights:

```text
w(tau in D+) = 1
w(tau in D^u) = max(0.05, g(tau))
```

Use `scripts/train_robomimic_official_weighted_sampler.py` and the same
official Robomimic BC-RNN-GMM policy config as v0.1.

### stress_abstain

Do not train or report a main TRIAGE-BC v0.2 endpoint row. Save score-shape,
support, and router diagnostics, and report the split as an abstention/stress
case. Weighted BC may still be trained as a baseline, but not as the v0.2
method row for an abstained split.

## Fresh-Split Gate

Run fresh split seeds:

- Can 40p/80b: `101`, `202`, `303`
- Lift MG: `101`, `202`, `303`
- Can MG: score/router diagnostics only unless the frozen rule does not abstain

Primary policy seed: `0`.

Endpoint budget:

- official Robomimic BC-RNN-GMM
- 200 epochs
- 100 epoch steps
- checkpoint: `model_epoch_200.pth`
- 50 valid-positive-start rollouts per split
- Can horizon: `400`
- Lift horizon: `150`
- device: `cuda`
- use `XLA_PYTHON_CLIENT_PREALLOCATE=false` for JAX score/setup work

Required baselines on fresh primary splits:

- v0.2 selected branch
- strongest relevant pre-v0.2 baseline:
  - Can 40p/80b: positive-only NN top40 and weighted BC
  - Lift MG: weighted BC and positive-only NN top160
- v0.1 TRIAGE-BC router-v2 branch
- all-demo BC if budget allows
- all-positive oracle diagnostic if budget allows

## Success Gate

This v0.2 candidate clears the development-to-paper gate only if:

- it is best or tied-best non-oracle on Can 40p/80b fresh splits,
- it matches or beats weighted BC on Lift MG fresh splits,
- Can MG is correctly abstained or a non-abstained branch is justified by the
  frozen rule,
- the result remains honest when split-level and paired-initial uncertainty are
  reported.

Development artifacts motivating this freeze:

- `results/final_paper/tables/v02_portfolio_router_REPORT.md`
- `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`
- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/REPORT.md`
- `results/final_paper/tables/v02_union_candidate_support_REPORT.md`
