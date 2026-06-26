# METHOD FREEZE: Candidate G Tail-Severity Router

Frozen for the next validation attempt on: 2026-06-26

This is a **development freeze**, not a paper-method claim. Candidate G was
designed after inspecting completed Can 40p/80b and Lift MG endpoint rows. Any
future endpoint run using this rule must be reported as a new frozen validation
attempt, not mixed into the discovery evidence.

## Scope

Candidate G is a hidden-label-free router over existing Robomimic BC-RNN-GMM
branches:

1. clean positive anchor,
2. triage/hard-support policy,
3. classifier-probability weighted BC.

The router uses support statistics from the positive-NN selected unlabeled set.
Hidden unlabeled labels are forbidden for score training, branch selection,
checkpoint selection, or policy training. Hidden labels are audit-only.

## Fixed Parameters

```text
tail_threshold = 0.5 * unlabeled_prob_mean
mild_tail_fraction_max = 0.03
mild comparison = below_fraction < mild_tail_fraction_max
```

These parameters are now frozen for the next validation attempt. The `0.03`
mild-tail cutoff is the main risk: it was selected after the completed Lift
audit and therefore cannot support a standalone paper claim without fresh
validation.

## Router Rule

For each split:

1. Train the same labeled positive/negative state-action classifier used by the
   v0.1/v0.2 support pipeline.
2. Build the positive-NN selected unlabeled support set with the existing task
   support size:
   - Can 40p/80b: `K = 40`
   - Lift MG: `K = 160`
3. Look up classifier probabilities for demos in that selected support set.
4. Compute:

```text
below_count = count(p_selected < 0.5 * unlabeled_prob_mean)
below_fraction = below_count / len(selected_support)
```

5. Select the branch:

```text
if below_count == 0:
    use clean_positive_anchor
elif below_fraction < 0.03:
    use triage_hard_support
else:
    use weighted_bc
```

## Branch Definitions

### clean_positive_anchor

For Can 40p/80b, use Candidate E:

```text
if initial positive-anchor action distance to labeled positive support > 3.0:
    execute weighted_bc for the episode
else:
    execute positive_only_nn for the episode
```

For Lift MG, use the positive-only NN policy directly. Candidate E's initial
distance gate is not promoted to Lift by this freeze.

### triage_hard_support

Use the existing v0.1 TRIAGE-BC hard-support branch for the task/split.

### weighted_bc

Use the existing classifier-probability weighted BC branch with demo weights

```text
w(tau in D+) = 1
w(tau in D^u) = max(0.05, g(tau))
```

and official Robomimic BC-RNN-GMM training.

## Discovery Evidence

The retrospective completed-row assembly is:

- Can 40p/80b: `198/250` versus completed per-split baseline oracle `192/250`.
- Lift MG: `154/250` versus completed per-split baseline oracle `154/250`.
- Combined: `352/500` versus completed per-split baseline oracle `346/500`.

Sensitivity to `mild_tail_fraction_max` is not broad:

- `0.000`: `343/500`
- `0.020` or `0.025`: `348/500`
- `0.026` through strict `0.050`: `352/500`
- `0.051` or `0.060`: `342/500`

## Next Validation

Before claiming Candidate G, run a fresh validation matrix or a clearly marked
held-out split extension with this exact rule:

- Can 40p/80b: at least five split seeds not used to choose this freeze, if
  available.
- Lift MG: at least five split seeds not used to choose this freeze, if
  available.
- Primary policy seed: `0`.
- Endpoint budget: `50` valid-positive-start rollouts per split.
- Checkpoint: `model_epoch_200.pth`.

If only the already completed split seeds are reported, Candidate G must be
framed as a discovery candidate and not as validated transfer.

## Artifacts

- `results/candidate_breakthrough/candidate_g_tail_severity_router_REPORT.md`
- `results/candidate_breakthrough/candidate_g_tail_severity_router_summary.csv`
- `results/candidate_breakthrough/candidate_g_tail_severity_router_sensitivity.csv`
- `scripts/summarize_candidate_g_tail_severity_router.py`
