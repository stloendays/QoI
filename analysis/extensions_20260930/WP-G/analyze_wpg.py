#!/usr/bin/env python3
"""WP-G analysis (PROTOCOL.md WP-G, DEVIATIONS.md 1-2): all-electron-reference Bader, Henkelman on-grid.

Reads vanda_results/checkpoints/*.json (copied back from Vanda) and writes reference.csv, probes.csv, rows.csv,
summary.csv, failures.csv, fig_ae_reference.{png,svg,pdf}, RESULTS.md, provenance.json.

    D:/Research/CatalystForge/.venv/Scripts/python.exe analyze_wpg.py
"""
from __future__ import annotations

import glob
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CK = HERE / "vanda_results" / "checkpoints"
TAUS = (1e-4, 1e-3, 1e-2)
ARMS = ("v", "g1", "g2")
SEED, NBOOT = 20260930, 2000


def mcnemar(a, b):
    """Exact McNemar on paired booleans: p-value of the discordant split."""
    n01, n10 = int(np.sum(~a & b)), int(np.sum(a & ~b))
    p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return n01, n10, p


def main():
    t0 = time.time()
    cks = {Path(p).stem: json.load(open(p, encoding="utf-8")) for p in glob.glob(str(CK / "*.json"))}
    assert len(cks) == 53, len(cks)
    floor = pd.read_csv(REPO / "stability" / "stability_floor_A1.csv").drop_duplicates("material_id").set_index("material_id")["stability_floor_A1_e"]
    ref, probes, rows, fails = [], [], [], []
    for m, d in sorted(cks.items()):
        ok = d["status"] == "SUCCESS"
        r = dict(material_id=m, status=d["status"], shape=d.get("shape"), natoms=d.get("natoms"), frozen_floor_e=float(floor[m]),
                 epsilon_chgcar=d.get("epsilon_chgcar"), epsilon_ae=d.get("epsilon_ae"), ae_min=d.get("ae_min"), bader_solves=d.get("bader_solves"))
        for a in ARMS:
            r["%s_floor_e" % a] = d.get("%s_floor_e" % a)
        if ok:
            qv, qa = np.array(d["reference"]["q_valence"]), np.array(d["reference"]["q_ae"])
            r["ref_max_abs_q_diff_valence_vs_ae_e"] = float(np.max(np.abs(qv - qa)))
        ref.append(r)
        for p in d.get("probes", []):
            probes.append(dict(material_id=m, **p))
        for x in d.get("rows", []):
            rows.append(dict(material_id=m, **x))
        for f in d.get("failures", []):
            fails.append(f)
    R = pd.DataFrame(ref); P = pd.DataFrame(probes); W = pd.DataFrame(rows)
    F = pd.DataFrame(fails) if fails else pd.DataFrame(columns=["material_id", "stage", "error"])
    for name, df in (("reference.csv", R), ("probes.csv", P), ("rows.csv", W), ("failures.csv", F)):
        df.to_csv(HERE / name, index=False)
    ok = R[R.status == "SUCCESS"].copy()
    n = len(ok)
    rng = np.random.default_rng(SEED)
    S = []
    # (1) eligibility, paired
    for t in TAUS:
        el = {a: (ok["%s_floor_e" % a] < t).values for a in ARMS}
        el["frozen"] = (ok.frozen_floor_e < t).values
        row = dict(analysis="eligibility", tau_e=t, n=n, **{"eligible_%s" % k: int(v.sum()) for k, v in el.items()})
        for a, b in (("v", "g1"), ("v", "g2"), ("g1", "g2"), ("frozen", "v")):
            n01, n10, p = mcnemar(el[a], el[b])
            row["mcnemar_%s_vs_%s" % (a, b)] = "%d/%d p=%.3g" % (n01, n10, p)
        S.append(row)
    # (2) floors relative to V (and to the frozen baderkit floor, context)
    for a in ("g1", "g2"):
        for base in ("v", "frozen"):
            den = ok["%s_floor_e" % base] if base == "v" else ok.frozen_floor_e
            x = np.log10(np.maximum(ok["%s_floor_e" % a].values, 1e-12) / np.maximum(den.values, 1e-12))
            b = [np.median(x[rng.integers(0, n, n)]) for _ in range(NBOOT)]
            S.append(dict(analysis="floor_log10_ratio", arm=a, base=base, n=n, median=float(np.median(x)),
                          ci_low=float(np.quantile(b, 0.025)), ci_high=float(np.quantile(b, 0.975)),
                          frac_increased=float(np.mean(x > 0))))
    # (3) certification: best certified ratio per codec and arm; codec ranking
    Wok = W[(W.status == "OK") & W.material_id.isin(ok.material_id)].copy()
    npts = ok.set_index("material_id").shape.map(lambda s: int(np.prod([int(v) for v in s.split("x")])))
    Wok["raw"] = Wok.material_id.map(npts) * 8
    Wok["cr_v"] = Wok.raw / Wok.chgcar_bytes
    Wok["cr_g1"] = Wok.raw / Wok.chgcar_bytes                      # AE reference stored exactly, not counted here
    Wok["cr_g2"] = 2 * Wok.raw / (Wok.chgcar_bytes + Wok.ae_bytes)
    elig = {a: ok.set_index("material_id")["%s_floor_e" % a] for a in ARMS}
    for t in TAUS:
        for a in ARMS:
            best = {}
            for m, g in Wok.groupby("material_id"):
                if not elig[a][m] < t:
                    continue
                c = g[g["%s_error_e" % a] < t]
                best[m] = (c.loc[c["cr_%s" % a].idxmax(), "codec"], float(c["cr_%s" % a].max())) if len(c) else ("none", 1.0)
            crs = np.array([v[1] for v in best.values()]) if best else np.array([np.nan])
            codecs = pd.Series([v[0] for v in best.values()]).value_counts()
            S.append(dict(analysis="certification", tau_e=t, arm=a, n_eligible=len(best), median_best_cr=float(np.nanmedian(crs)),
                          share_ZFP=float(codecs.get("ZFP", 0) / max(1, len(best))), share_SZ3=float(codecs.get("SZ3", 0) / max(1, len(best))),
                          share_SPERR=float(codecs.get("SPERR", 0) / max(1, len(best))), share_none=float(codecs.get("none", 0) / max(1, len(best)))))
    # (4) basin reassignment on the same rungs
    for a in ARMS:
        S.append(dict(analysis="reassignment", arm=a, n_rows=int(Wok["%s_reassigned_frac" % a].notna().sum()),
                      median=float(Wok["%s_reassigned_frac" % a].median()), p90=float(Wok["%s_reassigned_frac" % a].quantile(0.9))))
    S.append(dict(analysis="reproduction", n_rows=len(W), n_ok=int((W.status == "OK").sum()),
                  reproduced=int(W.get("reproduced", pd.Series(dtype=bool)).fillna(False).astype(bool).sum())))
    SM = pd.DataFrame(S)
    SM.to_csv(HERE / "summary.csv", index=False)

    e3 = SM[(SM.analysis == "eligibility") & (SM.tau_e == 1e-3)].iloc[0]
    g2_ne, g1_el = n - e3.eligible_g2, e3.eligible_g1
    v1 = "QSQ is needed under the standard practice" if g2_ne >= 0.10 * n else "not met (G2 leaves <10% non-evaluable)"
    v2 = ("an exact all-electron reference removes the instability" if (g1_el >= 0.95 * n and e3.eligible_g2 < 0.95 * n)
          else "not met (G1 %d/%d eligible, G2 %d/%d)" % (g1_el, n, e3.eligible_g2, n))
    figure(ok, SM)
    L = ["# WP-G — Qualification under all-electron-reference Bader", "",
         "Henkelman Bader 1.05 on-grid (`-b ongrid -vac 0.001`) on NUS Vanda (DEVIATIONS.md 1–3); %d of 53 materials"
         " succeeded, %d failure records. Arms: V valence reference, G1 exact AECCAR0+AECCAR2 reference, G2 reference also"
         " perturbed/compressed." % (n, len(F)), "",
         "## Acceptance (τ = 1e-3 e)", "",
         "- G2 non-evaluable: %d/%d (%.0f%%) → **%s**." % (g2_ne, n, 100 * g2_ne / n, v1),
         "- G1 eligible: %d/%d, G2 eligible: %d/%d → **%s**." % (g1_el, n, e3.eligible_g2, n, v2), "",
         "## Eligibility (paired, n = %d)" % n, "",
         "| τ (e) | frozen baderkit (valence) | V | G1 | G2 | McNemar V→G1 (gain/loss, p) | V→G2 | G1→G2 |", "|---:|---:|---:|---:|---:|---|---|---|"]
    for _, r in SM[SM.analysis == "eligibility"].iterrows():
        L.append("| %g | %d | %d | %d | %d | %s | %s | %s |" % (r.tau_e, r.eligible_frozen, r.eligible_v, r.eligible_g1, r.eligible_g2,
                                                           r.mcnemar_v_vs_g1, r.mcnemar_v_vs_g2, r.mcnemar_g1_vs_g2))
    L += ["", "## Floors", "", "| arm | relative to | material-median log10 ratio [95% CI] | fraction increased |", "|---|---|---|---:|"]
    for _, r in SM[SM.analysis == "floor_log10_ratio"].iterrows():
        L.append("| %s | %s | %.2f [%.2f, %.2f] | %.2f |" % (r.arm.upper(), "V" if r.base == "v" else "frozen baderkit", r["median"], r.ci_low, r.ci_high, r.frac_increased))
    L += ["", "## Certification", "", "| τ (e) | arm | eligible | median best certified CR | ZFP / SZ3 / SPERR / none best |", "|---:|---|---:|---:|---|"]
    for _, r in SM[SM.analysis == "certification"].iterrows():
        L.append("| %g | %s | %d | %.2f | %.2f / %.2f / %.2f / %.2f |" % (r.tau_e, r.arm.upper(), r.n_eligible, r.median_best_cr,
                                                                    r.share_ZFP, r.share_SZ3, r.share_SPERR, r.share_none))
    L += ["", "## Basin reassignment on the same rungs", "", "| arm | rows | median reassigned fraction | P90 |", "|---|---:|---:|---:|"]
    for _, r in SM[SM.analysis == "reassignment"].iterrows():
        L.append("| %s | %d | %.3g | %.3g |" % (r.arm.upper(), r.n_rows, r["median"], r.p90))
    rp = SM[SM.analysis == "reproduction"].iloc[0]
    L += ["", "Codec rows reproduced within 0.95–1.05 of the frozen realized L∞: %d of %d evaluated (%d total)." % (rp.reproduced, rp.n_ok, rp.n_rows),
          "", "Files: `reference.csv`, `probes.csv`, `rows.csv`, `summary.csv`, `failures.csv`, `fig_ae_reference.{png,svg,pdf}`,"
          " `provenance.json`, `DEVIATIONS.md`, `vanda_results/`."]
    (HERE / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    prov = dict(package="WP-G", protocol="analysis/extensions_20260930/PROTOCOL.md (WP-G) + DEVIATIONS.md",
                commit=subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                python=sys.version, platform=platform.platform(),
                checkpoints={k: hashlib.sha256((CK / (k + ".json")).read_bytes()).hexdigest() for k in sorted(cks)},
                bader_sha256=sorted({d.get("bader_sha256") for d in cks.values()} - {None}), wall_seconds_analysis=time.time() - t0)
    json.dump(prov, open(HERE / "provenance.json", "w"), indent=1)
    print("\n".join(L[:14]))


def figure(ok, SM):
    sys.path.insert(0, str(REPO / "figures" / "composite"))
    from style import DARK_B, DARK_G, INK, MID, OTHER, PALE_B, RED, Page, grid, log_ticks, open_frame  # noqa: E402
    import layout  # noqa: E402
    pg = Page(183.0, 66.0)
    ax = pg.ax(14, 12, 68, 48)
    pg.letter("a", 2, 65)
    lo, hi = 1e-9, 10
    ax.plot([lo, hi], [lo, hi], color=INK, lw=0.6, ls=(0, (4, 2)))
    ax.scatter(ok.v_floor_e.clip(lower=lo), ok.g1_floor_e.clip(lower=lo), s=10, color=DARK_G, lw=0, label="G1: exact AE reference", zorder=3)
    ax.scatter(ok.v_floor_e.clip(lower=lo), ok.g2_floor_e.clip(lower=lo), s=10, color=RED, lw=0, label="G2: AE reference perturbed too", zorder=4)
    ax.axhline(1e-3, color=OTHER, lw=0.6); ax.axvline(1e-3, color=OTHER, lw=0.6)
    ax.set_xscale("log"); ax.set_yscale("log"); log_ticks(ax)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("QSQ floor, valence reference V (e)"); ax.set_ylabel("QSQ floor, all-electron reference (e)")
    open_frame(ax); grid(ax)
    layout.legend(ax, loc="upper left")
    ax = pg.ax(108, 12, 70, 48)
    pg.letter("b", 96, 65)
    el = SM[SM.analysis == "eligibility"]
    x = np.arange(3)
    for j, (a, c, lab) in enumerate((("frozen", OTHER, "frozen baderkit (V)"), ("v", DARK_B, "Henkelman V"), ("g1", DARK_G, "G1"), ("g2", RED, "G2"))):
        ax.bar(x + (j - 1.5) * 0.2, el["eligible_%s" % a].values / el.n.values, width=0.19, color=c, label=lab, zorder=2)
    ax.set_xticks(x); ax.set_xticklabels([r"$10^{-4}$ e", r"$10^{-3}$ e", r"$10^{-2}$ e"])
    ax.set_ylim(0, 1.05); ax.set_ylabel("QSQ-eligible fraction (n = %d)" % int(el.n.iloc[0]))
    ax.set_xlabel(r"Bader tolerance $\tau$")
    open_frame(ax); grid(ax, "y")
    layout.legend(ax, loc="upper left")
    layout.audit(pg.fig)
    pg.save(str(HERE), "fig_ae_reference")


if __name__ == "__main__":
    main()
