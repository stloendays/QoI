# Figure 3 caption — final manuscript version (2026-09-11)

## Primary caption

**Figure 3 | Stability qualification converts binary Bader benchmarking into a three-state certification problem.** **A,** Naive binary outcomes for 762 development material–codec decisions at each Bader threshold (254 materials × 3 codecs), scored without testing whether the reference Bader analysis is numerically resolvable at the requested tolerance. **B,** QoI Stability Qualification (QSQ) first establishes material-level numerical eligibility and then assigns each decision as certified, eligible but not certified, or non-evaluable. **C,** Reclassification of naive failures after qualification. At 10^-4 e, 518 of 533 apparent failures (97.2%) are non-evaluable and only 15 remain genuine failures among eligible pairs; at 10^-3 e, 296 of 310 (95.5%) are non-evaluable and 14 remain genuine failures. At 10^-2 e, 61 of 108 apparent failures (56.5%) are non-evaluable. Eligibility is not a relaxed pass criterion: at 10^-4 e, 106 of 229 naive passes (46.3%) also occur on non-evaluable pairs. Thus, strict-threshold binary reporting confounds compressor-induced error with numerical instability of the downstream Bader analysis.

## Short caption option

**Figure 3 | Binary Bader benchmarking misattributes non-evaluable targets as codec failures.** QSQ converts each material–codec decision from an unconditional pass/fail label into certified, eligible but not certified, or non-evaluable. At 10^-4 and 10^-3 e, 97.2% and 95.5% of naive failures, respectively, occur on material–threshold pairs that fail the independent numerical-eligibility test. At 10^-4 e, 46.3% of naive passes are also non-evaluable.

## Approved in-text callout

> At the two strictest Bader contracts, 97.2% and 95.5% of apparent binary failures are reclassified as non-evaluable after independent stability qualification, demonstrating that unconditional pass/fail reporting is not a valid scientific benchmark at those precisions.

## Interpretation boundary

Do not describe QSQ as “rescuing” failed codecs or as a more permissive pass criterion. A non-evaluable material–threshold pair is neither a pass nor a failure; the label itself is scientifically undefined at the requested precision.
