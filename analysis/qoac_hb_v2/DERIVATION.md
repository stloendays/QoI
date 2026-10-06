# Hartree-aware basin projection (HAP) — derivation

## Problem

Decoded field x on a periodic grid of N points; integer labels tiling the grid into regions 0..L (Bader
basins of the exact AECCAR partition); target region sums t (the QOAC-B1 side channel). A is the
(L+1) x N indicator matrix, (A c)_i = sum_{r in i} c(r), and d = t - A x. For mu > 0 find

    c* = argmin_c  J(c),   J(c) = ||H c||^2 / s_H + mu ||c||^2 / s_rho,   subject to A c = d,

with s_H = ||H rho_ref||^2, s_rho = ||rho_ref||^2 (real-space grid sums, so the first term is the squared
historical Hartree relative RMSE of the correction) and y = x + c*.

## H as a Fourier multiplier

The historical operator (`codec_qoac_h_v02.hartree_potential_from_field(..., safe=False)`) is
`irfftn(m_half * rfftn(x))`, m_half(G) = 4 pi / |G|^2 for |G|^2 > 0 and 0 at G = 0; the x/y Nyquist indices
use the fftfreq sign (-n/2). On the kz = 0 and kz = Nyquist planes the half-grid multiplier is not even
under G -> -G in non-orthogonal cells (the Nyquist sign choice changes the cross terms), and irfftn keeps
only the Hermitian part of the product there. The effective operator is therefore the real, even multiplier

    m(G) = (m_half(G) + m_half(-G)) / 2   on kz in {0, Nyquist},    m(G) = m_half(G)   elsewhere,

so H is real-symmetric and diagonal in Fourier space, H^T H = F^-1 diag(m^2) F. The unit test checks that
`irfftn(m * rfftn(x))` reproduces the canonical function to 1e-12 on triclinic and hexagonal cells with
even and odd grid dimensions, and that <Hu, v> = <u, Hv>.

## KKT system

    M = H^T H / s_H + mu I / s_rho,     M(G) = m(G)^2 / s_H + mu / s_rho,     M(0) = mu / s_rho.

The Lagrangian c^T M c - 2 lambda^T (A c - d) gives

    c = M^{-1} A^T lambda,     (A M^{-1} A^T) lambda = d.

With B_j = M^{-1} 1_j the Gram matrix is G_ij = 1_i^T B_j = sum_{r in i} B_j(r), and c = sum_j lambda_j B_j.
Scaling M by a positive constant leaves c unchanged, so the code uses M' = s_H M = H^T H + kappa I with

    kappa = mu s_H / s_rho.

kappa is the only scalar the decoder needs besides the labels and t; it is stored as 8 bytes after the
QOAC-B1 side channel.

## Explicit treatment of G = 0

The regions tile the grid, so 1^T A = 1_N^T and summing the constraints gives N c_0 = sum_i d_i, where
c_0 = mean(c). Write c = c_0 1 + c_perp with mean(c_perp) = 0. Since M is diagonal in Fourier space, the
constant mode and the zero-mean subspace do not couple:

    J = kappa' N c_0^2 + c_perp^T M c_perp      (kappa' = mu / s_rho).

c_0 is fixed by the constraints, independently of M(0), and c_perp solves

    min c_perp^T M c_perp   s.t.  A c_perp = d_perp = d - c_0 n,   P c_perp = c_perp,

with n the region counts and P the zero-mean projector. Its solution is

    c_perp = P M^{-1} P A^T lambda,     G_perp lambda = d_perp,     G_perp = A P M^{-1} P A^T.

Applying P M^{-1} P is the Fourier division with the G = 0 entry of 1/M set to zero. G_perp is positive
semidefinite with null space spanned by the all-ones region vector (P A^T 1 = P 1_N = 0), and 1^T d_perp = 0.
We solve

    (G_perp + gamma 1 1^T) lambda = d_perp,     gamma = mean diag(G_perp),

which is positive definite. Left-multiplying by 1^T gives gamma (L+1) 1^T lambda = 1^T d_perp = 0, so
the solution satisfies G_perp lambda = d_perp. The system is Jacobi-scaled and Cholesky-factored once.

This is the same minimizer as the literal Gram A M^{-1} A^T, which contains the rank-one term
(s_rho / mu) n n^T / N from M(0) and loses accuracy as mu -> 0. The split removes that term. It also
defines the mu -> 0 limit: the minimum-Hartree-norm correction, since M'(G != 0) >= min m^2 > 0. A test
checks the split against the literal Gram, and the runner reports the 2-norm condition number of the scaled
regularized Gram for each mu.

## Algorithm

Precompute per (material partition, kappa), shared across kappas:
1. for each populated region j: F_j = rfftn(1_j); for each kappa: B_j = irfftn(F_j / (m^2 + kappa)) with the
   G = 0 entry zeroed; column j of G_perp = bincount(labels, B_j);
2. symmetrize, regularize, Jacobi-scale, Cholesky.

The B_j are not stored: c only needs M^{-1} applied once to the piecewise-constant field lambda[labels].

Per decoded candidate:
1. d = t - region_sums(x); c_0 = sum d / N; d_perp = d - c_0 n;
2. lambda from the Cholesky factor;
3. c = irfftn(rfftn(lambda[labels]) / (m^2 + kappa), G = 0 -> 0) + c_0;
4. y = project_to_region_sums(x + c, labels, t): one uniform pass that removes floating-point closure
   residual. It changes c by O(eps) per region and does not alter the solution.

Unpopulated regions are excluded, as in `project_to_region_sums`.

## Limits and checks (unit tests, `test_projection_v2.py`)

- mu -> infinity: M -> (mu / s_rho) I, c -> A^T (A A^T)^{-1} d = d_i / N_i on region i, the uniform B2 correction.
- Optimality: the uniform correction is feasible, so J(c_HAP) <= J(c_uniform) for every mu. The uniform
  correction is the minimum-L2 feasible correction, so ||c_HAP|| >= ||c_uniform||, and therefore
  ||H c_HAP||^2 <= ||H c_uniform||^2 for every mu.
- Dense check: on 4x5x6 and 5x4x4 grids, H is built column by column from the canonical Hartree function.
  The full KKT system [[2M, A^T], [A, 0]] is solved with numpy.linalg and agrees with HAP to 1e-9 relative.

## CTP

Certify-then-project stores a one-byte flag. The encoder runs Bader on the unprojected stream. If that
stream meets the Bader contract (error <= tau_B, zero reassignment), it is stored as is. Otherwise the
projection (uniform or HAP) is applied and its side channel is stored after the flag.
