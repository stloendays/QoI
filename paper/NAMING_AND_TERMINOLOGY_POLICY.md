# Naming and terminology policy

## Reader-facing naming rule

Formal scientific names used in the manuscript, figures, captions, presentations, and other reader-facing material should be semantic, concise, memorable, and interpretable without knowledge of the project's development history.

Do not use internal iteration labels such as `A.1`, `v2`, `v3.1`, `rev2`, dated suffixes, or similar engineering-style identifiers as formal method, framework, or concept names. Version labels belong to internal provenance only.

When naming a method, framework, workflow component, algorithm, or scientific concept, prefer names that:

- communicate what the method does or what scientific role it plays;
- are short enough to read naturally in a manuscript sentence;
- are easy to remember and cite;
- avoid unnecessary jargon and forced acronyms;
- do not overclaim scope or generality;
- remain consistent across title, abstract, main text, figures, captions, and talks.

## Provenance separation

Internal historical labels may remain in frozen data, scripts, manifests, filenames, archived protocol records, and commits whenever changing them would weaken reproducibility or provenance.

Therefore:

- reader-facing text uses the formal semantic name;
- frozen/internal assets may retain historical labels;
- historical labels should not be promoted into the scientific name of the method;
- if an earlier implementation must be discussed, describe it as an archived predecessor, earlier probe, or frozen implementation where possible.

## Current QoI paper terminology

The reader-facing framework name is:

**QoI Stability Qualification (QSQ)**

The operational procedure may be described as a:

**perturbation-based numerical identifiability test**

or, more briefly, a:

**stability probe**

The canonical logic is:

`stability qualification -> eligibility -> compression evaluation -> certification`

The terms have distinct roles:

- **stability qualification**: tests whether the requested QoI tolerance is numerically identifiable;
- **eligibility**: indicates whether a material-threshold pair can support a scientifically meaningful benchmark decision;
- **certification**: evaluates codec performance only after eligibility has been established.

`Protocol A` and `Protocol A.1` remain historical/internal labels for provenance and reproducibility. They should not be used as the preferred reader-facing method name in future manuscript revisions.
