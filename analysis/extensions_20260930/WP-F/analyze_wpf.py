#!/usr/bin/env python3
"""WP-F aggregation (PROTOCOL.md, WP-F): design-based archive estimates from the 300 checkpoints.

    D:/Research/CatalystForge/.venv/Scripts/python.exe analyze_wpf.py [--allow-partial]

Writes objects.csv, rungs.csv, estimates.csv, strata_results.csv, writer_prospective.csv, failures.csv,
fig_archive.{png,svg,pdf}, RESULTS.md, provenance.json. Every number in RESULTS.md is computed here.
"""
from __future__ import annotations

import argparse
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CKPT = Path(r"D:\Research\QoI-ext-cache\WP-F\checkpoints")
TAUS = (1e-4, 1e-3, 1e-2)
FRAME_TB = 8.4976                         # frame total without the frozen study (frame_provenance / strata.csv)
SEED, NBOOT = 20260930, 2000


def load(allow_partial):
    sample = pd.read_csv(HERE / "sample.csv")
    strata = pd.read_csv(HERE / "strata.csv").set_index("stratum")
    assert abs(strata.bytes_total.sum() / 1e12 - FRAME_TB) < 1e-3
    ck = {Path(p).stem: json.load(open(p, encoding="utf-8")) for p in glob.glob(str(CKPT / "*.json"))}
    missing = sorted(set(sample.task_id) - set(ck))
    if missing and not allow_partial:
        raise SystemExit("%d sampled objects have no checkpoint yet" % len(missing))
    objs, rungs, fails = [], [], []
    for _, s in sample.iterrows():
        d = ck.get(s.task_id)
        if d is None:
            continue
        ok = d.get("status") == "SUCCESS"
        o = dict(task_id=s.task_id, stratum=s.stratum, status=d.get("status"), frame_bytes=int(s.bytes),
                 json_bytes=int(d.get("json_bytes", s.bytes)), raw64_bytes=d.get("raw64_bytes"), lossless_bytes=d.get("lossless_bytes"),
                 npoints=d.get("npoints"), natoms=d.get("natoms"), shape=d.get("shape"), formula=d.get("formula"),
                 crystal_system=d.get("crystal_system"), spacegroup=d.get("spacegroup"), epsilon=d.get("epsilon"),
                 floor_e=d.get("floor_e"), bader_solves=d.get("bader_solves"), wall_seconds=d.get("wall_seconds"),
                 retried=d.get("retried", False), size_matches_frame=d.get("size_matches_frame"))
        for t in TAUS:
            k = str(t)
            elig = bool(ok and d["eligible"][k])
            ch = (d.get("writer_choice") or {}).get(k) if elig else None
            if not ok:
                stored, how = int(s.bytes), "failed: current json.gz"
            elif ch:
                stored, how = int(ch["compressed_bytes"]), "certified %s %g" % (ch["codec"], ch["rel"])
            else:
                stored, how = int(d["lossless_bytes"]), "lossless (%s)" % ("eligible, none certified" if elig else "non-evaluable")
            o["eligible_%g" % t] = elig if ok else None
            o["stored_%g" % t] = stored
            o["storage_%g" % t] = how
            o["codec_%g" % t] = ch["codec"] if ch else ""
        objs.append(o)
        for r in d.get("rows", []):
            rungs.append(dict(task_id=s.task_id, stratum=s.stratum, **{k: v for k, v in r.items()}))
        for f in d.get("failures", []):
            fails.append(dict(task_id=s.task_id, stratum=s.stratum, stage=f.get("stage"), error=f.get("error")))
    return sample, strata, pd.DataFrame(objs), pd.DataFrame(rungs), pd.DataFrame(fails), missing


def expand(df, strata, col):
    """Stratified expansion estimator of a population total."""
    g = df.groupby("stratum")[col].agg(["sum", "count"])
    return float(sum(strata.loc[h, "N_frame"] / strata.loc[h, "n_sample"] * g.loc[h, "sum"] for h in g.index))


def boot(df, strata, fn, rng):
    groups = {h: d for h, d in df.groupby("stratum")}
    vals = []
    for _ in range(NBOOT):
        res = pd.concat([d.iloc[rng.integers(0, len(d), len(d))] for d in groups.values()])
        vals.append(fn(res))
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def oracle_row(rows, raw, tau):
    ok = [r for r in rows if r.get("status") == "OK" and r.get("bound_respected") and r["bader_error_e"] < tau]
    return max(ok, key=lambda r: raw / r["compressed_bytes"]) if ok else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-partial", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    sample, strata, O, R, F, missing = load(a.allow_partial)
    O.to_csv(HERE / "objects.csv", index=False)
    R.to_csv(HERE / "rungs.csv", index=False)
    (F if len(F) else pd.DataFrame(columns=["task_id", "stratum", "stage", "error"])).to_csv(HERE / "failures.csv", index=False)
    rng = np.random.default_rng(SEED)
    okO = O[O.status == "SUCCESS"]
    N = strata.N_frame.sum()

    est = []
    Tj = expand(O, strata, "json_bytes")
    for t in TAUS:
        col = "stored_%g" % t
        Ts = expand(O, strata, col)
        Rj = Tj / Ts
        lo, hi = boot(O, strata, lambda d: expand(d, strata, "json_bytes") / expand(d, strata, col), rng)
        est.append(dict(tau_e=t, quantity="R_vs_json", estimate=Rj, ci_low=lo, ci_high=hi))
        est.append(dict(tau_e=t, quantity="saving_TB", estimate=FRAME_TB * (1 - 1 / Rj), ci_low=FRAME_TB * (1 - 1 / lo), ci_high=FRAME_TB * (1 - 1 / hi)))
        for base in ("raw64_bytes", "lossless_bytes"):   # successful objects only (their sizes exist)
            f = lambda d, b=base: expand(d[d.status == "SUCCESS"], strata, b) / expand(d[d.status == "SUCCESS"], strata, col)
            lo2, hi2 = boot(O, strata, f, rng)
            est.append(dict(tau_e=t, quantity="R_vs_%s_success_only" % base.split("_")[0], estimate=f(O), ci_low=lo2, ci_high=hi2))
        el = O["eligible_%g" % t].fillna(False).astype(bool)
        ne = O.assign(ne=(~el & (O.status == "SUCCESS")).astype(float), ne_b=(~el & (O.status == "SUCCESS")) * O.json_bytes)
        cnt = expand(ne, strata, "ne") / N
        byt = expand(ne, strata, "ne_b") / Tj
        lo3, hi3 = boot(ne, strata, lambda d: expand(d, strata, "ne") / N, rng)
        est.append(dict(tau_e=t, quantity="nonevaluable_fraction_count", estimate=cnt, ci_low=lo3, ci_high=hi3))
        est.append(dict(tau_e=t, quantity="nonevaluable_fraction_bytes", estimate=byt, ci_low=np.nan, ci_high=np.nan))
        for c in ("ZFP", "SZ3", "SPERR"):
            mix = O.assign(x=(O["codec_%g" % t] == c).astype(float))
            est.append(dict(tau_e=t, quantity="certified_share_%s" % c, estimate=expand(mix, strata, "x") / N, ci_low=np.nan, ci_high=np.nan))
    for base in ("raw64_bytes", "lossless_bytes"):
        s_ = O[O.status == "SUCCESS"]
        est.append(dict(tau_e=np.nan, quantity="format_gain_json_over_%s_success_only" % base.split("_")[0],
                        estimate=expand(s_, strata, "json_bytes") / expand(s_, strata, base), ci_low=np.nan, ci_high=np.nan))
    E = pd.DataFrame(est)
    E.to_csv(HERE / "estimates.csv", index=False)

    sr = []
    for h, d in O.groupby("stratum"):
        row = dict(stratum=h, N_frame=int(strata.loc[h, "N_frame"]), n_sample=int(strata.loc[h, "n_sample"]), n_success=int((d.status == "SUCCESS").sum()),
                   n_failed=int((d.status != "SUCCESS").sum()), median_json_MB=float(d.json_bytes.median() / 1e6))
        for t in TAUS:
            row["eligible_%g" % t] = int(d["eligible_%g" % t].fillna(False).astype(bool).sum())
            row["R_vs_json_%g" % t] = float(d.json_bytes.sum() / d["stored_%g" % t].sum())
        sr.append(row)
    S = pd.DataFrame(sr)
    S.to_csv(HERE / "strata_results.csv", index=False)

    # prospective writer check on the full ladders (D01-D09)
    wp = []
    rows_by = {k: v for k, v in R.groupby("task_id")} if len(R) else {}
    ck = {Path(p).stem: json.load(open(p, encoding="utf-8")) for p in glob.glob(str(CKPT / "*.json"))}
    for t in TAUS:
        num = den = 0
        miss = n = 0
        for _, o in okO[okO.stratum.str.match(r"D0\d")].iterrows():
            if not o["eligible_%g" % t]:
                continue
            d = ck[o.task_id]
            orc = oracle_row(d.get("rows", []), o.raw64_bytes, t)
            ch = (d.get("writer_choice") or {}).get(str(t))
            if orc is None:
                continue
            n += 1
            num += o.raw64_bytes / (ch["compressed_bytes"] if ch else o.raw64_bytes)
            den += o.raw64_bytes / orc["compressed_bytes"]
            miss += ch is None
        sub = okO[okO.stratum.str.match(r"D0\d") & okO["eligible_%g" % t].astype(bool)]
        oracle_bytes = writer_bytes = 0
        for _, o in sub.iterrows():
            d = ck[o.task_id]
            orc = oracle_row(d.get("rows", []), o.raw64_bytes, t)
            ch = (d.get("writer_choice") or {}).get(str(t))
            oracle_bytes += orc["compressed_bytes"] if orc else o.raw64_bytes
            writer_bytes += ch["compressed_bytes"] if ch else o.raw64_bytes
        wp.append(dict(tau_e=t, n_eligible_with_certifiable_row=n, misses=miss, miss_rate=miss / n if n else np.nan,
                       archive_fraction_of_oracle=(sub.raw64_bytes.sum() / writer_bytes) / (sub.raw64_bytes.sum() / oracle_bytes) if len(sub) else np.nan))
    W = pd.DataFrame(wp)
    W.to_csv(HERE / "writer_prospective.csv", index=False)

    figure(E, O, strata)
    results(E, S, W, O, F, missing)
    prov = dict(package="WP-F", protocol="analysis/extensions_20260930/PROTOCOL.md (WP-F)",
                commit=subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
                python=sys.version, executable=sys.executable, platform=platform.platform(),
                inputs={p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in ("sample.csv", "strata.csv", "frame.csv.gz")},
                checkpoints=len(ck), checkpoint_sha256={k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest() for k, v in sorted(ck.items())},
                wall_seconds_analysis=time.time() - t0,
                runner_wall_hours=float(O.wall_seconds.fillna(0).sum() / 3600))
    json.dump(prov, open(HERE / "provenance.json", "w"), indent=1)


def figure(E, O, strata):
    sys.path.insert(0, str(REPO / "figures" / "composite"))
    from style import DARK_B, DARK_G, INK, MID, OTHER, PALE_B, RED, Page, grid, open_frame  # noqa: E402
    import layout  # noqa: E402
    pg = Page(183.0, 64.0)
    ax = pg.ax(14, 12, 72, 46)
    pg.letter("a", 2, 63)
    g = lambda q, t=None: E[(E.quantity == q) & ((E.tau_e == t) if t is not None else E.tau_e.isna())].iloc[0]
    s_ = O[O.status == "SUCCESS"]
    Tj = FRAME_TB
    bars = [("MP json.gz\n(today)", Tj, None, OTHER),
            ("lossless\nfloat64", Tj / g("format_gain_json_over_lossless_success_only").estimate, None, PALE_B)]
    for t, c in zip((1e-4, 1e-3, 1e-2), (DARK_B, DARK_B, DARK_B)):
        r = g("R_vs_json", t)
        bars.append(("certified\n" + r"$\tau$=%g e" % t, Tj / r.estimate, (Tj / r.ci_high, Tj / r.ci_low), DARK_G if t != 1e-3 else RED))
    for i, (lab, v, ci, c) in enumerate(bars):
        ax.bar(i, v, color=c, width=0.62, zorder=2)
        if ci:
            ax.errorbar(i, v, yerr=[[v - ci[0]], [ci[1] - v]], color=INK, lw=0.7, capsize=2, zorder=3)
        ax.text(i, v + 0.12, "%.2f" % v, ha="center", va="bottom", fontsize=5.6)
    ax.set_xticks(range(len(bars))); ax.set_xticklabels([b[0] for b in bars], fontsize=5.6)
    ax.set_ylabel("MP charge-density archive (TB)")
    ax.set_ylim(0, Tj * 1.15)
    open_frame(ax); grid(ax, "y")
    ax2 = pg.ax(108, 12, 70, 46)
    pg.letter("b", 96, 63)
    order = list(strata.index)
    x = np.arange(len(order))
    for j, (t, c) in enumerate(((1e-4, PALE_B), (1e-3, RED), (1e-2, DARK_B))):
        fr = [1 - O[(O.stratum == h)]["eligible_%g" % t].fillna(False).astype(bool).mean() for h in order]
        ax2.plot(x, fr, marker="o", ms=3, lw=0.9, color=c, label=r"$\tau$ = %g e" % t, zorder=3)
    ax2.set_xticks(x); ax2.set_xticklabels(order, rotation=90, fontsize=5.4)
    ax2.set_ylim(0, 1.02); ax2.set_ylabel("non-evaluable fraction in stratum")
    ax2.set_xlabel("size stratum (small to large)")
    open_frame(ax2); grid(ax2, "y")
    layout.legend(ax2, loc="upper left")
    layout.audit(pg.fig)
    pg.save(str(HERE), "fig_archive")


def results(E, S, W, O, F, missing):
    g = lambda q, t: E[(E.quantity == q) & (E.tau_e == t)].iloc[0]
    r3 = g("R_vs_json", 1e-3)
    verdict = ("storage saving (lower 95%% bound %.2f > 1.5)" % r3.ci_low) if r3.ci_low > 1.5 else \
              ("not reported as a storage saving (lower 95%% bound %.2f <= 1.5)" % r3.ci_low)
    L = ["# WP-F — What qualification buys: the Materials Project charge-density archive", "",
         "Frame: 415,289 objects, %.4f TB (MP json.gz), without the 186 frozen development objects. Stratified sample n = %d;"
         " %d succeeded, %d failed (failed objects keep their current json.gz size: no saving credited)%s." % (
             FRAME_TB, len(O), int((O.status == "SUCCESS").sum()), int((O.status != "SUCCESS").sum()),
             "" if not missing else "; %d objects not yet run (partial analysis)" % len(missing)),
         "", "## Primary endpoint", "",
         "R(1e-3 e) = %.3f [%.3f, %.3f] against the current json.gz archive — **%s** — an estimated saving of %.2f TB [%.2f, %.2f]." % (
             r3.estimate, r3.ci_low, r3.ci_high, verdict, g("saving_TB", 1e-3).estimate, g("saving_TB", 1e-3).ci_low, g("saving_TB", 1e-3).ci_high),
         "", "## All tolerances", "",
         "| τ (e) | R vs json.gz [95% CI] | saving (TB) | R vs float64 | R vs lossless float64 | non-evaluable (objects) [95% CI] | non-evaluable (bytes) | certified ZFP / SZ3 / SPERR (objects) |",
         "|---:|---|---:|---:|---:|---|---:|---|"]
    for t in TAUS:
        a, s = g("R_vs_json", t), g("saving_TB", t)
        L.append("| %g | %.3f [%.3f, %.3f] | %.2f | %.2f | %.2f [%.2f, %.2f] | %.1f%% [%.1f, %.1f] | %.1f%% | %.1f%% / %.1f%% / %.1f%% |" % (
            t, a.estimate, a.ci_low, a.ci_high, s.estimate, g("R_vs_raw64_success_only", t).estimate,
            g("R_vs_lossless_success_only", t).estimate, g("R_vs_lossless_success_only", t).ci_low, g("R_vs_lossless_success_only", t).ci_high,
            100 * g("nonevaluable_fraction_count", t).estimate, 100 * g("nonevaluable_fraction_count", t).ci_low,
            100 * g("nonevaluable_fraction_count", t).ci_high, 100 * g("nonevaluable_fraction_bytes", t).estimate,
            100 * g("certified_share_ZFP", t).estimate, 100 * g("certified_share_SZ3", t).estimate, 100 * g("certified_share_SPERR", t).estimate))
    fl = E[E.quantity == "format_gain_json_over_lossless_success_only"].iloc[0].estimate
    L += ["", "Format gain alone (json.gz → lossless float64 + zlib, no scientific approximation): %.2f×. "
          "R vs lossless isolates what certified lossy compression adds on top of it." % fl,
          "", "## Prospective check of the WP-E writer (D01–D09 full ladders)", "",
          "| τ (e) | eligible objects with a certifiable rung | misses | archive fraction of oracle |", "|---:|---:|---:|---:|"]
    for _, w in W.iterrows():
        L.append("| %g | %d | %d | %.4f |" % (w.tau_e, w.n_eligible_with_certifiable_row, w.misses, w.archive_fraction_of_oracle))
    L += ["", "## Strata", "", S.to_markdown(index=False, floatfmt=".3g"), "",
          "## Failures", "", "%d failure records in %d objects (`failures.csv`)." % (len(F), F.task_id.nunique() if len(F) else 0), "",
          "Files: `objects.csv`, `rungs.csv`, `estimates.csv`, `strata_results.csv`, `writer_prospective.csv`, `failures.csv`,"
          " `fig_archive.{png,svg,pdf}`, `provenance.json`, `DEVIATIONS.md`."]
    # a partial analysis must never look like the final one to the monitor (RESULTS.md = done)
    (HERE / ("RESULTS_PARTIAL.md" if missing else "RESULTS.md")).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
