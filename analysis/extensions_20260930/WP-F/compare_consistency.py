#!/usr/bin/env python3
"""WP-F platform consistency check (DEVIATIONS.md 7-8): laptop vs cloud checkpoints of the same objects.

    python compare_consistency.py --laptop results_laptop/checkpoints --cloud results_cloud/consistency/checkpoints \
        --out-dir results_cloud --ids mp-2488566 mp-2285510 mp-2050393 mp-2367698 mp-2682232

Agreement rule of DEVIATIONS.md 7, per object:
  - eligibility identical at all three tau;
  - certified flag of every evaluated rung identical (the rung's certifiable_error flag, and certified at each tau:
    status OK, bound respected, Bader error < tau; DEVIATIONS.md 8); the evaluated rung sets are identical;
  - writer choice (codec and rung) identical at each tau;
  - compressed bytes of every rung within 0.1 %;
  - floor, every probe response and every rung's Bader error within 1e-6 e.
Writes CONSISTENCY.md and CONSISTENCY.json in --out-dir and consistency/consistency_fields.csv beside them.
Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

TAUS = ("0.0001", "0.001", "0.01")
TOL_E = 1e-6          # e
TOL_BYTES_REL = 1e-3  # 0.1 %
CONSISTENCY_IDS = ("mp-2488566", "mp-2285510", "mp-2050393", "mp-2367698", "mp-2682232")   # DEVIATIONS.md 7


def certified(row, tau):
    return bool(row.get("status") == "OK" and row.get("bound_respected") and row["bader_error_e"] < float(tau))


def adiff(a, b):
    if a is None or b is None:
        return math.inf
    a, b = float(a), float(b)
    if math.isinf(a) and math.isinf(b) and a == b:
        return 0.0
    return abs(a - b)


def rdiff(a, b):
    if a is None or b is None:
        return math.inf
    a, b = float(a), float(b)
    return abs(a - b) / abs(a) if a else (0.0 if b == 0 else math.inf)


def fmt(x):
    if x is None:
        return ""
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        return "%.10g" % x
    return str(x)


def compare(tid, lap, cld):
    """Return (field rows, object summary)."""
    rows = []

    def add(field, lv, cv, diff, kind, criterion, ok):
        rows.append(dict(task_id=tid, field=field, laptop=fmt(lv), cloud=fmt(cv), diff=fmt(diff), diff_kind=kind,
                         criterion=criterion, passes=ok))

    # status: both must have succeeded for the comparison to be possible
    add("status", lap.get("status"), cld.get("status"), "", "equal", "identical",
        lap.get("status") == cld.get("status") == "SUCCESS")
    if cld.get("status") != "SUCCESS":
        return rows, dict(task_id=tid, compared=False)
    # input identity and loaded field (informational)
    for f in ("sha256", "json_bytes", "shape", "npoints", "natoms", "natoms_bader", "spin_channels", "formula",
              "crystal_system", "spacegroup"):
        add(f, lap.get(f), cld.get(f), "", "equal", "informational", lap.get(f) == cld.get(f))
    for f in ("epsilon", "value_ptp", "value_min", "value_max"):
        add(f, lap.get(f), cld.get(f), adiff(lap.get(f), cld.get(f)), "abs", "informational", True)
    for f in ("raw64_bytes", "lossless_bytes"):
        add(f, lap.get(f), cld.get(f), rdiff(lap.get(f), cld.get(f)), "rel", "informational", True)
    add("bader_solves", lap.get("bader_solves"), cld.get("bader_solves"), "", "equal", "informational",
        lap.get("bader_solves") == cld.get("bader_solves"))
    # eligibility
    for t in TAUS:
        lv, cv = lap["eligible"].get(t), cld["eligible"].get(t)
        add("eligible@%s" % t, lv, cv, "", "equal", "identical", lv == cv)
    # floor and probes
    d = adiff(lap.get("floor_e"), cld.get("floor_e"))
    add("floor_e", lap.get("floor_e"), cld.get("floor_e"), d, "abs", "<= 1e-6 e", d <= TOL_E)
    lp = {p["seed"]: p for p in lap.get("probes", [])}
    cp = {p["seed"]: p for p in cld.get("probes", [])}
    add("probe_seeds", sorted(lp), sorted(cp), "", "equal", "identical", sorted(lp) == sorted(cp))
    for s in sorted(set(lp) | set(cp)):
        a, b = lp.get(s, {}), cp.get(s, {})
        d = adiff(a.get("response_e"), b.get("response_e"))
        add("probe_response_e[seed=%s]" % s, a.get("response_e"), b.get("response_e"), d, "abs", "<= 1e-6 e", d <= TOL_E)
        add("probe_n_reassigned[seed=%s]" % s, a.get("n_reassigned"), b.get("n_reassigned"),
            adiff(a.get("n_reassigned"), b.get("n_reassigned")), "abs", "informational", True)
    # rungs
    lr = {(r["codec"], r["nominal_tolerance_relative"]): r for r in lap.get("rows", [])}
    cr = {(r["codec"], r["nominal_tolerance_relative"]): r for r in cld.get("rows", [])}
    add("evaluated_rungs", len(lr), len(cr), "", "equal", "identical set", set(lr) == set(cr))
    for k in sorted(set(lr) | set(cr), key=lambda k: (k[0], k[1])):
        a, b = lr.get(k), cr.get(k)
        tag = "%s %g" % k
        if a is None or b is None:
            add("rung[%s] present" % tag, a is not None, b is not None, "", "equal", "identical set", False)
            continue
        add("rung[%s] status" % tag, a.get("status"), b.get("status"), "", "equal", "identical", a.get("status") == b.get("status"))
        add("rung[%s] certifiable_error" % tag, a.get("certifiable_error"), b.get("certifiable_error"), "", "equal",
            "identical", bool(a.get("certifiable_error")) == bool(b.get("certifiable_error")))
        for t in TAUS:
            ca, cb = certified(a, t), certified(b, t)
            add("rung[%s] certified@%s" % (tag, t), ca, cb, "", "equal", "identical", ca == cb)
        d = adiff(a.get("bader_error_e"), b.get("bader_error_e"))
        add("rung[%s] bader_error_e" % tag, a.get("bader_error_e"), b.get("bader_error_e"), d, "abs", "<= 1e-6 e", d <= TOL_E)
        if a.get("status") == "OK" or b.get("status") == "OK":
            d = rdiff(a.get("compressed_bytes"), b.get("compressed_bytes"))
            add("rung[%s] compressed_bytes" % tag, a.get("compressed_bytes"), b.get("compressed_bytes"), d, "rel",
                "<= 0.1 %", d <= TOL_BYTES_REL)
            add("rung[%s] realized_Linf" % tag, a.get("realized_Linf"), b.get("realized_Linf"),
                adiff(a.get("realized_Linf"), b.get("realized_Linf")), "abs", "informational", True)
            add("rung[%s] bound_respected" % tag, a.get("bound_respected"), b.get("bound_respected"), "", "equal",
                "informational", a.get("bound_respected") == b.get("bound_respected"))
            add("rung[%s] n_reassigned" % tag, a.get("n_reassigned"), b.get("n_reassigned"),
                adiff(a.get("n_reassigned"), b.get("n_reassigned")), "abs", "informational", True)
            add("rung[%s] codec_config" % tag, a.get("codec_config"), b.get("codec_config"), "", "equal", "informational",
                a.get("codec_config") == b.get("codec_config"))
        else:
            add("rung[%s] error" % tag, (a.get("error") or "")[:80], (b.get("error") or "")[:80], "", "equal", "informational",
                a.get("error") == b.get("error"))
    # writer choice
    lw, cw = lap.get("writer_choice") or {}, cld.get("writer_choice") or {}
    for t in TAUS:
        a, b = lw.get(t), cw.get(t)
        ka = (a["codec"], a["rel"]) if a else None
        kb = (b["codec"], b["rel"]) if b else None
        add("writer_choice@%s" % t, "%s %g" % ka if ka else "none", "%s %g" % kb if kb else "none", "", "equal",
            "identical (codec and rung)", ka == kb)
        if a and b:
            d = rdiff(a["compressed_bytes"], b["compressed_bytes"])
            add("writer_choice@%s compressed_bytes" % t, a["compressed_bytes"], b["compressed_bytes"], d, "rel", "<= 0.1 %",
                d <= TOL_BYTES_REL)
    return rows, dict(task_id=tid, compared=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--laptop", type=Path, required=True)
    ap.add_argument("--cloud", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--ids", nargs="+", default=list(CONSISTENCY_IDS))
    a = ap.parse_args()
    if tuple(a.ids) != CONSISTENCY_IDS:
        raise SystemExit("the consistency objects are fixed by DEVIATIONS.md 7: %s" % " ".join(CONSISTENCY_IDS))
    all_rows, summ = [], []
    for tid in a.ids:
        lap = json.load(open(a.laptop / (tid + ".json"), encoding="utf-8"))
        cp = a.cloud / (tid + ".json")
        cld = json.load(open(cp, encoding="utf-8")) if cp.exists() else dict(status="MISSING")
        rows, s = compare(tid, lap, cld)
        crit = [r for r in rows if r["criterion"] != "informational"]
        s.update(stratum=lap.get("stratum"), laptop_status=lap.get("status"), cloud_status=cld.get("status"),
                 n_checks=len(crit), n_failed=sum(not r["passes"] for r in crit),
                 laptop_wall_min=lap.get("wall_seconds", 0) / 60, cloud_wall_min=(cld.get("wall_seconds") or 0) / 60)
        for key, sel in (("max_abs_floor_e", lambda r: r["field"] == "floor_e"),
                         ("max_abs_probe_e", lambda r: r["field"].startswith("probe_response_e")),
                         ("max_abs_rung_bader_e", lambda r: r["field"].endswith("bader_error_e")),
                         ("max_rel_rung_bytes", lambda r: r["field"].startswith("rung[") and r["field"].endswith("compressed_bytes"))):
            v = [float(r["diff"]) for r in rows if sel(r) and r["diff"] != ""]
            s[key] = max(v) if v else None
        all_rows += rows
        summ.append(s)
    agree = all(s["compared"] and s["n_failed"] == 0 for s in summ)

    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "consistency").mkdir(exist_ok=True)
    with open(a.out_dir / "consistency" / "consistency_fields.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_rows[0]))
        w.writeheader()
        w.writerows(all_rows)

    def largest(sel, kind):
        cand = [r for r in all_rows if sel(r) and r["diff"] != "" and r["diff_kind"] == kind]
        if not cand:
            return None
        return max(cand, key=lambda r: float(r["diff"]))

    groups = [
        ("floor f_m (e)", lambda r: r["field"] == "floor_e", "abs", "<= 1e-6 e"),
        ("probe response (e)", lambda r: r["field"].startswith("probe_response_e"), "abs", "<= 1e-6 e"),
        ("rung Bader error (e)", lambda r: r["field"].startswith("rung[") and r["field"].endswith("bader_error_e"), "abs", "<= 1e-6 e"),
        ("rung compressed bytes (relative)", lambda r: r["field"].startswith("rung[") and r["field"].endswith("compressed_bytes"), "rel", "<= 0.1 %"),
        ("writer-choice compressed bytes (relative)", lambda r: r["field"].startswith("writer_choice") and r["field"].endswith("compressed_bytes"), "rel", "<= 0.1 %"),
        ("epsilon (field units)", lambda r: r["field"] == "epsilon", "abs", "informational"),
        ("value range ptp", lambda r: r["field"] == "value_ptp", "abs", "informational"),
        ("lossless bytes (relative)", lambda r: r["field"] == "lossless_bytes", "rel", "informational"),
        ("rung realized L-inf", lambda r: r["field"].endswith("realized_Linf"), "abs", "informational"),
        ("probe basin reassignments (voxels)", lambda r: r["field"].startswith("probe_n_reassigned"), "abs", "informational"),
        ("rung basin reassignments (voxels)", lambda r: r["field"].startswith("rung[") and r["field"].endswith("n_reassigned"), "abs", "informational"),
    ]
    exact = [
        ("eligibility at 1e-4, 1e-3, 1e-2 e", lambda r: r["field"].startswith("eligible@")),
        ("evaluated rung set", lambda r: r["field"] in ("evaluated_rungs",) or r["field"].endswith(" present")),
        ("rung status", lambda r: r["field"].startswith("rung[") and r["field"].endswith(" status")),
        ("rung certifiable_error flag", lambda r: r["field"].endswith(" certifiable_error")),
        ("rung certified at each tau", lambda r: "certified@" in r["field"]),
        ("writer choice (codec, rung) at each tau", lambda r: r["field"].startswith("writer_choice@") and r["field"].count(" ") == 0),
    ]
    L = ["# WP-F platform consistency: laptop vs GitHub-hosted ubuntu-24.04", "",
         "Rule: `DEVIATIONS.md` 7 (definitions in 8). Objects: %s. Laptop checkpoints: `results_laptop/checkpoints/` (as recorded); "
         "cloud checkpoints: `results_cloud/consistency/checkpoints/`. Every compared field: `consistency/consistency_fields.csv`." % ", ".join(a.ids),
         "", "**Verdict: %s** — %d of %d agreement checks pass." % (
             "AGREE" if agree else "DISAGREE", sum(s.get("n_checks", 0) - s.get("n_failed", 0) for s in summ),
             sum(s.get("n_checks", 0) for s in summ)),
         "", "## Per object", "",
         "| object | stratum | laptop / cloud status | checks | failed | max abs Δ floor (e) | max abs Δ probe (e) | max abs Δ rung Bader error (e) | max rel Δ rung bytes | wall laptop / cloud (min) |",
         "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for s in summ:
        L.append("| %s | %s | %s / %s | %d | %d | %s | %s | %s | %s | %.1f / %.1f |" % (
            s["task_id"], s["stratum"], s["laptop_status"], s["cloud_status"], s.get("n_checks", 0), s.get("n_failed", 0),
            fmt(s.get("max_abs_floor_e")), fmt(s.get("max_abs_probe_e")), fmt(s.get("max_abs_rung_bader_e")),
            fmt(s.get("max_rel_rung_bytes")), s["laptop_wall_min"], s["cloud_wall_min"]))
    L += ["", "## Exact-match fields", "", "| field | checks | identical |", "|---|---:|---:|"]
    for name, sel in exact:
        sub = [r for r in all_rows if sel(r)]
        L.append("| %s | %d | %d |" % (name, len(sub), sum(r["passes"] for r in sub)))
    L += ["", "## Largest differences", "", "| field | criterion | values compared | largest difference | where | laptop | cloud |",
          "|---|---|---:|---:|---|---|---|"]
    for name, sel, kind, crit in groups:
        sub = [r for r in all_rows if sel(r) and r["diff"] != ""]
        r = largest(sel, kind)
        if r is None:
            L.append("| %s | %s | 0 | | | | |" % (name, crit))
            continue
        L.append("| %s | %s | %d | %s | %s %s | %s | %s |" % (name, crit, len(sub), r["diff"], r["task_id"], r["field"],
                                                             r["laptop"], r["cloud"]))
    bad = [r for r in all_rows if r["criterion"] != "informational" and not r["passes"]]
    L += ["", "## Failed checks", ""]
    if bad:
        L += ["| object | field | laptop | cloud | difference | criterion |", "|---|---|---|---|---:|---|"]
        L += ["| %s | %s | %s | %s | %s | %s |" % (r["task_id"], r["field"], r["laptop"], r["cloud"], r["diff"], r["criterion"]) for r in bad]
    else:
        L.append("None.")
    info_bad = [r for r in all_rows if r["criterion"] == "informational" and r["diff_kind"] == "equal" and not r["passes"]]
    L += ["", "Informational fields that differ (not part of the rule): %s." % (
        ", ".join("%s %s" % (r["task_id"], r["field"]) for r in info_bad) if info_bad else "none")]
    (a.out_dir / "CONSISTENCY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    json.dump(dict(agree=agree, rule="DEVIATIONS.md 7", ids=a.ids, objects=summ,
                   failed_checks=[{k: r[k] for k in ("task_id", "field", "laptop", "cloud", "diff", "criterion")} for r in bad]),
              open(a.out_dir / "consistency" / "CONSISTENCY.json", "w", encoding="utf-8"), indent=1)
    print("\n".join(L[:12]))
    print("VERDICT", "AGREE" if agree else "DISAGREE")


if __name__ == "__main__":
    main()
