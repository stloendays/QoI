#!/usr/bin/env python3
"""Write RESULTS.md from CRITERIA.json (evaluate_criteria.py), results/manifest/SUMMARY.json, the descriptive numbers
of describe_results.py and the run metadata given on the command line. Numbers only; no interpretation beyond the
criteria. Usage: write_results_md.py --run-id ID --head SHA --results-commit SHA --window "start–end UTC"
--conclusion success --jobs "21/21" --tests "..." """
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import describe_results as dr

HERE = Path(__file__).resolve().parent
RES = HERE / "results" / "manifest"


def f3(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def f1(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.1f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    for k in ("run-id", "head", "results-commit", "window", "conclusion", "jobs", "tests"):
        ap.add_argument(f"--{k}", required=True)
    a = ap.parse_args()
    C = json.loads((HERE / "CRITERIA.json").read_text(encoding="utf-8"))["primary"]
    S = json.loads((RES / "SUMMARY.json").read_text(encoding="utf-8"))
    D = dr.describe(RES)
    man = list(csv.DictReader(open(HERE / "manifest.csv", encoding="utf-8")))
    dl = list(csv.DictReader(open(RES / "release_downloads.csv", encoding="utf-8")))
    coh = {r["material_id"]: r for r in csv.DictReader(open(HERE / "cohort.csv", encoding="utf-8"))}
    dl_ok = sum(1 for r in dl if r["sha256"] == coh[r["material_id"]][f"{r['file']}_gz_sha256"]
                and r["bytes"] == coh[r["material_id"]][f"{r['file']}_gz_bytes"])
    n = C["n_planned"]
    c1, c2, c3 = C["criterion_1"], C["criterion_2"], C["criterion_3"]
    yn = lambda b: "yes" if b else "**no**"  # noqa: E731
    na = C.get("not_analysed", {})
    L = [f"# QOAC-HB self-computed slab cohort (N = {n}) — frozen criteria (PROTOCOL.md `ae0076a`)", "",
         "Cohort (PROTOCOL.md sections 1–6, `COHORT.md`): MP summary 2026-09-28 -> 5,524 ranked formulas; 62 visited, 40 "
         "slabs drawn; 39 converged (ALGO = Normal), 1 NELM twice after the ALGO = All fallback (draw rank 11, HfMnF6); "
         f"input QC 39/39 pass; **N = {n}** (draw ranks 1–10 and 12–33), "
         f"npoints {min(int(m['npoints']) for m in man):,}–{max(int(m['npoints']) for m in man):,}, "
         f"{min(int(m['natoms']) for m in man)}–{max(int(m['natoms']) for m in man)} atoms. Density files: GitHub release "
         "`data-hb-selfslab-20261008` (96 assets, 1,805,055,269 bytes), served by `run_joint_selfslab.py` (DEVIATIONS D2); "
         f"{dl_ok}/{len(dl)} downloads recorded in `results/manifest/release_downloads.csv` match the `cohort.csv` byte "
         "count and SHA-256.", "",
         f"CI run {a.run_id} (workflow `hb_selfslab_cohort.yml`, head `{a.head}`, {a.window}, conclusion {a.conclusion}, "
         f"{a.jobs} jobs); results commit `{a.results_commit}`. {S['materials_success']}/{S['materials']} materials "
         f"successful, {len(S['materials_failed'])} FAILED, {len(S['materials_missing'])} MISSING, "
         f"{S['setting_failures']} setting failures. Criteria evaluated with "
         "`analysis/hb_slab_aeccar_cohort_20261007/evaluate_criteria.py` in place and unchanged (committed bytes SHA-256 "
         f"`0729424b…`, primary population only, `CRITERIA.json` in this directory); {a.tests}. "
         "Bootstrap: seed 20261007, 10,000 resamples of the median.", "",
         f"## Primary analysis (N = {n}, all planned)", "",
         "| criterion | result | threshold | pass |", "|---|---|---|---|",
         f"| 1. analyzable and jointly certified (R3, best post, all three tau_B) | {c1['value']}/{c1['n']} | "
         f">= ceil({n} x 46/48) = {c1['required']}/{n} | {yn(c1['pass'])} |",
         f"| 2. joint overhead at tau_B = 1e-4 (CR_hartree_only / CR_joint) | n = {c2['n']}, median {f3(c2.get('median'))}, "
         f"CI [{f3(c2.get('ci_low'))}, {f3(c2.get('ci_high'))}] | <= 1.10, CI upper <= 1.15 | {yn(c2['pass'])} |",
         f"| 3. utility at tau_B = 1e-4 (R3 / max of J, T1, GF at their best posts) | {c3['wins']}/{c3['n']} wins, median "
         f"{f3(c3.get('median'))}, CI [{f3(c3.get('ci_low'))}, {f3(c3.get('ci_high'))}], min {f3(c3.get('min'))} | "
         f">= ceil({n} x 36/48) = {c3['required_wins']}/{n}, > 1.10, CI lower > 1.00 | {yn(c3['pass'])} |", "",
         f"**Confirmatory {C['verdict']}** on the population of N = {n} slabs (criteria 1, 2 and 3: "
         f"{'pass' if c1['pass'] else 'fail'}, {'pass' if c2['pass'] else 'fail'}, {'pass' if c3['pass'] else 'fail'}). "
         f"Sole certifiers: {c3['n_sole_certifier']}/{c3['n_ratio']}.", "",
         "## Failures", ""]
    if S["materials_failed"] or S["materials_missing"] or na:
        L.append(f"- Materials: FAILED {S['materials_failed']}, MISSING {S['materials_missing']}; not analysed: {na}.")
    else:
        L.append(f"- Materials: none (0/{n} FAILED or MISSING).")
    L.append(f"- Settings: {S['setting_failures']} (`failures.csv`).")
    import pandas as pd
    B = pd.read_csv(RES / "joint_v2_best_post.csv", dtype={"material_id": str})
    A = pd.read_csv(RES / "bader_attempts.csv", dtype={"material_id": str})
    r3 = B[B.base == "R3"].pivot(index="material_id", columns="tau_bader", values="best_joint_post")
    miss = [m["material_id"] for m in man if m["material_id"] in r3.index and r3.loc[m["material_id"]].isna().any()]
    if miss:
        L.append(f"- Criterion 1 misses (R3 at its best joint post-processor not certified at all three tau_B), "
                 f"{len(miss)}/{n}, all SUCCESS materials, listed with every R3 Bader attempt of the material:")
        L += ["", "| material_id | formula | atoms | npoints | R3 certified at 1e-3 / 1e-4 / 1e-5 | R3 attempts | "
                  "smallest R3 Bader error (e) | largest reassigned fraction | J, T1, GF certified at all three tau_B |",
              "|---|---|---:|---:|---|---:|---:|---:|---|"]
        mi = {m["material_id"]: m for m in man}
        for mid in miss:
            a = A[(A.material_id == mid) & (A.base == "R3")]
            row = r3.loc[mid]
            cert = " / ".join("yes" if pd.notna(row.get(t)) else "no" for t in (1e-3, 1e-4, 1e-5))
            oth = B[(B.material_id == mid) & B.base.isin(["J", "T1", "GF"])]
            ok3 = all(oth[oth.base == b].best_joint_post.notna().sum() == 3 for b in ("J", "T1", "GF"))
            L.append(f"| `{mid}` | {mi[mid]['formula']} | {mi[mid]['natoms']} | {int(mi[mid]['npoints']):,} | {cert} | "
                     f"{len(a)} | {a.bader_error_e.min():.6f} | {a.reassigned_frac.max():g} | {'yes' if ok3 else 'no'} |")
        L.append("")
    U = D["uncertified_streams"]
    parts = []
    for b in dr.BASES:
        v = [U["by_base_tau"][f"{b}|{t:g}"] for t in dr.TAUS]
        if sum(v):
            parts.append(f"{b} {v[0]} at 1e-3, {v[1]} at 1e-4, {v[2]} at 1e-5")
    L.append(f"- Uncertified (base, post, tau_B) streams after the at most 5 Bader attempts, counted by the aggregator as "
             f"results: {U['n']} of {U['of']} non-`hartree_only` streams ({'; '.join(parts) or 'none'}); R3 at its best "
             f"joint post-processor: {U['r3_at_best_post']}.")
    T = D["by_tau"]
    L += ["", f"## Descriptive ({D['materials']['success']} analysed slabs)", "",
          "- Certified R3 best-post streams: " + ", ".join(
              f"{T[k]['r3_best_post_certified']}/{n} at {k}" for k in ("0.001", "0.0001", "1e-05"))
          + f"; largest Bader error / tau_B {f3(max((T[k]['max_bader_error_over_tau'] or 0) for k in T))}, largest "
          f"reassigned-voxel fraction {max((T[k]['max_reassigned_frac'] or 0) for k in T):g}.",
          "- R3 best joint post-processor: " + "; ".join(
              f"{k}: " + ", ".join(f"`{p}` {c}" for p, c in sorted(T[k]['r3_best_post_counts'].items(), key=lambda x: -x[1]))
              for k in ("0.001", "0.0001", "1e-05")) + ".",
          "- Median joint overhead (R3): " + ", ".join(
              f"{f3(T[k]['median_joint_overhead'])} at {k} (n = {T[k]['n_joint_overhead']})" for k in ("0.001", "0.0001", "1e-05"))
          + ". Median R3 joint CR: " + ", ".join(f"{f1(T[k]['median_r3_joint_cr'])} at {k}" for k in ("0.001", "0.0001", "1e-05")) + ".",
          "- CTP decisions (R3, evaluated rows): projected " + ", ".join(
              f"{T[k]['ctp_projected']}/{T[k]['ctp_evaluated']} at {k}" for k in ("0.001", "0.0001", "1e-05")) + ".",
          "- Median joint CR at tau_B = 1e-4 (certified materials): " + ", ".join(
              f"{b} {f1(T['0.0001']['median_joint_cr_by_base'][b])} ({T['0.0001']['n_certified_by_base'][b]}/{n})"
              for b in dr.BASES) + ".",
          f"- Utility ratio at 1e-4: {c3['wins']}/{c3['n_ratio']} > 1, min {f3(c3.get('min'))}.",
          f"- HB runtime per material on a runner: {D['materials']['seconds_min']:.0f}–{D['materials']['seconds_max']:.0f} s "
          f"(median {D['materials']['seconds_median']:.0f} s).", ""]
    (HERE / "RESULTS.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    (HERE / "DESCRIPTIVE.json").write_text(json.dumps(D, indent=1) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
