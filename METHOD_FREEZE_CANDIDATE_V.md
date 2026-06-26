# Candidate V Output-Anchor Validation Freeze

Date: 2026-06-26

## Purpose

Candidate V is the strongest training-side lead after Candidate F failed fresh
validation. It improves the Can split-404 first-20 screen (`18/20` versus
positive-only `17/20`) but ties positive-only on the split-404 50-episode check
(`39/50`). This freeze defines the next small validation step before spending
more endpoint budget.

## Frozen Method

Use positive-only initialization plus Candidate C sequence-mask fine-tuning with
an output-level anchor:

- initialize from the split-specific positive-only NN epoch-200 checkpoint;
- train on the split-specific weighted-BC train pool;
- use Candidate C sequence-mask weights with:
  - demo score threshold `0.20`;
  - state-action margin threshold `2.0`;
- add frozen-policy anchor hinge:
  `max(0, log pi_anchor(a|s) - log pi_train(a|s))`;
- apply the anchor hinge only where `loss_weight >= 0.999`;
- anchor-logprob weight `10.0`;
- train for `20` epochs with `100` batches per epoch;
- use checkpoint epoch `10` for validation.

No endpoint result from the validation split may be used to change these
hyperparameters or checkpoint selection.

## First Validation Split

Run Can 40p/80b split seed `505` first.

Reason: split `505` is a stability check where the positive-only anchor is
already strong. A useful training-side method must not damage this anchor while
borrowing sequence-mask coverage.

## Gate

For split `505`, evaluate only epoch `10`.

- First-20 screen: Candidate V should be no worse than positive-only by more
  than one episode.
- If the first-20 screen passes, run a 50-episode check.
- Promotion requires the 50-episode result to match or beat positive-only and
  not trail the best completed non-oracle baseline.

Failing this gate means Candidate V remains a split-404 development lead only,
not a paper-facing method.

## Result

Status as of 2026-06-26: failed the first validation gate.

- Split `505` first-20: Candidate V epoch `10` reached `16/20`, versus
  positive-only `15/20`; this passed the first-20 stability screen.
- Split `505` 50-episode check: Candidate V epoch `10` reached `38/50`, below
  positive-only `40/50` and below the best completed non-oracle baseline.

Decision: do not scale Candidate V as a paper-facing method. Output anchoring is
more promising than parameter L2, but this frozen non-404 validation result is
negative.
