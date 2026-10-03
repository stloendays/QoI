# Author-authorized scope addendum — three-stage workflow, certifying writer and finite-panel admission bound (2026-10-03)

## Authorization and purpose

The author reopened the scope re-frozen on 2026-09-30 (`paper/QOI_GENERALITY_SCOPE_ADDENDUM_20260930.md`) and the
2026-10-01 measurement-contract refreeze, with the instruction to revise the manuscript without adding experiments
and without removing or narrowing any claim (2026-10-03: "改稿件，不加实验也不删 claim … 好滴，开始吧"). This
addendum records what enters the reader-facing story from evidence that was already complete, and the one
supporting computation the author requested (a local re-computation of the QSQ floor to establish probe
exchangeability).

No primary cohort, perturbation definition, threshold, QoI definition, codec ladder or acceptance rule changes.
P1–P4, the grid-local-extrema result, the all-electron-reference decomposition and the Fourier mechanism are kept in
full.

## Canonical decisions

### Reader-facing organization: qualification → certification → diagnosis

The existing evidence is organized as three linked capabilities of one workflow:

1. **Qualification (eligibility).** QSQ decides whether the declared measurement contract can resolve the requested
   tolerance. Evidence: P1 equal-search control, P2 prospective validation, P3A implementation transfer,
   grid-local extrema, codec-shaped probe robustness, all-electron-reference contracts.
2. **Certification.** For an eligible contract, a reconstruction is certified when its re-derived QoI error is
   below the tolerance. Evidence: stability-qualified rate–fidelity frontier, certifying writer (WP-E, below),
   external confirmation.
3. **Diagnosis.** Mechanism layer explaining why a contract is unstable or a codec fails, per operator: Bader —
   partition-defining field and basin migration (Fig. 5, all-electron-reference decomposition); Hartree — Fourier
   error allocation weighted by the operator (Fig. 7).

The Bader diagnosis and the Hartree diagnosis stay separate. The Fourier statistic is not used to explain the
Bader residual.

### Three outcome labels (terminology unification)

Reader-facing labels, used identically in text, figures, captions and SI:

| Outcome | Condition | Meaning | Machine-readable reason code |
|---|---|---|---|
| **certified** | eligible and re-derived QoI error < τ | the reconstruction supports this QoI at this tolerance under this contract | `QOI_CERTIFIED` |
| **not certified** | eligible and error ≥ τ for every evaluated setting | a compression-use boundary for this contract | `QOI_NOT_CERTIFIED` |
| **non-evaluable** | QSQ floor ≥ τ | the reference analysis cannot resolve the tolerance; neither a codec pass nor a codec failure | `REFERENCE_NOT_RESOLVED` |

"Non-evaluable" is retained (not "not certifiable") because it is already the label in Figs. 1, 3, 4, S1, S7, the SI
and the claim–evidence matrix, and because it names the reference limitation rather than suggesting a codec outcome.
The brainstorm note `paper/QSQ_WORKFLOW_BRAINSTORM_20261003.md` is aligned to these labels.

### WP-E certifying writer — promote to a compact Results subsection

`analysis/extensions_20260930/WP-E/` (no new computation; 254 development materials, 6,343 frozen rows). The writer
runs QSQ, skips non-evaluable materials, and per codec bisects the tolerance ladder; it returns the loosest certified
row it evaluated across the three codecs, together with its certificate. The adopted policy (BISECT) was selected
by the pre-declared rule before any WP-F density was read.

Reader-facing numbers (over QSQ-eligible materials; archive compression = Σ raw bytes / Σ stored bytes):

| τ (e) | eligible | writer archive CR | oracle archive CR | fraction of oracle | misses | Bader solves per eligible material (writer / exhaustive) |
|---:|---:|---:|---:|---:|---:|---:|
| 1e-4 | 46 | 8.45 | 8.47 | 0.998 | 0/46 | 16.7 / 38.5 |
| 1e-3 | 143 | 14.90 | 15.13 | 0.985 | 0/143 | 16.7 / 37.0 |
| 1e-2 | 229 | 24.55 | 24.79 | 0.990 | 0/227 | 15.9 / 32.2 |

The best single-codec writer keeps at most 84.0% of the oracle at 1e-3 e (ZFP). With exact sequential QSQ (WP-H,
already in Methods) the mean end-to-end cost over all 254 materials falls from 12.004 to 10.339 Bader solves at
1e-3 e with unchanged archive compression and zero misses.

Boundary: certification is not monotone in tolerance for Bader; bisection can therefore return a tighter row than
the oracle (hence 98.5%, not 100%). Every returned row is evaluated, so every certificate is valid by construction.

### Finite-panel admission bound — Methods plus one Results sentence

If the n qualification probes and a later probe are exchangeable draws from the declared perturbation family, then
for every contract and every response distribution, P(admitted ∧ later probe ≥ τ) = p(1 − p)^n ≤ n^n/(n + 1)^(n+1)
(6.70% for n = 5). This is a distribution-free property of the finite-panel rule, not a worst-case certificate.

Evidence requirement: `analysis/extensions_20261003/QSQ-exchangeability/` (protocol declared before any probe ran)
reproduces the frozen five-seed floor locally and tests exchangeability with material-independent streams. The
Results sentence reports the observed joint rate (0.901% at 1e-3 e, 135/14,986) against the bound. Methods states
that the frozen seeds are shared across materials, so the bound holds per contract on average over the seed draw.

### Positioning — Compression Safeguards

Tyree et al. (EGUsphere 2026-4266) is cited with Jiao et al. and TOPIQ. Distinction: safeguards enforce
user-declared requirements on the decoded data; QSQ decides whether a declared QoI requirement is resolvable by the
reference analysis at all, which is a precondition for enforcing or certifying it.

### Discussion — what each outcome licenses

A Discussion paragraph maps outcomes to actions using completed evidence only: a non-evaluable contract can be
changed (exact partition-defining reference: 3/50 → 50/50 eligible at 1e-3 e), coarsened to the scientific decision
actually protected (P4: 60/60 directions preserved), or matched to a tolerance the reference resolves (external:
16 → 42 → 57 of 63 eligible); a not-certified result moves the search to a tighter setting or another codec
(the certifying writer).

## Figure policy

- **Fig. 1** is redrawn as the three-stage workflow with the three outcome labels, as a designed schematic (metro-map
  track, no box-and-arrow flowchart). It replaces the current Fig. 1; it does not add a figure.
- **Fig. 5** gains one panel for the all-electron-reference contract decomposition (charge-field, joint and
  partition-field contracts at 1e-3 e). The existing panels are kept.
- WP-E enters as Supplementary Fig. S9 (writer cost versus fraction of oracle). The eight-figure main-text
  architecture is unchanged.

## Not included

- **WP-F** (Materials Project archive estimate): 235/300 sampled objects complete; no reader-facing number until the
  pre-declared estimator runs on the complete sample.
- **WP-J** (JHTDB turbulence): pilot and confirmatory acceptance NOT MET; outside the electronic-density title. A new
  cohort with the qualification panel sized from the admission bound is pre-registered on
  `ext/turbulence-generality-20261001` and does not enter this manuscript.

## Claim boundaries

Do not claim:
- that the admission bound is a worst-case or per-material simultaneous guarantee;
- that the frozen shared seeds are independent across materials;
- that the certifying writer returns the oracle row (it returns a certified row at ≥ 98.5% of oracle archive
  compression in the development set);
- that the Hartree Fourier mechanism explains the Bader residual;
- that QSQ eligibility transfers between QoIs;
- cross-domain (turbulence) generality.

This addendum re-freezes the scope after the 2026-10-03 workflow integration.
