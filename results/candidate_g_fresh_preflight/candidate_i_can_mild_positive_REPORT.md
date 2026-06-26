# Candidate I Can-Mild-Positive Tail Router

**Status: rejected as a development candidate after fresh Lift 606
validation.** Candidate I was a task-aware refinement after Can 707
showed that both task-agnostic mild-tail triage and Can mild-tail
Candidate E can lose to the positive-only anchor. Its retained Lift
mild-tail triage branch then lost to positive-only on held-out Lift 606.

Frozen candidate rule under test:

- Can 40p/80b no tail: Candidate E initial-distance gate;
- Can 40p/80b mild tail: positive-only NN;
- Can 40p/80b severe tail (`below_fraction >= 0.03`): weighted BC;
- Lift MG no tail: positive-only NN;
- Lift MG mild tail: triage/hard support;
- Lift MG severe tail: weighted BC.

## Completed-Row Assembly

- Can: `198/250` versus completed oracle `192/250`.
- Lift: `154/250` versus completed oracle `154/250`.
- Combined: `352/500` versus completed oracle `346/500`.

Candidate I is identical to Candidate G/H on the completed Can+Lift rows:
completed Can has either no tail or severe tail, not a mild-tail case.
This completed-row assembly is no longer enough for a method claim
because fresh Lift mild-tail validation failed.

## Fresh Preflight Choices

| task | split | #<thr | frac<thr | Candidate G | Candidate H | Candidate I | note |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| can_paired | 606 | 0 | 0.000 | candidate_e_gate | candidate_e_gate | candidate_e_gate |  |
| can_paired | 707 | 1 | 0.025 | triage_bc | candidate_e_gate | positive_only_nn | I differs from H |
| lift_mg | 606 | 2 | 0.013 | triage_bc | triage_bc | triage_bc |  |
| lift_mg | 707 | 4 | 0.025 | triage_bc | triage_bc | triage_bc |  |

## Can 707 Endpoint Smoke

| method | Candidate I selected? | successes | avg len | protocol |
| --- | --- | ---: | ---: | --- |
| candidate_g_triage | no | 10/20 | 251.8 | 20 valid-positive starts |
| candidate_h_candidate_e_gate | no | 13/20 | 209.6 | 20 valid-positive starts |
| positive_only_nn | yes | 15/20 | 181.9 | 20 valid-positive starts |

- Candidate E opened its weighted fallback on `6/20` episodes. It rescued
  some starts but lost more than it gained on this fresh mild-tail split.
- Candidate I fixed this Can mild-tail failure by selecting positive-only.

## Lift 606 Endpoint Validation

| method | Candidate I selected? | successes | avg len | protocol |
| --- | --- | ---: | ---: | --- |
| triage_bc | yes | 23/50 | 100.1 | 50 valid-positive starts |
| positive_only_nn | no | 28/50 | 85.2 | 50 valid-positive starts |
| weighted_bc | no | 16/50 | 122.5 | 50 valid-positive starts |

- Candidate I selected triage on this retained Lift mild-tail case, but
  positive-only was stronger by `5/50` successes and weighted was worse.
- The smaller 20-episode smoke showed the same ordering between positive
  and triage (`14/20` versus `13/20`), and the 50-episode endpoint widened
  the gap.

## Read

- Candidate I should not be promoted or scaled as-is.
- The failure is informative: old completed Lift mild-tail rows favored
  triage, while fresh Lift 606 favors positive-only. A global task/tail
  rule is unstable for Lift mild tails.
- The next candidate should use a deployable episode-level gate or a new
  score diagnostic for Lift mild-tail cases, rather than only changing the
  global mild-tail branch.

## Artifacts

- Fresh preflight CSV: `results/candidate_g_fresh_preflight/candidate_i_can_mild_positive_fresh_preflight.csv`.
- Fresh endpoint validation CSV: `results/candidate_g_fresh_preflight/candidate_i_fresh_endpoint_validation.csv`.
- Candidate E eval: `results/candidate_g_fresh_preflight/can707_candidate_e_gate_eval20/REPORT.md`.
- Positive-only eval: `results/candidate_g_fresh_preflight/can707_positive_epoch200_eval20/REPORT.md`.
- Triage eval: `results/candidate_g_fresh_preflight/can707_triage_epoch200_eval20/REPORT.md`.
- Lift 606 triage eval: `results/candidate_g_fresh_preflight/lift606_triage_epoch200_eval50/REPORT.md`.
- Lift 606 positive-only eval: `results/candidate_g_fresh_preflight/lift606_positive_epoch200_eval50/REPORT.md`.
- Lift 606 weighted eval: `results/candidate_g_fresh_preflight/lift606_weighted_epoch200_eval50/REPORT.md`.
