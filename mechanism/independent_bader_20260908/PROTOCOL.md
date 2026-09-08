# Independent Bader and error-organization supplement, 2026-09-08

This is a new, exploratory mechanism study authorized by the user on 2026-09-08.
It neither changes nor contributes rows to the frozen external confirmatory
validation at scientific commit 893f931b3045b0b628329db81999c2f439d4e830.
No new DFT, external-corpus selection, codec development, or threshold retuning.

## Questions and panel

Q1: Is perturbation sensitivity specific to BaderKit ongrid or reproduced by
the independent Henkelman Bader 1.05 executable, in ongrid and neargrid modes?
Q2: Does rearranging an otherwise identical error-value multiset change Bader
charge response? Which integrand/domain-migration terms change?

Select two lowest, two central, and two highest A.1 floors separately among
development bulk and slab, sorted by (floor, material_id): 12 representatives.
Add mp-1007755 as a separately labelled known probe-failure sentinel. Exclude
the sentinel from representative-panel aggregate estimates. The selection and
existing source provenance are in panel.json. No external recovery materials
are used. These samples characterize mechanisms, not population prevalence.

## Analysis implementations and reference contract

1. BaderKit 0.10.2 ongrid, vacuum_tol=0.001 e/A^3, persistence_tol=0.5,
   nna_cutoff=False; charge, reference and total grids all the supplied field.
2. Henkelman Bader 1.05 `-b ongrid -vac 0.001`.
3. Henkelman Bader 1.05 `-b neargrid -vac 0.001`.

Henkelman does not implement BaderKit persistence merging. Therefore this is
an implementation/method sensitivity study, not a claim of identical algorithms.
All read the same valence-density field and lattice, without AECCAR substitution.
Write CHGCAR density values with 17 significant digits, Fortran grid ordering,
unchanged coordinates and atom order. Verify the serialized field roundtrip on
the pilot compute job before accepting inter-implementation differences.
ACF charges have finite printed precision; allow 2e-6 e numerical accounting
per atom. Tau decisions within 2e-6 e of a boundary are labelled ambiguous.
Each implementation compares perturbations against its OWN unperturbed output.
Report absolute baseline disagreement separately. Do not declare a continuous
physical Bader charge undefined on the basis of an implementation difference.

## Input perturbations, fixed before running

Stability: float32 roundtrip; uniform noise at the measured float32 L-infinity
amplitude with seeds [20260905,1,2,3,4]. Same field for each implementation.
Compression: ZFP/SZ3/SPERR at relative requested bounds 1e-4 and 1e-3, with the
same codec configuration and pinned packages as external validation.
Spatial controls only at relative 1e-4, for each codec and seeds [1701,1702,1703]:
- Global permutation of error values: preserves all error-value statistics;
  may relocate errors between physical regions, so is a stress control.
- Periodic three-axis translation of the error field: preserves its distribution
  and periodic autocorrelation, changes alignment with the unmodified density.
- Permutation within 16 equal-width bins in log10(original positive density),
  with a separate nonpositive bin: preserves global multiset and coarse density
  localization, disrupts fine spatial organization.
No clipping, positivity correction, density smoothing, grid resizing, or deletion
of failed variants. Record negative-density fractions and vacuum-region error.
Controls preserve the requested delta multiset; addition to the original density
can introduce floating-point roundoff, which is measured and reported.
Compression ratio belongs ONLY to actual codec roundtrips, not synthetic controls.

## Outputs and interpretation

Append one JSONL outcome per (material, perturbation, implementation), including
solver failures. Include per-atom original/reconstructed charge, max error,
timing, electron accounting, original implementation disagreement, A.1-like
five-seed response maximum, and tau=1e-4/1e-3/1e-2 verdicts for each implementation.
For BaderKit retain exact per-atom integrand + domain = total decomposition,
fraction of reassigned voxels, source-density-weighted migration, local-order
flips including periodic edges, error RMS/bias and axis correlations.
Aggregate spatial-control effects first over seeds per material/codec, then over
materials; show paired values and heterogeneity, not just a pooled significance.
Controls establishing an effect support sensitivity to error organization under
that transformation, not a unique proof of boundary-local causation.

## Execution and resource policy

Use Vanda/PBS group CFP03-CF-126 only, never personal allocation. First a two-case
input/solver pilot on one 36-core node, max wall 2h (72 allocated core-hours).
After numerical input/solver verification, use a single 36-core node with max
wall 48h (1728 allocated core-hours), 250GB RAM, independent material workers.
Keep one thread per material worker initially; this is numerical CPU Bader work,
not GPU-suitable training. Checkpoint each completed output row. A PBS walltime
interruption is incomplete work, not a solver failure or success. No automatic
second production allocation before reviewing actual use and remaining cases.
Archive logs, version output, PBS accounting, panel, code and small outputs.
Temporary input/rendered fields stay in dedicated scratch staging only.

## Input compatibility amendment, before production

Pilot 1356147 showed successful BaderKit fields but Henkelman binary exit 64
while parsing the high-precision geometry header. The official Henkelman source
at https://github.com/henkelmangroup/bader commit
3e739502ba086d4f1977e9a6245ec2a69a9bc86a uses fixed-width F13.6 lattice and
F10.6 coordinates. To retain identical full-precision geometry, build its 1.05
source with GCC 13.3.0 and change ONLY scale/lattice/coordinate READ statements
in chgcar_mod.f90 to free-format reads. No Bader, vacuum, assignment, refinement,
or integration code is modified. The patch is retained under reference_source.
Label these results Henkelman 1.05 with input-format adapter, not unmodified
binary runs. Before accepting the new pilot, compare both executables on the
same legacy six-decimal geometry and full-precision density, in both ongrid and
neargrid modes, requiring per-atom charge agreement within 2e-6 e. Production
uses the full-precision header and must still pass the exact input roundtrip.
Keep the failed pilot as results/pilot_attempt2. The first failed initialization
and both input-adapter pilots are reported separately in resource accounting.
