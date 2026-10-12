#!/usr/bin/env python3
"""Aggregate the deployment-cost shards (see PROTOCOL.md): per-operation table, endpoints E1-E5, RESULTS.md."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

TAUS = (1e-4, 1e-6, 1e-8)
PRIMARY = 1e-6
BANDWIDTHS = {"0.1Gbps": 0.1e9, "1Gbps": 1e9, "10Gbps": 10e9}
ARMS = ("A1", "A3", "A6", "M2", "Q")
NAMES = {"A1": "closed-form law (A1)", "A1ref": "law, reference implementation", "A3": "operational optimum (A3)",
         "A3ref": "A3, reference implementation", "A6": "best of ZFP/SZ3/SPERR (A6)", "M2": "MGARD s=-2",
         "Q": "QPET (best of 9)", "L_zlib": "float64+zlib-6", "L_zstd": "float64+zstd-3", "SRC": "source file as archived",
         "RAW": "raw float64"}
RNG_SEED, NBOOT = 20261012, 10000


def boot_median(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if x.size == 0:
        return [float("nan")] * 3
    r = np.random.default_rng(RNG_SEED)
    b = np.median(x[r.integers(0, x.size, (NBOOT, x.size))], axis=1)
    return [float(np.median(x)), float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))]


def load(root: Path):
    rows, infos, fails = [], [], []
    for f in root.rglob("cost_*.jsonl"):
        rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    for f in root.rglob("info_*.json"):
        infos.append(json.loads(f.read_text(encoding="utf-8")))
    for f in root.rglob("failures_*.json"):
        fails += json.loads(f.read_text(encoding="utf-8"))
    return pd.DataFrame(rows), infos, fails


def table(df: pd.DataFrame, infos: list) -> pd.DataFrame:
    """One row per (material, arm, tau): bytes, encode/decode/search seconds, memory, retrieval times."""
    info = {i["material_id"]: i for i in infos}
    out = []
    for (mid, arm, tau), g in df.groupby(["material_id", "arm", "tau"]):
        e = g[g.op == "encode"]; d = g[g.op == "decode"]; s = g[g.op == "search"]
        raw = int(g.raw_bytes.iloc[0])
        r = {"material_id": mid, "cohort": g.cohort.iloc[0], "system_type": g.system_type.iloc[0], "arm": arm,
             "tau": tau, "raw_bytes": raw,
             "bytes": int(e.bytes.iloc[0]) if len(e) else np.nan,
             "recorded_bytes": g.recorded_bytes.iloc[0],
             "encode_s": e.seconds_median.iloc[0] if len(e) else np.nan,
             "decode_s": d.seconds_median.iloc[0] if len(d) else np.nan,
             "search_s": s.seconds_median.iloc[0] if len(s) else np.nan,
             "search_param": s.param.iloc[0] if len(s) and "param" in s else "",
             "search_bytes": s.bytes.iloc[0] if len(s) else np.nan,
             "certified": bool(d.certified.iloc[0]) if len(d) and tau > 0 else None,
             "encode_mem_x": e.peak_rss_above_input_bytes.iloc[0] / raw if len(e) else np.nan,
             "decode_mem_x": d.peak_rss_above_input_bytes.iloc[0] / raw if len(d) else np.nan}
        for side, sub in (("encode", e), ("decode", d)):
            cp = sub.cli_peak_rss_bytes.iloc[0] if len(sub) and "cli_peak_rss_bytes" in sub else None
            r[f"{side}_cli_mem_x"] = cp / raw if cp is not None and np.isfinite(cp) else np.nan
            r[f"{side}_cli_s"] = sub.cli_seconds.iloc[0] if len(sub) and "cli_seconds" in sub else np.nan
        r["cr"] = raw / r["bytes"] if r["bytes"] == r["bytes"] else np.nan
        out.append(r)
    t = pd.DataFrame(out)
    # lossless references apply at every tolerance; the source file and raw float64 likewise
    extra = []
    for mid, i in info.items():
        base = {"material_id": mid, "cohort": i["cohort"], "system_type": i["system_type"], "raw_bytes": i["raw_bytes"]}
        for tau in TAUS:
            extra.append(base | {"arm": "SRC", "tau": tau, "bytes": i["source_bytes"],
                                 "decode_s": i["source_parse_seconds_median"], "cr": i["raw_bytes"] / i["source_bytes"]})
            extra.append(base | {"arm": "RAW", "tau": tau, "bytes": i["raw_bytes"], "decode_s": 0.0, "cr": 1.0})
            for L in ("L_zlib", "L_zstd"):
                m = t[(t.material_id == mid) & (t.arm == L)]
                if len(m):
                    extra.append(m.iloc[0].to_dict() | {"tau": tau})
    t = pd.concat([t[~t.arm.isin(["L_zlib", "L_zstd"])], pd.DataFrame(extra)], ignore_index=True)
    for k, b in BANDWIDTHS.items():
        t[f"ttf_{k}"] = 8.0 * t["bytes"] / b + t["decode_s"]
    t["decode_MBps"] = t.raw_bytes / 1e6 / t.decode_s
    return t


def paired(t, tau, cohort, col, ref="A1"):
    x = t[(t.tau == tau) & (t.cohort == cohort)].pivot_table(index="material_id", columns="arm", values=col)
    out = {}
    for arm in x.columns:
        if arm == ref:
            continue
        r = (x[arm] / x[ref]).dropna()
        out[arm] = {"n": int(r.size), "median_ratio_vs_" + ref: boot_median(r),
                    "ref_better": int((r > 1).sum())}
    return out


def summarize(t: pd.DataFrame, infos, fails) -> dict:
    S = {"n_materials": len(infos), "failures": fails,
         "runners": sorted({i["calibration"]["cpu"] for i in infos}), "cohorts": {}}
    for cohort in sorted(t.cohort.unique()):
        C = {}
        for tau in TAUS:
            sub = t[(t.tau == tau) & (t.cohort == cohort)]
            med = {}
            for arm, g in sub.groupby("arm"):
                med[arm] = {c: boot_median(g[c]) for c in
                            ("cr", "encode_s", "decode_s", "search_s", "decode_MBps", "encode_mem_x", "decode_mem_x",
                             "encode_cli_mem_x", "decode_cli_mem_x", "ttf_0.1Gbps", "ttf_1Gbps", "ttf_10Gbps")
                            if c in g and g[c].notna().any()}
                med[arm]["n"] = int(len(g)); med[arm]["total_bytes"] = float(g.bytes.sum())
                if "certified" in g and g.certified.notna().any():
                    med[arm]["certified"] = int((g.certified == True).sum())
            ttf_win = {}
            for k in BANDWIDTHS:
                p = sub.pivot_table(index="material_id", columns="arm", values=f"ttf_{k}")
                cols = [c for c in p.columns if c not in ("A1ref", "A3ref")]
                ttf_win[k] = {"A1_fastest": int((p[cols].idxmin(axis=1) == "A1").sum()), "n": int(len(p)),
                              "fastest_counts": p[cols].idxmin(axis=1).value_counts().to_dict()}
            # break-even bandwidth: below B*, A1 delivers a usable field first (inf: A1 is smaller and decodes faster)
            p_b = sub.pivot_table(index="material_id", columns="arm", values="bytes")
            p_d = sub.pivot_table(index="material_id", columns="arm", values="decode_s")
            be = {}
            for arm in p_b.columns:
                if arm in ("A1", "A1ref", "A3ref") or "A1" not in p_b:
                    continue
                db = (p_b[arm] - p_b["A1"]) * 8.0; dd = p_d["A1"] - p_d[arm]
                bstar = np.where(dd <= 0, np.where(db >= 0, np.inf, 0.0), np.where(db > 0, db / dd, 0.0)) / 1e9
                bstar = bstar[np.isfinite(p_b[arm].values) & np.isfinite(p_d[arm].values)]
                be[arm] = {"median_breakeven_Gbps": float(np.median(bstar)) if bstar.size else None,
                           "n": int(bstar.size), "A1_dominates": int(np.isinf(bstar).sum())}
            C[f"{tau:g}"] = {"medians": med, "breakeven": be,
                             "paired_decode": paired(t, tau, cohort, "decode_s"),
                             "paired_encode": paired(t, tau, cohort, "encode_s"),
                             "paired_search": paired(t, tau, cohort, "search_s") if tau == PRIMARY else {},
                             **{f"paired_ttf_{k}": paired(t, tau, cohort, f"ttf_{k}") for k in BANDWIDTHS},
                             "ttf_fastest": ttf_win}
        S["cohorts"][cohort] = C
    # reproduction checks
    chk = t[t.arm.isin(["A1", "A1ref", "A3", "A3ref", "A6", "M2", "Q"])]
    S["reproduction"] = {
        "streams": int(len(chk)),
        "certified": int((chk.certified == True).sum()),
        "bytes_equal_recorded": int((chk.bytes == chk.recorded_bytes).sum()),
        "max_abs_byte_difference": float((chk.bytes - chk.recorded_bytes).abs().max()),
        "search_param_mismatch": int(((t.search_bytes.notna()) & (t.search_bytes != t.recorded_bytes)).sum()),
    }
    return S


def fmt(v, d=3):
    return "n/a" if v is None or v != v else (f"{v:.{d}g}")


def ci(m):
    return f"{fmt(m[0])} [{fmt(m[1])}, {fmt(m[2])}]"


def results_md(S: dict) -> str:
    L = ["# Deployment cost — results", "",
         f"Materials: {S['n_materials']}; runner CPUs: {', '.join(S['runners'])}.", "",
         "Reproduction: " + ", ".join(f"{k} = {v}" for k, v in S["reproduction"].items()) + ".", ""]
    for cohort, C in S["cohorts"].items():
        for tau, R in C.items():
            L += [f"## {cohort}, τ = {tau}", "",
                  "| arm | CR | encode s | search s | decode s | decode MB/s | enc mem ×field | dec mem ×field | T(1 Gbit/s) s |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for arm in ("A1", "A1ref", "A3", "A3ref", "A6", "M2", "Q", "L_zlib", "L_zstd", "SRC", "RAW"):
                m = R["medians"].get(arm)
                if not m:
                    continue
                g = lambda k: ci(m[k]) if k in m else "n/a"
                mem_e = g("encode_cli_mem_x") if arm in ("M2", "Q") else g("encode_mem_x")
                mem_d = g("decode_cli_mem_x") if arm in ("M2", "Q") else g("decode_mem_x")
                L.append(f"| {NAMES[arm]} | {g('cr')} | {g('encode_s')} | {g('search_s')} | {g('decode_s')} | "
                         f"{g('decode_MBps')} | {mem_e} | {mem_d} | {g('ttf_1Gbps')} |")
            L += ["", "Paired ratios arm / A1 (median [95% CI], n, materials where A1 is lower):", ""]
            for key in ("paired_encode", "paired_search", "paired_decode", "paired_ttf_0.1Gbps", "paired_ttf_1Gbps",
                        "paired_ttf_10Gbps"):
                for arm, v in R.get(key, {}).items():
                    L.append(f"- {key[7:]}: {NAMES.get(arm, arm)} {ci(v['median_ratio_vs_A1'])}, n={v['n']}, "
                             f"A1 lower in {v['ref_better']}")
            L += ["", "Break-even bandwidth (A1 first to a usable field below it): " + "; ".join(
                f"{NAMES.get(k, k)} {fmt(v['median_breakeven_Gbps'])} Gbit/s (A1 smaller and faster in {v['A1_dominates']}/{v['n']})"
                for k, v in R["breakeven"].items())]
            L += ["", "Fastest to a usable field: " + "; ".join(
                f"{k}: A1 {v['A1_fastest']}/{v['n']} ({v['fastest_counts']})" for k, v in R["ttf_fastest"].items()), ""]
    if S["failures"]:
        L += ["## Failures", ""] + [f"- {f}" for f in S["failures"]]
    return "\n".join(L) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--shards-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    df, infos, fails = load(a.shards_root)
    t = table(df, infos)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    t.sort_values(["cohort", "material_id", "tau", "arm"]).to_csv(a.output_dir / "per_material.csv", index=False)
    df.drop(columns=["seconds_all"], errors="ignore").to_csv(a.output_dir / "per_operation.csv", index=False)
    pd.DataFrame([{"material_id": i["material_id"], **i["calibration"], "source_download_s": i.get("source_download_seconds"),
                   "source_parse_s": i["source_parse_seconds_median"], "npoints": i["npoints"]} for i in infos]
                 ).to_csv(a.output_dir / "runners.csv", index=False)
    S = summarize(t, infos, fails)
    (a.output_dir / "SUMMARY.json").write_text(json.dumps(S, indent=1, default=float), encoding="utf-8")
    (a.output_dir / "RESULTS.md").write_text(results_md(S), encoding="utf-8")
    print(results_md(S)[:3000])


if __name__ == "__main__":
    main()
