# QOAC-B2 — projection-aware Bader compression

Freeze date: 2026-10-05

Status: second engineering iteration, designed after the QOAC-B1 12-material engineering result and before any execution on the frozen 38-material holdout.

The 38 holdout materials remain untouched.

## Why B2 exists

QOAC-B1 established two facts under exact AECCAR partitioning:

1. a basin-sum projection can drive the actual Henkelman Bader charge error to numerical zero with zero basin reassignment;
2. explicitly transforming CHGCAR into per-basin means plus a zero-sum residual makes the field substantially harder to compress.

Therefore B2 discards the residual transform and retains only the scientifically useful operation:

    generic CHGCAR compression
      -> decode
      -> minimum-disturbance fixed-basin projection
      -> actual Bader certification.

## Fixed-partition constraint

Let Omega_i be an exact-reference partition region with N_i voxels. If the decoded field has a discrete region-sum error

    Delta_i = S_i^ref - S_i^dec,

B2 applies the uniform correction

    c_j = Delta_i / N_i,    j in Omega_i.

The corrected field satisfies the exact discrete region-sum constraint.

### Optimality of the uniform projection

For any correction vector c on a basin satisfying

    sum_j c_j = Delta_i,

the triangle inequality gives

    |Delta_i| <= N_i ||c||_inf,

so

    ||c||_inf >= |Delta_i| / N_i.

The uniform correction reaches equality.

Likewise, Cauchy-Schwarz gives

    Delta_i^2 <= N_i ||c||_2^2,

so

    ||c||_2 >= |Delta_i| / sqrt(N_i),

and the same uniform correction reaches equality.

Thus the fixed-basin uniform projection is simultaneously a minimum-Linf and minimum-L2 correction among all unconstrained corrections that restore the region sum.

This result does not claim topology preservation when the partition-defining reference is compressed; AECCAR remains exact in B2.

## Development-selected auxiliary density contract

A Bader-only contract would be degenerate: the field could be compressed arbitrarily and then projected to reproduce the basin sums while becoming scientifically useless for other purposes.

B2 therefore introduces an explicit auxiliary raw-density budget relative to the best frozen generic Bader-certified baseline.

For material m at the primary Bader tolerance tau_B = 1e-3 e, let

    epsilon_m^G1

be the realized CHGCAR Linf of the highest-compression frozen G1 row satisfying the Bader contract.

For a projected candidate P, require

    Linf(P) <= kappa * epsilon_m^G1.

The frozen frontier is

    kappa in {1, 2, 4, 8, 16}.

The engineering data from B1 were used to select **kappa = 4** as the primary B2 operating point because it is the smallest power-of-two frontier point at which the development panel shows broad competitive gain while retaining an explicit bounded raw-field degradation. This selection is a development decision, not a confirmatory result.

All five kappa values remain visible in reporting.

## Candidate search

For each material and kappa:

1. take every successful frozen WP-G G1 codec/tolerance row;
2. reproduce the same codec/tolerance on the original CHGCAR;
3. apply the exact-reference basin projection;
4. include the complete region-sum side channel in serialized bytes;
5. retain candidates with
       final_Linf <= kappa * epsilon_m^G1
   and fixed-basin closure <= 1e-9 on the scaled region-sum metric;
6. choose the candidate with maximum total compression ratio.

No new codec tolerance may be inserted between the frozen WP-G ladder points.

## Primary engineering verification

Population: the same 12 QOAC-B1 engineering materials.

For every selected candidate at kappa in {1,2,4,8,16}:
- reconstruct from the original CHGCAR;
- apply projection;
- run Henkelman Bader with the exact AECCAR reference;
- report max atomic-charge error and reassignment fraction.

### Engineering Gate A — scientific closure

At kappa = 4:
- 12/12 candidates must have actual Bader error <= 2e-6 e;
- 12/12 must have zero basin reassignment;
- 12/12 must satisfy the discrete region-sum closure threshold.

### Engineering Gate B — useful rate gain

At kappa = 4:

    R_CR = CR_B2 / CR_best_G1.

GO requires:
- at least 9/12 materials with R_CR > 1;
- median R_CR > 1.50.

### Engineering Gate C — side-channel practicality

At kappa = 4:
- side-channel bytes / total B2 bytes < 1% for all 12 materials.

The frozen holdout is authorized only if Gates A, B and C pass.

## Frozen holdout confirmation protocol

The 38 materials already frozen by QOAC-B1 remain the confirmatory population.

No holdout material may be executed before engineering authorization.

If authorized, each holdout material is evaluated only with:
- exact AECCAR reference;
- tau_B = 1e-3 e;
- primary kappa = 4;
- the pre-existing WP-G codec/tolerance ladder;
- the same projection and byte accounting.

Confirmatory success requires all of:

1. 38/38 materials analyzable with zero pipeline failures;
2. 38/38 selected candidates have actual Bader error <= 2e-6 e;
3. 38/38 have zero basin reassignment;
4. at least 30/38 have CR_B2 / CR_best_G1 > 1;
5. median CR_B2 / CR_best_G1 > 1.30;
6. fixed-seed nonparametric bootstrap 95% CI lower bound for the median ratio > 1.10;
7. side-channel fraction < 1% for all 38.

These holdout criteria are frozen before holdout execution.

## Secondary outputs

Report the complete development frontier over kappa = 1,2,4,8,16:
- win count;
- median, minimum and maximum CR ratio;
- median absolute B2 CR;
- median Linf ratio;
- Bader error and reassignment;
- side-channel fraction.

Also report density RMSE and mean-density deviation, but they are descriptive rather than optimization constraints in B2.

## Interpretation boundary

A successful B2 result would support:

> Under an exact and stable Bader partition, generic lossy compression can be followed by an optimal fixed-basin constraint projection that preserves Bader charge while permitting an explicit, controlled trade-off between raw-density fidelity and compression rate.

It would not support:
- compressed-AECCAR topology preservation;
- universal reuse of the projected CHGCAR for arbitrary downstream QoIs;
- an unbounded Bader-only compression claim.

Compression of the partition-defining field remains a separate QOAC-B3 problem.
