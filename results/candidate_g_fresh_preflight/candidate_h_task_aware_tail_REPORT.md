# Candidate H Task-Aware Tail Router

Candidate H is a response to the first fresh Candidate G endpoint smoke.
It keeps Candidate G's Lift interpretation but changes Can mild-tail
handling:

- Can 40p/80b: no or mild low tail uses Candidate E's clean anchor;
- Can 40p/80b: severe low tail (`below_fraction >= 0.03`) uses weighted BC;
- Lift MG: no tail uses positive-only, mild tail uses triage, severe tail
  uses weighted BC.

This is a discovery candidate, not a paper claim, because it was proposed
after seeing the fresh Can 707 smoke.

## Completed-Row Assembly

- Can: `198/250` versus completed oracle `192/250`.
- Lift: `154/250` versus completed oracle `154/250`.
- Combined: `352/500` versus completed oracle `346/500`.

Candidate H is identical to Candidate G on the completed Can+Lift rows,
because the completed Can rows had no mild-tail case.

## Fresh Support Preflight

| task | split | #<thr | frac<thr | Candidate G | Candidate H | note |
| --- | ---: | ---: | ---: | --- | --- | --- |
| can_paired | 606 | 0 | 0.000 | candidate_e_gate | candidate_e_gate |  |
| can_paired | 707 | 1 | 0.025 | triage_bc | candidate_e_gate | H differs from G |
| lift_mg | 606 | 2 | 0.013 | triage_bc | triage_bc |  |
| lift_mg | 707 | 4 | 0.025 | triage_bc | triage_bc |  |

## Can 707 Endpoint Smoke

- Candidate G selected triage: `10/20`
  success, avg length `251.8`.
- Clean positive anchor lower bound, positive-only: `15/20`
  success, avg length `181.9`.
- This single fresh split argues against task-agnostic mild-tail triage on
  Can; the next validation should freeze Candidate H before any broader
  endpoint matrix.

## Artifacts

- Fresh preflight CSV: `results/candidate_g_fresh_preflight/candidate_h_task_aware_tail_fresh_preflight.csv`.
- Candidate G triage eval: `results/candidate_g_fresh_preflight/can707_triage_epoch200_eval20/REPORT.md`.
- Positive-only eval: `results/candidate_g_fresh_preflight/can707_positive_epoch200_eval20/REPORT.md`.
