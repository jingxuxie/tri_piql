# v0.2 Fresh Baseline Coverage Audit

This audit separates rows required for the frozen v0.2 branch-selection claim from optional diagnostic controls.
It is evidence accounting only; it does not introduce new endpoint data.

## Summary

- Required branch-selection rows complete: `7/7`.
- Optional diagnostic rows run in the fresh five-split gate: `0/4`.
- The current v0.2 fresh-gate claim is a branch-selection comparison over selected, positive-only, weighted, and v0.1 fixed branches.
- Fresh all-demo and all-positive rows would be useful diagnostic controls, but they are not required for the current validated branch-selection claim and should not be implied as completed fresh-gate evidence.

## Row Coverage

| setting_label | row_label | requirement | status | completed_splits | missing_splits | successes | episodes | success_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | v0.2 selected hard union | required_branch_selection | complete | 101/202/303/404/505 |  | 197 | 250 | 0.788 |
| Can 40p/80b | positive-only NN | required_branch_selection | complete | 101/202/303/404/505 |  | 174 | 250 | 0.696 |
| Can 40p/80b | weighted BC | required_branch_selection | complete | 101/202/303/404/505 |  | 158 | 250 | 0.632 |
| Can 40p/80b | v0.1 TRIAGE-BC | required_branch_selection | complete | 101/202/303/404/505 |  | 171 | 250 | 0.684 |
| Can 40p/80b | all-demo BC | optional_diagnostic | optional_not_run |  | 101/202/303/404/505 |  |  |  |
| Can 40p/80b | all-positive oracle | optional_diagnostic | optional_not_run |  | 101/202/303/404/505 |  |  |  |
| Lift MG | v0.2 selected weighted BC | required_branch_selection | complete | 101/202/303/404/505 |  | 143 | 250 | 0.572 |
| Lift MG | positive-only NN | required_branch_selection | complete | 101/202/303/404/505 |  | 125 | 250 | 0.500 |
| Lift MG | v0.1 TRIAGE-BC | required_branch_selection | complete | 101/202/303/404/505 |  | 143 | 250 | 0.572 |
| Lift MG | all-demo BC | optional_diagnostic | optional_not_run |  | 101/202/303/404/505 |  |  |  |
| Lift MG | all-positive oracle | optional_diagnostic | optional_not_run |  | 101/202/303/404/505 |  |  |  |

## Interpretation

- A3 now closes the required v0.1 fixed-branch objection for the fresh five-split Can/Lift gate.
- The paper should describe the fresh gate as a complete selected-vs-strong-baseline/v0.1 audit, not as a full SOTA leaderboard with all possible diagnostic controls.
- If more GPU budget is spent, the highest-value optional fresh rows are all-demo and all-positive oracle controls, clearly labeled as diagnostics.
