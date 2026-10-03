# QSQ Workflow Brainstorm: Eligibility -> Certification -> Diagnosis

Date: 2026-10-03

Status: research/design note. This document records the current conceptual interpretation of the workflow. It does **not** replace frozen protocols or claim-evidence tables, and it should not be treated as new experimental evidence until the corresponding analyses are implemented and audited.

**Terminology alignment (2026-10-03).** The reader-facing outcome labels are **certified**, **not certified** and **non-evaluable** (`paper/NAMING_AND_TERMINOLOGY_POLICY.md`). The label originally written here as "NOT CERTIFIABLE" is the paper's **non-evaluable** outcome and has been renamed throughout this note. The integrated manuscript wording is governed by `paper/WORKFLOW_SCOPE_ADDENDUM_20261003.md`.

## 1. What problem the workflow is intended to answer

The workflow is not designed to decide whether a scientific dataset is "true" in an absolute sense. Its operational question is narrower and auditable:

> Can a lossy-compressed representation support a specified downstream quantity of interest (QoI), at a specified scientific tolerance, under a validated reference protocol?

Conventional compressor guarantees are usually data-space guarantees, e.g.

```
||x_tilde - x||_inf <= epsilon
```

but scientific users ultimately consume downstream observables `Q(x)`. The desired scientific-use contract is therefore closer to

```
|Q(x_tilde) - Q(x)| <= tau_Q
```

subject to the important prerequisite that `Q(x)` itself is sufficiently stable to resolve `tau_Q`.

## 2. Three-stage interpretation

### Stage A — Eligibility: is the ruler precise enough?

Before judging compression, evaluate the numerical stability of the uncompressed reference QoI.

If the reference uncertainty / perturbation floor is too large relative to the requested QoI tolerance, the case is not eligible for certification at that tolerance.

This outcome should be reported as:

**NON-EVALUABLE**

It does not mean that the original field is wrong, nor that a compressor failed. It means that the current reference pipeline cannot resolve a compression-induced effect at the requested scale.

Possible follow-up actions include improving the numerical reference, performing convergence studies, adopting a physically justified more stable QoI definition, or selecting a tolerance consistent with the scientific question.

### Stage B — Certification: does the compressed representation preserve the intended scientific use?

For an eligible case, compress and reconstruct the field, compute the same downstream QoI, and compare against the uncompressed reference:

```
Delta Q = Q(x_tilde) - Q(x)
```

If the predefined certification criterion is satisfied, report:

**CERTIFIED at the specified QoI/tolerance/protocol**

If the reference is eligible but the compression-induced QoI error exceeds the tolerance, report:

**NOT CERTIFIED**

"Not certified" is therefore a usage boundary, not a global statement that the compressor is bad. It means that this compressor/setting should not be relied upon for this particular QoI at this particular tolerance without further adjustment.

### Stage C — Diagnosis: why did certification succeed or fail?

Certification alone provides a decision. The mechanism layer should investigate why different reconstructions can produce different QoI errors even at matched data-space error.

Candidate explanatory variables already relevant to the project include:

- reconstruction-error magnitude;
- spatial localization of error;
- Fourier error spectrum `|Delta x(G)|^2`;
- low-G versus high-G error content;
- spectral centroid;
- downstream-operator-weighted error measures;
- local/topological sensitivity for partition-based QoIs.

The working hypothesis is not "high frequency is always bad" or "low frequency is always bad." Rather:

> Which error modes matter is determined jointly by the reconstruction-error structure and the downstream operator.

This separates **detection** ("the QoI failed") from **diagnosis** ("which error modes and operator sensitivities explain the failure").

## 3. Decision semantics

The workflow should preserve three distinct outcomes:

| Reference stability at target tolerance | Compression QoI criterion | Outcome | Meaning |
|---|---|---|---|
| insufficient | not evaluated as a certification decision | NON-EVALUABLE | reference resolution is insufficient for the requested claim |
| sufficient | satisfied | CERTIFIED | compressed representation is supported for this QoI/tolerance/protocol |
| sufficient | violated | NOT CERTIFIED | this compression setting is not supported for this QoI/tolerance/protocol |

These labels must not be collapsed. In particular, NON-EVALUABLE is a measurement/reference limitation, whereas NOT CERTIFIED is a compression-use limitation after eligibility has been established.

## 4. Practical value

The workflow can be used to construct a QoI-specific operating envelope for scientific compression.

For a sequence of compressor settings or achieved compression ratios, identify the region in which the scientific-use criterion remains satisfied. Conceptually:

```
maximize compression benefit
subject to:
  reference is eligible at tau_Q
  QoI error <= tau_Q
```

This turns the user-facing question from "Which compressor has the best PSNR/RMSE/L_inf?" into "How aggressively may this field be compressed while retaining support for the scientific analysis I intend to perform?"

The result is deliberately QoI-specific. A representation certified for Bader charge at one tolerance is not automatically certified for a Hartree-related observable, another tolerance, or another downstream analysis.

## 5. Example: charge density -> Bader QoI

Conceptual execution:

```
uncompressed charge density
        |
        v
reference QoI + stability assessment
        |
        +-- insufficient at tau_Q --> NON-EVALUABLE
        |
        v
compress -> decompress
        |
        v
data-space error audit
        |
        v
same Bader analysis
        |
        v
Delta Q versus tau_Q
        |
        +-- pass --> CERTIFIED
        |
        +-- fail --> NOT CERTIFIED
                       |
                       v
                mechanism diagnosis
```

The key distinction is that a small `L_inf` reconstruction error is not itself a scientific-use certificate. The downstream QoI must be evaluated, and the reference must first be capable of supporting the requested resolution.

## 6. Generality beyond charge density

The abstraction is field/operator/QoI based:

```
scientific field
    -> lossy compression
    -> reconstruction error
    -> downstream operator
    -> QoI error
```

For electronic-structure data, examples include charge density feeding Bader or Hartree-related analyses. For turbulence, velocity fields can feed derivative-based observables such as vorticity or Q-criterion.

Status of the turbulence example (2026-10-03): the JHTDB pilot and independent confirmation (`ext/turbulence-generality-20261001`, WP-J) did not meet the pre-declared acceptance criteria (confirmatory rejected/eligible risk ratios 3.71 and 3.18 against a required 5). A second independent cohort with a 19-probe qualification panel sized from the finite-panel admission bound was then pre-registered and run on `ext/turbulence-n19-20261003`, and met acceptance on both endpoints (vortex mask RR 17.7, enstrophy RR 13.4; joint admission-and-exceedance 0.79% and 0.45% against the 1.89% bound). It stays outside the electronic-density manuscript unless the author decides otherwise.

The general claim to test is therefore not that one frequency band is universally important. It is that scientific compressibility is jointly conditioned by:

1. reference stability,
2. the downstream operator,
3. the spatial/frequency structure of reconstruction error.

## 7. Product-level interpretation

A useful long-term interpretation of QSQ is a **scientific data quality-control / admission layer** between storage compression and downstream science.

The compressor answers:

> How can the field be represented more compactly?

QSQ answers:

> For which declared scientific uses is that representation supported?

This can eventually support machine-readable scientific-use contracts containing at least:

- dataset / field identity;
- compressor and setting;
- achieved error and compression statistics;
- QoI definition;
- reference protocol and stability evidence;
- target tolerance;
- certification outcome;
- failure / non-certifiability reason;
- optional mechanism diagnostics.

## 8. Guardrails for manuscript wording

Prefer claims such as:

> The framework assesses whether a lossy-compressed representation remains suitable for a specified downstream QoI at a specified tolerance under a validated reference protocol.

Avoid global claims such as:

> The framework proves that the data are scientifically correct.

Certification is conditional on the declared QoI, tolerance, reference protocol, numerical setup, and tested population. The workflow should expose these conditions rather than hide them.

## 9. Immediate implications for the project

This brainstorm suggests that the workflow should be communicated as three linked capabilities:

**Eligibility -> Certification -> Diagnosis**

and that future implementation/reporting should make the reason code explicit:

- `REFERENCE_NOT_RESOLVED`
- `QOI_CERTIFIED`
- `QOI_NOT_CERTIFIED`

Additional reason codes may later distinguish numerical-reference limitations, downstream-analysis failures, missing QoI outputs, and mechanism-audit status.

Any incorporation into the frozen manuscript should occur only after checking consistency with the current protocol definitions, existing QSQ terminology, and the claim-evidence matrix.
