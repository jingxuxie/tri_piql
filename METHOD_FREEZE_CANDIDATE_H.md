# METHOD FREEZE: Candidate H Task-Aware Tail Router

Frozen for the next validation attempt on: 2026-06-26

This is a **development freeze**, not a paper-method claim. Candidate H was
created after Candidate G failed a fresh Can 707 endpoint smoke, so any future
endpoint matrix using this rule must be presented as a new validation attempt.

## Scope

Candidate H is a hidden-label-free router over existing Robomimic BC-RNN-GMM
branches:

1. clean positive anchor,
2. triage/hard-support policy,
3. classifier-probability weighted BC.

Hidden unlabeled labels are forbidden for score training, branch selection,
checkpoint selection, or policy training. Hidden labels are audit-only.

## Fixed Parameters

```text
tail_threshold = 0.5 * unlabeled_prob_mean
mild_tail_fraction_max = 0.03
mild comparison = below_fraction < mild_tail_fraction_max
severe comparison = below_fraction >= mild_tail_fraction_max
```

For each split, build the positive-NN selected unlabeled support set and compute:

```text
below_count = count(p_selected < tail_threshold)
below_fraction = below_count / len(selected_support)
```

## Router Rule

### Can 40p/80b

```text
if below_fraction >= 0.03:
    use weighted_bc
else:
    use candidate_e_gate
```

The Can clean anchor is Candidate E:

```text
if initial positive-anchor action distance to labeled positive support > 3.0:
    execute weighted_bc for the episode
else:
    execute positive_only_nn for the episode
```

### Lift MG

```text
if below_count == 0:
    use positive_only_nn
elif below_fraction < 0.03:
    use triage_hard_support
else:
    use weighted_bc
```

## Why Candidate G Was Replaced

Candidate G used task-agnostic mild-tail triage. On fresh Can 707, that selected
triage on a mild tail (`1/40 = 0.025`) even though the hidden-label support audit
was worse than positive-only:

- positive-only support: `32` hidden positives, `8` hidden bad;
- triage support: `29` hidden positives, `18` hidden bad.

The bounded endpoint smoke confirmed the risk:

- Candidate G triage: `10/20`;
- positive-only clean-anchor lower bound: `15/20`.

## Discovery Evidence

Candidate H is identical to Candidate G on the completed Can+Lift rows:

- Can 40p/80b: `198/250` versus completed per-split baseline oracle `192/250`;
- Lift MG: `154/250` versus completed per-split baseline oracle `154/250`;
- combined: `352/500` versus completed per-split baseline oracle `346/500`.

Fresh support preflight on seeds `606` and `707` chooses:

- Can 606: Candidate E gate;
- Can 707: Candidate E gate;
- Lift 606: triage/hard support;
- Lift 707: triage/hard support.

## Next Validation

Run a fresh or clearly held-out validation matrix with this exact rule before
making any Candidate H claim. At minimum, the next endpoint check should cover:

- Can 707 Candidate E gate, because positive-only is only a lower bound for the
  branch;
- Lift 606 or 707 triage versus positive-only/weighted, because Lift is where
  mild-tail triage is retained.

## Artifacts

- `results/candidate_g_fresh_preflight/candidate_h_task_aware_tail_REPORT.md`
- `results/candidate_g_fresh_preflight/candidate_h_task_aware_tail_fresh_preflight.csv`
- `scripts/summarize_candidate_h_task_aware_tail_router.py`
