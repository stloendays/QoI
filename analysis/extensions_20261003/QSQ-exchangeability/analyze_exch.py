"""Pre-declared analyses A–D of PROTOCOL.md for the QSQ probe-exchangeability package."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CKPT = Path(r"D:\Research\QoI-ext-cache\QSQ-exch\checkpoints")
TAUS = (1e-4, 1e-3, 1e-2)
N_PANEL = 5
BOUND = N_PANEL**N_PANEL / (N_PANEL + 1) ** (N_PANEL + 1)
BOOT, BOOT_SEED = 2000, 20261003


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kappa(a: np.ndarray, b: np.ndarray) -> float:
    po = float(np.mean(a == b))
    pe = float(np.mean(a) * np.mean(b) + (1 - np.mean(a)) * (1 - np.mean(b)))
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> int:
    t0 = time.time()
    floor_csv = REPO / "stability" / "stability_floor_A1.csv"
    outcomes_csv = REPO / "validation" / "qsq_prospective" / "p2_fresh_probes" / "outcomes.csv"
    frozen_floor = {r["material_id"]: float(r["stability_floor_A1_e"]) for r in read_csv(floor_csv)}
    fresh: dict[str, list[float]] = {}
    for r in read_csv(outcomes_csv):
        fresh.setdefault(r["material_id"], []).append(float(r["bader_response_max_e"]))

    probes, failures, status = [], [], {}
    panel_f: dict[str, list[float]] = {}
    panel_i: dict[str, list[float]] = {}
    for ck in sorted(CKPT.glob("*.json")):
        p = json.loads(ck.read_text(encoding="utf-8"))
        mid = p["material_id"]
        status[mid] = p["status"]
        failures.extend(p.get("failures", []))
        for q in p["probes"]:
            probes.append(q)
            (panel_f if q["family"] == "frozen_qsq" else panel_i).setdefault(mid, []).append(q["bader_response_max_e"])
    mats = sorted(m for m in status if len(panel_f.get(m, [])) == N_PANEL and len(panel_i.get(m, [])) == N_PANEL
                  and len(fresh.get(m, [])) == 59)

    rows, summary = [], []
    for m in mats:
        ff, fi = max(panel_f[m]), max(panel_i[m])
        rows.append({
            "material_id": m, "frozen_floor_e": frozen_floor[m], "recomputed_floor_F_e": ff,
            "abs_diff_F_vs_frozen_e": abs(ff - frozen_floor[m]), "floor_I_e": fi,
            "fresh_above_F": sum(x > ff for x in fresh[m]), "fresh_above_I": sum(x > fi for x in fresh[m]),
            "n_fresh": len(fresh[m]),
        })

    def add(analysis: str, metric: str, value: float, lo: float | None = None, hi: float | None = None,
            num: int | None = None, den: int | None = None, note: str = "") -> None:
        summary.append({"analysis": analysis, "metric": metric, "value": value, "ci95_low": lo, "ci95_high": hi,
                        "numerator": num, "denominator": den, "note": note})

    # A. floor reproduction
    exact = sum(r["abs_diff_F_vs_frozen_e"] <= 1e-9 for r in rows)
    add("A_floor_reproduction", "exact_floor_matches", exact / len(rows), num=exact, den=len(rows), note="|diff| <= 1e-9 e")
    add("A_floor_reproduction", "max_abs_floor_diff_e", max(r["abs_diff_F_vs_frozen_e"] for r in rows))
    for t in TAUS:
        agree = sum((r["frozen_floor_e"] < t) == (r["recomputed_floor_F_e"] < t) for r in rows)
        add("A_floor_reproduction", f"eligibility_agreement_tau_{t:g}", agree / len(rows), num=agree, den=len(rows))

    # B. exchangeability: fraction of fresh responses above each panel's maximum
    rng = np.random.default_rng(BOOT_SEED)
    above_f = np.array([r["fresh_above_F"] for r in rows], float)
    above_i = np.array([r["fresh_above_I"] for r in rows], float)
    nfr = np.array([r["n_fresh"] for r in rows], float)
    idx = rng.integers(0, len(rows), size=(BOOT, len(rows)))
    for name, arr in (("panel_I_independent", above_i), ("panel_F_frozen_shared", above_f)):
        est = arr.sum() / nfr.sum()
        boot = arr[idx].sum(1) / nfr[idx].sum(1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        accepted = lo <= 1 / 6 <= hi
        add("B_exchangeability", f"P_fresh_above_max5_{name}", est, lo, hi, int(arr.sum()), int(nfr.sum()),
            ("ACCEPTED: CI contains 1/6" if accepted else "CI excludes 1/6") if name == "panel_I_independent"
            else "reported alongside; shared seeds")

    # C. admission bound and D. panel agreement
    for name, floors in (("panel_F_frozen_shared", "recomputed_floor_F_e"), ("panel_I_independent", "floor_I_e")):
        for t in TAUS:
            joint = sum(sum(x >= t for x in fresh[r["material_id"]]) for r in rows if r[floors] < t)
            admitted_trials = sum(len(fresh[r["material_id"]]) for r in rows if r[floors] < t)
            n_adm = sum(r[floors] < t for r in rows)
            add("C_admission_bound", f"joint_rate_{name}_tau_{t:g}", joint / nfr.sum(), num=joint, den=int(nfr.sum()),
                note=f"bound n=5: {BOUND:.4f}")
            add("C_admission_bound", f"conditional_risk_{name}_tau_{t:g}",
                joint / admitted_trials if admitted_trials else float("nan"), num=joint, den=admitted_trials)
            add("C_admission_bound", f"coverage_{name}_tau_{t:g}", n_adm / len(rows), num=n_adm, den=len(rows))
    for t in TAUS:
        a = np.array([r["recomputed_floor_F_e"] < t for r in rows])
        b = np.array([r["floor_I_e"] < t for r in rows])
        add("D_panel_agreement", f"agreement_tau_{t:g}", float(np.mean(a == b)), num=int(np.sum(a == b)), den=len(rows))
        add("D_panel_agreement", f"kappa_tau_{t:g}", kappa(a, b))

    with (HERE / "probes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(probes[0]))
        w.writeheader()
        w.writerows(sorted(probes, key=lambda q: (q["material_id"], q["family"], int(q["seed_label"]))))
    with (HERE / "material_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (HERE / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    with (HERE / "failures.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["material_id", "family", "seed_label", "error"])
        w.writeheader()
        w.writerows(failures)

    s = {r["metric"]: r for r in summary}
    lines = [
        "# QSQ probe exchangeability — results",
        "",
        f"Materials analysed: **{len(rows)}/254** (material-level failures: {sum(v != 'SUCCESS' for v in status.values())};"
        f" probe failures: {len(failures)}). Protocol: `PROTOCOL.md`.",
        "",
        "## A. Local recomputation of the frozen five-seed floor",
        "",
        f"- exact floor matches (|Δ| ≤ 1e-9 e): **{s['exact_floor_matches']['numerator']}/{len(rows)}**;"
        f" max |Δ| = {s['max_abs_floor_diff_e']['value']:.3g} e",
    ]
    for t in TAUS:
        r = s[f"eligibility_agreement_tau_{t:g}"]
        lines.append(f"- eligibility agreement at τ = {t:g} e: **{r['numerator']}/{r['denominator']}**")
    bi, bf = s["P_fresh_above_max5_panel_I_independent"], s["P_fresh_above_max5_panel_F_frozen_shared"]
    lines += [
        "",
        "## B. Exchangeability (fresh responses above the five-probe maximum; exchangeable value 1/6 = 16.67%)",
        "",
        f"- independent per-material streams: **{100*bi['value']:.2f}%** ({bi['numerator']}/{bi['denominator']}),"
        f" 95% CI {100*bi['ci95_low']:.2f}–{100*bi['ci95_high']:.2f}% → **{bi['note']}**",
        f"- frozen shared seeds: {100*bf['value']:.2f}% ({bf['numerator']}/{bf['denominator']}),"
        f" 95% CI {100*bf['ci95_low']:.2f}–{100*bf['ci95_high']:.2f}%",
        "",
        f"## C. Joint admission-and-exceedance rate (bound for n = 5: {100*BOUND:.2f}%)",
        "",
        "| τ (e) | panel | joint rate | conditional risk among admitted | coverage |",
        "|---:|---|---:|---:|---:|",
    ]
    for t in TAUS:
        for name, label in (("panel_F_frozen_shared", "frozen (shared seeds)"), ("panel_I_independent", "independent streams")):
            j, c, v = (s[f"{k}_{name}_tau_{t:g}"] for k in ("joint_rate", "conditional_risk", "coverage"))
            lines.append(f"| {t:g} | {label} | {100*j['value']:.3f}% ({j['numerator']}/{j['denominator']}) |"
                         f" {100*c['value']:.3f}% | {v['numerator']}/{v['denominator']} |")
    lines += ["", "## D. Agreement between the frozen and independent panels", ""]
    for t in TAUS:
        a, k = s[f"agreement_tau_{t:g}"], s[f"kappa_tau_{t:g}"]
        lines.append(f"- τ = {t:g} e: agreement {a['numerator']}/{a['denominator']}, κ = {k['value']:.3f}")
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    prov = {
        "script": "analyze_exch.py", "python": sys.version, "platform": platform.platform(),
        "inputs_sha256": {str(p.relative_to(REPO)): sha256_file(p) for p in (floor_csv, outcomes_csv)},
        "checkpoint_dir": str(CKPT), "n_checkpoints": len(status), "bootstrap": [BOOT, BOOT_SEED],
        "bound_n5": BOUND, "wall_seconds": time.time() - t0,
    }
    (HERE / "provenance.json").write_text(json.dumps(prov, indent=1), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
