#!/usr/bin/env python3
"""Freeze an outcome-blind candidate universe for P4 chemical-decision validation.

This script intentionally reads only materials_metadata.csv plus raw NOMAD
structure files. It MUST NOT read QSQ eligibility, codec outcomes, P2/P3A
outcomes, or Bader charges. Candidate pairing is based only on chemical identity,
shared provenance, composition, cell geometry and atom correspondence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from pymatgen.io.vasp.inputs import Poscar
from scipy.optimize import linear_sum_assignment

BASE = "https://nomad-lab.eu/prod/v1/api/v1"
UA = "QoI-QSQ-P4-outcome-blind-candidate-audit/1.0"
ADSORBATE_ELEMENTS = {"H", "C", "O"}
MAX_ADDED_ATOMS = 4
MAX_MAPPING_DISTANCE_A = 0.35
MAX_TARGET_DISTANCE_A = 3.0
LATTICE_ATOL_A = 1e-4
LATTICE_RTOL = 1e-5


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fallback_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else fallback_fields
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def entry_id(url: str) -> str:
    m = re.search(r"/entries/([^/]+)/raw/", url)
    if not m:
        raise RuntimeError(f"cannot parse NOMAD entry id from {url}")
    return m.group(1)


def get(url: str, tries: int = 3) -> tuple[bytes | None, str]:
    last = ""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90, context=ssl.create_default_context()) as r:
                return r.read(), f"HTTP_{getattr(r, 'status', 200)}"
        except urllib.error.HTTPError as exc:
            last = f"HTTP_{exc.code}"
            if exc.code in (401, 403, 404):
                break
        except Exception as exc:
            last = f"{type(exc).__name__}:{exc}"
        if i + 1 < tries:
            time.sleep(2 ** i)
    return None, last or "UNKNOWN_ERROR"


def archive_mainfile(eid: str) -> str | None:
    data, _ = get(f"{BASE}/entries/{eid}/archive", tries=2)
    if not data:
        return None
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception:
        return None
    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "mainfile" and isinstance(v, str) and v.strip():
                    return v.strip()
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(x, list):
            stack.extend(v for v in x if isinstance(v, (dict, list)))
    return None


def structure_candidates(eid: str) -> list[str]:
    paths = ["CONTCAR", "POSCAR"]
    mainfile = archive_mainfile(eid)
    if mainfile:
        parent = str(Path(mainfile).parent)
        if parent not in ("", "."):
            paths = [f"{parent}/CONTCAR", f"{parent}/POSCAR"] + paths
    out: list[str] = []
    for p in paths:
        if p not in out:
            out.append(p)
    return out


def fetch_structure(eid: str):
    attempts = []
    for rel in structure_candidates(eid):
        quoted = "/".join(urllib.parse.quote(x) for x in rel.split("/"))
        data, status = get(f"{BASE}/entries/{eid}/raw/{quoted}", tries=2)
        attempts.append({"path": rel, "status": status})
        if not data:
            continue
        try:
            text = data.decode("utf-8", errors="strict")
            structure = Poscar.from_str(text).structure
            return structure, rel, sha256(data), attempts
        except Exception as exc:
            attempts[-1]["parse_error"] = f"{type(exc).__name__}:{exc}"
    return None, "", "", attempts


def composition(structure) -> Counter[str]:
    return Counter(str(site.specie.symbol) for site in structure)


def comp_delta(a: Counter[str], b: Counter[str]) -> Counter[str] | None:
    all_el = set(a) | set(b)
    if any(b[e] < a[e] for e in all_el):
        return None
    return Counter({e: b[e] - a[e] for e in all_el if b[e] > a[e]})


def map_atoms(sa, sb) -> tuple[dict[int, int], list[int], float, float] | None:
    """Map every state-A atom to a same-element atom in state B by PBC distance."""
    ca, cb = composition(sa), composition(sb)
    mapping: dict[int, int] = {}
    dists: list[float] = []
    for element, count_a in ca.items():
        ia = [i for i, s in enumerate(sa) if str(s.specie.symbol) == element]
        ib = [i for i, s in enumerate(sb) if str(s.specie.symbol) == element]
        if len(ib) < count_a:
            return None
        fa = np.asarray([sa[i].frac_coords for i in ia], dtype=float)
        fb = np.asarray([sb[i].frac_coords for i in ib], dtype=float)
        cost = np.asarray(sb.lattice.get_all_distances(fa, fb), dtype=float)
        rr, cc = linear_sum_assignment(cost)
        for r, c in zip(rr.tolist(), cc.tolist()):
            mapping[ia[r]] = ib[c]
            dists.append(float(cost[r, c]))
    if len(mapping) != len(sa):
        return None
    unmatched = sorted(set(range(len(sb))) - set(mapping.values()))
    return mapping, unmatched, (max(dists) if dists else 0.0), (float(np.sqrt(np.mean(np.square(dists)))) if dists else 0.0)


def nearest_target(sa, sb, mapping: dict[int, int], unmatched_b: list[int], ca: Counter[str], cb: Counter[str]):
    host_elements = {e for e in ca if ca[e] == cb[e] and ca[e] > 0}
    candidates = [(ia, ib) for ia, ib in mapping.items() if str(sa[ia].specie.symbol) in host_elements]
    if not candidates or not unmatched_b:
        return None
    best = None
    for ia, ib in candidates:
        for j in unmatched_b:
            d = float(sb.get_distance(ib, j))
            key = (d, str(sa[ia].specie.symbol), ia, ib, j)
            if best is None or key < best[0]:
                best = (key, ia, ib, j)
    assert best is not None
    key, ia, ib, added_j = best
    return {
        "target_species": str(sa[ia].specie.symbol),
        "target_index_A_zero_based": ia,
        "target_index_B_zero_based": ib,
        "nearest_added_index_B_zero_based": added_j,
        "target_to_added_distance_A": key[0],
    }


def pair_id(upload_id: str, a: str, b: str) -> str:
    h = hashlib.sha256(f"P4|{upload_id}|{a}|{b}".encode()).hexdigest()[:16]
    return f"P4-{h}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    z = ap.parse_args()
    root = z.repo_root.resolve(); out = z.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)

    meta_path = root / "materials_metadata.csv"
    metadata = [r for r in read_csv(meta_path) if r.get("corpus") == "dev_slab" and r.get("source", "").startswith("NOMAD")]
    if not metadata:
        raise RuntimeError("no NOMAD dev_slab rows found")

    # Hard guard: this audit must not read outcome-bearing files.
    forbidden = ["stability", "benchmark", "p2_", "p3a_", "master_benchmark"]
    source_text = Path(__file__).read_text(encoding="utf-8").lower()
    if any(f"root / \"{x}" in source_text for x in forbidden):
        raise RuntimeError("outcome-bearing path referenced by P4 candidate audit")

    structures: dict[str, Any] = {}
    retrieval = []
    meta_by_id = {r["material_id"]: r for r in metadata}
    for i, r in enumerate(metadata, 1):
        m = r["material_id"]; eid = entry_id(r["url"])
        s, rel, file_sha, attempts = fetch_structure(eid)
        retrieval.append({
            "material_id": m, "upload_id": r.get("upload_id", ""), "entry_id": eid,
            "formula_metadata": r.get("formula", ""), "structure_status": "PASS" if s is not None else "FAIL",
            "structure_raw_path": rel, "structure_raw_sha256": file_sha,
            "natoms_metadata": r.get("natoms", ""), "natoms_structure": len(s) if s is not None else "",
            "attempts_json": json.dumps(attempts, separators=(",", ":")),
        })
        if s is not None:
            structures[m] = s
        print(f"[{i:03d}/{len(metadata):03d}] {m} structure={'PASS' if s is not None else 'FAIL'}", flush=True)

    groups: dict[str, list[str]] = defaultdict(list)
    for r in metadata:
        if r.get("upload_id"):
            groups[r["upload_id"]].append(r["material_id"])

    candidates = []; exclusions = []
    def reject(upload: str, a: str, b: str, reason: str, detail: str = ""):
        exclusions.append({"upload_id": upload, "material_1": a, "material_2": b, "reason": reason, "detail": detail})

    for upload, mids in sorted(groups.items()):
        for x, y in combinations(sorted(mids), 2):
            if x not in structures or y not in structures:
                reject(upload, x, y, "STRUCTURE_UNAVAILABLE")
                continue
            sx, sy = structures[x], structures[y]
            # Primary P4 uses addition-type paired states only; equal-size site isomers are reserved for secondary work.
            if len(sx) == len(sy):
                reject(upload, x, y, "EQUAL_ATOM_COUNT_SECONDARY_ONLY")
                continue
            a, b, sa, sb = (x, y, sx, sy) if len(sx) < len(sy) else (y, x, sy, sx)
            ma, mb = meta_by_id[a], meta_by_id[b]
            if ma.get("ngrid") != mb.get("ngrid"):
                reject(upload, a, b, "GRID_SHAPE_DIFFERS", f"{ma.get('ngrid')} vs {mb.get('ngrid')}")
                continue
            if not np.allclose(np.asarray(sa.lattice.matrix), np.asarray(sb.lattice.matrix), rtol=LATTICE_RTOL, atol=LATTICE_ATOL_A):
                reject(upload, a, b, "LATTICE_DIFFERS")
                continue
            ca, cb = composition(sa), composition(sb)
            delta = comp_delta(ca, cb)
            if delta is None:
                reject(upload, a, b, "NOT_PURE_ADDITION")
                continue
            added_n = sum(delta.values())
            if added_n < 1 or added_n > MAX_ADDED_ATOMS:
                reject(upload, a, b, "ADDED_ATOM_COUNT_OUT_OF_RANGE", str(added_n))
                continue
            if not set(delta).issubset(ADSORBATE_ELEMENTS):
                reject(upload, a, b, "ADDED_SPECIES_OUTSIDE_FROZEN_SET", ";".join(sorted(delta)))
                continue
            mapped = map_atoms(sa, sb)
            if mapped is None:
                reject(upload, a, b, "ATOM_MAPPING_FAILED")
                continue
            mapping, unmatched, max_d, rms_d = mapped
            if len(unmatched) != added_n:
                reject(upload, a, b, "UNMATCHED_COUNT_INCONSISTENT", f"{len(unmatched)} vs {added_n}")
                continue
            unmatched_comp = Counter(str(sb[i].specie.symbol) for i in unmatched)
            if unmatched_comp != delta:
                reject(upload, a, b, "UNMATCHED_COMPOSITION_INCONSISTENT", f"{dict(unmatched_comp)} vs {dict(delta)}")
                continue
            if max_d > MAX_MAPPING_DISTANCE_A:
                reject(upload, a, b, "HOST_MAPPING_TOO_LARGE", f"max={max_d:.6g}")
                continue
            target = nearest_target(sa, sb, mapping, unmatched, ca, cb)
            if target is None:
                reject(upload, a, b, "NO_PERSISTENT_HOST_TARGET")
                continue
            if float(target["target_to_added_distance_A"]) > MAX_TARGET_DISTANCE_A:
                reject(upload, a, b, "NO_LOCAL_HOST_TARGET_WITHIN_CUTOFF", f"d={target['target_to_added_distance_A']:.6g}")
                continue
            candidates.append({
                "pair_id": pair_id(upload, a, b), "upload_id": upload,
                "upload_description": ma.get("upload_description", "") or mb.get("upload_description", ""),
                "state_A_material_id": a, "state_B_material_id": b,
                "state_A_formula": ma.get("formula", ""), "state_B_formula": mb.get("formula", ""),
                "ngrid": ma.get("ngrid", ""), "natoms_A": len(sa), "natoms_B": len(sb),
                "added_composition": ";".join(f"{e}:{delta[e]}" for e in sorted(delta)),
                "added_indices_B_zero_based": ";".join(str(i) for i in unmatched),
                "host_mapping_max_distance_A": max_d, "host_mapping_rms_distance_A": rms_d,
                **target,
                "selection_basis": "chemistry_provenance_geometry_only",
                "status": "CANDIDATE_FROZEN_NO_OUTCOMES_READ",
            })

    candidates.sort(key=lambda r: (r["upload_id"], r["pair_id"]))
    exclusions.sort(key=lambda r: (r["upload_id"], r["material_1"], r["material_2"], r["reason"]))
    retrieval.sort(key=lambda r: r["material_id"])
    write_csv(out / "p4_candidate_pairs.csv", candidates, ["pair_id", "status"])
    write_csv(out / "p4_pair_exclusions.csv", exclusions, ["upload_id", "material_1", "material_2", "reason", "detail"])
    write_csv(out / "p4_structure_retrieval.csv", retrieval, ["material_id", "structure_status"])

    by_upload = Counter(r["upload_id"] for r in candidates)
    failed_structures = sum(r["structure_status"] != "PASS" for r in retrieval)
    lines = [
        "# P4 outcome-blind chemistry candidate audit", "",
        "Status: **CANDIDATE_UNIVERSE_FROZEN**", "",
        "This audit was constructed from `materials_metadata.csv` and raw NOMAD structure files only. It does not read QSQ eligibility, codec outcomes, P2 fresh-probe outcomes, P3A outcomes, or Bader charges.", "",
        f"NOMAD development slab states audited: **{len(metadata)}**; structure retrieval failures: **{failed_structures}**.",
        f"Chemistry/provenance/geometry-qualified directed addition pairs: **{len(candidates)}**; excluded pair comparisons: **{len(exclusions)}**.", "",
        "Frozen primary pairing rule: same NOMAD upload, same density-grid shape, same lattice within tolerance, 1-4 added H/C/O atoms, all state-A atoms mappable to state B within 0.35 A, and a persistent host atom within 3.0 A of an added atom. The target is the nearest persistent host atom chosen from geometry only.", "",
        "| Upload | Description | Candidate pairs |", "|---|---|---:|",
    ]
    desc = {}
    for r in metadata:
        if r.get("upload_id"):
            desc[r["upload_id"]] = r.get("upload_description", "")
    for upload in sorted(by_upload):
        lines.append(f"| {upload} | {desc.get(upload,'')} | {by_upload[upload]} |")
    lines += ["", "## Interpretation boundary", "", "These are candidate chemistry pairs, not yet P4 outcomes. Reference charge-transfer decisions, ambiguity margins, codec trials and qualification policies must be frozen/evaluated in subsequent stages. No pair may be added or removed later because of QSQ or codec performance; exclusions after this point must be provenance/reference failures and must remain visible in accounting."]
    (out / "P4_CANDIDATE_AUDIT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {
        "status": "CANDIDATE_UNIVERSE_FROZEN",
        "metadata_sha256": sha256(meta_path.read_bytes()),
        "audit_script_sha256": sha256(Path(__file__).read_bytes()),
        "nomad_dev_slab_states": len(metadata),
        "structure_retrieval_failures": failed_structures,
        "candidate_pairs": len(candidates),
        "excluded_pair_comparisons": len(exclusions),
        "outcome_bearing_files_read": False,
        "adsorbate_elements": sorted(ADSORBATE_ELEMENTS),
        "max_added_atoms": MAX_ADDED_ATOMS,
        "max_mapping_distance_A": MAX_MAPPING_DISTANCE_A,
        "max_target_distance_A": MAX_TARGET_DISTANCE_A,
    }
    (out / "execution_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
