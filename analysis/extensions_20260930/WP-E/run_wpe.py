#!/usr/bin/env python3
"""WP-E: certifying-writer policies evaluated on the frozen development ladders (PROTOCOL.md, WP-E).

No new computation: every Bader error, compressed size and eligibility flag is read from the frozen
benchmark. A policy "evaluates" a rung when it queries that row's re-derived Bader error (cost 1 solve);
QSQ costs 6 solves (reference + 5 probes) for every material.

    D:/Research/CatalystForge/.venv/Scripts/python.exe run_wpe.py
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TAUS = (1e-4, 1e-3, 1e-2)
CODECS = ("ZFP", "SZ3", "SPERR")
QSQ_COST = 6
SEED, NBOOT = 20260930, 2000


def load():
    b = pd.read_csv(REPO / "benchmark" / "master_benchmark_full.csv")
    b["codec"] = b.codec.str.upper()
    fl = pd.read_csv(REPO / "stability" / "stability_floor_A1.csv")
    floor = fl.drop_duplicates("material_id").set_index("material_id")["stability_floor_A1_e"]
    b["floor"] = b.material_id.map(floor)
    assert b.floor.notna().all() and b.material_id.nunique() == 254 and len(b) == 6343
    for t in TAUS:  # the frozen eligibility columns must equal f_m < tau
        col = "eligible_A1_at_%s" % ("0.0001" if t == 1e-4 else "0.001" if t == 1e-3 else "0.01")
        assert (b[col].astype(str).str.lower().isin(["true", "1"]) == (b.floor < t)).all(), col
    return b.sort_values(["material_id", "codec", "nominal_tolerance_relative"]).reset_index(drop=True)


def certified(row, tau):
    return bool(row.bound_respected) and row.Bader_error_resolved_e < tau


def scan(ladder, tau):
    """Loosest rung downwards, stop at the first certified. Returns (row or None, cost)."""
    cost = 0
    for _, r in ladder.iloc[::-1].iterrows():
        cost += 1
        if certified(r, tau):
            return r, cost
    return None, cost


def bisect(ladder, tau):
    """Binary search assuming certification is monotone in tolerance (tight -> loose)."""
    rows = [r for _, r in ladder.iterrows()]
    lo, hi, cost, best = -1, len(rows), 0, None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        cost += 1
        if certified(rows[mid], tau):
            lo, best = mid, rows[mid]
        else:
            hi = mid
    return best, cost


def exhaustive(ladder, tau):
    ok = [r for _, r in ladder.iterrows() if certified(r, tau)]
    return (max(ok, key=lambda r: r.compression_ratio) if ok else None), len(ladder)


BASE = {"EXHAUSTIVE": exhaustive, "SCAN": scan, "BISECT": bisect}
POLICIES = ["EXHAUSTIVE", "SCAN", "BISECT"] + ["%s-%s" % (p, c) for p in ("SCAN", "BISECT") for c in CODECS]


def run_policy(name, g, tau):
    base, _, only = name.partition("-")
    best, cost = None, 0
    for c in (CODECS if not only else (only,)):
        lad = g[g.codec == c]
        if lad.empty:
            continue
        r, k = BASE[base](lad, tau)
        cost += k
        if r is not None and (best is None or r.compression_ratio > best.compression_ratio):
            best = r
    return best, cost


def main():
    t0 = time.time()
    b = load()
    rows = []
    for mid, g in b.groupby("material_id"):
        raw = int(g.raw_bytes.iloc[0])
        assert (g.raw_bytes == raw).all()
        for tau in TAUS:
            elig = bool(g.floor.iloc[0] < tau)
            oracle, _ = run_policy("EXHAUSTIVE", g, tau) if elig else (None, 0)
            for p in POLICIES:
                r, cost = run_policy(p, g, tau) if elig else (None, 0)
                if r is not None:  # mechanical certificate re-check
                    assert elig and certified(r, tau)
                rows.append(dict(material_id=mid, system_type=g.system_type.iloc[0], tau_e=tau, eligible=elig, policy=p,
                                 raw_bytes=raw, stored_bytes=int(r.compressed_bytes) if r is not None else raw,
                                 returned_codec=r.codec if r is not None else "", returned_rel_tol=float(r.nominal_tolerance_relative) if r is not None else np.nan,
                                 returned_cr=float(r.compression_ratio) if r is not None else np.nan,
                                 oracle_cr=float(oracle.compression_ratio) if oracle is not None else np.nan,
                                 oracle_exists=oracle is not None, evaluations=cost, solves=QSQ_COST + cost,
                                 ladder_rows=len(g)))
    pm = pd.DataFrame(rows)
    pm.to_csv(HERE / "policy_material.csv", index=False)

    rng = np.random.default_rng(SEED)
    summ = []
    for (tau, p), d in pm.groupby(["tau_e", "policy"]):
        e = d[d.eligible]
        o = pm[(pm.tau_e == tau) & (pm.policy == "EXHAUSTIVE") & pm.eligible].set_index("material_id")
        e = e.set_index("material_id").loc[o.index]
        arc = e.raw_bytes.sum() / e.stored_bytes.sum()
        arc_o = o.raw_bytes.sum() / o.stored_bytes.sum()
        miss = int((e.oracle_exists & ~e.returned_cr.notna()).sum())
        short = (e.returned_cr / e.oracle_cr)[e.oracle_exists].fillna(0.0)
        ids = np.arange(len(e))
        boot = []
        for _ in range(NBOOT):
            s = rng.choice(ids, len(ids), replace=True)
            boot.append((e.raw_bytes.values[s].sum() / e.stored_bytes.values[s].sum()) /
                        (o.raw_bytes.values[s].sum() / o.stored_bytes.values[s].sum()))
        summ.append(dict(tau_e=tau, policy=p, n_materials=len(d), n_eligible=len(e), n_oracle_certifiable=int(e.oracle_exists.sum()),
                         archive_cr=arc, oracle_archive_cr=arc_o, fraction_of_oracle=arc / arc_o,
                         fraction_ci_low=float(np.quantile(boot, 0.025)), fraction_ci_high=float(np.quantile(boot, 0.975)),
                         miss_count=miss, miss_rate=miss / max(1, int(e.oracle_exists.sum())),
                         per_material_cr_ratio_median=float(short.median()) if len(short) else np.nan,
                         per_material_cr_ratio_p05=float(short.quantile(0.05)) if len(short) else np.nan,
                         mean_evaluations_eligible=float(e.evaluations.mean()), mean_solves_eligible=float(e.solves.mean()),
                         mean_solves_all=float(QSQ_COST + d.evaluations.mean())))
    sm = pd.DataFrame(summ)
    sm.to_csv(HERE / "policy_summary.csv", index=False)

    # adoption rule (tau = 1e-3 e), multi-codec policies only
    p3 = sm[(sm.tau_e == 1e-3) & sm.policy.isin(["EXHAUSTIVE", "SCAN", "BISECT"])]
    ok = p3[(p3.fraction_of_oracle >= 0.98) & (p3.miss_rate <= 0.02)].sort_values("mean_solves_eligible")
    adopted = ok.iloc[0].policy if len(ok) else "SCAN"
    why = ("fewest mean solves among multi-codec policies meeting >= 0.98 of oracle archive compression and <= 2% misses at 1e-3 e"
           if len(ok) else "no multi-codec policy met both criteria; protocol default SCAN")
    sel = p3.set_index("policy").loc[adopted]
    json.dump(dict(adopted_policy=adopted, reason=why, tau_e=1e-3, fraction_of_oracle=float(sel.fraction_of_oracle),
                   miss_rate=float(sel.miss_rate), mean_solves_eligible=float(sel.mean_solves_eligible),
                   candidates=p3[["policy", "fraction_of_oracle", "miss_rate", "mean_solves_eligible"]].to_dict("records"),
                   decided_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
              open(HERE / "adopted_policy.json", "w"), indent=1)

    inputs = [REPO / "benchmark" / "master_benchmark_full.csv", REPO / "stability" / "stability_floor_A1.csv"]
    prov = dict(package="WP-E", protocol="analysis/extensions_20260930/PROTOCOL.md (WP-E)",
                commit=subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                python=sys.version, executable=sys.executable, platform=platform.platform(),
                packages={m: __import__(m).__version__ for m in ("numpy", "pandas")},
                inputs={str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                wall_seconds=time.time() - t0)
    json.dump(prov, open(HERE / "provenance.json", "w"), indent=1)
    print(sm.round(4).to_string())
    print("ADOPTED:", adopted, "-", why)


if __name__ == "__main__":
    main()
