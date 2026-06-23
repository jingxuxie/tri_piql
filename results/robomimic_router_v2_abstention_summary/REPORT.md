# Robomimic Router V2 Abstention Summary

This report converts the score-shape feature audit into a stricter hidden-label-free router.
The router assigns a hard-support branch only for clean score shapes and abstains on large ambiguous MG-style pools.

Hidden labels are not used by the router. Purity columns are audit-only fields inherited from the selector diagnostics.

## Rule

- Abstain if calibrated positive mass is at least `800` and the unlabeled count above the labeled-positive minimum is at least `400`.
- Otherwise use `hard_pos_min` if labeled-positive p10 is at least `0.85` and count above labeled-positive minimum is at least `80`.
- Otherwise use `hard_adaptive_masscap`.

## Decisions

| analysis | observed mode | policy 20k | mass | >=pos_min | current branch | router v2 branch | status |
|---|---|---:|---:|---:|---|---|---|
| can_paired_80p80b | hard | 0.900 | 82.4 | 32.7 | hard_adaptive_masscap | hard_adaptive_masscap | assigned |
| can_paired_40p80b | hard | 0.733 | 49.4 | 17.0 | hard_adaptive_masscap | hard_adaptive_masscap | assigned |
| can_paired_20p80b | hard | 0.667 | 34.1 | 6.7 | hard_adaptive_masscap | hard_adaptive_masscap | assigned |
| lift_mg_sparse | hard | 0.667 | 346.9 | 237.3 | hard_pos_min | hard_pos_min | assigned |
| can_mg_sparse | soft | 0.333 | 1947.9 | 1025.7 | soft_weighted | stress_abstain | abstained |
| can_paired_40p80b_shuffle42 | hard_validation | 0.633 | 60.2 | 26.0 | hard_adaptive_masscap | hard_adaptive_masscap | assigned |
| lift_mg_sparse_shuffle42 | hard_validation | 0.600 | 461.7 | 190.7 | hard_pos_min | hard_pos_min | assigned |
| can_mg_sparse_shuffle42 | fragile | 0.100 | 1466.3 | 515.7 | hard_pos_min | stress_abstain | abstained |

## Outcome Audit

| quantity | value |
|---|---:|
| assigned rows | 6 |
| abstained rows | 2 |
| assigned mean 20k success | 0.700 |
| assigned min 20k success | 0.600 |
| abstained mean 20k success | 0.217 |
| abstained max 20k success | 0.333 |
| current-router all-row mean 20k success | 0.579 |
| current-router all-row min 20k success | 0.100 |

## Interpretation

- Router v2 keeps the paper-facing paired Can and Lift rows assigned, including the shuffled validation splits.
- It abstains on both original and shuffled Can MG, where the current router either relies on a modest soft-weighting stress result or flips to a weak hard branch.
- This is a better method-candidate posture than forcing a hard/soft choice on Can MG. The draft can frame the current method as a high-confidence hard-support converter and present Can MG as an abstention/stress diagnostic.
- The remaining research gap is to replace abstention with a validated policy-quality proxy if we want Can MG to become a main result.
