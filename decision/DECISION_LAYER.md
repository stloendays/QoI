# Scientific Compression Decision Layer

Status: **post-freeze software extension**. This layer does not alter P1-P4, QSQ thresholds, cohorts, endpoint definitions, or any frozen manuscript claim.

## Purpose

The current QSQ benchmark answers whether a requested downstream Bader tolerance is scientifically evaluable and whether a measured codec operating point is certified. The decision layer adds a separate question:

> Among operating points that are already QSQ-eligible and scientifically certified, which measured configuration best matches the user's engineering objective?

The separation is deliberate:

`scientific objective -> QSQ -> eligibility -> codec evaluation -> certification -> decision ranking`

QSQ remains the qualification layer. The decision layer is downstream decision support; it cannot create or override scientific validity.

## Deterministic recommendation states

The reference implementation (`scripts/recommend_codec.py`) returns one of four states:

- `CERTIFIED_RECOMMENDATION`: QSQ eligibility is satisfied and at least one measured operating point is certified; rank only those certified candidates.
- `NO_CERTIFIED_CANDIDATE`: the QoI is eligible at the requested tolerance, but no measured codec setting satisfies the contract.
- `NON_EVALUABLE_BADER_UNSTABLE`: QSQ does not support the requested absolute-Bader tolerance; no codec is labeled pass/fail at that precision.
- `ELIGIBILITY_UNAVAILABLE` / `MATERIAL_NOT_FOUND`: required evidence is absent; do not invent a recommendation.

## Supported objectives

The first implementation is intentionally conservative and uses the frozen absolute re-derived Bader-charge contract.

1. `max-compression`: choose the highest compression ratio among certified measured candidates.
2. `max-margin`: prefer the smallest `Bader_error_resolved_e`, using compression ratio as the tie-breaker.
3. `min-runtime`: prefer the smallest measured `encode_seconds + bader_seconds`, using compression ratio as the tie-breaker.
4. `balanced`: combine normalized log compression ratio, scientific margin `(tau - Bader_error_resolved_e) / tau`, and measured runtime. Default weights are 0.50 / 0.35 / 0.15 and are explicit CLI parameters.

No ranking objective is allowed to rescue a non-evaluable or uncertified candidate.

## Why the Agent should sit outside this layer

An Agent is useful, but only as an orchestrator around deterministic scientific components. Its legitimate jobs are:

- translate a user request such as "I care mostly about storage but need Bader error below 1e-3 e" into a structured decision request;
- run QSQ/eligibility checks and the deterministic ranking code;
- explain the winning configuration, alternatives, margins, and missing evidence;
- request or schedule additional benchmark measurements when no certified measured candidate exists;
- preserve a machine-readable decision trace.

The Agent must **not**:

- change QSQ thresholds, seeds, perturbation definitions, or eligibility labels;
- label a QSQ-rejected target as scientifically certified because an LLM judges it "close enough";
- extrapolate certification to unmeasured codec settings;
- treat the P4 charge-transfer-sign result as a universal license to ignore QSQ for other materials/endpoints;
- silently switch the scientific endpoint from precise Bader charge to a coarser endpoint to obtain a favorable answer.

Therefore the architecture is:

`Natural-language user intent`

`-> Agent / orchestrator (non-authoritative)`

`-> explicit measurement contract`

`-> QSQ + deterministic certification (authoritative)`

`-> deterministic Decision Layer (authoritative for ranking measured certified candidates)`

`-> Agent explanation / next-action proposal (non-authoritative)`

## Task-aware extension

P4 shows why a future task-aware contract registry is scientifically useful: a strict absolute Bader-charge tolerance and a coarse charge-transfer-sign endpoint are different measurement contracts. The correct extension is **not** to bypass QSQ. It is to declare the endpoint first and attach endpoint-specific qualification/evidence rules.

A future contract registry can therefore expose, for example:

- `bader_absolute(tau_e=1e-3)` — supported now by the QSQ benchmark and deterministic recommender;
- `charge_transfer_sign(pair_definition=...)` — only where endpoint-specific reference/validation evidence exists;
- future QoIs — each with its own stability qualification and certification semantics.

Until such endpoint-specific evidence exists, the Agent must say "unsupported contract" rather than reuse the Bader contract or infer scientific safety.

## Reproducibility requirement

Every recommendation should save:

- material ID;
- requested endpoint and tolerance;
- QSQ eligibility source;
- candidate rows considered;
- certification rule/source;
- objective and weights;
- selected candidate and alternatives;
- repository commit/hash of the benchmark inputs.

This makes the Agent interface auditable while keeping the scientific decision path deterministic.
