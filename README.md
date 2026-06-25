# TRIAGE-BC / Tri-PIQL

Research scaffold for tri-signal offline imitation from scarce successes,
explicit failures, and mixed unlabeled logs.

The current paper-facing plan is `tri_piql_paper_completion_plan.md`. The
frozen forward-looking method contract is `METHOD_FREEZE.md`, with machine-readable
settings in `configs/final_method.yaml` and `configs/final_eval.yaml`. Existing
results are development, validation, ablation, or diagnostic evidence unless
they are rerun under the freeze and staged under `results/final_paper/`.
The current writing scaffold is `PAPER_DRAFT_OUTLINE.md`, which maps staged
figures, tables, claims, caveats, and limitations into a paper section plan.
The current Markdown manuscript draft is `paper/triage_bc_draft.md`, and the
current standalone LaTeX manuscript scaffold is `paper/triage_bc_paper.tex`
with compiled output at `paper/triage_bc_paper.pdf`.

## Current diagnostics

The executable target is a set of fast GridWorld diagnostics:

- generate good, bad, and unlabeled mixed trajectories;
- compare BC-positive, BC-all, weighted BC, and a tabular Tri-PIQL prototype;
- verify that bad demonstrations induce avoidance;
- test when trajectory-level filtering is insufficient and transition-level anti-preference is needed.

Basic shortcut smoke:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_gridworld_diagnostic.py \
  --steps 300 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --out-dir results/gridworld_diagnostic
```

Stronger loop-mixed diagnostic:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_gridworld_diagnostic.py \
  --scenario loop_mixed \
  --steps 600 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --positive-prefix-len 6 \
  --out-dir results/gridworld_loop_mixed
```

Neural reward version of the loop-mixed diagnostic:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_neural_gridworld.py \
  --steps 1200 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --feature-mode coords \
  --negative-shortcut-frac 0.5 \
  --out-dir results/neural_gridworld_loop_mixed_contrastive
```

Larger coordinate-grid version:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_neural_gridworld.py \
  --width 21 --height 21 --max-steps 60 --trap-x 15 --trap-y 7 \
  --positive-prefix-len 20 \
  --steps 1200 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --feature-mode coords \
  --negative-shortcut-frac 0.5 \
  --out-dir results/neural_pointgrid21_loop_mixed
```

Current summary:

- `results/gridworld_diagnostic/REPORT.md`: useful smoke, but BC-positive and weighted BC are also strong.
- `results/gridworld_prefix_stitching/REPORT.md`: Tri-PIQL beats naive cloning, but weighted BC still solves it.
- `results/gridworld_loop_mixed/REPORT.md`: current best synthetic result; Tri-PIQL succeeds across the tested sweep while weighted BC fails because it clones repeated bad loop actions inside otherwise useful unlabeled trajectories.
- `results/neural_gridworld_loop_mixed_contrastive/REPORT.md`: current best function-approximation result; neural Tri-PIQL succeeds across the tested sweep while weighted BC fails.
- `results/neural_pointgrid21_loop_mixed/REPORT.md`: larger coordinate-grid result; neural Tri-PIQL AWBC succeeds across the tested sweep, weighted BC fails, and greedy-Q is less reliable than the offline extractor.
- `results/continuous_pointnav_posterior_hard_sweep_stable_5seed/REPORT.md`: controlled continuous-action diagnostic; with 90% bad unlabeled trajectories, conservative trajectory-posterior BC and top-demo BC reach 1.000 success over five seeds while all-data BC is 0.233 and positive+unlabeled BC is 0.247.
- `results/continuous_pointnav_gap_select_contamination_5seed_merged/REPORT.md`: current best continuous-control diagnostic; score-gap trajectory selection recovers pure hidden-good support and gap-demo BC reaches 1.000 success over five seeds at 50%, 75%, 90%, and 95% bad unlabeled data. At 95% bad data, all-data BC is 0.153, positive+unlabeled BC is 0.060, and fixed-prior posterior BC is 0.800.
- `results/minari_inspection/D4RL__pointmaze__large-v2/REPORT.md`: first real Minari dataset inspection and return/length split.
- `results/minari_pointmaze_large_bc_smoke/REPORT.md`: first recovered-environment PointMaze BC smoke.
- `results/minari_inspection/D4RL__pointmaze__large-dense-v2/REPORT.md`: dense PointMaze inspection with usable return labels.
- `results/minari_pointmaze_large_dense_bc_smoke/REPORT.md`: dense PointMaze BC smoke.
- `results/minari_pointmaze_large_tri_piql_smoke/REPORT.md`: sparse PointMaze Tri-PIQL score smoke; useful negative actor-extraction result.
- `results/minari_pointmaze_large_dense_tri_piql_smoke/REPORT.md`: dense PointMaze Tri-PIQL score smoke; useful negative actor-extraction result.
- `results/minari_pointmaze_large_dense_tri_iql_filtered/REPORT.md`: dense PointMaze V/Q Tri-PIQL smoke; useful negative advantage-extraction result.
- `results/minari_pointmaze_large_dense_action_rerank/SEED_SUMMARY.md`: dense PointMaze state-action reranker smoke; modest two-seed signal, not yet paper-strength.
- `results/minari_kitchen_mixed_bc_smoke/REPORT.md`: Kitchen mixed BC smoke; classifier separates labels but simple BC gets zero reward.
- `results/minigrid_fourrooms_discrete_smoke/REPORT.md`: MiniGrid FourRooms discrete smoke; feed-forward BC/reranking is too weak under partial observability.
- `results/robomimic_inspection/can_paired_low_dim/REPORT.md`: Robomimic Can paired low-dimensional inspection; balanced success/failure demos with a clean 10 positive / 10 negative / 160 unlabeled split.
- `results/robomimic_can_paired_offline/REPORT.md`: Robomimic Can offline diagnostic; state-action classifier reaches 0.854 held-out AUC from scarce labels.
- `results/robomimic_can_playback_check/REPORT.md`: Robomimic Can simulator compatibility check; stored held-out successful demos replay at 10/10 success.
- `results/robomimic_can_rollout_smoke/REPORT.md`: Robomimic Can random-reset rollout smoke; current lightweight feed-forward BC/rerank policies get zero success.
- `results/robomimic_can_rollout_valid_states/REPORT.md`: Robomimic Can held-out-state rollout smoke with scarce labels; current lightweight feed-forward policies get zero success.
- `results/robomimic_can_rollout_valid_states_budget80/REPORT.md`: Robomimic Can held-out-state rollout smoke with 80 positive and 80 negative labels; current lightweight feed-forward policies still get zero success.
- `results/robomimic_can_knn_valid_states_budget80/REPORT.md`: Robomimic Can oracle-support KNN sanity check; all train positives get nonzero held-out success, best 0.4 over five validation starts.
- `results/robomimic_can_knn_valid_states_classifier_unlabeled_t09/REPORT.md`: Robomimic Can scarce-label plus classifier-selected unlabeled KNN; improves from 0.0 scarce-positive KNN to 0.2 over five validation starts.
- `results/robomimic_can_gmm_valid_states_all_train_positive/REPORT.md`: Robomimic Can oracle-support learned GMM; all train positives get nonzero held-out success, best 0.4 over five validation starts.
- `results/robomimic_can_gmm_valid_states_top80_unlabeled_demos/REPORT.md`: Robomimic Can scarce-label plus trajectory-selected unlabeled GMM; top 80 unlabeled demos include 61 hidden positives and the GMM mean policy reaches 0.2 held-out success.
- `results/robomimic_can_gmm_scarce_vs_top80_seed_summary/REPORT.md`: three-seed GMM summary; scarce-positive GMM is 0.0 across seeds, top-80 selected-demo GMM has nonzero but noisy success, best mean 0.133.
- `results/robomimic_can_gmm_gap_vs_top80_summary/REPORT.md`: Robomimic Can score-gap transfer; gap selection picks about 25 pure hidden-positive unlabeled demos and reaches 0.333 held-out success at 5k over seeds 0/1/2, compared with 0.300 for fixed top-80 at 20k and 0.067 for scarce positives at 20k.
- `results/robomimic_can_gmm_extractor_diagnostics_summary/REPORT.md`: Robomimic GMM extractor diagnostics; support-validation NLL/MSE checkpoint selection and prev-action/time features do not improve the score-gap policy, so the next Robomimic step should use a stronger sequence-aware imitation backbone.
- `results/robomimic_official_bc_rnn_gap_vs_scarce_seed0_summary/REPORT.md`: official Robomimic BC-RNN-GMM seed-0 comparison; score-gap selected support reaches 0.700 held-out success at 10k/15k/20k steps, while same-backbone scarce-positive BC reaches 0.100 at 20k.
- `results/robomimic_official_bc_rnn_seed0_support_controls/REPORT.md`: official Robomimic same-backbone support controls; fixed top-80 matches score-gap at 0.700 success on seed 0, so the current score-gap advantage is compact pure support rather than higher rollout success on this seed.
- `results/robomimic_official_bc_rnn_seed2_coverage_stress/REPORT.md`: official Robomimic coverage stress; seed-2 score-gap selects only 9 pure unlabeled demos and peaks at 0.100 success, while fixed top-80 selects 74 hidden-positive plus 6 hidden-bad demos and reaches 0.900 success at 20k.
- `results/robomimic_official_bc_rnn_gap_min40_seed2_summary/REPORT.md`: coverage-aware score-gap fix; requiring at least 40 selected unlabeled demos gives 65 hidden-positive plus 1 hidden-bad selected demo and reaches 0.900 success at 10k/15k/20k on seed 2.
- `results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md`: current best Robomimic result; coverage-aware score-gap with a hidden-label-free `4 x labeled-positive demo count` coverage floor has three-seed mean success 0.800/0.867/0.900 at 10k/15k/20k, versus 0.700/0.733/0.833 for fixed top-80, while selecting 7 hidden-bad demos instead of 24.
- `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`: matched heavy-contamination stress check with 20 hidden-positive / 80 hidden-bad unlabeled demos; precision-biased top-20 reaches mean 0.667 success at 20k over three seeds versus 0.333 for posx4 and 0.233 for fixed top-80, showing that the balanced-split `4 x` coverage rule is too contamination-prone here.
- `results/robomimic_adaptive_masscap_selector_summary/REPORT.md`: current hidden-label-free adaptive selector; calibrated unlabeled positive-mass plus a mass cap preserves the validated 0.900 balanced and 0.667 stress 20k mean success endpoints, and reaches 0.733 mean success at 15k/20k on the intermediate 40p/80b split.
- `results/robomimic_adaptive_selector_sweep_pos_count/REPORT.md`: support-only positive-count sweep with 80 hidden-bad demos; validates that the mass-capped selector switches from top20 precision to coverage/mass-capped support as estimated positive mass rises.
- `results/robomimic_bad_label_ablation/REPORT.md`: support-only bad-label ablation; positive-vs-unlabeled scoring is weak, but positive-only nearest-neighbor support is a strong no-bad-label control.
- `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_3seed_summary/REPORT.md`: official BC-RNN-GMM no-bad-label control on the 40p/80b split; positive-only NN top40 ties masscap on best-per-seed mean but is lower at fixed 10k/15k/20k checkpoints.
- `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`: three-seed official BC-RNN-GMM intermediate split check; mass-capped support reaches 0.733 mean success at 15k/20k, versus coverage-gap 0.567/0.600, top20 0.667/0.700, and positive-only NN top40 0.533/0.633.
- `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_3seed_summary/REPORT.md`: official weighted BC control on the 40p/80b split; classifier-probability weighting is competitive at 10k/15k (0.600/0.700 mean success), but lower than mass-capped hard support at fixed 20k (0.567 versus 0.733).
- `results/robomimic_can40_checkpoint_selection_masscap_weighted/RULE_SUMMARY.md`: Can 40p/80b checkpoint-selection diagnostic; masscap stays ahead of weighted BC at fixed 15k/20k and oracle-best, while simple likelihood rules are not reliable enough to justify best-checkpoint reporting.
- `results/robomimic_can40_long_budget_seed0_summary/REPORT.md`: Can 40p/80b seed-0 50k-budget diagnostic; weighted BC peaks at 10k and degrades after 20k, while masscap peaks at 20k/30k, so longer optimization alone does not explain the 20k weighted gap.
- `results/robomimic_can40_endpoint_50ep_3seed_summary/REPORT.md`: Can 40p/80b three-seed fixed-20k higher-episode check; masscap remains ahead of weighted BC on every seed over 50 episodes, with mean success 0.680 versus 0.573.
- `results/final_paper/tables/can_paired_pos40_bad80_split11_endpoint_REPORT.md`: first frozen Can 40p/80b final split endpoint; TRIAGE-BC reaches 0.760 versus weighted BC 0.720 over 50 fixed-20k rollouts.
- `results/final_paper/tables/can_paired_pos40_bad80_split22_endpoint_REPORT.md`: second frozen Can 40p/80b final split endpoint; TRIAGE-BC reaches 0.520 versus weighted BC 0.440 over 50 fixed-20k rollouts.
- `results/final_paper/tables/can_paired_pos40_bad80_split33_endpoint_REPORT.md`: third frozen Can 40p/80b final split endpoint; TRIAGE-BC reaches 0.700 versus weighted BC 0.640 over 50 fixed-20k rollouts.
- `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`: completed primary frozen endpoint aggregate; diagnostic all-positive oracle is 0.980, and among non-oracle rows positive-only NN top40 is strongest at 0.720, followed by TRIAGE-BC 0.660, weighted BC 0.600, and all-demo BC 0.540 over 150 endpoint rollouts.
- `results/robomimic_lift_mg_official_bc_rnn_seed0_summary/REPORT.md`: first cross-task Robomimic Lift MG screen; classifier top-160 purifies a 19.4% reward-positive unlabeled pool to 96.3% selected-positive support and reaches 0.700 success at 20k, while the hidden-label-free `pos_min` calibrated threshold reaches 0.800 on seed 0, matching oracle all-positive support and beating all-demo cloning at 0.100.
- `results/robomimic_lift_mg_official_bc_rnn_posmin_3seed_summary/REPORT.md`: three-seed Lift MG `pos_min` follow-up; support purification is stable at 86.4% selected-positive purity on average, with 20k mean success 0.667 and best-per-seed mean 0.700. Seed 1 peaks at 15k, so checkpoint-selection evidence is the next remaining Lift robustness question.
- `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`: same-seed Lift MG controls; `pos_min` is far above all-demo cloning at 20k (0.667 versus 0.200 mean success), beats the soft classifier-weighted BC sampler at 20k (0.667 versus 0.533), and is close to all-positive oracle support (0.633 mean success at 20k, 0.733 best-per-seed).
- `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_3seed_summary/REPORT.md`: official Robomimic weighted BC baseline; classifier probabilities make soft weighted BC much stronger than all-demo cloning (0.533 versus 0.200 at 20k), but hard `pos_min` support selection remains better at fixed 20k.
- `results/robomimic_lift_mg_checkpoint_selection_posmin_oracle_alltrain/REPORT.md`: Lift checkpoint-selection diagnostic; train-support or labeled-positive likelihood preserves the fixed-20k pos-min story, but random validation likelihood is misleading because it scores the bad-dominated holdout. This is a negative result for best-checkpoint reporting, not a replacement for fixed-budget comparisons.
- `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md`: Lift no-bad-label positive-only NN control; top80 is pure but coverage-limited, broader top-k degrades quickly, and top160 remains below bad-aware `pos_min` at fixed 15k/20k and oracle-by-seed mean (0.333/0.567/0.567 versus 0.533/0.667/0.700).
- `results/robomimic_lift_mg_endpoint_50ep_summary/REPORT.md`: Lift MG fixed-20k higher-episode check; `pos_min` remains ahead of weighted BC over 50 episodes (0.600 versus 0.533), but the edge over positive-only NN top160 is small (0.600 versus 0.560).
- `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`: completed frozen Lift endpoint aggregate; diagnostic all-positive oracle is 0.700, and among non-oracle rows weighted BC is strongest at 0.620, followed by positive-only NN top160 0.547, TRIAGE-BC 0.493, and all-demo BC 0.207 over 150 endpoint rollouts.
- `results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`: classifier-score top160 support ablation on frozen Lift; high support purity does not rescue the policy result, with pooled success 0.453 versus 0.493 for TRIAGE-BC and 0.620 for weighted BC.
- `results/robomimic_can_mg_official_bc_rnn_seed0_summary/REPORT.md`: Can MG sparse one-seed stress diagnostic; all-positive oracle support reaches 0.400 at 20k, all-demo mixed cloning reaches 0.200, pos-p10 hard support reaches 0.300, and classifier-weighted sampling reaches 0.400.
- `results/robomimic_can_mg_official_bc_rnn_weighted_prob_3seed_summary/REPORT.md`: Can MG weighted-sampler three-seed follow-up; weighted BC reaches 0.333 mean success at 20k and 0.367 best-per-seed, showing nontrivial signal from broad weighted coverage with modest absolute success.
- `results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`: matched Can MG controls; weighted BC is the best fixed-20k three-seed row (0.333) versus all-positive support (0.200), pos-p10 hard support (0.167), and all-demo cloning (0.100), but remains a stress diagnostic because absolute success is modest.
- `results/robomimic_hidden_free_router_summary/REPORT.md`: first hidden-label-free hard/soft router candidate; uses labeled-score calibration and unlabeled score saturation to choose hard adaptive support for paired Can, pos-min hard threshold for Lift, and soft weighting for Can MG.
- `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/REPORT.md`: shuffled 40p/80b validation of the router-selected hard adaptive-masscap branch; mean success is 0.767/0.733/0.633 at 10k/15k/20k over three seeds.
- `results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/REPORT.md`: shuffled Lift MG validation of the router-selected hard pos-min branch; high-purity support transfers, but mean success is lower than the original Lift split at 0.400/0.400/0.600 for 10k/15k/20k.
- `results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/REPORT.md`: shuffled Can MG branch-boundary check; the current router flips from soft weighted to hard pos-min, and a seed-0 hard/soft policy comparison is weak for both branches.
- `results/robomimic_router_feature_diagnostics/REPORT.md`: hidden-label-free score-shape audit; simple score-shape alternatives do not rescue the Can MG fragility, so the next router should abstain or use a validation proxy on large bad-dominated MG pools.
- `results/robomimic_router_v2_abstention_summary/REPORT.md`: stricter hidden-label-free router candidate; keeps paired Can and Lift assigned to hard-support branches while abstaining on both original and shuffled Can MG stress cases.
- `results/robomimic_can_mg_branch_proxy_summary/REPORT.md`: Can MG likelihood-proxy test; positive/negative BC likelihood chooses too-pure all-positive support on original Can MG and cannot detect the weak shuffled branches, so it does not replace router-v2 abstention.
- `results/robomimic_square_quality_transfer_summary/REPORT.md`: Square MH support-side transfer diagnostic; scarce `better`/`worse` relative-quality labels produce a strong score on NutAssemblySquare, but this is not a reward-failure benchmark.
- `results/robomimic_square_quality_policy_smoke_summary/REPORT.md`: Square MH one-seed official BC-RNN-GMM policy smoke; better-only, mixed better+worse, and adaptive-masscap policies all get 0/10 success at epoch 50 and epoch 100 on held-out `better_valid` initial states, so Square remains support-side evidence for now.
- `results/robomimic_transport_quality_transfer_summary/REPORT.md`: Transport MH support-side transfer diagnostic; scarce `better`/`worse` relative-quality labels almost perfectly recover hidden `better` support (adaptive-masscap purity 0.972), but all demos are reward-positive, so this is not a failure-demo benchmark.
- `results/robomimic_adaptive_posmass_selector_summary/REPORT.md`: predecessor adaptive selector; useful as a control because it preserves endpoints but can over-expand support in intermediate contamination regimes.
- `METHOD_FREEZE.md`: frozen TRIAGE-BC v0.1 method contract for future final split runs; fresh final artifacts should be staged under `results/final_paper/`.
- `results/ITERATION_LOG.md`: concise interpretation and next-step notes.

## External Dataset Setup

The `tri-piql` conda environment now has Minari/Gymnasium installed for the next benchmark stage.

Verified:

```bash
conda run -n tri-piql minari list remote --prefix D4RL/pointmaze
```

This currently lists D4RL PointMaze datasets such as `D4RL/pointmaze/medium-v2`, `D4RL/pointmaze/large-v2`, and dense variants. `D4RL/pointmaze/large-v2` has been downloaded locally.

Inspect and create a trajectory-level split:

```bash
conda run -n tri-piql python scripts/inspect_minari_dataset.py \
  D4RL/pointmaze/large-v2 \
  --out-dir results/minari_inspection \
  --top-frac 0.10 --bottom-frac 0.20 \
  --score-mode return_length \
  --seed 0
```

Run the current PointMaze BC smoke with recovered-environment evaluation:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_bc_baselines.py \
  D4RL/pointmaze/large-v2 \
  --out-dir results/minari_pointmaze_large_bc_smoke \
  --steps 600 --classifier-steps 300 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 10 --eval-horizon 800 \
  --seed 0
```

The sparse PointMaze reward is almost fully tied at return `1`, so the first split uses `return_length`: failed trajectories rank below successful ones, and shorter successful trajectories rank above slower successful ones. The first smoke is not a final benchmark result, but it validates that mixed-log cloning underperforms positive-only and classifier-weighted BC on the recovered environment.

Dense PointMaze has a usable return distribution:

```bash
conda run -n tri-piql python scripts/inspect_minari_dataset.py \
  D4RL/pointmaze/large-dense-v2 \
  --out-dir results/minari_inspection \
  --top-frac 0.10 --bottom-frac 0.20 \
  --score-mode return \
  --seed 0
```

Current real-data Tri-PIQL smoke:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_tri_piql_smoke.py \
  D4RL/pointmaze/large-dense-v2 \
  --out-dir results/minari_pointmaze_large_dense_tri_piql_smoke \
  --steps 800 --actor-steps 700 --classifier-steps 300 \
  --batch-size 512 --traj-batch-size 12 \
  --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 10 --eval-horizon 800 \
  --seed 0
```

The current PointMaze Tri-PIQL score smoke is a negative result: the learned trajectory score can separate labels, but the extracted actor underperforms BC-positive and classifier-weighted BC. The next real-data method step should add an actual IQL-style V/Q training path for continuous actions instead of tuning the scalar score actor weights.

V/Q smoke:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_tri_iql_smoke.py \
  D4RL/pointmaze/large-dense-v2 \
  --out-dir results/minari_pointmaze_large_dense_tri_iql_filtered \
  --steps 1000 --actor-steps 700 --classifier-steps 300 \
  --batch-size 512 --traj-batch-size 12 \
  --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 10 --eval-horizon 800 \
  --trajectory-reduction sum \
  --seed 0
```

The V/Q smoke is also negative: reward ranking and positive/negative advantage separation look reasonable, but raw, normalized, top-q, and positive-only advantage-weighted actor extraction all underperform BC-positive. The next method direction should change the policy extraction mechanism or benchmark choice, not keep tuning advantage weights on this PointMaze split.

Action-reranking smoke:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_action_rerank_smoke.py \
  D4RL/pointmaze/large-dense-v2 \
  --out-dir results/minari_pointmaze_large_dense_action_rerank \
  --bc-steps 700 --classifier-steps 500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 10 --eval-horizon 800 \
  --candidate-count 64 \
  --noise-stds 0.10 0.25 \
  --action-penalties 0.05 0.20 \
  --seed 0
```

Across two seeds, state-action reranking learns a real positive-vs-negative action distinction and improves dense return, but success-rate gains are not robust. The best two-seed success mean ties BC-positive at 0.300. See `results/minari_pointmaze_large_dense_action_rerank/SEED_SUMMARY.md`.

Other real-data screening:

- `D4RL/kitchen/mixed-v2`: return labels are clean and the classifier separates positives/negatives, but simple feed-forward BC gets zero rollout reward over the first smoke. This target likely needs a stronger robotics imitation stack before it can test Tri-PIQL.
- `D4RL/minigrid/fourrooms-v0`: compact and discrete, but feed-forward partial-observation BC reaches only 5% success, and tri-signal weighting/reranking does not improve it. This target likely needs recurrence or full-state features before it is useful.

Robomimic Can paired low-dimensional data has a clean tri-signal structure, but the current lightweight feed-forward JAX imitation stack is not rollout-capable.
The downloaded file is excluded from git under `data/`.

Inspect the dataset and create the scarce-label split:

```bash
conda run -n tri-piql python scripts/inspect_robomimic_dataset.py \
  data/robomimic/v1.5/can/paired/low_dim_v15.hdf5 \
  --out-dir results/robomimic_inspection/can_paired_low_dim \
  --label-budget 10
```

Run the offline viability diagnostic:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_robomimic_offline_diagnostic.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_paired_offline \
  --steps 1000 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --seed 0
```

This offline diagnostic is not a rollout benchmark. It shows that the paired Can data has clean scarce good/bad labels and that a state-action classifier generalizes to held-out success/failure demos.

Verify simulator reconstruction by replaying held-out successful demonstrations:

```bash
NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/check_robomimic_playback.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_playback_check \
  --demo-source valid_positive --max-demos 10
```

Run the current short rollout smoke:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_can_rollout_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_rollout_smoke \
  --bc-steps 1000 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 5 --eval-horizon 400 \
  --candidate-count 32 --noise-stds 0.10 --action-penalties 0.05 \
  --seed 0
```

Run the nonparametric KNN support checks:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_knn_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_knn_valid_states_classifier_unlabeled_t09 \
  --source positive_plus_classifier_unlabeled \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --k-values 1 3 5 \
  --classifier-steps 800 --batch-size 512 --hidden-dim 128 --depth 2 \
  --unlabeled-threshold 0.9 --seed 0
```

The current Robomimic evidence is: scarce positive KNN gets 0.0 success, classifier-selected unlabeled KNN gets 0.2, and oracle all-train-positive KNN gets 0.4 on the same five held-out successful initial states. This is a useful tri-signal direction, but it needs a stronger sequence/action-distribution policy extractor before it can become a main paper result.

Run the learned GMM extractor with trajectory-level unlabeled selection:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_valid_states_top80_unlabeled_demos \
  --source positive_plus_classifier_top_unlabeled_demos \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --steps 1500 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 5 --policy-modes mode mean classifier_rerank \
  --candidate-count 32 --top-unlabeled-demos 80 --seed 0
```

Three-seed summary:

```bash
conda run -n tri-piql python scripts/summarize_robomimic_gmm_runs.py \
  results/robomimic_can_gmm_valid_states_scarce \
  results/robomimic_can_gmm_valid_states_scarce_seed1 \
  results/robomimic_can_gmm_valid_states_scarce_seed2 \
  results/robomimic_can_gmm_valid_states_top80_unlabeled_demos \
  results/robomimic_can_gmm_valid_states_top80_unlabeled_demos_seed1 \
  results/robomimic_can_gmm_valid_states_top80_unlabeled_demos_seed2 \
  --out-dir results/robomimic_can_gmm_scarce_vs_top80_seed_summary
```

This gives a learned-policy version of the Robomimic signal, but the local GMM extractor is noisy: score-gap selected support works better than scarce-positive and fixed top-k support, but checkpoint choice is unstable. The stronger Robomimic branch below is the current baseline to extend.

Run the official Robomimic BC-RNN-GMM score-gap baseline:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/prepare_robomimic_official_bc_rnn.py \
  --out-dir results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup \
  --train-output-dir "$PWD/results/robomimic_official_bc_rnn_gap_seed0_mlphead_train" \
  --source positive_plus_classifier_gap_unlabeled_demos \
  --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 \
  --seq-length 10 --actor-layer-dims 1024,1024 \
  --rnn-hidden-dim 400 --rnn-layers 2 --gmm-modes 5 \
  --train-batch-size 100 \
  --classifier-steps 800 --batch-size 512 --hidden-dim 128 --depth 2 \
  --gap-select-max-unlabeled-demos 80 --gap-select-min-unlabeled-demos 4 \
  --seed 0

JAX_PLATFORMS=cpu conda run -n tri-piql \
  python -m robomimic.scripts.train \
  --config results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup/config.json

JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/evaluate_robomimic_official_policy.py \
  --out-dir results/robomimic_official_bc_rnn_gap_seed0_mlphead_eval \
  --checkpoint-glob 'results/robomimic_official_bc_rnn_gap_seed0_mlphead_train/*/*/models/model_epoch_*.pth' \
  --eval-episodes 10 --eval-horizon 400 \
  --eval-init-mode valid_positive_states \
  --device cuda --seed 0
```

Matched seed-0 official-backbone result:

| source | train demos | hidden-bad selected | checkpoint | held-out success |
|---|---:|---:|---:|---:|
| labeled positives only | 10 | 0 | 20k | 0.100 |
| score-gap cutoff | 43 | 0 | 10k | 0.700 |
| score-gap cutoff | 43 | 0 | 20k | 0.700 |
| fixed top-80 | 90 | 8 | 10k | 0.700 |
| fixed top-80 | 90 | 8 | 20k | 0.700 |
| seed-2 score-gap cutoff | 19 | 0 | 20k | 0.000 |
| seed-2 score-gap min40 | 76 | 1 | 20k | 0.900 |
| seed-2 fixed top-80 | 90 | 6 | 20k | 0.900 |

The Robomimic story is now: classifier-ranked unlabeled support plus a competent sequence-aware BC backbone can make the baseline work, and soft classifier-probability weighted BC is a meaningful baseline. The selector still has to trade off purity and coverage. Pure largest-gap can be too conservative; a coverage floor fixes the balanced split, top20 precision is better under heavy contamination, and mass-capped coverage is best at fixed 15k/20k on the intermediate 40p/80b split. Positive-only nearest-neighbor support is a strong no-bad-label control on Can 40p/80b, so the honest claim is not that bad labels are strictly necessary. The completed frozen Lift matrix shows the complementary caveat: bad-aware `pos_min` improves selected-support purity, but weighted BC and positive-only NN beat TRIAGE-BC at the policy endpoint, so Lift should be written as calibration/stability and precision/coverage evidence rather than a bad-label policy win. Can MG sparse is currently a calibration stress case where broad soft weighting is the best matched fixed-20k row (0.333 versus 0.200 for all-positive, 0.167 for pos-p10, and 0.100 for all-demo), but the absolute success is too modest for a main benchmark claim. Naive local state-action weighted BC and under-configured Robomimic BC are not the method we should claim.

The consolidated paper-facing claim package is in `results/PAPER_CLAIM_PACKAGE.md`, with compact CSV tables under `results/paper_tables/`. Its main boundary is that weighted BC is now a strong baseline, not a strawman: hard calibrated support wins on paired Can, fresh frozen Lift favors weighted BC despite TRIAGE support-purity gains, and Can MG remains a stress diagnostic where broad soft weighting is currently better than the matched hard-support controls. A seed-0 Can 40p/80b 50k-budget check suggests longer Robomimic BC training is not a default fix: weighted BC peaks early and degrades, while masscap peaks around 20k/30k. A three-seed 50-episode endpoint check keeps masscap ahead at fixed 20k on every seed, but also shows the mean gap is modest (0.680 versus 0.573) and 10-episode endpoint estimates are noisy. Square and Transport add support-side evidence that the score-calibration mechanism transfers to additional manipulation task families under relative-quality labels.

The hard-vs-soft score conversion diagnostic is in `results/robomimic_hard_soft_tradeoff_summary/REPORT.md`. It turns that baseline result into the next method question: paired Can looks like a hard-support case, fresh frozen Lift exposes a coverage failure for the current hard threshold, and Can MG has a large high-score plateau where a future converter may need to preserve soft weighted coverage.

The first hidden-label-free router candidate is in `results/robomimic_hidden_free_router_summary/REPORT.md`. It removes the diagnostic hidden-label purity term and uses only labeled-score calibration plus unlabeled score saturation, but it still needs validation on a held-out split or task before becoming the central method claim.

`METHOD_FREEZE.md` now freezes the forward-looking TRIAGE-BC v0.1 method before fresh final split runs. The freeze fixes the score model, trajectory aggregation, mass estimate, router-v2 thresholds, official BC-RNN-GMM training budget, checkpoint schedule, final split seeds, and 50-episode evaluation protocol. The completed primary frozen Can 40p/80b final split seeds 11, 22, and 33 are directionally positive against weighted BC and pooled all-demo cloning, but not against the strongest no-bad-label control: positive-only NN top40 reaches 0.720, TRIAGE-BC reaches 0.660, weighted BC reaches 0.600, and all-demo BC reaches 0.540 pooled over 150 fixed-20k endpoint rollouts. The completed frozen Lift matrix is a coverage counterexample: weighted BC reaches 0.620, positive-only NN top160 reaches 0.547, TRIAGE-BC reaches 0.493, all-demo BC reaches 0.207, and diagnostic all-positive oracle reaches 0.700. Any future change to those choices should be logged as a new method variant or ablation, not silently substituted into the final claims.
