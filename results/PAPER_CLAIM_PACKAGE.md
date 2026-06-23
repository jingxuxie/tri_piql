# Tri-Signal Offline IRL Claim Package

Status: current evidence package as of 2026-06-23.

This package consolidates the results that are defensible for a paper draft and separates them from diagnostics that should stay out of the main claims.

## Short Answer On The Baseline

Weighted BC should not be treated as weak. Once implemented with the official Robomimic BC-RNN-GMM backbone and classifier-probability sampling, it is a strong baseline:

- Can 40 positive / 80 bad split: weighted BC has the best 10k mean success (`0.600`) and is close at 15k (`0.700`), but drops below mass-capped hard support at 20k (`0.567` versus `0.733`).
- Lift MG: weighted BC is much stronger than all-demo cloning (`0.533` versus `0.200` at 20k), but hard `pos_min` support is better at the fixed 20k endpoint (`0.667`).
- Can MG sparse: matched controls now favor weighted BC at fixed 20k (`0.333`) over all-positive support (`0.200`), pos-p10 hard support (`0.167`), and all-demo cloning (`0.100`), but the absolute success is still modest enough to keep this as a stress diagnostic.

The Can 40p/80b checkpoint-selection diagnostic also rules out a simple "weighted only needed a better checkpoint" explanation: weighted BC oracle-best is `0.700`, while masscap oracle-best is `0.767`. A seed-0 50k-budget check adds that weighted BC does not simply need longer optimization: it peaks at 10k (`0.700`) and is lower at 20k/30k/40k/50k (`0.500`/`0.300`/`0.500`/`0.300`). A three-seed 50-episode endpoint check keeps masscap ahead at fixed 20k on every seed, with mean success `0.680` versus `0.573`, but also shows the endpoint gap is modest and the 10-episode estimates were noisy. The supported claim is therefore not "weighted BC is bad" or "hard filtering always wins." The supported claim is: scarce positive and bad labels learn a useful desirability score, and the conversion of that score into training data should adapt between hard support and soft weighting depending on coverage and contamination.

## Proposed Paper Frame

Working title:

> Tri-Signal Imitation from Scarce Success, Failure, and Mixed Offline Logs

Current paper-facing thesis:

> When successful demonstrations are scarce and offline logs are heavily contaminated, explicit negative demonstrations can calibrate a desirability score over unlabeled behavior. That score can recover useful hidden-positive support or soft sampling weights, improving over naive mixed-log cloning. The key algorithmic issue is the precision/coverage conversion from scores to policy training data.

This is a narrower but much better-supported story than the original full Tri-PIQL claim. The strongest robotics evidence currently supports tri-signal score-calibrated imitation with a competent sequence BC backbone, not a complete inverse-Q method that uniformly beats weighted BC across tasks.

## Main Supported Claims

| Claim | Status | Evidence | Caveat |
|---|---|---|---|
| Contaminated unlabeled logs hurt naive BC. | supported | Continuous PointNav all-data BC degrades from `0.460` to `0.153` success as bad fraction rises from 50% to 95%; Robomimic Lift MG all-demo reaches only `0.200` at 20k; Can MG all-demo reaches `0.100`. | Needs strong BC backbone for robotics interpretation. |
| Scarce positive and bad labels can recover useful hidden-positive support. | supported | Continuous PointNav score-gap demo BC gets `1.000` success at 50/75/90/95% bad; Robomimic Can balanced support has `0.962` aggregate purity and `0.900` 20k success. | In robotics this is currently a selector/backbone result, not the full inverse-Q objective. |
| The selector must trade off purity and coverage. | supported | Balanced Can uses coverage-gap; 20p/80b stress uses top20 precision; 40p/80b uses mass-capped coverage for best 15k/20k mean. | A single fixed top-k or single threshold is not enough. |
| Hard selected support can beat soft weighted BC at fixed later checkpoints. | supported on paired Can and Lift | Can 40p/80b: masscap `0.733` versus weighted `0.567` at 20k. Lift MG: pos-min `0.667` versus weighted `0.533` at 20k. | Weighted BC is competitive and sometimes better earlier. |
| Soft weighted BC can be better when broad coverage matters. | supported diagnostic on Can MG | Can MG sparse has a large high-score plateau; weighted BC beats matched all-positive, all-demo, and pos-p10 controls at fixed 20k (`0.333` versus `0.200`, `0.100`, and `0.167`). | Stress diagnostic only: absolute success is modest and the hard/soft converter is not final. |
| Bad labels are strictly necessary. | not supported | Positive-only NN top40 is strong on Can 40p/80b and ties masscap on best-per-seed mean. Lift positive-only NN top160 is viable but remains below bad-aware `pos_min` at fixed 15k/20k and oracle-by-seed mean. | Better claim: bad labels improve fixed-budget stability and calibration, and can improve coverage-quality tradeoffs on harder mixed-quality pools. |
| Current full Tri-PIQL/IQL actor extraction beats all baselines on real continuous-control tasks. | not supported | Minari PointMaze/Kitchen and early Robomimic feed-forward/GMM extractors were negative or unstable. | Keep these as diagnostics, not main claims. |

## Core Tables

Detailed CSVs are in `results/paper_tables/`:

- `continuous_pointnav_table.csv`
- `robotics_core_table.csv`
- `claim_matrix.csv`

The hard-vs-soft score conversion diagnostic is in `results/robomimic_hard_soft_tradeoff_summary/`. The first hidden-label-free router candidate is in `results/robomimic_hidden_free_router_summary/`, with shuffled-split validation anchors in `results/robomimic_hidden_free_router_validation_shuffle42/`, `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/`, `results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/`, and `results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/`. A follow-up score-shape audit is in `results/robomimic_router_feature_diagnostics/`, the stricter abstention router is summarized in `results/robomimic_router_v2_abstention_summary/`, and the failed Can MG likelihood-proxy attempt is in `results/robomimic_can_mg_branch_proxy_summary/`. Can 40p/80b masscap-vs-weighted checkpoint-selection, one-seed long-budget, and higher-episode endpoint diagnostics are in `results/robomimic_can40_checkpoint_selection_masscap_weighted/`, `results/robomimic_can40_long_budget_seed0_summary/`, `results/robomimic_can40_endpoint_50ep_summary/`, and `results/robomimic_can40_endpoint_50ep_3seed_summary/`. Support-side Square and Transport quality transfer diagnostics are in `results/robomimic_square_quality_transfer_summary/` and `results/robomimic_transport_quality_transfer_summary/`; the first Square policy smoke is a negative result in `results/robomimic_square_quality_policy_smoke_summary/`.

No-bad-label controls: `results/robomimic_bad_label_ablation/REPORT.md` and `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_3seed_summary/REPORT.md` show that positive-only NN is a strong Can 40p/80b control. The Lift diagnostic in `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md` shows a different regime: positive-only NN top80 is high-purity but coverage-limited, broader positive-only support quickly admits bad demos, and top160 remains below bad-aware `pos_min` at fixed 15k/20k and oracle-by-seed mean.

### Continuous PointNav

This is the cleanest controlled mechanism result. Positive labels are only route prefixes, so positive-only BC cannot solve the full route. Unlabeled data contains hidden safe full routes and hidden trap trajectories.

| bad frac | all-data BC | pos+unlabeled BC | weighted BC state-action | score-gap demo BC |
|---:|---:|---:|---:|---:|
| 0.50 | 0.460 | 0.453 | 0.400 | 1.000 |
| 0.75 | 0.367 | 0.300 | 0.000 | 1.000 |
| 0.90 | 0.233 | 0.247 | 0.000 | 1.000 |
| 0.95 | 0.153 | 0.060 | 0.200 | 1.000 |

Source: `results/continuous_pointnav_gap_select_contamination_5seed_merged/REPORT.md`.

### Robomimic Can Paired

All rows use official Robomimic BC-RNN-GMM with 20k optimizer steps and held-out validation-positive initial states.

| split | method | selected unlabeled | hidden-positive | hidden-bad | purity | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 80p/80b | coverage-aware score-gap | 61.3 | 59.0 | 2.3 | 0.962 | 0.800 | 0.867 | 0.900 |
| 80p/80b | fixed top80 | 80.0 | 72.0 | 8.0 | 0.900 | 0.700 | 0.733 | 0.833 |
| 20p/80b | top20 precision | 20.0 | 15.0 | 5.0 | 0.750 | 0.367 | 0.433 | 0.667 |
| 20p/80b | posx4 coverage-gap | 52.3 | 20.0 | 32.3 | 0.382 | 0.267 | 0.300 | 0.333 |
| 20p/80b | fixed top80 | 80.0 | 20.0 | 60.0 | 0.250 | 0.233 | 0.167 | 0.233 |
| 40p/80b | mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 | 0.500 | 0.733 | 0.733 |
| 40p/80b | weighted BC sampler | 120.0 | 40.0 | 80.0 | 0.333 | 0.600 | 0.700 | 0.567 |
| 40p/80b | top20 precision | 20.0 | 19.7 | 0.3 | 0.983 | 0.567 | 0.667 | 0.700 |
| 40p/80b | positive-only NN top40 | 40.0 | 31.0 | 9.0 | 0.775 | 0.433 | 0.533 | 0.633 |

Sources:

- `results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md`
- `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`
- `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`

Checkpoint-selection diagnostic: `results/robomimic_can40_checkpoint_selection_masscap_weighted/RULE_SUMMARY.md` compares existing Can 40p/80b masscap and weighted checkpoints. Masscap remains ahead at fixed 15k/20k (`0.733`/`0.733`) and oracle-best (`0.767`) versus weighted (`0.700`/`0.567`, oracle-best `0.700`). Train-support and labeled-positive likelihood select the fixed-20k endpoint and preserve the hard-support edge; held-out positive likelihood is noisy and reverses the comparison (`0.467` masscap versus `0.667` weighted), while positive-minus-negative contrastive likelihood selects weak early checkpoints. This supports fixed-budget reporting and argues against claiming best-checkpoint numbers from simple likelihood rules.

Longer-budget diagnostic: `results/robomimic_can40_long_budget_seed0_summary/REPORT.md` trains seed 0 from scratch to 50k using the original 20k train masks. Masscap reaches `0.300`/`0.800`/`0.800`/`0.700`/`0.600` at 10k/20k/30k/40k/50k, while weighted BC reaches `0.700`/`0.500`/`0.300`/`0.500`/`0.300`. This is only one seed, but it directly argues against "weighted BC just needs a longer run" as the default explanation.

Higher-episode endpoint diagnostic: `results/robomimic_can40_endpoint_50ep_3seed_summary/REPORT.md` re-evaluates the original fixed-20k masscap and weighted endpoints for 50 episodes on all three seeds. Masscap remains ahead on every seed (`0.700`/`0.620`/`0.720` versus `0.560`/`0.500`/`0.660`), with mean success `0.680` versus `0.573`. The gap shrinks relative to the 10-episode table (`0.107` versus `0.167`) and approximate pooled binomial intervals overlap, so this strengthens the direction while weakening any claim that the endpoint gap is large or precisely estimated from 10 episodes.

### Robomimic Lift MG

Lift MG is the best cross-task robotics transfer result so far.

| method | train demos | selected unlabeled | purity | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 247.3 | 237.3 | 0.864 | 0.267 | 0.533 | 0.667 | 0.700 |
| positive-only NN top160 | 170.0 | 160.0 | 0.787 | 0.300 | 0.333 | 0.567 | 0.567 |
| weighted BC sampler | 1430.0 | 1420.0 | 0.194 | 0.300 | 0.500 | 0.533 | 0.633 |
| all train positives | 286.0 | 276.0 | 1.000 | 0.433 | 0.700 | 0.633 | 0.733 |
| all train demos | 1440.0 | 1420.0 | 0.194 | 0.033 | 0.167 | 0.200 | 0.267 |

Sources: `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md` and `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md`.

No-bad-label Lift diagnostic: `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md` tests positive-only nearest-neighbor support. Positive-only NN top80 selects 78 hidden-positive and 2 hidden-bad demos but is coverage-limited on seed 0. Top160 selects 126 hidden-positive and 34 hidden-bad demos, reaching three-seed mean success `0.300`/`0.333`/`0.567` at 10k/15k/20k and oracle-by-seed mean `0.567`. Bad-aware `pos_min` selects 203 hidden-positive and 27 hidden-bad demos on seed 0 support diagnostics and reaches `0.267`/`0.533`/`0.667` with oracle-by-seed mean `0.700`. This supports a calibrated bad-label benefit on Lift without claiming bad labels are universally required.

### Robomimic Can MG Sparse

Can MG is a calibration stress diagnostic, not a main positive result yet.

| method | seeds | selected/weighted unlabeled | purity | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|---:|---:|
| top160 selected support | 1 | 160 | 0.706 | 0.100 | 0.100 | 0.000 | 0.100 |
| weighted BC sampler | 3 | 3840 | 0.179 | 0.133 | 0.200 | 0.333 | 0.367 |
| all train positives | 3 | 688 | 1.000 | 0.033 | 0.133 | 0.200 | 0.233 |
| all train demos | 3 | 3840 | 0.179 | 0.000 | 0.200 | 0.100 | 0.233 |
| pos-p10 calibrated threshold | 3 | 773 | 0.538 | 0.000 | 0.100 | 0.167 | 0.167 |

Source: `results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`.

### Hard-Vs-Soft Conversion Diagnostic

The current selector-score evidence supports treating weighted BC as a branch of the method family. A support-only diagnostic now compares score-plateau shape with current policy anchors:

| analysis | observed best mode | support diagnostic | score >= 0.95 demos | best clean hard prefix |
|---|---|---|---:|---:|
| Can paired 80p/80b | hard coverage | hard-support candidate | 0.0 | 80 |
| Can paired 40p/80b | hard mass-capped | hard-support candidate | 0.0 | 50 |
| Can paired 20p/80b | hard precision | hard-support candidate | 0.0 | 20 |
| Lift MG sparse | hard threshold | hard-support candidate | 85.3 | 320 |
| Can MG sparse | soft weighting | soft-weighting candidate | 652.3 | 160 |

Source: `results/robomimic_hard_soft_tradeoff_summary/REPORT.md`.

Interpretation: Can MG has a large high-score plateau, but the clean hard prefix is much smaller than the plateau. The matched controls now support soft sampling as the better Can MG stress-diagnostic branch at fixed 20k, while paired Can and Lift have cleaner hard prefixes matching their hard-support wins.

### Hidden-Free Router Candidate

The first method-level router removes the diagnostic hidden-label purity term. It uses only labeled positive/negative score calibration and the unlabeled score distribution:

| analysis | router branch | training rule | score >= 0.95 demos | labeled-positive p10 | anchored 20k |
|---|---|---|---:|---:|---:|
| Can paired 80p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.748 | 0.900 |
| Can paired 40p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.748 | 0.733 |
| Can paired 20p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.749 | 0.667 |
| Lift MG sparse | hard pos-min threshold | pos-min calibrated threshold | 85.3 | 0.887 | 0.667 |
| Can MG sparse | soft weighted | classifier-probability weighted sampler | 652.3 | 0.943 | 0.333 |

Source: `results/robomimic_hidden_free_router_summary/REPORT.md`.

Shuffled validation splits:

| analysis | router branch | selected unlabeled | hidden-positive | purity | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|---:|---:|
| Can paired 40p/80b shuffle42 | hard adaptive masscap | 63.3 | 39.3 | 0.621 | 0.767 | 0.733 | 0.633 |
| Lift MG shuffle42 | hard pos-min threshold | 199.3 | 185.0 | 0.928 | 0.400 | 0.400 | 0.600 |
| Can MG shuffle42 | hard pos-min threshold | 649.0 | 414.0 | 0.638 | 0.000 | 0.200 | 0.100 |

Sources:

- `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/REPORT.md`
- `results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/REPORT.md`
- `results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/REPORT.md`

Interpretation: this is now a concrete algorithmic candidate rather than only a post-hoc diagnostic, but the shuffled validations expose real limits. The hard branches transfer on Can 40p/80b and Lift MG, but both fixed-20k endpoints are below the corresponding original splits: Can 40p/80b is `0.633` versus `0.733`, and Lift MG is `0.600` versus `0.667`. The Can MG shuffle is a sharper fragility result: the current absolute plateau rule flips from soft weighted to hard `pos_min`, and a seed-0 hard/soft comparison is weak for both (`0.100` fixed 20k each). The router should therefore be presented as an early method candidate with real validation signal and visible split sensitivity, not as the final central paper method.

Feature audit: `results/robomimic_router_feature_diagnostics/REPORT.md` compares hidden-label-free score-shape rules. A mass-only alternative marks both Can MG splits as soft-like, but the Can MG shuffled seed-0 soft policy remains weak; a large-pos-min alternative keeps the same Can MG branch flip as the current rule. The stricter router v2 in `results/robomimic_router_v2_abstention_summary/REPORT.md` therefore abstains on both original and shuffled Can MG, while assigning paired Can and Lift hard-support branches. Across its six assigned Can/Lift rows, fixed-20k success has mean `0.700` and minimum `0.600`; the two abstained Can MG rows have mean `0.217` and maximum `0.333`.

### Router V2 Abstention Candidate

Router v2 is the safest current method-level candidate:

| class | rows | decision | fixed-20k outcome |
|---|---:|---|---:|
| paired Can + Lift, original and shuffled | 6 | assigned hard support | mean `0.700`, min `0.600` |
| Can MG, original and shuffled | 2 | abstain / stress diagnostic | mean `0.217`, max `0.333` |

This reframes the method away from forcing a hard-vs-soft answer on every task. The supported paper-facing method is now a high-confidence hard-support converter with abstention on large ambiguous score shapes. Can MG remains useful because it exposes where a future validation-proxy or quality-estimator branch is needed.

### Can MG Branch-Proxy Attempt

`results/robomimic_can_mg_branch_proxy_summary/REPORT.md` tests a natural hidden-label-free replacement for abstention: score trained final-20k branches by BC log-likelihood on labeled and held-out positive/negative masks. This does **not** work well enough:

- On original Can MG, the rollout-best final-20k method is weighted sampling (`0.333`), but all tested likelihood proxies choose all-positive support (`0.200`).
- On shuffled Can MG, the hard and soft seed-0 branches tie at `0.100`, so likelihood can select a branch but cannot detect that both branches are weak.

Interpretation: positive imitation and negative rejection are not enough on Can MG. The missing proxy must capture coverage-sensitive rollout quality; until then, router v2 abstention is the more honest method behavior.

### Square Quality Transfer Diagnostic

`results/robomimic_square_quality_transfer_summary/REPORT.md` adds a support-side transfer check on a new Robomimic task family, NutAssemblySquare. Square MH has relative-quality masks (`better`, `okay`, `worse`) but no reward-failure demonstrations, so this is **not** a main bad-demo benchmark.

Using 10 `better_train` positives, 10 `worse_train` negatives, and an 80/80 hidden `better`/`worse` unlabeled mix:

| quantity | value |
|---|---:|
| labeled-positive mean score | `0.939` |
| labeled-negative mean score | `0.053` |
| `pos_min` selected purity | `0.803` |
| adaptive-masscap selected purity | `0.712` |
| hidden-free router branch | hard adaptive masscap |

Interpretation: scarce relative-quality labels transfer to a new manipulation task and produce a useful desirability score. This strengthens the score-calibration mechanism claim, but it remains support-only until a quality-sensitive Square policy evaluation is added.

A first bounded Square policy smoke was added in `results/robomimic_square_quality_policy_smoke_summary/`. It trained official BC-RNN-GMM policies for better-only support, mixed better+worse support, and adaptive-masscap support on seed 0. All three methods get `0.000` success at epoch 50 and epoch 100 over 10 held-out `better_valid` initial-state rollouts with horizon 500. This is a negative/inconclusive policy result; Square should remain support-side transfer evidence unless a stronger Square policy setup or direct quality-sensitive evaluator is added.

### Transport Quality Transfer Diagnostic

`results/robomimic_transport_quality_transfer_summary/REPORT.md` adds a second support-side relative-quality transfer check on TwoArmTransport. Transport MH has `better`/`okay`/`worse` masks and all `300` trajectories are reward-positive, so this is also **not** a failure-demo benchmark.

Using 10 `better_train` positives, 10 `worse_train` negatives, and the remaining 35/35 hidden `better`/`worse` train demos as unlabeled:

| quantity | value |
|---|---:|
| labeled-positive mean score | `0.988` |
| labeled-negative mean score | `0.014` |
| top-30 selected purity | `1.000` |
| `pos_min` selected purity | `1.000` |
| adaptive-masscap selected purity | `0.972` |

Interpretation: scarce relative-quality labels transfer cleanly to a harder two-arm manipulation task and recover almost all hidden `better` support. This strengthens the cross-task score-calibration mechanism, but it remains support-side evidence only.

## Unsupported Or Risky Claims

Do not claim:

- "Weighted BC is bad." It is strong when implemented correctly.
- "Hard support is always better than soft weights." Can MG matched controls contradict this at fixed 20k, though it remains a stress diagnostic rather than a main benchmark claim.
- "Bad labels are required." Positive-only NN is a strong control on Can 40p/80b. Lift now shows a three-seed regime where bad-aware calibration has a clearer fixed-budget coverage-quality advantage, but that is not a universal necessity claim.
- "The full inverse-Q objective is validated on Robomimic." The strongest robotics rows are classifier-ranked support / weighted sampling plus official BC-RNN-GMM.
- "Best checkpoint proves the method." Fixed-budget reporting is cleaner; Lift and Can 40p/80b likelihood diagnostics show simple hidden-label-free checkpoint rules are too brittle. Ten-episode Robomimic evaluations should also be treated as noisy endpoint estimates.

## Next Experiments

Highest value next steps:

1. Replace router-v2 abstention with a validated hidden-label-free policy-quality proxy if Can MG should become a main positive result rather than a stress diagnostic; simple positive/negative BC likelihood is now ruled out.
2. If the paper needs a stronger bad-label-ablation claim, add another task or policy setup where the positive-only NN control is tested with the same three-seed protocol.
3. If best-checkpoint reporting is desired, design a stronger predeclared checkpoint-selection rule; current Lift and Can 40p/80b likelihood diagnostics do not solve the issue.
4. If using Square or Transport MH beyond support diagnostics, replace sparse-success evaluation with a quality-sensitive evaluator; sparse success alone is unsuitable because the downloaded MH demos are all successful.
5. If returning to the original Tri-PIQL objective, compare it against the official weighted BC sampler, not the earlier under-configured weighted BC.

## Bottom Line

The baseline now works well enough to shape the paper. The credible story is not that weighted BC fails. It is that tri-signal labels make the score useful, and the method contribution should be the calibrated conversion from that score into policy-training data under scarce positives, explicit failures, and mixed unlabeled logs.
