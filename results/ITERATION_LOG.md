# Tri-PIQL Iteration Log

## 2026-06-26: ICLR claim wording and layout sync

Implemented:

- Updated `paper/iclr2026/main.tex` so the provisional ICLR abstract states the
  fresh v0.2 gate as barely positive overall: Can `197/250` versus `192/250`,
  Lift `143/250` versus `146/250`, and combined `340/500` versus `338/500`.
- Tightened the ICLR introduction and fresh-gate paragraph to mention the
  severe split-404 Can reversal and to frame the result as branch selection,
  not universal hard-support dominance.
- Compressed ICLR-only related-work prose after validation showed the first
  wording pass pushed the provisional ICLR PDF from 15 to 16 pages.

Validation:

- The first `make -C paper validate` run correctly failed on ICLR layout:
  `main.pdf` became 16 pages and the references/appendix page-boundary checks
  moved.
- After compression, `make -C paper validate` passed, rebuilding both PDFs,
  restoring the ICLR PDF to 15 pages, checking `134` unique artifact references,
  and validating `METHOD_FREEZE_V02`.
- `python scripts/validate_paper_claim_numbers.py` and `git diff --check`
  passed before the full validation rerun.

Interpretation:

- The provisional venue source now carries the same cautious fresh-gate
  semantics as the standalone paper while preserving the validated ICLR layout
  envelope.

## 2026-06-26: Can hard-support claim-boundary tightening

Implemented:

- Tightened the standalone manuscript, Markdown scaffold, and outline so the
  Can 40p/80b contribution says hard selected support beats weighted and
  all-demo controls, while positive-only retrieval remains stronger on Can.
- Added a stale-claim guard to `scripts/validate_paper_claim_numbers.py` so the
  older unqualified phrase "Can 40p/80b favors hard selected support" fails the
  current claim validator.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed after adding the new
  stale-claim guard.
- `make -C paper validate` passed, rebuilding the standalone and ICLR PDFs,
  checking `134` unique artifact references, and validating
  `METHOD_FREEZE_V02`.
- `git diff --check` passed.

Interpretation:

- The contribution wording now matches the final claim contract more closely:
  the Can evidence supports a hard-over-weighted/control result, not a broad
  claim that hard support is the best Can converter against positive-only
  retrieval.

## 2026-06-26: Reproduction command scope sync

Implemented:

- Updated `paper/REPRODUCE_PAPER.md` so the documented coverage-shift per-split
  regeneration commands use the completed-diagnostic wording already used by
  `paper/Makefile`.
- Added `paper/REPRODUCE_PAPER.md` to the guarded document set in
  `scripts/validate_paper_claim_numbers.py`, so stale reproduction-command
  wording such as "until the multi-split check is run" now fails the claim
  validator.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed with the reproduction
  checklist included in the guarded surface.
- `make -C paper validate` passed, rebuilding the standalone and ICLR PDFs,
  checking `134` unique artifact references, and validating `METHOD_FREEZE_V02`.
- A focused stale scan over the reproduction checklist, Makefile, claim package,
  outline, manuscript, checklist, final claim contract, reviewer summary, and
  top-tier plan found no old coverage-shift or fresh-gate overclaim wording.
- `git diff --check` passed, and no Robomimic train/eval jobs were running.

Interpretation:

- The documented reproduction path now matches the current completed
  coverage-shift diagnostic evidence, reducing the risk that users regenerate
  old-scope reports during submission prep.

## 2026-06-26: Claim-package non-Can C1 refresh

Implemented:

- Updated `results/PAPER_CLAIM_PACKAGE.md` from the stale split-101-only Lift
  hard-negative endpoint note to the completed split-101/202/303 aggregate:
  bad-aware proxy top40 `15/150` versus state-action positive-NN top40 `5/150`,
  with 82 hidden positives and 38 hidden bad selected versus 12 hidden positives
  and 108 hidden bad.
- Reframed the claim package bottom line so frozen v0.2 is a barely positive
  selected-vs-baseline Can+Lift gate that ties the completed always-hard-support
  branch, not a dominance result.
- Tightened `PAPER_DRAFT_OUTLINE.md` so the contribution sentence says fresh
  v0.2 branch selection is barely positive rather than unqualified improvement.
- Updated `paper/Makefile` report-generation commands so per-split Lift
  hard-negative and Can coverage-shift reports regenerate with completed
  diagnostic framing instead of stale "remaining splits" language.
- Extended `scripts/validate_paper_claim_numbers.py` to include
  `results/PAPER_CLAIM_PACKAGE.md` and `paper/Makefile` in the stale-claim
  surface, rejecting old C1 split-101-only and unqualified fresh-gate wording.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed with the claim package
  and Makefile included in the guarded document set.
- `make -C paper validate` passed after regenerating the affected reports,
  rebuilding the standalone and ICLR PDFs, checking `134` unique artifact
  references, and validating `METHOD_FREEZE_V02`.
- A focused stale scan over the claim package, outline, Makefile, generated
  Lift hard-negative reports, generated coverage-shift reports, manuscript, and
  reviewer handoff surfaces found no old split-101-only or unqualified
  fresh-gate wording.
- `git diff --check` passed, and no Robomimic train/eval jobs were running.

Interpretation:

- The durable claim package now matches the current evidence: non-Can C1 is
  completed but low-success exploratory mechanism evidence, while the submission
  spine remains a careful precision/coverage empirical study.

## 2026-06-26: Top-tier plan five-split refresh

Implemented:

- Refreshed `triage_bc_top_tier_completion_plan.md` so the strategic plan
  reflects the completed five-split v0.2 fresh gate rather than the earlier
  three-split weakness.
- Tightened the plan's method-evidence language: v0.2 is now described as
  barely positive branch-selection evidence that reduces regret versus
  positive-only and weighted fixed branches, ties the completed always-hard
  branch on Can+Lift, and should not be framed as fixed-branch dominance.
- Updated the A1 and Week-2 sections to mark the fresh-gate extension complete
  and to route any further GPU budget toward optional all-demo/all-positive
  diagnostics, stronger non-Can endpoint evidence, or better policy-quality
  proxies.
- Extended `scripts/validate_paper_claim_numbers.py` so it validates the
  top-tier plan alongside the manuscript/checklist/handoff docs and rejects
  stale plan wording about "only three split seeds" or v0.2 beating the best
  fixed branch.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed with the top-tier
  plan included in the guarded document set.
- `make -C paper validate` passed, rebuilding the standalone and ICLR PDFs,
  checking `134` unique artifact references, and validating `METHOD_FREEZE_V02`.
- A focused stale-plan scan found no remaining old three-split or unqualified
  fresh-gate improvement wording in the current paper-facing surfaces.

Interpretation:

- The plan now matches the current submission decision: the project is ready to
  pursue a careful top-tier empirical-study submission, but not a methods/SOTA
  dominance claim without new evidence.

## 2026-06-26: Reviewer claim handoff tightening

Implemented:

- Tightened `paper/REVIEWER_CLAIM_SUMMARY.md` and `FINAL_CLAIM_CONTRACT.md`
  so the handoff docs match the manuscript caveats: v0.2 is barely positive,
  the fresh gate is a selected-vs-strong-baseline/v0.1 audit, optional fresh
  all-demo/all-positive diagnostics remain unrun, and no complete fresh SOTA
  leaderboard is implied.
- Added validator checks in `scripts/validate_paper_claim_numbers.py` requiring
  the reviewer summary and final claim contract to include the "barely
  positive" and "fresh all-demo/all-positive diagnostic" caveats.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed.
- `make -C paper validate` passed, rebuilding the standalone and ICLR PDFs,
  checking `134` unique artifact references, and validating `METHOD_FREEZE_V02`.
- A stale-claim scan over the manuscript and reviewer handoff surfaces found no
  old fresh-gate/Lift-overclaim wording.
- `git diff --check` passed, and no Robomimic train/eval jobs were running.

Interpretation:

- This aligns the one-page reviewer handoff and final claim contract with the
  manuscript, reducing risk that submission prep overstates the v0.2 gate.

## 2026-06-26: Router-regret reproduction coverage

Implemented:

- Promoted the v0.2 router-regret table to a first-class reproduction artifact
  in `paper/REPRODUCE_PAPER.md`.
- Added `scripts/summarize_v02_router_regret_table.py` to the cheap
  regeneration and expanded manual command lists in `paper/REPRODUCE_PAPER.md`
  and `paper/README.md`.
- Added the `v02_router_regret_REPORT.md` artifact-map row to
  `scripts/validate_paper_structure.py` so the reproduction map now guards the
  router-regret report alongside the fresh-gate, uncertainty, baseline
  coverage, and router-support reports.
- Updated the current expected artifact-reference count in
  `paper/REPRODUCE_PAPER.md` and `paper/MANUSCRIPT_CHECKLIST.md` from `133` to
  `134`.

Validation:

- `python scripts/validate_paper_structure.py` passed.
- `python scripts/validate_paper_artifact_refs.py` passed with `134` unique
  artifact references.
- `make -C paper validate` passed, regenerating the router-regret table and
  preserving the paper claim, structure, artifact-reference, and
  method-freeze gates.

Interpretation:

- This closes a reproducibility gap around the A2 portfolio-regret evidence:
  readers can now regenerate the central router-regret artifact through the
  documented cheap path, and the validator will catch future omissions.

## 2026-06-26: Manuscript reviewer-scope tightening

Implemented:

- Tightened the Discussion/Limitations and Conclusion text in
  `paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
  `paper/triage_bc_draft.md`.
- Reframed the final v0.2 wording from an unqualified fresh-gate improvement
  to a barely positive portfolio result: Can is positive, Lift is negative
  against the completed per-split baseline, and combined Can+Lift is only
  `340/500` versus `338/500`.
- Added explicit reviewer-facing caveats that generated split constructions
  are not intended to replace default benchmark rows and that optional fresh
  all-demo/all-positive diagnostics remain unrun.
- Extended `scripts/validate_paper_claim_numbers.py` to reject unqualified
  "portfolio router can improve a fresh Can+Lift gate" wording and to require
  the barely-positive, generated-probe-boundary, and optional-diagnostics
  caveats in the manuscript surfaces.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed after the new
  validator guards.
- `make -C paper validate` passed, rebuilding the standalone and ICLR PDFs,
  preserving the 18-page standalone and 15-page ICLR layouts, checking 133
  unique artifact references, and validating `METHOD_FREEZE_V02`.

Interpretation:

- This pass improves top-tier reviewer posture without adding a new experiment:
  the manuscript now makes the empirical-study framing harder to misread as a
  methods/SOTA dominance claim.

## 2026-06-26: Fresh v0.2 claim-tightening guard

Implemented:

- Tightened the paper abstract wording in `paper/triage_bc_paper.tex`,
  `paper/iclr2026/main.tex`, and `paper/triage_bc_draft.md` so fresh v0.2 is
  described as Can-positive but Lift-negative against the completed per-split
  baseline, not as a Lift improvement.
- Updated `results/final_paper_v02/README.md` to include the completed fresh
  Lift v0.1 hard-support audit rows and to report the current Lift baseline
  total `146/250` and combined fresh-gate baseline total `338/500`.
- Added stale-claim guards to `scripts/validate_paper_claim_numbers.py` for
  the old `340/500` versus `317/500` fresh-gate wording, the stale `125/250`
  Lift baseline total, and Lift-improvement phrases.
- Refreshed the documented artifact-reference count from `131` to `133` in
  the paper checklist and reproduction notes.

Result:

- The current claim boundary is now more explicit: fresh v0.2 selected rows
  are `340/500` versus `338/500` overall, with Can positive at `197/250`
  versus `192/250` and Lift negative at `143/250` versus `146/250`.
- The validator now fails if current paper-facing docs reintroduce the stale
  three-split fresh-gate baseline or claim that fresh Lift improved.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed.
- `make -C paper validate` passed, rebuilding both PDFs, checking claim
  numbers, checking 133 unique artifact references, validating paper structure,
  and validating `METHOD_FREEZE_V02` against the router code and staged
  artifacts.

## 2026-06-26: Fresh v0.2 baseline coverage audit

Implemented:

- Added `scripts/summarize_v02_fresh_baseline_coverage.py`.
- Generated
  `results/final_paper_v02/tables/v02_fresh_baseline_coverage.csv` and
  `results/final_paper_v02/tables/v02_fresh_baseline_coverage_REPORT.md`.
- Wired the new generator into `make -C paper validate`, `paper/README.md`,
  `paper/REPRODUCE_PAPER.md`, `paper/MANUSCRIPT_CHECKLIST.md`, and
  `scripts/validate_paper_structure.py`.
- Fixed stale v0.2 fresh-gate numbers in `results/final_paper/README.md`
  from the old three-split gate to the current five-split gate.
- Updated `results/final_paper_v02/README.md` and
  `triage_bc_top_tier_completion_plan.md` to point to the coverage audit.

Result:

- Required fresh-gate branch-selection rows are now explicitly audited as
  `7/7` complete: Can selected hard union, Can positive-only NN, Can weighted
  BC, Can v0.1 TRIAGE-BC, Lift selected weighted BC, Lift positive-only NN,
  and Lift v0.1 TRIAGE-BC.
- Optional fresh-gate diagnostic rows are explicitly audited as `0/4` run:
  Can all-demo, Can all-positive oracle, Lift all-demo, and Lift all-positive
  oracle.
- This supports the current claim boundary: the fresh v0.2 artifact is a
  complete selected-vs-strong-baseline/v0.1 branch-selection audit, not a full
  SOTA leaderboard with every diagnostic control.

Validation:

- `make -C paper validate` passed after regenerating the v0.2 Can, Lift, gate,
  uncertainty, baseline-coverage, router-regret, and readiness artifacts.
- The validation rebuilt both PDFs, checked paper claim numbers, checked 133
  unique artifact references, validated structure, and validated
  `METHOD_FREEZE_V02` against the v0.2 router code and staged artifacts.

Interpretation:

- This was the highest-return no-GPU follow-up after closing A3: it prevents
  the paper package from over-implying completed all-demo/all-positive fresh
  diagnostics while making the completed branch-selection evidence easier to
  defend to reviewers.

## 2026-06-26: A3 fresh Can v0.1 split404/505 completion

Environment:

- Used the `tri-piql` conda environment with GPU/MuJoCo flags:
  `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`.
- Ran each remaining split as train first, then epoch-200-only evaluation on
  50 validation-positive Can starts.

Commands:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 404 \
  --method triage_bc \
  --policy-seed 0 \
  --stage train \
  --device cuda
```

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 404 \
  --method triage_bc \
  --policy-seed 0 \
  --stage eval \
  --eval-episodes 50 \
  --device cuda \
  --checkpoint results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_triage_bc_policy0/train/can_paired_pos40_bad80_split404_triage_bc_policy0_official_bc_rnn/20260625213341/models/model_epoch_200.pth
```

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 505 \
  --method triage_bc \
  --policy-seed 0 \
  --stage train \
  --device cuda
```

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 505 \
  --method triage_bc \
  --policy-seed 0 \
  --stage eval \
  --eval-episodes 50 \
  --device cuda \
  --checkpoint results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_triage_bc_policy0/train/can_paired_pos40_bad80_split505_triage_bc_policy0_official_bc_rnn/20260625214146/models/model_epoch_200.pth
```

Implemented:

- Completed the final two A3 fresh Can v0.1 TRIAGE-BC endpoint cells.
- Trained splits `404` and `505` official Robomimic BC-RNN-GMM policies for
  200 epochs each.
- Evaluated only `model_epoch_200.pth` for each split on 50
  validation-positive Can starts.
- Regenerated `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
  and `results/final_paper_v02/tables/v02_router_regret_REPORT.md`.
- Fixed `scripts/summarize_v02_router_regret_table.py` so the generated report
  says fresh Can v0.1 is complete when all current split seeds are present.
- Updated `results/final_paper_v02/README.md` and
  `triage_bc_top_tier_completion_plan.md` to move fresh Can v0.1 from partial
  to complete.

Result:

- Split `404` v0.1 TRIAGE-BC epoch-200 endpoint: `36/50` success, average
  length `190.8`.
- Split `505` v0.1 TRIAGE-BC epoch-200 endpoint: `36/50` success, average
  length `185.8`.
- Fresh Can v0.1 is now complete across splits `101/202/303/404/505`:
  `28/50`, `36/50`, `35/50`, `36/50`, and `36/50`, for `171/250`.
- On completed Can rows, v0.1 is below v0.2 hard union `197/250` and
  positive-only NN `174/250`, but above weighted BC `158/250`.
- Router-regret now records v0.1 Can as a complete row with regret `38/250`;
  combined completed v0.1 Can/Lift cells are `314/500` with regret `49/500`.

Validation:

- `make -C paper validate` passed after regenerating the v0.2 Can, gate,
  uncertainty, router-regret, and readiness artifacts.
- The validation rebuilt both PDFs, checked paper claim numbers, checked 131
  unique artifact references, validated structure, and validated
  `METHOD_FREEZE_V02` against the v0.2 router code and staged artifacts.
- `results/final_paper_v02/tables/v02_router_regret_REPORT.md` now records
  fresh Can v0.1 as a complete five-split row.

Interpretation:

- Completing A3 removes the reviewer objection that the v0.1 Can fixed branch
  was missing from the fresh five-split comparison.
- The completed row supports the current framing: v0.2 is the stronger Can
  hard-support branch overall, while v0.1 is not a hidden stronger baseline.
  Split `404` remains the main caveat because v0.1 beats the v0.2 selected row
  there (`36/50` versus `27/50`) but still trails positive-only NN (`39/50`).

## 2026-06-26: A3 fresh Can v0.1 split303 endpoint

Environment:

- Used the `tri-piql` conda environment with GPU/MuJoCo flags:
  `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`.
- Continued the bounded A3 pattern: train only, then evaluate only the
  epoch-200 checkpoint on 50 validation-positive Can starts.

Commands:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 303 \
  --method triage_bc \
  --policy-seed 0 \
  --stage train \
  --device cuda
```

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 303 \
  --method triage_bc \
  --policy-seed 0 \
  --stage eval \
  --eval-episodes 50 \
  --device cuda \
  --checkpoint results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_triage_bc_policy0/train/can_paired_pos40_bad80_split303_triage_bc_policy0_official_bc_rnn/20260625212246/models/model_epoch_200.pth
```

Implemented:

- Completed the third A3 fresh Can v0.1 TRIAGE-BC endpoint cell.
- Trained split `303` official Robomimic BC-RNN-GMM for 200 epochs.
- Evaluated only `model_epoch_200.pth` on 50 validation-positive Can starts.
- Regenerated `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
  and `results/final_paper_v02/tables/v02_router_regret_REPORT.md`.
- Updated `results/final_paper_v02/README.md` and
  `triage_bc_top_tier_completion_plan.md` so A2/A3 now report fresh Can v0.1
  as split `101/202/303` partial.

Result:

- Split `303` v0.1 TRIAGE-BC epoch-200 endpoint: `35/50` success, average
  length `192.9`.
- This is below split-303 v0.2 hard union `39/50` and positive-only NN `36/50`,
  but above weighted BC `25/50`.
- At the time of this split-303 entry, router-regret recorded the fresh Can
  v0.1 partial row as `99/150` with regret `30/150`; combined completed v0.1
  Can/Lift cells were `242/400` with regret `41/400`. The split-404/505
  completion entry above supersedes this partial aggregate.
- At the time of this entry, remaining A3 fresh Can v0.1 endpoint gaps were
  split seeds `404` and `505`; the newest completion entry above closes them.

Validation:

- `make -C paper validate` passed after regenerating the v0.2 Can, gate,
  uncertainty, router-regret, and readiness artifacts.
- The validation rebuilt both PDFs, checked paper claim numbers, checked 131
  unique artifact references, validated structure, and validated
  `METHOD_FREEZE_V02` against the v0.2 router code and staged artifacts.
- At the time of this entry,
  `results/final_paper_v02/tables/v02_router_regret_REPORT.md` recorded fresh
  Can v0.1 as split `101/202/303` partial and pointed to split `404/505` as
  the remaining A3 gaps. The newest completion entry above supersedes that
  partial report.

Interpretation:

- Split `303` is close to positive-only NN but still loses by `1/50`; v0.2 hard
  union remains the best completed split-303 row.
- At this point in the audit, the three completed Can v0.1 splits reinforced
  the paper framing that v0.2 improves the hard-support branch over the older
  v0.1 converter on Can. The split-404/505 completion above gives the current
  five-split read.

## 2026-06-26: A3 fresh Can v0.1 split202 endpoint

Environment:

- Used the `tri-piql` conda environment with GPU/MuJoCo flags:
  `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`.
- Ran the job as train first, then epoch-200-only evaluation to avoid the
  unnecessary four-checkpoint sweep used by the split-101 run.

Commands:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 202 \
  --method triage_bc \
  --policy-seed 0 \
  --stage train \
  --device cuda
```

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 202 \
  --method triage_bc \
  --policy-seed 0 \
  --stage eval \
  --eval-episodes 50 \
  --device cuda \
  --checkpoint results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_triage_bc_policy0/train/can_paired_pos40_bad80_split202_triage_bc_policy0_official_bc_rnn/20260625211012/models/model_epoch_200.pth
```

Implemented:

- Completed the second missing A3 fresh Can v0.1 TRIAGE-BC endpoint cell.
- Trained split `202` official Robomimic BC-RNN-GMM for 200 epochs.
- Evaluated only `model_epoch_200.pth` on 50 validation-positive Can starts.
- Regenerated `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
  and `results/final_paper_v02/tables/v02_router_regret_REPORT.md`.
- Updated `results/final_paper_v02/README.md` and
  `triage_bc_top_tier_completion_plan.md` so A2/A3 now report fresh Can v0.1
  as split `101/202` partial rather than split `101` only.

Result:

- Split `202` v0.1 TRIAGE-BC epoch-200 endpoint: `36/50` success, average
  length `190.9`.
- This is below split-202 positive-only NN `40/50` and v0.2 hard union `45/50`,
  but above weighted BC `33/50`.
- Router-regret now records the fresh Can v0.1 partial row as `64/100` with
  regret `26/100`; combined completed v0.1 Can/Lift cells are `207/350` with
  regret `37/350`.
- Remaining A3 fresh Can v0.1 endpoint gaps are split seeds `303`, `404`, and
  `505`.

Validation:

- `make -C paper validate` passed after regenerating the v0.2 Can, gate,
  uncertainty, router-regret, and readiness artifacts.
- The validation rebuilt both PDFs, checked paper claim numbers, checked 131
  unique artifact references, validated structure, and validated
  `METHOD_FREEZE_V02` against the v0.2 router code and staged artifacts.
- `results/final_paper_v02/tables/v02_router_regret_REPORT.md` now records
  fresh Can v0.1 as split `101/202` partial and points to split `303/404/505`
  as the remaining A3 gaps.

Interpretation:

- Split `202` is less unfavorable to v0.1 than split `101`, but v0.2 hard union
  still has the best completed split-202 endpoint row.
- The partial A3 trend remains consistent with the current paper framing:
  v0.2 improves the Can hard-support branch over the older v0.1 converter, but
  the fixed-branch leaderboard remains incomplete until splits `303`, `404`,
  and `505` are run.

## 2026-06-26: A3 fresh Can v0.1 split101 endpoint

Environment:

- Used the `tri-piql` conda environment with GPU/MuJoCo flags:
  `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`.
- No other matching Robomimic training/evaluation processes were active before
  launching the run.

Command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --out-dir results/final_paper_v02 \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 101 \
  --method triage_bc \
  --policy-seed 0 \
  --stage all \
  --eval-episodes 50 \
  --device cuda
```

Implemented:

- Completed the first missing A3 fresh Can v0.1 TRIAGE-BC endpoint cell.
- Reused the prepared split-101 setup under
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_triage_bc_policy0`.
- Trained official Robomimic BC-RNN-GMM for 200 epochs and evaluated the saved
  epoch 50/100/150/200 checkpoints on 50 validation-positive Can starts.
- Regenerated `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
  and `results/final_paper_v02/tables/v02_router_regret_REPORT.md`.
- Updated `results/final_paper_v02/README.md`,
  `scripts/summarize_v02_router_regret_table.py`, and
  `triage_bc_top_tier_completion_plan.md` so the A2/A3 handoff reports fresh
  Can v0.1 as partial rather than not run.

Result:

- Split `101` v0.1 TRIAGE-BC endpoint checkpoint sweep:
  epoch 50 `6/50`, epoch 100 `29/50`, epoch 150 `28/50`, epoch 200 `28/50`.
- The final-matrix epoch-200 row is `28/50`, below split-101 weighted BC
  `37/50` and v0.2 hard union `45/50`.
- At the time of this split-101 entry, router-regret recorded v0.1 TRIAGE-BC as
  a partial Can row: `28/50` with regret `17/50`; combined completed v0.1
  Can/Lift cells were `171/300`, with 28/300 regret. The split-202 entry above
  supersedes this partial aggregate.
- At the time of this entry, remaining A3 fresh Can v0.1 endpoint gaps were
  split seeds `202`, `303`, `404`, and `505`; the current remaining gaps are
  tracked by the newest A3 entry above.

Validation:

- `make -C paper validate` passed after regenerating the v0.2 Can, gate,
  uncertainty, router-regret, and readiness artifacts.
- `results/final_paper_v02/tables/v02_router_regret_REPORT.md` now states that
  fresh Can v0.1 is partial and points to the per-regime CSV for missing seeds.
- No active `run_final_matrix`, Robomimic training, weighted-sampler training,
  or official-policy evaluation processes remained after the run.

Interpretation:

- This strengthens the fixed-branch audit by replacing one `not_run` v0.1 Can
  cell with endpoint evidence.
- The result is not favorable to v0.1 hard support on split `101`; it supports
  the paper's current story that v0.2's hard union is an improvement over the
  older v0.1 converter on Can, while the A3 leaderboard is still incomplete.

## 2026-06-26: Lift hard-negative manuscript synchronization

Environment:

- No GPU or training used.
- This was a paper-package synchronization pass after the completed Lift
  hard-negative split-303 endpoint run.

Implemented:

- Updated `paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
  `paper/triage_bc_draft.md` so the appendix no longer calls Hard-negative Lift
  a support-only diagnostic.
- The manuscript now reports the completed three-split endpoint read:
  `15/150` for bad-aware proxy top40 versus `5/150` for state-action
  positive-NN top40.
- Added the Lift endpoint report path to the manuscript artifact maps:
  `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.
- Compacted the ICLR artifact map and Lift endpoint wording so
  `paper/iclr2026/main.pdf` stays at the expected 15 pages while retaining both
  denominator-qualified and aggregate Lift support counts.
- Strengthened `scripts/validate_paper_claim_numbers.py` so the Lift
  hard-negative endpoint numbers are checked against the LaTeX sources,
  ICLR source, markdown draft, checklist, outline, reviewer summary, and final
  claim contract.

Validation:

- `make -C paper validate` passed, including PDF rebuilds, claim-number checks,
  structure/page-count checks, artifact reference checks, and method-freeze
  checks.
- `python scripts/validate_paper_claim_numbers.py` passed.
- `python scripts/validate_paper_structure.py` passed.
- `python scripts/validate_paper_artifact_refs.py` checked 131 unique artifact
  references.
- `python scripts/validate_method_freeze_v02.py` passed.
- `git diff --check` passed.
- No active `run_final_matrix`, Robomimic training, weighted-sampler training,
  or official-policy evaluation processes were found.

Interpretation:

- This does not add new endpoint evidence; it closes a paper-facing consistency
  gap. The submitted manuscript now matches the completed non-Can Lift endpoint
  artifact while preserving the low-success exploratory framing.

## 2026-06-25: Lift hard-negative split303 endpoint completion

Environment:

- Used the `tri-piql` conda environment with GPU/MuJoCo flags:
  `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`.
- Robomimic official BC-RNN-GMM endpoint budget: 200 epochs, 100 gradient steps
  per epoch, 50 valid-positive Lift starts, horizon 150.

Implemented:

- Trained split `303` `state_action_positive_nn_top40` and
  `bad_aware_proxy_top40` to `model_epoch_200.pth`.
- Evaluated both split `303` checkpoints with
  `scripts/evaluate_robomimic_official_policy.py`.
- Regenerated split `303` and parent three-split Lift hard-negative endpoint
  reports under `results/final_paper/ablations/lift_hard_negative_endpoint_200ep`.
- Updated the C1 claim package, readiness audit, paper Makefile, and validators
  from the previous two-split status to the completed three-split status.

Result:

- Split `303`: `bad_aware_proxy_top40` reached `2/50`; the positive-NN support
  baseline reached `1/50`.
- Split `101/202/303` aggregate: `bad_aware_proxy_top40` reached `15/150` with
  `82` hidden positives and `38` hidden bad demos selected; positive-NN reached
  `5/150` with `12` hidden positives and `108` hidden bad demos selected.
- The submission-readiness audit now marks the second non-Can task criterion as
  `Caution`: the directional effect is complete, but absolute success remains
  low.

Validation:

- `python scripts/validate_paper_claim_numbers.py` passed.
- `python scripts/validate_paper_structure.py` passed.
- `python scripts/validate_paper_artifact_refs.py` checked 131 unique artifact
  references.
- `python scripts/validate_method_freeze_v02.py` passed.

Interpretation:

- This completes the planned three-split non-Can Lift hard-negative endpoint
  gate and strengthens the mechanism story beyond Can.
- It still does not justify a primary non-Can endpoint or methods-dominance
  claim because the absolute success rate is only `15/150` versus `5/150`.

## 2026-06-25: Lift hard-negative split202 endpoint extension

Environment:

- Used the `tri-piql` conda environment with GPU/MuJoCo flags:
  `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`.
- Robomimic official BC-RNN-GMM endpoint budget: 200 epochs, 100 gradient steps
  per epoch, 50 valid-positive Lift starts, horizon 150.

Implemented:

- Generated Lift hard-negative endpoint configs for split seeds `202` and
  `303` under `results/final_paper/ablations/lift_hard_negative_endpoint_200ep`.
- Parallel HDF5 mask-writing prep hit a file-lock error on split `202`; reran
  split `202` sequentially and left the successful split `303` setup staged.
- Trained split `202` `state_action_positive_nn_top40` and
  `bad_aware_proxy_top40` to `model_epoch_200.pth`.
- Evaluated both split `202` checkpoints with
  `scripts/evaluate_robomimic_official_policy.py`.
- Added a parent two-split Lift endpoint aggregate report at
  `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.

Result:

- Split `202`: `bad_aware_proxy_top40` reached `6/50`; the positive-NN support
  baseline reached `1/50`.
- Split `101/202` aggregate: `bad_aware_proxy_top40` reached `13/100` with
  `59` hidden positives and `21` hidden bad demos selected; positive-NN reached
  `4/100` with `7` hidden positives and `73` hidden bad demos selected.

Validation:

- `make -C paper validate` passed end to end.
- The gate regenerated the paper artifact stack, rebuilt both PDFs, validated
  claim numbers and structure, checked 131 unique artifact references, passed
  the v0.2 method-freeze validator, and passed the configured LaTeX log scans.

Interpretation:

- The non-Can Lift hard-negative mechanism is now stronger than the previous
  split-101-only read, but it remains exploratory C1 evidence. Absolute Lift
  endpoint success is low and split `303` is still unrun, so the paper should not
  claim a non-Can endpoint win yet.

## 2026-06-25: v0.2 method-freeze provenance gate

Environment:

- No GPU or training used.
- Full paper validation ran from the repository root via `make -C paper validate`.

Implemented:

- Added `scripts/validate_method_freeze_v02.py`, a provenance check that
  validates `METHOD_FREEZE_V02.md` against the v0.2 router implementation in
  `scripts/summarize_v02_fresh_router_support_audit.py`.
- The validator also checks the staged v0.2 router-support artifacts: Can
  fresh splits route to `hard_risk_union`, Lift MG fresh splits route to
  `soft_weighted`, and endpoint selected-row roles match those branches.
- Wired the validator into `paper/Makefile`, `paper/README.md`,
  `paper/MANUSCRIPT_CHECKLIST.md`, and `paper/REPRODUCE_PAPER.md`.
- Marked the Week 1 `METHOD_FREEZE_V02.md` deliverable as staged and
  validator-covered in `triage_bc_top_tier_completion_plan.md`.

Validation:

- `make -C paper validate` passed end to end.
- The gate regenerated the paper artifact stack, rebuilt both PDFs, validated
  claim numbers and structure, checked 131 unique artifact references, passed
  the v0.2 method-freeze validator, and passed the configured LaTeX log scans.
- `python scripts/validate_method_freeze_v02.py` passed.
- `git diff --check` passed before the full validation gate.

Interpretation:

- The paper package now has an explicit freeze-to-code-to-artifact provenance
  check for v0.2. This reduces reviewer/reproducer ambiguity between the older
  v0.1-style final-matrix runner path and the frozen v0.2 portfolio-router
  audit used for the fresh Can+Lift gate.
- This does not strengthen the endpoint result itself; it strengthens the
  submission's reproducibility and method-contract discipline.

## 2026-06-25: Submission-readiness audit

Environment:

- No GPU or training used.
- Full paper validation ran from the repository root via `make -C paper validate`.

Implemented:

- Added `scripts/summarize_submission_readiness_audit.py`, a generated
  acceptance-readiness audit over the staged final-paper artifact package.
- Wrote `results/final_paper/tables/submission_readiness_audit.csv` and
  `results/final_paper/tables/submission_readiness_audit_REPORT.md`.
- Wired the audit into `paper/Makefile`, `paper/MANUSCRIPT_CHECKLIST.md`,
  `paper/REPRODUCE_PAPER.md`, `FINAL_CLAIM_CONTRACT.md`, and the paper
  structure/claim-number validators.
- Marked the top-tier plan's master evidence-table Week 1 deliverable as
  staged.

Validation:

- `make -C paper validate` passed end to end.
- The gate regenerated the paper artifact stack, rebuilt both PDFs, validated
  claim numbers and structure, checked 130 unique artifact references, and
  passed the configured LaTeX log scans.
- `python -m py_compile scripts/summarize_submission_readiness_audit.py
  scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
  scripts/validate_paper_structure.py` passed.
- `git diff --check` passed before the full validation gate.

Interpretation:

- The generated audit reports 6/6 high-quality empirical-submission criteria as
  passing and 4/4 top-tier methods/SOTA dominance criteria as not met.
- This strengthens the current submission posture: a careful precision/coverage
  empirical study with cautious v0.2 portfolio-router evidence, not a
  methods-dominance or SOTA claim.

## 2026-06-25: Final claim contract and full paper validation

Environment:

- No GPU or training used.
- Full paper validation ran from the repository root via `make -C paper validate`.

Implemented:

- Added `FINAL_CLAIM_CONTRACT.md`, the final paper-facing allowed-claim and
  forbidden-claim boundary for the current evidence package.
- Added the contract to `paper/README.md`, `paper/MANUSCRIPT_CHECKLIST.md`,
  and `paper/REPRODUCE_PAPER.md`.
- Refreshed stale v0.2 reproduction commands in `paper/README.md` and
  `paper/REPRODUCE_PAPER.md` from split seeds `101/202/303` to the current
  five-split gate `101/202/303/404/505`.
- Wired `FINAL_CLAIM_CONTRACT.md` into
  `scripts/validate_paper_artifact_refs.py`,
  `scripts/validate_paper_claim_numbers.py`, and
  `scripts/validate_paper_structure.py`.

Validation:

- `make -C paper validate` passed end to end.
- The gate regenerated paper tables/figures, rebuilt both PDFs, validated claim
  numbers and structure, checked 128 unique artifact references, and passed the
  configured LaTeX log scans.
- `git diff --check` passed.
- No Robomimic train/eval processes were running.

Interpretation:

- The Week 1 `FINAL_CLAIM_CONTRACT.md` deliverable is now staged and
  validator-covered.
- The paper handoff docs now match the actual five-split v0.2 validation gate.
- The contract preserves the current honest framing: a high-quality
  precision/coverage empirical study with cautious v0.2 portfolio evidence,
  not a methods/SOTA dominance claim.

## 2026-06-25: Reviewer-facing claim summary

Environment:

- No GPU or training used.
- Paper-facing validation ran from the repository root.

Implemented:

- Added `paper/REVIEWER_CLAIM_SUMMARY.md`, a compact claim/evidence/limitation
  summary for reviewers.
- Added the summary to `paper/README.md`, `paper/MANUSCRIPT_CHECKLIST.md`, and
  `paper/REPRODUCE_PAPER.md`.
- Wired the new summary into `scripts/validate_paper_artifact_refs.py`,
  `scripts/validate_paper_structure.py`, and
  `scripts/validate_paper_claim_numbers.py`.
- Marked the top-tier plan's one-page reviewer-facing summary deliverable as
  staged.

Validation:

- `python scripts/validate_paper_claim_numbers.py`
- `python scripts/validate_paper_structure.py`
- `python scripts/validate_paper_artifact_refs.py` checked 126 unique artifact
  references.
- `git diff --check`

Interpretation:

- This closes the named Week 4 paper-polish deliverable without expanding
  claims.
- The summary keeps the v0.2 result framed as directional branch-selection
  evidence and keeps the Lift hard-negative split-101 endpoint as exploratory
  C1 evidence only.

## 2026-06-25: Lift hard-negative endpoint smoke

Environment:

- Conda env: `tri-piql`
- GPU/MuJoCo runs used `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`

Implemented:

- Prepared split-101 endpoint configs from
  `results/final_paper/ablations/lift_hard_negative_action_conflict_splits/split101/split_indices.json`.
- Trained official Robomimic BC-RNN-GMM for 50 epochs, 100 steps per epoch:
  `state_action_positive_nn_top40` and `bad_aware_proxy_top40`.
- Evaluated both epoch-50 checkpoints on 10 valid-positive Lift starts.

Result artifact:

- `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/REPORT.md`
- `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/endpoint_smoke_10ep_summary.csv`

Result:

- `bad_aware_proxy_top40`: `2/10`, average length `127.8`, support `21` hidden
  positives and `19` hidden bad demos on split 101.
- `state_action_positive_nn_top40`: `1/10`, average length `141.4`, support
  `7` hidden positives and `33` hidden bad demos on split 101.

Interpretation:

- This is directionally consistent with the support audit but very weak.
- It is only a feasibility smoke, not a C1 endpoint result.
- The next meaningful gate is split-101 at 200 epochs and 50 rollouts before
  expanding to seeds `202` and `303`.

## 2026-06-25: Lift hard-negative full-budget split-101 gate

Environment:

- Conda env: `tri-piql`
- GPU/MuJoCo runs used `XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl`

Implemented:

- Prepared a separate full-budget output root:
  `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/`.
- Trained official Robomimic BC-RNN-GMM for 200 epochs, 100 steps per epoch:
  `state_action_positive_nn_top40` and `bad_aware_proxy_top40`.
- Evaluated both epoch-200 checkpoints on 50 valid-positive Lift starts.

Result artifact:

- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/REPORT.md`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/endpoint_200ep_summary.csv`

Result:

- `bad_aware_proxy_top40`: `7/50`, average length `137.3`, support `21` hidden
  positives and `19` hidden bad demos on split 101.
- `state_action_positive_nn_top40`: `3/50`, average length `143.6`, support
  `7` hidden positives and `33` hidden bad demos on split 101.

Interpretation:

- The full-budget split-101 result is directionally consistent with the support
  audit and the 50-epoch smoke.
- The absolute success rate is low, so this should remain exploratory unless
  split seeds `202/303` are run and preserve the margin.
- Do not promote a non-Can C1 endpoint claim from this single split.

## 2026-06-25: Generated regime-probe summary table

Implemented:

- `scripts/summarize_generated_regime_probe_table.py`: aggregates the
  endpoint-backed hard-negative, coverage-shift, and prefix-positive Can probes.
- `results/final_paper/tables/generated_regime_probe_summary.csv`
- `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`

Result:

- Hard-negative Can: bad-aware `104/150` versus positive-only `91/150`,
  support `113/7` versus `70/50`.
- Coverage-shift Can: bad-aware `120/150` versus positive-only `103/150`,
  support `118/2` versus `105/15`.
- Prefix-positive Can: bad-aware `119/150` versus positive-only `6/150`,
  support `195/45` versus `37/203`.

Interpretation:

- This is the concise main-table artifact requested by the top-tier plan.
- It is generated regime-probe evidence, not a default Robomimic benchmark row.

## 2026-06-22: Fast GridWorld diagnostics

Environment:

- Conda env: `tri-piql`
- GPU runs use `XLA_PYTHON_CLIENT_PREALLOCATE=false`
- JAX CUDA device was verified before these runs.

Implemented:

- `tri_piql/envs/gridworld.py`: deterministic 7x7 GridWorld with a safe goal route and a bad trap shortcut.
- `tri_piql/algos/tabular.py`: tabular BC, classifier-weighted BC, and a tabular Tri-PIQL prototype with trajectory ranking, latent unlabeled desirability, signed action-centered advantage constraints, and an advantage-weighted BC policy extractor.
- `scripts/run_gridworld_diagnostic.py`: short multi-seed runner that writes CSV, JSON, and Markdown reports.

### Full-positive diagnostic

Command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_gridworld_diagnostic.py \
  --steps 300 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --out-dir results/gridworld_diagnostic
```

Result artifact:

- `results/gridworld_diagnostic/REPORT.md`

Interpretation:

- BC-all reliably imitates the majority bad shortcut and hits the trap.
- BC-positive, weighted BC, and Tri-PIQL all solve the task because the labeled positive trajectories already contain the full safe route.
- This is a useful Stage 1 smoke test but not a paper-strength comparison.

### Prefix-positive stitching diagnostic

Command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_gridworld_diagnostic.py \
  --steps 500 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --positive-prefix-len 6 \
  --out-dir results/gridworld_prefix_stitching
```

Result artifact:

- `results/gridworld_prefix_stitching/REPORT.md`

Interpretation:

- BC-positive fails because positives only cover the first part of the safe route.
- BC on positives plus unlabeled fails under moderate to high contamination because it imitates hidden bad shortcut data.
- Tri-PIQL succeeds across the tested contamination levels by using likely-good unlabeled data while avoiding labeled bad behavior.
- Weighted BC also succeeds, so this diagnostic does not yet establish a clear advantage over a strong filtering baseline.

### Loop-mixed transition filtering diagnostic

Command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_gridworld_diagnostic.py \
  --scenario loop_mixed \
  --steps 600 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --positive-prefix-len 6 \
  --out-dir results/gridworld_loop_mixed
```

Result artifact:

- `results/gridworld_loop_mixed/REPORT.md`

Interpretation:

- Labeled positives again only cover the safe prefix, so BC-positive cannot finish the route.
- Unlabeled successful trajectories contain repeated bad loop actions before recovery, so trajectory-level weighted BC gives the whole trajectory high weight and then clones the loop.
- Explicit bad snippets label the loop action as undesirable. Tri-PIQL's signed transition constraint downweights that action while still using the later unlabeled route actions.
- Tri-PIQL succeeds across all tested contamination levels and seeds; weighted BC fails in all rows.
- The latent trajectory desirability AUC is not consistently high in this diagnostic, especially when trajectory-level quality is deliberately ambiguous. That is acceptable for this diagnostic because the intended mechanism is transition-level anti-preference, not pure trajectory filtering.

### Current research conclusion

The code now gives fast validated evidence for the basic mechanism:

- explicit bad data prevents naive mixed-log imitation;
- latent desirability can recover useful unlabeled trajectories;
- signed good/bad advantage diagnostics have the intended signs;
- the policy extractor must be offline support-constrained; greedy Q over learned reward can exploit unsupported states and is kept only as a diagnostic row.
- trajectory-level filtering is insufficient when useful unlabeled trajectories contain repeated bad actions; the loop-mixed diagnostic is the best current paper-facing synthetic result.

The next step should move from tabular diagnostics to a small function-approximation version of the loop-mixed setting, then to one state-based Minari/D4RL task once the neural implementation matches the tabular result.

## 2026-06-22: Neural GridWorld reward learner

Implemented:

- `tri_piql/algos/neural_gridworld.py`: MLP reward model over GridWorld state/action features, trained with the same ranking, latent desirability, signed advantage, conservative, and reward regularization losses.
- `scripts/run_neural_gridworld.py`: neural loop-mixed runner with the same baselines and reports as the tabular diagnostic.
- `make_loop_mixed_dataset(..., negative_shortcut_frac=...)`: optional labeled bad set containing both bad loop-action snippets and full bad shortcut trajectories.

### Neural loop-mixed contrastive diagnostic

Command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false conda run -n tri-piql \
  python scripts/run_neural_gridworld.py \
  --steps 1200 --seeds 0 1 2 --bad-fracs 0.25 0.50 0.75 0.90 \
  --feature-mode coords \
  --negative-shortcut-frac 0.5 \
  --out-dir results/neural_gridworld_loop_mixed_contrastive
```

Result artifact:

- `results/neural_gridworld_loop_mixed_contrastive/REPORT.md`

Interpretation:

- This is the best current function-approximation result.
- Neural Tri-PIQL AWBC succeeds in all 12 tested settings.
- Weighted BC succeeds in 0 of 12 settings.
- Hidden unlabeled desirability AUC is 1.0 in every tested setting when the labeled bad set includes both shortcut failures and bad loop-action snippets.
- The minimum learned positive-negative return gap is positive; the minimum good-action advantage is positive; the maximum bad-action advantage is negative.
- A shorter 800-step sweep had one low-contamination seed failure even though reward diagnostics were good; 1200 steps is the current fast stable budget.

### Updated research conclusion

The current synthetic evidence now supports a stronger mechanism claim:

- trajectory-level filtering can fail when otherwise useful unlabeled trajectories contain repeated undesirable transitions;
- explicit bad snippets provide transition-level anti-preference signal;
- full bad trajectories calibrate latent trajectory desirability;
- the combined tri-signal objective survives a small neural reward parameterization.

The next step is to port the neural loop-mixed implementation pattern to one small continuous-state offline task or a Minari/D4RL state-based task, while keeping the first run short and heavily logged.

## 2026-06-22: Larger coordinate-grid diagnostic

Implemented:

- `scripts/run_neural_gridworld.py` now accepts grid geometry controls: `--width`, `--height`, `--max-steps`, `--trap-x`, and `--trap-y`.

### 21x21 coordinate-grid loop-mixed diagnostic

Command:

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

Result artifact:

- `results/neural_pointgrid21_loop_mixed/REPORT.md`

Interpretation:

- Neural Tri-PIQL AWBC succeeds in all 12 tested settings.
- Weighted BC succeeds in 0 of 12 settings.
- Hidden unlabeled desirability AUC is 1.0 in every tested setting.
- The minimum learned positive-negative return gap is positive; the minimum good-action advantage is positive; the maximum bad-action advantage is negative.
- Greedy-Q over the learned neural reward is less stable than AWBC on this larger grid, so the offline support-constrained policy extractor remains the right promoted policy row.

### Updated next step

The synthetic evidence now has three increasingly strong tiers: tabular, neural 7x7 coordinate reward, and neural 21x21 coordinate reward. The next meaningful escalation is no longer another grid variant; it should be a small real offline benchmark setup, starting with Minari/D4RL state-based data if the dependency path is clean.

## 2026-06-22: Minari setup check

Installed into `tri-piql`:

- `minari==0.5.3`
- `gymnasium==1.3.0`
- `pandas==3.0.3`
- `matplotlib==3.11.0`
- `huggingface_hub` via the Minari `hf` extra, required by `minari list remote`.
- `h5py==3.16.0`, required to load HDF5-backed Minari datasets.
- `gymnasium-robotics==1.4.2` and `mujoco==3.9.0`, required to recover and roll out PointMaze environments.

Verified:

- JAX still sees the CUDA device after the installs.
- `minari list remote --prefix D4RL/pointmaze` works and lists 8 PointMaze datasets.
- The listed PointMaze files are hundreds of MB, so the first actual dataset download should be an explicit next step.

Environment note:

- Matplotlib import warns that `/home/eston/.config/matplotlib` is not writable in this session. Use `MPLCONFIGDIR=/tmp/matplotlib` for plotting commands.

## 2026-06-22: First Minari PointMaze split and BC smoke

Implemented:

- `tri_piql/datasets/minari_splits.py`: Minari dataset inspection, return/score statistics, trajectory-level split generation, and split artifacts.
- `scripts/inspect_minari_dataset.py`: CLI for writing `summary.json`, `episodes.csv`, `split_indices.json`, and `REPORT.md`.
- `scripts/run_minari_bc_baselines.py`: short continuous-action BC baseline runner with recovered-environment rollout evaluation for Minari datasets.

Downloaded:

- `D4RL/pointmaze/large-v2` to the local Minari cache.

### Dataset inspection

Command:

```bash
conda run -n tri-piql python scripts/inspect_minari_dataset.py \
  D4RL/pointmaze/large-v2 \
  --out-dir results/minari_inspection \
  --top-frac 0.10 --bottom-frac 0.20 \
  --score-mode return_length \
  --seed 0
```

Result artifact:

- `results/minari_inspection/D4RL__pointmaze__large-v2/REPORT.md`

Key facts:

- Total episodes: 3360.
- Total transitions: 1,000,000.
- Sparse trajectory returns are nearly unusable for ranking: 3355 of 3360 trajectories have return 1.
- The usable first split is `return_length`, which ranks failures below successes and shorter successful episodes above slower successful episodes.
- Split sizes: 336 positive, 672 negative, 2352 unlabeled.
- Positive split length mean: 43.8 steps.
- Negative split length mean: 541.0 steps; it includes all 5 return-0 failures plus the slowest successful trajectories.

### Recovered-environment BC smoke

Command:

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

Result artifact:

- `results/minari_pointmaze_large_bc_smoke/REPORT.md`

Short-run rollout result:

| method | success | return | length |
|---|---:|---:|---:|
| BC-positive | 0.400 | 0.400 | 511.8 |
| BC-positive+unlabeled | 0.300 | 0.300 | 631.7 |
| BC-all | 0.200 | 0.200 | 725.1 |
| classifier-weighted BC | 0.400 | 0.400 | 564.0 |

Classifier diagnostic:

- Labeled transition accuracy: 0.912.
- Positive transition probability mean: 0.821.
- Negative transition probability mean: 0.166.
- Unlabeled transition probability mean: 0.405.

Interpretation:

- This is a real-data train/eval smoke, not a final benchmark result.
- The pipeline can now load Minari data, construct trajectory labels, train continuous-action policies, recover PointMaze, and evaluate rollouts.
- Mixed-log cloning already underperforms positive-only and classifier-weighted BC on this split, so the next real-data experiment should add Tri-PIQL's signed advantage / inverse-Q reward component against this same classifier-weighted BC baseline.
- Sandboxed JAX could not initialize CUDA (`cuInit` error 100), but the same command with escalation saw `CudaDevice(id=0)` and ran successfully with `XLA_PYTHON_CLIENT_PREALLOCATE=false`.

## 2026-06-22: PointMaze Tri-PIQL score smoke and dense dataset pivot

Implemented:

- `scripts/run_minari_tri_piql_smoke.py`: continuous-action PointMaze smoke runner with:
  - classifier-weighted BC baseline,
  - learned state-action score over `(observation, desired_goal, action)`,
  - positive-vs-negative trajectory ranking,
  - signed positive/negative transition score constraints,
  - latent unlabeled trajectory q values,
  - random-action conservative score penalty,
  - q-only and score-AWBC actor extraction variants.

Also fixed:

- `scripts/run_minari_bc_baselines.py` now uses `info["success"]` for rollout success when available. This matters for dense PointMaze because dense rewards can be positive before goal success.

### Sparse PointMaze Tri-PIQL score smoke

Command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_tri_piql_smoke.py \
  D4RL/pointmaze/large-v2 \
  --out-dir results/minari_pointmaze_large_tri_piql_smoke \
  --steps 800 --actor-steps 700 --classifier-steps 300 \
  --batch-size 512 --traj-batch-size 12 \
  --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 10 --eval-horizon 800 \
  --seed 0
```

Result artifact:

- `results/minari_pointmaze_large_tri_piql_smoke/REPORT.md`

Short-run rollout result:

| method | success | return | length |
|---|---:|---:|---:|
| BC-positive | 0.500 | 0.500 | 449.7 |
| classifier-weighted BC | 0.500 | 0.500 | 525.8 |
| Tri-PIQL q-BC | 0.200 | 0.200 | 676.3 |
| Tri-PIQL score-AWBC | 0.400 | 0.400 | 525.5 |

Score diagnostics:

- q positive/negative/unlabeled mean: 0.724 / 0.243 / 0.575.
- positive-vs-negative q AUC: 1.000.
- unlabeled q vs label-score Spearman: 0.686.
- transition score positive/negative/unlabeled mean: 1.868 / -4.670 / -1.646.

Interpretation:

- The sparse split produces good ranking diagnostics, but the actor extraction underperforms.
- q-only actor extraction is worse than score-AWBC, so simply admitting q-weighted unlabeled data is not enough.
- A lower-prior/temperature variant (`results/minari_pointmaze_large_tri_piql_prior035_temp07`) did not improve the result.

### Dense PointMaze inspection and BC smoke

Downloaded:

- `D4RL/pointmaze/large-dense-v2` to the local Minari cache.

Inspection command:

```bash
conda run -n tri-piql python scripts/inspect_minari_dataset.py \
  D4RL/pointmaze/large-dense-v2 \
  --out-dir results/minari_inspection \
  --top-frac 0.10 --bottom-frac 0.20 \
  --score-mode return \
  --seed 0
```

Result artifact:

- `results/minari_inspection/D4RL__pointmaze__large-dense-v2/REPORT.md`

Key facts:

- Total episodes: 3360.
- Total transitions: 1,000,000.
- Dense trajectory returns are usable: p10 / p50 / p90 = 16.364 / 23.513 / 35.340.
- Split sizes: 336 positive, 672 negative, 2352 unlabeled.

BC smoke artifact:

- `results/minari_pointmaze_large_dense_bc_smoke/REPORT.md`

Short-run dense BC result:

| method | success | dense return | length |
|---|---:|---:|---:|
| BC-positive | 0.300 | 51.021 | 675.1 |
| BC-positive+unlabeled | 0.300 | 58.403 | 646.9 |
| BC-all | 0.200 | 61.356 | 690.6 |
| classifier-weighted BC | 0.100 | 72.695 | 743.5 |

Interpretation:

- Dense return and goal success can disagree in short rollouts; classifier-weighted BC gets high dense return but poor success.
- Success rate remains the more relevant promoted PointMaze metric.

### Dense PointMaze Tri-PIQL score smoke

Command:

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

Result artifact:

- `results/minari_pointmaze_large_dense_tri_piql_smoke/REPORT.md`

Short-run rollout result:

| method | success | dense return | length |
|---|---:|---:|---:|
| BC-positive | 0.500 | 42.861 | 580.7 |
| classifier-weighted BC | 0.300 | 48.194 | 684.6 |
| Tri-PIQL q-BC | 0.100 | 51.389 | 727.1 |
| Tri-PIQL score-AWBC | 0.100 | 43.648 | 732.2 |

Score diagnostics:

- q positive/negative/unlabeled mean: 0.720 / 0.406 / 0.482.
- positive-vs-negative q AUC: 0.952.
- unlabeled q vs label-score Spearman: 0.254.
- transition score positive/negative/unlabeled mean: 1.464 / -0.444 / 0.253.

Interpretation:

- This is a useful negative result. The current scalar score objective can learn some label separation, but it does not produce a better continuous-action policy on PointMaze.
- More score-weight tuning is not the right next step.
- The missing real-data method component is an actual IQL-style continuous-action V/Q training path with expectile value fitting and advantage extraction. The synthetic GridWorld result used exact dynamic programming for Q; the current PointMaze smoke only uses a scalar state-action score and therefore lacks the support-constrained Bellman structure needed for reliable actor extraction.

## 2026-06-22: PointMaze V/Q Tri-PIQL smoke

Implemented:

- `scripts/run_minari_tri_iql_smoke.py`: continuous-action V/Q Tri-PIQL smoke runner with:
  - learned reward `r(s,a,s')`,
  - Q network `Q(s,a)`,
  - V network `V(s)`,
  - TD consistency `Q ~= r + gamma V(s')`,
  - IQL-style expectile value fitting,
  - positive-vs-negative trajectory reward ranking,
  - signed good/bad advantage constraints,
  - latent unlabeled trajectory q values,
  - random-action conservative Q penalty,
  - raw, normalized, top-q, and positive-only advantage-weighted actor extraction variants.

### Dense PointMaze V/Q smoke

Command:

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

Result artifact:

- `results/minari_pointmaze_large_dense_tri_iql_filtered/REPORT.md`

Short-run rollout result:

| method | success | dense return | length |
|---|---:|---:|---:|
| BC-positive | 0.500 | 41.841 | 581.4 |
| classifier-weighted BC | 0.300 | 46.758 | 660.8 |
| Tri-IQL raw AWBC | 0.100 | 29.309 | 726.7 |
| Tri-IQL normalized AWBC | 0.100 | 32.140 | 727.6 |
| Tri-IQL top-q AWBC | 0.000 | 39.706 | 800.0 |
| Tri-IQL positive-only AWBC | 0.100 | 28.948 | 727.8 |

V/Q diagnostics:

- q positive/negative/unlabeled mean: 0.760 / 0.371 / 0.475.
- positive-vs-negative q AUC: 0.983.
- learned reward trajectory gap: 753.088.
- unlabeled q vs label-score Spearman: 0.299.
- raw advantage positive/negative/unlabeled mean: 1.263 / -0.762 / 0.104.
- top-q actor keeps 32.0% of unlabeled transitions.

Interpretation:

- The V/Q objective learns clear positive-vs-negative separation and signed advantage separation, but the advantage-weighted actor is worse than plain BC-positive.
- Dropping unlabeled data does not rescue the actor: positive-only advantage weighting is still 0.100 success.
- The failure is therefore not just excessive unlabeled admission. The learned advantage is not selecting behavior-cloning weights that preserve a good PointMaze policy.
- More PointMaze advantage-weight tuning is unlikely to be productive. The next useful branch should either:
  - change policy extraction, for example supervised positive BC with a separate learned bad-action penalty or action-space reranking at evaluation, or
  - move the real-data benchmark to a setting where return labels, bad behavior, and action support align more directly with the method, such as locomotion medium-replay or Robomimic paired low-dimensional data.

## 2026-06-22: PointMaze state-action reranking smoke

Implemented:

- `scripts/run_minari_action_rerank_smoke.py`: keeps the positive BC actor as the anchor, trains a state-action classifier on `(s,a)` pairs from positive vs negative trajectories, samples candidate actions around the BC action at evaluation time, and chooses the candidate with the best classifier score minus an action-deviation penalty.

Motivation:

- The previous PointMaze failures came from retraining actors with noisy q/advantage weights.
- This test keeps the stable BC actor and uses bad-action knowledge only as a local action reranker.

### Dense PointMaze action-rerank smoke

Seed 0 command:

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

Seed 1 used the same command with:

```bash
--out-dir results/minari_pointmaze_large_dense_action_rerank_seed1 --seed 1
```

Result artifacts:

- `results/minari_pointmaze_large_dense_action_rerank/REPORT.md`
- `results/minari_pointmaze_large_dense_action_rerank_seed1/REPORT.md`
- `results/minari_pointmaze_large_dense_action_rerank/SEED_SUMMARY.md`

Two-seed aggregate:

| method | success mean | success values | dense return mean |
|---|---:|---|---:|
| BC-positive | 0.300 | 0.200, 0.400 | 49.848 |
| weighted BC, obs classifier | 0.250 | 0.200, 0.300 | 51.098 |
| state-action rerank, noise 0.10, penalty 0.05 | 0.200 | 0.300, 0.100 | 65.496 |
| state-action rerank, noise 0.10, penalty 0.20 | 0.150 | 0.200, 0.100 | 68.563 |
| state-action rerank, noise 0.25, penalty 0.05 | 0.300 | 0.300, 0.300 | 57.964 |
| state-action rerank, noise 0.25, penalty 0.20 | 0.200 | 0.300, 0.100 | 56.867 |

Classifier diagnostics:

- Seed 0 state-action classifier labeled accuracy: 0.825.
- Seed 1 state-action classifier labeled accuracy: 0.809.

Interpretation:

- State-action bad/good scoring is a more promising PointMaze extraction mechanism than AWBC: it can increase dense return and one setting is stable at 0.300 success across two seeds.
- It is not yet a success-rate win over BC-positive, whose two-seed mean is also 0.300.
- The dense return gains are not sufficient for a main claim because task success is the stronger PointMaze metric.
- Next useful step: either make reranking goal-aware and success-oriented, or move to locomotion/Robomimic where scalar return labels and policy quality are better aligned.

## 2026-06-22: Additional Minari target screening

Motivation:

- The available Minari D4RL catalog in this environment does not include Hopper, Walker2d, or HalfCheetah.
- To avoid overfitting PointMaze, screened other available compact state-based datasets.

### Kitchen mixed

Downloaded:

- `D4RL/kitchen/mixed-v2`

Inspection artifact:

- `results/minari_inspection/D4RL__kitchen__mixed-v2/REPORT.md`

Key facts:

- 621 episodes, 156,560 transitions.
- Return distribution is usable: p10 / p50 / p90 = 230 / 357 / 444.
- Split sizes: 63 positive, 125 negative, 433 unlabeled.
- Environment recovery works via `FrankaKitchen-v1`.

BC smoke command:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_minari_bc_baselines.py \
  D4RL/kitchen/mixed-v2 \
  --out-dir results/minari_kitchen_mixed_bc_smoke \
  --obs-keys observation \
  --steps 700 --classifier-steps 500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --max-train-transitions 150000 \
  --eval-episodes 5 --eval-horizon 450 \
  --seed 0
```

Result artifact:

- `results/minari_kitchen_mixed_bc_smoke/REPORT.md`

Short-run result:

| method | return |
|---|---:|
| BC-positive | 0.000 |
| BC-positive+unlabeled | 0.000 |
| BC-all | 0.000 |
| classifier-weighted BC | 0.000 |

Classifier diagnostic:

- Labeled transition accuracy: 0.928.
- Positive/negative/unlabeled probability mean: 0.893 / 0.111 / 0.527.

Interpretation:

- Kitchen has useful labels, but simple feed-forward BC is too weak to get any rollout reward in this first smoke.
- This is not a good immediate benchmark target without a stronger robotics imitation setup.

### MiniGrid FourRooms

Downloaded and installed:

- `D4RL/minigrid/fourrooms-v0`
- `minigrid==3.1.0`

Inspection artifact:

- `results/minari_inspection/D4RL__minigrid__fourrooms-v0/REPORT.md`

Key facts:

- 590 episodes, 10,010 transitions.
- Return distribution is usable but narrow: p10 / p50 / p90 = 0.757 / 0.838 / 0.946.
- Split sizes: 59 positive, 118 negative, 413 unlabeled.
- Discrete action space with 7 actions.

Implemented:

- `scripts/run_minigrid_discrete_smoke.py`: discrete MLP BC, state-action classifier, classifier-weighted BC, and all-action reranking.

Command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql python scripts/run_minigrid_discrete_smoke.py \
  D4RL/minigrid/fourrooms-v0 \
  --out-dir results/minigrid_fourrooms_discrete_smoke \
  --steps 1000 --classifier-steps 700 \
  --batch-size 256 --hidden-dim 128 --depth 2 \
  --eval-episodes 100 --eval-horizon 100 \
  --rerank-alphas 0.5 1.0 2.0 \
  --seed 0
```

Result artifact:

- `results/minigrid_fourrooms_discrete_smoke/REPORT.md`

Short-run result:

| method | success | return |
|---|---:|---:|
| BC-positive | 0.050 | 0.048 |
| BC-positive+unlabeled | 0.050 | 0.048 |
| BC-all | 0.050 | 0.048 |
| weighted BC, state-action | 0.050 | 0.048 |
| BC-positive + rerank alpha 0.5 | 0.050 | 0.048 |
| BC-positive + rerank alpha 1.0 | 0.050 | 0.048 |
| BC-positive + rerank alpha 2.0 | 0.010 | 0.009 |

Classifier diagnostic:

- Labeled state-action classifier accuracy: 0.791.

Interpretation:

- MiniGrid is fast and discrete, but feed-forward partial-observation BC is too weak at evaluation.
- This target likely needs recurrence or full-state features before it can fairly test tri-signal learning.

### Updated real-data direction

Current real-data screen:

- PointMaze: useful but success and dense return are misaligned; reranking gives a modest signal but not a robust success win.
- Kitchen: clean return labels, but simple BC gets zero reward.
- MiniGrid: fast discrete task, but partial observability makes feed-forward BC too weak.

Next most useful target should be Robomimic low-dimensional paired/mixed data if dependency and dataset access are manageable, because the plan expects explicit good/bad paired demonstrations and success metrics that are more aligned with the method.

## 2026-06-22: Robomimic Can paired low-dimensional screen

Downloaded:

- `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`

Implemented:

- `scripts/inspect_robomimic_dataset.py`: HDF5 inspection, return statistics, Robomimic mask reading, and scarce-label split generation.
- `scripts/run_robomimic_offline_diagnostic.py`: offline state-action classifier plus BC policy diagnostics on labeled positive, labeled negative, unlabeled, and held-out validation demos.

### Dataset inspection

Command:

```bash
conda run -n tri-piql python scripts/inspect_robomimic_dataset.py \
  data/robomimic/v1.5/can/paired/low_dim_v15.hdf5 \
  --out-dir results/robomimic_inspection/can_paired_low_dim \
  --label-budget 10
```

Result artifact:

- `results/robomimic_inspection/can_paired_low_dim/REPORT.md`

Key facts:

- 200 demos, split exactly into 100 positive and 100 negative demos.
- Robomimic masks provide 180 train demos and 20 validation demos.
- Returns are 0 for failures and mostly 5 or 6 for successes.
- Default scarce-label split: 10 labeled positive demos, 10 labeled negative demos, 160 unlabeled train demos, 10 validation positive demos, and 10 validation negative demos.
- Low-dimensional observation vector uses the sorted Robomimic `obs` keys and 7-dimensional continuous actions.

### Offline paired-action diagnostic

Command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_robomimic_offline_diagnostic.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_paired_offline \
  --steps 1000 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --seed 0
```

Result artifact:

- `results/robomimic_can_paired_offline/REPORT.md`

Policy offline metrics:

| method | valid positive MSE | valid negative MSE | neg-pos MSE gap |
|---|---:|---:|---:|
| BC-positive | 0.04986 | 0.14027 | 0.09041 |
| BC-positive+unlabeled | 0.02390 | 0.02713 | 0.00323 |
| BC-all | 0.02484 | 0.02712 | 0.00228 |
| classifier-weighted BC, state-action | 0.02435 | 0.06093 | 0.03657 |

State-action classifier diagnostic:

- Train labeled accuracy: 0.985.
- Held-out validation accuracy: 0.747.
- Held-out positive-vs-negative AUC: 0.854.
- Validation positive/negative logit mean: 11.517 / -8.385.
- Unlabeled positive probability mean: 0.501.

Interpretation:

- Robomimic Can paired low-dimensional data is now the best real-data next target.
- The offline diagnostic is not a rollout result, but it shows a clean scarce-label setting and a state-action good/bad signal that generalizes to held-out paired demos.
- Positive-only BC has the largest positive-vs-negative MSE gap but uses only 1,198 labeled positive transitions. Classifier-weighted BC uses the large unlabeled pool while retaining more separation from negative validation actions than BC-all or positive+unlabeled.
- The next step should install the minimal Robomimic/robosuite evaluation stack and run real Can rollouts for positive BC, BC-all, classifier-weighted BC, and a local bad-action reranker before adding a heavier Tri-PIQL actor.

## 2026-06-22: Robomimic Can rollout screen

Installed:

- `robosuite==1.5.1`

Environment notes:

- The HDF5 metadata specifies `PickPlaceCan`, environment version `1.5.1`, Panda OSC pose control, object observations, and 7D continuous actions.
- `NUMBA_DISABLE_JIT=1` is needed for these smoke commands because robosuite imports otherwise hit a Numba cache locator error when no private macros file exists.
- `MUJOCO_GL=egl` is used for headless MuJoCo.

Implemented:

- `scripts/check_robomimic_playback.py`: resets robosuite from stored XML/state and replays stored actions.
- `scripts/run_robomimic_can_rollout_smoke.py`: trains the current JAX BC and state-action classifier baselines, maps HDF5 `object` observations to robosuite `object-state`, and evaluates either normal robosuite resets or held-out HDF5 initial states.

### Playback compatibility check

Command:

```bash
NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/check_robomimic_playback.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_playback_check \
  --demo-source valid_positive --max-demos 10
```

Result artifact:

- `results/robomimic_can_playback_check/REPORT.md`

Result:

- Held-out successful demo playback succeeds on all 10 validation positive demos.
- This verifies that stored simulator XML/state plus stored actions are compatible with the installed robosuite stack.

### Scarce-label rollout smoke

Random-reset command:

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

Held-out-state command used the same settings plus:

```bash
--out-dir results/robomimic_can_rollout_valid_states --eval-init-mode valid_positive_states
```

Result artifacts:

- `results/robomimic_can_rollout_smoke/REPORT.md`
- `results/robomimic_can_rollout_valid_states/REPORT.md`

Short-run result:

| setting | BC-positive | BC-positive+unlabeled | BC-all | weighted BC | positive BC + SA rerank |
|---|---:|---:|---:|---:|---:|
| random robosuite reset | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| held-out positive initial states | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

### High-label-budget sanity check

Created:

- `results/robomimic_inspection/can_paired_low_dim_budget80/REPORT.md`

Command:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_can_rollout_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json \
  --out-dir results/robomimic_can_rollout_valid_states_budget80 \
  --bc-steps 1200 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 5 --eval-horizon 400 \
  --eval-init-mode valid_positive_states \
  --candidate-count 32 --noise-stds 0.10 --action-penalties 0.05 \
  --seed 0
```

Result artifact:

- `results/robomimic_can_rollout_valid_states_budget80/REPORT.md`

Result:

- Even with 80 labeled positive demos and 80 labeled negative demos, all current feed-forward BC/rerank policies get 0.000 success on five held-out positive initial states.
- The state-action classifier remains useful: held-out validation accuracy is 0.796 and positive/negative logit means are 6.735 / -4.667.

Interpretation:

- Robomimic Can is compatible and has a clean tri-signal structure, but the current lightweight feed-forward policy stack is not strong enough for rollout evaluation.
- More tuning of the current MLP actor is unlikely to answer the research question. The useful Robomimic branch should use a stronger imitation backbone, such as official Robomimic low-dimensional BC/RNN/GMM training or a local sequence/action-distribution policy, before adding Tri-PIQL losses.
- Until that backbone is working, Robomimic should be treated as a promising but not immediate paper-result target.

### KNN support sanity checks

Implemented:

- `scripts/run_robomimic_knn_smoke.py`: nonparametric low-dimensional nearest-neighbor policy evaluation with three sources:
  - scarce labeled positives only,
  - oracle all train positives,
  - scarce labeled positives plus classifier-selected unlabeled transitions.

Scarce-positive KNN command:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_knn_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_knn_valid_states_scarce \
  --source labeled_positive \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --k-values 1 3 5 --seed 0
```

Oracle all-positive KNN command:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_knn_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json \
  --out-dir results/robomimic_can_knn_valid_states_budget80 \
  --source all_train_positive \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --k-values 1 3 5 --seed 0
```

Classifier-selected unlabeled KNN command:

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

Result artifacts:

- `results/robomimic_can_knn_valid_states_scarce/REPORT.md`
- `results/robomimic_can_knn_valid_states_budget80/REPORT.md`
- `results/robomimic_can_knn_valid_states_classifier_unlabeled_t05/REPORT.md`
- `results/robomimic_can_knn_valid_states_classifier_unlabeled_t09/REPORT.md`

Held-out positive initial-state result:

| source | k=1 | k=3 | k=5 |
|---|---:|---:|---:|
| scarce positives only | 0.000 | 0.000 | 0.000 |
| oracle all train positives | 0.200 | 0.400 | 0.200 |
| scarce positives + classifier unlabeled, threshold 0.5 | 0.000 | 0.000 | 0.000 |
| scarce positives + classifier unlabeled, threshold 0.9 | 0.000 | 0.200 | 0.200 |

Interpretation update:

- The all-positive oracle KNN result proves that the low-dimensional state library contains enough support for nonzero held-out success.
- Scarce positives alone are insufficient.
- Classifier-selected unlabeled transitions recover part of the oracle-support benefit from only 10 positive and 10 negative labeled demos, improving held-out success from 0.000 to 0.200 in this five-episode smoke.
- This is the first Robomimic rollout signal aligned with the paper idea, but it is too preliminary and too nonparametric to be a main result.
- Next useful Robomimic step: replace KNN with a learned sequence/action-distribution extractor trained on classifier-selected unlabeled transitions, then rerun this exact held-out-state protocol before returning to random-reset evaluation.

### Learned GMM action-distribution extractor

Implemented:

- `scripts/run_robomimic_gmm_smoke.py`: diagonal GMM action policy trained by weighted negative log likelihood, with policy modes for mixture mode, mixture mean, sampling, and classifier-reranked GMM samples.
- The script supports scarce positives, oracle all-train positives, transition-threshold selected unlabeled data, and trajectory-level top-scoring unlabeled demo selection.
- It also supports `obs_prev_action_time` features as a cheap history-conditioned policy check.

Key commands:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_valid_states_scarce \
  --source labeled_positive \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --steps 1500 --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 5 --policy-modes mode mean sample \
  --sample-temperature 0.2 --seed 0
```

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json \
  --out-dir results/robomimic_can_gmm_valid_states_all_train_positive \
  --source all_train_positive \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --steps 1500 --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 5 --policy-modes mode mean sample \
  --sample-temperature 0.2 --seed 0
```

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
  --candidate-count 32 --sample-temperature 0.5 \
  --top-unlabeled-demos 80 --unlabeled-weight-mode prob --seed 0
```

Result artifacts:

- `results/robomimic_can_gmm_valid_states_scarce/REPORT.md`
- `results/robomimic_can_gmm_valid_states_classifier_unlabeled_t09/REPORT.md`
- `results/robomimic_can_gmm_valid_states_classifier_unlabeled_t099/REPORT.md`
- `results/robomimic_can_gmm_history_valid_states_classifier_unlabeled_t09/REPORT.md`
- `results/robomimic_can_gmm_valid_states_top40_unlabeled_demos/REPORT.md`
- `results/robomimic_can_gmm_valid_states_top80_unlabeled_demos/REPORT.md`
- `results/robomimic_can_gmm_valid_states_all_train_positive/REPORT.md`

Held-out positive initial-state result:

| source / extractor | best success | note |
|---|---:|---|
| scarce positives, GMM | 0.000 | all mode/mean/sample variants fail |
| transition-selected unlabeled, threshold 0.9, GMM | 0.000 | selects 6,454 transitions with mean selected prob 0.991 |
| transition-selected unlabeled, threshold 0.99, GMM | 0.000 | selects 5,171 transitions with mean selected prob 0.999 |
| transition-selected unlabeled, threshold 0.9, history GMM | 0.000 | `obs_prev_action_time` features do not rescue |
| top 40 unlabeled demos, GMM | 0.000 | selects 35 hidden-positive demos out of 40 |
| top 80 unlabeled demos, GMM | 0.200 | selects 61 hidden-positive demos out of 80; mixture mean succeeds 1/5 |
| oracle all train positives, GMM | 0.400 | matches oracle all-positive KNN best result |

Interpretation update:

- The learned GMM policy class is capable: with oracle all-train positives it reaches 0.400 success, matching the KNN oracle support check.
- Scarce positives alone remain insufficient.
- Transition-level classifier selection is high-confidence but not enough for a learned policy; it appears to select fragments that KNN can sometimes exploit locally but that do not train a stable closed-loop GMM.
- Trajectory-level top-demo selection is better aligned with policy learning. Top 80 selected unlabeled demos include 61 hidden-positive demos and produce the first learned-policy Robomimic tri-signal improvement: 0.000 to 0.200 success over scarce-positive GMM.
- The result is still a five-episode smoke, not paper-strength. The next Robomimic step should evaluate top-demo selection over more seeds and replace the hand-chosen top-80 rule with a calibrated latent trajectory posterior / coverage criterion.

### Top-demo GMM seed check

Implemented:

- `scripts/summarize_robomimic_gmm_runs.py`: aggregates completed GMM smoke directories into `all_metrics.csv`, `summary.csv`, and `REPORT.md`.

Additional runs:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_valid_states_top80_unlabeled_demos_seed1 \
  --source positive_plus_classifier_top_unlabeled_demos \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --steps 1500 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 5 --policy-modes mode mean classifier_rerank \
  --candidate-count 32 --sample-temperature 0.5 \
  --top-unlabeled-demos 80 --unlabeled-weight-mode prob --seed 1
```

The same command was run with `--seed 2` and output directory `results/robomimic_can_gmm_valid_states_top80_unlabeled_demos_seed2`.

For a same-seed scarce-label baseline, the scarce-positive GMM command was also rerun with seeds 1 and 2:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_valid_states_scarce_seed1 \
  --source labeled_positive \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --steps 1500 --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 5 --policy-modes mode mean sample \
  --sample-temperature 0.2 --seed 1
```

Summary command:

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

Result artifact:

- `results/robomimic_can_gmm_scarce_vs_top80_seed_summary/REPORT.md`

Three-seed held-out positive initial-state result:

| source / method | success mean | seed values |
|---|---:|---|
| scarce positives, GMM mode | 0.000 | 0.000, 0.000, 0.000 |
| scarce positives, GMM mean | 0.000 | 0.000, 0.000, 0.000 |
| scarce positives, GMM sample | 0.000 | 0.000, 0.000, 0.000 |
| top-80 selected demos, GMM mode | 0.133 | 0.000, 0.000, 0.400 |
| top-80 selected demos, GMM mean | 0.067 | 0.200, 0.000, 0.000 |
| top-80 selected demos, classifier rerank | 0.000 | 0.000, 0.000, 0.000 |

Interpretation update:

- The learned-policy Robomimic signal survives as a weak three-seed improvement over scarce-positive GMM, but it is not robust enough for a main claim.
- Scarce-positive GMM is consistently zero, so the selected unlabeled demos are adding useful policy support.
- The instability is now the main problem: different seeds succeed under different extraction modes, and the best mean success is only 0.133 over five held-out starts.
- Next method step should not be another fixed top-k run. It should make selection less brittle, for example by combining latent trajectory posterior with a coverage/diversity term, and then evaluate on all 10 held-out positive starts.

### Robomimic baseline pivot

Additional diversity-selection checks:

- `results/robomimic_can_gmm_valid_states_diverse_top80_seed0/REPORT.md`
- `results/robomimic_can_gmm_valid_states_diverse_top80_seed2/REPORT.md`

Both diversity runs selected many hidden-positive demos but stayed at zero rollout success across all evaluated GMM policy modes. This makes the immediate Robomimic bottleneck a baseline/extractor issue, not another top-k selection variant.

Stronger positive-only baselines:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json \
  --out-dir results/robomimic_can_gmm_budget80_positive_stronger \
  --source labeled_positive \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 3000 --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode mean sample \
  --sample-temperature 0.2 --seed 0
```

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_can_rollout_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json \
  --out-dir results/robomimic_can_rollout_valid_states_budget80_stronger_mlp \
  --eval-init-mode valid_positive_states \
  --eval-episodes 5 --eval-horizon 400 \
  --bc-steps 5000 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 256 --depth 3 \
  --noise-stds 0.05 --action-penalties 0.01 \
  --candidate-count 32 --seed 0
```

Result artifacts:

- `results/robomimic_can_gmm_budget80_positive_stronger/REPORT.md`
- `results/robomimic_can_rollout_valid_states_budget80_stronger_mlp/REPORT.md`

Held-out positive initial-state result:

| baseline | labels / source | episodes | best success | note |
|---|---|---:|---:|---|
| old deterministic MLP BC | budget-80 split, shorter smoke | 5 | 0.000 | underpowered baseline |
| stronger deterministic MLP BC | 80 labeled positive demos | 5 | 0.400 | `bc_labeled_positive`; 5000 steps, 256x3 MLP |
| stronger diagonal GMM BC | 80 labeled positive demos | 10 | 0.600 | stochastic sample policy; mode reaches 0.500 |

Interpretation update:

- The earlier zero-success Robomimic BC result should not be used as a serious baseline.
- With enough positive labels and a stronger extractor, plain positive-only imitation can solve held-out validation starts at nontrivial rates.
- This does not invalidate the scarce-label problem: scarce 10-positive GMM remains zero, and the top-demo selected-unlabeled signal is still weak/noisy.
- The next Robomimic comparison should first standardize a credible imitation baseline, then ask whether tri-signal unlabeled selection improves it under the same label budget. The immediate baseline family should include deterministic MLP BC and stochastic/mixture BC, not only the original short MSE smoke.

### Robomimic optimization-budget check

The 3k/5k optimizer settings above are smoke-test budgets, not paper-facing training budgets. They are offline gradient updates, not environment interaction steps, so they should not be compared directly to online RL papers reporting 1M environment steps. Still, for Robomimic baselines, 5k updates is too small to defend as a final number.

Additional runs:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_scarce_20k_mode \
  --source labeled_positive \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 20000 --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode \
  --sample-temperature 0.2 --seed 0
```

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_top80_20k_mode \
  --source positive_plus_classifier_top_unlabeled_demos \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 20000 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode \
  --candidate-count 32 --sample-temperature 0.2 \
  --top-unlabeled-demos 80 --unlabeled-weight-mode prob --seed 0
```

Summary artifact:

- `results/robomimic_can_gmm_stronger_budget_summary/REPORT.md`

Held-out positive initial-state result:

| setting | train transitions | optimizer steps | eval starts | success |
|---|---:|---:|---:|---:|
| scarce positives, GMM mode | 1,198 | 20,000 | 10 | 0.000 |
| scarce positives + top-80 selected unlabeled demos, GMM mode | 9,027 | 20,000 | 10 | 0.400 |

Interpretation update:

- Longer optimization alone did not rescue the 10-positive scarce baseline.
- The selected-unlabeled policy improves from 0.300 at 3k updates to 0.400 at 20k updates under the same held-out-start protocol.
- The selected top-80 set contains 60 hidden-positive demos out of 80 and 7,829 selected unlabeled transitions.
- This is a stronger Robomimic signal than the earlier 3k/5-episode smoke, but it is still one seed and one deterministic GMM mode. A paper-facing table should run a larger update budget with checkpoints or early selection, multiple seeds, and a standard imitation backbone.
- The immediate next experimental question is no longer whether 5k was enough. It was not. The question is whether the selected-unlabeled improvement survives seeds and stronger BC/GMM training budgets without relying on hidden labels.

### Robomimic checkpointed budget curve

Implemented:

- `scripts/run_robomimic_gmm_smoke.py` now supports `--eval-checkpoints`, allowing one training run to evaluate intermediate optimizer checkpoints.
- `scripts/summarize_robomimic_gmm_runs.py` now groups by split path, max training steps, evaluated checkpoint step, and source transition count, so scarce-label and budget-80 rows are not accidentally mixed.
- `scripts/run_robomimic_can_rollout_smoke.py` uses a clipped sigmoid to avoid noisy overflow warnings in high-confidence classifier logits.

Additional seed-1 checkpoint runs:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_scarce_seed1_ckpt50k_mode \
  --source labeled_positive \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 50000 --eval-checkpoints 20000 50000 \
  --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode \
  --sample-temperature 0.2 --seed 1
```

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_top80_seed1_ckpt50k_mode \
  --source positive_plus_classifier_top_unlabeled_demos \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 50000 --eval-checkpoints 20000 50000 \
  --classifier-steps 800 \
  --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode \
  --candidate-count 32 --sample-temperature 0.2 \
  --top-unlabeled-demos 80 --unlabeled-weight-mode prob --seed 1
```

Result artifacts:

- `results/robomimic_can_gmm_scarce_seed1_ckpt50k_mode/REPORT.md`
- `results/robomimic_can_gmm_top80_seed1_ckpt50k_mode/REPORT.md`
- `results/robomimic_can_gmm_stronger_budget_summary/REPORT.md`

Held-out positive initial-state result:

| seed | setting | train transitions | checkpoint | success |
|---:|---|---:|---:|---:|
| 0 | scarce positives, GMM mode | 1,198 | 20,000 | 0.000 |
| 0 | scarce positives + top-80 selected unlabeled demos, GMM mode | 9,027 | 20,000 | 0.400 |
| 1 | scarce positives, GMM mode | 1,198 | 20,000 | 0.100 |
| 1 | scarce positives + top-80 selected unlabeled demos, GMM mode | 9,133 | 20,000 | 0.200 |
| 1 | scarce positives, GMM mode | 1,198 | 50,000 | 0.200 |
| 1 | scarce positives + top-80 selected unlabeled demos, GMM mode | 9,133 | 50,000 | 0.200 |

Interpretation update:

- The seed-0 20k result shows selected unlabeled support can substantially outperform scarce positives.
- The seed-1 checkpoint curve is more conservative: selected unlabeled improves the 20k checkpoint, but the scarce-positive baseline catches up by 50k.
- This confirms the user's concern: once optimization is less naive, the baseline is stronger and the Robomimic claim is not yet robust enough.
- The current Robomimic result should be framed as a promising support-recovery signal, not a paper-ready method win.
- Next Robomimic step should either run the same 20k/50k checkpoint curve on seed 2 or move to an official/sequence-aware Robomimic BC backbone before claiming real-data improvements.

### Robomimic seed-2 checkpoint and simpler-task pivot

Additional seed-2 checkpoint runs:

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_scarce_seed2_ckpt50k_mode \
  --source labeled_positive \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 50000 --eval-checkpoints 20000 50000 \
  --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode \
  --sample-temperature 0.2 --seed 2
```

```bash
JAX_PLATFORMS=cpu NUMBA_DISABLE_JIT=1 MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_top80_seed2_ckpt50k_mode \
  --source positive_plus_classifier_top_unlabeled_demos \
  --feature-mode obs \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 50000 --eval-checkpoints 20000 50000 \
  --classifier-steps 800 \
  --batch-size 512 --hidden-dim 256 --depth 3 \
  --components 5 --policy-modes mode \
  --candidate-count 32 --sample-temperature 0.2 \
  --top-unlabeled-demos 80 --unlabeled-weight-mode prob --seed 2
```

Updated summary artifact:

- `results/robomimic_can_gmm_stronger_budget_summary/REPORT.md`

Held-out positive initial-state result:

| checkpoint | scarce positives | top-80 selected unlabeled | seeds |
|---:|---:|---:|---|
| 20,000 | 0.067 | 0.300 | 0, 1, 2 |
| 50,000 | 0.150 | 0.150 | 1, 2 |

Interpretation update:

- At 20k optimizer steps, selected unlabeled support has a meaningful three-seed edge over scarce positives.
- At 50k optimizer steps, the advantage disappears in the two completed seeds because the scarce baseline improves and the selected-unlabeled policy does not consistently improve with more training.
- This makes Robomimic a useful stress test but likely too hard/noisy for first validation: it mixes the tri-signal question with contact-rich closed-loop manipulation, sequence memory, and imitation-backbone limitations.
- The next validation layer should be simpler but not toy-only: a controlled continuous point-navigation benchmark with continuous actions, closed-loop rollout, explicit good/bad/mixed demonstrations, and strong BC baselines trained long enough to converge.

## 2026-06-22: Controlled continuous PointNav bridge

Motivation:

- Robomimic Can is useful as a stress test but is too coupled to manipulation and imitation-backbone quality for first validation.
- The missing validation layer is continuous-state/action and closed-loop, but simple enough that the oracle good-support BC baseline can solve it.

Implemented:

- `scripts/run_continuous_pointnav_smoke.py`: a deterministic 2D continuous point-navigation task with:
  - start in the lower-left corner, goal in the upper-right, and a circular trap near the diagonal shortcut;
  - scarce labeled positives as safe-route prefixes only;
  - labeled negatives as bad shortcut trajectories through the trap;
  - unlabeled data as a mixed pool of hidden safe full routes and hidden bad shortcuts;
  - deterministic MLP BC baselines, state-action classifier weighted BC, action reranking, top-demo selected-unlabeled BC, and hidden-good oracle BC.

Command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_bridge_v1 \
  --seeds 0 1 2 \
  --bad-fracs 0.75 0.90 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-frac 0.25
```

Result artifact:

- `results/continuous_pointnav_bridge_v1/REPORT.md`

Closed-loop success:

| bad frac | mixed BC | weighted BC | local rerank | top-demo selected BC | hidden-good oracle |
|---:|---:|---:|---:|---:|---:|
| 0.75 | 0.356 | 0.000 | 0.000 | 0.956 | 1.000 |
| 0.90 | 0.244 | 0.000 | 0.000 | 0.522 | 1.000 |

Diagnostics:

- At 75% bad unlabeled data, the top-25% selected demos are mostly/all hidden good; top-demo BC nearly matches the hidden-good oracle.
- At 90% bad unlabeled data, top-demo selection still improves over mixed BC but admits more hidden bad demos because the selection prior is too high for the true good fraction.
- Local state-action reranking fails because positives are only prefixes; the classifier learns that prefix-like actions are good and blocks the later right-turn behavior needed to finish the route.
- State-action weighted BC also fails for the same reason: local transition scoring is not enough when positive labels lack full-route support.

Interpretation update:

- This controlled continuous task gives a cleaner first validation than Robomimic: the oracle is strong, naive/mixed baselines are imperfect, and selected unlabeled support creates a large improvement.
- The mechanism supported here is trajectory-level recovery of useful unlabeled support, not local bad-action reranking.
- This result aligns with the Robomimic top-demo signal and explains why transition-threshold selection/reranking failed there.
- Next step should turn this bridge into a more paper-facing ablation: sweep the assumed top-unlabeled fraction / prior, report selected hidden-good purity only as a diagnostic, and compare against a tuned positive+unlabeled BC baseline over more seeds.

### Continuous PointNav top-fraction ablation

Implemented:

- `scripts/run_continuous_pointnav_smoke.py` now supports `--top-unlabeled-fracs`, so one dataset/classifier pass can evaluate multiple assumed good-fraction/top-demo priors.
- The report now includes a selection diagnostics table. Hidden-good purity is logged only because this is a controlled diagnostic; it is not used by the method.

Command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_topfrac_ablation_90bad \
  --seeds 0 1 2 3 4 \
  --bad-fracs 0.90 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 0.15 0.25 0.35
```

Result artifact:

- `results/continuous_pointnav_topfrac_ablation_90bad/REPORT.md`

Closed-loop success at 90% bad unlabeled data:

| method | success |
|---|---:|
| positive-prefix BC | 0.000 |
| positive + unlabeled BC | 0.213 |
| all-data BC | 0.260 |
| state-action weighted BC | 0.000 |
| local state-action rerank | 0.000 |
| top-demo BC, top 5% | 1.000 |
| top-demo BC, top 10% | 0.953 |
| top-demo BC, top 15% | 0.680 |
| top-demo BC, top 25% | 0.467 |
| top-demo BC, top 35% | 0.460 |
| hidden-good oracle BC | 1.000 |

Selection diagnostics:

| top fraction | hidden-good demo purity | hidden-good transition purity |
|---:|---:|---:|
| 0.05 | 1.000 | 1.000 |
| 0.10 | 0.967 | 0.989 |
| 0.15 | 0.681 | 0.878 |
| 0.25 | 0.409 | 0.701 |
| 0.35 | 0.292 | 0.584 |

Interpretation update:

- This is the cleanest current validation of the tri-signal support-recovery story.
- In the hardest controlled setting tested so far, a conservative top-demo prior recovers hidden safe-route support and matches the hidden-good oracle across five seeds.
- Over-admitting unlabeled data steadily degrades performance as hidden bad demos enter the selected set, matching the intended motivation for calibrated latent desirability.
- Local state-action weighting/reranking is the wrong mechanism when positives are only prefixes; trajectory-level unlabeled selection is the supported mechanism.
- The next controlled-task step should replace fixed top-k selection with an explicit calibrated trajectory posterior / prior objective, then report sensitivity to prior misspecification without using hidden labels.

### Continuous PointNav calibrated posterior ablation

Implemented:

- `scripts/run_continuous_pointnav_smoke.py` now supports calibrated trajectory-posterior weighting through `--posterior-priors` and `--posterior-temperature`.
- The posterior maps each unlabeled trajectory score to a soft desirability weight, with a calibrated bias chosen so the mean posterior matches the assumed unlabeled-good prior.
- Reports now include posterior diagnostics: posterior mean, hidden-good demo weight purity, and hidden-good transition weight purity. Hidden labels are diagnostic only and are not used by training.

Commands:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_posterior_ablation_90bad \
  --seeds 0 1 2 3 4 \
  --bad-fracs 0.90 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 \
  --posterior-priors 0.05 0.10 0.15 \
  --posterior-temperature 0.05
```

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_posterior_temp002_90bad \
  --seeds 0 1 2 3 4 \
  --bad-fracs 0.90 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 \
  --posterior-priors 0.05 0.10 \
  --posterior-temperature 0.02
```

Result artifacts:

- `results/continuous_pointnav_posterior_ablation_90bad/REPORT.md`
- `results/continuous_pointnav_posterior_temp002_90bad/REPORT.md`

Closed-loop success at 90% bad unlabeled data:

| method | success |
|---|---:|
| all-data BC | 0.260 |
| positive + unlabeled BC | 0.213 |
| positive-prefix BC | 0.000 |
| state-action weighted BC | 0.000 |
| local state-action rerank | 0.000 |
| top-demo BC, top 5% | 1.000 |
| top-demo BC, top 10% | 0.953 |
| posterior BC, prior 5%, temp 0.05 | 0.800 |
| posterior BC, prior 10%, temp 0.05 | 0.927 |
| posterior BC, prior 15%, temp 0.05 | 0.507 |
| posterior BC, prior 5%, temp 0.02 | 1.000 |
| posterior BC, prior 10%, temp 0.02 | 0.947 |
| hidden-good oracle BC | 1.000 |

Posterior diagnostics:

| prior | temp | posterior mean | hidden-good demo weight purity | hidden-good transition weight purity |
|---:|---:|---:|---:|---:|
| 0.05 | 0.05 | 0.050 | 1.000 | 1.000 |
| 0.10 | 0.05 | 0.100 | 0.966 | 0.989 |
| 0.15 | 0.05 | 0.150 | 0.681 | 0.878 |
| 0.05 | 0.02 | 0.050 | 1.000 | 1.000 |
| 0.10 | 0.02 | 0.100 | 0.967 | 0.989 |

Interpretation update:

- This directly answers the Robomimic-vs-simpler-task question: Robomimic is a useful stress test, but it is not the right first validation layer because imitation-backbone weakness can mask the tri-signal mechanism.
- In the simpler continuous closed-loop task, the oracle good-support BC solves the task, naive/mixed BC is weak, and calibrated trajectory-posterior weighting recovers the hidden safe-route support under 90% bad unlabeled contamination.
- The supported mechanism is now sharper: trajectory-level latent desirability / support recovery works; local state-action weighting and local action reranking fail when the scarce positive labels are only prefixes.
- For the paper path, this controlled task should be treated as the main diagnostic environment before returning to Robomimic with a stronger standard imitation backbone.

### Continuous PointNav stable hard-regime sweep

Implementation fixes:

- `scripts/run_continuous_pointnav_smoke.py` now writes partial CSV/JSON/report artifacts after every completed seed/fraction run. This makes bounded longer sweeps interruptible without losing completed results.
- Method train/eval seeds are now derived from stable method names via `stable_method_offset`, so adding or removing a baseline no longer silently changes another method's optimization seed or evaluation starts.
- Selection and posterior diagnostics are now grouped by `bad_frac`, matching the metrics table.

Commands:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_posterior_hard_sweep_stable_seeds \
  --seeds 0 1 2 \
  --bad-fracs 0.90 0.95 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 \
  --posterior-priors 0.05 0.10 \
  --posterior-temperature 0.02
```

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_posterior_hard_sweep_stable_seeds_extra34 \
  --seeds 3 4 \
  --bad-fracs 0.90 0.95 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 \
  --posterior-priors 0.05 0.10 \
  --posterior-temperature 0.02
```

The two outputs were merged into:

- `results/continuous_pointnav_posterior_hard_sweep_stable_5seed/REPORT.md`

Closed-loop success:

| bad frac | all-data BC | pos+unlabeled BC | weighted BC | top-demo 5% | top-demo 10% | posterior 5% | posterior 10% | oracle |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.90 | 0.233 | 0.247 | 0.000 | 1.000 | 0.947 | 1.000 | 0.953 | 1.000 |
| 0.95 | 0.153 | 0.060 | 0.200 | 0.887 | 0.673 | 0.800 | 0.527 | 1.000 |

Selection / posterior diagnostics:

| bad frac | prior/top frac | selected demo purity | selected transition purity |
|---:|---:|---:|---:|
| 0.90 | 0.05 | 1.000 | 1.000 |
| 0.90 | 0.10 | 0.967 | 0.989 |
| 0.95 | 0.05 | 0.911 | 0.964 |
| 0.95 | 0.10 | 0.556 | 0.793 |

Interpretation update:

- The 90% bad-unlabeled regime is now a clean five-seed controlled result: conservative posterior-weighted BC and conservative top-demo BC match the hidden-good oracle, while mixed BC and positive+unlabeled BC are around 0.23-0.25 and local state-action methods fail.
- The 95% regime is an informative limit case, not the main claim. Conservative trajectory-level recovery still gives a large improvement over BC baselines, but it is no longer oracle-level because the selected set contains too few full safe trajectories and occasional hidden bad trajectories.
- The posterior is useful but not automatically better than hard top-k. At 95% bad data, soft posterior weights can underfit when the assumed good prior is too low and can admit too much bad support when the prior is too high.
- The next method improvement should target this exact failure boundary: add a coverage/diversity constraint or uncertainty-aware prior selection so conservative posterior weighting does not collapse when useful unlabeled support is very sparse.

### Continuous PointNav gap-selection pilot

Implemented:

- `scripts/run_continuous_pointnav_smoke.py` now supports score-gap trajectory selection through `--gap-select-max-fracs` and `--gap-select-min-frac`.
- The gap rule sorts unlabeled trajectories by mean state-action classifier score, then chooses the largest score drop within an allowed prefix. This is an unsupervised prior-selection heuristic; it does not use hidden good/bad labels.
- The runner now reports gap-selection diagnostics and adds two methods:
  - `tri_signal_gap_demo_bc_max...`: BC on positive prefixes plus gap-selected unlabeled trajectories.
  - `tri_signal_gap_posterior_bc_max...`: posterior-weighted BC with the posterior mean set to the selected gap fraction.

Pilot command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_gap_select_seed1_95bad \
  --seeds 1 \
  --bad-fracs 0.95 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 \
  --gap-select-max-fracs 0.10 \
  --gap-select-min-frac 0.02 \
  --posterior-priors 0.05 0.10 \
  --posterior-temperature 0.02
```

Result artifact:

- `results/continuous_pointnav_gap_select_seed1_95bad/REPORT.md`

Seed-1 95% bad result:

| method | success | trap |
|---|---:|---:|
| all-data BC | 0.200 | 0.800 |
| positive+unlabeled BC | 0.067 | 0.833 |
| local state-action weighted BC | 0.000 | 0.000 |
| fixed top-demo 5% | 0.433 | 0.567 |
| fixed posterior prior 5% | 0.000 | 0.433 |
| gap-demo BC, max 10% | 1.000 | 0.000 |
| gap-posterior BC, max 10% | 1.000 | 0.000 |
| hidden-good oracle BC | 1.000 | 0.000 |

Diagnostic:

- Fixed top 5% selected 5 hidden-good and 4 hidden-bad demos.
- The score-gap selector stopped at 5 demos, all hidden-good, with selected fraction 0.028 and demo/transition purity 1.000.
- This confirms the current failure boundary is not "weighted BC cannot work"; it is that local transition weighting and fixed-prior trajectory weighting can be the wrong weighting mechanism when the useful unlabeled support is extremely sparse.

### Continuous PointNav gap-selection 5-seed hard result

Command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_gap_select_95bad_5seed \
  --seeds 0 1 2 3 4 \
  --bad-fracs 0.95 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 \
  --gap-select-max-fracs 0.10 \
  --gap-select-min-frac 0.02 \
  --posterior-priors 0.05 0.10 \
  --posterior-temperature 0.02
```

Result artifact:

- `results/continuous_pointnav_gap_select_95bad_5seed/REPORT.md`

Closed-loop success at 95% bad unlabeled data:

| method | success | trap |
|---|---:|---:|
| all-data BC | 0.153 | 0.847 |
| positive+unlabeled BC | 0.060 | 0.853 |
| local state-action weighted BC | 0.200 | 0.000 |
| fixed top-demo 5% | 0.887 | 0.113 |
| fixed posterior prior 5% | 0.800 | 0.087 |
| gap-demo BC, max 10% | 1.000 | 0.000 |
| gap-posterior BC, max 10% | 1.000 | 0.000 |
| hidden-good oracle BC | 1.000 | 0.000 |

Gap-selection diagnostics:

| max frac | selected frac | score gap | selected demo purity | selected transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.056 | 0.398 | 1.000 | 1.000 | 10.0 | 0.0 |

Interpretation update:

- The score-gap rule closes the 95% sparse-support failure in this controlled setting: it recovers a pure hidden-good unlabeled support set without using hidden labels and matches the oracle over five seeds.
- This is now the strongest controlled continuous result: it shows a full chain from scarce positive prefixes plus explicit negatives to unlabeled-support recovery, and it distinguishes local state-action weighting from trajectory-level support weighting.
- The method claim should be framed as calibrated trajectory-support recovery / weighted BC, not as naive local transition-weighted BC.
- Later Robomimic sections address the contamination-sweep direction with sequence-aware imitation; the remaining controlled-setting lesson is that trajectory-level support recovery was more reliable than naive local transition weighting.

### Continuous PointNav gap-selection contamination curve

Command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_continuous_pointnav_smoke.py \
  --out-dir results/continuous_pointnav_gap_select_contamination_5seed \
  --seeds 0 1 2 3 4 \
  --bad-fracs 0.50 0.75 0.90 0.95 \
  --bc-steps 6000 --classifier-steps 2500 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --eval-episodes 30 \
  --top-unlabeled-fracs 0.05 0.10 \
  --gap-select-max-fracs 0.10 \
  --gap-select-min-frac 0.02 \
  --posterior-priors 0.05 0.10 \
  --posterior-temperature 0.02
```

The sweep was stopped after the 90% block because the 95% block had already been run completely. The completed 50/75/90 rows were merged with `results/continuous_pointnav_gap_select_95bad_5seed`.

Merged result artifact:

- `results/continuous_pointnav_gap_select_contamination_5seed_merged/REPORT.md`

Closed-loop success:

| bad frac | all-data BC | pos+unlabeled BC | local weighted BC | fixed top-demo 5% | fixed posterior 5% | gap-demo BC | gap-posterior BC | oracle |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.460 | 0.453 | 0.400 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.75 | 0.367 | 0.300 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.90 | 0.233 | 0.247 | 0.000 | 1.000 | 1.000 | 1.000 | 0.800 | 1.000 |
| 0.95 | 0.153 | 0.060 | 0.200 | 0.887 | 0.800 | 1.000 | 1.000 | 1.000 |

Gap-selection diagnostics:

| bad frac | selected frac | selected demo purity | selected transition purity | good demos | bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.048 | 1.000 | 1.000 | 8.6 | 0.0 |
| 0.75 | 0.040 | 1.000 | 1.000 | 7.2 | 0.0 |
| 0.90 | 0.089 | 1.000 | 1.000 | 16.0 | 0.0 |
| 0.95 | 0.056 | 1.000 | 1.000 | 10.0 | 0.0 |

Interpretation update:

- The hard score-gap trajectory-support selector is now robust across the controlled contamination sweep: it matches the hidden-good oracle at all tested bad-demo fractions from 50% to 95%.
- The cleanest method story is binary trajectory-level weighting/selection followed by BC on recovered support. This is still "weighted BC" in a trajectory-level sense, but not local state-action weighted BC.
- Soft gap-posterior weighting is not yet reliable: it matches oracle at 50%, 75%, and 95%, but drops to 0.800 at 90% despite pure selected support. This points to an optimization/weight-shape issue, not a support-identification issue.
- For writing, the controlled diagnostic should emphasize the separation between:
  - weak local weighting / local reranking,
  - brittle fixed-prior support weighting at extreme contamination,
  - robust score-gap trajectory-support recovery.

## 2026-06-22: Robomimic score-gap support transfer

Implemented:

- `scripts/run_robomimic_gmm_smoke.py` now supports `--source positive_plus_classifier_gap_unlabeled_demos`.
- The new source computes mean classifier probability per unlabeled trajectory, sorts demos, and selects the prefix ending at the largest score gap between `--gap-select-min-unlabeled-demos` and `--gap-select-max-unlabeled-demos`.
- `scripts/summarize_robomimic_gmm_runs.py` now reports selector type and selected-demo count, so score-gap rows are not confused with fixed-top-k rows.

Selection diagnostic command:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_gap_selection_diagnostic_seed0 \
  --source positive_plus_classifier_gap_unlabeled_demos \
  --eval-init-mode valid_positive_states \
  --eval-episodes 1 --eval-horizon 1 \
  --steps 1 --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 2 \
  --gap-select-max-unlabeled-demos 80 \
  --gap-select-min-unlabeled-demos 4 \
  --policy-modes mode \
  --seed 0
```

Selection result:

- Fixed top-80 seed-0 selection: 80 unlabeled demos, 60 hidden-positive demos, 9027 source transitions.
- Score-gap seed-0 selection: 23 unlabeled demos, all 23 hidden-positive, 3470 source transitions, selected mean probability 0.907.

Policy commands:

```bash
JAX_PLATFORMS=cpu conda run -n tri-piql \
  python scripts/run_robomimic_gmm_smoke.py \
  --split-path results/robomimic_inspection/can_paired_low_dim/split_indices.json \
  --out-dir results/robomimic_can_gmm_gap_seed0_ckpt20k_mode \
  --source positive_plus_classifier_gap_unlabeled_demos \
  --eval-init-mode valid_positive_states \
  --eval-episodes 10 --eval-horizon 400 \
  --steps 20000 --eval-checkpoints 5000 10000 20000 \
  --classifier-steps 800 \
  --batch-size 512 --hidden-dim 128 --depth 2 \
  --components 5 \
  --gap-select-max-unlabeled-demos 80 \
  --gap-select-min-unlabeled-demos 4 \
  --unlabeled-weight-mode prob \
  --policy-modes mode \
  --seed 0
```

The same 5k setting was run for seeds 1 and 2 with output directories:

- `results/robomimic_can_gmm_gap_seed1_5k_mode`
- `results/robomimic_can_gmm_gap_seed2_5k_mode`

Aggregate artifact:

- `results/robomimic_can_gmm_gap_vs_top80_summary/REPORT.md`

Held-out positive-state success:

| source | selector | ckpt | selected demos | hidden-positive demos | seeds | success |
|---|---|---:|---:|---:|---|---:|
| labeled positives | none | 20k | 0.0 | 0.0 | 0,1,2 | 0.067 |
| fixed top-80 unlabeled | fixed top | 20k | 80.0 | 61.7 | 0,1,2 | 0.300 |
| score-gap unlabeled | score gap | 5k | 25.0 | 25.0 | 0,1,2 | 0.333 |

Seed-0 checkpoint curve for score-gap GMM:

| checkpoint | success |
|---:|---:|
| 5k | 0.400 |
| 10k | 0.200 |
| 20k | 0.100 |

Interpretation update:

- The score-gap support idea transfers to Robomimic selection: across seeds 0/1/2, it selects a much smaller set of unlabeled demos and every selected demo is hidden-positive in the available diagnostics.
- As a learned-policy smoke, score-gap GMM at 5k slightly beats fixed top-80 GMM at 20k on the existing three-seed held-out-state protocol, while using about one third of the selected demonstrations and no hidden-bad selected demos.
- This is not yet a main Robomimic claim. Performance still depends strongly on GMM checkpointing, and seed 0 degrades with more optimizer steps. The immediate Robomimic method issue is policy extraction / early stopping, not support identification.
- The next Robomimic step should either add validation-based checkpoint selection or move the score-gap selected support into a stronger Robomimic imitation backbone.

## 2026-06-22: Robomimic GMM extractor checkpoint diagnostics

Implemented:

- `scripts/run_robomimic_gmm_smoke.py` now supports a source-support validation split via `--gmm-validation-frac`.
- The runner can report checkpoint validation NLL, GMM-mode action MSE, and mixture-mean action MSE.
- `--checkpoint-selection-metric` selects among `support_val_nll`, `support_val_mode_mse`, and `support_val_mean_mse`.
- `--retrain-selected-checkpoint` retrains on the full selected support to the selected step before rollout, avoiding direct selection by rollout success.
- `scripts/summarize_robomimic_gmm_runs.py` now includes feature mode and checkpoint-selection metric in summary tables.

Artifacts:

- `results/robomimic_can_gmm_gap_supportval_seed0_ckpt20k_mode/REPORT.md`
- `results/robomimic_can_gmm_gap_supportval_mode_mse_seed0_ckpt20k/REPORT.md`
- `results/robomimic_can_gmm_gap_history_seed0_ckpt10k_mode/REPORT.md`
- `results/robomimic_can_gmm_extractor_diagnostics_summary/REPORT.md`

Seed-0 checkpoint diagnostics:

| extractor / selector | features | selected ckpt | selected-full success | best checkpoint success |
|---|---|---:|---:|---:|
| support-val NLL | obs | 2.5k | 0.000 | 0.300 at 10k on support-val train |
| support-val mode MSE | obs | 2.5k | 0.000 | 0.300 at 10k on support-val train |
| no validation selector | obs | manual 5k/10k/20k curve | n/a | 0.400 at 5k on full support |
| no validation selector | obs+prev-action+time | manual 5k/10k curve | n/a | 0.100 at 5k |

Checkpoint validation table for the obs support split:

| checkpoint | support train NLL | support val NLL | support val mode MSE | support-val-train rollout success |
|---:|---:|---:|---:|---:|
| 2.5k | -17.422 | 41.458 | 0.035938 | 0.000 |
| 5k | -18.794 | 55.160 | 0.039345 | 0.100 |
| 10k | -19.877 | 80.991 | 0.040724 | 0.300 |
| 20k | -20.714 | 138.568 | 0.045370 | 0.000 |

Interpretation update:

- Support-validation NLL and deterministic validation action error select too early for this local GMM extractor. They prefer 2.5k, but closed-loop rollout improves later and peaks at 10k on the validation-split policy.
- Adding previous-action and time features changes the selected support set but does not improve policy extraction; seed-0 success drops to 0.100 at 5k and 0.000 at 10k.
- The Robomimic bottleneck remains the imitation backbone / policy extraction, not score-gap support identification. The next Robomimic branch should move selected support into a stronger sequence-aware Robomimic policy rather than tune this local diagonal GMM further.
- Environment probe: `robosuite` is installed in `tri-piql`, but `robomimic` and `torch` are not. An official Robomimic BC/RNN backbone would require dependency setup; the fastest next implementation branch is likely a local JAX recurrent BC/GMM extractor on the score-gap selected support.

## 2026-06-22: Official Robomimic BC-RNN-GMM baseline

Installed and validated the stronger Robomimic policy backbone in the `tri-piql` conda environment:

- `torch` / `torchvision` / `torchaudio` CUDA 12.6 wheels.
- Editable Robomimic source checkout at `external/robomimic`.
- `scripts/prepare_robomimic_official_bc_rnn.py` writes HDF5 demo masks and official Robomimic BC-RNN-GMM configs.
- `scripts/evaluate_robomimic_official_policy.py` evaluates saved Robomimic `.pth` checkpoints on the same held-out positive initial states used by the local baselines.

Important config lesson:

- A first official BC-RNN-GMM run removed the Robomimic default actor MLP head (`actor_layer_dims=()`), trained for 5k steps on score-gap support, and got 0.000 success across saved checkpoints.
- Restoring the Robomimic default actor head (`1024,1024`) and training for 20k steps made the baseline work.

Matched seed-0 official-backbone comparison:

| source | support | train demos | hidden-bad selected demos | checkpoint | success |
|---|---|---:|---:|---:|---:|
| labeled positive | 10 labeled positives only | 10 | 0 | 5k | 0.000 |
| labeled positive | 10 labeled positives only | 10 | 0 | 10k | 0.000 |
| labeled positive | 10 labeled positives only | 10 | 0 | 15k | 0.000 |
| labeled positive | 10 labeled positives only | 10 | 0 | 20k | 0.100 |
| score-gap support | 10 positives + 33 selected unlabeled | 43 | 0 | 5k | 0.100 |
| score-gap support | 10 positives + 33 selected unlabeled | 43 | 0 | 10k | 0.700 |
| score-gap support | 10 positives + 33 selected unlabeled | 43 | 0 | 15k | 0.700 |
| score-gap support | 10 positives + 33 selected unlabeled | 43 | 0 | 20k | 0.700 |

Artifacts:

- Summary: `results/robomimic_official_bc_rnn_gap_vs_scarce_seed0_summary/REPORT.md`
- Gap setup: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup/REPORT.md`
- Gap eval: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_eval/REPORT.md`
- Scarce setup: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_setup/REPORT.md`
- Scarce eval: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_eval/REPORT.md`

Interpretation update:

- The baseline issue was not just "BC is too naive"; it was also the backbone/config and optimization budget.
- On Robomimic, the supported story is now trajectory-level score-gap support selection plus a competent sequence-aware BC backbone, not local state-action weighted BC.
- This seed-0 result is strong enough to continue Robomimic, but it is not yet a final claim. Next controls should include more seeds and a same-backbone fixed top-k selected-support baseline.

## 2026-06-22: Official Robomimic fixed top-k support control

Ran the same official Robomimic BC-RNN-GMM backbone and 20k-step budget for fixed top-80 classifier-ranked support.

Artifacts:

- Summary: `results/robomimic_official_bc_rnn_seed0_support_controls/REPORT.md`
- Top-80 setup: `results/robomimic_official_bc_rnn_top80_seed0_mlphead_setup/REPORT.md`
- Top-80 eval: `results/robomimic_official_bc_rnn_top80_seed0_mlphead_eval/REPORT.md`

Support comparison:

| source | train demos | selected unlabeled demos | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|
| labeled positive | 10 | 0 | 0 | 0 | n/a |
| score-gap cutoff | 43 | 33 | 33 | 0 | 1.000 |
| fixed top-80 | 90 | 80 | 72 | 8 | 0.900 |

Rollout comparison:

| source | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| labeled positive | 0.000 | 0.000 | 0.000 | 0.100 |
| score-gap cutoff | 0.100 | 0.700 | 0.700 | 0.700 |
| fixed top-80 | 0.300 | 0.700 | 0.700 | 0.700 |

Interpretation update:

- The fixed top-80 official control matches score-gap at 10k/15k/20k and is better at 5k on this seed.
- Score-gap selected exactly the first 33 demos from the fixed ranking, stopping before lower-confidence additions that introduced hidden-bad demos.
- This weakens any "score-gap is best" Robomimic rollout claim for seed 0. The supported claim is compact pure support: 33 pure selected unlabeled demos match 80 selected demos with 8 hidden-bad demos.
- Next Robomimic tests should stress this cutoff with more seeds and/or heavier contamination. Claims should distinguish "support compactness / purity" from "higher rollout success."

## 2026-06-22: Seed-2 Robomimic coverage stress

Ran support-only diagnostics for seeds 1 and 2, then trained/evaluated seed-2 score-gap and fixed top-80 official Robomimic BC-RNN-GMM controls.

Artifacts:

- Summary: `results/robomimic_official_bc_rnn_seed2_coverage_stress/REPORT.md`
- Seed-2 gap setup/eval:
  - `results/robomimic_official_bc_rnn_gap_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_gap_seed2_mlphead_eval/REPORT.md`
- Seed-2 top-80 setup/eval:
  - `results/robomimic_official_bc_rnn_top80_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top80_seed2_mlphead_eval/REPORT.md`

Support diagnostics:

| seed | source | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---:|---|---:|---:|---:|---:|---:|
| 0 | score-gap cutoff | 43 | 33 | 33 | 0 | 1.000 |
| 0 | fixed top-80 | 90 | 80 | 72 | 8 | 0.900 |
| 1 | score-gap cutoff | 55 | 45 | 45 | 0 | 1.000 |
| 1 | fixed top-80 | 90 | 80 | 70 | 10 | 0.875 |
| 2 | score-gap cutoff | 19 | 9 | 9 | 0 | 1.000 |
| 2 | fixed top-80 | 90 | 80 | 74 | 6 | 0.925 |

Seed-2 rollout comparison:

| source | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| score-gap cutoff | 0.000 | 0.000 | 0.100 | 0.000 |
| fixed top-80 | 0.200 | 0.600 | 0.700 | 0.900 |

Interpretation update:

- Seed 2 shows the largest-gap cutoff can be much too conservative: pure support with only 9 selected unlabeled demos is not enough for the official policy.
- Fixed top-80 wins decisively on seed 2 despite 6 hidden-bad selected demos, because it has much broader hidden-positive coverage.
- The next method branch should be coverage-aware support selection, not more claims that score-gap is best. A candidate is a score-gap rule with a minimum selected-demo floor or a soft high-ranked weighting rule.

## 2026-06-22: Coverage-floor score-gap fixes seed-2 Robomimic

Tested the simplest coverage-aware variant already supported by the selector: score-gap with `--gap-select-min-unlabeled-demos 40`.

Artifacts:

- Summary: `results/robomimic_official_bc_rnn_gap_min40_seed2_summary/REPORT.md`
- Setup: `results/robomimic_official_bc_rnn_gap_min40_seed2_mlphead_setup/REPORT.md`
- Eval: `results/robomimic_official_bc_rnn_gap_min40_seed2_mlphead_eval/REPORT.md`

Support comparison on seed 2:

| source | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|
| original score-gap | 19 | 9 | 9 | 0 | 1.000 |
| score-gap min40 | 76 | 66 | 65 | 1 | 0.985 |
| fixed top-80 | 90 | 80 | 74 | 6 | 0.925 |

Seed-2 rollout comparison:

| source | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| original score-gap | 0.000 | 0.000 | 0.100 | 0.000 |
| score-gap min40 | 0.100 | 0.900 | 0.900 | 0.900 |
| fixed top-80 | 0.200 | 0.600 | 0.700 | 0.900 |

Interpretation update:

- The min40 coverage floor fixes the seed-2 failure while keeping support cleaner than fixed top-80.
- This is now the best candidate Robomimic selector: not pure largest-gap, but coverage-aware score-gap.
- The next research question is how to choose the coverage floor without hidden labels or rollout success. Candidate rules: set a floor from labeled-positive demo count, require a minimum selected transition count, or use a plateau/score-mass criterion.

## 2026-06-22: Three-seed official Robomimic coverage-aware score-gap

Finished the matched three-seed official Robomimic BC-RNN-GMM comparison between coverage-aware score-gap (`--gap-select-min-unlabeled-demos 40`) and fixed top-80 classifier-ranked support.

Artifacts:

- Summary: `results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md`
- Coverage-aware seed-0 eval: `results/robomimic_official_bc_rnn_gap_min40_seed0_mlphead_eval/REPORT.md`
- Coverage-aware seed-1 eval: `results/robomimic_official_bc_rnn_gap_min40_seed1_mlphead_eval/REPORT.md`
- Coverage-aware seed-2 eval: `results/robomimic_official_bc_rnn_gap_min40_seed2_mlphead_eval/REPORT.md`
- Fixed top-80 seed-1 eval: `results/robomimic_official_bc_rnn_top80_seed1_mlphead_eval/REPORT.md`

Support comparison:

| method | selected unlabeled | hidden-positive selected | hidden-bad selected | aggregate purity |
|---|---:|---:|---:|---:|
| coverage-aware score-gap | 184 | 177 | 7 | 0.962 |
| fixed top-80 | 240 | 216 | 24 | 0.900 |

Three-seed mean rollout success:

| method | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| coverage-aware score-gap | 0.133 | 0.800 | 0.867 | 0.900 |
| fixed top-80 | 0.233 | 0.700 | 0.733 | 0.833 |

Interpretation update:

- Coverage-aware score-gap is the current best Robomimic selector: worse at 5k, but better at 10k/15k/20k mean success and cleaner than fixed top-80.
- The correct claim is not that naive weighted BC is best. The supported claim is that scarce positive/negative labels can select useful unlabeled support, and that selection needs a purity-coverage tradeoff.
- The next method step is to choose the coverage floor without hidden labels or rollout success, then test whether that rule survives heavier contamination or another Robomimic task.
- Implementation hygiene: `scripts/prepare_robomimic_official_bc_rnn.py` now tags future HDF5 masks by selector settings, e.g. gap min/max and top-k, to avoid collisions between original score-gap, min40 score-gap, and top-k reruns.

## 2026-06-22: Label-budget coverage floor formalization

Converted the ad hoc `min40` score-gap floor into a hidden-label-free rule:

`effective_min_selected_unlabeled_demos = max(abs_min, ceil(multiplier * labeled_positive_demo_count))`

with `multiplier = 4.0` and `abs_min = 4`. Because the Robomimic split uses 10 labeled-positive demos, this gives an effective floor of 40.

Code changes:

- `scripts/run_robomimic_gmm_smoke.py` now supports `--gap-select-min-labeled-positive-multiplier`.
- `scripts/prepare_robomimic_official_bc_rnn.py` exposes the same flag and tags masks as `posx4_max80`, avoiding collisions with earlier `min40` masks.
- `scripts/run_robomimic_window_gmm_smoke.py` accepts the same flag for compatibility with the shared selector.

Support-only verification:

| seed | same selected demos as min40 | train demos | selected unlabeled | hidden-bad selected | effective min | train filter key |
|---:|---|---:|---:|---:|---:|---|
| 0 | yes | 83 | 73 | 6 | 40 | `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_train` |
| 1 | yes | 55 | 45 | 0 | 40 | `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_train` |
| 2 | yes | 76 | 66 | 1 | 40 | `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_train` |

Artifacts:

- `results/robomimic_official_bc_rnn_gap_posx4_seed0_mlphead_setup/REPORT.md`
- `results/robomimic_official_bc_rnn_gap_posx4_seed1_mlphead_setup/REPORT.md`
- `results/robomimic_official_bc_rnn_gap_posx4_seed2_mlphead_setup/REPORT.md`

Interpretation update:

- The current best result can now be described as coverage-aware score-gap with a label-budget floor, not as a hand-picked `min40` constant.
- Since the selected demo IDs exactly match the evaluated min40 runs, the three-seed rollout result carries over without retraining.
- The next stress test should vary contamination or task while keeping the `4 x labeled-positive` rule fixed.

## 2026-06-22: Heavy-contamination Robomimic stress check

Created a stress split with only 20 hidden-positive unlabeled demos and 80 hidden-bad unlabeled demos, instead of the default 80/80 balanced unlabeled pool.

Code changes:

- `scripts/inspect_robomimic_dataset.py` now supports `--unlabeled-positive-count` and `--unlabeled-negative-count`.
- `scripts/prepare_robomimic_official_bc_rnn.py` now supports `--mask-prefix`, used here as `tri_stress_p20_b80` to avoid HDF5 mask collisions with the default split.

Artifacts:

- Summary: `results/robomimic_official_bc_rnn_stress_p20_b80_seed0_summary/REPORT.md`
- Stress split: `results/robomimic_inspection/can_paired_low_dim_stress_pos20_bad80/REPORT.md`
- Selector score analysis: `results/robomimic_selector_score_analysis_stress_p20_b80/REPORT.md`
- Matched three-selector summary: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`
- Coverage-aware eval seed 0: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Coverage-aware eval seed 1: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Coverage-aware eval seed 2: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed2_mlphead_eval/REPORT.md`
- Precision-biased top-20 eval seed 0: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Precision-biased top-20 eval seed 1: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Precision-biased top-20 eval seed 2: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed2_mlphead_eval/REPORT.md`
- Fixed top-80 eval seed 0: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Fixed top-80 eval seed 1: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Fixed top-80 eval seed 2: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_eval/REPORT.md`

Support-only diagnostics:

| method | selected unlabeled | hidden-positive selected | hidden-bad selected | aggregate purity |
|---|---:|---:|---:|---:|
| coverage-aware score-gap posx4 | 157 | 60 | 97 | 0.382 |
| precision-biased top-20 | 60 | 45 | 15 | 0.750 |
| fixed top-80 | 240 | 60 | 180 | 0.250 |

Seed-0 rollout comparison:

| method | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| coverage-aware score-gap posx4 | 0.200 | 0.400 | 0.300 | 0.400 |
| precision-biased top-20 | 0.000 | 0.500 | 0.300 | 0.800 |
| fixed top-80 | 0.000 | 0.000 | 0.300 | 0.300 |

Matched three-selector rollout:

| method | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| top-20 mean | 0.000 | 0.367 | 0.433 | 0.667 |
| posx4 mean | 0.067 | 0.267 | 0.300 | 0.333 |
| fixed top-80 mean | 0.067 | 0.233 | 0.167 | 0.233 |
| top-20 minus posx4 mean | -0.067 | 0.100 | 0.133 | 0.333 |
| top-20 minus fixed top-80 mean | -0.067 | 0.133 | 0.267 | 0.433 |

Interpretation update:

- The fixed `4 x` labeled-positive coverage rule survives the support-selection stress better than fixed top-80, but it is too coverage-biased under 80% bad unlabeled data.
- A precision-biased top-20 rule is much cleaner in this stress pool and beats both controls in the matched three-seed policy comparison, reaching mean 0.667 success at 20k versus 0.333 for posx4 and 0.233 for fixed top-80.
- This reframes the method direction: balanced Robomimic data favors coverage-aware score-gap, while heavy contamination needs an adaptive purity/coverage rule rather than a fixed coverage floor.

## 2026-06-22: Adaptive Robomimic positive-mass selector

Added a hidden-label-free adaptive support rule to `scripts/analyze_robomimic_selector_scores.py`.

Rule:

- Score unlabeled demos by mean classifier probability.
- Estimate unlabeled positive-demo mass by calibrating demo scores between the labeled negative and labeled positive demo-score means.
- If estimated positive mass is at least the `4 x labeled-positive` coverage floor, use coverage-aware score-gap.
- Otherwise, use precision mode with top `2 x labeled-positive` unlabeled demos.

Artifacts:

- Summary: `results/robomimic_adaptive_posmass_selector_summary/REPORT.md`
- Balanced analysis: `results/robomimic_selector_score_analysis_balanced_80p80b/REPORT.md`
- Stress analysis: `results/robomimic_selector_score_analysis_stress_p20_b80/REPORT.md`

Adaptive selector decisions:

| split | estimated positive mass | floor | adaptive mode | aggregate support purity |
|---|---:|---:|---|---:|
| balanced 80p/80b | 80.4-84.6 | 40 | coverage-gap | 0.962 |
| stress 20p/80b | 32.6-35.9 | 40 | precision top20 | 0.750 |

Policy results carried over from the matched official Robomimic runs:

| split | adaptive selector | 5k | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|
| balanced 80p/80b | coverage-gap | 0.133 | 0.800 | 0.867 | 0.900 |
| stress 20p/80b | precision top20 | 0.000 | 0.367 | 0.433 | 0.667 |

Interpretation update:

- The adaptive rule makes the current Robomimic story less hand-picked: one hidden-label-free rule selects coverage when the unlabeled pool has enough estimated positive mass and precision when the coverage floor would over-select bad demos.
- This two-endpoint result motivated the later mass-capped positive-count sweep below, which found and corrected an intermediate-regime support over-expansion issue.

## 2026-06-22: Mass-capped adaptive selector sweep

Added a positive-count sweep and refined the adaptive selector with a hidden-label-free mass cap.

Artifacts:

- Current selector summary: `results/robomimic_adaptive_masscap_selector_summary/REPORT.md`
- Positive-count sweep: `results/robomimic_adaptive_selector_sweep_pos_count/REPORT.md`
- Intermediate three-seed policy check: `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`
- Updated analyzer: `scripts/analyze_robomimic_selector_scores.py`
- Sweep runner: `scripts/run_robomimic_adaptive_selector_sweep.py`

Refinement:

- The earlier `adaptive_posmass` rule switches from precision to coverage when estimated positive mass exceeds the `4 x labeled-positive` floor.
- The sweep found an intermediate-regime rough edge: at 40 hidden-positive / 80 hidden-bad unlabeled demos, the original switch selects 74 demos with 34 hidden-bad demos, purity 0.541.
- The refined `adaptive_masscap` rule keeps the same precision/coverage decision but caps coverage when the score-gap cut selects more than `1.25 x` estimated positive mass. In the 40/80 intermediate mixture it selects 50 demos with 13.667 hidden-bad demos, purity 0.728 and recall 0.908.

Mass-capped sweep summary with 80 hidden-bad unlabeled demos:

| hidden-positive unlabeled | adaptive mode | selected | hidden-positive | hidden-bad | purity | recall |
|---:|---|---:|---:|---:|---:|---:|
| 5 | precision_top20 | 20.000 | 5.000 | 15.000 | 0.250 | 1.000 |
| 10 | precision_top20 | 20.000 | 10.000 | 10.000 | 0.500 | 1.000 |
| 20 | precision_top20 | 20.000 | 15.000 | 5.000 | 0.750 | 0.750 |
| 30 | coverage_gap,top_estimated_mass | 46.333 | 28.333 | 18.000 | 0.616 | 0.944 |
| 40 | top_estimated_mass | 50.000 | 36.333 | 13.667 | 0.728 | 0.908 |
| 50 | coverage_gap,top_estimated_mass | 49.333 | 41.000 | 8.333 | 0.833 | 0.820 |
| 60 | coverage_gap | 53.667 | 48.667 | 5.000 | 0.910 | 0.811 |
| 70 | coverage_gap | 54.000 | 51.667 | 2.333 | 0.963 | 0.738 |
| 80 | coverage_gap | 61.333 | 59.000 | 2.333 | 0.968 | 0.737 |

Endpoint policy status:

- Balanced 80p/80b: mass-capped rule matches coverage-gap, so it carries over the existing official BC-RNN-GMM 20k mean success 0.900.
- Stress 20p/80b: mass-capped rule matches top20 precision, so it carries over the existing official BC-RNN-GMM 20k mean success 0.667.

Intermediate 40p/80b official BC-RNN-GMM three-seed result:

| selector | selected unlabeled mean | hidden-positive mean | hidden-bad mean | purity mean | 5k | 10k | 15k | 20k | best-per-seed mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| original coverage-gap | 74.0 | 40.0 | 34.0 | 0.541 | 0.167 | 0.333 | 0.567 | 0.600 | 0.667 |
| top20 precision | 20.0 | 19.7 | 0.3 | 0.983 | 0.033 | 0.567 | 0.667 | 0.700 | 0.700 |

Interpretation update:

- The refined selector is stronger for a paper claim because it keeps the endpoint wins while identifying and correcting a contamination-dependent support-expansion failure.
- The three-seed 40p/80b policy result supports the refinement: mass-capped support beats original coverage-gap by 0.167 at 15k and 0.133 at 20k while cutting hidden-bad selected demos from 34.0 to 13.7 on average.
- Top20 precision remains a strong control. It has the best 10k mean and nearly pure support, but it uses only 19.7 of the 40 hidden-positive demos on average.
- The honest Robomimic claim is adaptive support selection, not a fixed support size: balanced data favors coverage, heavy contamination favors precision, and this intermediate split favors mass-capped coverage by 15k/20k.

## 2026-06-22: Robomimic bad-label ablation and no-bad policy control

Added a no-bad-label support diagnostic and an official BC-RNN-GMM policy control for the strongest no-bad selector.

Code changes:

- `scripts/run_robomimic_bad_label_ablation.py`: support-only ablation comparing the current positive-vs-negative classifier selector against positive-only nearest-neighbor ranking and positive-vs-unlabeled scoring.
- `scripts/run_robomimic_gmm_smoke.py`: added `positive_plus_positive_nn_top_unlabeled_demos` support source.
- `scripts/prepare_robomimic_official_bc_rnn.py`: exposes the same positive-only NN support source for official BC-RNN-GMM training.

Artifacts:

- Support ablation: `results/robomimic_bad_label_ablation/REPORT.md`
- No-bad policy control: `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_3seed_summary/REPORT.md`
- Updated 40p/80b comparison: `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`

Support-only result at 40 hidden-positive / 80 hidden-bad:

| selector | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 |
| positive-only NN top40 | 40.0 | 31.0 | 9.0 | 0.775 |
| positive-vs-unlabeled top40 | 40.0 | 16.0 | 24.0 | 0.400 |

Official BC-RNN-GMM policy result on the 40p/80b split:

| selector | 5k | 10k | 15k | 20k | best-per-seed mean |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| positive-only NN top40 | 0.167 | 0.433 | 0.533 | 0.633 | 0.767 |
| coverage-gap | 0.167 | 0.333 | 0.567 | 0.600 | 0.667 |
| top20 precision | 0.033 | 0.567 | 0.667 | 0.700 | 0.700 |

Interpretation update:

- Positive-vs-unlabeled is a weak no-bad baseline; treating contaminated unlabeled data as background loses many hidden positives.
- Positive-only nearest-neighbor support is a strong no-bad-label control, not a strawman. It ties masscap on best-per-seed mean.
- Masscap is still better at fixed 10k/15k/20k checkpoints and keeps more hidden-positive support. This supports a fixed-budget stability claim for explicit bad-aware adaptive selection.
- The paper should not claim that bad labels are strictly necessary on this Robomimic split. The stronger, more defensible claim is that bad labels help choose a more stable precision/coverage tradeoff.

## 2026-06-22: Robomimic Lift MG cross-task screen

Downloaded and inspected a second Robomimic low-dimensional task:

- Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`
- Inspection: `results/robomimic_inspection/lift_mg_low_dim_sparse/REPORT.md`
- Selector analysis: `results/robomimic_lift_mg_selector_score_analysis/REPORT.md`
- Policy summary: `results/robomimic_lift_mg_official_bc_rnn_seed0_summary/REPORT.md`

Code changes:

- `scripts/inspect_robomimic_dataset.py`: now supports non-masked Robomimic datasets with a deterministic stratified fallback train/valid split and optional shuffled label pools.
- `scripts/prepare_robomimic_official_bc_rnn.py`: added `all_train_demos` and skips unnecessary selector training for pure sources like labeled-positive and all-train controls.
- `scripts/run_robomimic_gmm_smoke.py` and `scripts/prepare_robomimic_official_bc_rnn.py`: added a hidden-label-free demo-threshold selector, including the `pos_min` rule that thresholds unlabeled demos at the minimum labeled-positive demo score.

Lift MG sparse dataset statistics:

| total demos | reward-positive | zero-return | validation positive | validation negative |
|---:|---:|---:|---:|---:|
| 1500 | 316 | 1184 | 30 | 30 |

Default split after holding out validation demos:

| pool | positive | negative |
|---|---:|---:|
| labeled | 10 | 10 |
| unlabeled | 276 | 1144 |
| all train demos | 286 | 1154 |

Support result:

| source | train demos | train positive | train negative | selected unlabeled | selected hidden positive | selected hidden bad | purity |
|---|---:|---:|---:|---:|---:|---:|---:|
| labeled positives | 10 | 10 | 0 | 0 | 0 | 0 | n/a |
| top-80 selected support | 90 | 87 | 3 | 80 | 77 | 3 | 0.963 |
| top-160 selected support | 170 | 164 | 6 | 160 | 154 | 6 | 0.963 |
| pos-min calibrated threshold | 240 | 213 | 27 | 230 | 203 | 27 | 0.883 |
| adaptive masscap | 289 | 233 | 56 | 279 | 223 | 56 | 0.799 |
| all train demos | 1440 | 286 | 1154 | 1420 | 276 | 1144 | 0.194 |
| all train positives | 286 | 286 | 0 | 276 | 276 | 0 | 1.000 |

Official BC-RNN-GMM seed-0 policy screen:

- Backbone: same official Robomimic BC-RNN-GMM as Can, `1024,1024` actor head, 2-layer LSTM with hidden size 400, 5 GMM modes.
- Training budget: 20k optimizer steps, checkpoints at 5k / 10k / 15k / 20k.
- Evaluation: 10 held-out reward-positive Lift initial states, horizon 150.

| source | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| labeled positives | 0.100 | 0.000 | 0.000 | 0.200 | 0.200 |
| top-80 selected support | 0.000 | 0.300 | 0.100 | 0.200 | 0.300 |
| top-160 selected support | 0.000 | 0.500 | 0.300 | 0.700 | 0.700 |
| pos-min calibrated threshold | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |
| adaptive masscap | 0.100 | 0.400 | 0.600 | 0.600 | 0.600 |
| all train demos | 0.100 | 0.100 | 0.300 | 0.100 | 0.300 |
| all train positives | 0.200 | 0.300 | 0.700 | 0.800 | 0.800 |

Interpretation update:

- Robomimic v1.5 only has paired low-dimensional data for Can. Lift MG is not paired same-initial-state good/bad data; labels are derived from sparse reward.
- Lift validates cross-task support purification: the classifier-ranked top-160 support turns a 19.4% reward-positive unlabeled pool into 96.3% selected-positive support.
- The oracle all-positive row reaches 0.800 success at 20k, so Lift is learnable with the same backbone and evaluation protocol.
- The selected-support policy result is coverage-limited, not task-limited. Top-80 recovers 77 hidden positives and reaches only 0.200 at 20k; top-160 recovers 154 hidden positives and reaches 0.700 at 20k, near the 0.800 oracle-positive row.
- The hidden-label-free adaptive masscap rule chooses broader support, with 223 hidden positives and 56 bad demos, and reaches 0.600 at 15k/20k. It is below manual top-160 on this seed but still far above all-demo cloning at 20k.
- The new hidden-label-free `pos_min` threshold uses only labeled positive/negative classifier calibration, selects 203 hidden positives plus 27 bad demos, and reaches 0.800 at 20k. On this seed it matches the oracle all-positive row, so the earlier Lift gap was a selector calibration issue rather than a task-capability failure.
- This should still be treated as a strong one-seed screen rather than a final benchmark. It supports the selector mechanism beyond Can, but a paper-facing cross-task claim still needs more seeds.

## 2026-06-22: Robomimic Lift MG pos-min three-seed follow-up

Extended the hidden-label-free `pos_min` selector to seeds 1 and 2.

Artifacts:

- Three-seed summary: `results/robomimic_lift_mg_official_bc_rnn_posmin_3seed_summary/REPORT.md`
- Seed 1 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_eval/REPORT.md`
- Seed 2 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_eval/REPORT.md`

Support result:

| seed | train demos | selected unlabeled | hidden positive | hidden bad | purity |
|---:|---:|---:|---:|---:|---:|
| 0 | 240 | 230 | 203 | 27 | 0.883 |
| 1 | 254 | 244 | 206 | 38 | 0.844 |
| 2 | 248 | 238 | 206 | 32 | 0.866 |
| mean | 247.3 | 237.3 | 205.0 | 32.3 | 0.864 |

Official BC-RNN-GMM policy result:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |
| 1 | 0.200 | 0.200 | 0.500 | 0.400 | 0.500 |
| 2 | 0.000 | 0.200 | 0.500 | 0.800 | 0.800 |
| mean | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |

Interpretation update:

- Support purification is robust: `pos_min` turns a 19.4% reward-positive unlabeled pool into 86.4% selected-positive support on average.
- The policy evidence is positive but not claim-complete. Seeds 0 and 2 reach 0.800 at 20k, but seed 1 peaks at 0.500 at 15k and drops to 0.400 at 20k.
- The cross-task Lift claim should be support-transfer plus promising policy performance, not a final benchmark win yet. Same-seed all-positive and all-demo controls were run next; the remaining mechanism question is a hidden-label-free checkpoint-selection rule that would avoid seed 1's 20k drop.

## 2026-06-22: Robomimic Lift MG same-seed controls

Ran the missing Lift controls for seeds 1 and 2:

- All-positive oracle support: `results/robomimic_lift_mg_official_bc_rnn_allpositive_seed1_eval/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_allpositive_seed2_eval/REPORT.md`
- All-demo mixed-log cloning: `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed1_eval/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed2_eval/REPORT.md`
- Consolidated comparison: `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`

Three-seed policy result:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |
| all train positives | 0.167 | 0.433 | 0.700 | 0.633 | 0.733 |
| all train demos | 0.067 | 0.033 | 0.167 | 0.200 | 0.267 |

Interpretation update:

- The same-backbone all-demo baseline is genuinely weak on Lift despite using 1440 train demos; bad-dominated mixed cloning reaches only 0.200 mean success at 20k.
- `pos_min` is far above all-demo cloning and close to all-positive oracle support. It is slightly higher than all-positive at fixed 20k (0.667 vs 0.633) but slightly lower on best-per-seed (0.700 vs 0.733), so the honest claim is near-oracle, not oracle-dominating.
- Seed 1's 20k drop is not solely a selector failure: all-positive oracle support also peaks at 15k (0.700) and drops at 20k (0.500). This motivates checkpoint-selection or fixed-15k reporting if we want a less brittle Lift number.

## 2026-06-22: Robomimic Lift MG checkpoint-selection diagnostic

Scored all saved Lift official BC-RNN-GMM checkpoints for pos-min, all-positive oracle, and all-demo cloning with Robomimic validation log-likelihood.

Artifact:

- `results/robomimic_lift_mg_checkpoint_selection_posmin_oracle_alltrain/REPORT.md`

Mean selected rollout success by offline filter:

| filter | pos-min | all-positive | all-demo |
|---|---:|---:|---:|
| train-support likelihood | 0.667 | 0.633 | 0.200 |
| random valid-all likelihood | 0.200 | 0.167 | 0.200 |
| valid-positive likelihood | 0.600 | 0.467 | 0.200 |
| labeled-positive likelihood | 0.667 | 0.633 | 0.200 |

Interpretation update:

- Simple offline likelihood does not rescue seed 1 or justify best-checkpoint reporting.
- Random valid-all likelihood is actively misleading because the held-out validation set contains many failed demos; it selects early checkpoints for the selected-support policies even when later checkpoints roll out much better.
- Train-support and labeled-positive likelihood mostly pick 20k, so the fixed-budget comparison remains the cleanest Lift result: pos-min is far above all-demo and close to oracle-positive, but not a claimed oracle-dominating method.
- This also explains why naive mixed-log BC is so weak: optimizing likelihood on bad-dominated support is not aligned with successful rollout behavior.

## 2026-06-22: Robomimic Lift MG weighted BC baseline

Added a soft weighted BC baseline for the official Robomimic BC-RNN-GMM backbone.

Code changes:

- `scripts/run_robomimic_gmm_smoke.py`: added `positive_plus_classifier_weighted_unlabeled_demos` as a shared classifier scoring source.
- `scripts/prepare_robomimic_official_bc_rnn.py`: writes classifier-probability demo weights for weighted official BC setup.
- `scripts/train_robomimic_official_weighted_sampler.py`: local official-backbone trainer that uses a demo-level `WeightedRandomSampler` while saving normal Robomimic checkpoints.

Artifacts:

- Three-seed weighted summary: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_3seed_summary/REPORT.md`
- Updated controls table: `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`

Weighted sampler support:

| seed | train demos | hidden positive unlabeled | hidden bad unlabeled | hidden-positive mean weight | hidden-bad mean weight |
|---:|---:|---:|---:|---:|---:|
| 0 | 1430 | 276 | 1144 | 0.755 | 0.163 |
| 1 | 1430 | 276 | 1144 | 0.761 | 0.164 |
| 2 | 1430 | 276 | 1144 | 0.754 | 0.159 |
| mean | 1430 | 276 | 1144 | 0.757 | 0.162 |

Three-seed policy result:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| pos-min hard support | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |
| classifier probability weighted sampler | 0.067 | 0.300 | 0.500 | 0.533 | 0.633 |
| all train positives | 0.167 | 0.433 | 0.700 | 0.633 | 0.733 |
| all train demos | 0.067 | 0.033 | 0.167 | 0.200 | 0.267 |

Interpretation update:

- Weighted BC is not inherently bad. Once implemented on the official sequence backbone, classifier weighting is much better than all-demo cloning.
- It is still lower than hard `pos_min` support at fixed 20k (`0.533` vs `0.667`). Keeping all hidden-bad sequences at nonzero weight appears to inject enough conflicting behavior to hurt the sequence BC endpoint.
- The paper-facing robotics comparison should include both soft weighted BC and hard support selection. The defensible claim is not "weighted BC is bad"; it is that explicit bad-aware classifier scores help both, and calibrated hard support gives the cleaner fixed-budget result on Lift.

## 2026-06-22: Robomimic Can 40p/80b weighted BC control

Added the same official-backbone soft weighted BC baseline to the intermediate Can split with 40 hidden-positive and 80 hidden-bad unlabeled demos.

Artifacts:

- Three-seed weighted summary: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_3seed_summary/REPORT.md`
- Updated selector comparison: `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`

Weighted sampler support:

| seed | train demos | weighted unlabeled | hidden positive | hidden bad | hidden-positive mean weight | hidden-bad mean weight |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 130 | 120 | 40 | 80 | 0.677 | 0.333 |
| 1 | 130 | 120 | 40 | 80 | 0.692 | 0.332 |
| 2 | 130 | 120 | 40 | 80 | 0.683 | 0.313 |
| mean | 130 | 120 | 40 | 80 | 0.684 | 0.326 |

Three-seed policy result:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| classifier probability weighted sampler | 0.267 | 0.600 | 0.700 | 0.567 | 0.700 |
| coverage-gap | 0.167 | 0.333 | 0.567 | 0.600 | 0.667 |
| top20 precision | 0.033 | 0.567 | 0.667 | 0.700 | 0.700 |
| positive-only NN top40 | 0.167 | 0.433 | 0.533 | 0.633 | 0.767 |

Interpretation update:

- Weighted BC is not a bad baseline on Can either. It has the best 10k mean and nearly matches mass-capped adaptive at 15k.
- The fixed 20k endpoint still favors hard support selection: mass-capped adaptive reaches 0.733 while weighted BC reaches 0.567.
- This answers the baseline concern: the project should not claim naive weighted BC is weak. The better claim is that bad-aware classifier scores are useful, and turning them into calibrated hard support gives cleaner fixed-budget behavior when the unlabeled pool contains many bad demonstrations.

## 2026-06-22: Robomimic Can MG sparse stress diagnostic

Downloaded and inspected the official Robomimic Can machine-generated sparse low-dimensional dataset.

Artifacts:

- Dataset inspection: `results/robomimic_inspection/can_mg_low_dim_sparse/REPORT.md`
- One-seed diagnostic summary: `results/robomimic_can_mg_official_bc_rnn_seed0_summary/REPORT.md`

Dataset split:

| item | count |
|---|---:|
| total demos | 3900 |
| reward-positive demos | 718 |
| reward-negative demos | 3182 |
| labeled positives | 10 |
| labeled negatives | 10 |
| hidden-positive unlabeled | 688 |
| hidden-bad unlabeled | 3152 |
| validation positives | 20 |

Support diagnostics:

| source | selected unlabeled | hidden positive | hidden bad | purity |
|---|---:|---:|---:|---:|
| pos-min calibrated threshold | 1039 | 485 | 554 | 0.467 |
| pos-p10 calibrated threshold | 714 | 378 | 336 | 0.529 |
| classifier probability weighted sampler | 3840 | 688 | 3152 | 0.179 |
| adaptive masscap | 6 | 3 | 3 | 0.500 |
| coverage-gap posx4 max800 | 799 | 403 | 396 | 0.504 |
| top160 selected support | 160 | 113 | 47 | 0.706 |

One-seed official BC-RNN-GMM policy result:

| source | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| top160 selected support | 0.000 | 0.100 | 0.100 | 0.000 | 0.100 |
| pos-p10 calibrated threshold | 0.000 | 0.000 | 0.100 | 0.300 | 0.300 |
| classifier probability weighted sampler | 0.000 | 0.300 | 0.200 | 0.400 | 0.400 |
| all train positives | 0.000 | 0.000 | 0.100 | 0.400 | 0.400 |
| all train demos | 0.000 | 0.000 | 0.100 | 0.200 | 0.200 |

Interpretation update:

- Can MG sparse is learnable but weaker than paired Can: all-positive oracle support reaches 0.400 at 20k.
- The bad-dominated mixed log is harmful: all-demo cloning reaches only 0.200 at 20k.
- Current hidden-label-free selected-support rules only partially transfer. Pos-min over-selects many false positives, adaptive gap under-selects because classifier scores saturate, and top160 is too coverage-limited for policy learning.
- Pos-p10 is the best Can MG selected-support row so far: it beats all-demo cloning at 20k (`0.300` vs `0.200`) and is close to the all-positive oracle row (`0.400`), but it is still not a paper-facing win.
- Soft weighted sampling is best on this one-seed Can MG stress screen: it reaches 0.400 at 20k, matching all-positive oracle support despite keeping every bad unlabeled demo at nonzero weight. Hidden positives get much higher mean demo weight than hidden bad demos (0.885 vs 0.432), which appears enough when broad coverage matters.
- This should be kept as a calibration stress diagnostic. It points to the next method problem: decide when classifier scores should become hard support and when they should remain soft sampling weights under large bad-dominated unlabeled pools.

## 2026-06-22: Paper-facing claim package

Added a consolidated paper-facing evidence package:

- Claim package: `results/PAPER_CLAIM_PACKAGE.md`
- Continuous mechanism table: `results/paper_tables/continuous_pointnav_table.csv`
- Robotics core table: `results/paper_tables/robotics_core_table.csv`
- Claim matrix: `results/paper_tables/claim_matrix.csv`

Main conclusion:

- The baseline concern is resolved in the honest direction: classifier-probability weighted BC is strong when implemented with the official Robomimic BC-RNN-GMM backbone.
- The supported paper story is not that weighted BC is bad. It is that tri-signal labels learn a useful score, and the method contribution should be the calibrated conversion from scores to hard support or soft sampling under different precision/coverage regimes.
- Paper-ready positive evidence: Continuous PointNav 5-seed mechanism result, Robomimic Can paired selector results across balanced/intermediate/heavy contamination, and Lift MG three-seed transfer.
- Diagnostic/not-main evidence: Can MG sparse one-seed stress, Minari negatives, and earlier under-configured Robomimic policy extractors.

## 2026-06-22: Hard-vs-soft score conversion diagnostic

Added a support-only diagnostic that consolidates existing Robomimic selector-score analyses and current fixed-20k policy anchors:

- Script: `scripts/summarize_robomimic_hard_soft_tradeoff.py`
- Report: `results/robomimic_hard_soft_tradeoff_summary/REPORT.md`
- CSVs: `diagnostic_summary.csv`, `rule_summary.csv`, `policy_anchor_summary.csv`

Result:

| analysis | observed policy mode | support candidate | score >= 0.95 demos | best clean hard prefix |
|---|---|---|---:|---:|
| Can paired 80p/80b | hard coverage | hard-support candidate | 0.0 | 80 |
| Can paired 40p/80b | hard mass-capped | hard-support candidate | 0.0 | 50 |
| Can paired 20p/80b | hard precision | hard-support candidate | 0.0 | 20 |
| Lift MG sparse | hard threshold | hard-support candidate | 85.3 | 320 |
| Can MG sparse | soft weighting | soft-weighting candidate | 652.3 | 160 |

Interpretation:

- This reframes weighted BC as a branch of the method family, not a weak baseline.
- Paired Can and Lift have sufficiently clean hard prefixes, matching the hard-support policy wins.
- Can MG has a large high-score plateau and the clean hard prefix is much smaller than that plateau; the later weighted three-seed follow-up makes this a soft-coverage hypothesis rather than a clean soft-weighting win.
- The diagnostic still uses hidden labels to evaluate purity, so the next method step is to replace that purity term with a hidden-label-free score-shape or validation proxy.

## 2026-06-22: Can MG weighted BC three-seed follow-up

Ran seeds 1 and 2 for the official Robomimic Can MG classifier-probability weighted sampler, matching the seed-0 setup:

- Setup seed 1: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed1_setup/REPORT.md`
- Eval seed 1: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed1_eval/REPORT.md`
- Setup seed 2: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed2_setup/REPORT.md`
- Eval seed 2: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed2_eval/REPORT.md`
- Summary: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_3seed_summary/REPORT.md`

Support/weight diagnostics:

| seed | train demos | weighted unlabeled | hidden positive | hidden bad | hidden-positive mean weight | hidden-bad mean weight |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3850 | 3840 | 688 | 3152 | 0.885 | 0.432 |
| 1 | 3850 | 3840 | 688 | 3152 | 0.871 | 0.410 |
| 2 | 3850 | 3840 | 688 | 3152 | 0.878 | 0.416 |
| mean | 3850 | 3840 | 688 | 3152 | 0.878 | 0.419 |

Policy results:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.000 | 0.300 | 0.200 | 0.400 | 0.400 |
| 1 | 0.000 | 0.100 | 0.400 | 0.300 | 0.400 |
| 2 | 0.000 | 0.000 | 0.000 | 0.300 | 0.300 |
| mean | 0.000 | 0.133 | 0.200 | 0.333 | 0.367 |

Interpretation update:

- The three-seed weighted follow-up gives a modest but nontrivial Can MG signal before matched controls are considered.
- Classifier weights are stable and meaningful: hidden-positive demos receive about twice the mean weight of hidden-bad demos across seeds.
- Every weighted seed reaches nonzero success by 20k, but fixed 20k mean is only `0.333` and best-per-seed mean is `0.367`.
- Can MG should remain a calibration stress case until the matched controls are summarized and folded into the hard-vs-soft interpretation.

## 2026-06-22: Can MG matched controls three-seed follow-up

Ran the missing official Robomimic Can MG control seeds for all-positive oracle support, all-demo cloning, and pos-p10 hard support.

New artifacts:

- Summary: `results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`
- All-positive seed 1/2 evals: `results/robomimic_can_mg_official_bc_rnn_allpositive_seed1_eval/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_allpositive_seed2_eval/REPORT.md`
- All-demo seed 1/2 evals: `results/robomimic_can_mg_official_bc_rnn_alltrain_seed1_eval/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_alltrain_seed2_eval/REPORT.md`
- Pos-p10 seed 1/2 evals: `results/robomimic_can_mg_official_bc_rnn_posp10_seed1_eval/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_posp10_seed2_eval/REPORT.md`

Matched three-seed policy means:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| classifier probability weighted sampler | 0.000 | 0.133 | 0.200 | 0.333 | 0.367 |
| all train positives | 0.000 | 0.033 | 0.133 | 0.200 | 0.233 |
| all train demos | 0.000 | 0.000 | 0.200 | 0.100 | 0.233 |
| pos-p10 calibrated threshold | 0.000 | 0.000 | 0.100 | 0.167 | 0.167 |

Interpretation update:

- The matched controls now make weighted sampling the best fixed-20k Can MG row, not just a seed-0 artifact.
- This does not make Can MG a main positive benchmark result. The absolute success is modest, and the result should stay framed as a stress diagnostic for hard-vs-soft score conversion.
- All-demo cloning remains weak at fixed 20k (`0.100`), so the bad-dominated mixed log is still harmful.
- Pos-p10 purifies the pool to about `0.538` selected-positive purity but appears too coverage-limited for this split.

## 2026-06-22: Hidden-free hard/soft router candidate

Added a first method-level router that removes the hidden-label purity term from the previous hard-vs-soft diagnostic.

Artifacts:

- Script: `scripts/summarize_robomimic_hidden_free_router.py`
- Report: `results/robomimic_hidden_free_router_summary/REPORT.md`
- CSV: `results/robomimic_hidden_free_router_summary/router_summary.csv`

Router rule:

- Count unlabeled demos with classifier score at least `0.95`.
- If that saturated plateau is at least `max(400, 40 x labeled_positive_count)`, use soft classifier-probability weighted sampling.
- Otherwise, if labeled-positive score p10 is at least `0.85` and the saturated plateau is at least `4 x labeled_positive_count`, use the calibrated `pos_min` hard threshold.
- Otherwise, use adaptive-masscap hard support.

Router decisions:

| analysis | branch | training rule | saturated demos | labeled-positive p10 | anchored 20k |
|---|---|---|---:|---:|---:|
| Can paired 80p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.748 | 0.900 |
| Can paired 40p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.748 | 0.733 |
| Can paired 20p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.749 | 0.667 |
| Lift MG sparse | hard pos-min threshold | pos-min calibrated threshold | 85.3 | 0.887 | 0.667 |
| Can MG sparse | soft weighted | classifier-probability weighted sampler | 652.3 | 0.943 | 0.333 |

Interpretation:

- This is a concrete hidden-label-free candidate for the score-to-policy-training conversion, not just a post-hoc hidden-label diagnostic.
- It matches the current fixed-20k policy anchors across paired Can, Lift MG, and Can MG without using hidden unlabeled labels in the decision.
- It should be treated as a candidate method; the next section adds one shuffled-split validation anchor, but broader task-family validation is still needed before promoting it to the main paper claim.

## 2026-06-22: Shuffled 40p/80b router validation

Created a shuffled paired-Can 40 positive / 80 bad validation split and trained the router-selected hard adaptive-masscap branch with the same official Robomimic BC-RNN-GMM backbone.

Artifacts:

- Split inspection: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80_shuffle42/REPORT.md`
- Selector analysis: `results/robomimic_selector_score_analysis_pos40_bad80_shuffle42/REPORT.md`
- Three-seed policy summary: `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/REPORT.md`
- Router validation summary: `results/robomimic_hidden_free_router_validation_shuffle42/REPORT.md`

Support audit:

| selected unlabeled | hidden positive | hidden bad | purity | rule mode |
|---:|---:|---:|---:|---|
| 63.3 | 39.3 | 24.0 | 0.621 | adaptive_masscap_coverage_gap |

Policy means:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| shuffle42 adaptive masscap | 0.167 | 0.767 | 0.733 | 0.633 | 0.767 |

Interpretation update:

- The hidden-free router's hard branch transfers to a new shuffled paired-Can 40p/80b split without using hidden unlabeled labels in the decision.
- The result is positive but not stronger than the original 40p/80b split: fixed 20k mean is `0.633` versus `0.733`, while 10k/15k remain strong.
- This is useful validation evidence for the method candidate, not a reason to promote hard support as universally better than soft weighting.

## 2026-06-22: Shuffled Lift MG router validation

Created a shuffled Lift MG sparse split and trained the router-selected hard `pos_min` branch with the official Robomimic BC-RNN-GMM backbone.

Artifacts:

- Split inspection: `results/robomimic_inspection/lift_mg_low_dim_sparse_shuffle42/REPORT.md`
- Selector analysis: `results/robomimic_lift_mg_selector_score_analysis_shuffle42/REPORT.md`
- Three-seed policy summary: `results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/REPORT.md`
- Combined router validation summary: `results/robomimic_hidden_free_router_validation_shuffle42/REPORT.md`

Actual policy setup support:

| train demos | selected unlabeled | hidden positive | hidden bad | purity |
|---:|---:|---:|---:|---:|
| 209.3 | 199.3 | 185.0 | 14.3 | 0.928 |

Policy means:

| source | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|
| shuffle42 Lift pos-min | 0.133 | 0.400 | 0.400 | 0.600 | 0.600 |

Interpretation update:

- The hidden-free router still selects the hard `pos_min` branch on a new Lift MG split, and the selected support remains high-purity.
- The policy result is positive but weaker than the original Lift split: fixed 20k mean is `0.600` versus `0.667`, and best-per-seed mean is also `0.600` versus `0.700`.
- This strengthens the claim that the branch transfers, while also strengthening the caveat that Lift policy performance is split- and checkpoint-sensitive.

## 2026-06-22: Shuffled Can MG router branch-boundary check

Created a shuffled Can MG sparse split and ran the support/router screen for the current hidden-free hard/soft router.

Artifacts:

- Split inspection: `results/robomimic_inspection/can_mg_low_dim_sparse_shuffle42/REPORT.md`
- Selector analysis: `results/robomimic_selector_score_analysis_can_mg_shuffle42/REPORT.md`
- Seed-0 hard/soft policy comparison: `results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/REPORT.md`
- Combined router validation summary: `results/robomimic_hidden_free_router_validation_shuffle42/REPORT.md`

Support and routing:

| split | saturated demos >= 0.95 | router branch | selected/weighted unlabeled | hidden positive | hidden bad | purity |
|---|---:|---|---:|---:|---:|---:|
| original Can MG | 652.3 | soft weighted | 3840 | 688 | 3152 | 0.179 |
| shuffle42 Can MG | 312.7 | hard pos-min | 649 | 414 | 235 | 0.638 |

Seed-0 policy comparison on shuffle42:

| source | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| hard pos-min | 0.000 | 0.000 | 0.200 | 0.100 | 0.200 |
| soft weighted counterfactual | 0.000 | 0.100 | 0.100 | 0.100 | 0.100 |

Interpretation update:

- The fixed absolute plateau rule is brittle on Can MG: the same task family flips from soft weighted to hard `pos_min` under a label/split shuffle.
- The seed-0 policy check does not show a soft-weighted rescue; both branches are weak on this validation split.
- This should stop us from promoting the current router as the final method. The next method step should replace the fixed `score >= 0.95` trigger with a more robust score-shape or validation proxy before spending on more Can MG seeds.

## 2026-06-22: Router score-shape feature audit

Added a hidden-label-free feature audit for the hard/soft router.

Artifacts:

- Script: `scripts/summarize_robomimic_router_feature_diagnostics.py`
- Report: `results/robomimic_router_feature_diagnostics/REPORT.md`
- CSV: `results/robomimic_router_feature_diagnostics/feature_summary.csv`

Key feature table:

| analysis | observed mode | policy 20k | estimated mass | score >= 0.95 | count >= pos-min | pos-min purity | current rule | stress-abstain rule |
|---|---|---:|---:|---:|---:|---:|---|---|
| Can paired 80p/80b | hard | 0.900 | 82.4 | 0.0 | 32.7 | 1.000 | hard adaptive | hard adaptive |
| Can paired 40p/80b | hard | 0.733 | 49.4 | 0.0 | 17.0 | 1.000 | hard adaptive | hard adaptive |
| Can paired 20p/80b | hard | 0.667 | 34.1 | 0.0 | 6.7 | 1.000 | hard adaptive | hard adaptive |
| Lift MG | hard | 0.667 | 346.9 | 85.3 | 237.3 | 0.864 | hard pos-min | hard pos-min |
| Can MG | soft diagnostic | 0.333 | 1947.9 | 652.3 | 1025.7 | 0.475 | soft weighted | stress abstain |
| Can paired 40p/80b shuffle42 | hard validation | 0.633 | 60.2 | 3.0 | 26.0 | 0.881 | hard adaptive | hard adaptive |
| Lift MG shuffle42 | hard validation | 0.600 | 461.7 | 159.3 | 190.7 | 0.928 | hard pos-min | hard pos-min |
| Can MG shuffle42 | fragile | 0.100 | 1466.3 | 312.7 | 515.7 | 0.651 | hard pos-min | stress abstain |

Interpretation update:

- The current absolute-plateau rule explains the design split but is not robust.
- A mass-only alternative would route both Can MG splits to soft weighting, but the shuffled seed-0 soft policy is still weak; a large-pos-min alternative keeps the same Can MG branch flip as the current rule.
- The best next router direction is an abstention or validation-proxy branch for large bad-dominated MG pools. Paired Can and Lift remain the cleaner paper-facing hard-support evidence.

## 2026-06-22: Router v2 abstention candidate

Added a stricter hidden-label-free router candidate that turns the Can MG fragility into an explicit abstention decision instead of forcing a hard/soft branch.

Artifacts:

- Script: `scripts/summarize_robomimic_router_v2_abstention.py`
- Report: `results/robomimic_router_v2_abstention_summary/REPORT.md`
- CSV: `results/robomimic_router_v2_abstention_summary/router_v2_summary.csv`

Router v2 rule:

- Abstain if calibrated estimated positive mass is at least `800` and the count above the labeled-positive minimum score is at least `400`.
- Otherwise use `hard_pos_min` when labeled-positive p10 is at least `0.85` and the count above labeled-positive minimum is at least `80`.
- Otherwise use `hard_adaptive_masscap`.

Decision audit:

| class | rows | router v2 decision | fixed-20k outcome |
|---|---:|---|---:|
| paired Can + Lift, original and shuffled | 6 | assigned hard support | mean `0.700`, min `0.600` |
| Can MG, original and shuffled | 2 | stress abstain | mean `0.217`, max `0.333` |

Interpretation update:

- Router v2 preserves the paper-facing hard-support evidence on paired Can and Lift, including shuffled validations.
- It abstains on both Can MG splits: original Can MG has only modest soft-weighting success, and shuffled Can MG is weak for both hard and soft seed-0 branches.
- This is currently the cleanest method-level framing: a high-confidence hard-support converter with an abstention/stress branch, not a universal hard-vs-soft router.
- To make Can MG a main positive result, the next method step needs a validated hidden-label-free policy-quality proxy rather than another fixed score threshold.

## 2026-06-22: Can MG branch-likelihood proxy test

Tested whether a hidden-label-free BC likelihood proxy can replace router-v2 abstention on Can MG.

Artifacts:

- Original Can MG checkpoint scores: `results/robomimic_can_mg_branch_proxy_final20k_original/REPORT.md`
- Shuffled Can MG checkpoint scores: `results/robomimic_can_mg_branch_proxy_final20k_shuffle42/REPORT.md`
- Summary: `results/robomimic_can_mg_branch_proxy_summary/REPORT.md`
- Script: `scripts/summarize_robomimic_can_mg_branch_proxy.py`

Setup:

- Reused existing final-20k official Robomimic BC-RNN-GMM checkpoints.
- Scored policies on labeled-positive, labeled-negative, held-out valid-positive, and held-out valid-negative masks.
- Compared positive log-likelihood, positive-minus-negative likelihood gap, and negative rejection against actual fixed-20k rollout success.

Method means:

| split | method | runs | rollout 20k | valid-positive LL | valid contrastive gap | valid negative rejection |
|---|---:|---:|---:|---:|---:|---:|
| Can MG original | all-positive | 3 | 0.200 | -39995254.667 | 147031693.600 | 187026948.267 |
| Can MG original | all-demo | 3 | 0.100 | -41332625.533 | 33560461.133 | 74893086.667 |
| Can MG original | pos-p10 | 3 | 0.167 | -45557884.178 | 101496491.067 | 147054375.245 |
| Can MG original | weighted | 3 | 0.333 | -40054130.867 | 39934926.244 | 79989057.111 |
| Can MG shuffle42 | hard pos-min | 1 | 0.100 | -42532609.667 | 99066174.733 | 141598784.400 |
| Can MG shuffle42 | soft weighted | 1 | 0.100 | -38082416.600 | 35150932.600 | 73233349.200 |

Interpretation update:

- On original Can MG, every tested likelihood proxy selects all-positive support, but the rollout-best fixed-20k method is weighted sampling (`0.333` versus `0.200`).
- The proxy over-rewards tight positive imitation and strong negative rejection, while missing the broad coverage that makes weighted sampling better on this stress split.
- On shuffled Can MG, hard and soft final-20k policies tie at `0.100`; likelihood can choose a branch but cannot detect that both branches are weak.
- This is a negative result for replacing router-v2 abstention with simple likelihood. The next proxy must predict coverage-sensitive rollout quality, not just positive fit or negative rejection.

## 2026-06-22: Square MH relative-quality transfer diagnostic

Downloaded and inspected Robomimic Square MH low-dimensional data, then ran a support-side score calibration diagnostic using relative-quality masks.

Artifacts:

- Dataset: `data/robomimic/v1.5/square/mh/low_dim_v15.hdf5`
- Reward-success inspection: `results/robomimic_inspection/square_mh_low_dim/REPORT.md`
- Relative-quality split: `results/robomimic_inspection/square_mh_quality_better_worse/REPORT.md`
- Selector analysis: `results/robomimic_selector_score_analysis_square_mh_quality_better_worse/REPORT.md`
- Router extra: `results/robomimic_hidden_free_router_square_quality_extra/REPORT.md`
- Summary: `results/robomimic_square_quality_transfer_summary/REPORT.md`

Important caveat:

- Square MH has `300` reward-positive demos and `0` reward-negative demos. It has `better` / `okay` / `worse` relative-quality masks, so this is not a bad-demo or failure-demo benchmark.

Quality split:

- Labeled positives: 10 `better_train` demos.
- Labeled negatives: 10 `worse_train` demos.
- Unlabeled: 80 hidden `better_train` demos plus 80 hidden `worse_train` demos.
- `okay` demos are excluded to keep the hidden audit well-defined.

Score and selection results:

| quantity | value |
|---|---:|
| labeled-positive mean score | 0.939 |
| labeled-positive p10 score | 0.893 |
| labeled-negative mean score | 0.053 |
| labeled-negative max score | 0.115 |
| top-20 selected purity | 0.800 |
| pos-min selected purity | 0.803 |
| adaptive-masscap selected purity | 0.712 |
| router branch | hard adaptive masscap |

Interpretation update:

- Scarce relative-quality labels transfer cleanly to NutAssemblySquare and produce a useful desirability score.
- This strengthens the cross-task score-calibration mechanism but remains support-only evidence.
- A Square policy result would need a quality-sensitive evaluation target; sparse success alone is not enough because all recorded Square MH demos are successful.

## 2026-06-22: Square MH policy smoke is negative

Ran a bounded one-seed official Robomimic BC-RNN-GMM policy smoke on the Square MH relative-quality split.

Artifacts:

- Better-only setup/eval: `results/robomimic_square_quality_better_seed0_setup/`, `results/robomimic_square_quality_better_seed0_eval/`
- Mixed better+worse setup/eval: `results/robomimic_square_quality_mixed_seed0_setup/`, `results/robomimic_square_quality_mixed_seed0_eval/`
- Adaptive-masscap setup/eval: `results/robomimic_square_quality_adaptive_seed0_setup/`, `results/robomimic_square_quality_adaptive_seed0_eval/`
- Summary: `results/robomimic_square_quality_policy_smoke_summary/REPORT.md`
- Script: `scripts/summarize_robomimic_square_quality_policy_smoke.py`

Protocol:

- Seed 0.
- Official BC-RNN-GMM.
- Epoch 50 and epoch 100 checkpoints, corresponding to 5k and 10k optimizer steps in this config.
- Evaluation on held-out `better_valid` initial states, 10 episodes per checkpoint, horizon 500.

Results:

| method | train demos | selected unlabeled | epoch 50 | epoch 100 |
|---|---:|---:|---:|---:|
| better-only BC | 90 | 0 | 0.000 | 0.000 |
| mixed better+worse BC | 180 | 0 | 0.000 | 0.000 |
| adaptive-masscap support BC | 69 | 59 | 0.000 | 0.000 |

Interpretation update:

- All evaluated Square policies fail all held-out `better_valid` rollouts and run to the full 500-step horizon.
- This does not undermine the Square support-side score diagnostic, but it means Square is not ready as policy evidence.
- Keep Square in the paper package only as relative-quality score-transfer evidence unless we add a stronger Square policy setup or direct quality-sensitive evaluator.

## 2026-06-22: Can 40p/80b checkpoint-selection diagnostic

Extended the offline checkpoint-selection analysis to the Can 40 positive / 80 bad intermediate split, focusing on the live masscap-vs-weighted comparison.

Artifacts:

- Raw checkpoint scoring: `results/robomimic_can40_checkpoint_selection_masscap_weighted/REPORT.md`
- Rule summary: `results/robomimic_can40_checkpoint_selection_masscap_weighted/RULE_SUMMARY.md`
- CSVs: `checkpoint_scores.csv`, `selected_checkpoints.csv`, `selection_rule_summary.csv`, `selection_rule_aggregate.csv`, `fixed_epoch_summary.csv`
- New summarizer: `scripts/summarize_robomimic_checkpoint_selection_rules.py`

Setup:

- Existing checkpoints only; no new policy training.
- Compared mass-capped hard support against classifier-probability weighted BC on seeds 0/1/2.
- Scored checkpoints on train support, held-out positive/negative, and labeled positive/negative filters.
- Added composite positive-minus-negative and joint positive+negative likelihood rules.

Fixed/checkpoint outcomes:

| method | 5k | 10k | 15k | 20k | oracle-best |
|---|---:|---:|---:|---:|---:|
| masscap | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| weighted BC | 0.267 | 0.600 | 0.700 | 0.567 | 0.700 |

Likelihood-rule outcomes:

| rule | masscap selected | weighted selected |
|---|---:|---:|
| train-support likelihood | 0.733 | 0.567 |
| labeled-positive likelihood | 0.733 | 0.567 |
| valid-positive likelihood | 0.467 | 0.667 |
| valid positive-minus-negative likelihood | 0.167 | 0.267 |
| labeled joint positive+negative likelihood | 0.767 | 0.567 |

Interpretation update:

- The masscap advantage is not just a hidden best-checkpoint artifact: weighted oracle-best is 0.700, below masscap oracle-best 0.767.
- Simple likelihood checkpoint rules are not reliable enough for best-checkpoint reporting. Train-support and labeled-positive likelihood preserve the fixed-20k story; valid-positive likelihood is noisy and hurts masscap; positive-minus-negative likelihood selects weak early checkpoints.
- Keep fixed-budget reporting as the clean paper-facing comparison. Best-per-seed can remain secondary but should not be promoted without a stronger predeclared checkpoint rule.

## 2026-06-22: Lift positive-only NN no-bad-label control

Added a Lift MG no-bad-label nearest-neighbor support control. This addresses the live caveat that positive-only NN is strong on the Can 40p/80b split.

Artifacts:

- Summary: `results/robomimic_lift_mg_posonly_nn_seed0_summary/REPORT.md`
- Script: `scripts/summarize_robomimic_lift_posonly_nn_control.py`
- Setup-only support sweep: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top80_seed0_setup/`, `top160_seed0_setup/`, `top240_seed0_setup/`, `top320_seed0_setup/`
- Seed-0 policy evals: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top80_seed0_eval/`, `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed0_eval/`

Support sweep:

| method | selected unlabeled | hidden positive | hidden bad | purity |
|---|---:|---:|---:|---:|
| positive-only NN top80 | 80 | 78 | 2 | 0.975 |
| positive-only NN top160 | 160 | 126 | 34 | 0.787 |
| positive-only NN top240 | 240 | 143 | 97 | 0.596 |
| positive-only NN top320 | 320 | 164 | 156 | 0.512 |
| bad-aware pos-min seed0 | 230 | 203 | 27 | 0.883 |

Seed-0 policy results:

| method | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| positive-only NN top80 | 0.300 | 0.300 | 0.400 | 0.400 | 0.400 |
| positive-only NN top160 | 0.500 | 0.200 | 0.200 | 0.500 | 0.500 |
| bad-aware pos-min | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |

Interpretation update:

- Lift MG gives cleaner evidence for bad-label calibration than Can 40p/80b: positive-only NN has a sharp precision/coverage tradeoff, while bad-aware `pos_min` recovers many more hidden positives with fewer bad demos than broad positive-only support.
- The one-seed policy diagnostic favors `pos_min` strongly at fixed 20k, but it should not be promoted as a main three-seed ablation until extended to seeds 1 and 2.
- The current paper wording remains: bad labels are not strictly necessary in every split, but they improve fixed-budget stability and calibration, and Lift now shows a concrete regime where no-bad-label positive-only support is coverage-limited.

## 2026-06-22: Lift positive-only NN top160 three-seed extension

Extended the Lift MG no-bad-label top160 control to policy seeds 1 and 2, matching the existing bad-aware `pos_min` three-seed protocol.

Artifacts:

- Summary: `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md`
- Script: `scripts/summarize_robomimic_lift_posonly_nn_control.py`
- Seed 1 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed1_setup/`, `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed1_eval/`
- Seed 2 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed2_setup/`, `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed2_eval/`

Three-seed policy results:

| method | 5k | 10k | 15k | 20k | oracle-by-seed |
|---|---:|---:|---:|---:|---:|
| positive-only NN top160 | 0.400 | 0.300 | 0.333 | 0.567 | 0.567 |
| bad-aware pos-min | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |

Interpretation update:

- Positive-only NN top160 is not a collapsed baseline, but it does not remove the Lift evidence for bad-aware calibration.
- The bad-aware `pos_min` branch remains stronger at the fixed 15k and 20k checkpoints and under oracle-by-seed checkpoint selection.
- This sharpens the claim: bad labels are not universally necessary, but on Lift MG they improve the coverage-quality tradeoff relative to a positive-only nearest-neighbor selector.

## 2026-06-22: Can 40p/80b seed-0 50k budget check

Ran a bounded longer-budget diagnostic to test whether the weighted BC baseline on Can 40p/80b is mainly under-optimized at 20k.

Artifacts:

- Summary: `results/robomimic_can40_long_budget_seed0_summary/REPORT.md`
- Masscap 50k setup/eval: `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_existingmask_50k_setup/`, `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_existingmask_50k_eval/`
- Weighted 50k setup/eval: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_existingmask_50k_setup/`, `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_existingmask_50k_eval/`

Protocol:

- Reused the original 20k Can 40p/80b train masks and weighted sampler weights.
- Trained from scratch to 50k optimizer steps, saving every 10k.
- Evaluated 10 held-out validation-positive initial states with horizon 400.
- A regenerated masscap setup was not used because the current selector script selected a different support set (`71` train demos instead of the original `60`), which would confound a pure budget check.

Budget curve:

| method | 10k | 20k | 30k | 40k | 50k | best |
|---|---:|---:|---:|---:|---:|---:|
| adaptive masscap | 0.300 | 0.800 | 0.800 | 0.700 | 0.600 | 0.800 |
| weighted probability sampler | 0.700 | 0.500 | 0.300 | 0.500 | 0.300 | 0.700 |

Interpretation update:

- This one-seed diagnostic does not support the explanation that weighted BC just needs longer optimization. Weighted peaks early at 10k and is worse after 20k.
- Masscap also does not improve monotonically with longer training: it peaks at 20k/30k and then degrades.
- For paper-facing robotics comparisons, 20k fixed-budget reporting remains more defensible than simply increasing Robomimic BC training to 50k.

## 2026-06-22: Can 40p/80b seed-0 endpoint 50-episode check

Re-evaluated the original seed-0 fixed-20k Can 40p/80b masscap and weighted checkpoints with more held-out rollouts to estimate endpoint noise.

Artifacts:

- Summary: `results/robomimic_can40_endpoint_50ep_summary/REPORT.md`
- Masscap eval: `results/robomimic_can40_seed0_endpoint_50ep_masscap_eval/REPORT.md`
- Weighted eval: `results/robomimic_can40_seed0_endpoint_50ep_weighted_eval/REPORT.md`

Protocol:

- Original seed-0 fixed-20k checkpoints from the three-seed table.
- 50 evaluation episodes each, cycling the same 10 validation-positive initial states five times.
- Horizon 400.

Endpoint results:

| method | original 10 ep | 50 ep | approximate 95% CI |
|---|---:|---:|---:|
| adaptive masscap | 0.800 | 0.700 | [0.573, 0.827] |
| weighted probability sampler | 0.500 | 0.560 | [0.422, 0.698] |

Interpretation update:

- The direction remains favorable to masscap on seed 0, but the gap narrows from `0.300` to `0.140`.
- The per-initial-state pattern shows the difference is concentrated on a few validation starts, not uniformly present on every start.
- This is a useful caveat for paper writing: keep the three-seed fixed-budget table as the main evidence, but avoid overclaiming precision from 10-episode endpoint estimates.

## 2026-06-22: Transport MH relative-quality transfer diagnostic

Downloaded and inspected Robomimic Transport MH low-dimensional data, then ran the same support-side relative-quality score diagnostic used for Square.

Artifacts:

- Dataset: `data/robomimic/v1.5/transport/mh/low_dim_v15.hdf5`
- Reward-success inspection: `results/robomimic_inspection/transport_mh_low_dim/REPORT.md`
- Quality split: `results/robomimic_inspection/transport_mh_quality_better_worse/REPORT.md`
- Selector analysis: `results/robomimic_selector_score_analysis_transport_mh_quality_better_worse/REPORT.md`
- Summary: `results/robomimic_transport_quality_transfer_summary/REPORT.md`

Important caveat:

- Transport MH has `300` reward-positive demos and `0` reward-negative demos. It has relative-quality masks, so this is not a bad-demo or failure-demo benchmark.

Quality split:

- Labeled positives: 10 `better_train` demos.
- Labeled negatives: 10 `worse_train` demos.
- Unlabeled: 35 hidden `better_train` demos plus 35 hidden `worse_train` demos.
- `okay` demos are excluded to keep hidden labels well-defined.

Score and selection results:

| quantity | value |
|---|---:|
| labeled-positive mean score | 0.988 |
| labeled-positive p10 score | 0.979 |
| labeled-negative mean score | 0.014 |
| labeled-negative max score | 0.041 |
| top-30 selected purity | 1.000 |
| pos-min selected purity | 1.000 |
| adaptive-masscap selected purity | 0.972 |

Interpretation update:

- Scarce relative-quality labels transfer cleanly to TwoArmTransport and produce an even stronger quality score than the Square support diagnostic.
- Adaptive masscap selects all 35 hidden-better unlabeled demos while admitting only 1 hidden-worse demo on average.
- This broadens the support-side score-calibration mechanism across manipulation task families, but it should not be promoted as policy or failure-avoidance evidence.

## 2026-06-23: Can 40p/80b three-seed endpoint 50-episode check

Extended the seed-0 higher-episode endpoint diagnostic to all three seeds for the original fixed-20k Can 40p/80b masscap-vs-weighted comparison.

Artifacts:

- Summary: `results/robomimic_can40_endpoint_50ep_3seed_summary/REPORT.md`
- Seed-1 evals: `results/robomimic_can40_seed1_endpoint_50ep_masscap_eval/REPORT.md`, `results/robomimic_can40_seed1_endpoint_50ep_weighted_eval/REPORT.md`
- Seed-2 evals: `results/robomimic_can40_seed2_endpoint_50ep_masscap_eval/REPORT.md`, `results/robomimic_can40_seed2_endpoint_50ep_weighted_eval/REPORT.md`
- Regenerator: `scripts/summarize_robomimic_can40_endpoint_50ep_3seed.py`

Protocol:

- Checkpoints: original fixed-20k checkpoints from the three-seed table.
- Evaluation: 50 held-out validation-positive initial-state rollouts per seed and method.
- Horizon: 400.
- Each seed/method cycles the same 10 validation-positive initial states five times.

Endpoint results:

| seed | masscap 10 ep | weighted 10 ep | masscap 50 ep | weighted 50 ep | gap 50 ep |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.800 | 0.500 | 0.700 | 0.560 | 0.140 |
| 1 | 0.600 | 0.600 | 0.620 | 0.500 | 0.120 |
| 2 | 0.800 | 0.600 | 0.720 | 0.660 | 0.060 |

Aggregate:

| method | 10 ep mean | 50 ep seed mean | pooled 50 ep |
|---|---:|---:|---:|
| adaptive masscap | 0.733 | 0.680 +/- 0.043 | 102/150 |
| weighted probability sampler | 0.567 | 0.573 +/- 0.066 | 86/150 |

Interpretation update:

- The higher-episode direction favors masscap on every seed, which strengthens the fixed-budget Can 40p/80b result.
- The mean gap shrinks from 0.167 in the original 10-episode table to 0.107 in the 50-episode table.
- Approximate pooled binomial intervals still overlap, so this is a robustness/caveat check rather than a standalone statistical proof.
- Paper language should say the masscap endpoint edge persists under less noisy evaluation, but is modest.

## 2026-06-24: TRIAGE-BC v0.1 method freeze

Created the forward-looking method contract requested by the paper completion plan. This separates existing development/validation evidence from future fresh final-split claims.

Artifacts:

- Method freeze: `METHOD_FREEZE.md`
- Method config: `configs/final_method.yaml`
- Evaluation config: `configs/final_eval.yaml`
- Final artifact staging README: `results/final_paper/README.md`

Frozen method summary:

- Paper-facing method name: TRIAGE-BC v0.1.
- Score model: state-action binary classifier trained on labeled positives versus labeled negatives, with unlabeled demos excluded from score-model training.
- Trajectory score: mean sigmoid classifier probability over transitions.
- Positive mass: calibrated by labeled-positive and labeled-negative mean demo scores.
- Router v2:
  - abstain if estimated positive mass >= 800 and count above positive minimum >= 400;
  - otherwise use hard `pos_min` if labeled-positive p10 >= 0.85 and count above positive minimum >= 80;
  - otherwise use hard adaptive masscap.
- Policy backbone: official Robomimic BC-RNN-GMM, sequence length 10, actor MLP 1024/1024, LSTM hidden 400 x 2 layers, 5 GMM modes.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps, checkpoints at 5k/10k/15k/20k.
- Primary final split seeds: 11, 22, 33.
- Primary policy seed per final split: 0.
- Final evaluation: 50 held-out validation-positive rollouts, fixed-budget reporting, no best-checkpoint main claims.

Interpretation update:

- Existing results outside `results/final_paper/` remain development, validation, ablation, or diagnostic evidence unless rerun under the freeze.
- Any future change to score model, router thresholds, policy config, checkpoint schedule, or final evaluation protocol should be logged as a new variant or ablation.
- The next compute-bearing step should start from the freeze, preferably a bounded Lift 50-episode endpoint check or the first fresh Can 40p/80b final split.

## 2026-06-24: Lift MG core endpoint 50-episode check

Ran the missing higher-episode Lift endpoint diagnostic for the core fixed-20k comparison: bad-aware `pos_min`, classifier-probability weighted BC, and positive-only NN top160.

Artifacts:

- Summary: `results/robomimic_lift_mg_endpoint_50ep_summary/REPORT.md`
- Regenerator: `scripts/summarize_robomimic_lift_endpoint_50ep.py`
- Pos-min evals: `results/robomimic_lift_mg_seed{0,1,2}_endpoint_50ep_posmin_eval/REPORT.md`
- Weighted evals: `results/robomimic_lift_mg_seed{0,1,2}_endpoint_50ep_weighted_eval/REPORT.md`
- Positive-only top160 evals: `results/robomimic_lift_mg_seed{0,1,2}_endpoint_50ep_posonly_top160_eval/REPORT.md`

Protocol:

- Original Lift MG sparse split.
- Original fixed-20k checkpoints from the three-seed table.
- 50 evaluation episodes per seed and method.
- Horizon 150.
- The split has 30 validation-positive initial states; 50 episodes cycle through the ordered start list.

Endpoint results:

| method | 10 ep mean | 50 ep seed mean | pooled 50 ep |
|---|---:|---:|---:|
| bad-aware pos-min | 0.667 | 0.600 +/- 0.065 | 90/150 |
| weighted probability sampler | 0.533 | 0.533 +/- 0.025 | 80/150 |
| positive-only NN top160 | 0.567 | 0.560 +/- 0.049 | 84/150 |

Interpretation update:

- Bad-aware `pos_min` still leads weighted BC at the fixed 20k endpoint under a less noisy evaluation budget.
- The gap over positive-only NN top160 is small: 0.600 versus 0.560.
- This weakens any strong bad-label-necessity wording. The paper should say bad labels improve calibration and can improve fixed-budget coverage-quality tradeoffs, while positive-only retrieval remains a strong baseline.
- Approximate pooled intervals overlap, so this is robustness evidence and a paper caveat, not a standalone statistical proof.

## 2026-06-24: First frozen final Can 40p/80b split endpoint

Ran the first fresh final-split comparison under `METHOD_FREEZE.md`: Can Paired 40 hidden-positive / 80 hidden-bad unlabeled, split seed 11, policy seed 0.

Artifacts:

- Runner: `scripts/run_final_matrix.py`
- Summary CSV: `results/final_paper/tables/can_paired_pos40_bad80_split11_endpoint.csv`
- Summary report: `results/final_paper/tables/can_paired_pos40_bad80_split11_endpoint_REPORT.md`
- TRIAGE run: `results/final_paper/per_seed/can_paired_pos40_bad80_split11_triage_bc_policy0/REPORT.md`
- Weighted run: `results/final_paper/per_seed/can_paired_pos40_bad80_split11_weighted_bc_policy0/REPORT.md`

Protocol:

- Frozen router-v2 selected `hard_adaptive_masscap` for TRIAGE-BC.
- Official Robomimic BC-RNN-GMM, fixed 20k endpoint.
- Endpoint-only evaluation for this fast pass: 50 validation-positive rollouts, horizon 400, rollout seed 0.
- The all-checkpoint 50-episode curve was intentionally stopped after training because it was too slow for fast iteration; endpoint evaluation is the primary frozen metric.

Endpoint results:

| method | selected unlabeled | hidden-positive | hidden-bad | purity | 20k success |
|---|---:|---:|---:|---:|---:|
| TRIAGE-BC hard adaptive masscap | 70 | 40 | 30 | 0.571 | 0.760 |
| weighted BC sampler | 120 | 40 | 80 | 0.333 | 0.720 |

Interpretation update:

- The first fresh final split preserves the desired direction: TRIAGE-BC beats weighted BC at the fixed 20k endpoint.
- The gap is small: 0.040 over 50 episodes, so this should be treated as one encouraging final-split datapoint, not a standalone claim.
- The support audit is informative: TRIAGE-BC recovered all 40 hidden positives while filtering 50/80 hidden bad demos, despite lower purity than the original development split.
- Next final evidence should repeat the same endpoint comparison on split seeds 22 and 33, and then broaden to the required baselines.

## 2026-06-24: Second frozen final Can 40p/80b split endpoint

Ran the same frozen endpoint comparison on split seed 22.

Artifacts:

- Split-22 summary CSV: `results/final_paper/tables/can_paired_pos40_bad80_split22_endpoint.csv`
- Split-22 summary report: `results/final_paper/tables/can_paired_pos40_bad80_split22_endpoint_REPORT.md`
- Two-split aggregate CSV: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`
- Two-split aggregate report: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`
- TRIAGE run: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_triage_bc_policy0/REPORT.md`
- Weighted run: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_weighted_bc_policy0/REPORT.md`

Protocol:

- Same `METHOD_FREEZE.md` contract as split 11.
- Frozen router-v2 selected `hard_adaptive_masscap` for TRIAGE-BC.
- Official Robomimic BC-RNN-GMM, fixed 20k endpoint.
- Endpoint evaluation: 50 validation-positive rollouts, horizon 400, rollout seed 0.

Endpoint results:

| method | selected unlabeled | hidden-positive | hidden-bad | purity | 20k success |
|---|---:|---:|---:|---:|---:|
| TRIAGE-BC hard adaptive masscap | 73 | 36 | 37 | 0.493 | 0.520 |
| weighted BC sampler | 120 | 40 | 80 | 0.333 | 0.440 |

Two-split aggregate so far:

| method | endpoint successes | success rate |
|---|---:|---:|
| TRIAGE-BC hard adaptive masscap | 64/100 | 0.640 |
| weighted BC sampler | 58/100 | 0.580 |

Interpretation update:

- The second fresh final split also favors TRIAGE-BC, with a 0.080 endpoint gap.
- Split 22 is clearly harder than split 11: both methods drop, and TRIAGE support purity falls from 0.571 to 0.493.
- The aggregate direction is now 2/2 frozen splits favoring TRIAGE-BC, but the mean gap is modest at 0.060.
- Paper language should say the final-split evidence is encouraging and directionally consistent so far, not complete. Split seed 33 and broader frozen baselines remain required.

## 2026-06-24: Third frozen final Can 40p/80b split endpoint

Ran the final primary split-seed comparison for Can Paired 40 hidden-positive / 80 hidden-bad unlabeled under `METHOD_FREEZE.md`: split seed 33, policy seed 0.

Artifacts:

- Split-33 summary CSV: `results/final_paper/tables/can_paired_pos40_bad80_split33_endpoint.csv`
- Split-33 summary report: `results/final_paper/tables/can_paired_pos40_bad80_split33_endpoint_REPORT.md`
- Updated three-split aggregate CSV: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`
- Updated three-split aggregate report: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`
- TRIAGE run: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_triage_bc_policy0/REPORT.md`
- Weighted run: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_weighted_bc_policy0/REPORT.md`

Protocol:

- Same `METHOD_FREEZE.md` contract as split seeds 11 and 22.
- Frozen router-v2 selected `hard_adaptive_masscap` for TRIAGE-BC.
- Official Robomimic BC-RNN-GMM, fixed 20k endpoint.
- Endpoint evaluation: 50 validation-positive rollouts, horizon 400, rollout seed 0.

Endpoint results:

| method | selected unlabeled | hidden-positive | hidden-bad | purity | 20k success |
|---|---:|---:|---:|---:|---:|
| TRIAGE-BC hard adaptive masscap | 47 | 34 | 13 | 0.723 | 0.700 |
| weighted BC sampler | 120 | 40 | 80 | 0.333 | 0.640 |

Completed primary final split aggregate:

| method | endpoint successes | success rate |
|---|---:|---:|
| TRIAGE-BC hard adaptive masscap | 99/150 | 0.660 |
| weighted BC sampler | 90/150 | 0.600 |

Interpretation update:

- All three primary frozen split seeds favor TRIAGE-BC over weighted BC at the fixed 20k endpoint.
- The pooled gap is modest: 0.060 over 150 endpoint rollouts.
- Split 33 has cleaner TRIAGE support than split 22, with 0.723 purity, but lower hidden-positive coverage than split 11: 34/40 hidden positives selected.
- This completes the primary Can 40p/80b hard-vs-weighted final split matrix. The paper can now state this result as a completed Can final-split finding, while still caveating that broader frozen baselines remain required for a complete benchmark claim.

## 2026-06-24: Frozen Can 40p/80b positive-only NN control

Ran the strongest no-bad-label control on the same primary frozen Can Paired 40 hidden-positive / 80 hidden-bad splits: positive-only nearest-neighbor top40 support plus official BC-RNN-GMM.

Artifacts:

- Updated aggregate CSV: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`
- Updated aggregate report: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`
- Split-11 positive-only run: `results/final_paper/per_seed/can_paired_pos40_bad80_split11_positive_only_nn_policy0/REPORT.md`
- Split-22 positive-only run: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_positive_only_nn_policy0/REPORT.md`
- Split-33 positive-only run: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_positive_only_nn_policy0/REPORT.md`

Protocol:

- Same frozen split seeds, policy seed, official BC-RNN-GMM training budget, and 50-episode endpoint evaluation as TRIAGE-BC and weighted BC.
- Positive-only NN selects the 40 unlabeled demos nearest to labeled positives, without using bad labels or hidden labels.

Endpoint results:

| split seed | TRIAGE-BC | weighted BC | positive-only NN top40 |
|---:|---:|---:|---:|
| 11 | 0.760 | 0.720 | 0.840 |
| 22 | 0.520 | 0.440 | 0.760 |
| 33 | 0.700 | 0.640 | 0.560 |
| pooled | 0.660 | 0.600 | 0.720 |

Positive-only support audit:

| split seed | selected unlabeled | hidden-positive | hidden-bad | purity |
|---:|---:|---:|---:|---:|
| 11 | 40 | 36 | 4 | 0.900 |
| 22 | 40 | 37 | 3 | 0.925 |
| 33 | 40 | 33 | 7 | 0.825 |
| pooled | 120 | 106 | 14 | 0.883 |

Interpretation update:

- This is the most important caveat added so far: on the frozen Can matrix, positive-only NN top40 beats TRIAGE-BC pooled (`0.720` versus `0.660`) and wins on two of three splits.
- The bad-label-aware TRIAGE support still beats the soft weighted sampler, but it is not the best Can final method once the strong no-bad-label baseline is included.
- Paper language should not claim a bad-label benefit on Can 40p/80b. The Can result supports hard selected support over soft weighted sampling and establishes positive-only retrieval as a required baseline.
- The best current bad-label benefit evidence remains more plausible on Lift MG, where bad-aware `pos_min` stays ahead of weighted BC and slightly ahead of positive-only NN top160 under the 50-episode endpoint check.

## 2026-06-24: Frozen Can 40p/80b all-demo mixed cloning control

Ran the all-demo mixed BC control on the same primary frozen Can Paired 40 hidden-positive / 80 hidden-bad splits under `METHOD_FREEZE.md`.

Artifacts:

- Updated aggregate CSV: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`
- Updated aggregate report: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`
- Split-11 all-demo run: `results/final_paper/per_seed/can_paired_pos40_bad80_split11_bc_all_mixed_policy0/REPORT.md`
- Split-22 all-demo run: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_bc_all_mixed_policy0/REPORT.md`
- Split-33 all-demo run: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_bc_all_mixed_policy0/REPORT.md`

Protocol:

- Same frozen split seeds, policy seed, official BC-RNN-GMM training budget, and 50-episode endpoint evaluation as TRIAGE-BC, weighted BC, and positive-only NN.
- All-demo BC trains on all 180 train demos in each split; it does not select an unlabeled support subset, so support purity is undefined.
- Split 11 evaluation used the standard CUDA evaluator. Split 22 CUDA approval timed out twice in Codex, so split 22 and 33 all-demo evaluations used the CPU device fallback with the same checkpoint, seed, init-state mode, episodes, and horizon.

Endpoint results:

| split seed | TRIAGE-BC | weighted BC | positive-only NN top40 | all-demo BC |
|---:|---:|---:|---:|---:|
| 11 | 0.760 | 0.720 | 0.840 | 0.500 |
| 22 | 0.520 | 0.440 | 0.760 | 0.560 |
| 33 | 0.700 | 0.640 | 0.560 | 0.560 |
| pooled | 0.660 | 0.600 | 0.720 | 0.540 |

Interpretation update:

- All-demo mixed cloning is now complete for the frozen Can matrix and is the weakest pooled row: 81/150 successes versus 99/150 for TRIAGE-BC, 90/150 for weighted BC, and 108/150 for positive-only NN.
- Split 22 is an exception where all-demo BC exceeds TRIAGE-BC, so the honest claim is pooled and caveated rather than "mixed BC always fails."
- The Can final story is now stable but narrow: positive-only retrieval is strongest; TRIAGE-BC beats weighted BC and pooled all-demo cloning; the result still does not support a bad-label benefit claim on Can 40p/80b.

## 2026-06-24: Frozen Can 40p/80b all-positive oracle diagnostic

Ran the all-train-positive oracle diagnostic on the same primary frozen Can Paired 40 hidden-positive / 80 hidden-bad splits under `METHOD_FREEZE.md`.

Artifacts:

- Updated aggregate CSV: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`
- Updated aggregate report: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`
- Split-11 oracle run: `results/final_paper/per_seed/can_paired_pos40_bad80_split11_all_train_positive_oracle_policy0/REPORT.md`
- Split-22 oracle run: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_all_train_positive_oracle_policy0/REPORT.md`
- Split-33 oracle run: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_all_train_positive_oracle_policy0/REPORT.md`

Protocol:

- Same frozen split seeds, policy seed, official BC-RNN-GMM training budget, and 50-episode endpoint evaluation as the non-oracle rows.
- Oracle source is `all_train_positive`, which trains on all true-positive train demos. This is 90 demos per split, not a deployable method.
- Endpoint evaluations used CPU device fallback with the same checkpoint, seed, init-state mode, episodes, and horizon.

Endpoint results:

| split seed | TRIAGE-BC | weighted BC | positive-only NN top40 | all-demo BC | all-positive oracle |
|---:|---:|---:|---:|---:|---:|
| 11 | 0.760 | 0.720 | 0.840 | 0.500 | 0.980 |
| 22 | 0.520 | 0.440 | 0.760 | 0.560 | 0.980 |
| 33 | 0.700 | 0.640 | 0.560 | 0.560 | 0.980 |
| pooled | 0.660 | 0.600 | 0.720 | 0.540 | 0.980 |

Interpretation update:

- The all-positive oracle is near-saturated: 147/150 successes across the frozen Can endpoint matrix.
- This is useful because it proves the final eval starts and BC-RNN-GMM backbone can solve the task when given broad true-positive support.
- The remaining Can gap is therefore support conversion, not task solvability. It does not rescue a bad-label benefit claim, because positive-only NN remains the strongest non-oracle row.

## 2026-06-24: Frozen Lift MG sparse split-11 final row

Ran the first fresh frozen final-paper Lift MG sparse split row under `METHOD_FREEZE.md`.

Artifacts:

- Summary CSV: `results/final_paper/tables/lift_mg_mg_sparse_split11_endpoint_summary.csv`
- Summary report: `results/final_paper/tables/lift_mg_mg_sparse_split11_endpoint_summary_REPORT.md`
- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_weighted_bc_policy0/REPORT.md`
- Positive-only NN top160 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_positive_only_nn_policy0/REPORT.md`
- All-demo BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_bc_all_mixed_policy0/REPORT.md`
- All-positive oracle run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_all_train_positive_oracle_policy0/REPORT.md`

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: 11, with shuffled label pools.
- Policy/classifier seed: 0.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint evaluation: 50 validation-positive initial-state rollouts, horizon 150, fixed `model_epoch_200.pth`.
- Evaluations used CPU fallback with the same checkpoint, seed, init-state mode, episodes, and horizon across methods.

Endpoint results:

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| all-positive oracle | 0.660 | 33/50 | 286 | 0 | n/a |
| TRIAGE-BC / pos-min | 0.540 | 27/50 | 188 | 178 | 0.949 |
| weighted BC | 0.480 | 24/50 | 1430 | 1420 weighted | 0.194 |
| positive-only NN top160 | 0.460 | 23/50 | 170 | 160 | 0.531 |
| all-demo BC | 0.260 | 13/50 | 1440 | all train demos | 0.194 |

Interpretation update:

- This fresh split preserves the useful Lift ordering: bad-aware hard support beats weighted BC, positive-only NN, and all-demo cloning at the fixed endpoint.
- The bad-label calibration story is clearer than on frozen Can: positive-only NN top160 support collapses to 0.531 hidden-positive purity on this split, while TRIAGE / pos-min reaches 0.949 purity.
- The endpoint edge over weighted BC is still small, only 3 successes out of 50. This should be used as one split row supporting the existing Lift pattern, not as a standalone decisive result.
- The oracle reaches 0.660, so this split is learnable but harder than the original Lift 50-episode endpoint check and much less saturated than the frozen Can oracle diagnostic.
- All-demo mixed cloning remains weak at 0.260, reinforcing that contaminated Lift logs hurt naive BC under the official sequence BC backbone.

## 2026-06-24: Frozen Lift MG sparse split-22 final row

Ran the second fresh frozen final-paper Lift MG sparse split row under `METHOD_FREEZE.md`.

Artifacts:

- Summary CSV: `results/final_paper/tables/lift_mg_mg_sparse_split22_endpoint_summary.csv`
- Summary report: `results/final_paper/tables/lift_mg_mg_sparse_split22_endpoint_summary_REPORT.md`
- Two-split aggregate CSV: `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary.csv`
- Two-split aggregate report: `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`
- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_weighted_bc_policy0/REPORT.md`
- Positive-only NN top160 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_positive_only_nn_policy0/REPORT.md`
- All-demo BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_bc_all_mixed_policy0/REPORT.md`
- All-positive oracle run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_all_train_positive_oracle_policy0/REPORT.md`

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: 22, with shuffled label pools.
- Policy/classifier seed: 0.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint evaluation: 50 validation-positive initial-state rollouts, horizon 150, fixed `model_epoch_200.pth`.
- Evaluations used CPU fallback with the same checkpoint, seed, init-state mode, episodes, and horizon across methods.

Endpoint results:

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| positive-only NN top160 | 0.680 | 34/50 | 170 | 160 | 0.700 |
| all-positive oracle | 0.680 | 34/50 | 286 | 0 | n/a |
| weighted BC | 0.660 | 33/50 | 1430 | 1420 weighted | 0.194 |
| TRIAGE-BC / pos-min | 0.500 | 25/50 | 171 | 161 | 0.932 |
| all-demo BC | 0.200 | 10/50 | 1440 | all train demos | 0.194 |

Two-split frozen Lift aggregate:

| method | split 11 | split 22 | pooled |
|---|---:|---:|---:|
| all-positive oracle | 0.660 | 0.680 | 67/100 |
| weighted BC | 0.480 | 0.660 | 57/100 |
| positive-only NN top160 | 0.460 | 0.680 | 57/100 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 52/100 |
| all-demo BC | 0.260 | 0.200 | 23/100 |

Interpretation update:

- Split 22 reverses the split-11 ordering: positive-only NN and weighted BC beat TRIAGE-BC at the fixed endpoint.
- Bad labels still improve support purity on split 22: TRIAGE-BC selects 150 hidden-positive and 11 hidden-bad demos, while positive-only NN selects 112 hidden-positive and 48 hidden-bad demos.
- The two-split frozen Lift aggregate no longer supports a clean TRIAGE-over-weighted claim. Weighted BC and positive-only NN both reach 57/100, while TRIAGE-BC reaches 52/100.
- All-demo mixed cloning remains consistently weak at 23/100 pooled, so contaminated-log robustness remains supported.
- Paper language should now treat Lift as split-sensitive evidence for score-to-support conversion and strong baselines, not as a decisive bad-label benefit result.

## 2026-06-24: Frozen Lift MG sparse split-33 core row

Ran the third fresh frozen Lift MG sparse row for the core non-oracle comparison under `METHOD_FREEZE.md`.

Artifacts:

- Split-33 core CSV: `results/final_paper/tables/lift_mg_mg_sparse_split33_core_endpoint_summary.csv`
- Split-33 core report: `results/final_paper/tables/lift_mg_mg_sparse_split33_core_endpoint_summary_REPORT.md`
- Three-split core CSV: `results/final_paper/tables/lift_mg_mg_sparse_core3_endpoint_summary.csv`
- Three-split core report: `results/final_paper/tables/lift_mg_mg_sparse_core3_endpoint_summary_REPORT.md`
- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/REPORT.md`
- Positive-only NN top160 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_positive_only_nn_policy0/REPORT.md`

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: 33, with shuffled label pools.
- Policy/classifier seed: 0.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint evaluation: 50 validation-positive initial-state rollouts, horizon 150, fixed `model_epoch_200.pth`.
- Evaluations used CPU fallback with the same checkpoint, seed, init-state mode, episodes, and horizon across methods.
- This bounded pass ran only the core non-oracle methods. Split-33 all-demo BC and all-positive oracle remain unrun.

Endpoint results:

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| weighted BC | 0.720 | 36/50 | 1430 | 1420 weighted | 0.194 |
| positive-only NN top160 | 0.500 | 25/50 | 170 | 160 | 0.906 |
| TRIAGE-BC / pos-min | 0.440 | 22/50 | 112 | 102 | 1.000 |

Three-split frozen Lift core aggregate:

| method | split 11 | split 22 | split 33 | pooled |
|---|---:|---:|---:|---:|
| weighted BC | 0.480 | 0.660 | 0.720 | 93/150 |
| positive-only NN top160 | 0.460 | 0.680 | 0.500 | 82/150 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 0.440 | 74/150 |

Interpretation update:

- Split 33 strengthens the coverage caveat: TRIAGE-BC reaches perfect selected-support purity, but only selects 102 hidden positives and reaches 0.440 endpoint success.
- Weighted BC is the clear winner on split 33 at 0.720, and now leads the three-split frozen Lift core aggregate with 93/150 successes.
- Positive-only NN top160 also beats TRIAGE-BC on the three-split core aggregate, 82/150 versus 74/150.
- Bad labels improve support purity on all fresh Lift splits, but the policy result does not support a bad-label benefit claim on Lift.
- Paper language should frame Lift as evidence that precision/coverage conversion is the real bottleneck, not as evidence that hard bad-aware filtering is the best policy converter.

## 2026-06-24: Frozen Lift MG sparse split-33 controls and full five-method aggregate

Completed the split-33 all-demo BC and all-positive oracle controls under the same frozen endpoint protocol, then promoted the Lift MG sparse table from a core-only three-split comparison to a full three-split five-method matrix.

Artifacts:

- Split-33 full CSV: `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary.csv`
- Split-33 full report: `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`
- Full three-split aggregate CSV: `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary.csv`
- Full three-split aggregate report: `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`
- Split-33 all-demo run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_bc_all_mixed_policy0/REPORT.md`
- Split-33 all-positive oracle run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_all_train_positive_oracle_policy0/REPORT.md`

Protocol:

- Same Lift MG sparse split seed 33, policy seed 0, official BC-RNN-GMM, 200 epochs, and fixed `model_epoch_200.pth` endpoint.
- Endpoint evaluation used 50 validation-positive initial-state rollouts, horizon 150, CPU fallback, same seed/init-state mode as the existing core rows.
- All-demo BC trains on all 1440 train demos; all-positive oracle trains on all 286 true-positive train demos and is diagnostic only.

Split-33 endpoint results:

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| all-positive oracle | 0.760 | 38/50 | 286 | 0 | n/a |
| weighted BC | 0.720 | 36/50 | 1430 | 1420 weighted | 0.194 |
| positive-only NN top160 | 0.500 | 25/50 | 170 | 160 | 0.906 |
| TRIAGE-BC / pos-min | 0.440 | 22/50 | 112 | 102 | 1.000 |
| all-demo BC | 0.160 | 8/50 | 1440 | all train demos | 0.194 |

Full three-split frozen Lift aggregate:

| method | split 11 | split 22 | split 33 | pooled |
|---|---:|---:|---:|---:|
| all-positive oracle | 0.660 | 0.680 | 0.760 | 105/150 |
| weighted BC | 0.480 | 0.660 | 0.720 | 93/150 |
| positive-only NN top160 | 0.460 | 0.680 | 0.500 | 82/150 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 0.440 | 74/150 |
| all-demo BC | 0.260 | 0.200 | 0.160 | 31/150 |

Interpretation update:

- Weighted BC is the strongest non-oracle method on the completed frozen Lift matrix, reaching 93/150 successes.
- TRIAGE-BC improves selected-support purity on all splits, but the policy result is coverage-limited: split 33 has perfect TRIAGE support purity and still trails weighted BC by 14 successes.
- All-demo mixed cloning is weak on every Lift split and now reaches only 31/150 pooled, so contaminated-log negative-control evidence is stronger.
- The all-positive oracle reaches 105/150 pooled, showing Lift is learnable with broad true-positive support but not saturated.
- The paper should not use Lift as a bad-label policy-benefit result. It should use Lift to argue that score-to-support conversion and precision/coverage balance are the remaining bottleneck.

## 2026-06-24: Frozen Lift MG classifier-score top160 ablation

Tested a broader hard-support converter on the frozen Lift MG sparse splits: labeled positives plus the top 160 unlabeled demos by classifier trajectory score.

Artifacts:

- Ablation CSV: `results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary.csv`
- Ablation report: `results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`
- Split-11 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_classifier_topk_policy0/REPORT.md`
- Split-22 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_classifier_topk_policy0/REPORT.md`
- Split-33 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_classifier_topk_policy0/REPORT.md`

Protocol:

- Same frozen Lift MG sparse split seeds 11/22/33, policy seed 0, official BC-RNN-GMM, 200 epochs, and fixed `model_epoch_200.pth` endpoint.
- Endpoint evaluation used 50 validation-positive initial-state rollouts per split, horizon 150, CPU fallback.
- This is an ablation, not part of the frozen main five-method table.

Support audit:

| split seed | selected unlabeled | hidden-positive | hidden-bad | purity |
|---:|---:|---:|---:|---:|
| 11 | 160 | 154 | 6 | 0.963 |
| 22 | 160 | 150 | 10 | 0.938 |
| 33 | 160 | 158 | 2 | 0.988 |

Endpoint results:

| method | split 11 | split 22 | split 33 | pooled |
|---|---:|---:|---:|---:|
| classifier-score top160 | 0.320 | 0.380 | 0.660 | 68/150 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 0.440 | 74/150 |
| positive-only NN top160 | 0.460 | 0.680 | 0.500 | 82/150 |
| weighted BC | 0.480 | 0.660 | 0.720 | 93/150 |

Interpretation update:

- Classifier-score top160 fixes the split-33 coverage failure directionally, reaching 33/50 versus 22/50 for TRIAGE-BC / pos-min.
- It fails as a general Lift rule: split 11 and split 22 drop to 16/50 and 19/50 despite high support purity.
- Pooled success is 68/150, below TRIAGE-BC, positive-only NN, and weighted BC.
- This rules out a simple fixed classifier top-k rescue. The next Lift method idea needs a policy-quality proxy, task-aware coverage criterion, or variance/checkpoint analysis rather than just broader pure support.

## 2026-06-24: Frozen Can 20p/80b split-11 endpoint diagnostic

Ran a bounded frozen-runner diagnostic on Can Paired with 20 labeled positives and 80 labeled bad demos, split seed 11, policy seed 0.

Artifacts:

- Diagnostic CSV: `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic.csv`
- Diagnostic report: `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md`
- Positive-only NN run: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_positive_only_nn_policy0/REPORT.md`
- TRIAGE-BC run: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_weighted_bc_policy0/REPORT.md`
- Classifier-score top20 setup audit: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_classifier_topk_policy0/REPORT.md`

Protocol:

- Robomimic Can Paired low-dimensional data, frozen split seed 11, policy/classifier seed 0.
- Official Robomimic BC-RNN-GMM, 200 epochs, fixed `model_epoch_200.pth` endpoint.
- Endpoint evaluation used 50 validation-positive initial-state rollouts, horizon 400, CPU fallback.
- This is a diagnostic single split, not a main Can 20p/80b table.

Support audit:

| method/setup | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| positive-only NN top20 | 20 | 17 | 3 | 0.850 |
| TRIAGE-BC / adaptive masscap | 50 | 20 | 30 | 0.400 |
| weighted BC sampler | 100 | 20 | 80 | 0.200 |
| classifier-score top20 setup only | 20 | 11 | 9 | 0.550 |

Endpoint results:

| method | success | successes |
|---|---:|---:|
| positive-only NN top20 | 0.680 | 34/50 |
| TRIAGE-BC / adaptive masscap | 0.660 | 33/50 |
| weighted BC sampler | 0.360 | 18/50 |

Interpretation update:

- The split does not rescue a bad-label policy-benefit claim: positive-only NN top20 edges TRIAGE-BC by one success.
- TRIAGE-BC recovers all hidden-positive unlabeled demos but also admits 30 hidden-bad demos; on this split the additional coverage does not beat cleaner no-bad-label retrieval.
- Weighted BC is clearly weak under this heavy contamination setting, reaching only 18/50 successes from the full 100-demo contaminated pool.
- The result is useful as a support-conversion diagnostic and should be framed as evidence that soft weighting can fail badly under action-conflicting contamination, not as evidence that bad labels are strictly necessary.

## 2026-06-24: Frozen Can 80p/80b support audit and split-33 endpoint diagnostic

Prepared fresh frozen Can Paired balanced 80 hidden-positive / 80 hidden-bad split seeds 11/22/33 for TRIAGE-BC, positive-only NN top80, and classifier-score top80. Then trained/evaluated the most informative endpoint comparison on split seed 33, where TRIAGE-BC had the best support-purity chance.

Artifacts:

- Diagnostic CSV: `results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint.csv`
- Diagnostic report: `results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`
- Split-33 TRIAGE-BC run: `results/final_paper/per_seed/can_paired_balanced_80p80b_split33_triage_bc_policy0/REPORT.md`
- Split-33 positive-only NN run: `results/final_paper/per_seed/can_paired_balanced_80p80b_split33_positive_only_nn_policy0/REPORT.md`

Support audit:

| split seed | method/setup | selected unlabeled | hidden-positive | hidden-bad | purity |
|---:|---|---:|---:|---:|---:|
| 11 | TRIAGE-BC / adaptive masscap | 50 | 43 | 7 | 0.860 |
| 11 | positive-only NN top80 | 80 | 72 | 8 | 0.900 |
| 11 | classifier-score top80 | 80 | 63 | 17 | 0.787 |
| 22 | TRIAGE-BC / adaptive masscap | 75 | 55 | 20 | 0.733 |
| 22 | positive-only NN top80 | 80 | 76 | 4 | 0.950 |
| 22 | classifier-score top80 | 80 | 57 | 23 | 0.713 |
| 33 | TRIAGE-BC / adaptive masscap | 40 | 39 | 1 | 0.975 |
| 33 | positive-only NN top80 | 80 | 72 | 8 | 0.900 |
| 33 | classifier-score top80 | 80 | 70 | 10 | 0.875 |

Split-33 endpoint results:

| method | success | successes |
|---|---:|---:|
| positive-only NN top80 | 0.980 | 49/50 |
| TRIAGE-BC / adaptive masscap | 0.860 | 43/50 |

Interpretation update:

- Fresh balanced Can does not rescue the bad-label policy-benefit claim. Positive-only NN has better hidden-positive coverage on all three support audits and wins the split-33 endpoint comparison by 6/50 successes.
- Split 33 is especially informative because TRIAGE-BC had much higher support purity (`0.975` versus `0.900`), yet lower coverage (`39` versus `72` hidden positives) and lower policy success.
- Classifier-score top80 is not a rescue branch; it is lower-purity than positive-only NN on every fresh support audit.
- The older balanced-Can development result remains useful as score-to-support evidence, but the fresh frozen diagnostic says the main paper should not use balanced Can as evidence that explicit bad labels beat strong no-bad-label retrieval.

## 2026-06-24: Continuous PointNav equal label-budget-5 sweep

Ran the controlled PointNav mechanism benchmark with a smaller equal label budget: 5 positive route-prefix demonstrations and 5 bad shortcut trajectories. This directly addresses the plan's label-budget ablation for the clean synthetic/continuous setting where positive-only BC cannot solve the task by construction.

Artifacts:

- Raw report: `results/continuous_pointnav_gap_select_label_budget5_5seed/REPORT.md`
- Raw metrics: `results/continuous_pointnav_gap_select_label_budget5_5seed/metrics.csv`
- Paper-facing summary: `results/final_paper/ablations/continuous_pointnav_label_budget5_gap_selection_REPORT.md`
- Paper-facing CSV: `results/final_paper/ablations/continuous_pointnav_label_budget5_gap_selection.csv`

Protocol:

- 5 seeds, bad fractions 0.50/0.75/0.90/0.95.
- 180 unlabeled trajectories per seed/fraction.
- Positive labels are 16-step safe-route prefixes only.
- BC steps 6000, classifier steps 2500, 30 closed-loop evaluation rollouts per row.
- TRIAGE row uses trajectory score-gap demo selection with max fraction 0.10 and min fraction 0.02.

Main success results:

| bad frac | BC-all | pos+unlabeled BC | local weighted BC | TRIAGE gap-demo BC | oracle good BC |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.400 | 0.467 | 0.200 | 1.000 | 1.000 |
| 0.75 | 0.340 | 0.293 | 0.200 | 1.000 | 1.000 |
| 0.90 | 0.240 | 0.147 | 0.000 | 1.000 | 1.000 |
| 0.95 | 0.100 | 0.113 | 0.140 | 1.000 | 1.000 |

Gap-selection diagnostics:

| bad frac | selected frac | demo purity | transition purity | hidden-good demos | hidden-bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.034 | 1.000 | 1.000 | 6.2 | 0.0 |
| 0.75 | 0.062 | 1.000 | 1.000 | 11.2 | 0.0 |
| 0.90 | 0.089 | 1.000 | 1.000 | 16.0 | 0.0 |
| 0.95 | 0.057 | 1.000 | 1.000 | 10.2 | 0.0 |

Interpretation update:

- The controlled mechanism result survives smaller equal scarce labels. With only 5 positives and 5 negatives, score-gap demo selection matches the hidden-good oracle across all tested contamination levels.
- This is stronger paper evidence than another Robomimic sweep for the specific mechanism claim: explicit bad labels calibrate trajectory-level support recovery when positives are only prefixes.
- Local state-action weighting remains the wrong mechanism in this environment. It cannot recover the full safe route despite using the same good/bad classifier signal.
- Budget 5 gives a clean label-efficiency result for the main controlled benchmark; the budget-2 stress follow-up is recorded below.

## 2026-06-24: Continuous PointNav equal label-budget-2 stress sweep

Ran the controlled PointNav mechanism benchmark with only 2 positive route-prefix demonstrations and 2 bad shortcut trajectories. This is the stress version of the label-budget ablation.

Artifacts:

- Raw report: `results/continuous_pointnav_gap_select_label_budget2_5seed/REPORT.md`
- Raw metrics: `results/continuous_pointnav_gap_select_label_budget2_5seed/metrics.csv`
- Paper-facing summary: `results/final_paper/ablations/continuous_pointnav_label_budget2_gap_selection_REPORT.md`
- Paper-facing CSV: `results/final_paper/ablations/continuous_pointnav_label_budget2_gap_selection.csv`

Protocol:

- 5 seeds, bad fractions 0.50/0.75/0.90/0.95.
- 180 unlabeled trajectories per seed/fraction.
- Positive labels are 16-step safe-route prefixes only.
- BC steps 6000, classifier steps 2500, 30 closed-loop evaluation rollouts per row.
- TRIAGE row uses trajectory score-gap demo selection with max fraction 0.10 and min fraction 0.02.

Main success results:

| bad frac | BC-all | pos+unlabeled BC | local weighted BC | TRIAGE gap-demo BC | TRIAGE gap-posterior BC | oracle good BC |
|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.460 | 0.440 | 0.147 | 1.000 | 1.000 | 1.000 |
| 0.75 | 0.360 | 0.320 | 0.000 | 1.000 | 1.000 | 1.000 |
| 0.90 | 0.180 | 0.133 | 0.173 | 1.000 | 1.000 | 1.000 |
| 0.95 | 0.140 | 0.120 | 0.000 | 1.000 | 1.000 | 1.000 |

Gap-selection diagnostics:

| bad frac | selected frac | demo purity | transition purity | hidden-good demos | hidden-bad demos |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.032 | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.75 | 0.032 | 1.000 | 1.000 | 5.8 | 0.0 |
| 0.90 | 0.079 | 1.000 | 1.000 | 14.2 | 0.0 |
| 0.95 | 0.051 | 1.000 | 1.000 | 9.2 | 0.0 |

Boundary checks:

- Fixed top-5% demo BC is strong through 90% bad contamination but drops to 0.867 at 95%.
- Fixed top-10% demo BC drops to 0.787 at 90% and 0.613 at 95%.
- Fixed-prior posterior BC becomes brittle at the boundary: prior 0.05 reaches 0.633 at 95%, and prior 0.10 reaches 0.607.
- Score-gap demo BC and score-gap posterior BC avoid this boundary failure by selecting smaller pure support.

Interpretation update:

- The controlled mechanism result survives extreme equal scarce labels. With only 2 positives and 2 negatives, score-gap demo selection and gap-posterior BC match the hidden-good oracle across all tested contamination levels.
- This is now the strongest label-efficiency evidence for the controlled benchmark.
- The key positive result is not just that the classifier can score hidden-good trajectories. The important part is adaptive score-to-support conversion: fixed-fraction and fixed-prior converters fail at the 95% boundary even though the gap selector keeps pure support.
- Local state-action weighting again remains the wrong converter in this environment, reaching 0.000 success at 75% and 95% bad contamination.

## 2026-06-24: Continuous PointNav bad-label-count sweep

Ran the controlled PointNav bad-label-count ablation with the positive budget fixed at 5 route-prefix demonstrations and the bad-demo count set to 1, 2, or 5.

Artifacts:

- `n_neg=1` raw report: `results/continuous_pointnav_bad_label_count_npos5_nneg1_5seed/REPORT.md`
- `n_neg=2` raw report: `results/continuous_pointnav_bad_label_count_npos5_nneg2_5seed/REPORT.md`
- `n_neg=5` raw report: `results/continuous_pointnav_gap_select_label_budget5_5seed/REPORT.md`
- Paper-facing summary: `results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md`
- Paper-facing CSV: `results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5.csv`

Protocol:

- 5 seeds, bad fractions 0.50/0.75/0.90/0.95.
- 180 unlabeled trajectories per seed/fraction.
- Positive labels are 16-step safe-route prefixes only.
- Bad labels are full shortcut trajectories through the trap.
- BC steps 6000, classifier steps 2500, 30 closed-loop evaluation rollouts per row.
- TRIAGE row uses trajectory score-gap demo selection with max fraction 0.10 and min fraction 0.02.

Main success results:

| n_neg | bad frac | BC-all | local weighted BC | TRIAGE gap-demo BC | TRIAGE gap-posterior BC |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.50 | 0.460 | 0.187 | 1.000 | 1.000 |
| 1 | 0.75 | 0.360 | 0.180 | 1.000 | 1.000 |
| 1 | 0.90 | 0.240 | 0.000 | 1.000 | 1.000 |
| 1 | 0.95 | 0.153 | 0.320 | 1.000 | 1.000 |
| 2 | 0.50 | 0.487 | 0.200 | 1.000 | 1.000 |
| 2 | 0.75 | 0.353 | 0.147 | 1.000 | 1.000 |
| 2 | 0.90 | 0.220 | 0.000 | 0.973 | 1.000 |
| 2 | 0.95 | 0.147 | 0.000 | 0.993 | 0.600 |
| 5 | 0.50 | 0.400 | 0.200 | 1.000 | 1.000 |
| 5 | 0.75 | 0.340 | 0.200 | 1.000 | 1.000 |
| 5 | 0.90 | 0.240 | 0.000 | 1.000 | 1.000 |
| 5 | 0.95 | 0.100 | 0.140 | 1.000 | 0.573 |

Support diagnostics:

- Gap selection has 1.000 demo purity and 1.000 transition purity in all 12 rows.
- It admits 0 hidden-bad demos on average in every row.
- At 95% bad unlabeled data, the selected support averages 10.2 hidden-good demos and 0 hidden-bad demos for every bad-label count.

Interpretation update:

- The controlled mechanism is highly label-efficient in its use of explicit bad demonstrations. With 5 positive prefixes, even 1 bad shortcut demo is enough for score-gap demo BC to reach 1.000 success at every tested contamination level.
- The result is not monotonic in the bad-demo count because policy training and posterior conversion have stochastic boundary failures. With 2 bad demos, gap-demo dips slightly at 90% and 95%; with 5 bad demos, gap-demo is perfect but gap-posterior remains brittle at 95%.
- The support-side story is clean and stronger than the policy-side stochasticity: score-gap selection recovers pure hidden-good support across all tested counts and contamination levels.
- This supports a controlled label-efficiency claim for explicit bad labels, but it does not establish a zero-bad-label comparison because the tri-signal classifier requires negative examples.

## 2026-06-24: Frozen Can 40p/80b score-support tradeoff

Aggregated existing frozen Can Paired 40 hidden-positive / 80 hidden-bad score diagnostics across split seeds 11/22/33 into a precision/coverage support sweep.

Artifacts:

- Summary script: `scripts/summarize_can40_score_support_tradeoff.py`
- Figure script: `scripts/plot_can40_precision_coverage.py`
- Aggregate CSV: `results/final_paper/ablations/can40_score_support_tradeoff.csv`
- Per-split CSV: `results/final_paper/ablations/can40_score_support_tradeoff_per_split.csv`
- Paper-facing report: `results/final_paper/ablations/can40_score_support_tradeoff_REPORT.md`
- Paper Figure 2 candidate: `results/final_paper/figures/can40_precision_coverage.png`
- Paper Figure 2 candidate PDF: `results/final_paper/figures/can40_precision_coverage.pdf`

Aggregate support sweep:

| support rule | selected/split | purity | hidden-positive recall | hidden-bad admission | endpoint success |
|---|---:|---:|---:|---:|---:|
| classifier top10 | 10.0 | 0.867 | 0.217 | 0.017 | n/a |
| classifier top20 | 20.0 | 0.850 | 0.425 | 0.037 | n/a |
| classifier top40 | 40.0 | 0.708 | 0.708 | 0.146 | n/a |
| classifier top60 | 60.0 | 0.600 | 0.900 | 0.300 | n/a |
| classifier top80 | 80.0 | 0.483 | 0.967 | 0.517 | n/a |
| TRIAGE adaptive masscap | 63.3 | 0.579 | 0.917 | 0.333 | 0.660 |
| weighted full pool | 120.0 | 0.333 | 1.000 | 1.000 | 0.600 |
| positive-only NN top40 | 40.0 | 0.883 | 0.883 | 0.058 | 0.720 |

Interpretation update:

- The classifier-score top-k sweep directly shows the precision/coverage tradeoff requested by the plan: small supports are cleaner but miss many hidden positives; broad supports recover positives while admitting many hidden bad demos.
- TRIAGE-BC adaptive masscap gets high hidden-positive recall (`110/120`) and beats weighted BC at the endpoint (`99/150` versus `90/150`) by reducing bad admission.
- Positive-only NN top40 is a better Can 40p/80b support point: it recovers slightly fewer hidden positives (`106/120`) but admits far fewer hidden bad demos (`14/240`) and reaches the best non-oracle endpoint success (`108/150`).
- This reinforces the main Can interpretation: score-to-support conversion matters, but the current bad-aware converter is not on the best precision/coverage frontier compared with strong no-bad retrieval.

## 2026-06-24: Can MG branch-proxy staged as abstention diagnostic

Refreshed the existing Can MG branch-proxy analysis and staged it under final-paper ablations.

Artifacts:

- Summary script: `scripts/summarize_robomimic_can_mg_branch_proxy.py`
- Paper-facing report: `results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`
- Method proxy CSV: `results/final_paper/ablations/can_mg_branch_proxy_summary/method_proxy_scores.csv`
- Proxy-winner CSV: `results/final_paper/ablations/can_mg_branch_proxy_summary/proxy_winners.csv`

Main result:

| split | rollout-best | best 20k | failed proxy behavior |
|---|---|---:|---|
| Can MG original | weighted BC | 0.333 | all tested likelihood proxies choose all-positive support, which reaches 0.200 |
| Can MG shuffle42 | hard/soft tie | 0.100 | likelihood can choose a branch but cannot detect that both branches are weak |

Interpretation update:

- Simple positive imitation, positive-minus-negative likelihood gap, and negative rejection are not valid replacements for router-v2 abstention on Can MG.
- The failure mode is coverage: the all-positive branch fits positives and rejects negatives, but loses the broad support that weighted sampling uses.
- Can MG should remain a stress/limitation result unless a new coverage-sensitive policy-quality proxy is proposed and predeclared before further policy training.

## 2026-06-24: Current Robomimic endpoint matrix figure

Generated a consolidated current Robomimic endpoint matrix from staged final-paper artifacts.

Artifacts:

- Summary script: `scripts/summarize_final_endpoint_matrix.py`
- CSV: `results/final_paper/tables/robotics_current_endpoint_matrix.csv`
- Report: `results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md`
- Figure PNG: `results/final_paper/figures/robotics_current_endpoint_matrix.png`
- Figure PDF: `results/final_paper/figures/robotics_current_endpoint_matrix.pdf`

Rows included:

- Can 40p/80b: primary frozen three-split aggregate over split seeds 11/22/33.
- Lift MG: primary frozen three-split aggregate over split seeds 11/22/33.
- Can 20p/80b: diagnostic split-11 endpoint only.
- Can 80p/80b: diagnostic split-33 endpoint only, with split 11/22 support-only audits.

Interpretation update:

- The figure is suitable as a current Figure 3 candidate only because diagnostic single-split tasks are visibly shaded and labeled.
- It makes the current robotics story compact: Can 40p/80b supports TRIAGE over weighted/all-demo but not over positive-only NN; Lift MG supports contaminated-log harm and score-calibration but favors weighted BC at the endpoint; the Can 20/80 and 80/80 diagnostics both reinforce the positive-only caveat.
- Completing three-split endpoint tables for Can 20p/80b and Can 80p/80b remains the main compute-heavy upgrade if those tasks are to become primary table rows.

## 2026-06-24: Controlled PointNav mechanism figure

Generated a consolidated controlled PointNav mechanism table and two-panel figure from the staged final-paper ablations.

Artifacts:

- Summary script: `scripts/summarize_pointnav_controlled_mechanism.py`
- CSV: `results/final_paper/tables/pointnav_controlled_mechanism.csv`
- Report: `results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`
- Figure PNG: `results/final_paper/figures/pointnav_controlled_mechanism.png`
- Figure PDF: `results/final_paper/figures/pointnav_controlled_mechanism.pdf`

Figure content:

- Left panel: equal scarce labels with only 2 positive route prefixes and 2 bad shortcut trajectories. TRIAGE gap support reaches 1.000 success at 50/75/90/95% bad unlabeled data, matching the hidden-good oracle while BC-all, positive+unlabeled BC, and local weighted BC degrade.
- Right panel: fixed 5 positive prefixes with 1/2/5 bad shortcut demos. Gap support remains perfect for 1 and 5 bad demos and near-perfect for 2 bad demos at the high-contamination boundary.

Interpretation update:

- This is now the cleanest main controlled mechanism artifact for the paper.
- It supports the label-efficiency claim for explicit bad labels without spending more Robomimic compute.
- It should be used as the main controlled PointNav Table 1 / mechanism figure source, while the raw ablation reports remain appendices.

## 2026-06-24: Score-shape diagnostics figure

Generated the current Figure 4 score-shape diagnostic from existing score-ranking artifacts.

Artifacts:

- Summary script: `scripts/plot_score_shape_diagnostics.py`
- CSV: `results/final_paper/tables/score_shape_diagnostics.csv`
- Report: `results/final_paper/tables/score_shape_diagnostics_REPORT.md`
- Figure PNG: `results/final_paper/figures/score_shape_diagnostics.png`
- Figure PDF: `results/final_paper/figures/score_shape_diagnostics.pdf`

Source scope:

- Can 40p/80b: frozen split seeds 11/22/33.
- Lift MG: frozen split seeds 11/22/33.
- Can MG: original stress diagnostic; not a final endpoint row.

Key score-shape summaries:

| analysis | positive mean | bad mean | pos >= .95 | bad >= .95 | plotted threshold |
|---|---:|---:|---:|---:|---:|
| Can 40p/80b | 0.713 | 0.368 | 0.117 | 0.017 | 0.479 |
| Lift MG | 0.790 | 0.152 | 0.399 | 0.002 | 0.903 |
| Can MG | 0.886 | 0.423 | 0.518 | 0.094 | 0.873 |

Interpretation update:

- Can 40p/80b has meaningful positive/bad overlap, which supports the precision/coverage conversion framing.
- Lift MG has strong score separation, but the frozen endpoint matrix still favors weighted BC; this visualizes why support purity alone is not enough.
- Can MG has a large high-score plateau containing both positives and bad demos, which supports router-v2 abstention and the failed likelihood-proxy interpretation.

## 2026-06-24: Frozen Can 20p/80b three-split support audit

Prepared the missing frozen Can Paired 20 hidden-positive / 80 hidden-bad split-seed 22 and 33 support/setup rows for TRIAGE-BC, positive-only NN top20, and weighted BC. Then trained/evaluated a bounded split-22 endpoint extension for TRIAGE-BC and positive-only NN top20, and aggregated split seeds 11/22/33 into a support diagnostic.

Artifacts:

- Summary script: `scripts/summarize_can20_support_audit.py`
- Aggregate CSV: `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split.csv`
- Per-split CSV: `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_per_split.csv`
- Paper-facing report: `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`
- New split-22 setup runs: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_*_policy0/`
- New split-33 setup runs: `results/final_paper/per_seed/can_paired_pos20_bad80_split33_*_policy0/`
- Split-22 positive-only endpoint report: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_positive_only_nn_policy0/eval_endpoint_200/REPORT.md`
- Split-22 TRIAGE endpoint report: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_triage_bc_policy0/eval_endpoint_200/REPORT.md`

Aggregate support audit:

| support rule | selected/split | purity | hidden-positive recall | hidden-bad admission | completed endpoint |
|---|---:|---:|---:|---:|---:|
| classifier top20 | 20.0 | 0.683 | 0.683 | 0.079 | n/a |
| TRIAGE adaptive masscap | 41.0 | 0.439 | 0.900 | 0.287 | 46/100 |
| positive-only NN top20 | 20.0 | 0.817 | 0.817 | 0.046 | 54/100 |
| weighted full pool | 100.0 | 0.200 | 1.000 | 1.000 | 18/50 |

Interpretation update:

- TRIAGE-BC recovers more hidden-positive unlabeled demos than positive-only NN top20 across the three splits (`54/60` versus `49/60`) but admits far more hidden-bad demos (`69/240` versus `11/240`).
- The router behavior is split-sensitive: broad contaminated support on split 11 and 22, but a cleaner top20-style support on split 33.
- The completed split-11 and split-22 endpoint results both favor positive-only NN over TRIAGE-BC: 34/50 versus 33/50 on split 11, and 20/50 versus 13/50 on split 22.
- Weighted BC remains clearly weak under heavy contamination on the split-11 endpoint, but split-22 weighted endpoint training was not run.
- This strengthens the precision/coverage framing and the positive-only baseline caveat; it still does not support a bad-label policy-benefit claim on Can 20p/80b.

## 2026-06-24: Paper outline and method diagram

Started the writing phase by turning the current claim package into a paper-facing outline and adding a reproducible Figure 1 candidate.

Artifacts:

- Paper outline: `PAPER_DRAFT_OUTLINE.md`
- Method-diagram script: `scripts/plot_triage_bc_method_diagram.py`
- Figure PNG: `results/final_paper/figures/triage_bc_method_diagram.png`
- Figure PDF: `results/final_paper/figures/triage_bc_method_diagram.pdf`
- Manuscript draft: `paper/triage_bc_draft.md`
- Paper README: `paper/README.md`
- Artifact-reference validator: `scripts/validate_paper_artifact_refs.py`

Outline status:

- Uses the current safe thesis: tri-signal labels can calibrate desirability scores, but score-to-support conversion is the bottleneck.
- Maps every main figure/table slot to staged artifacts under `results/final_paper/`.
- Keeps positive-only NN, weighted BC, Lift coverage, and Can MG abstention as explicit limitations.
- Leaves the LaTeX target undecided; this is a claim-safe scaffold for the manuscript, not a submission template.
- The draft artifact references currently validate with `python scripts/validate_paper_artifact_refs.py`.

## 2026-06-24: Standalone LaTeX manuscript scaffold

Converted the claim-safe Markdown draft into a compileable standalone LaTeX
paper scaffold, while preserving the narrower score-to-support conversion
framing and explicit limitations.

Artifacts:

- LaTeX source: `paper/triage_bc_paper.tex`
- Bibliography: `paper/references.bib`
- Build helper: `paper/Makefile`
- Compiled PDF: `paper/triage_bc_paper.pdf`
- Updated paper README: `paper/README.md`
- Updated artifact-reference validator: `scripts/validate_paper_artifact_refs.py`

Draft content:

- Adds a compact related-work section with initial anchors for imitation
  learning, DAgger, adversarial imitation, offline RL, advantage-weighted
  policy extraction, Robomimic, and positive-unlabeled learning.
- Converts TRIAGE-BC v0.1 from `METHOD_FREEZE.md` into a method section with
  score learning, trajectory calibration, positive-mass estimation,
  support-conversion rules, router-v2 pseudocode, and policy-training details.
- Includes the staged paper figures from `results/final_paper/figures/` and a
  conservative endpoint-result table.
- Keeps the main caveats explicit: positive-only NN is strongest on Can,
  weighted BC is strongest on Lift, Can MG is abstained/stress evidence, and
  the robotics method is not a validated inverse-Q actor-extraction method.

Validation:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
git diff --check
```

The validator now checks TeX figure includes and bibliography references in
addition to Markdown artifact paths. Current result: `checked 36 unique artifact
references`, and the LaTeX build produces a 10-page PDF with citations and
figures resolved.

## 2026-06-24: Primary-only Robomimic Figure 3

Split the Robomimic endpoint visualization into a main-paper primary matrix and
a broader diagnostic matrix.

Artifacts:

- Updated summary script: `scripts/summarize_final_endpoint_matrix.py`
- Primary CSV: `results/final_paper/tables/robotics_primary_endpoint_matrix.csv`
- Primary report: `results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`
- Primary figure PNG: `results/final_paper/figures/robotics_primary_endpoint_matrix.png`
- Primary figure PDF: `results/final_paper/figures/robotics_primary_endpoint_matrix.pdf`
- Diagnostic matrix retained: `results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md`

Rationale:

- The old Figure 3 candidate showed Can 20p/80b and Can 80p/80b as shaded
  diagnostic rows. That was accurate but visually risky for a main paper figure.
- The new primary figure contains only completed frozen three-split aggregates:
  Can 40p/80b and Lift MG.
- The diagnostic Can 20p/80b and Can 80p/80b rows remain staged for appendix
  discussion and claim-package caveats.

Interpretation:

- Can 40p/80b remains the main positive robotics result for hard support over
  weighted BC and all-demo cloning, with positive-only NN still stronger.
- Lift MG remains the main coverage counterexample, where weighted BC is the
  best non-oracle row.

## 2026-06-24: Primary endpoint uncertainty summary

Added descriptive uncertainty summaries for the primary frozen Robomimic endpoint
matrix.

Artifacts:

- Summary script: `scripts/summarize_primary_endpoint_uncertainty.py`
- Endpoint uncertainty CSV: `results/final_paper/tables/primary_endpoint_uncertainty.csv`
- Pairwise delta CSV: `results/final_paper/tables/primary_endpoint_pairwise_deltas.csv`
- Report: `results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md`

Content:

- Reports pooled rollout-level Wilson intervals for each primary Can 40p/80b
  and Lift MG method row.
- Reports split-level mean/std across split seeds 11/22/33.
- Reports paired split deltas for the main paper comparisons.

Interpretation:

- Can 40p/80b favors TRIAGE-BC over weighted BC on every split, but the pooled
  gap is modest (`+0.060`) and descriptive Wilson intervals overlap.
- Can 40p/80b does not support TRIAGE-BC over positive-only NN; positive-only is
  higher pooled and the paired split deltas change sign.
- Lift MG favors weighted BC over TRIAGE-BC pooled, but the split deltas are not
  direction-consistent because TRIAGE-BC wins split 11.
- These intervals are descriptive rather than formal independent-test claims
  because endpoint rollouts reuse validation-positive start pools within each
  split.

## 2026-06-24: Algorithm and precision/coverage manuscript pass

Tightened the manuscript method and analysis text without adding new compute.

Updated artifacts:

- LaTeX source: `paper/triage_bc_paper.tex`
- Markdown draft: `paper/triage_bc_draft.md`
- Outline: `PAPER_DRAFT_OUTLINE.md`

Changes:

- Added a frozen TRIAGE-BC v0.1 algorithmic summary: data split, classifier
  training, trajectory scoring, positive-mass estimation, score-shape routing,
  fixed-budget policy training, and audit-only hidden-label use.
- Added a precision/coverage analysis section. It defines hidden-positive recall
  and hidden-bad admission for audit, explains why hard support helps under
  action-conflicting contamination, and explains why hard support fails when it
  under-covers useful state-action regions.
- Cleared the draft TODO about refining method pseudocode; remaining writing
  tasks are related-work tightening, template conversion, optional appendix
  diagnostics, and any venue-specific statistical additions.

## 2026-06-24: Paper reproducibility checklist

Added and tested a concise reproduction checklist for the current paper package.

Artifacts:

- Reproduction checklist: `paper/REPRODUCE_PAPER.md`
- Updated paper README: `paper/README.md`
- Updated artifact-reference validator: `scripts/validate_paper_artifact_refs.py`

Checklist scope:

- Separates cheap artifact regeneration from expensive frozen Robomimic
  train/eval reruns.
- Gives the exact cheap commands for regenerating the method diagram, PointNav
  mechanism figure, Can 40 precision/coverage table and figure, primary
  endpoint matrix, uncertainty table, score-shape diagnostics, and Can 20
  support audit.
- Gives the frozen `scripts/run_final_matrix.py` command template for expensive
  primary Robomimic reruns.
- Lists validation gates for Python syntax, artifact-reference checking, LaTeX
  compile, and diff whitespace hygiene.

Validation:

```bash
python scripts/plot_triage_bc_method_diagram.py
python scripts/summarize_pointnav_controlled_mechanism.py
python scripts/summarize_can40_score_support_tradeoff.py
python scripts/plot_can40_precision_coverage.py
python scripts/summarize_final_endpoint_matrix.py
python scripts/summarize_primary_endpoint_uncertainty.py
python scripts/plot_score_shape_diagnostics.py
python scripts/summarize_can20_support_audit.py
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
git diff --check
```

The artifact validator now includes `paper/REPRODUCE_PAPER.md` and checks `50`
unique artifact references.

## 2026-06-24: Related-work manuscript tightening

Tightened the paper's related-work framing without changing experiments or
claims.

Updated artifacts:

- LaTeX source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- Markdown draft: `paper/triage_bc_draft.md`
- Bibliography: `paper/references.bib`
- Outline: `PAPER_DRAFT_OUTLINE.md`

Changes:

- Added related-work anchors for classical IRL, apprenticeship learning,
  maximum-entropy IRL, GAIL, CQL, data-quality work in imitation learning, and
  Robomimic sequence imitation.
- Clarified that the robotics contribution is score-to-support conversion
  before official BC-RNN-GMM, not a validated inverse-Q robotics method or a new
  Robomimic policy architecture.
- Mirrored the related-work argument in the Markdown draft and removed the
  related-work TODO from the remaining draft tasks.

Validation:

```bash
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
pdftotext paper/triage_bc_paper.pdf /tmp/triage_bc_paper.txt
git diff --check
```

Results:

- Artifact-reference validator still checks `50` unique artifact references.
- The compiled PDF is 12 pages on letter paper.
- The LaTeX log scan produced no warning or overfull matches.
- The extracted PDF text contains the new related-work anchors.
- `git diff --check` is clean.

## 2026-06-24: Manuscript checklist and validation wiring

Promoted the figure/table map into a dedicated manuscript handoff checklist for
venue-template conversion.

Updated artifacts:

- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Paper README: `paper/README.md`
- Artifact-reference validator: `scripts/validate_paper_artifact_refs.py`
- Outline: `PAPER_DRAFT_OUTLINE.md`
- Completion plan status: `tri_piql_paper_completion_plan.md`

Checklist content:

- Main-paper claim map with evidence reports.
- Claims to avoid, keeping the current score-to-support framing conservative.
- Figure/table slot map for the standalone draft.
- Appendix-only diagnostic map for Can 20p/80b, Can 80p/80b, Can MG, and Lift
  classifier top160.
- Submission validation commands and expected current gates.
- Open decisions for venue/template conversion.

Policy decisions recorded:

- Square and Transport remain repository-only diagnostics for now.
- They should enter a venue appendix only if a later draft needs support-side
  relative-quality examples.

Validation:

```bash
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
git diff --check
```

Results:

- Artifact-reference validator now checks `54` unique artifact references.
- The compiled PDF is 14 pages on letter paper.
- The LaTeX log scan produced no warning, underfull, or overfull matches.
- `git diff --check` is clean.

## 2026-06-24: Precision/coverage theory pass

Added the small analysis component requested by the completion plan, without
adding new experiments or strengthening claims beyond the evidence.

Updated artifacts:

- LaTeX source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- Markdown draft: `paper/triage_bc_draft.md`
- Outline: `PAPER_DRAFT_OUTLINE.md`
- Completion plan status: `tri_piql_paper_completion_plan.md`

Changes:

- Added a simple mixture view of the unlabeled log as useful hidden support plus
  harmful/action-conflicting support.
- Added a schematic BC risk decomposition with a coverage/estimation term and a
  bad-action contamination term.
- Added the weighted-BC analogue using effective sample size and weighted bad
  mass.
- Connected the analysis back to the frozen method: mass-capping estimates when
  marginal coverage is no longer worth marginal contamination, pos-min broadens
  support when score shapes are favorable, and abstention is appropriate when
  the score shape cannot identify the tradeoff.
- Kept the section explicitly non-theorem-level because the current robotics
  policies are nonlinear sequence BC learners.

Validation:

```bash
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
pdftotext paper/triage_bc_paper.pdf /tmp/triage_bc_paper.txt
git diff --check
```

Results:

- Artifact-reference validator still checks `50` unique artifact references.
- The compiled PDF is 13 pages on letter paper.
- The LaTeX log scan produced no warning or overfull matches.
- The extracted PDF text contains `A Simple Precision/Coverage Analysis` and
  the mixture/risk-decomposition language.
- `git diff --check` is clean.

## 2026-06-24: Diagnostic appendix pass

Promoted the existing diagnostic evidence into an explicit appendix section
without changing the main result claims.

Updated artifacts:

- LaTeX source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- Markdown draft: `paper/triage_bc_draft.md`
- Outline: `PAPER_DRAFT_OUTLINE.md`
- Completion plan status: `tri_piql_paper_completion_plan.md`

Changes:

- Added the broader Robomimic diagnostic endpoint matrix as an appendix figure.
- Added a compact appendix diagnostic table for Can 20p/80b, Can 80p/80b, Can
  MG, and the Lift MG classifier-top160 ablation.
- Kept Can 20p/80b and Can 80p/80b labeled as diagnostics rather than main
  claims because they are not complete three-split endpoint tables.
- Resolved the draft TODO about whether diagnostic Can rows should appear in
  appendix figures: yes, appendix only.

Validation:

```bash
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
pdftotext paper/triage_bc_paper.pdf /tmp/triage_bc_paper.txt
git diff --check
```

Results:

- Artifact-reference validator now checks `53` unique artifact references.
- The compiled PDF is 14 pages on letter paper.
- The LaTeX log scan produced no warning, underfull, or overfull matches after
  replacing the appendix table with an itemized diagnostic list.
- The extracted PDF text contains `Diagnostic Endpoint and Support Evidence`
  and the Can 20p/80b, Can 80p/80b, Can MG, and Lift top160 diagnostics.
- `git diff --check` is clean.

## 2026-06-24: Paper claim-number validator

Added a cheap guardrail that checks quoted manuscript numbers against the
staged final-paper CSVs.

Updated artifacts:

- Claim-number validator: `scripts/validate_paper_claim_numbers.py`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Paper README: `paper/README.md`
- Reproduction checklist: `paper/REPRODUCE_PAPER.md`
- Outline: `PAPER_DRAFT_OUTLINE.md`
- Completion plan status: `tri_piql_paper_completion_plan.md`

Changes:

- Validates the primary Can 40p/80b and Lift MG endpoint counts against
  `results/final_paper/tables/robotics_primary_endpoint_matrix.csv`.
- Validates PointNav label-budget success, Can 40 support-side
  precision/coverage counts, Can 20/80 diagnostics, Can MG branch-proxy
  diagnostics, and Lift classifier-top160 diagnostics.
- Checks the manuscript checklist retains the key claim-avoidance guardrails:
  no uniform TRIAGE-BC-over-weighted claim, no uniform TRIAGE-BC-over-positive
  claim, no bad-label-necessity claim on Can, and no validated inverse-Q
  robotics claim.
- Adds the validator to the paper README, reproduction checklist, and
  submission checklist.

Validation:

```bash
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_artifact_refs.py scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
git diff --check
```

Results:

- Claim-number validator passes: `validated paper claim numbers against staged
  CSVs and manuscript text`.
- Artifact-reference validator now checks `55` unique artifact references.
- The compiled PDF is 14 pages on letter paper.
- The final LaTeX log scan produced no warning, underfull, or overfull matches.
- `git diff --check` is clean.

## 2026-06-24: PointNav-first result-order freeze

Resolved the remaining result-order decision for the standalone manuscript.
The paper now presents PointNav as the first result subsection because it is the
cleanest mechanism test, then moves to the Robomimic endpoint matrix and
precision/coverage caveats.

Updated artifacts:

- LaTeX source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- Markdown draft: `paper/triage_bc_draft.md`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Outline: `PAPER_DRAFT_OUTLINE.md`
- Completion plan status: `tri_piql_paper_completion_plan.md`

Changes:

- Added a `Controlled PointNav Mechanism Result` subsection at the start of the
  LaTeX Results section.
- Kept Robomimic as the benchmark endpoint evidence immediately afterward.
- Recorded the result-order decision in the checklist, outline, and completion
  plan so template conversion has one less open structural choice.
- Preserved the conservative claim framing: PointNav isolates the support
  recovery mechanism and is not presented as robotics-scale dominance evidence.

Validation:

```bash
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_artifact_refs.py scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
git diff --check
```

Results:

- Claim-number validator passes.
- Artifact-reference validator checks `55` unique artifact references.
- The compiled PDF is 14 pages on letter paper.
- The final LaTeX log scan produced no warning, underfull, or overfull matches.
- `git diff --check` is clean.

## 2026-06-24: Primary endpoint paired-bootstrap audit

Added a paired uncertainty audit for the primary Robomimic endpoint matrix using
the staged per-episode metrics.

Updated artifacts:

- Paired-bootstrap script: `scripts/summarize_primary_endpoint_paired_bootstrap.py`
- Paired-bootstrap CSV: `results/final_paper/tables/primary_endpoint_paired_bootstrap.csv`
- Paired-bootstrap report: `results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md`
- LaTeX source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- Markdown draft: `paper/triage_bc_draft.md`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Paper README and reproduction checklist: `paper/README.md`,
  `paper/REPRODUCE_PAPER.md`
- Claim package: `results/PAPER_CLAIM_PACKAGE.md`
- Outline and completion plan status: `PAPER_DRAFT_OUTLINE.md`,
  `tri_piql_paper_completion_plan.md`
- Claim-number validator: `scripts/validate_paper_claim_numbers.py`

Method:

- For each method pair, episode successes are averaged by held-out
  `initial_demo_id`.
- Bootstrap samples resample split seeds and paired initial states, avoiding the
  assumption that repeated rollouts from the same initial states are fully
  independent.
- Exact split-level sign tests are reported as a low-power guardrail with only
  three split seeds.

Key results:

| task | comparison | point delta | paired bootstrap 95% interval | split signs |
|---|---:|---:|---:|---:|
| Can 40p/80b | TRIAGE-BC - weighted BC | +0.060 | [-0.113, 0.240] | +++ |
| Can 40p/80b | TRIAGE-BC - positive-only NN | -0.060 | [-0.313, 0.200] | --+ |
| Lift MG | weighted BC - TRIAGE-BC | +0.122 | [-0.100, 0.317] | -++ |
| Lift MG | TRIAGE-BC - all-demo BC | +0.306 | [0.211, 0.400] | +++ |

Interpretation update:

- The Can 40p/80b hard-support-over-weighted result remains directionally
  consistent across splits, but the paired bootstrap interval crosses zero.
- Can 40p/80b still does not support TRIAGE-BC over positive-only retrieval.
- Lift MG remains a coverage-sensitive reversal favoring weighted BC over
  TRIAGE-BC in point estimate, but not as a formal significance claim.
- The only primary paired-bootstrap interval strictly above zero is TRIAGE-BC
  over all-demo BC on Lift MG.
- The manuscript now explicitly uses this as a wording guardrail rather than as
  a new stronger claim.

Validation:

```bash
python -m py_compile scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_artifact_refs.py scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
git diff --check
```

Results:

- Paired-bootstrap report regenerates from staged per-episode metrics.
- Claim-number validator passes against the staged paired-bootstrap CSV and
  manuscript text.
- Artifact-reference validator checks `58` unique artifact references.
- The compiled PDF is 14 pages on letter paper.
- The final LaTeX log scan produced no warning, underfull, or overfull matches.
- `git diff --check` is clean.

## 2026-06-24: Provisional ICLR template conversion

Converted the claim-checked standalone manuscript into a provisional
ICLR-format submission shell.

Updated artifacts:

- ICLR-format source and PDF: `paper/iclr2026/main.tex`,
  `paper/iclr2026/main.pdf`
- Local ICLR 2026 style bundle: `paper/iclr2026/iclr2026_conference.sty`,
  `paper/iclr2026/iclr2026_conference.bst`, `paper/iclr2026/fancyhdr.sty`,
  `paper/iclr2026/natbib.sty`, `paper/iclr2026/math_commands.tex`
- ICLR bibliography copy: `paper/iclr2026/references.bib`
- Build helper: `paper/Makefile`
- Standalone and ICLR claim validators:
  `scripts/validate_paper_claim_numbers.py`,
  `scripts/validate_paper_artifact_refs.py`
- Paper docs and status handoff: `paper/README.md`,
  `paper/MANUSCRIPT_CHECKLIST.md`, `paper/REPRODUCE_PAPER.md`,
  `PAPER_DRAFT_OUTLINE.md`, `tri_piql_paper_completion_plan.md`
- TeX intermediate ignores in `.gitignore`

Changes:

- Transplanted the standalone draft into the official ICLR 2026 style as a
  provisional shell.
- Moved the longer precision/coverage derivation to the appendix in the ICLR
  source while keeping the concise precision/coverage view in the main text.
- Placed the bibliography before the appendix and forced the appendix onto a
  new page after the references.
- Extended paper validators so the ICLR source is checked for quoted claim
  numbers, graphics, and bibliography references.
- Added an ICLR target to the paper Makefile.
- Documented that the ICLR files should be refreshed if the final target venue
  or year changes.

Validation:

```bash
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
make -C paper all
make -C paper iclr
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/iclr2026/main.pdf
pdftotext -layout -f 10 -l 10 paper/iclr2026/main.pdf -
pdftotext -layout -f 11 -l 11 paper/iclr2026/main.pdf -
git diff --check
latexmk -c -cd paper/triage_bc_paper.tex
latexmk -c -cd paper/iclr2026/main.tex
```

Results:

- Claim-number validator passes against staged CSVs, the standalone manuscript,
  the ICLR manuscript, and the Markdown draft.
- Artifact-reference validator checks `63` unique local references.
- The standalone PDF remains 14 pages on letter paper.
- The ICLR PDF is 13 pages on letter paper.
- `make -C paper all` and `make -C paper iclr` both report their PDFs are up
  to date.
- ICLR references begin on page 10 and appendix material begins on page 11, so
  the main text fits the ICLR 2026 9-page main-text budget.
- The standalone LaTeX log scan produced no warning, underfull, or overfull
  matches before cleanup.
- The ICLR log scan produced no unresolved-reference, natbib, or overfull
  matches before cleanup; remaining underfull boxes are from template/page
  balancing and long artifact paths.
- `git diff --check` is clean.

## 2026-06-24: ICLR reproducibility-map polish

Polished the submission-facing reproducibility appendix without changing
experimental claims or numbers.

Updated artifacts:

- Standalone source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- ICLR source and PDF: `paper/iclr2026/main.tex`,
  `paper/iclr2026/main.pdf`
- Artifact-reference validator: `scripts/validate_paper_artifact_refs.py`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`

Changes:

- Renamed the internal `Artifact Checklist` appendix to `Reproducibility and
  Artifact Map`.
- Added a short reproducibility statement pointing to `METHOD_FREEZE.md`,
  `configs/final_method.yaml`, `configs/final_eval.yaml`, and
  `paper/REPRODUCE_PAPER.md`.
- Made the ICLR source start references on page 10 and appendix material on
  page 11 with explicit page breaks.
- Extended the artifact-reference validator to check root-relative `\path{...}`
  entries in TeX sources.

Validation:

```bash
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/iclr2026/main.pdf
pdftotext -layout -f 9 -l 11 paper/iclr2026/main.pdf -
git diff --check
```

Results:

- Claim-number validator passes.
- Artifact-reference validator checks `63` unique local references, now
  including root-relative TeX `\path{...}` entries.
- The standalone PDF remains 14 pages.
- The ICLR PDF remains 13 pages; page 9 ends at the conclusion, references
  start on page 10, and appendix material starts on page 11.
- Both LaTeX log scans produced no unresolved-reference, citation-warning, or
  overfull matches under the recorded scan patterns.

## 2026-06-24: PointNav bad-label-count appendix promotion

Promoted an already-staged controlled ablation into the manuscript appendix so
the paper has explicit label-efficiency evidence for the mechanism.

Updated artifacts:

- Standalone source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- ICLR source and PDF: `paper/iclr2026/main.tex`,
  `paper/iclr2026/main.pdf`
- Markdown draft: `paper/triage_bc_draft.md`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Reproduction checklist: `paper/REPRODUCE_PAPER.md`
- Claim-number validator: `scripts/validate_paper_claim_numbers.py`

Evidence promoted:

- Source report:
  `results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md`
- With 5 positive prefixes and `1/2/5` labeled bad shortcut trajectories, the
  selected support has `1.000` demo purity, `1.000` transition purity, and
  `0` hidden-bad demos in every row.
- The 1-bad and 5-bad settings reach `1.000` gap-demo success at every tested
  contamination level.
- The 2-bad setting remains near-perfect but dips to `0.973` and `0.993` at
  90% and 95% bad unlabeled data.

Interpretation update:

- This strengthens the controlled PointNav label-efficiency story.
- It is explicitly framed as controlled mechanism evidence, not a claim that
  bad labels are necessary on Can or that TRIAGE-BC beats positive-only
  retrieval on robotics.

Validation:

```bash
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
pdftotext -layout -f 9 -l 11 paper/iclr2026/main.pdf -
git diff --check
```

Results:

- Claim-number validator passes and now checks the PointNav bad-label-count CSV
  for pure selected support, zero hidden-bad admission, and the stated 1-bad and
  5-bad perfect-success rows.
- Artifact-reference validator checks `64` unique local references.
- Standalone PDF is 15 pages.
- ICLR PDF remains 13 pages; main text ends on page 9, references start on page
  10, and appendix material starts on page 11.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Submission-language cleanup

Removed internal planning language from the paper sources so the draft reads as
a submission artifact rather than a self-assessment memo.

Updated artifacts:

- Standalone source and PDF: `paper/triage_bc_paper.tex`,
  `paper/triage_bc_paper.pdf`
- ICLR source and PDF: `paper/iclr2026/main.tex`,
  `paper/iclr2026/main.pdf`
- Markdown draft: `paper/triage_bc_draft.md`

Changes:

- Replaced "current method" / "current evaluation" phrasing in the limitations
  with submission-facing wording for TRIAGE-BC v0.1 and the 50-rollout
  endpoint protocol.
- Replaced the conclusion's internal "publishable version" sentence with a
  direct central claim: support calibration is the bottleneck, and reliable
  hidden-label-free score-to-support conversion is the next algorithmic step.
- Updated the Markdown draft TODOs to acknowledge that the provisional ICLR
  source already exists.

Validation:

```bash
rg -n "A publishable version|Decide target template|transplant `triage_bc_paper\\.tex`|current method|current evidence|current evaluation|Remaining Draft TODOs" paper/iclr2026/main.tex paper/triage_bc_paper.tex paper/triage_bc_draft.md paper/MANUSCRIPT_CHECKLIST.md PAPER_DRAFT_OUTLINE.md tri_piql_paper_completion_plan.md
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
pdftotext -layout -f 9 -l 11 paper/iclr2026/main.pdf -
git diff --check
```

Results:

- The wording scan now finds the old "current evidence" language only in
  `tri_piql_paper_completion_plan.md`; the paper sources no longer contain the
  internal "publishable version" wording.
- Claim-number validator passes.
- Artifact-reference validator checks `64` unique local references.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages; main text ends on page 9, references start on page
  10, and appendix material starts on page 11.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Figure-map consistency guard

Synchronized the manuscript handoff docs with the current compiled figure order
and added a cheap structure validator to prevent future drift.

Updated artifacts:

- Structure validator: `scripts/validate_paper_structure.py`
- Figure map: `PAPER_DRAFT_OUTLINE.md`
- Reproduction checklist: `paper/REPRODUCE_PAPER.md`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Paper README: `paper/README.md`
- Standalone and ICLR PDFs: `paper/triage_bc_paper.pdf`,
  `paper/iclr2026/main.pdf`

Changes:

- Corrected the outline and reproduction map to match the manuscript order:
  Figure 1 method diagram, Figure 2 PointNav mechanism, Figure 3 primary
  robotics matrix, Figure 4 Can precision/coverage, Figure 5 score-shape
  diagnostics.
- Added `scripts/validate_paper_structure.py`, which checks both LaTeX sources
  for the expected figure-label order and checks the Markdown figure-map rows.
- Added the new validator to the paper README, reproduction checklist, and
  manuscript submission checklist.

Validation:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
pdftotext -layout -f 9 -l 11 paper/iclr2026/main.pdf -
git diff --check
```

Results:

- Structure validator passes: `validated paper figure order and figure-map
  rows`.
- Claim-number validator passes.
- Artifact-reference validator checks `65` unique local references.
- Paired-bootstrap report regenerates from staged per-episode metrics.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages; main text ends on page 9, references start on page
  10, and appendix material starts on page 11.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Automated ICLR page-budget guard

Extended the paper structure validator so page-budget and appendix-boundary
checks are automatic rather than only manual `pdfinfo` / `pdftotext` steps.

Updated artifacts:

- Structure validator: `scripts/validate_paper_structure.py`
- Paper README: `paper/README.md`
- Reproduction checklist: `paper/REPRODUCE_PAPER.md`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Standalone and ICLR PDFs: `paper/triage_bc_paper.pdf`,
  `paper/iclr2026/main.pdf`

Changes:

- `scripts/validate_paper_structure.py` now checks:
  - standalone PDF page count is 15;
  - ICLR PDF page count is 13;
  - ICLR page 9 still contains the conclusion and not references;
  - ICLR page 10 contains references;
  - ICLR page 11 starts the appendix.
- Updated documentation for the new validator scope and expected output:
  `validated paper figure order, figure-map rows, and PDF layout`.

Validation:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
git diff --check
```

Results:

- Structure validator passes: `validated paper figure order, figure-map rows,
  and PDF layout`.
- Claim-number validator passes.
- Artifact-reference validator checks `65` unique local references.
- Paired-bootstrap report regenerates from staged per-episode metrics.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages, with the main text ending on page 9, references on
  page 10, and appendix material beginning on page 11.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Manuscript claim-contract validator

Extended the claim-number validator so it also enforces the paper's core
overclaim-avoidance contract across the standalone LaTeX, ICLR LaTeX, and
Markdown manuscript sources.

Updated artifacts:

- Claim-number / claim-contract validator:
  `scripts/validate_paper_claim_numbers.py`
- Paper README: `paper/README.md`
- Reproduction checklist: `paper/REPRODUCE_PAPER.md`
- Manuscript checklist: `paper/MANUSCRIPT_CHECKLIST.md`
- Outline: `PAPER_DRAFT_OUTLINE.md`
- Standalone and ICLR PDFs: `paper/triage_bc_paper.pdf`,
  `paper/iclr2026/main.pdf`

Changes:

- The validator now requires the manuscript sources to retain the key caveats:
  not validated inverse-Q robotics, positive-only NN as a strongest Can
  baseline, weighted BC as strongest on Lift, descriptive rather than formal
  significance wording, repeated-start dependence, score-to-support framing,
  and broad weighted coverage as an essential baseline.
- It fails on unqualified overclaim patterns such as bad labels being necessary,
  hard filtering always winning, TRIAGE-BC uniformly beating baselines, weighted
  BC being weak, best-checkpoint proof language, or validated full inverse-Q
  claims.
- Updated paper docs to describe `scripts/validate_paper_claim_numbers.py` as a
  number-and-claim-contract validator.

Validation:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

Results:

- Claim validator passes: `validated paper claim numbers and claim contract
  against staged CSVs and manuscript text`.
- Structure validator passes: `validated paper figure order, figure-map rows,
  and PDF layout`.
- Artifact-reference validator checks `65` unique local references.
- Paired-bootstrap report regenerates from staged per-episode metrics.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Paired initial-state uncertainty figure

Staged the planned final-evaluation uncertainty visual from existing endpoint
episode metrics, without rerunning any policies.

Updated artifacts:

- `scripts/plot_primary_endpoint_paired_deltas.py`
- `results/final_paper/tables/primary_endpoint_paired_initial_deltas.csv`
- `results/final_paper/tables/primary_endpoint_paired_deltas_REPORT.md`
- `results/final_paper/figures/primary_endpoint_paired_deltas.png`
- `results/final_paper/figures/primary_endpoint_paired_deltas.pdf`
- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/triage_bc_draft.md`
- `PAPER_DRAFT_OUTLINE.md`
- `tri_piql_paper_completion_plan.md`
- `results/final_paper/README.md`

Changes:

- Added a generator for paired initial-state endpoint deltas. Each plotted
  point averages repeated rollouts from the same validation-positive start;
  black intervals reuse the staged bootstrap that resamples split seeds and
  paired initial states.
- Included the paired-delta figure as an appendix uncertainty figure in both
  standalone and ICLR-format LaTeX sources.
- Wired the generator into `make -C paper validate`, paper reproduction docs,
  and the structure/artifact validators.

Validation:

```bash
make -C paper validate
make -C paper all
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

Results:

- `make -C paper validate` passes and regenerates the paired-delta figure.
- `make -C paper all` passes through the same gate.
- Claim validator passes: `validated paper claim numbers and claim contract
  against staged CSVs and manuscript text`.
- Structure validator passes: `validated paper figure order, figure-map rows,
  and PDF layout`.
- Artifact-reference validator checks `69` unique local references.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Makefile validation gate

Added a self-contained paper Makefile gate so the claim/package checks are a
single command instead of a remembered command sequence.

Updated artifacts:

- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/triage_bc_paper.pdf`
- `paper/iclr2026/main.pdf`

Changes:

- `make -C paper validate` now py-compiles the paper validators, regenerates
  the paired-bootstrap audit, rebuilds both PDFs, runs the claim, structure, and
  artifact-reference validators, and fails if the recorded LaTeX warning scans
  find matches.
- `make -C paper all` aliases the same validation gate.
- Paper README, reproduction docs, and manuscript checklist now advertise the
  Makefile gate as the shortest validation path while keeping the expanded
  manual commands visible.

Validation:

```bash
make -C paper validate
make -C paper all
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

Results:

- `make -C paper validate` passes and rebuilds both PDFs.
- `make -C paper all` passes through the same gate.
- Claim validator passes: `validated paper claim numbers and claim contract
  against staged CSVs and manuscript text`.
- Structure validator passes: `validated paper figure order, figure-map rows,
  and PDF layout`.
- Artifact-reference validator checks `65` unique local references.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages.
- Both LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Bad-label control summary table

Staged a generated bad-label control summary from existing final-paper artifacts,
without rerunning policies.

Updated artifacts:

- `scripts/summarize_bad_label_control_table.py`
- `results/final_paper/tables/bad_label_control_summary.csv`
- `results/final_paper/tables/bad_label_control_summary_REPORT.md`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/triage_bc_draft.md`
- `PAPER_DRAFT_OUTLINE.md`
- `tri_piql_paper_completion_plan.md`
- `results/final_paper/README.md`
- `results/PAPER_CLAIM_PACKAGE.md`
- `scripts/validate_paper_structure.py`

Changes:

- Consolidated PointNav, Can 40, Can 20, Can 80, and Lift bad-aware versus
  positive-only evidence into one generated paper-facing table.
- Made the caveat explicit: explicit bad labels are useful calibration signal,
  but the current bad-aware converter is not a broad positive-only winner.
- Wired the generator into the paper Makefile validation path and artifact maps.

Validation:

```bash
python -m py_compile scripts/summarize_bad_label_control_table.py scripts/validate_paper_structure.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
python scripts/summarize_bad_label_control_table.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
make -C paper validate
make -C paper all
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

Results:

- Bad-label generator reproduces the CSV and Markdown report.
- Claim validator passes: `validated paper claim numbers and claim contract
  against staged CSVs and manuscript text`.
- Structure validator passes: `validated paper figure order, figure-map rows,
  and PDF layout`.
- Artifact-reference validator checks `72` unique local references.
- `make -C paper validate` and `make -C paper all` both pass.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 13 pages.
- Strict LaTeX log scans produced no matches under the recorded scan patterns.

## 2026-06-25: Compiled bad-label control appendix table

Promoted the generated bad-label control summary into the compiled standalone
and ICLR appendix drafts.

Updated artifacts:

- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/triage_bc_draft.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/README.md`
- `PAPER_DRAFT_OUTLINE.md`
- `tri_piql_paper_completion_plan.md`
- `scripts/validate_paper_claim_numbers.py`
- `scripts/validate_paper_structure.py`

Changes:

- Added appendix table `tab:bad-label-controls` to both LaTeX drafts.
- Kept the table as control evidence: bad labels improve calibration/support
  purity in some settings, but positive-only retrieval remains stronger on the
  frozen Can diagnostics and frozen Lift endpoint.
- Extended the claim validator to read
  `results/final_paper/tables/bad_label_control_summary.csv` and enforce the
  table's endpoint/support numbers.
- Extended the structure validator to require the new table label and updated
  the ICLR page-count expectation to 14 pages while keeping the main-text
  boundary checks: conclusion on page 9, references on page 10, appendix on
  page 11.

Validation:

```bash
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/validate_paper_artifact_refs.py
python scripts/summarize_bad_label_control_table.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
make -C paper validate
make -C paper all
pdftotext -layout paper/triage_bc_paper.pdf -
pdftotext -layout paper/iclr2026/main.pdf -
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
```

Results:

- `make -C paper validate` and `make -C paper all` both pass.
- Claim validator passes and now guards the bad-label CSV/table contract.
- Structure validator passes with required figure and table labels.
- Artifact-reference validator checks `72` unique local references.
- Rendered PDF text contains the bad-label table rows, including Can 40p/80b
  `110 pos/80 bad vs 106 pos/14 bad` and Lift MG
  `421/20 vs 342/138 hidden pos/bad`.
- Standalone PDF remains 15 pages.
- ICLR PDF is now 14 pages total; main text still ends before references on
  page 10 and appendix starts on page 11.
- Strict LaTeX log scans produced no matches under the recorded scan patterns.

## 2026-06-25: Master evidence tables for high-impact v0.2 gate

Generated standardized endpoint/support evidence tables from current
final-paper per-seed artifacts, and wired them into the paper validation path.

Updated artifacts:

- `scripts/summarize_master_evidence_tables.py`
- `results/final_paper/tables/endpoint_master_table.csv`
- `results/final_paper/tables/support_master_table.csv`
- `results/final_paper/tables/baseline_strength_REPORT.md`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `results/final_paper/README.md`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Changes:

- Normalized `53` support rows and `40` endpoint rows from final-paper
  manifests, support audits, hidden-label audits, and endpoint metrics.
- Report confirms the current v0.1 matrix does not clear the high-impact
  methods bar: Can 40p/80b is led by positive-only NN, and Lift MG is led by
  weighted BC.
- Can 20p/80b and Can 80p/80b are explicitly marked diagnostic/incomplete.
- Reconciled the Can 20p/80b split-22 endpoint extension from
  `eval_endpoint_200/metrics.csv`.
- Added the generator to `make -C paper validate` and to the reproduction
  checklist.

Validation:

```bash
python -m py_compile scripts/summarize_master_evidence_tables.py scripts/validate_paper_structure.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
python scripts/summarize_master_evidence_tables.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
git diff --check
```

Results:

- Master evidence generator reproduces the two CSVs and Markdown report.
- Claim validator passes.
- Structure validator passes.
- Artifact-reference validator checks `74` unique local references.
- `make -C paper validate` passes.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 14 pages.
- Strict LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Hard-negative Can split-101 endpoint smoke and 200-epoch check

Promoted the hard-negative Can action-conflict diagnostic from support-only
evidence to a bounded endpoint check on generated split seed 101. The split
uses 10 labeled positive demos plus 40 selected unlabeled demos, so the endpoint
comparison directly tests whether a bad-aware selector can beat state-action
positive-NN support when the bad demos are nearest-neighbor action conflicts.

Updated artifacts:

- `scripts/prepare_hard_negative_can_endpoint_configs.py`
- `scripts/summarize_hard_negative_can_endpoint_smoke.py`
- `results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/endpoint_setup_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/endpoint_smoke_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/REPORT.md`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/endpoint_setup_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/REPORT.md`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `results/final_paper/README.md`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Endpoint smoke at 50 epochs / 10 valid-positive rollouts:

| support rule | selected hidden pos | selected hidden bad | success |
|---|---:|---:|---:|
| `hybrid_rank_fusion_badaware_heavy_top40` | 36 | 4 | 4/10 |
| `bad_aware_proxy_top40` | 40 | 0 | 1/10 |
| `state_action_positive_nn_top40` | 16 | 24 | 0/10 |

Endpoint check at the frozen 200-epoch / 50-rollout budget:

| support rule | selected hidden pos | selected hidden bad | success |
|---|---:|---:|---:|
| `hybrid_rank_fusion_badaware_heavy_top40` | 36 | 4 | 33/50 |
| `state_action_positive_nn_top40` | 16 | 24 | 30/50 |

Interpretation:

- The hard-negative construction is doing its job: state-action positive-NN
  support admits many action-conflict bad demos on split 101, while the
  bad-aware and hybrid selectors recover much cleaner hidden-positive support.
- The endpoint result is promising but modest: the hybrid beats positive-NN by
  only 3 successes out of 50 on one generated split.
- This should stay framed as a development endpoint check until split seeds
  202 and 303 are run under the same 200-epoch / 50-rollout protocol.
- Pure bad-aware support is too narrow for the endpoint despite perfect support
  purity in the smoke; the useful candidate is the coverage-buffered hybrid.

Validation commands:

```bash
python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 101 --num-epochs 50 --epoch-steps 100 --save-every-epochs 25
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/sapn40/setup/robomimic_bc_rnn_config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/bap40/setup/robomimic_bc_rnn_config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/hrfbh40/setup/robomimic_bc_rnn_config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/hard_negative_can_action_conflict_splits/split101/split_indices.json --out-dir results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/eval_smoke_all --checkpoint-glob "results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/*/train/**/models/model_epoch_50.pth" --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 101 --out-root results/final_paper/ablations/hard_negative_can_endpoint_200ep --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 --candidate state_action_positive_nn_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/sapn40/setup/robomimic_bc_rnn_config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/hrfbh40/setup/robomimic_bc_rnn_config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/hard_negative_can_action_conflict_splits/split101/split_indices.json --out-dir results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/eval_50ep --checkpoint-glob "results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/*/train/**/models/model_epoch_200.pth" --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
```

Results:

- Smoke summary reproduces `4/10`, `1/10`, and `0/10` for hybrid, bad-aware,
  and positive-NN respectively.
- 200-epoch summary reproduces `33/50` for the hybrid and `30/50` for
  positive-NN top40.

## 2026-06-25: Hard-negative Can action-conflict support diagnostic

Built a cheap Experiment Group C1 diagnostic that generates Can splits where
labeled positives are a compact successful cluster, hidden positives are far
from that cluster, and bad demos are ranked by near-positive state distance plus
action conflict. The goal is to test whether bad labels can matter before
spending GPU time on endpoint BC.

Updated artifacts:

- `scripts/summarize_hard_negative_can_action_conflict_audit.py`
- `results/final_paper/ablations/hard_negative_can_action_conflict_construction.csv`
- `results/final_paper/ablations/hard_negative_can_action_conflict_support_per_split.csv`
- `results/final_paper/ablations/hard_negative_can_action_conflict_summary.csv`
- `results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md`
- `results/final_paper/ablations/hard_negative_can_action_conflict_splits/`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `results/final_paper/README.md`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Changes:

- Generated split seeds `101`, `202`, and `303` from the paired low-dimensional
  Can dataset without training policies.
- Construction audit confirms selected unlabeled bad demos are closer in state
  to the labeled-positive cluster than held-out valid bad demos, and have much
  higher hard-negative score (`~0.0` versus about `-1.8`).
- Support gate over three generated splits: state-action positive-NN top40
  reaches `0.583` hidden-positive recall, `0.208` hidden-bad admission, and
  `0.583` purity.
- The bad-aware distance proxy top40 reaches `1.000` hidden-positive recall,
  `0.000` hidden-bad admission, and `1.000` purity.
- Hybrid rank fusion top40 reaches `0.875` hidden-positive recall, `0.062`
  hidden-bad admission, and `0.875` purity.
- Added the generator to `make -C paper validate`, the reproduction map, the
  manuscript checklist, and the structure validator. This is support evidence
  only; endpoint BC is still required before making a rollout claim.

Validation:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py scripts/summarize_master_evidence_tables.py scripts/summarize_candidate_family_audit.py scripts/summarize_hybrid_candidate_support_audit.py scripts/summarize_hard_negative_can_action_conflict_audit.py
python scripts/summarize_hard_negative_can_action_conflict_audit.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
make -C paper validate
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

Results:

- Hard-negative Can generator reproduces the construction CSV, per-split CSV,
  summary CSV, report, and split JSON files in about 3 seconds.
- Structure validator passes.
- Artifact-reference validator checks `80` unique local references.
- `make -C paper validate` passes.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 14 pages.
- Strict Makefile LaTeX log scans produced no matches under the recorded scan
  patterns.
- `git diff --check` is clean.

## 2026-06-25: Candidate-family oracle/proxy audit for v0.2 gate

Generated a candidate-family audit from staged endpoint, support, and Can MG
proxy artifacts to answer whether the current portfolio contains a branch that
can beat the strongest baseline before spending fresh GPU budget.

Updated artifacts:

- `scripts/summarize_candidate_family_audit.py`
- `results/final_paper/tables/candidate_family_audit.csv`
- `results/final_paper/tables/candidate_family_decision_table.csv`
- `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `results/final_paper/README.md`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Changes:

- Audited `24` candidate/support rows across Can 40p/80b, Lift MG, Can
  20p/80b, and Can 80p/80b.
- Added endpoint-oracle, strongest-baseline, bad-aware-only, coverage-proxy,
  and audit-support winner summaries.
- The current endpoint-evaluated portfolio only matches the strongest baseline
  by selecting that baseline: positive-only NN on Can 40p/80b and weighted BC
  on Lift MG.
- No bad-aware hard branch currently beats the strongest positive-only/weighted
  baseline on an endpoint-evaluated robotics setting.
- Can MG proxy stress remains a warning: simple positive/negative likelihood
  proxies miss the rollout-best weighted branch on original Can MG.
- Added the generator to `make -C paper validate` and to the reproduction
  checklist.

Validation:

```bash
python -m py_compile scripts/summarize_candidate_family_audit.py scripts/summarize_master_evidence_tables.py scripts/validate_paper_structure.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
python scripts/summarize_master_evidence_tables.py
python scripts/summarize_candidate_family_audit.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
make -C paper validate
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
git diff --check
```

Results:

- Candidate-family audit generator reproduces the two CSVs and Markdown report.
- Claim validator passes.
- Structure validator passes.
- Artifact-reference validator checks `76` unique local references.
- `make -C paper validate` passes.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 14 pages.
- Strict LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Hybrid candidate support screen before endpoint training

Generated a support-only hybrid candidate audit from staged split files,
classifier score diagnostics, and full positive-NN support rankings. This
checks whether simple positive-NN / classifier hybrids are worth GPU endpoint
training before committing fresh runs.

Updated artifacts:

- `scripts/summarize_hybrid_candidate_support_audit.py`
- `results/final_paper/tables/hybrid_candidate_support_per_split.csv`
- `results/final_paper/tables/hybrid_candidate_support_summary.csv`
- `results/final_paper/tables/hybrid_candidate_support_REPORT.md`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `results/final_paper/README.md`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Changes:

- Audited `94` summary rows and `282` per-split rows across Can 40p/80b, Lift
  MG, Can 20p/80b, and Can 80p/80b.
- Added full positive-only NN top-k support sweeps from HDF5 state-action
  rankings.
- Added hybrid support rules: intersections, classifier-threshold filters,
  threshold-then-refill variants, unions, rank fusion, and Pareto-style top-k.
- Can 40p/80b: positive-only top40 remains the practical frontier point
  (`0.883` recall, `0.058` bad admission). Cleaner hybrids such as
  `hybrid_filter_mid_mean_pos40` improve purity (`0.980`) but lower recall
  (`0.808`), while coverage-restored variants admit more bad demos.
- Lift MG: classifier-heavy hybrids are pure but still hard-support variants;
  the audit supports treating Lift as a soft/coverage branch instead of
  spending endpoint budget on another hard-filter policy.
- Added the generator to `make -C paper validate` and to the reproduction
  checklist.

Validation:

```bash
python -m py_compile scripts/summarize_hybrid_candidate_support_audit.py scripts/summarize_candidate_family_audit.py scripts/summarize_master_evidence_tables.py scripts/validate_paper_structure.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py
python scripts/summarize_master_evidence_tables.py
python scripts/summarize_candidate_family_audit.py
python scripts/summarize_hybrid_candidate_support_audit.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
make -C paper validate
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
git diff --check
```

Results:

- Hybrid support audit generator reproduces the per-split CSV, summary CSV, and
  Markdown report in about 15 seconds.
- Claim validator passes.
- Structure validator passes.
- Artifact-reference validator checks `78` unique local references.
- `make -C paper validate` passes.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 14 pages.
- Strict LaTeX log scans produced no matches under the recorded scan patterns.
- `git diff --check` is clean.

## 2026-06-25: Endpoint-check artifact validation refresh

Refreshed the paper validation gate after adding the hard-negative Can
split-101 endpoint smoke and 200-epoch endpoint-check artifacts.

Validation:

```bash
python -m py_compile scripts/prepare_hard_negative_can_endpoint_configs.py scripts/summarize_hard_negative_can_endpoint_smoke.py scripts/validate_paper_structure.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_claim_numbers.py
make -C paper validate
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

Results:

- Endpoint summary scripts regenerate the smoke and 200-epoch reports.
- Structure validator passes.
- Artifact-reference validator checks `82` unique local references.
- Claim-number validator passes.
- `make -C paper validate` passes and rebuilds both PDFs.

## 2026-06-25: Hard-negative diagnostic manuscript integration

Promoted the generated hard-negative Can three-split endpoint check from a
paper-facing report into the appendix text, while keeping the framing explicit:
the winning row is a bad-aware rank-fusion hybrid candidate on a generated
action-conflict diagnostic, not the frozen TRIAGE-BC v0.1 primary benchmark.

Updated artifacts:

- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/triage_bc_draft.md`
- `scripts/validate_paper_claim_numbers.py`
- `scripts/validate_paper_structure.py`
- `paper/triage_bc_paper.pdf`
- `paper/iclr2026/main.pdf`

Changes:

- Added an appendix table for the hard-negative Can diagnostic:
  bad-aware hybrid top40 selects `113` hidden positives and `7` hidden bad
  demos and reaches `104/150`; state-action positive-NN top40 selects `70`
  hidden positives and `50` hidden bad demos and reaches `91/150`.
- Added matching prose to the standalone LaTeX, ICLR LaTeX, and Markdown draft.
- Extended the claim-number validator to load
  `results/final_paper/ablations/hard_negative_can_endpoint_200ep/endpoint_200ep_3split_summary.csv`
  and verify all per-split hard-negative endpoint/support counts plus the
  aggregate `104/150` versus `91/150` claim.
- Added `tab:hard-negative-can` to the structure validator's required table
  label order.
- Updated the standalone PDF page-count expectation from 15 to 16. The ICLR
  shell remains 14 pages total, with references still beginning on page 10 and
  appendix material on page 11.

Validation:

```bash
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
git diff --check
make -C paper validate
```

Results:

- Claim-number validator passes and now covers the hard-negative diagnostic
  counts.
- Structure validator passes with the new table label and standalone 16-page
  PDF expectation.
- Artifact-reference validator checks `82` unique local references.
- `make -C paper validate` passes.
- Standalone PDF is now 16 pages.
- ICLR PDF remains 14 pages.
- Standalone PDF remains 15 pages.
- ICLR PDF remains 14 pages.
- `git diff --check` is clean.

## 2026-06-25: Hard-negative Can three-split endpoint check

Completed the split-seed 202 and 303 endpoint follow-up for the generated
hard-negative Can action-conflict diagnostic, then aggregated split seeds
101/202/303. This upgrades the previous split-101 development signal into a
three-split targeted diagnostic.

Updated artifacts:

- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/endpoint_setup_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/REPORT.md`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/endpoint_setup_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/REPORT.md`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/endpoint_200ep_3split_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`
- `scripts/summarize_hard_negative_can_endpoint_smoke.py`
- `paper/Makefile`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `results/final_paper/README.md`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Endpoint results at 200 epochs / 50 valid-positive rollouts per split:

| split | hybrid selected pos/bad | positive-NN selected pos/bad | hybrid success | positive-NN success |
|---:|---:|---:|---:|---:|
| 101 | 36/4 | 16/24 | 33/50 | 30/50 |
| 202 | 38/2 | 22/18 | 35/50 | 27/50 |
| 303 | 39/1 | 32/8 | 36/50 | 34/50 |
| aggregate | 113/7 | 70/50 | 104/150 | 91/150 |

Interpretation:

- The generated hard-negative construction now gives the clearest robotics
  endpoint case for bad-aware selection: the hybrid rank-fusion rule beats
  state-action positive-NN by `13/150` successes while admitting far fewer
  hidden bad demos.
- This should be framed as targeted generated-diagnostic evidence, not as a
  primary Robomimic benchmark row, because the split construction was designed
  to expose action-conflict negatives.
- The result is strong enough to justify writing an appendix diagnostic around
  hard-negative support quality and endpoint transfer.

Validation:

```bash
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 202 --out-root results/final_paper/ablations/hard_negative_can_endpoint_200ep --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 --candidate state_action_positive_nn_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 303 --out-root results/final_paper/ablations/hard_negative_can_endpoint_200ep --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 --candidate state_action_positive_nn_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/sapn40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/hrfbh40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/sapn40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/hrfbh40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/hard_negative_can_action_conflict_splits/split202/split_indices.json --out-dir results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/eval_50ep --checkpoint-glob "results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/*/train/**/models/model_epoch_200.pth" --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/hard_negative_can_action_conflict_splits/split303/split_indices.json --out-dir results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/eval_50ep --checkpoint-glob "results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/*/train/**/models/model_epoch_200.pth" --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_claim_numbers.py
make -C paper validate
```

Results:

- Aggregate endpoint report reproduces hybrid `104/150` versus positive-NN
  `91/150`.
- Structure validator passes.
- Artifact-reference validator checks `82` unique local references.
- Claim-number validator passes.
- `make -C paper validate` passes and rebuilds both PDFs.

## 2026-06-25: Final hard-negative manuscript validation status

The appendix now includes the generated hard-negative Can table in both LaTeX
sources and the Markdown draft. The paper-facing claim is validator-backed by
the three-split endpoint CSV, and the build gate passes after updating the
standalone page-count expectation to 16.

Current validated status:

- Hard-negative appendix table reports bad-aware hybrid `104/150` versus
  state-action positive-NN top40 `91/150`.
- Claim-number validator passes and checks the hard-negative per-split and
  aggregate counts.
- Structure validator passes with required table labels
  `tab:main-results`, `tab:bad-label-controls`, and `tab:hard-negative-can`.
- Artifact-reference validator checks `82` unique local references.
- `make -C paper validate` passes.
- Standalone PDF is 16 pages.
- ICLR PDF is 14 pages.
- `git diff --check` is clean.

## 2026-06-25: Can coverage-shift support audit and split-101 endpoint check

Implemented Experiment Group C2 as a generated scarce-positive coverage-shift
Can diagnostic. Labeled positives come from one compact initial-object-pose
cluster, hidden positives come from the other successful clusters, and bad demos
are spread across all pose clusters.

New artifacts:

- `scripts/summarize_can_coverage_shift_audit.py`
- `results/final_paper/ablations/can_coverage_shift_construction.csv`
- `results/final_paper/ablations/can_coverage_shift_support_per_split.csv`
- `results/final_paper/ablations/can_coverage_shift_summary.csv`
- `results/final_paper/ablations/can_coverage_shift_REPORT.md`
- `results/final_paper/ablations/can_coverage_shift_splits/`
- `results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/REPORT.md`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md`

Three-split support audit:

| candidate | hidden-positive selected | hidden-bad selected | hidden-positive recall | hidden-bad admission | purity |
|---|---:|---:|---:|---:|---:|
| state-action positive-NN top40 | 105/120 | 15/240 | 0.875 | 0.062 | 0.875 |
| bad-aware proxy top40 | 120/120 | 0/240 | 1.000 | 0.000 | 1.000 |
| bad-aware-heavy hybrid top40 | 118/120 | 2/240 | 0.983 | 0.008 | 0.983 |

Endpoint results on split 101:

| budget | candidate | selected pos/bad | success |
|---|---|---:|---:|
| 50 epochs, 10 eval starts | state-action positive-NN top40 | 34/6 | 0/10 |
| 50 epochs, 10 eval starts | bad-aware proxy top40 | 40/0 | 2/10 |
| 50 epochs, 10 eval starts | bad-aware-heavy hybrid top40 | 39/1 | 4/10 |
| 200 epochs, 50 eval starts | state-action positive-NN top40 | 34/6 | 35/50 |
| 200 epochs, 50 eval starts | bad-aware-heavy hybrid top40 | 39/1 | 39/50 |

Interpretation:

- This is a second targeted robotics diagnostic, distinct from C1
  action-conflict hard negatives.
- The support signal is very strong and the split-101 endpoint result is
  directionally positive, but the 200-epoch endpoint effect is modest
  (`+4/50`) and currently single-split.
- Do not promote this to a primary paper-table claim yet. The next
  evidence step is split seeds `202` and `303` at the same 200-epoch /
  50-evaluation-start endpoint budget for positive-NN top40 versus the
  bad-aware-heavy hybrid.

Validation:

```bash
python -m compileall -q scripts/summarize_can_coverage_shift_audit.py scripts/prepare_hard_negative_can_endpoint_configs.py scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_can_coverage_shift_audit.py
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-root results/final_paper/ablations/can_coverage_shift_splits --audit-csv results/final_paper/ablations/can_coverage_shift_support_per_split.csv --out-root results/final_paper/ablations/can_coverage_shift_endpoint_smoke --mask-prefix cov_can --experiment-prefix cov_can --report-title 'Can Coverage-Shift Endpoint Setup' --split-seed 101 --num-epochs 50 --epoch-steps 100 --save-every-epochs 25 --candidate state_action_positive_nn_top40 --candidate bad_aware_proxy_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/sapn40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/bap40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/hrfbh40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_coverage_shift_splits/split101/split_indices.json --out-dir results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/eval_smoke_all --checkpoint-glob 'results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/*/train/**/models/model_epoch_50.pth' --eval-episodes 10 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101 --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is directionally consistent with the support audit: the hybrid keeps almost all hidden-positive coverage while removing most hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the frozen-budget multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-root results/final_paper/ablations/can_coverage_shift_splits --audit-csv results/final_paper/ablations/can_coverage_shift_support_per_split.csv --out-root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --mask-prefix cov_can200 --experiment-prefix cov_can200 --report-title 'Can Coverage-Shift Endpoint Setup' --split-seed 101 --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 --candidate state_action_positive_nn_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/sapn40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/hrfbh40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_coverage_shift_splits/split101/split_indices.json --out-dir results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/eval_50ep --checkpoint-glob 'results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/*/train/**/models/model_epoch_200.pth' --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md
git diff --check
```

## 2026-06-25: Can coverage-shift three-split endpoint check

Finished the split seeds `202` and `303` endpoint checks for Experiment Group
C2, using the same official Robomimic BC-RNN-GMM budget as split `101`: 200
epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts
per split.

Aggregate endpoint result:

| candidate | selected hidden pos/bad | support purity | success |
|---|---:|---:|---:|
| bad-aware-heavy hybrid top40 | 118/2 | 0.983 | 120/150 |
| state-action positive-NN top40 | 105/15 | 0.875 | 103/150 |

Per-split endpoint result:

| split | hybrid | positive-NN |
|---:|---:|---:|
| 101 | 39/50 | 35/50 |
| 202 | 41/50 | 29/50 |
| 303 | 40/50 | 39/50 |

Interpretation:

- The three-split endpoint result is directionally consistent with the support
  audit: the hybrid keeps nearly all hidden-positive coverage while reducing
  hidden-bad contamination under initial-pose coverage shift.
- This is useful as targeted generated-diagnostic evidence that explicit bad
  labels can matter beyond the C1 action-conflict construction.
- Keep it separate from the primary Robomimic benchmark table unless the paper
  explicitly frames the row as generated diagnostic evidence.

New/updated artifacts:

- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/REPORT.md`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/REPORT.md`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/endpoint_200ep_3split_summary.csv`

Validation:

```bash
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-root results/final_paper/ablations/can_coverage_shift_splits --audit-csv results/final_paper/ablations/can_coverage_shift_support_per_split.csv --out-root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --mask-prefix cov_can200 --experiment-prefix cov_can200 --report-title 'Can Coverage-Shift Endpoint Setup' --split-seed 202 --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 --candidate state_action_positive_nn_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-root results/final_paper/ablations/can_coverage_shift_splits --audit-csv results/final_paper/ablations/can_coverage_shift_support_per_split.csv --out-root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --mask-prefix cov_can200 --experiment-prefix cov_can200 --report-title 'Can Coverage-Shift Endpoint Setup' --split-seed 303 --num-epochs 200 --epoch-steps 100 --save-every-epochs 50 --candidate state_action_positive_nn_top40 --candidate hybrid_rank_fusion_badaware_heavy_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/sapn40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/hrfbh40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_coverage_shift_splits/split202/split_indices.json --out-dir results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/eval_50ep --checkpoint-glob 'results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/*/train/**/models/model_epoch_200.pth' --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/REPORT.md
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/sapn40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/hrfbh40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_coverage_shift_splits/split303/split_indices.json --out-dir results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/eval_50ep --checkpoint-glob 'results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/*/train/**/models/model_epoch_200.pth' --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows unless the manuscript explicitly frames it as generated diagnostic evidence.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md
```

## 2026-06-25: Promoted coverage-shift diagnostic into the paper gate

Integrated the completed C2 coverage-shift diagnostic into the manuscript and
validation package. The standalone and ICLR LaTeX sources now include
`tab:coverage-shift-can`, and the Markdown draft has the matching prose/table.

Paper-facing claim now checked by validators:

- Bad-aware-heavy hybrid top40: `120/150` endpoint successes, `118` hidden
  positives selected, `2` hidden bad selected.
- State-action positive-NN top40: `103/150` endpoint successes, `105` hidden
  positives selected, `15` hidden bad selected.
- Per-split endpoint pairs: `39/50` vs `35/50`, `41/50` vs `29/50`, and
  `40/50` vs `39/50`.

Updated files:

- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/triage_bc_draft.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/Makefile`
- `scripts/validate_paper_claim_numbers.py`
- `scripts/validate_paper_structure.py`
- `triage_bc_high_impact_completion_plan.md`

Validation:

```bash
python -m py_compile scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
make -C paper validate
git diff --check
```

## 2026-06-25: v0.2 proxy endpoint validation diagnostic

Implemented Experiment D2 as a cheap artifact-only diagnostic over the existing
candidate-family audit. This tests whether the current hidden-label-free
coverage-only proxy predicts endpoint success well enough to justify freezing a
v0.2 branch selector.

New artifacts:

- `scripts/plot_proxy_endpoint_validation.py`
- `results/final_paper/tables/proxy_endpoint_validation.csv`
- `results/final_paper/tables/proxy_endpoint_validation_correlations.csv`
- `results/final_paper/tables/proxy_endpoint_validation_winners.csv`
- `results/final_paper/tables/proxy_endpoint_validation_REPORT.md`
- `results/final_paper/figures/proxy_endpoint_validation.png`
- `results/final_paper/figures/proxy_endpoint_validation.pdf`

Key result:

| setting | endpoint winner | coverage-proxy winner | match |
|---|---|---|---|
| Can 40p/80b | positive-only NN top40 `108/150` | weighted BC full pool `90/150` | false |
| Lift MG | weighted BC `93/150` | weighted BC `93/150` | true |
| Can 20p/80b | positive-only NN top20 `54/100` | weighted BC full pool `18/50` | false |
| Can 80p/80b | positive-only NN top80 `49/50` | positive-only NN top80 `49/50` | true |

Correlation summary:

| analysis set | rows | coverage Pearson | coverage Spearman | audit Pearson | audit Spearman |
|---|---:|---:|---:|---:|---:|
| all endpoint-evaluated support rows | 12 | -0.023 | 0.190 | 0.395 | 0.317 |
| primary complete rows | 7 | 0.472 | 0.600 | 0.131 | 0.306 |
| Can 40p/80b rows | 3 | -0.972 | -1.000 | 0.972 | 1.000 |
| Lift MG rows | 4 | 0.847 | 0.632 | -0.966 | -1.000 |

Interpretation:

- Coverage-only selection explains Lift MG but fails Can-style contamination by
  choosing too-broad weighted support.
- Audit-only precision-risk scores explain Can but fail Lift, where high-purity
  hard support under-covers the policy learner.
- Do not freeze v0.2 around the current coverage-only proxy. The next method
  step should add hidden-label-free bad-risk and action-conflict features before
  spending fresh endpoint GPU budget.

Validation:

```bash
python scripts/plot_proxy_endpoint_validation.py
python -m py_compile scripts/plot_proxy_endpoint_validation.py
git diff --check
```

## 2026-06-25: v0.2 support-side proxy feature screen

Screened simple hidden-label-free proxy features over the existing hybrid
candidate support audit before spending any endpoint GPU budget. The screen
uses selected-support size and mean classifier score as deployable proxy
features, with hidden labels used only for audit.

New artifacts:

- `scripts/summarize_v02_proxy_feature_screen.py`
- `results/final_paper/tables/v02_proxy_feature_screen.csv`
- `results/final_paper/tables/v02_proxy_feature_screen_winners.csv`
- `results/final_paper/tables/v02_proxy_feature_screen_REPORT.md`

Key result:

- Across four settings and seven deployable coverage/classifier-score proxy
  formulas, proxy winners match the audit-support winner in only `1/28`
  setting-proxy cases.
- Proxy winners strictly dominate the positive-NN baseline on hidden support
  metrics in only `2/28` setting-proxy cases.

Best audit-support rows are setting-specific:

| setting | audit-support winner | support audit |
|---|---|---|
| Can 40p/80b | positive-NN top40 | recall `0.883`, bad admission `0.058` |
| Lift MG | classifier top320 | recall `0.859`, bad admission `0.073` |
| Can 20p/80b | hybrid filter mid mean fill classifier to20 | recall `0.833`, bad admission `0.042` |
| Can 80p/80b | hybrid intersection pos80 classifier160 | recall `0.917`, bad admission `0.083` |

Interpretation:

- Coverage-only proxies over-select broad supports.
- Classifier-score-only proxies under-cover.
- Simple coverage/classifier combinations do not recover the audit frontier.
- Do not endpoint-train a new branch from these features. The next useful v0.2
  feature should explicitly estimate action-conflict or bad-neighbor risk.

Validation:

```bash
python scripts/summarize_v02_proxy_feature_screen.py
python -m py_compile scripts/summarize_v02_proxy_feature_screen.py
git diff --check
```

## 2026-06-25: v0.2 action-risk proxy feature screen

Screened explicit hidden-label-free action-conflict and bad-neighbor risk
features over the existing hybrid candidate support audit before spending any
endpoint GPU budget. Per-demo risk scores use only labeled positives, labeled
negatives, and unlabeled support features; hidden labels are used only for audit
columns and winner checks.

New artifacts:

- `scripts/summarize_v02_action_risk_feature_screen.py`
- `results/final_paper/tables/v02_action_risk_feature_screen_per_split.csv`
- `results/final_paper/tables/v02_action_risk_feature_screen.csv`
- `results/final_paper/tables/v02_action_risk_feature_screen_winners.csv`
- `results/final_paper/tables/v02_action_risk_feature_screen_REPORT.md`

Key result:

- Across four settings and eight deployable action-risk proxy formulas, proxy
  winners match the audit-support winner in only `1/32` setting-proxy cases.
- Proxy winners strictly dominate the setting-specific positive-NN baseline on
  hidden support metrics in only `2/32` setting-proxy cases.

Best audit-support rows remain setting-specific:

| setting | audit-support winner | support audit |
|---|---|---|
| Can 40p/80b | positive-NN top40 | recall `0.883`, bad admission `0.058` |
| Lift MG | classifier top320 | recall `0.859`, bad admission `0.073` |
| Can 20p/80b | tied hybrid top20 / fill variants | recall `0.833`, bad admission `0.042` |
| Can 80p/80b | positive-NN top80 / intersection frontier | recall `0.917`, bad admission `0.083` |

Interpretation:

- The action-conflict and bad-neighbor features are useful diagnostics, but they
  do not produce a reliable selector over the current stale candidate family.
- Do not endpoint-train a new v0.2 branch from this candidate family. The next
  useful method step is either a new candidate generator that optimizes these
  risks directly, or an honest abstention/router freeze.

Validation:

```bash
python scripts/summarize_v02_action_risk_feature_screen.py
python -m py_compile scripts/summarize_v02_action_risk_feature_screen.py
git diff --check
```

## 2026-06-25: v0.2 direct action-risk candidates and Can40 endpoint gate

Built candidates directly from hidden-label-free action-conflict and
bad-neighbor risk rankings, then ran a bounded endpoint gate on the strongest
Can 40p/80b split-11 support candidate.

New support artifacts:

- `scripts/summarize_v02_action_risk_candidate_audit.py`
- `results/final_paper/tables/v02_action_risk_candidate_support_per_split.csv`
- `results/final_paper/tables/v02_action_risk_candidate_support_summary.csv`
- `results/final_paper/tables/v02_action_risk_candidate_support_decision.csv`
- `results/final_paper/tables/v02_action_risk_candidate_support_REPORT.md`
- `scripts/summarize_v02_policy_coverage_diagnostic.py`
- `results/final_paper/tables/v02_policy_coverage_diagnostic.csv`
- `results/final_paper/tables/v02_policy_coverage_diagnostic_per_initial.csv`
- `results/final_paper/tables/v02_policy_coverage_diagnostic_REPORT.md`
- `results/final_paper/tables/v02_policy_coverage_diagnostic_split22.csv`
- `results/final_paper/tables/v02_policy_coverage_diagnostic_split22_per_initial.csv`
- `results/final_paper/tables/v02_policy_coverage_diagnostic_split22_REPORT.md`

Support result:

- Direct risk-generated candidates strictly dominate the setting-specific
  positive-NN support baseline in `4/4` audited settings.
- On Can 40p/80b split 11, `bad_neighbor_safe_top40` selects `40/40` hidden
  positives and `0/80` hidden bad demos, versus positive-NN top40 selecting
  `36/40` hidden positives and `4/80` hidden bad demos.
- The less distribution-shifting `positive_nn_risk_fusion_top40` variant
  selects `39/40` hidden positives and `1/80` hidden bad demo.
- On Can 40p/80b split 22, `positive_nn_risk_fusion_top40` has perfect support
  audit, selecting `40/40` hidden positives and `0/80` hidden bad demos, versus
  positive-NN top40 selecting `37/40` hidden positives and `3/80` hidden bad
  demos.

Endpoint artifacts:

- Setup helper patch: `scripts/prepare_hard_negative_can_endpoint_configs.py`
  now accepts `--split-path`, has shorter tags for action-risk candidates, and
  disambiguates repeated audit candidate IDs by matching the audit `source` to
  the exact split path.
- 50-epoch smoke report:
  `results/final_paper/ablations/v02_action_risk_endpoint_smoke_can40/REPORT.md`
- 200-epoch endpoint gate:
  `results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md`

Can 40p/80b split-11 endpoint results:

| candidate / method | protocol | success |
|---|---|---:|
| `bad_neighbor_safe_top40` | 50 epochs, 10 rollouts | `1/10` |
| `positive_nn_risk_fusion_top40` | 50 epochs, 10 rollouts | `2/10` |
| `positive_nn_top40` | 50 epochs, 10 rollouts | `4/10` |
| `bad_neighbor_safe_top40` | 200 epochs, 50 rollouts | `0.720` |
| `positive_nn_risk_fusion_top40` | 200 epochs, 50 rollouts | `0.820` |
| existing positive-NN top40 | 200 epochs, 50 rollouts | `0.840` |
| existing TRIAGE-BC | 20k checkpoint, 50 rollouts | `0.760` |
| existing weighted BC | 20k checkpoint, 50 rollouts | `0.720` |
| split-22 `positive_nn_risk_fusion_top40` | 200 epochs, 50 rollouts | `0.640` |
| split-22 existing positive-NN top40 | 200 epochs, 50 rollouts | `0.760` |
| split-22 existing TRIAGE-BC | 200 epochs, 50 rollouts | `0.520` |
| split-22 existing weighted BC | 200 epochs, 50 rollouts | `0.440` |

Interpretation:

- The direct risk candidate is a strong support-label result but not a stronger
  endpoint policy on the first primary gate.
- The risk-hybrid narrows the endpoint gap and beats TRIAGE-BC on this split,
  but it still trails the strongest same-split positive-NN baseline.
- The split-22 confirmation rejects the current risk-hybrid as a v0.2 method:
  even with perfect hidden support, it trails positive-NN by `0.120`.
- This is important negative evidence: maximizing hidden-label support purity
  can shift the behavior distribution enough to hurt BC-RNN-GMM.
- Initial-state and transition-level policy-coverage diagnostics do not rescue
  the proxy: coverage distances are too similar across positive-NN and
  risk-hybrid candidates to explain endpoint rank reliably.
- Do not promote either action-risk candidate as v0.2, and do not spend
  split-33 endpoint compute on this unchanged candidate family. A next v0.2
  attempt needs a different policy-quality proxy or a candidate generator that
  preserves policy-learning coverage, not only hidden-label purity.

Validation:

```bash
python scripts/summarize_v02_action_risk_candidate_audit.py
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 11 --split-path results/final_paper/splits/can_paired_pos40_bad80_split11/split_indices.json --audit-csv results/final_paper/tables/v02_action_risk_candidate_support_per_split.csv --out-root results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40 --mask-prefix v02risk200_can40 --experiment-prefix v02risk200_can40 --report-title 'v0.2 Action-Risk Can40 200ep Endpoint Setup' --eval-horizon 400 --num-epochs 200 --epoch-steps 100 --save-every-epochs 200 --candidate bad_neighbor_safe_top40 --candidate positive_nn_risk_fusion_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11/bns40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/splits/can_paired_pos40_bad80_split11/split_indices.json --out-dir results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11/bns40/eval --checkpoint results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11/bns40/train/v02risk200_can40_s11_bns40_seed0_bc_rnn_e200/20260625052835/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11/pnrf40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/splits/can_paired_pos40_bad80_split11/split_indices.json --out-dir results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11/pnrf40/eval --checkpoint results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11/pnrf40/train/v02risk200_can40_s11_pnrf40_seed0_bc_rnn_e200/20260625054130/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_v02_policy_coverage_diagnostic.py
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 22 --split-path results/final_paper/splits/can_paired_pos40_bad80_split22/split_indices.json --audit-csv results/final_paper/tables/v02_action_risk_candidate_support_per_split.csv --out-root results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40 --mask-prefix v02risk200_can40 --experiment-prefix v02risk200_can40 --report-title 'v0.2 Action-Risk Can40 200ep Endpoint Setup' --eval-horizon 400 --num-epochs 200 --epoch-steps 100 --save-every-epochs 200 --candidate positive_nn_risk_fusion_top40
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split22/pnrf40/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/splits/can_paired_pos40_bad80_split22/split_indices.json --out-dir results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split22/pnrf40/eval --checkpoint results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split22/pnrf40/train/v02risk200_can40_s22_pnrf40_seed0_bc_rnn_e200/20260625060043/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_v02_policy_coverage_diagnostic.py --split-path results/final_paper/splits/can_paired_pos40_bad80_split22/split_indices.json --risk-endpoint-root results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split22 --out-prefix results/final_paper/tables/v02_policy_coverage_diagnostic_split22
```

## 2026-06-25: Can prefix-positive support and endpoint gate

Built the controlled C3 Robomimic diagnostic where labeled positives are only
early prefixes from successful Can demos, labeled negatives are failed demos,
and the unlabeled pool contains full successful and failed trajectories.

New artifacts:

- `scripts/summarize_can_prefix_positive_audit.py`
- `scripts/summarize_can_prefix_positive_endpoint.py`
- `results/final_paper/ablations/can_prefix_positive_REPORT.md`
- `results/final_paper/ablations/can_prefix_positive_construction.csv`
- `results/final_paper/ablations/can_prefix_positive_support_per_split.csv`
- `results/final_paper/ablations/can_prefix_positive_summary.csv`
- `results/final_paper/ablations/can_prefix_positive_splits/split*/split_indices.json`
- `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/REPORT.md`
- `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/endpoint_200ep_aggregate_summary.csv`
- `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split*/REPORT.md`
- `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split*/endpoint_200ep_summary.csv`

Support gate:

| candidate | selected | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|
| `prefix_bad_aware_state_top80` | 240 | 195 | 45 | 0.812 |
| `prefix_state_action_nn_top80` | 240 | 37 | 203 | 0.154 |

Endpoint gate over split seeds `101`, `202`, and `303`:

| candidate | hidden-positive selected | hidden-bad selected | success |
|---|---:|---:|---:|
| `prefix_bad_aware_state_top80` | 195 | 45 | 119/150 |
| `prefix_state_action_nn_top80` | 37 | 203 | 6/150 |

Per-split endpoint rows:

| split | bad-aware success | prefix-NN success |
|---:|---:|---:|
| 101 | 26/50 | 1/50 |
| 202 | 43/50 | 2/50 |
| 303 | 50/50 | 3/50 |

Interpretation:

- This is the first strong Robomimic transfer of the PointNav
  prefix-positive mechanism.
- The result is much stronger than the failed action-risk v0.2 branch because
  the support advantage translates into endpoint behavior across the full
  three-split 200-epoch / 50-rollout gate.
- This is now strong controlled robotics evidence, but not a primary benchmark
  row because the split construction changes the default Robomimic setting.

Commands:

```bash
python scripts/summarize_can_prefix_positive_audit.py
conda run -n tri-piql python scripts/prepare_hard_negative_can_endpoint_configs.py --split-seed 202 --split-root results/final_paper/ablations/can_prefix_positive_splits --audit-csv results/final_paper/ablations/can_prefix_positive_support_per_split.csv --out-root results/final_paper/ablations/can_prefix_positive_endpoint_200ep --mask-prefix prefix_can200 --experiment-prefix prefix_can --report-title 'Can Prefix-Positive Endpoint Setup' --num-epochs 200 --epoch-steps 100 --save-every-epochs 100 --candidate prefix_state_action_nn_top80 --candidate prefix_bad_aware_state_top80
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split202/prefix_bad_aware_state_top80/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split202/prefix_state_action_nn_top80/setup/config.json
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_prefix_positive_splits/split202/split_indices.json --out-dir results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split202/prefix_bad_aware_state_top80/eval_50ep --checkpoint results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split202/prefix_bad_aware_state_top80/train/prefix_can_s202_prefix_bad_aware_state_top80_seed0_bc_rnn_e200/20260625061722/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql python scripts/evaluate_robomimic_official_policy.py --split-path results/final_paper/ablations/can_prefix_positive_splits/split202/split_indices.json --out-dir results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split202/prefix_state_action_nn_top80/eval_50ep --checkpoint results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split202/prefix_state_action_nn_top80/train/prefix_can_s202_prefix_state_action_nn_top80_seed0_bc_rnn_e200/20260625062142/models/model_epoch_200.pth --eval-episodes 50 --eval-horizon 400 --eval-init-mode valid_positive_states --device cuda --seed 0
python scripts/summarize_can_prefix_positive_endpoint.py
```

Continuation:

- Repeated the same prepare/train/evaluate protocol for split seeds `101` and
  `303`.
- Exact checkpoint paths and per-split metrics are captured in
  `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/split*/REPORT.md`.
- Regenerated the aggregate with `python scripts/summarize_can_prefix_positive_endpoint.py`.

Validation:

```bash
python -m py_compile scripts/summarize_can_prefix_positive_audit.py scripts/summarize_can_prefix_positive_endpoint.py scripts/prepare_hard_negative_can_endpoint_configs.py
git diff --check
pgrep -af 'run_final_matrix|robomimic.scripts.train|train_robomimic_official_weighted_sampler|evaluate_robomimic_official_policy'
```

## 2026-06-25: Paper-facing prefix-positive diagnostic integration

Converted the completed Can prefix-positive endpoint gate into a paper-facing
diagnostic artifact and wired it into the manuscript/checklist/repro path
without promoting it to a primary benchmark row.

New / refreshed artifacts:

- `scripts/plot_can_prefix_positive_diagnostic.py`
- `results/final_paper/tables/can_prefix_positive_diagnostic.csv`
- `results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`
- `results/final_paper/figures/can_prefix_positive_diagnostic.png`
- `results/final_paper/figures/can_prefix_positive_diagnostic.pdf`
- refreshed `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/REPORT.md`

Manuscript integration:

- Added the prefix-positive Can result as an appendix diagnostic in
  `paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
  `paper/triage_bc_draft.md`.
- Kept the claim scoped as generated diagnostic evidence: prefix bad-aware
  state top80 reaches `119/150` and selects `195` hidden positives with `45`
  hidden bad demos, while prefix state-action positive-NN top80 reaches
  `6/150` and selects `37` hidden positives with `203` hidden bad demos.
- Added the artifact to `paper/MANUSCRIPT_CHECKLIST.md`,
  `paper/REPRODUCE_PAPER.md`, `paper/README.md`,
  `results/final_paper/README.md`, and the paper validators.

Validation:

```bash
python scripts/summarize_can_prefix_positive_endpoint.py
python scripts/plot_can_prefix_positive_diagnostic.py
python -m py_compile scripts/plot_can_prefix_positive_diagnostic.py scripts/summarize_can_prefix_positive_endpoint.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/validate_paper_artifact_refs.py
latexmk -pdf -interaction=nonstopmode -halt-on-error triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error iclr2026/main.tex
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
git diff --check
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
```

All validators passed. The rebuilt standalone PDF remains 16 pages and the
ICLR-format PDF remains 14 pages; references still begin on page 10 and the
appendix starts on page 11 under `scripts/validate_paper_structure.py`.

## 2026-06-25: Prefix-positive appendix figure visibility gate

Made the C3 prefix-positive result visible in the compiled appendix rather than
only listing it in artifact maps.

Changes:

- Added `fig:prefix-positive-can` to `paper/triage_bc_paper.tex` and
  `paper/iclr2026/main.tex`.
- Included `results/final_paper/figures/can_prefix_positive_diagnostic.pdf`
  as an appendix figure after the paired endpoint-delta figure.
- Updated `scripts/validate_paper_structure.py` to require the new figure label
  and to expect the intentional appendix page-count change.
- Updated current-status page-count docs in `paper/MANUSCRIPT_CHECKLIST.md`,
  `paper/README.md`, `PAPER_DRAFT_OUTLINE.md`, and
  `tri_piql_paper_completion_plan.md`.

Validation:

```bash
make -C paper validate
```

Result:

- Full paper validation passed.
- Standalone PDF is now 17 pages.
- ICLR-format PDF is now 15 pages.
- The main-text boundary is unchanged: conclusion on page 9, references on page
  10, and appendix starts on page 11.

## 2026-06-25: Cautious diagnostic-paper framing adoption

Aligned the manuscript front matter with the evidence level in the high-impact
plan. The paper now uses the cautious diagnostic title:

`When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study`

Changes:

- Updated the title, abstract, and contribution list in
  `paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
  `paper/triage_bc_draft.md`.
- Updated the working-title surfaces in `PAPER_DRAFT_OUTLINE.md` and
  `tri_piql_paper_completion_plan.md`.
- Added a status note in `triage_bc_high_impact_completion_plan.md`.

Rationale:

- The current evidence is strong for a precision/coverage phenomenon paper, not
  a universal method-dominance paper.
- The new abstract explicitly includes the controlled PointNav and generated
  Robomimic Can diagnostics as positive mechanisms.
- It also preserves the primary Robomimic caveats: positive-only retrieval is
  stronger on Can 40p/80b and weighted BC is strongest on Lift MG.

Validation:

```bash
make -C paper validate
```

The full paper gate passed after the rewrite. The compiled page layout remains
17 pages for the standalone PDF and 15 pages for the ICLR-format PDF, with
conclusion on page 9, references on page 10, and appendix starting on page 11.

## 2026-06-25: Paper validation documentation synchronization

Synchronized the paper-facing validation docs with the current post-prefix-
positive artifact package.

Updated documentation:

- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/README.md`
- `paper/REPRODUCE_PAPER.md`

Main fixes:

- Updated the expected artifact-reference validator count to `90` unique
  references.
- Added the prefix-positive endpoint and diagnostic plotting scripts to the
  submission-check compile commands.
- Made the LaTeX log-scan contract precise: the standalone draft still has no
  warning, underfull, or overfull matches, while the ICLR shell uses the
  Makefile pattern that tolerates underfull layout messages but fails on
  undefined-reference, warning, natbib-warning, or overfull matches.
- Documented the current PDF sizes as 17 standalone pages and 15 ICLR-format
  pages.
- Expanded the reproduction guide's cheap/manual commands to include the
  coverage-shift endpoint summaries and prefix-positive diagnostic artifacts.

Validation:

```bash
make -C paper validate
git diff --check
```

Results:

- `make -C paper validate` passed.
- Claim-number, structure, and artifact-reference validators passed; the
  artifact validator reports `checked 90 unique artifact references`.
- The standalone PDF rebuilt at 17 pages.
- The ICLR-format PDF rebuilt at 15 pages, with references on page 10 and
  appendix material starting on page 11.
- `git diff --check` passed.
- The stale-count and stale-warning-text search over the three paper docs
  returned no matches.

## 2026-06-25: Claim package synchronized with diagnostic framing

Updated `results/PAPER_CLAIM_PACKAGE.md` so the paper-facing claim package now
matches the cautious diagnostic title and the newest generated Can diagnostics.

Changes:

- Updated the evidence-package date to 2026-06-25.
- Replaced the old TRIAGE-BC method-title surface with
  `When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study`.
- Added the hard-negative, coverage-shift, and prefix-positive Can diagnostics
  as generated mechanism evidence, not primary benchmark rows.
- Added a supported-diagnostic claim row for generated Can settings where
  explicit bad labels beat matched positive-only retrieval:
  hard-negative `104/150` versus `91/150`, coverage-shift `120/150` versus
  `103/150`, and prefix-positive `119/150` versus `6/150`.
- Added the relevant generated-diagnostic reports to the artifact narrative.

Validation:

```bash
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_claim_numbers.py
git diff --check
```

Results:

- Artifact-reference validator passed with `checked 90 unique artifact
  references`.
- Claim-number validator passed.
- `git diff --check` passed.

## 2026-06-25: Precision/coverage marginal-support proposition

Strengthened the diagnostic/theory path after re-checking the v0.2 candidate
reports. The current candidate-family audit still shows that the endpoint
oracle can only match the strongest baseline by selecting that baseline, and
the existing coverage proxy does not justify more endpoint GPU budget for the
current candidate family. I therefore improved the paper's precision/coverage
analysis rather than launching another long run.

Changes:

- Added a compact marginal support criterion to
  `paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
  `paper/triage_bc_draft.md`.
- The criterion states when adding one more unlabeled trajectory should reduce
  the schematic hard-support risk bound: expected coverage gain must exceed
  the normalized increase in bad-action mass.
- The wording keeps the scope as an organizing decomposition for nonlinear
  sequence BC, not a formal performance guarantee.

Validation:

```bash
make -C paper validate
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
git diff --check
```

Results:

- Full paper validation passed.
- Standalone PDF remains 17 pages.
- ICLR-format PDF remains 15 pages.
- Claim-number and structure validators passed.
- `git diff --check` passed.

## 2026-06-25: Action-risk v0.2 no-go made paper-visible

Made the failed action-risk v0.2 endpoint gate visible in the manuscript
appendix and claim validator. This addresses a reviewer-facing risk: support
audits alone can look like a promising method result, but the endpoint gate
shows that improved hidden-label support purity did not beat the strongest
positive-only endpoint baseline.

Changes:

- Added an appendix diagnostic bullet to `paper/triage_bc_paper.tex` and
  `paper/iclr2026/main.tex`.
- Added the matching row to `paper/triage_bc_draft.md`.
- Added artifact-map/checklist references in `paper/REPRODUCE_PAPER.md` and
  `paper/MANUSCRIPT_CHECKLIST.md`.
- Extended `scripts/validate_paper_claim_numbers.py` to check the split-11 and
  split-22 action-risk endpoint/support counts from staged CSVs.

Key checked numbers:

- Split 11: positive-NN/risk fusion selects 39 hidden positives and 1 hidden
  bad demo, but reaches `0.820` versus positive-only NN `0.840`.
- Split 22: positive-NN/risk fusion selects 40 hidden positives and 0 hidden
  bad demos, but reaches `0.640` versus positive-only NN `0.760`.
- Current artifact-reference validator count is now `93` unique references.

Validation:

```bash
make -C paper validate
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
git diff --check
```

Results:

- Full paper validation passed.
- Claim-number, structure, and artifact-reference validators passed.
- Standalone PDF is now 18 pages.
- ICLR-format PDF remains 15 pages, with the main-text boundary unchanged.
- `git diff --check` passed.

## 2026-06-25: Claim package readiness snapshot added

Made the v0.2 no-go state explicit in the claim package and high-impact plan.
The action-risk endpoint gate is now represented as a supported no-go claim:
support purity can improve without beating the endpoint baseline.

Changes:

- Added a main claim-package row for the action-risk v0.2 endpoint no-go.
- Added v0.2 development artifact pointers to `results/PAPER_CLAIM_PACKAGE.md`.
- Added a submission-readiness snapshot separating green diagnostic evidence
  from red methods-paper gates.
- Added a current go/no-go status table to
  `triage_bc_high_impact_completion_plan.md`.
- Updated `tri_piql_paper_completion_plan.md` so its executive diagnosis and
  bottom-line next steps reflect the action-risk v0.2 no-go.

Validation:

```bash
make -C paper validate
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
git diff --check
```

Results:

- Full paper validation passed.
- Claim-number and artifact-reference validators passed.
- Artifact-reference count remains `93` unique references.
- Standalone PDF remains 18 pages.
- ICLR-format PDF remains 15 pages.
- `git diff --check` passed.

## 2026-06-25: Can 40 v0.2 union candidate endpoint gate

Tested a less aggressive follow-up to the failed action-risk replacement
candidate. Instead of replacing positive-only support with risk-ranked support,
the new candidate keeps positive-only NN top40 and unions in demos selected by
positive-NN/risk-fusion top40.

Artifacts:

- `scripts/summarize_v02_union_candidate_audit.py`
- `scripts/summarize_v02_union_endpoint.py`
- `scripts/summarize_v02_union_endpoint_aggregate.py`
- `results/final_paper/tables/v02_union_candidate_support_REPORT.md`
- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/REPORT.md`

Support audit:

- Across Can 40p/80b split seeds `11`, `22`, and `33`, the union selects
  `119/120` hidden-positive demos and `16/240` hidden-bad demos.
- Per split: split 11 selects `40/40` hidden positives and `5/80` hidden bad;
  split 22 selects `40/40` and `3/80`; split 33 selects `39/40` and `8/80`.

Endpoint gate:

- Official Robomimic BC-RNN-GMM, 200 epochs, 50 valid-positive-start rollouts
  per split.
- Union reaches `116/150` pooled success (`0.773`): split 11 `0.760`, split 22
  `0.780`, split 33 `0.780`.
- Existing frozen rows on the same Can 40p/80b matrix: positive-only NN
  `108/150`, TRIAGE-BC v0.1 `99/150`, weighted BC `90/150`, and all-demo BC
  `81/150`.

Interpretation:

- This is the first Can 40p/80b development candidate that beats the strong
  positive-only NN row in the pooled frozen endpoint matrix.
- It should not be promoted as TRIAGE-BC v0.2 yet: it loses split 11 to
  positive-only NN (`0.760` versus `0.840`), has not been frozen on fresh
  splits, and does not address Lift MG or Can MG.

## 2026-06-25: v0.2 candidate-family refresh and portfolio-router audit

Folded the Can 40 union branch into the main v0.2 candidate-family and proxy
reports, then built a cheap hidden-label-free portfolio-router audit over
existing endpoint artifacts.

Updated / added scripts:

- `scripts/summarize_candidate_family_audit.py`
- `scripts/plot_proxy_endpoint_validation.py`
- `scripts/summarize_v02_portfolio_router_audit.py`

Generated artifacts:

- `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`
- `results/final_paper/tables/proxy_endpoint_validation_REPORT.md`
- `results/final_paper/figures/proxy_endpoint_validation.{png,pdf}`
- `results/final_paper/tables/v02_portfolio_router_REPORT.md`
- `results/final_paper/tables/v02_portfolio_router_decisions.csv`
- `results/final_paper/tables/v02_portfolio_router_summary.csv`

Candidate-family result:

- Can 40p/80b now contains an endpoint-evaluated bad-aware branch above the
  strongest baseline: union `116/150` versus positive-only NN `108/150`.
- Lift MG still only matches the strongest baseline by selecting weighted BC:
  weighted `93/150` versus TRIAGE-BC v0.1 `74/150`.
- Coverage-only proxy remains insufficient: it still selects weighted BC on
  Can 40, where weighted reaches only `90/150`.

Portfolio-router rule audited:

- Abstain if estimated positive mass is at least `800` and the count above the
  labeled-positive minimum is at least `400`.
- Otherwise choose soft weighted BC if estimated positive mass is at least
  `200` and count above the labeled-positive minimum is at least `80`.
- Otherwise choose hard positive-NN/risk union support.

Development endpoint result:

- Can 40p/80b: router chooses union, `116/150`.
- Lift MG: router chooses weighted BC, `93/150`.
- Pooled primary development result: `209/300`, versus strongest pre-union
  per-task baselines `201/300`, v0.1 `173/300`, and all-positive oracle
  `252/300`.

Interpretation:

- This is the first plausible cross-task v0.2 shape: hard union for Can-like
  low-mass contamination, weighted support for Lift-like coverage, and
  abstention on Can MG-style large ambiguous pools.
- It is still post-hoc development evidence. The rule was written after the
  Can union endpoint gate, Lift is solved by selecting a baseline branch, Can
  20/80 union rows are support-only, and fresh split validation is required
  before this can become a paper method.

### v0.2 development freeze draft

Drafted the fresh-split validation contract for the portfolio router:

- `METHOD_FREEZE_V02.md`
- `configs/final_method_v02.yaml`
- `configs/final_eval_v02.yaml`

The freeze is explicit that this is not a final paper method yet. It
predeclares split seeds `101`, `202`, and `303` for Can 40p/80b and Lift MG,
policy seed `0`, official Robomimic BC-RNN-GMM at 200 epochs, 50 endpoint
rollouts, and the mass/count router rule:

- high ambiguous mass/count: abstain,
- moderate mass/count: soft weighted BC,
- otherwise: hard positive-NN/risk union support.

The YAML configs parse successfully with `yaml.safe_load`.

## 2026-06-25: First fresh v0.2 Can 40 endpoint split

Ran the first predeclared fresh-split endpoint gate for the frozen v0.2
portfolio router on Can 40p/80b split seed `101`.

New / updated scripts:

- `scripts/summarize_v02_fresh_router_support_audit.py`
- `scripts/summarize_v02_fresh_can_endpoint.py`
- `scripts/train_robomimic_official_weighted_sampler.py`

Generated artifacts:

- `results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
- `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split101/positive_nn_risk_union_top40/eval_50ep/REPORT.md`
- `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_positive_only_nn_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_weighted_bc_policy0/eval/REPORT.md`

Support/router preflight:

- Can 40p/80b split `101`: frozen router chooses hard
  `positive_nn_risk_union_top40`.
- Union support selects `49` unlabeled demos: `40/40` hidden positives and
  `9/80` hidden bad demos.
- Positive-only NN top40 selects `31/40` hidden positives and `9/80` hidden bad
  demos.
- Risk-fusion top40 alone is support-clean on this split (`40/40` positives and
  `0/80` bad), but the frozen method remains the predeclared union branch.

Endpoint results, official Robomimic BC-RNN-GMM, 200 epochs, 50 valid-positive
starts:

- v0.2 selected union: `45/50` success (`0.900`).
- Positive-only NN baseline: `19/50` success (`0.380`).
- Weighted BC baseline: `37/50` success (`0.740`).

Interpretation:

- This is a clean first fresh Can split for the frozen v0.2 router: the selected
  union row beats both completed strong same-backbone baselines by `+8/50`
  versus weighted BC and `+26/50` versus positive-only NN.
- It is still only one fresh Can split. The v0.2 claim remains unresolved until
  Can split seeds `202` and `303` and the Lift selected weighted rows are run
  under the same frozen protocol.
- During this run, an accidental plain Robomimic train was started for weighted
  BC and stopped before any epoch checkpoint. The completed weighted baseline
  used `scripts/train_robomimic_official_weighted_sampler.py` with explicit demo
  weights. The trainer now supports `--experiment-name` and absolute
  `--output-dir` overrides to avoid future output collisions.

## 2026-06-25: Second fresh v0.2 Can 40 endpoint split

Ran the second predeclared fresh Can 40p/80b v0.2 gate on split seed `202`.

Updated artifacts:

- `results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
- `results/final_paper_v02/README.md`
- `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split202/positive_nn_risk_union_top40/eval_50ep/REPORT.md`
- `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_positive_only_nn_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_weighted_bc_policy0/eval/REPORT.md`

Support/router preflight:

- Can 40p/80b split `202`: frozen router again chooses hard
  `positive_nn_risk_union_top40`.
- Union support selects `44` unlabeled demos: `39/40` hidden positives and
  `5/80` hidden bad demos.
- Positive-only NN top40 selects `35/40` hidden positives and `5/80` hidden bad
  demos.
- Risk-fusion top40 selects `38/40` hidden positives and `2/80` hidden bad
  demos.

Endpoint results, official Robomimic BC-RNN-GMM, 200 epochs, 50 valid-positive
starts:

- v0.2 selected union: `45/50` success (`0.900`).
- Positive-only NN baseline: `40/50` success (`0.800`).
- Weighted BC baseline: `33/50` success (`0.660`).

Current completed fresh Can summary:

- Split `101`: union `45/50`, weighted BC `37/50`, positive-only NN `19/50`.
- Split `202`: union `45/50`, positive-only NN `40/50`, weighted BC `33/50`.
- Pooled completed fresh Can rows: v0.2 union `90/100` versus best completed
  per-split non-oracle baselines `77/100`.

Interpretation:

- The first fresh Can result replicated: the frozen v0.2 union branch is best
  non-oracle on both completed fresh Can splits.
- This is now meaningful Can evidence, but still not a full v0.2 methods gate:
  Can seed `303` and the fresh Lift selected weighted rows remain required.

## 2026-06-25: Third fresh v0.2 Can 40 endpoint split and completed Can gate

Completed the third predeclared fresh Can 40p/80b v0.2 gate on split seed
`303`, including the selected union branch and the two strongest same-backbone
baselines.

Updated artifacts:

- `results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_can_endpoint_REPORT.md`
- `results/final_paper_v02/README.md`
- `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split303/positive_nn_risk_union_top40/eval_50ep/REPORT.md`
- `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_positive_only_nn_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_weighted_bc_policy0/eval/REPORT.md`

Support/router preflight:

- Can 40p/80b split `303`: frozen router again chooses hard
  `positive_nn_risk_union_top40`.
- Union support selects `45` unlabeled demos: `40/40` hidden positives and
  `5/80` hidden bad demos.
- Across the three fresh Can splits, union support selects `119/120` hidden
  positives and `19/240` hidden bad demos.

Endpoint results, official Robomimic BC-RNN-GMM, 200 epochs, 50 valid-positive
starts:

- v0.2 selected union: `39/50` success (`0.780`).
- Positive-only NN baseline: `36/50` success (`0.720`).
- Weighted BC baseline: `25/50` success (`0.500`).

Completed fresh Can 40p/80b gate:

- Split `101`: union `45/50`, weighted BC `37/50`, positive-only NN `19/50`.
- Split `202`: union `45/50`, positive-only NN `40/50`, weighted BC `33/50`.
- Split `303`: union `39/50`, positive-only NN `36/50`, weighted BC `25/50`.
- Pooled selected v0.2 union: `129/150`.
- Best completed non-oracle baseline per split: `113/150`.

Interpretation:

- The frozen v0.2 hard-union branch is best non-oracle on all three fresh Can
  splits, with margins `+8/50`, `+5/50`, and `+3/50`.
- This clears the Can branch of the v0.2 fresh gate. It still does not by
  itself clear the high-impact methods-paper gate because the fresh Lift
  selected weighted rows remain required.

## 2026-06-25: Fresh v0.2 Lift MG endpoint gate

Completed the predeclared fresh Lift MG v0.2 gate on split seeds `101`, `202`,
and `303`, using the frozen router branch and the strongest completed
same-backbone baseline.

Updated artifacts:

- `results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_lift_endpoint_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- `results/final_paper_v02/README.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split101_weighted_bc_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split101_positive_only_nn_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split202_weighted_bc_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split202_positive_only_nn_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_weighted_bc_policy0/eval/REPORT.md`
- `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_positive_only_nn_policy0/eval/REPORT.md`

Support/router preflight:

- Lift MG split `101`: frozen router chooses soft `weighted_bc`.
- Lift MG split `202`: frozen router chooses soft `weighted_bc`.
- Lift MG split `303`: frozen router chooses soft `weighted_bc`.
- Across the three fresh Lift splits, weighted support includes all `828/828`
  hidden-positive unlabeled demos and all `3432/3432` hidden-bad unlabeled
  demos. This is expected for the soft branch and should be interpreted as
  coverage, not purity.

Endpoint results, official Robomimic BC-RNN-GMM, 200 epochs, 50 valid-positive
starts:

- Split `101`: selected weighted BC `31/50`, positive-only NN top160 `28/50`.
- Split `202`: selected weighted BC `30/50`, positive-only NN top160 `25/50`.
- Split `303`: selected weighted BC `19/50`, positive-only NN top160 `21/50`.

Completed fresh Lift MG gate:

- Pooled selected v0.2 weighted branch: `80/150`.
- Best completed non-oracle baseline per split: `74/150`.
- Per-split margins are `+3/50`, `+5/50`, and `-2/50`.
- Combined with the completed fresh Can 40p/80b gate, v0.2 selected branches
  reach `209/300` versus `187/300` for the best completed non-oracle baseline
  per split.

Interpretation:

- The frozen v0.2 router correctly moves away from hard support on Lift-like
  broad-coverage rows, and the selected weighted branch is modestly better in
  aggregate than positive-only NN top160.
- This is not a decisive algorithmic win. The Lift branch is essentially
  router-selected weighted BC, and split `303` favors positive-only NN. The
  paper should present this as precision/coverage branch-selection evidence,
  with Can carrying the cleaner hard-union improvement.

## 2026-06-25: v0.2 fresh gate integrated into manuscript

Promoted the completed frozen v0.2 fresh Can+Lift gate into the standalone,
ICLR-format, and Markdown manuscript drafts with cautious framing.

Updated artifacts:

- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/triage_bc_draft.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/REPRODUCE_PAPER.md`
- `paper/README.md`
- `scripts/validate_paper_claim_numbers.py`
- `scripts/validate_paper_structure.py`
- `paper/triage_bc_paper.pdf`
- `paper/iclr2026/main.pdf`

Main manuscript changes:

- Added a frozen v0.2 portfolio-router method subsection and a main-result
  table for the fresh endpoint gate.
- Added the fresh gate numbers: Can `129/150` versus `113/150`, Lift `80/150`
  versus `74/150`, and combined selected branches `209/300` versus `187/300`.
- Kept the language conservative: Can is the cleaner hard-union improvement;
  Lift is a modest branch-selection result where the selected branch is
  weighted BC and split `303` loses to positive-only NN.
- Restored explicit guardrail wording that positive-only NN is strongest on the
  original Can caveat rows and weighted BC is strongest on the original Lift
  matrix.

Validation:

```bash
make -C paper validate
```

The full paper gate passed. It regenerated the staged reports and figures,
rebuilt both PDFs, validated claim numbers, validated structure and page
boundaries, checked 103 unique artifact references, and ran the configured
LaTeX log scans. The standalone PDF is now 17 pages. The ICLR-format PDF is 15
pages, with conclusion on page 9, references on page 10, and appendix material
starting on page 11.

## 2026-06-25: v0.2 fresh gate paired-start uncertainty audit

Added a cheap uncertainty audit for the completed frozen v0.2 fresh Can+Lift
gate using existing endpoint `episode_metrics.csv` files. The audit groups
repeated rollouts by `initial_demo_id`, compares the router-selected branch
against the best completed non-oracle baseline within each split, and bootstraps
split units plus paired validation initial states.

Generated artifacts:

- `scripts/summarize_v02_fresh_gate_uncertainty.py`
- `results/final_paper_v02/tables/v02_fresh_gate_uncertainty.csv`
- `results/final_paper_v02/tables/v02_fresh_gate_paired_initial_deltas.csv`
- `results/final_paper_v02/tables/v02_fresh_gate_uncertainty_per_split.csv`
- `results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`

Main audit read:

- Can 40p/80b: selected hard union `129/150` versus best baselines `113/150`;
  pooled delta `+0.107`; paired-bootstrap interval `[-0.033, 0.260]`; split
  signs `+++`.
- Lift MG: selected weighted branch `80/150` versus best baselines `74/150`;
  pooled delta `+0.040`; paired-bootstrap interval `[-0.083, 0.178]`; split
  signs `++-`.
- Combined Can+Lift: selected branches `209/300` versus best baselines
  `187/300`; pooled delta `+0.073`; paired-bootstrap interval
  `[-0.022, 0.179]`; split signs `+++++-`.

Interpretation:

- The intervals all cross zero, so the v0.2 gate remains directional,
  branch-selection evidence rather than a formal significance claim.
- Can remains the clean hard-union improvement. Lift remains a modest
  branch-selection result where the selected branch is weighted BC and one split
  still favors positive-only NN.
- Manuscript wording, the checklist, reproduction docs, and claim validators now
  include this caution explicitly.

Validation:

```bash
make -C paper validate
```

The full paper gate passed after regenerating all paper-facing reports and
figures, rebuilding the standalone and ICLR PDFs, validating claim numbers,
validating structure and page boundaries, checking 105 unique artifact
references, and running the configured LaTeX log scans. The standalone PDF is
17 pages. The ICLR-format PDF is 15 pages, with conclusion on page 9,
references on page 10, and appendix material starting on page 11.

## 2026-06-25: A1 five-split v0.2 extension preflight

Started Priority A1 from `triage_bc_top_tier_completion_plan.md`: expand the
frozen v0.2 fresh Can+Lift gate from three split seeds to five split seeds before
making stronger top-tier claims.

Prepared new split/score artifacts for split seeds `404` and `505`:

- Can 40p/80b: `results/final_paper_v02/splits/can_paired_pos40_bad80_split404/`
  and `results/final_paper_v02/splits/can_paired_pos40_bad80_split505/`.
- Lift MG: `results/final_paper_v02/splits/lift_mg_mg_sparse_split404/` and
  `results/final_paper_v02/splits/lift_mg_mg_sparse_split505/`.
- Score diagnostics under `results/final_paper_v02/score_diagnostics/*404*`
  and `results/final_paper_v02/score_diagnostics/*505*`.

Generated a five-split support/router preflight in:

- `results/final_paper_v02/tables/a1_preflight_5split/v02_fresh_router_support_REPORT.md`
- `results/final_paper_v02/A1_FIVE_SPLIT_EXTENSION_PREFLIGHT.md`

Preflight read:

- Can split `404`: frozen v0.2 chooses `hard_risk_union`; union selects `39/40`
  hidden positives and `5/80` hidden bad demos.
- Can split `505`: frozen v0.2 chooses `hard_risk_union`; union selects `40/40`
  hidden positives and `4/80` hidden bad demos.
- Lift split `404`: frozen v0.2 chooses `soft_weighted`.
- Lift split `505`: frozen v0.2 chooses `soft_weighted`.
- Across five Can splits, hard union selects `198/200` hidden positives and
  `28/400` hidden bad demos. This is support-side preflight evidence only, not
  endpoint evidence.

Prepared endpoint configs for the added A1 queue:

- Can `404`/`505`: v0.2 hard union, positive-only NN top40, weighted BC.
- Lift `404`/`505`: weighted BC and positive-only NN top160.

Next step:

- Run the GPU endpoint queue documented in
  `results/final_paper_v02/A1_FIVE_SPLIT_EXTENSION_PREFLIGHT.md`.
- Keep all five-split summaries in a separate draft output directory until
  every required added endpoint row is complete.

## 2026-06-25: A1 Can split 404 selected-branch endpoint

Ran the first bounded endpoint job from the A1 five-split expansion: Can
40p/80b split `404`, frozen v0.2 selected hard-union branch
`positive_nn_risk_union_top40`.

Training/evaluation:

- Train config:
  `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split404/positive_nn_risk_union_top40/setup/config.json`
- Epoch-200 checkpoint:
  `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split404/positive_nn_risk_union_top40/train/v02fresh_can40_s404_positive_nn_risk_union_top40_seed0_bc_rnn_e200/20260625140247/models/model_epoch_200.pth`
- Evaluation report:
  `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split404/positive_nn_risk_union_top40/eval_50ep/REPORT.md`
- Draft progress summary:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_can_endpoint_REPORT.md`

Result:

- v0.2 selected hard union reaches `27/50` success (`0.540`) with average
  length `248.4`.
- This is much lower than splits `101`/`202`/`303` (`45/50`, `45/50`,
  `39/50`). The A1 extension may weaken the clean Can story unless split `404`
  positive-only NN and weighted BC are also low.
- Do not update paper claims yet. Current comparable Can fresh-gate baseline
  evidence remains the original three splits: selected `129/150` versus best
  completed baselines `113/150`.

Next step:

- Run split `404` positive-only NN and weighted BC baselines before interpreting
  the split `404` selected-branch result.

## 2026-06-25: A1 Can split 404 positive-only baseline

Completed the first Can split `404` comparator after the selected branch was
weak. The `run_final_matrix.py --stage all` wrapper finished training but hung
before writing eval metrics, so it was interrupted after the epoch-200
checkpoint was present. Evaluation was then run directly with
`scripts/evaluate_robomimic_official_policy.py` against the exact epoch-200
checkpoint.

Artifacts:

- Positive-only checkpoint:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`
- Positive-only eval report:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/eval/REPORT.md`
- Updated draft progress report:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_can_endpoint_REPORT.md`

Result:

- Positive-only NN reaches `39/50` success (`0.780`) with average length
  `169.3`.
- v0.2 hard union on the same split is only `27/50` (`0.540`), so split `404`
  is a clear selected-branch loss to a no-bad-label baseline.
- Across Can splits with completed selected rows and at least one completed
  non-oracle baseline (`101`/`202`/`303`/`404`), v0.2 selected is now
  `156/200` versus best completed baselines `152/200`. This margin is much
  weaker than the original three-split Can gate.

Interpretation:

- The A1 extension is already doing useful stress-testing: it weakens the
  "clean Can" story and supports the paper's cautious framing.
- Do not promote five-split Can numbers until split `404` weighted BC and split
  `505` selected/baseline rows are complete.

## 2026-06-25: A1 Can split 404 weighted BC baseline

Completed the remaining strong baseline for Can split `404` with the direct
weighted-sampler trainer and direct endpoint evaluator, avoiding the
`run_final_matrix.py --stage all` post-train hang seen in the positive-only
row.

Artifacts:

- Weighted BC checkpoint:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/train/can_paired_pos40_bad80_split404_weighted_bc_policy0_official_bc_rnn/20260625143118/models/model_epoch_200.pth`
- Weighted BC eval report:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/eval/REPORT.md`
- Updated draft progress report:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_can_endpoint_REPORT.md`

Result:

- Weighted BC reaches `33/50` success (`0.660`) with average length `208.9`.
- Split `404` now has all three relevant endpoint rows: v0.2 selected hard
  union `27/50`, positive-only NN `39/50`, and weighted BC `33/50`.
- The best completed non-oracle baseline on split `404` is positive-only NN,
  so the selected branch loses by `12/50` on this split.
- Across the four completed Can splits (`101`/`202`/`303`/`404`), v0.2
  selected remains `156/200` versus best completed baselines `152/200`
  (margin `+0.020`).

Interpretation:

- The split `404` endpoint result substantially weakens the earlier three-split
  Can margin but does not reverse the four-split aggregate.
- Do not promote five-split Can numbers until split `505` selected, positive
  only, and weighted rows are complete.

## 2026-06-25: A1 Can split 505 selected-branch endpoint

Ran the next A1 selected-branch endpoint: Can 40p/80b split `505`, frozen v0.2
hard-union branch `positive_nn_risk_union_top40`.

Artifacts:

- Train config:
  `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split505/positive_nn_risk_union_top40/setup/config.json`
- Epoch-200 checkpoint:
  `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split505/positive_nn_risk_union_top40/train/v02fresh_can40_s505_positive_nn_risk_union_top40_seed0_bc_rnn_e200/20260625144046/models/model_epoch_200.pth`
- Evaluation report:
  `results/final_paper_v02/ablations/v02_fresh_endpoint_200ep_can40/split505/positive_nn_risk_union_top40/eval_50ep/REPORT.md`
- Updated draft progress report:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_can_endpoint_REPORT.md`

Result:

- v0.2 selected hard union reaches `41/50` success (`0.820`) with average
  length `158.8`.
- Completed selected Can rows are now `197/250` across split seeds
  `101`/`202`/`303`/`404`/`505`.
- Comparable Can evidence is unchanged until split `505` baselines finish:
  selected `156/200` versus best completed baselines `152/200` over
  `101`/`202`/`303`/`404`.

Interpretation:

- Split `505` selected performance is healthy, but it cannot repair or confirm
  the five-split claim until the positive-only NN and weighted BC comparator
  rows are complete.

## 2026-06-25: A1 Can split 505 baseline completion

Completed the remaining Can split `505` strong baselines with direct train/eval
calls: positive-only NN top40 and classifier-probability weighted BC.

Artifacts:

- Positive-only checkpoint:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/train/can_paired_pos40_bad80_split505_positive_only_nn_policy0_official_bc_rnn/20260625144918/models/model_epoch_200.pth`
- Positive-only eval report:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/eval/REPORT.md`
- Weighted BC checkpoint:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_weighted_bc_policy0/train/can_paired_pos40_bad80_split505_weighted_bc_policy0_official_bc_rnn/20260625145704/models/model_epoch_200.pth`
- Weighted BC eval report:
  `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_weighted_bc_policy0/eval/REPORT.md`
- Updated five-split Can progress report:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_can_endpoint_REPORT.md`

Result:

- Split `505`: selected hard union `41/50` (`0.820`), positive-only NN
  `40/50` (`0.800`), weighted BC `30/50` (`0.600`).
- All five Can split rows are now comparable. v0.2 selected totals `197/250`
  versus best completed non-oracle baselines `192/250`, margin `+0.020`.
- Per-split margins versus best non-oracle baseline are `+8/50`, `+5/50`,
  `+3/50`, `-12/50`, and `+1/50` for splits
  `101`/`202`/`303`/`404`/`505`.

Interpretation:

- A1 Can no longer supports a clean strong claim; it supports a small average
  selected-branch edge with one severe split-level reversal.
- Keep this as draft/progress evidence only until the Lift added-split rows are
  also complete and the canonical paper summaries are intentionally promoted.

## 2026-06-25: A1 Lift added splits and five-split gate completion

Completed the remaining A1 Lift MG endpoints for added split seeds `404` and
`505`, using direct train/eval commands rather than the wrapper.

Artifacts:

- Lift split `404` weighted report:
  `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_weighted_bc_policy0/eval/REPORT.md`
- Lift split `404` positive-only report:
  `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/eval/REPORT.md`
- Lift split `505` weighted report:
  `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_weighted_bc_policy0/eval/REPORT.md`
- Lift split `505` positive-only report:
  `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_positive_only_nn_policy0/eval/REPORT.md`
- Draft Lift summary:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_lift_endpoint_REPORT.md`
- Draft combined gate summary:
  `results/final_paper_v02/tables/a1_endpoint_progress/v02_fresh_gate_REPORT.md`

Result:

- Lift split `404`: selected weighted BC `30/50` (`0.600`) versus
  positive-only NN `25/50` (`0.500`).
- Lift split `505`: selected weighted BC `33/50` (`0.660`) versus
  positive-only NN `26/50` (`0.520`).
- Five-split Lift aggregate: selected weighted BC `143/250` versus best
  non-oracle baselines `125/250`, margin `+0.072`; selected wins 4/5 splits.
- Five-split Can aggregate from the completed A1 matrix: selected hard union
  `197/250` versus best non-oracle baselines `192/250`, margin `+0.020`;
  selected wins 4/5 splits.
- Combined Can+Lift A1 draft gate: selected rows `340/500` versus best
  per-split non-oracle baselines `317/500`, margin `+0.046`.

Implementation note:

- Updated `scripts/summarize_v02_fresh_gate.py` so the interpretation section
  reports split counts dynamically; the old hardcoded text was only correct for
  the original three-split gate.

Interpretation:

- A1 resolves the "only three split seeds" weakness in the draft evidence, but
  the resulting effect is modest and still has one losing split on each task.
- Do not promote these draft five-split rows into the paper until the canonical
  tables and uncertainty audit are regenerated intentionally.

## 2026-06-25: Promoted A1 five-split gate into canonical paper artifacts

Promoted the completed A1 five-split endpoint matrix from draft/progress
reports into the canonical `results/final_paper_v02/tables/` reports, the
manuscript, the claim package, and the paper validation contract.

Canonical five-split gate:

- Can 40p/80b selected hard union: `197/250` versus `192/250` best per-split
  non-oracle baselines; split margins `+8/50`, `+5/50`, `+3/50`, `-12/50`,
  and `+1/50`.
- Lift MG selected weighted BC: `143/250` versus `125/250` positive-only NN;
  split margins `+3/50`, `+5/50`, `-2/50`, `+5/50`, and `+7/50`.
- Combined selected rows: `340/500` versus `317/500`, pooled margin `+0.046`.
- Paired initial-state bootstrap intervals still cross zero: Can
  `[-0.144, 0.168]`, Lift `[-0.027, 0.167]`, combined `[-0.049, 0.136]`.

Implementation and validation:

- Updated the paper validation pipeline to regenerate v0.2 Can, Lift, router
  support, gate, and uncertainty reports over split seeds
  `101`/`202`/`303`/`404`/`505`.
- Updated `scripts/validate_paper_claim_numbers.py` to enforce the five-split
  counts, split rows, intervals, and manuscript caveats.
- Fixed v0.2 CSV writers to emit LF line endings so `git diff --check` stays
  clean after regeneration.
- `make -C paper validate` passes, including both LaTeX builds, claim-number
  validation, structure validation, artifact reference validation, and strict
  LaTeX log scans.

Interpretation:

- A1 is now a canonical paper-facing result, not just a preflight draft.
- The high-impact framing remains cautious: v0.2 is positive branch-selection
  evidence, but not a formal significance claim and not a universal dominance
  claim over positive-only retrieval or weighted BC.

## 2026-06-25: A2 router-regret table staged

Built the first paper-facing router-regret table for the v0.2 portfolio story.

Artifacts:

- Script:
  `scripts/summarize_v02_router_regret_table.py`
- Summary CSV:
  `results/final_paper_v02/tables/v02_router_regret_summary.csv`
- Per-regime CSV:
  `results/final_paper_v02/tables/v02_router_regret_per_regime.csv`
- Report:
  `results/final_paper_v02/tables/v02_router_regret_REPORT.md`

Result:

- Completed Can+Lift fresh rows: v0.2 selected branches have `14/500` regret
  to the audit-only oracle branch selector.
- Always positive-only NN has `55/500` Can+Lift regret.
- Always weighted BC has `53/500` Can+Lift regret.
- Generated Can regime probes show zero regret for bad-aware hard support on
  hard-negative, coverage-shift, and prefix-positive settings.
- Can MG is recorded as v0.2 `stress_abstain`, not a forced failure.

Scope caveat:

- This is an A2 current-state artifact, not a complete fixed-branch leaderboard.
  v0.1 TRIAGE-BC and fresh Lift hard-support rows are marked as A3 gaps rather
  than filled from non-comparable older split seeds.

Validation:

- Added the script to `paper/Makefile validate`.
- `make -C paper validate` passes and now checks 106 artifact references.

## 2026-06-25: A3 baseline completion started with fresh Lift v0.1 row

Started A3 by training and evaluating the first missing fresh v0.1
TRIAGE-BC / hard-support row:

- Task/split/method: `lift_mg`, `mg_sparse`, split seed `101`, `triage_bc`,
  policy seed `0`.
- Router branch: `hard_pos_min`.
- Training support: `301` demos, including `291` selected unlabeled demos.
- Checkpoints evaluated: epoch `50`, `100`, `150`, and `200`.
- Endpoint row used by the paper tables: epoch `200`, `36/50` successes
  (`0.720`) over valid-positive starts.

This row is stronger than the frozen v0.2 selected weighted branch on Lift
split `101` (`31/50`) and positive-only NN (`28/50`). After regenerating the
fresh gate, the canonical A1/A3-aware numbers are:

- Can 40p/80b remains `197/250` versus `192/250` best completed baselines.
- Lift MG becomes `143/250` versus `133/250` best completed per-split
  baselines, with split `101` now using `triage_bc` as the best baseline.
- Combined Can+Lift becomes `340/500` versus `325/500`, pooled margin
  `+0.030`.
- Paired initial-state bootstrap intervals still cross zero: Can
  `[-0.144, 0.168]`, Lift `[-0.017, 0.177]`, combined `[-0.045, 0.142]`.

Router-regret update:

- v0.2 Can+Lift regret to the completed oracle selector is now `19/500`.
- Always positive-only NN regret is `60/500`.
- Always weighted BC regret is `58/500`.
- v0.1 TRIAGE-BC is now partial rather than absent: `36/50` on the completed
  Lift split101 cell, with Can fresh and Lift split seeds `202`/`303`/`404`/`505`
  still marked as A3 gaps.

Implementation and validation:

- Fixed the fresh endpoint summarizers to select `model_epoch_200` when
  `metrics.csv` contains multiple checkpoint rows.
- Updated the router-regret script to consume completed `triage_bc` rows and
  mark partial branch coverage explicitly.
- Updated the manuscript, claim package, completion plan, and claim-number
  validator to the revised A3-aware numbers.
- `make -C paper validate` passes end to end.

## 2026-06-25: A3 Lift split202 v0.1 row completed

Completed the second fresh Lift v0.1 TRIAGE-BC / hard-support row:

- Task/split/method: `lift_mg`, `mg_sparse`, split seed `202`, `triage_bc`,
  policy seed `0`.
- Router branch: `hard_pos_min`.
- Training support: `231` demos, including `221` selected unlabeled demos.
- Endpoint evaluation: epoch `200`, `34/50` successes (`0.680`) over
  valid-positive starts.

This is again stronger than the frozen v0.2 selected weighted branch on the
same split (`30/50`) and positive-only NN (`25/50`). After regenerating the
paper artifacts with split101 and split202 v0.1 rows included:

- Can 40p/80b remains `197/250` versus `192/250`.
- Lift MG is now nearly tied: v0.2 weighted `143/250` versus best completed
  per-split baselines `142/250`; v0.2 wins only splits `404` and `505`.
- Combined Can+Lift is `340/500` versus `334/500`, pooled margin `+0.012`.
- Paired initial-state bootstrap intervals still cross zero: Can
  `[-0.144, 0.168]`, Lift `[-0.069, 0.158]`, combined `[-0.067, 0.128]`.

Router-regret update:

- v0.2 Can+Lift regret to the completed oracle selector is now `23/500`.
- Always positive-only NN regret is `64/500` on the Can+Lift rows.
- Always weighted BC regret is `62/500` on the Can+Lift rows.
- v0.1 TRIAGE-BC is still partial: `70/100` on completed Lift split101/202
  cells, with Can fresh and Lift split seeds `303`/`404`/`505` still A3 gaps.

Implementation and validation:

- Updated claim-number constants, manuscript text, claim package, completion
  plan, and v0.2 reports to the split202-aware numbers.
- Tightened the ICLR manuscript wording to keep the compiled PDF at the
  validator-expected 15 pages after the more cautious A3 wording.
- `make -C paper validate` passes end to end.

## 2026-06-25: A3 Lift split303 v0.1 row completed

Completed the third fresh Lift v0.1 TRIAGE-BC / hard-support audit row:

- Task/split/method: `lift_mg`, `mg_sparse`, split seed `303`, `triage_bc`,
  policy seed `0`.
- Router branch: `hard_pos_min`.
- Training support: `385` demos, including `375` selected unlabeled demos.
- Endpoint evaluation: epoch `200`, `20/50` successes (`0.400`) over
  valid-positive starts.

This row beats the frozen v0.2 selected weighted branch on the same split by
one success (`20/50` versus `19/50`) but does not beat positive-only NN
(`21/50`). After regenerating the paper artifacts with split101, split202, and
split303 v0.1 rows included:

- Can 40p/80b remains `197/250` versus `192/250`.
- Lift MG remains nearly tied: v0.2 weighted `143/250` versus best completed
  per-split baselines `142/250`; v0.2 wins only splits `404` and `505`.
- Combined Can+Lift remains `340/500` versus `334/500`, pooled margin
  `+0.012`.
- Paired initial-state bootstrap intervals still cross zero: Can
  `[-0.144, 0.168]`, Lift `[-0.069, 0.158]`, combined `[-0.067, 0.128]`.

Router-regret update:

- v0.2 Can+Lift regret to the completed oracle selector remains `23/500`.
- Always positive-only NN regret is `64/500` on the Can+Lift rows.
- Always weighted BC regret is `62/500` on the Can+Lift rows.
- v0.1 TRIAGE-BC is still partial but now covers three Lift cells:
  `90/150` with `1/150` regret to the same completed-split oracle.

Implementation and validation:

- Regenerated the Lift endpoint, fresh-gate, uncertainty, and router-regret
  reports under `results/final_paper_v02/tables/`.
- Updated the manuscript text, claim package, completion plans, and checklist
  to reflect the completed split303 audit row and refreshed regret counts.
- `make -C paper validate` passes end to end, including the claim-number
  validator and the 15-page ICLR PDF layout check.

## 2026-06-25: A3 Lift split404/505 v0.1 rows completed

Completed the remaining fresh Lift v0.1 TRIAGE-BC / hard-support audit rows:

- Split `404`: router branch `hard_pos_min`, training support `219` demos
  including `209` selected unlabeled demos, endpoint `29/50` successes
  (`0.580`) at epoch `200`.
- Split `505`: router branch `hard_pos_min`, training support `215` demos
  including `205` selected unlabeled demos, endpoint `24/50` successes
  (`0.480`) at epoch `200`.

These rows complete the five-split Lift v0.1 audit. Split `404` is just below
the frozen v0.2 selected weighted branch (`29/50` versus `30/50`) and above
positive-only NN (`25/50`). Split `505` is below both weighted BC (`33/50`) and
positive-only NN (`26/50`).

After regenerating the paper artifacts with all five Lift v0.1 rows included:

- Can 40p/80b remains `197/250` versus `192/250`.
- Lift MG becomes negative against the best completed per-split baselines:
  v0.2 weighted `143/250` versus `146/250`.
- Completed Lift v0.1 hard support ties weighted BC in aggregate at `143/250`,
  but the per-split oracle reaches `154/250`.
- Combined Can+Lift weakens to `340/500` versus `338/500`, pooled margin
  `+0.004`.
- Paired initial-state bootstrap intervals still cross zero: Can
  `[-0.144, 0.168]`, Lift `[-0.083, 0.140]`, combined `[-0.074, 0.120]`.

Router-regret update:

- v0.2 Can+Lift regret to the completed oracle selector remains `23/500`.
- Always positive-only NN regret is `64/500` on the Can+Lift rows.
- Always weighted BC regret is `62/500` on the Can+Lift rows.
- Always hard support now ties v0.2 on completed Can+Lift regret (`23/500`),
  so the portfolio claim should not be written as dominance over every fixed
  branch.

Implementation notes:

- Regenerated the Lift endpoint, fresh-gate, uncertainty, and router-regret
  reports under `results/final_paper_v02/tables/`.
- Updated the claim-number validator, manuscript text, claim package,
  checklist, and completion plans to the weaker `340/500` versus `338/500`
  gate.
- `make -C paper validate` passes end to end, including the refreshed
  claim-number validator and the 15-page ICLR PDF layout check.

## 2026-06-25: TRI-Signal regime-probe suite registry added

Created `REGIME_PROBE_SUITE.md` to turn the generated diagnostics into a
coherent paper-facing suite rather than a loose list of ablations.

The registry freezes six regimes:

- Prefix-positive Can: bad-aware `119/150` versus positive-only `6/150`.
- Hard-negative Can: bad-aware `104/150` versus positive-only `91/150`.
- Coverage-shift Can: bad-aware `120/150` versus positive-only `103/150`.
- Default Can 40p/80b: v0.2 hard union `197/250` versus best baselines
  `192/250`, while original v0.1 still loses to positive-only NN.
- Lift MG broad coverage: v0.2 weighted and v0.1 hard support tie at
  `143/250`, below the best per-split baseline total `146/250`.
- Can MG score plateau: abstention remains justified because likelihood
  proxies select weaker hard-support policies on the original Can MG check.

This is intentionally framed as a registry/freeze for paper claims, not a
retroactive claim that completed generated probes were pre-registered before
initial exploration. Future generated variants must be added to the registry
before endpoint training if they are to support fresh validation claims.

Also updated `METHOD_FREEZE_V02.md` to record that the original fresh seeds were
`101`/`202`/`303` and the five-split A1 extension added `404`/`505` before
promoting five-split endpoint numbers.

## 2026-06-25: Cross-regime precision/coverage frontier staged

Created `scripts/summarize_precision_coverage_frontier.py` and wired it into
`paper/Makefile` so the paper validation path regenerates:

- `results/final_paper/tables/precision_coverage_frontier.csv`
- `results/final_paper/tables/precision_coverage_frontier_REPORT.md`
- `results/final_paper/figures/precision_coverage_frontier.png`
- `results/final_paper/figures/precision_coverage_frontier.pdf`

The artifact puts Can 40p/80b, Can 20p/80b, Can 80p/80b, Lift MG, hard-negative
Can, coverage-shift Can, and prefix-positive Can in one hidden-positive-recall
versus hidden-bad-admission space. Endpoint-backed matched comparisons recover
the intended thesis: generated probes improve when bad-aware or hybrid support
improves both recall and bad-admission over positive-only retrieval, while
default Can 40p/80b and Lift MG show why positive-only precision and broad
weighted coverage remain first-class baselines.

## 2026-06-25: Policy-quality proxy no-go table staged

Created `scripts/summarize_policy_quality_proxy_no_go.py` and wired it into
`paper/Makefile` so the paper validation path regenerates:

- `results/final_paper/tables/policy_quality_proxy_no_go.csv`
- `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`

The consolidated table turns the scattered no-go evidence into a single
appendix artifact. It covers positive likelihood, positive-minus-negative
likelihood, negative rejection, coverage-only selection, initial/transition
coverage, support purity, and hidden-positive recall. Deployable proxy attempts
match endpoint winners in only `2/11` rows; audit-only support rows match in
`3/6`; original Can MG likelihood-style proxies match in `0/6`.

Paper-facing updates:

- Added the no-go artifact to the manuscript checklist, reproduction map,
  outline, Markdown draft, standalone TeX, ICLR TeX, claim package, and
  completion plans.
- Updated the expected artifact-reference validator count to `112` unique
  references and the standalone PDF page count to `17`.

Validation:

```bash
python scripts/summarize_policy_quality_proxy_no_go.py
python -m py_compile scripts/summarize_policy_quality_proxy_no_go.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_claim_numbers.py
make -C paper validate
```

The full paper validation gate passed: both PDFs compiled, the claim-number and
structure validators passed, and the artifact-reference validator reported
`checked 112 unique artifact references`.

## 2026-06-25: Hard-union component ablation staged

Created `scripts/summarize_hard_union_component_ablation.py` and wired it into
`paper/Makefile` along with the cheap upstream union and Can40 support
summaries:

- `scripts/summarize_can40_score_support_tradeoff.py`
- `scripts/summarize_v02_union_candidate_audit.py`
- `scripts/summarize_v02_union_endpoint_aggregate.py`
- `scripts/summarize_hard_union_component_ablation.py`

New generated B3 artifacts:

- `results/final_paper/tables/hard_union_component_ablation.csv`
- `results/final_paper/tables/hard_union_component_ablation_per_split.csv`
- `results/final_paper/tables/hard_union_component_ablation_REPORT.md`

The component table answers the B3 hard-union question without new policy
training:

- Positive-only NN top40 selects `106/120` hidden positives and `14/240`
  hidden bad demos, reaching `108/150`.
- Risk-fusion top40 improves the support audit to `117/120` hidden positives
  and `3/240` hidden bad demos, but reaches only `73/100`, `-0.070` versus
  positive-only on the same two endpoint splits.
- The union selects `119/120` hidden positives and `16/240` hidden bad demos,
  reaching `116/150`, `+0.053` versus positive-only over all three splits.
- Classifier-only top40 is support-only and dominated by positive-only top40
  (`85/120` hidden positives and `35/240` hidden bad demos).
- Weighted BC reaches `90/150`; v0.1 adaptive masscap reaches `99/150`.

Interpretation:

The union helps by combining mechanisms, not by replacing positive-only with
risk-fusion. It preserves the positive-only anchor and adds risk-derived
coverage. The pooled gain comes from split `22` and split `33`; split `11` still
favors positive-only NN.

Paper-facing updates:

- Added the B3 artifact to the manuscript checklist, reproduction map, outline,
  Markdown draft, standalone TeX, ICLR TeX, claim package, and completion plans.
- Extended `scripts/validate_paper_claim_numbers.py` with hard-union component
  row checks.
- Updated the artifact-reference validator count to `114` and the standalone
  PDF page count to `18`.

Validation:

```bash
python scripts/summarize_hard_union_component_ablation.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
```

The full paper validation gate passed after compacting the appendix wording:
both PDFs compiled, the ICLR-format PDF remained at 15 pages, the claim-number
and structure validators passed, and the artifact-reference validator reported
`checked 120 unique artifact references`.

## 2026-06-25: Active abstention evaluation staged

Created `scripts/summarize_active_abstention_evaluation.py` and staged the C2
abstention audit from existing router-v2 and Can MG branch-proxy artifacts.

New generated C2 artifacts:

- `results/final_paper/tables/active_abstention_evaluation.csv`
- `results/final_paper/tables/active_abstention_assignment_summary.csv`
- `results/final_paper/tables/active_abstention_evaluation_REPORT.md`

Key rows:

- Original Can MG is `stress_abstain` with mass/count `1947.9`/`1025.7`.
  Forced branches top out at weighted BC `0.333`, all-demo is worst at `0.100`,
  and likelihood-style proxies match best success in `0/6` cases.
- Shuffled Can MG is also `stress_abstain` with mass/count `1466.3`/`515.7`.
  The staged hard and soft forced branches both reach only `0.100`; proxies
  match best success in `6/6` cases only because both branches are tied and weak.
- Across the router-v2 audit, assigned rows average `0.700` fixed-20k success
  with minimum `0.600`, while abstained rows average `0.217` and top out at
  `0.333`.

Interpretation:

This stages C2 as a stress/limitation result. Abstention is justified as risk
control for large ambiguous MG score plateaus until a coverage-sensitive
policy-quality proxy is validated. It is not a Can MG endpoint-success claim.

Paper-facing updates:

- Added the active-abstention artifact to the manuscript checklist,
  reproduction map, outline, Markdown draft, claim package, and completion
  plans.
- Extended `paper/Makefile` to regenerate the C2 artifact.
- Extended `scripts/validate_paper_claim_numbers.py` with active-abstention row
  and assignment-summary checks.
- Extended `scripts/validate_paper_structure.py` with the new artifact-map rows.

Validation:

```bash
python scripts/summarize_active_abstention_evaluation.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
```

The full paper validation gate passed: both PDFs compiled, the ICLR-format PDF
remained at 15 pages, the claim-number and structure validators passed, and the
artifact-reference validator reported `checked 122 unique artifact references`.

## 2026-06-25: Theory-lite proposition staged

Staged Priority C3 by naming the existing precision/coverage risk decomposition
as `Proposition 1 (coverage-contamination criterion)` in the standalone TeX,
ICLR TeX, and Markdown draft.

Key proposition:

- Under the mixed useful/harmful support model, adding an unlabeled trajectory
  should improve the hard-selector bound when its marginal coverage gain exceeds
  its normalized marginal contamination cost.
- The weighted analogue keeps the same logic but replaces selected support size
  with effective sample size and bad-demo count with weighted bad-action mass.

Interpretation:

This is a theory-lite organizing result, not a formal guarantee for nonlinear
BC-RNN-GMM policies. It makes the empirical reversals explicit: hard support
wins when extra data mostly adds action-conflicting failures, soft weighting
wins when coverage dominates, and abstention is appropriate when the score shape
does not justify either branch.

Paper-facing updates:

- Updated `paper/triage_bc_paper.tex`, `paper/iclr2026/main.tex`, and
  `paper/triage_bc_draft.md`.
- Added C3 status to `triage_bc_top_tier_completion_plan.md` and
  `tri_piql_paper_completion_plan.md`.
- Added a theory-lite claim row to `results/PAPER_CLAIM_PACKAGE.md`.
- Added validator checks for `Proposition 1`, the
  `coverage-contamination criterion`, and the marginal coverage/contamination
  condition.

Validation:

```bash
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
```

The full paper validation gate passed: both PDFs compiled, the ICLR-format PDF
remained at 15 pages, the claim-number and structure validators passed, and the
artifact-reference validator reported `checked 122 unique artifact references`.

The full paper validation gate passed: both PDFs compiled, the claim-number and
structure validators passed, and the artifact-reference validator reported
`checked 114 unique artifact references`.

## 2026-06-25: Failure-mode initial-state audit staged

Created `scripts/summarize_failure_mode_initial_states.py` and wired it into
`paper/Makefile` after the hard-union component ablation.

New generated B4 artifacts:

- `results/final_paper/tables/failure_mode_initial_states_cases.csv`
- `results/final_paper/tables/failure_mode_initial_states.csv`
- `results/final_paper/tables/failure_mode_initial_states_REPORT.md`

The audit reuses existing Can 40p/80b endpoint rollouts and selects three
representative paired initial states:

- Hard-union rescue: split `33` / `demo_105`, union `5/5` versus positive-only
  `0/5`, weighted `1/5`, and all-demo `0/5`.
- Positive-anchor regression: split `11` / `demo_39`, positive-only `5/5`
  versus union `0/5` and weighted `0/5`.
- Soft-pool rescue: split `33` / `demo_99`, weighted `5/5` versus positive-only
  `0/5` and union `1/5`.

Interpretation:

The failure-mode audit supports the paper's current precision/coverage framing
rather than a one-sided hard-union story. The union can rescue states that
positive-only and full-pool cloning miss, but positive-only and weighted BC each
have representative rescue cases. The report explicitly marks grasp and
loop/miss fields as proxies derived from success and horizon-length failures,
not video-level annotations.

Paper-facing updates:

- Added the B4 artifact to the manuscript checklist, reproduction map, outline,
  Markdown draft, standalone TeX, ICLR TeX, claim package, and completion plans.
- Extended `scripts/validate_paper_claim_numbers.py` with selected-case and
  per-method row checks.
- Extended `scripts/validate_paper_structure.py` with the new artifact-map rows.

Validation:

```bash
python scripts/summarize_failure_mode_initial_states.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
```

The full paper validation gate passed: both PDFs compiled, the claim-number and
structure validators passed, and the artifact-reference validator reported
`checked 116 unique artifact references`.

## 2026-06-25: Prefix-length robustness support sweep staged

Created `scripts/summarize_can_prefix_length_robustness.py` and wired it into
`paper/Makefile` after the prefix-positive endpoint/figure artifact.

New generated B5 artifacts:

- `results/final_paper/tables/can_prefix_length_robustness.csv`
- `results/final_paper/tables/can_prefix_length_robustness_all_candidates.csv`
- `results/final_paper/tables/can_prefix_length_robustness_REPORT.md`
- generated split files under
  `results/final_paper/ablations/can_prefix_length_robustness_splits/`

The sweep varies the labeled-positive prefix length for the generated Can
prefix-positive construction while holding split seeds `101/202/303`, label
budget, and top80 support size fixed:

- Short prefixes: bad-aware state top80 selects `157` hidden positives and `83`
  hidden bad demos, versus prefix positive-NN top80 `61` and `179`; recall delta
  `+0.400`, bad-admission delta `-0.400`.
- Default prefixes: bad-aware state top80 selects `195` hidden positives and
  `45` hidden bad demos, versus prefix positive-NN top80 `37` and `203`; recall
  delta `+0.658`, bad-admission delta `-0.658`.
- Long prefixes: bad-aware state top80 selects `199` hidden positives and `41`
  hidden bad demos, versus prefix positive-NN top80 `22` and `218`; recall
  delta `+0.737`, bad-admission delta `-0.737`.

Interpretation:

The generated prefix-positive probe is not a one-point artifact of the default
prefix length. Across the short/default/long support-only sweep, bad-aware top80
improves hidden-positive recall and reduces hidden-bad admission at matched
support size. This strengthens the generated-probe mechanism story but should
not be promoted as a new endpoint result without endpoint training on a
non-default prefix setting.

Paper-facing updates:

- Added the B5 artifact to the manuscript checklist, reproduction map, outline,
  Markdown draft, standalone TeX, ICLR TeX, claim package, and completion plans.
- Extended `scripts/validate_paper_claim_numbers.py` with prefix-length
  robustness row checks.
- Extended `scripts/validate_paper_structure.py` with the new artifact-map rows.

Validation:

```bash
python scripts/summarize_can_prefix_length_robustness.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
```

The full paper validation gate passed: both PDFs compiled, the claim-number and
structure validators passed, and the artifact-reference validator reported
`checked 118 unique artifact references`.

## 2026-06-25: Lift hard-negative support audit staged

Created `scripts/summarize_lift_hard_negative_action_conflict_audit.py` as the
first non-Can generated support diagnostic for Priority C1.

New generated C1 support-only artifacts:

- `results/final_paper/ablations/lift_hard_negative_action_conflict_construction.csv`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_support_per_split.csv`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md`
- generated split files under
  `results/final_paper/ablations/lift_hard_negative_action_conflict_splits/`

Key support rows over generated Lift split seeds `101/202/303`:

- State-action positive-NN top40 selects `12/120` hidden positives and admits
  `108/240` hidden bad demos (`0.100` recall, `0.450` bad admission).
- Bad-aware proxy top40 selects `82/120` hidden positives and admits `38/240`
  hidden bad demos (`0.683` recall, `0.158` bad admission).
- Hybrid positive/filter/refill top40 selects `68/120` hidden positives and
  admits `52/240` hidden bad demos (`0.567` recall, `0.217` bad admission).

Interpretation:

The generated bad-aware support mechanism transfers beyond Can at the
support-audit level. This clears the first C1 support gate, but it should not be
reported as a non-Can policy result until Lift endpoint training is run.

Paper-facing updates:

- Added the support-only C1 artifact to the manuscript checklist, reproduction
  map, outline, Markdown draft, standalone TeX, ICLR TeX, claim package, and
  completion plans.
- Extended `paper/Makefile` to regenerate the Lift audit.
- Extended `scripts/validate_paper_claim_numbers.py` with Lift support row
  checks.
- Extended `scripts/validate_paper_structure.py` with the new artifact-map rows.

Validation:

```bash
python scripts/summarize_lift_hard_negative_action_conflict_audit.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_paper_structure.py
make -C paper validate
```
