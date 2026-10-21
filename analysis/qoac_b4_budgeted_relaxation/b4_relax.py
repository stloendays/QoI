#!/usr/bin/env python3
"""QOAC-B4: budgeted leaf relaxation of the QOAC-B3 partition-faithful correction.

QOAC-B3 (``analysis/qoac_b3_design``) escalates voxels until the decoded
partition field reproduces the reference Henkelman on-grid partition voxel for
voxel. Every reassignment is forbidden, including reassignments that move far
less charge than the Bader tolerance tau_B allows.

B4 keeps the B3 machinery (log-domain base quantizer, refinement ladder, side
information coder) and adds one idea: a set R of *relaxed* voxels that are
allowed to change basin, chosen so that the resulting per-atom charge change is
bounded a priori by ``theta * tau_B``. The guarantee does not depend on running
Bader on the decoded field; the actual Bader run is still done and reported.

Construction (see PROTOCOL.md section 2 for the argument):

* Only reference *leaves* (voxels that are nobody's reference successor) and
  non-maxima, non-vacuum voxels are eligible for R.
* Constrained voxels p not in R must satisfy B3 tier B plus one extra rule: the
  decoded successor is not in R.
* Relaxed voxels p in R must not become stationary, must not step into R and
  must not step into vacuum.
* Vacuum mask and every reference maximum are kept exactly as in B3.

Then every constrained voxel keeps its reference label (B3 Theorem 1 restricted
to chains that never enter R), and a relaxed voxel takes the label of one of
its 26 neighbours. The charge of atom a can therefore change by at most

    B_a = sum_{p in R, atom(p) = a, p touches another atom} |c_p|
        + sum_{p in R, atom(p) != a, a in atoms(N(p))}    |c_p|

where c_p is the charge carried by voxel p (CHGCAR / npoints). R is grown
greedily (smallest |c_p| first) only while every B_a <= theta * tau_B.

When every voxel is exact, g == f, nobody points into R (leaves) and every
relaxed voxel steps to its reference successor, which is not a leaf, not
vacuum (regular reference) and not itself. So the loop terminates, exactly as
B3's does.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qoac_b3_design"))

from b3_correct import (EXACT, Reference, check_constraints, level_value,  # noqa: E402
                        quantize, side_info_size)
from ongrid import successor, vacuum_mask, weighted_candidates  # noqa: E402

RELAXED_LABEL = -7  # sentinel: never a real volnum label (labels are >= 1)


# --------------------------------------------------------------------------
# Budget bookkeeping
# --------------------------------------------------------------------------

@dataclass
class Budget:
    """Per-atom a-priori charge-change bound for a relaxed set."""
    atom: np.ndarray          # flat per-voxel atom index (reference), vacuum = natoms+1
    charge: np.ndarray        # flat |c_p| in electrons
    limit: float              # theta * tau_B (electrons)
    bound: np.ndarray         # running B_a, index = atom label
    nbr_atoms: dict           # voxel -> tuple of distinct neighbour atoms != own (cached)

    @classmethod
    def make(cls, atom_flat, charge_flat, limit, natoms):
        return cls(np.asarray(atom_flat, dtype=np.int64), np.abs(np.asarray(charge_flat, float)),
                   float(limit), np.zeros(natoms + 2), {})

    def others(self, p: int, st) -> tuple:
        if p not in self.nbr_atoms:
            a = self.atom[p]
            nb = np.unique(self.atom[st.nbr[:, p]])
            vac = self.bound.size - 1          # vacuum atom label (natoms+1): never a target
            self.nbr_atoms[p] = tuple(int(x) for x in nb if x != a and 0 < x < vac)
        return self.nbr_atoms[p]

    def try_add(self, p: int, st) -> bool:
        """Add voxel p to the relaxed set if every atom bound stays <= limit."""
        oth = self.others(p, st)
        if not oth:
            return True                       # cannot change atom at all: free
        c = self.charge[p]
        touched = (int(self.atom[p]),) + oth
        if any(self.bound[a] + c > self.limit for a in touched):
            return False
        for a in touched:
            self.bound[a] += c
        return True

    def max_bound(self, natoms: int) -> float:
        return float(self.bound[1:natoms + 1].max(initial=0.0))


def reference_leaves(ref: Reference) -> np.ndarray:
    """Flat bool: voxels that are no voxel's reference successor."""
    has_pred = np.zeros(ref.f.size, dtype=bool)
    s = ref.part.succ
    moving = s != np.arange(s.size)
    has_pred[s[moving]] = True
    return ~has_pred


# --------------------------------------------------------------------------
# Constraint check with a relaxed set
# --------------------------------------------------------------------------

@dataclass
class RelaxCheck:
    ok: bool
    vac: np.ndarray
    nonmax: np.ndarray        # violations of constrained voxels (incl. "points into R")
    relaxed: np.ndarray       # violations of relaxed voxels
    maxima: np.ndarray
    wrong_succ: np.ndarray
    counts: dict


def check_relaxed(g, ref: Reference, R: np.ndarray, margin: float = 0.0,
                  vac_margin: float = 0.0, exact: np.ndarray | None = None) -> RelaxCheck:
    g = np.ascontiguousarray(g, dtype=np.float64).ravel()
    if exact is None:
        exact = g == ref.f
    if R.any():
        lab2 = ref.lab.copy()
        lab2[R] = RELAXED_LABEL
        ref2 = replace(ref, lab=lab2)
    else:
        ref2 = ref
    base = check_constraints(g, ref2, "B", margin, vac_margin, exact)
    nonmax = base.nonmax & ~R
    vac_f = ref.lab == ref.part.nbasins + 1
    sg = base.wrong_succ
    idx = np.arange(g.size)
    rel = R & ~vac_f
    bad_rel = rel & ((sg == idx) | R[sg] | vac_f[sg])
    if margin > 0 and rel.any():
        st = ref.st
        p = np.flatnonzero(rel)
        stencil_exact = exact[p] & np.all(exact[st.nbr[:, p]], axis=0)
        T = weighted_candidates(g.reshape(ref.shape), st)[:, p]
        nb = st.nbr[:, p]
        allowed = ~(R[nb] | vac_f[nb])
        best_ok = np.where(allowed, T, -np.inf).max(axis=0)
        best_no = np.where(~allowed, T, -np.inf).max(axis=0)
        gap = best_ok - np.maximum(g[p], best_no)
        bad_rel[p[(gap < margin) & ~stencil_exact]] = True
    ok = not (base.vac.any() or nonmax.any() or base.maxima.any() or bad_rel.any())
    counts = {"vac": int(base.vac.sum()), "nonmax": int(nonmax.sum()),
              "relaxed": int(bad_rel.sum()), "maxima": int(base.maxima.sum())}
    return RelaxCheck(ok, base.vac, nonmax, bad_rel, base.maxima, sg, counts)


# --------------------------------------------------------------------------
# Correction loop
# --------------------------------------------------------------------------

@dataclass
class B4Result:
    g: np.ndarray
    level: np.ndarray
    relaxed: np.ndarray
    iterations: int
    history: list
    side_bits: int
    side_bytes: int
    n_edits: int
    n_relaxed: int
    edits_by_level: dict
    max_atom_bound_e: float


def correct_budgeted(ref: Reference, eps, budget: Budget, natoms: int, margin: float = 0.0,
                     vac_margin: float = 0.0, g0: np.ndarray | None = None,
                     max_iter: int = 10_000) -> B4Result:
    """B3's escalation loop, except that a violating eligible leaf is first
    offered to the relaxed set (free) and only escalated if the budget refuses."""
    f = ref.f
    st = ref.st
    if g0 is None:
        _, g0 = quantize(f, eps)
    g0 = np.ascontiguousarray(g0, dtype=np.float64).ravel()
    if np.ndim(eps):
        eps = np.ascontiguousarray(eps, dtype=np.float64).ravel()
    eligible = reference_leaves(ref) & ~ref.is_fmax & (ref.lab != ref.part.nbasins + 1)
    R = np.zeros(f.size, dtype=bool)
    refused = np.zeros(f.size, dtype=bool)
    level = np.zeros(f.size, dtype=np.int64)
    g = level_value(f, g0, eps, level)
    history = []
    it = 0
    while it < max_iter:
        exact = level >= EXACT
        chk = check_relaxed(g, ref, R, margin, vac_margin, exact | (g == f))
        history.append({**chk.counts, "R": int(R.sum())})
        if chk.ok:
            break
        it += 1
        # 1) offer violating eligible leaves to R, cheapest first
        bad = np.flatnonzero(chk.nonmax)
        cand = bad[eligible[bad] & ~R[bad] & ~refused[bad]]
        newly = np.zeros(f.size, dtype=bool)
        for p in cand[np.argsort(budget.charge[cand], kind="stable")]:
            if budget.try_add(int(p), st):
                R[p] = True
                newly[p] = True
            else:
                refused[p] = True
        # 2) escalate everything still violating (as in B3)
        cul = np.zeros(f.size, dtype=bool)
        cul[chk.vac] = True
        still = bad[~newly[bad]]
        cul[still] = True
        cul[ref.part.succ[still]] = True
        cul[chk.wrong_succ[still]] = True
        rb = np.flatnonzero(chk.relaxed)
        cul[rb] = True
        cul[ref.part.succ[rb]] = True
        cul[chk.wrong_succ[rb]] = True
        if margin > 0 and (still.size or rb.size):
            pp = np.concatenate([still, rb])
            T = weighted_candidates(g.reshape(ref.shape), st)[:, pp]
            nb = st.nbr[:, pp]
            forbidden = (ref.lab[nb] != ref.lab[pp][None, :]) | R[nb]
            k = np.argmax(np.where(forbidden, T, -np.inf), axis=0)
            has = forbidden.any(axis=0)
            cul[nb[k[has], np.flatnonzero(has)]] = True
        mx = np.flatnonzero(chk.maxima)
        if mx.size:
            cul[mx] = True
            nbm = st.nbr[:, mx]
            thr = g[mx] - max(margin, 0.0)
            cul[nbm[g[nbm] >= thr[None, :]]] = True
        stuck = cul & (level >= EXACT)
        if stuck.any():
            viol = np.flatnonzero(chk.nonmax | chk.relaxed | chk.maxima)
            allx = np.all(level[st.nbr[:, viol]] >= EXACT, axis=0) & (level[viol] >= EXACT)
            for p in viol[~allx]:
                cul[st.nbr[:, p]] = True
        cul &= level < EXACT
        if not cul.any() and not newly.any():
            raise RuntimeError("B4 correction stalled: reference irregular or margin infeasible")
        level[cul] += 1
        g = level_value(f, g0, eps, level)
    else:
        raise RuntimeError("max_iter reached")
    bits, nbytes = side_info_size(level, g.size)
    edits = {int(k): int((level == k).sum()) for k in range(1, EXACT + 1) if (level == k).any()}
    return B4Result(g.reshape(ref.shape), level.reshape(ref.shape), R.reshape(ref.shape), it, history,
                    bits, nbytes, int((level > 0).sum()), int(R.sum()), edits, budget.max_bound(natoms))


# --------------------------------------------------------------------------
# Python-side verification (independent of the Fortran binary)
# --------------------------------------------------------------------------

def atom_charges(charge_flat, atom_flat, natoms: int) -> np.ndarray:
    s = np.bincount(np.asarray(atom_flat).ravel(), weights=np.asarray(charge_flat).ravel(),
                    minlength=natoms + 2)
    return s[1:natoms + 1]


def remap_volnum(dec_part, ref_part) -> np.ndarray:
    """Relabel a decoded volnum map with the reference basin numbers.

    Basin numbers are assigned in scan order of the first voxel that reaches a
    maximum, so moving a relaxed voxel with a small scan index can permute the
    numbering even though every basin keeps its maximum. Labels are therefore
    compared by maximum identity. Decoded basins whose maximum is not a
    reference maximum map to -1."""
    lut = {int(m): i + 1 for i, m in enumerate(ref_part.maxima)}
    remap = np.array([0] + [lut.get(int(m), -1) for m in dec_part.maxima] + [ref_part.nbasins + 1])
    return remap[np.asarray(dec_part.volnum).ravel()]


def changed_only_in_R(dec_lab, ref_lab, R) -> bool:
    """dec_lab must already be in reference numbering (see remap_volnum), or be
    an atom map, whose numbering does not depend on scan order."""
    diff = np.asarray(dec_lab).ravel() != np.asarray(ref_lab).ravel()
    return bool(not np.any(diff & ~np.asarray(R).ravel()))


__all__ = ["Budget", "B4Result", "RelaxCheck", "atom_charges", "changed_only_in_R",
           "check_relaxed", "correct_budgeted", "reference_leaves", "vacuum_mask", "successor"]
