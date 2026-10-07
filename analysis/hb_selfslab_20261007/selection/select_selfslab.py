#!/usr/bin/env python3
"""Eligibility funnel, ranking and slab draw of the self-computed slab cohort (PROTOCOL.md sections 1-6).

Phases
  funnel  steps 2-4: eligibility (counts at every step), exclusions, one material per reduced formula, hash ranking.
          Outputs selection/funnel.json and selection/ranked.csv.gz (every ranked material).
  draw    step 5-6: walk ranked.csv.gz in rank order and build slabs until 40 materials have an accepted slab.
          Outputs selection/draw_materials.csv (every visited material and its decision), selection/draw_slabs.csv
          (every termination evaluated), selection/drawn.csv (the 40) and selection/slabs/<material_id>.json.
  check   build slabs for named materials only (no ranking, no exclusion), for testing on used materials.

Only metadata and pymatgen structure operations; no DFT, compression, Hartree or Bader quantity.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import math
import multiprocessing as mp
import platform
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SALT = "QOAC-HB-SELFSLAB-20261007|"
PARQUET_NAME = "part-00000-2cc5f2cc-2a79-4051-b013-2f9dec6a302e-c000.zstd.parquet"
PARQUET_SHA256 = "669e5a3bdf1644633f8c771a98b434bf449451a9aa6ce2556d0901ba1dff235b"
PARQUET_BYTES = 414_503_512
F_BLOCK = set(range(57, 72)) | set(range(89, 104))          # La-Lu, Ac-Lr
NOBLE_GASES = {"He", "Ne", "Ar", "Kr", "Xe", "Rn", "Og"}
MILLERS = [(0, 0, 1), (1, 1, 0), (1, 1, 1), (1, 0, 0)]
MIN_SLAB, MIN_VAC = 10.0, 15.0
MAX_ATOMS, MAX_NPOINTS = 40, 5_832_000
N_DRAW = 40
KSPACING_INV = 0.25                                           # Angstrom^-1
WORKERS = 6
BATCH = 12
TIMEOUT_S = 900
# MPRelaxSet POTCAR symbols absent from the Vanda PBE PAW library (potpaw_PBE.54, directory listing of 2026-10-08).
ABSENT_ON_VANDA = {"W_pv"}


def h(x: str) -> str:
    return hashlib.sha256((SALT + x).encode("utf-8")).hexdigest()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def sha256_file(p: Path) -> str:
    d = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            d.update(chunk)
    return d.hexdigest()


def sha256_text(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def env() -> dict:
    from importlib.metadata import version
    return {"python": platform.python_version(), "platform": platform.platform(),
            **{p: version(p) for p in ("pymatgen", "pyarrow", "numpy", "spglib", "pandas")}}


def kpoints(abc) -> list[int]:
    return [max(1, math.ceil(2 * math.pi / (abc[0] * KSPACING_INV))),
            max(1, math.ceil(2 * math.pi / (abc[1] * KSPACING_INV))), 1]


# ---------------------------------------------------------------------------------------------------------- funnel
def prim_nsites(struct_dict) -> int:
    from pymatgen.core import Structure
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    s = Structure.from_dict(struct_dict)
    if len(s) <= 8:
        return len(s)       # a primitive cell never has more sites than the stored cell
    p = SpacegroupAnalyzer(s, symprec=0.1).find_primitive()
    return len(p) if p is not None else len(s)


def phase_funnel(parquet: Path, out: Path) -> None:
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from pymatgen.core import Composition, Element
    from pymatgen.io.vasp.sets import MPRelaxSet

    assert parquet.stat().st_size == PARQUET_BYTES, "parquet size differs from the protocol"
    digest = sha256_file(parquet)
    assert digest == PARQUET_SHA256, "parquet SHA-256 differs from the protocol"
    potcar = MPRelaxSet.CONFIG["POTCAR"]
    cols = ["material_id", "energy_above_hull", "is_magnetic", "ordering", "nelements", "nsites", "elements",
            "formula_pretty"]
    t = pq.read_table(parquet, columns=cols)
    counts = {"0_summary_rows": t.num_rows}
    m1 = pc.fill_null(pc.equal(t["energy_above_hull"], 0.0), False)
    t1 = t.filter(m1)
    counts["1_energy_above_hull_eq_0"] = t1.num_rows
    cross = {}
    for mag, order in zip(t1["is_magnetic"].to_pylist(), t1["ordering"].to_pylist()):
        k = f"is_magnetic={mag}|ordering={order}"
        cross[k] = cross.get(k, 0) + 1
    t2 = t1.filter(pc.fill_null(pc.equal(t1["is_magnetic"], False), False))
    counts["2_is_magnetic_false"] = t2.num_rows
    t3 = t2.filter(pc.less_equal(t2["nelements"], 3))
    counts["3_nelements_1_to_3"] = t3.num_rows
    keep = set(t3["material_id"].to_pylist())
    # step 4 needs structures: read them only for the rows that survive steps 1-3
    ts = pq.read_table(parquet, columns=["material_id", "structure"],
                       filters=[("energy_above_hull", "=", 0.0), ("is_magnetic", "=", False), ("nelements", "<=", 3)])
    sdict = {m: s for m, s in zip(ts["material_id"].to_pylist(), ts["structure"].to_pylist()) if m in keep}
    del ts
    assert len(sdict) == len(keep)
    rows = t3.to_pylist()
    with mp.Pool(WORKERS) as pool:
        prim = pool.map(prim_nsites, [sdict[r["material_id"]] for r in rows], chunksize=64)
    for r, p in zip(rows, prim):
        r["prim_nsites"] = p
    rows = [r for r in rows if r["prim_nsites"] <= 8]
    counts["4_primitive_nsites_le_8"] = len(rows)
    rows = [r for r in rows if not any(Element(e).Z in F_BLOCK or e in NOBLE_GASES for e in r["elements"])]
    counts["5_no_f_block_no_noble_gas"] = len(rows)
    rows = [r for r in rows if all(e in potcar for e in r["elements"])]
    counts["6_mprelaxset_potcar_for_every_element"] = len(rows)

    from pymatgen.core import Structure
    ex_ids = {r["id"] for r in csv.DictReader(open(HERE / "exclusion_ids_union.csv", encoding="utf-8"))}
    ex_f = {r["reduced_formula"] for r in csv.DictReader(open(HERE / "exclusion_formulas_union.csv", encoding="utf-8"))}
    for r in rows:
        st = Structure.from_dict(sdict[r["material_id"]])
        r["reduced_formula"] = st.composition.reduced_formula
        r["formula_pretty_reduced"] = Composition(r["formula_pretty"]).reduced_formula
        r["hash"] = h(r["material_id"])
    rows = [r for r in rows if r["material_id"] not in ex_ids]
    counts["7_not_excluded_id"] = len(rows)
    rows = [r for r in rows if r["reduced_formula"] not in ex_f]
    counts["8_not_excluded_formula"] = len(rows)
    best: dict[str, dict] = {}
    for r in rows:
        b = best.get(r["reduced_formula"])
        if b is None or r["hash"] < b["hash"]:
            best[r["reduced_formula"]] = r
    ranked = sorted(best.values(), key=lambda r: r["hash"])
    counts["9_one_per_reduced_formula"] = len(ranked)
    out.mkdir(parents=True, exist_ok=True)
    with gzip.open(out / "ranked.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["rank", "material_id", "reduced_formula", "formula_pretty", "nelements", "nsites", "prim_nsites",
                    "energy_above_hull", "is_magnetic", "ordering", "hash"])
        for i, r in enumerate(ranked, 1):
            w.writerow([i, r["material_id"], r["reduced_formula"], r["formula_pretty"], r["nelements"], r["nsites"],
                        r["prim_nsites"], r["energy_above_hull"], r["is_magnetic"], r["ordering"], r["hash"]])
    (out / "structures_ranked.json.gz").write_bytes(gzip.compress(json.dumps(
        {r["material_id"]: sdict[r["material_id"]] for r in ranked}, default=str).encode("utf-8"), mtime=0))
    log = {"phase": "funnel", "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "parquet": {"name": PARQUET_NAME, "bytes": PARQUET_BYTES, "sha256": digest},
           "magnetism_field": "is_magnetic == False",
           "is_magnetic_x_ordering_after_step_1": dict(sorted(cross.items())),
           "counts": counts,
           "n_formula_pretty_differs_from_structure_formula": sum(
               1 for r in ranked if r["formula_pretty_reduced"] != r["reduced_formula"]),
           "exclusion_inputs_sha256": {"exclusion_ids_union.csv": sha256_text(HERE / "exclusion_ids_union.csv"),
                                       "exclusion_formulas_union.csv": sha256_text(HERE / "exclusion_formulas_union.csv")},
           "outputs_sha256": {"ranked.csv.gz": sha256_file(out / "ranked.csv.gz"),
                              "structures_ranked.json.gz": sha256_file(out / "structures_ranked.json.gz")},
           "script_sha256": sha256_text(Path(__file__)), "environment": env()}
    (out / "funnel.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


# ------------------------------------------------------------------------------------------------------------ draw
def build_slab(mid: str, struct_dict: dict) -> dict:
    """Section 5 of PROTOCOL.md for one material: the accepted slab (as a dict) or the reason there is none."""
    warnings.filterwarnings("ignore")
    from pymatgen.core import Structure
    from pymatgen.core.surface import SlabGenerator, get_symmetrically_equivalent_miller_indices
    from pymatgen.io.vasp.sets import MPRelaxSet
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    ge = load("grid_estimate", ROOT / "grid_estimate.py")

    t0 = time.time()
    bulk = Structure.from_dict(struct_dict)
    red = bulk.composition.reduced_formula
    conv = SpacegroupAnalyzer(bulk, symprec=0.1).get_conventional_standard_structure()
    conv_ox = conv.copy()
    conv_ox.add_oxidation_state_by_guess()
    oxi = {str(sp): getattr(sp, "oxi_state", 0) for sp in conv_ox.composition}
    terms, tried = [], []
    accepted = None
    for hkl in MILLERS:
        eq = {tuple(int(v) for v in x) for x in get_symmetrically_equivalent_miller_indices(conv, hkl, return_hkil=False)}
        dup = next((t for t in tried if t in eq), None)
        if dup is not None:
            terms.append({"miller": "".join(map(str, hkl)), "termination": "", "status": f"equivalent_to_{''.join(map(str, dup))}"})
            continue
        tried.append(hkl)
        try:
            slabs = SlabGenerator(conv_ox, hkl, min_slab_size=MIN_SLAB, min_vacuum_size=MIN_VAC, center_slab=True,
                                  in_unit_planes=False, primitive=True).get_slabs()
        except Exception as exc:  # noqa: BLE001
            terms.append({"miller": "".join(map(str, hkl)), "termination": "", "status": "generator_error",
                          "error": f"{type(exc).__name__}:{str(exc)[:120]}"})
            continue
        if not slabs:
            terms.append({"miller": "".join(map(str, hkl)), "termination": "", "status": "no_slabs"})
            continue
        for i, s in enumerate(slabs):
            o = s.get_orthogonal_c_slab()
            g, gf, npts = ge.grids(o.lattice.abc, 520.0, "Accurate")
            rec = {"miller": "".join(map(str, hkl)), "termination": i, "shift": f"{s.shift:.6f}",
                   "symmetric": int(o.is_symmetric()), "polar": int(o.is_polar()),
                   "stoichiometric": int(o.composition.element_composition.reduced_formula == red),
                   "natoms": len(o), "a": f"{o.lattice.a:.6f}", "b": f"{o.lattice.b:.6f}", "c": f"{o.lattice.c:.6f}",
                   "gamma": f"{o.lattice.gamma:.4f}", "ng": "x".join(map(str, g)), "ngf": "x".join(map(str, gf)),
                   "npoints_est": npts}
            fail = next((k for k, bad in (("not_symmetric", not rec["symmetric"]), ("polar", rec["polar"]),
                                          ("not_stoichiometric", not rec["stoichiometric"]),
                                          ("natoms_gt_40", rec["natoms"] > MAX_ATOMS),
                                          ("npoints_gt_5832000", npts > MAX_NPOINTS)) if bad), "")
            rec["status"] = fail or "accepted"
            terms.append(rec)
            if not fail:
                o.remove_oxidation_states()
                accepted = (rec, o)
                break
        if accepted:
            break
    res = {"material_id": mid, "reduced_formula": red, "conv_nsites": len(conv), "oxidation_guess": oxi,
           "terminations": terms, "seconds": round(time.time() - t0, 1)}
    if accepted:
        rec, o = accepted
        symbols = [MPRelaxSet.CONFIG["POTCAR"][el.symbol] for el in o.get_sorted_structure().composition.elements]
        res |= {"decision": "accepted", "slab": o.as_dict(), "accepted": rec, "potcar_symbols": symbols,
                "kpoints": kpoints(o.lattice.abc)}
        absent = [p for p in symbols if p in ABSENT_ON_VANDA]
        if absent:
            res |= {"decision": "rejected", "reason": "potcar_symbol_absent_on_vanda:" + ";".join(absent)}
    else:
        res |= {"decision": "rejected", "reason": "no_acceptable_slab"}
    return res


def phase_draw(out: Path, check: list[str] | None = None, check_source: Path | None = None) -> None:
    if check:
        import pyarrow.parquet as pq
        t = pq.read_table(check_source, columns=["material_id", "structure"],
                          filters=[("material_id", "in", check)]).to_pylist()
        order = [{"rank": i + 1, "material_id": r["material_id"]} for i, r in enumerate(t)]
        sdict = {r["material_id"]: r["structure"] for r in t}
    else:
        with gzip.open(HERE / "ranked.csv.gz", "rt", encoding="utf-8") as f:
            order = list(csv.DictReader(f))
        sdict = json.loads(gzip.decompress((HERE / "structures_ranked.json.gz").read_bytes()))
    visited, n_acc, pos = [], 0, 0
    t_start = time.time()
    while n_acc < (len(order) if check else N_DRAW) and pos < len(order):
        batch = order[pos:pos + BATCH]
        pos += len(batch)
        pool = mp.Pool(WORKERS)
        jobs = [pool.apply_async(build_slab, (r["material_id"], sdict[r["material_id"]])) for r in batch]
        results = []
        for r, j in zip(batch, jobs):
            try:
                res = j.get(timeout=TIMEOUT_S)      # each material gets at least TIMEOUT_S of run time
            except mp.TimeoutError:
                res = {"material_id": r["material_id"], "decision": "rejected", "reason": "slab_generation_timeout",
                       "terminations": []}
            except Exception as exc:  # noqa: BLE001
                res = {"material_id": r["material_id"], "decision": "rejected",
                       "reason": f"error:{type(exc).__name__}:{str(exc)[:120]}", "terminations": []}
            res["rank"] = int(r["rank"])
            results.append(res)
        pool.terminate()
        pool.join()
        for res in results:
            if not check and n_acc >= N_DRAW:
                break       # results beyond the 40th accepted material are not part of the draw and are discarded
            visited.append(res)
            if res["decision"] == "accepted":
                n_acc += 1
                res["draw_rank"] = n_acc
        print(f"visited {len(visited)} accepted {n_acc} elapsed {time.time() - t_start:.0f}s", flush=True)
    write_draw(out, visited, check is not None)


def write_draw(out: Path, visited: list[dict], is_check: bool) -> None:
    out.mkdir(parents=True, exist_ok=True)
    tcols = ["rank", "material_id", "miller", "termination", "shift", "symmetric", "polar", "stoichiometric", "natoms",
             "a", "b", "c", "gamma", "ng", "ngf", "npoints_est", "status", "error"]
    with open(out / "draw_slabs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=tcols, lineterminator="\n")
        w.writeheader()
        for res in visited:
            for t in res.get("terminations", []):
                w.writerow({"rank": res["rank"], "material_id": res["material_id"], **{k: t.get(k, "") for k in tcols[2:]}})
    mcols = ["rank", "material_id", "reduced_formula", "decision", "reason", "draw_rank", "miller", "termination",
             "natoms", "ngf", "npoints_est", "kpoints", "potcar_symbols", "conv_nsites", "oxidation_guess", "seconds"]
    with open(out / "draw_materials.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=mcols, lineterminator="\n")
        w.writeheader()
        for res in visited:
            acc = res.get("accepted", {})
            w.writerow({"rank": res["rank"], "material_id": res["material_id"],
                        "reduced_formula": res.get("reduced_formula", ""), "decision": res["decision"],
                        "reason": res.get("reason", ""), "draw_rank": res.get("draw_rank", ""),
                        "miller": acc.get("miller", ""), "termination": acc.get("termination", ""),
                        "natoms": acc.get("natoms", ""), "ngf": acc.get("ngf", ""),
                        "npoints_est": acc.get("npoints_est", ""),
                        "kpoints": "x".join(map(str, res["kpoints"])) if "kpoints" in res else "",
                        "potcar_symbols": " ".join(res.get("potcar_symbols", [])), "conv_nsites": res.get("conv_nsites", ""),
                        "oxidation_guess": json.dumps(res.get("oxidation_guess", {}), sort_keys=True),
                        "seconds": res.get("seconds", "")})
    drawn = [r for r in visited if r.get("draw_rank")]
    (out / "slabs").mkdir(exist_ok=True)
    for r in drawn:
        p = out / "slabs" / f"{r['material_id']}.json"
        p.write_text(json.dumps(r["slab"], indent=1, default=str) + "\n", encoding="utf-8")
    dcols = ["draw_rank", "rank", "material_id", "reduced_formula", "miller", "termination", "natoms", "a", "b", "c",
             "ngf", "npoints_est", "kpoints", "potcar_symbols", "slab_json_sha256"]
    with open(out / "drawn.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=dcols, lineterminator="\n")
        w.writeheader()
        for r in drawn:
            acc = r["accepted"]
            w.writerow({"draw_rank": r["draw_rank"], "rank": r["rank"], "material_id": r["material_id"],
                        "reduced_formula": r["reduced_formula"], "miller": acc["miller"],
                        "termination": acc["termination"], "natoms": acc["natoms"], "a": acc["a"], "b": acc["b"],
                        "c": acc["c"], "ngf": acc["ngf"], "npoints_est": acc["npoints_est"],
                        "kpoints": "x".join(map(str, r["kpoints"])), "potcar_symbols": " ".join(r["potcar_symbols"]),
                        "slab_json_sha256": sha256_text(out / "slabs" / f"{r['material_id']}.json")})
    reasons: dict[str, int] = {}
    for r in visited:
        k = r["decision"] if r["decision"] == "accepted" else r.get("reason", "")
        reasons[k] = reasons.get(k, 0) + 1
    log = {"phase": "check" if is_check else "draw", "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "n_visited": len(visited), "n_accepted": len(drawn), "decisions": reasons,
           "last_rank_visited": visited[-1]["rank"] if visited else None,
           "outputs_sha256": {n: sha256_text(out / n) for n in ("draw_slabs.csv", "draw_materials.csv", "drawn.csv")},
           "script_sha256": sha256_text(Path(__file__)), "grid_estimate_sha256": sha256_text(ROOT / "grid_estimate.py"),
           "environment": env()}
    (out / ("check_log.json" if is_check else "draw_log.json")).write_text(json.dumps(log, indent=2) + "\n",
                                                                             encoding="utf-8")
    print(json.dumps({k: v for k, v in log.items() if k != "environment"}, indent=2))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["funnel", "draw", "check"])
    ap.add_argument("--parquet", type=Path, default=Path(r"D:\Research\QoI-ext-cache\selfslab") / PARQUET_NAME)
    ap.add_argument("--out", type=Path, default=HERE)
    ap.add_argument("--ids", nargs="*")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(ROOT))
    if a.phase == "funnel":
        phase_funnel(a.parquet, a.out)
    elif a.phase == "draw":
        phase_draw(a.out)
    else:
        phase_draw(a.out, check=a.ids, check_source=a.parquet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
