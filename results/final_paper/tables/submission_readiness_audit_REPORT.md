# Submission Readiness Audit

Generated from staged final-paper artifacts. This audit is an evidence-accounting table, not a new experiment.

## Summary

- High-quality empirical submission criteria: 6 pass, 0 caution.
- Top-tier methods/SOTA dominance criteria: 1 caution, 4 not met.
- Recommended posture: submit as a careful precision/coverage empirical study with a cautious v0.2 portfolio-router method component.

## Criteria

| required for | status | criterion | evidence | decision |
|---|---|---|---|---|
| high_quality_empirical_submission | Pass | Frozen v0.2 fresh gate is complete and documented. | Combined selected 340/500 versus best baselines 338/500; Can 197/250 versus 192/250; Lift 143/250 versus 146/250. | Use as cautious portfolio-router evidence, not a decisive win. |
| high_quality_empirical_submission | Pass | Generated regime probes are formalized and separated from default benchmark rows. | Hard-negative Can 104/150 vs 91/150; Coverage-shift Can 120/150 vs 103/150; Prefix-positive Can 119/150 vs 6/150 | Keep as mechanism diagnostics and cite REGIME_PROBE_SUITE.md for allowed claims. |
| high_quality_empirical_submission | Pass | Strong baselines are included in the primary Can/Lift evidence package and the fresh branch-selection audit. | Primary matrix includes all-demo, positive-only NN, weighted BC, TRIAGE-BC, and oracle rows for Can and Lift; fresh branch-selection required rows are 7/7 complete, with optional all-demo/all-positive diagnostic rows 0/4 run. | Primary baselines are complete; the v0.2 fresh gate is a complete selected-vs-strong-baseline/v0.1 audit, while all-demo/all-positive fresh rows remain optional diagnostics. |
| high_quality_empirical_submission | Pass | Uncertainty is reported without overclaiming significance. | Primary intervals cross zero: True; v0.2 intervals cross zero: True; combined v0.2 interval [-0.074, 0.120]. | Report counts, split signs, and bootstrap context; do not claim formal significance. |
| high_quality_empirical_submission | Pass | Title, abstract, and claim handoff emphasize when bad demos help instead of universal dominance. | Final claim contract and reviewer-facing summary are staged and validator-covered. | Use precision/coverage framing as the submission spine. |
| high_quality_empirical_submission | Pass | Reproducibility scripts validate quoted numbers and artifact references. | make -C paper validate regenerates paper artifacts, compiles both PDFs, and runs claim, structure, and artifact validators. | Keep this as the required pre-submission gate. |
| top_tier_methods_dominance | Not met | v0.2 beats every fixed branch across multiple regimes with stable margins. | v0.2 regret is 23/500 on completed Can+Lift rows, while always-hard support also has regret 23 in the router-regret table. | Do not frame as methods/SOTA dominance. |
| top_tier_methods_dominance | Not met | v0.2 fresh gate remains positive over five or more split seeds with intervals mostly above zero. | Combined selected margin is 0.004 with paired-bootstrap interval [-0.074, 0.120]. | Keep v0.2 as directional branch-selection evidence. |
| top_tier_methods_dominance | Not met | The latest candidate-breakthrough search validates a general method beyond scoped Can discovery. | Candidate F 198/250 vs positive 174/250, weighted 158/250, triage 171/250, per-split oracle 192/250; Candidate F 31/40 ties positive-only 31/40; weighted is 29/40; Candidate F 81/100 vs best completed baselines 84/100; worse on 2/2 completed validation rows, while the 4/5 no-worse gate allows at most 1; Can-style Candidate F transfer 145/250 vs Lift oracle 154/250; tail-severity diagnostic 154/250 is not frozen; Can404 sequence-mask 16/20 and best negative-action hinge 14/20 remain below positive-only 17/20; Best Can404 first-20 output-anchor checkpoint 18/20 vs positive-only 17/20; Can404 50-episode check 39/50 ties positive-only 39/50; frozen Can505 check 38/50 vs positive-only 40/50; Candidate W 85/100 ties Candidate E 85/100 over splits 404+505; split404 46/50 but split505 39/50 vs positive-only 40/50. | Candidate F failed its predeclared fresh Can validation gate early, and later transition/object-anchor/router follow-ups also failed validation; keep them as scoped discovery / failed-development evidence. |
| top_tier_methods_dominance | Caution | A second non-Can task family shows a bad-label endpoint benefit over positive-only retrieval. | Lift hard-negative splits 101,202,303 are 15/150 versus 5/150; the directional non-Can effect is complete, but absolute success remains low. | Use as exploratory C1 mechanism evidence, not as primary endpoint dominance. |
| top_tier_methods_dominance | Not met | A hidden-label-free policy-quality proxy predicts hard-versus-soft winners better than mass/count heuristics. | Consolidated proxy no-go table shows deployable proxy attempts match endpoint winners in only 2/11 rows. | Keep policy-quality prediction as an open problem and abstention as risk control. |

## Outputs

- `results/final_paper/tables/submission_readiness_audit.csv`
- `results/final_paper/tables/submission_readiness_audit_REPORT.md`
