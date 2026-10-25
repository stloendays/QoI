#!/usr/bin/env python3
"""Space-group symmetry of a density grid and its action on the Hermitian Fourier orbits of the v0.2 topology.

An operation is an index map n -> M n + T (mod N) of the grid. If rho(M n + T) = rho(n), the Fourier coefficients
(numpy forward convention, c(h) = sum_n rho(n) exp(-2 pi i sum_j h_j n_j / N_j)) satisfy

    c(h) = exp(2 pi i sum_j (h_j / N_j) (M^{-1} T)_j) * c(h'),   h'_j = sum_i h_i (M^{-1})_ij N_j / N_i  (mod N),

so every coefficient of a symmetry star is predicted from one representative. The encoder finds the operations from
the structure (spglib through pymatgen, symprec 1e-3), keeps those that map the grid onto itself and hold on the density
to OP_TOL x ptp in real space, closes them into a group (every element must hold as well; otherwise no symmetry is
used), and stores a greedy generating set. The decoder rebuilds the same sorted group from the generators.
"""
from __future__ import annotations

import numpy as np

OP_TOL = 1e-5          # max |rho(M n + T) - rho(n)| / ptp for an operation to be used
SYMPREC = 1e-3


def _key(op):
    M, T = op
    return tuple(int(v) for v in M.ravel()) + tuple(int(v) for v in T)


def compose(a, b, N):
    """a after b: n -> Ma (Mb n + Tb) + Ta."""
    Ma, Ta = a
    Mb, Tb = b
    return Ma @ Mb, (Ma @ Tb + Ta) % N


def closure(ops, N, limit=4096):
    N = np.asarray(N, dtype=np.int64)
    ident = (np.eye(3, dtype=np.int64), np.zeros(3, dtype=np.int64))
    group = {_key(ident): ident}
    frontier = [ident]
    gens = [(np.asarray(M, np.int64), np.asarray(T, np.int64) % N) for M, T in ops]
    while frontier:
        nxt = []
        for g in frontier:
            for h in gens:
                c = compose(h, g, N)
                k = _key(c)
                if k not in group:
                    group[k] = c
                    nxt.append(c)
                    if len(group) > limit:
                        raise RuntimeError("symmetry closure exceeds the limit")
        frontier = nxt
    return [group[k] for k in sorted(group)]


def generators(group, N):
    """Greedy generating set of a closed group, in its sorted order."""
    gens, have = [], {_key((np.eye(3, dtype=np.int64), np.zeros(3, dtype=np.int64)))}
    for g in group:
        if _key(g) in have:
            continue
        gens.append(g)
        have = {_key(x) for x in closure(gens, N)}
        if len(have) == len(group):
            break
    return gens


def _index_map(op, shape, idx=None):
    M, T = op
    N = np.asarray(shape, dtype=np.int64)
    if idx is None:
        idx = np.indices(shape, dtype=np.int64).reshape(3, -1)
    img = (M @ idx + T[:, None]) % N[:, None]
    return np.ravel_multi_index(img, shape)


def _reciprocal_ok(M, N):
    Minv = np.rint(np.linalg.inv(M.astype(float))).astype(np.int64)
    if not np.array_equal(M @ Minv, np.eye(3, dtype=np.int64)):
        return False
    K = Minv * N[None, :] / N[:, None]
    return bool(np.max(np.abs(K - np.rint(K))) < 1e-9)


def grid_group(structure, rho):
    """The closed group of grid operations that hold on rho, plus a status record."""
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    shape = rho.shape
    N = np.asarray(shape, dtype=np.int64)
    ptp = float(np.ptp(rho)) or 1.0
    flat = rho.ravel()
    grid_idx = np.indices(shape, dtype=np.int64).reshape(3, -1)

    def holds(op):
        return float(np.max(np.abs(flat[_index_map(op, shape, grid_idx)] - flat))) / ptp <= OP_TOL

    try:
        sg = SpacegroupAnalyzer(structure, symprec=SYMPREC)
        sgops = sg.get_symmetry_operations(cartesian=False)
        sginfo = f"{sg.get_space_group_symbol()} ({sg.get_space_group_number()})"
    except Exception as e:  # noqa: BLE001
        return closure([], N), {"status": f"spglib failed: {type(e).__name__}", "spacegroup": "", "ops": 1}
    acc = []
    for op in sgops:
        W = np.rint(op.rotation_matrix).astype(np.int64)
        Mf = W * N[:, None] / N[None, :]
        M = np.rint(Mf).astype(np.int64)
        Tf = np.asarray(op.translation_vector, float) * N
        T = np.rint(Tf).astype(np.int64) % N
        if np.max(np.abs(Mf - M)) > 1e-9 or np.max(np.abs(Tf - np.rint(Tf))) > 1e-6 or not _reciprocal_ok(M, N):
            continue
        if holds((M, T)):
            acc.append((M, T))
    group = closure(acc, N)
    if not all(_reciprocal_ok(M, N) and holds((M, T)) for M, T in group):
        return closure([], N), {"status": "closure fails on the density", "spacegroup": sginfo, "ops": 1}
    return group, {"status": "OK", "spacegroup": sginfo, "ops": len(group), "spglib_ops": len(sgops)}


def iter_relations(topo, group):
    """Per operation, in group order: image orbit position p, whether the image is the partner (conj), and the phase
    with c(h) = phase * c(p) (conj False) or phase * conj(c(p)) (conj True). Generated one operation at a time."""
    shape = topo.shape
    N = np.asarray(shape, dtype=np.int64)
    K = topo.rep_flat.size
    h = np.stack(np.unravel_index(topo.rep_flat, shape)).astype(np.int64)
    pos_of = np.full(int(np.prod(N)), -1, dtype=np.int64)
    pos_of[topo.rep_flat] = np.arange(K)
    ns = ~topo.self_conjugate
    pos_of[topo.partner_flat[ns]] = -2 - np.arange(K)[ns]          # partner of orbit k is stored as -2 - k
    hn = h / N[:, None]
    for M, T in group:
        Minv = np.rint(np.linalg.inv(M.astype(float))).astype(np.int64)
        Ki = np.rint(Minv * N[None, :] / N[:, None]).astype(np.int64)
        fl = np.ravel_multi_index((Ki.T @ h) % N[:, None], shape)
        p = pos_of[fl]
        conj = p < 0
        p = np.where(conj, -2 - p, p)
        if np.any(p < 0) or np.any(p >= K):
            raise RuntimeError("symmetry image outside the orbit table")
        ph = np.exp(2j * np.pi * (hn.T @ (Minv @ T)))
        yield p, conj, ph


def orbit_relations(topo, group):
    return list(iter_relations(topo, group))


class Plan:
    """Coding order (shell-major, then orbit position), symmetry classes restricted to one shell (so that every shell
    remains an independent segment), and the member transforms c(member) ~ a c(rep) or a conj(c(rep))."""

    def __init__(self, topo, group):
        K = topo.rep_flat.size
        shell = topo.shell_ids.astype(np.int64)
        self.order = np.argsort(shell, kind="stable")
        self.bounds = np.searchsorted(shell[self.order], np.arange(int(shell.max(initial=0)) + 2))
        rank = np.empty(K, dtype=np.int64)
        rank[self.order] = np.arange(K)
        rels = (lambda: iter_relations(topo, group)) if len(group) > 1 else (lambda: iter(()))
        best = rank.copy()
        for p, _, _ in rels():                     # the representative is the first star member of the same shell
            same = shell[p] == shell
            best = np.where(same, np.minimum(best, rank[p]), best)
        root = self.order[best]
        member = root != np.arange(K)
        a = np.ones(K, dtype=np.complex128)
        cj = np.zeros(K, dtype=bool)
        done = ~member
        reps = np.flatnonzero(~member)
        for p, conj, ph in rels():
            t = p[reps]
            sel = (root[t] == reps) & ~done[t]
            tgt, src = t[sel], reps[sel]
            c = conj[src]
            # c(src) = ph c(tgt) -> c(tgt) = conj(ph) c(src);  c(src) = ph conj(c(tgt)) -> c(tgt) = ph conj(c(src))
            a[tgt] = np.where(c, ph[src], np.conj(ph[src]))
            cj[tgt] = c
            done[tgt] = True
        if not np.all(done):
            raise RuntimeError("symmetry member without a transform")
        self.root, self.member, self.a, self.cj = root, member, a, cj
        self.nops = len(group)
        self.classes = int(np.count_nonzero(~member))
