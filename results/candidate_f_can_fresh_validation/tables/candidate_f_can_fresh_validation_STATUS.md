# Candidate F Fresh Can-Only Validation Status

**Status: validation gate failed early.** The validation split seeds are
`808/909/1001/1112/1213`; pilot seeds `606/707` are excluded from
claim-bearing validation because they were already used to decide whether
Candidate F should continue.

Setup-complete validation splits: `2/5`.
Ready trained validation splits: `2/5`.
Claim-ready validation splits: `2/5`.

## Frozen Validation Rows

| seed | split_exists | tail_status | below_count | below_fraction | candidate_f_branch | positive_only_nn_ckpt200 | positive_only_nn_success50 | weighted_bc_ckpt200 | weighted_bc_success50 | triage_bc_ckpt200 | triage_bc_success50 | candidate_e_eval50 | candidate_e_success50 | candidate_f_success50 | best_baseline_method | best_baseline_success50 | candidate_f_delta_vs_best50 | candidate_f_no_worse_best50 | claim_use |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 808 | 1 | ready | 0 | 0.000 | candidate_e_gate | 1 | 43/50 | 1 | 25/50 | 1 | 16/50 | 1 | 42/50 | 42/50 | positive_only_nn | 43/50 | -1 | 0 | fresh_validation |
| 909 | 1 | ready | 0 | 0.000 | candidate_e_gate | 1 | 41/50 | 1 | 18/50 | 1 | 22/50 | 1 | 39/50 | 39/50 | positive_only_nn | 41/50 | -2 | 0 | fresh_validation |
| 1001 | 0 | missing_setup |  |  |  | 0 |  | 0 |  | 0 |  | 0 |  |  |  |  |  |  | fresh_validation |
| 1112 | 0 | missing_setup |  |  |  | 0 |  | 0 |  | 0 |  | 0 |  |  |  |  |  |  | fresh_validation |
| 1213 | 0 | missing_setup |  |  |  | 0 |  | 0 |  | 0 |  | 0 |  |  |  |  |  |  | fresh_validation |

## Pilot Rows Excluded From Claims

| seed | claim_use | candidate_f_branch | candidate_f_first20 | positive_first20 | weighted_first20 | triage_first20 | candidate_e_first20 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 606 | pilot_only_excluded | candidate_e_gate | 16/20 | 16/20 | 14/20 |  | 16/20 |
| 707 | pilot_only_excluded | weighted_bc | 15/20 | 15/20 | 15/20 | 10/20 | 13/20 |

## Read

- Claim-ready validation rows: `2/5`.
- Frozen gate failed early: Candidate F is worse than the best completed non-oracle baseline on `2` validation rows, while the 4/5 no-worse gate allows at most `1`.
- Stop Candidate F scaling for a methods-dominance claim and return to the cautious precision/coverage paper framing or a new candidate.
- The pilot rows remain neutral: Candidate F ties positive-only across
  `606/707` at `31/40`, so they are useful context but not validation
  evidence.
- Claim promotion requires the gate in
  `METHOD_FREEZE_CANDIDATE_F_CAN_FRESH.md`.

## Artifacts

- Validation CSV: `results/candidate_f_can_fresh_validation/tables/candidate_f_can_fresh_validation_status.csv`.
- Pilot CSV: `results/candidate_f_can_fresh_validation/tables/candidate_f_can_fresh_pilot_rows.csv`.
- Freeze: `METHOD_FREEZE_CANDIDATE_F_CAN_FRESH.md`.
