# METHOD FREEZE: Candidate I Can-Mild-Positive Tail Router

Status as of 2026-06-26: **rejected as a development candidate**. The freeze
below remains as the exact rule that was tested, but it should not be promoted
or scaled as a paper method.

Frozen for the next validation attempt on: 2026-06-26

This is a **development freeze**, not a paper-method claim. Candidate I was
created after a fresh Can 707 endpoint smoke showed that Candidate G and
Candidate H both route mild Can tails away from a stronger positive-only anchor.
It subsequently failed the retained Lift mild-tail validation on Lift 606.

## Scope

Candidate I is a hidden-label-free router over existing Robomimic BC-RNN-GMM
branches:

1. Candidate E clean anchor on no-tail Can splits,
2. positive-only NN on mild-tail Can splits,
3. weighted BC on severe-tail Can splits,
4. positive-only / triage / weighted routing on Lift by tail severity.

Hidden unlabeled labels are forbidden for score training, branch selection,
checkpoint selection, or policy training. Hidden labels are audit-only.

## Fixed Parameters

```text
tail_threshold = 0.5 * unlabeled_prob_mean
mild_tail_fraction_max = 0.03
mild comparison = 0 < below_fraction < mild_tail_fraction_max
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
if below_count == 0:
    use candidate_e_gate
elif below_fraction < 0.03:
    use positive_only_nn
else:
    use weighted_bc
```

Candidate E gate:

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

## Why Candidate H Was Replaced

Candidate H used Candidate E on Can mild-tail cases. On fresh Can 707, Candidate
E opened the weighted fallback on `6/20` episodes and scored `13/20`, below the
positive-only anchor at `15/20`.

The same split also rejected Candidate G's task-agnostic mild-tail triage:

- Candidate G triage: `10/20`;
- Candidate H Candidate E gate: `13/20`;
- Candidate I positive-only: `15/20`.

## Why Candidate I Was Rejected

Candidate I retained triage/hard support for Lift mild-tail splits. On fresh
Lift 606, the matched epoch-200 endpoint comparison showed:

- Candidate I selected triage: `23/50`;
- positive-only NN: `28/50`;
- weighted BC: `16/50`.

The smaller 20-episode smoke already had the same ordering between positive-only
and triage (`14/20` versus `13/20`). The broader 50-episode check makes the
retained Lift branch a validation failure.

## Discovery Evidence

Candidate I is identical to Candidate G/H on the completed Can+Lift rows:

- Can 40p/80b: `198/250` versus completed per-split baseline oracle `192/250`;
- Lift MG: `154/250` versus completed per-split baseline oracle `154/250`;
- combined: `352/500` versus completed per-split baseline oracle `346/500`.

Fresh support preflight on seeds `606` and `707` chooses:

- Can 606: Candidate E gate;
- Can 707: positive-only NN;
- Lift 606: triage/hard support;
- Lift 707: triage/hard support.

## Next Direction

Do not run a larger Candidate I matrix as-is. The old completed Lift mild-tail
rows favored triage, while fresh Lift 606 favors positive-only, so a global
task/tail rule is unstable for Lift mild tails. The next candidate should use a
deployable episode-level gate or a new score diagnostic for Lift mild-tail
cases.

## Artifacts

- `results/candidate_g_fresh_preflight/candidate_i_can_mild_positive_REPORT.md`
- `results/candidate_g_fresh_preflight/candidate_i_can_mild_positive_fresh_preflight.csv`
- `results/candidate_g_fresh_preflight/candidate_i_fresh_endpoint_validation.csv`
- `scripts/summarize_candidate_i_can_mild_positive_router.py`
