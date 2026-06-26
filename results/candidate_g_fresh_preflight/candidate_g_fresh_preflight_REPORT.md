# Candidate G Fresh-Split Preflight

This report applies the frozen Candidate G branch rule to prepared split
artifacts only. It does not use endpoint outcomes.

| task | split | min/mean | #<thr | frac<thr | choice | support hp/bad | purity |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| can_paired | 606 | 0.635 | 0 | 0.000 | candidate_e_gate | 31/9 | 0.775 |
| can_paired | 707 | 0.125 | 1 | 0.025 | triage_bc | 29/18 | 0.617 |
| lift_mg | 606 | 0.215 | 2 | 0.013 | triage_bc | 144/32 | 0.818 |
| lift_mg | 707 | 0.215 | 4 | 0.025 | triage_bc | 149/23 | 0.866 |

## Read

- `can_paired` choices: `{'candidate_e_gate': 1, 'triage_bc': 1}`.
- `lift_mg` choices: `{'triage_bc': 2}`.
- This preflight only says which frozen branch would be evaluated on
  unseen split seeds and what hidden-label support audit that branch has.
- Endpoint rollouts are still required before Candidate G can support a
  methods claim.

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_g_fresh_preflight_summary.csv`.
