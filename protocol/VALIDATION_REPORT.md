# Validation report — what may and may not be called external

Date: 2026-09-04.

## 1. Audit of the development corpora

Both existing corpora are **disqualified** from being described as an external
test. Each was used for hypothesis generation, metric debugging, algorithm
development and parameter selection. The scripts that consumed them are listed
below as the audit trail.

### Materials Project bulk, n = 186

Used by 18 scripts, including:

| Purpose | Scripts |
|---|---|
| hypothesis generation | `stage0_corpus.py`, `stage0_composition.py`, `vacuum_analysis.py` |
| metric debugging | `verify_primary_claim.py`, `diag_bias.py`, `diag_bit_vs_chemistry.py`, `diag_boundary.py` |
| algorithm development | `gate_g0c_promolecule.py`, `stage1_sz3.py`, `stage1_ratefidelity.py` |
| parameter selection | `stage1_sz3.py` (reserve fractions, tolerance ladders), `population_weighted.py` |
| current evidence chain | `stability_floor.py`, `honest_benchmark.py`, `lossless_baseline.py` |

### NOMAD slabs, n = 68

Used by 12 scripts, including `slab_experiment.py`, `bias_experiment.py`,
`boundary_experiment.py`, `audit_circularity.py`, `diag_boundary.py`.

The 68 systems come from five NOMAD uploads:

| upload | n | description |
|---|---:|---|
| `9kY9WrfNTLm0zUauVB-cjQ` | 14 | Cl on Ti, several facets and adsorption sites |
| `iX4CUI7eR3CwsuDltNempA` | 14 | clean and O-covered Co(0001), Cr(110), Fe |
| `reTvTXQBTiSwmntKl7EmAQ` | 14 | GaN electrochemical surfaces, with AECCARs |
| `qM7AMKciQ7GRVR8rCNm0mw` | 14 | RuO2 CO2RR, adsorbate and spectator variations |
| `2gWjvlhHTEqE85zHVCPFkw` | 12 | clean fcc metal surfaces |

**Verdict: neither corpus is external. Results measured on them are
development results and must be labelled as such.**

## 2. The strict external test corpus

Option A of the directive is achievable: a genuinely untouched public corpus
exists, covering both regimes.

| Source | Regime | Why it is independent |
|---|---|---|
| **AFLOW `ICSD_WEB`** | bulk | A different DFT pipeline, not merely a different sample of the same one: different code settings and pseudopotentials from Materials Project. Tests the claim against an independent calculation chain. |
| **NOMAD `structural_type=2D`** | vacuum-containing | Real vacuum gaps and near-P1 symmetry, so the same physics as slabs. No 2D entry was touched: the slab corpus came from the five surface uploads above, none of which is a 2D entry. |

Frozen at `data/external_test/MANIFEST.json` with URL, byte count and SHA-256
for every file. Target size 40 bulk + 30 2D.

**Once frozen this corpus may not be used to select or tune any parameter.** It
is scored once, under `results/stability/FROZEN_PROTOCOL.md`.

### Two parsing hazards handled, not guessed around

- **AFLOW CHGCARs are pre-VASP5 and carry no species line at all.** Parsing
  alone yields placeholder element names and silently wrong chemistry, which
  would corrupt every Bader charge. Species come from the AFLUX API, and a
  material is **skipped** unless the API composition reproduces the file's own
  atom counts exactly. No element assignment is inferred.
- **The `structural_type=2D` label is not evidence of a vacuum gap.** One
  candidate had a 3.7 Å c-axis and no vacuum. The regime is defined by the
  vacuum, so the vacuum fraction is measured and a minimum of 15 % is required.

## 3. The question this corpus is for

> **Does the bulk-stable / slab-unstable Bader stability behaviour reproduce on
> data untouched by development?**

On the development corpora the non-evaluable rate under Protocol A is:

| threshold | bulk | slab |
|---|---:|---:|
| 1e-4 e | 16.7 % | 38.2 % |
| 1e-3 e | 4.3 % | 14.7 % |
| 1e-2 e | 0.5 % | 2.9 % |

If the external corpus reproduces a comparable ordering — vacuum-containing
systems non-evaluable at roughly two to three times the bulk rate — the
methodological claim generalises beyond this project's data and beyond one DFT
pipeline. If it does not, the claim is specific to the development corpora and
must be stated that way.

## 4. Result: the bulk/slab split does NOT reproduce

Frozen corpus: 65 systems, 37 AFLOW bulk and 28 NOMAD 2D (vacuum fraction median
36 %, range 16-70 %), every file with a SHA-256. Stability floors measured under
the frozen protocol, once.

### Stability floor

| Stratum | n | median | p90 | max |
|---|---:|---:|---:|---:|
| development bulk (MP) | 186 | 6.38e-09 | 3.17e-04 | 2.14e-02 |
| development slab (NOMAD surfaces) | 68 | 1.85e-05 | 1.68e-03 | 1.11e-02 |
| **external bulk (AFLOW)** | 37 | 7.00e-09 | **6.54e-03** | **9.93e-02** |
| **external vacuum (NOMAD 2D)** | 28 | 4.47e-09 | 3.53e-04 | 5.00e-04 |

### Non-evaluable rate

| threshold | dev bulk | dev slab | ext bulk | ext vacuum | dev slab/bulk | ext vacuum/bulk |
|---|---:|---:|---:|---:|---:|---:|
| 1e-4 | 16.7 % | 38.2 % | 27.0 % | 25.0 % | 2.3x | **0.9x** |
| 1e-3 | 4.3 % | 14.7 % | 13.5 % | 0.0 % | 3.4x | **0.0x** |
| 1e-2 | 0.5 % | 2.9 % | 10.8 % | 0.0 % | 5.5x | **0.0x** |

Rank-based effect size, P(vacuum-regime floor > bulk floor):
**development 0.672, external 0.419** — the direction reverses.

### Verdict

**The claim "Bader instability is markedly more common for slabs than for bulk"
does not generalise.** On untouched data the vacuum-containing systems are the
*more* stable stratum, and the external bulk set is markedly *less* stable than
the development bulk set (10.8 % non-evaluable at 1e-2 against 0.5 %; max floor
9.93e-02 against 2.14e-02).

The development-corpus measurement stands as a measurement. What fails is the
generalisation: the split was a property of those particular NOMAD metal-slab
uploads, not of having a vacuum gap. NOMAD 2D systems have vacuum too — 36 %
median — and are stable.

### Is it grid resolution?

No. Across all 319 systems the correlation of `log10(floor)` with
`log10(points per Å³)` is **+0.136**, with `log10(points per atom)` **+0.197**,
with `log10(n atoms)` **+0.124**. AFLOW bulk has the coarsest grids of any
stratum (median 1809 points/Å³ against 4279 for MP bulk) yet the same median
floor; only its tail differs.

### What survives, and is stronger for it

Instability is **common** — 25-27 % of systems are non-evaluable at 1e-4 in
*every* stratum, including both external ones — and it is **not predictable from
any cheap proxy**: not system class, not vacuum content, not grid density, not
atom count. That is a stronger argument for the frozen protocol than the
bulk/slab story was, because it removes the tempting shortcut of qualifying a
QoI by inspection of the system type. It has to be measured per material.

## 5. Status

| Item | Status |
|---|---|
| Development-corpus audit | **COMPLETE** |
| External corpus frozen | **COMPLETE** (65 systems, SHA-256, `data/external_test/MANIFEST.json`) |
| External stability floors measured | **COMPLETE** |
| Reproduction verdict | **COMPLETE — does not reproduce** |
| External rate-fidelity benchmark | **PENDING** |

## 6. Restatement under Protocol A.1 (2026-09-05)

The float32 probe of Protocol A was found to be order-preserving and blind to
the watershed's tie resolution (`results/stability/PROTOCOL_A1.md`). Sections 3-4
above are retained as the archived Protocol A record and marked
**PROVISIONAL / archived**. Under A.1 (five pre-registered noise seeds, floor =
max over seeds), scored once on the same frozen corpus:

| threshold | dev bulk | dev slab | ext bulk | ext vacuum |
|---|---:|---:|---:|---:|
| 1e-4 | 77.4 % | 94.1 % | 73.0 % | 71.4 % |
| 1e-3 | 44.6 % | 41.2 % | 40.5 % | 21.4 % |
| 1e-2 | 9.7 % | 10.3 % | 16.2 % | 0.0 % |

Rank effect P(vacuum floor > bulk floor): development **0.564**, external
**0.382**. Grid proxies: r(log floor, log points/atom) = +0.08, r(log floor,
log atoms) = +0.17.

**Verdict unchanged**: the bulk/slab split does not generalise, and the
vacuum-containing external stratum is again the *more* stable one. The
verdict on claim 6 is the same under both probes; the magnitudes of claims 6b
and 7 are larger. Source: `results/stability/eligibility_summary_a1.csv`.
