# Candidate E Multi-Split First-20 Screen

Candidate E uses positive-only by default and switches to weighted BC for
the full episode when the positive-only initial action has labeled
positive-support distance greater than `3.0`.

This regenerated report prefers isolated-RNG router outputs when present,
so non-selected stochastic policies do not perturb selected-policy samples.

Baseline entries are first-20 slices from existing 50-episode official
baseline eval CSVs. Candidate E entries are fresh 20-episode router evals.

| split | positive | weighted | triage | cand E | delta vs best | gate opens | weighted steps | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | 7/20 | 12/20 | 11/20 | 7/20 | -5 | 2 | 800 | weighted last.pth |
| 202 | 17/20 | 13/20 | 12/20 | 17/20 | +0 | 0 | 0 | epoch200 |
| 303 | 15/20 | 10/20 | 13/20 | 15/20 | +0 | 0 | 0 | epoch200 |
| 404 | 17/20 | 13/20 | 14/20 | 19/20 | +2 | 2 | 257 | epoch200 |
| 505 | 15/20 | 12/20 | 14/20 | 16/20 | +1 | 6 | 1298 | epoch200 |
| total | 71/100 | 60/100 | 64/100 | 74/100 | -2 | 10 | 2355 | split101 weighted uses last.pth |

## Read

- Isolated-RNG evaluation strengthens Candidate E on split 404
  (`19/20` first-20, `46/50` in the 50-episode follow-up).
- Candidate E matches or beats the best first-20 baseline on splits 202,
  303, 404, and 505, but remains badly below the weighted baseline on
  split 101.
- In aggregate Candidate E reaches `74/100`, beating every single
  aggregate baseline but below the per-split baseline oracle (`76/100`).
- On splits 202 and 303 the gate never opens, so Candidate E reduces to
  the positive-only anchor. On split 101 the same threshold opens on two
  long weighted episodes without rescue, while the split would prefer
  broader weighted behavior overall.
- The next version should calibrate the initial-distance threshold from
  training-only support statistics or add a second confidence feature;
  do not promote the hand-set threshold unchanged.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_e_multisplit_screen_first20_summary.csv`.
- Router eval dirs:
  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split101_eval20_isolated_rng`,
  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split202_eval20_isolated_rng`,
  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split303_eval20_isolated_rng`,
  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval20_isolated_rng`,
  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split505_eval20_isolated_rng`.
