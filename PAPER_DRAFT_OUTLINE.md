# TRIAGE-BC Paper Draft Outline

Working title:

> When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study

This is a paper-writing scaffold, not a claim expansion. It maps the current frozen evidence into a draft structure and keeps the limitations explicit.

## One-Sentence Thesis

Scarce success and failure labels can learn a useful desirability score over contaminated offline logs, but the decisive problem is converting that score into policy-training support under a precision/coverage tradeoff.

## Claim Contract

Use:

- Mixed offline logs can hurt naive behavior cloning.
- Tri-signal scoring can recover useful hidden-positive support in controlled settings.
- Hard support can beat soft weighting on frozen Can 40p/80b.
- Soft weighting can beat hard support when coverage dominates, as on frozen Lift MG and Can MG stress diagnostics.
- A frozen v0.2 portfolio router passes a fresh Can+Lift gate by selecting hard union on Can and weighted coverage on Lift (`209/300` versus `187/300` best per-split baselines), but paired-bootstrap intervals cross zero and keep the claim directional.
- Strong positive-only retrieval is a first-class baseline and often beats the current bad-aware converter.

Avoid:

- Bad labels are required.
- TRIAGE-BC uniformly beats weighted BC.
- TRIAGE-BC uniformly beats positive-only retrieval.
- The full inverse-Q / Tri-PIQL actor objective is validated on Robomimic.
- Best-checkpoint selection proves the method.

## Abstract Skeleton

Offline imitation datasets often contain a small number of trusted successful demonstrations, a small number of known failures, and a larger unlabeled log with mixed behavior. A common response is to clone all data or softly weight the log with a learned score, but these choices can fail under action-conflicting contamination or coverage-sensitive tasks. We study the score-to-policy conversion problem: how scarce successes and failures should calibrate support selection from a mixed log. TRIAGE-BC learns a tri-signal desirability score, estimates hidden positive mass, and routes between hard support, soft weighting, and abstention. In controlled continuous PointNav, adaptive score-gap support reaches perfect success under extreme contamination. On frozen Robomimic endpoints, v0.1 exposes the precision/coverage tradeoff, and a frozen v0.2 portfolio router reaches `209/300` selected-branch successes versus `187/300` for best per-split baselines on fresh Can+Lift splits. The resulting evidence supports a narrower but useful conclusion: support calibration is the bottleneck, and strong no-bad-label retrieval must be included in this problem class.

## Contributions

1. Formalize offline imitation from scarce positive demonstrations, scarce failure demonstrations, and a contaminated unlabeled log as a score-to-support conversion problem.
2. Propose TRIAGE-BC v0.1 and a frozen v0.2 portfolio router: tri-signal score learning, trajectory-score calibration, positive-mass estimation, hidden-label-free support routing, and BC-RNN-GMM policy learning.
3. Provide controlled PointNav evidence that adaptive score-gap support can solve heavy-contamination settings where all-demo, positive-plus-unlabeled, and local weighted BC degrade.
4. Provide frozen Robomimic evidence showing both sides of the precision/coverage tradeoff: Can 40p/80b favors hard selected support, Lift MG favors broader weighted coverage, and fresh v0.2 branch selection improves the combined Can+Lift gate.
5. Establish strong caveats through positive-only NN, all-positive oracle, score-shape diagnostics, and Can MG branch-proxy failure.

## Recommended Paper Structure

### 1. Introduction

Lead with the data problem: trusted successes and failures are scarce, but offline logs are abundant and contaminated.

Core motivation:

- Cloning everything can imitate harmful modes.
- Weighting everything can still preserve action-conflicting bad behavior.
- Filtering too hard can lose coverage needed by sequence BC.

Suggested final paragraph:

> We show that the central algorithmic question is not only whether a classifier can distinguish good and bad behavior, but how its scores should be converted into the policy-training distribution.

### 2. Related Work

Status: the LaTeX and Markdown drafts now have a concise related-work pass. Keep it organized around:

- Behavior cloning and offline imitation.
- Classical IRL, apprenticeship learning, maximum-entropy IRL, and adversarial imitation.
- Offline RL / CQL / IQL / advantage-weighted imitation.
- Learning from positive/unlabeled or positive/negative data.
- Dataset filtering, data quality, and demonstration selection.
- Robomimic-style sequence imitation backbones.

Important distinction:

> TRIAGE-BC uses scarce positive and failure labels to calibrate the support for a behavior-cloning policy. It is not claiming a validated inverse-Q robotics method, a new Robomimic policy architecture, or a generic trajectory-quality metric.

### 3. Problem Setting

Define:

- `D+`: scarce labeled successful demonstrations.
- `D-`: scarce labeled failed or undesirable demonstrations.
- `Du`: large unlabeled mixed-quality log.
- No online training.
- Hidden labels and task rewards are evaluation-only.

Make the distinction explicit:

- The method can use labels in `D+` and `D-`.
- The method cannot use hidden labels inside `Du`.
- Oracle rows are diagnostics, not deployable methods.

### 4. Method

Describe TRIAGE-BC v0.1 using `METHOD_FREEZE.md` and `configs/final_method.yaml`, then describe the frozen v0.2 portfolio router using `METHOD_FREEZE_V02.md`.

Subsections:

1. State-action desirability classifier.
2. Trajectory score aggregation.
3. Positive-mass estimate from labeled score means.
4. Candidate support converters:
   - adaptive mass-capped hard support,
   - positive-min threshold support,
   - soft weighted sampler,
   - abstention.
5. Frozen router and algorithmic summary.
6. v0.2 portfolio router over hard union, soft weighted BC, and stress abstention.
7. Policy backbone: official Robomimic BC-RNN-GMM for robotics; lightweight BC for controlled PointNav.

Important caveat:

> TRIAGE-BC is currently a score-calibrated imitation method, not a validated inverse-Q actor-extraction method.

### 5. Controlled Mechanism Experiments

Use `results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`.

Primary table/figure:

- `results/final_paper/figures/pointnav_controlled_mechanism.png`
- `results/final_paper/tables/pointnav_controlled_mechanism.csv`

Main result:

- With only 2 positive route-prefix demos and 2 bad shortcut demos, score-gap support reaches `1.000` success at 50/75/90/95% bad unlabeled data.
- Mixed and weighted baselines degrade.
- This is the cleanest evidence that scarce explicit bad labels can calibrate useful support when positives are incomplete prefixes.

Suggested wording:

> The controlled task isolates the mechanism: positive labels alone describe only route prefixes, so successful closed-loop behavior requires recovering hidden-good unlabeled trajectories without admitting shortcut failures.

### 6. Robomimic Main Results

Use `results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md` for the main paper and `results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md` for appendix diagnostics.

Primary figure:

- `results/final_paper/figures/robotics_primary_endpoint_matrix.png`

Primary frozen rows:

- Can 40p/80b, three split seeds, 150 endpoint rollouts.
- Lift MG, three split seeds, 150 endpoint rollouts.
- Descriptive uncertainty: `results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md`.
- Paired initial-state bootstrap audit: `results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md`.

Diagnostic appendix rows:

- Status: included in the standalone LaTeX and Markdown drafts as appendix-only
  diagnostics.
- Can 20p/80b: split-11 endpoint in the diagnostic matrix, plus two-split positive-only versus TRIAGE extension in the ablation report.
- Can 80p/80b: split-33 endpoint plus support audits.
- Can MG: branch-proxy failure, used as abstention evidence.
- Lift MG classifier top160: fixed-top-k rescue failure, used as coverage evidence.

Robotics result paragraph:

> On Can 40p/80b, TRIAGE-BC improves over weighted BC and all-demo cloning at the fixed 20k endpoint, reaching `99/150` successes versus `90/150` and `81/150`. However, positive-only NN top40 reaches `108/150`, so this is not evidence that bad labels are necessary on Can. On Lift MG, contaminated-log cloning is weak (`31/150`), but weighted BC is strongest among non-oracle methods (`93/150`), ahead of positive-only NN (`82/150`) and TRIAGE-BC (`74/150`). This cross-task reversal is the paper's key precision/coverage result.

Uncertainty wording:

> Can 40p/80b favors TRIAGE-BC over weighted BC on every split, but the pooled gap is modest (`+0.060`) and both rollout-level Wilson intervals and paired initial-state bootstrap intervals overlap zero. Lift MG favors weighted BC pooled, but not on every split. We therefore report counts, split context, paired-bootstrap context, and direction of paired split deltas rather than formal significance claims.

### 7. Precision/Coverage Analysis

Status: the LaTeX and Markdown drafts now include both the empirical
precision/coverage analysis and a simple mixture-model risk decomposition.

Use:

- `results/final_paper/figures/can40_precision_coverage.png`
- `results/final_paper/ablations/can40_score_support_tradeoff_REPORT.md`
- `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`

Can 40p/80b:

- TRIAGE adaptive masscap: `110/120` hidden positives, `80/240` hidden bad, endpoint `99/150`.
- Positive-only NN top40: `106/120` hidden positives, `14/240` hidden bad, endpoint `108/150`.
- Weighted full pool: full positive recall and full bad admission, endpoint `90/150`.

Can 20p/80b diagnostic:

- TRIAGE: `54/60` hidden positives, `69/240` hidden bad, completed endpoints `46/100`.
- Positive-only NN top20: `49/60` hidden positives, `11/240` hidden bad, completed endpoints `54/100`.

Interpretation:

> Bad labels improve the score but the current converter can be off the best precision/coverage frontier relative to positive-only retrieval.

Analysis paragraph:

> A hard selector helps when it removes action-conflicting bad support faster than it loses useful state-action coverage. It fails when discarded trajectories contain coverage the sequence policy needs. TRIAGE-BC's mass cap, positive-min branch, and abstention branch are hidden-label-free approximations to this tradeoff, not guarantees of policy optimality.

Theory paragraph:

> Under a mixed unlabeled distribution, support rules trade off hidden-good
> recall against hidden-bad admission. The draft decomposes imitation error into
> a coverage term that shrinks with useful selected mass and a contamination
> term that grows with admitted bad-action mass. The weighted-BC analogue uses
> effective sample size and weighted bad mass. This justifies why hard support,
> soft weighting, and abstention each have a regime instead of treating any one
> converter as universally optimal.

### 8. Score-Shape Diagnostics And Abstention

Use:

- `results/final_paper/figures/score_shape_diagnostics.png`
- `results/final_paper/tables/score_shape_diagnostics_REPORT.md`
- `results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`

Core points:

- Can 40p/80b has score overlap, motivating adaptive masscap.
- Lift MG has strong score separation, but endpoint success still favors weighted coverage.
- Can MG has a high-score plateau, motivating abstention.
- Simple positive/negative likelihood branch proxies fail on Can MG.

Suggested limitation:

> A high-purity support set is not sufficient evidence of policy quality. The policy learner may still need coverage that the hard support converter discards.

### 9. Limitations

List directly:

- Positive-only NN is strongest on frozen Can 40p/80b and Can 20p/80b diagnostics.
- Weighted BC is strongest on frozen Lift MG.
- v0.2 selected weighted BC is only a modest Lift improvement over positive-only NN (`80/150` versus `74/150`) and loses one fresh split.
- Can MG is an abstention/stress diagnostic, not a main success.
- Square and Transport are support-side relative-quality diagnostics, not failure-demo policy benchmarks.
- The robotics method relies on a strong BC-RNN-GMM backbone.
- Full inverse-Q / Tri-PIQL actor extraction remains unvalidated on real robotics.

### 10. Conclusion

Close on the useful narrowed claim:

> The empirical lesson is that tri-signal labels are valuable, but their value is mediated by score-to-support conversion. Future work should treat policy-quality prediction, coverage-aware support selection, and strong positive-only retrieval as central components rather than baselines to be dismissed.

## Figure And Table Map

Status: promoted into `paper/MANUSCRIPT_CHECKLIST.md` with claim, figure,
appendix, validation, and open-decision tracking. Quoted numeric claims and
core overclaim-avoidance caveats are guarded by
`scripts/validate_paper_claim_numbers.py`.

| Slot | Artifact | Role |
|---|---|---|
| Figure 1 | `results/final_paper/figures/triage_bc_method_diagram.png` | TRIAGE-BC pipeline |
| Figure 2 | `results/final_paper/figures/pointnav_controlled_mechanism.png` | Controlled mechanism result |
| Figure 3 | `results/final_paper/figures/robotics_primary_endpoint_matrix.png` | Primary Robomimic endpoint matrix |
| Figure 4 | `results/final_paper/figures/can40_precision_coverage.png` | Precision/coverage frontier |
| Figure 5 | `results/final_paper/figures/score_shape_diagnostics.png` | Score-shape and abstention diagnostic |
| Appendix Figure | `results/final_paper/figures/robotics_current_endpoint_matrix.png` | Diagnostic endpoint matrix |
| Appendix Figure | `results/final_paper/figures/primary_endpoint_paired_deltas.png` | Paired initial-state endpoint uncertainty |
| Appendix Table | `results/final_paper/tables/primary_endpoint_uncertainty.csv` | Primary endpoint uncertainty |
| Appendix Table | `results/final_paper/tables/primary_endpoint_paired_bootstrap.csv` | Paired initial-state bootstrap uncertainty |
| Appendix Table | `results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md` | Fresh v0.2 paired initial-state uncertainty |
| Appendix Table | In-source table `tab:bad-label-controls` backed by `results/final_paper/tables/bad_label_control_summary.csv` | Bad-label versus positive-only control summary in the compiled appendix |
| Appendix Table | `results/final_paper/tables/bad_label_control_summary.csv` | Bad-label versus positive-only control summary |
| Appendix Table | `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split.csv` | Heavy-contamination Can caveat |
| Appendix Table | `results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint.csv` | Balanced Can caveat |
| Appendix Table | `results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary.csv` | Fixed top-k Lift failure |
| Appendix Table | `results/final_paper/ablations/can_mg_branch_proxy_summary/method_proxy_scores.csv` | Branch-proxy failure |

## Main Numbers To Quote

Controlled PointNav:

- Label budget 2/2, score-gap demo BC: `1.000` success at 50/75/90/95% bad unlabeled data.
- Label budget 5/5, score-gap demo BC: `1.000` success at all tested bad fractions.

Can 40p/80b frozen endpoint:

- All-positive oracle: `147/150`.
- Positive-only NN top40: `108/150`.
- TRIAGE-BC: `99/150`.
- Weighted BC: `90/150`.
- All-demo BC: `81/150`.

Lift MG frozen endpoint:

- All-positive oracle: `105/150`.
- Weighted BC: `93/150`.
- Positive-only NN top160: `82/150`.
- TRIAGE-BC: `74/150`.
- All-demo BC: `31/150`.

Can 20p/80b diagnostic:

- Positive-only NN top20: `54/100` over two completed endpoint splits.
- TRIAGE-BC: `46/100` over the same two endpoint splits.
- Weighted BC: `18/50` on split 11 only.

Can 80p/80b diagnostic:

- Positive-only NN top80: `49/50` on split 33.
- TRIAGE-BC: `43/50` on split 33.

Can MG stress:

- Weighted BC: `0.333` fixed-20k mean.
- All-positive support: `0.200`.
- Pos-p10 hard support: `0.167`.
- All-demo cloning: `0.100`.

## Open Decisions Before Submission

1. Whether Can 20p/80b split-33 endpoint is worth the compute. Current split-22 extension already strengthens the positive-only caveat.
2. Square/Transport are repository-only diagnostics for now; include them in a venue appendix only if a later draft needs support-side relative-quality examples.
3. Confirm the final venue/year. A provisional ICLR 2026 shell now exists, but
   the style files should be refreshed if the target changes.

## Immediate Writing Tasks

1. Polish the current ICLR-format draft for space and readability.
2. Add venue-specific statistical tests only if the target venue expects them.

Result ordering is frozen for submission formatting: PointNav-first mechanism
evidence, then Robomimic endpoint evidence and caveats. The provisional ICLR
compile is 15 pages total, with references on page 10 and appendix material
starting on page 11.
