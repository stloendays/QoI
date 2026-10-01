# Contract-aware QoI Stability Qualification — interface specification

Status: **development specification**. This document defines the optimization-layer interface for future QSQ implementations. It does not replace the frozen five-seed QSQ endpoint used by the current manuscript.

## 1. Purpose

QSQ should qualify the numerical stability of the **actual scientific measurement contract**, not an abstract data array in isolation.

A downstream quantity is written as

[
Q = Q(x_1,ldots,x_p; A),
]

where (x_j) are input fields or auxiliary references and (A) denotes the downstream numerical algorithm and its settings.

Each input is assigned one declared role:

- **exact** — retained bitwise / numerically unchanged by the deployment workflow;
- **approximate** — compressed, quantized, interpolated, reduced in precision, or otherwise perturbed;
- **derived** — deterministically reconstructed from declared exact/approximate inputs;
- **excluded** — not part of the downstream measurement contract.

QSQ perturbs only inputs declared **approximate**. Exact inputs remain fixed.

## 2. Contract object

A machine-readable QSQ contract should contain:

- `qoi_name`;
- `algorithm_name` and implementation/version identifier;
- scientific tolerance `tau`;
- input-field list;
- role of every input;
- perturbation amplitude rule for every approximate input;
- perturbation family;
- frozen seed list;
- response metric;
- eligibility rule;
- optional early-stopping rule;
- provenance hashes for the reference inputs.

Conceptual schema:

```json
{
  "qoi": "bader_charge",
  "algorithm": "henkelman_bader_1.05_ongrid",
  "tau": 0.001,
  "inputs": [
    {
      "name": "CHGCAR",
      "role": "approximate",
      "perturbation_scale": "float32_Linf"
    },
    {
      "name": "AECCAR0+AECCAR2",
      "role": "exact"
    }
  ],
  "perturbation_family": "iid_uniform",
  "seeds": [20260905, 1, 2, 3, 4],
  "response": "max_abs_per_atom_charge_change",
  "eligibility": "max_seed_response < tau",
  "early_reject": true
}
```

The JSON above is illustrative syntax, not a replacement for the frozen manuscript contract.

## 3. Qualification response

For contract (C), seed (k), and declared perturbations (delta_{j,k}),

[
r_{C,k}
=
d_Qleft[
Q(x_1',ldots,x_p';A),
Q(x_1,ldots,x_p;A)
ight],
]

where

[
x_j'=
egin{cases}
x_j+delta_{j,k}, & x_j	ext{ approximate},\
x_j, & x_j	ext{ exact}.
end{cases}
]

The finite-panel stability floor is

[
f_C=max_k r_{C,k}.
]

Binary qualification at tolerance (	au) is

[
mathrm{eligible}(C,	au)
iff
f_C<	au.
]

This remains an empirical finite-panel qualification, not a worst-case mathematical bound.

## 4. Exact sequential execution

For binary eligibility at a fixed (	au), probes are evaluated in the frozen order.

If any response satisfies

[
r_{C,k}ge	au,
]

evaluation stops immediately and the contract is rejected. Because the final statistic is the maximum over the same seeds, this rule is exactly classification-equivalent to evaluating all five probes.

Full five-seed execution remains mandatory when the numerical value of (f_C) itself is required.

## 5. Bader examples

### Contract B1 — compressed CHGCAR, exact all-electron partition reference

- CHGCAR: approximate;
- AECCAR0+AECCAR2: exact;
- QSQ perturbs CHGCAR only.

This corresponds to the scientific semantics tested by WP-G G1.

### Contract B2 — compressed CHGCAR and compressed all-electron partition reference

- CHGCAR: approximate;
- AECCAR0+AECCAR2: approximate;
- QSQ perturbs both with separately declared scales and deterministic seed streams.

This corresponds to WP-G G2.

### Contract B3 — exact CHGCAR, approximate partition reference

- CHGCAR: exact;
- AECCAR0+AECCAR2: approximate;
- QSQ perturbs only the partition-defining reference.

This is the WP-I G3 mechanism-decomposition arm.

The contracts must not be pooled as if they were one QoI definition. They answer different deployment questions.

## 6. Codec independence

The qualification perturbation family is defined by the measurement contract, not by the compressor being ranked.

Therefore the primary QSQ decision remains codec-independent.

Codec-shaped perturbations may be used as robustness diagnostics, but cannot silently redefine eligibility for individual codecs.

## 7. Recommended execution states

A production implementation may expose:

- `QUALIFIED` — all required probes remain below (	au);
- `REJECTED` — at least one probe reaches or exceeds (	au);
- `INPUT_FAILURE` — required exact/approximate input is unavailable or invalid;
- `ANALYSIS_FAILURE` — downstream solver fails under the declared contract.

`REJECTED` is not a codec failure. `INPUT_FAILURE` is not converted to `REJECTED` for scientific analysis, although conservative archive-level accounting may count failures against an adoption criterion when predeclared.

## 8. Certificate payload

A future certifying writer should record at minimum:

- contract hash;
- QoI and algorithm identifier;
- (	au);
- roles and hashes of reference inputs;
- perturbation scale(s);
- seed list;
- number of probes actually evaluated;
- early-stop seed if rejected;
- eligibility state;
- selected codec and operating point if qualified;
- verified downstream error;
- compressed bytes / compression ratio;
- provenance commit.

The certificate should be sufficient to reconstruct *what was qualified*, not only *what codec was used*.

## 9. Scientific interpretation lock

Contract-aware QSQ changes the object being qualified from “a material” to “a declared material–QoI–algorithm–input-handling contract”.

It must not be interpreted as:
- a universal material-stability label;
- a codec-specific admission rule;
- a worst-case guarantee over all perturbations;
- evidence that an exact auxiliary reference is always necessary;
- permission to change reference semantics solely to improve eligibility.

The deployment contract is chosen for scientific reasons first; QSQ then measures its numerical stability.
