#!/usr/bin/env python3
"""Audit recoverability of original electronic-structure provenance for frozen P3B panel.

This script does not run DFT and does not infer missing inputs. It queries public
NOMAD archives/raw text inputs and optionally authenticated Materials Project
task metadata, then records compact evidence candidates for later human review.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

USER_AGENT = "QoI-QSQ-P3B-provenance-audit/1.0"
NOMAD_BASE = "https://nomad-lab.eu/prod/v1/api/v1"
MP_NEW_BASE = "https://api.materialsproject.org"
MP_LEGACY_BASE = "https://www.materialsproject.org/rest/v2"
MAX_RAW_BYTES = 25_000_000

CATEGORIES = (
    "code_version", "xc", "pseudopotential", "spin", "kpoints", "encut",
    "smearing", "structure", "charge_convention", "grid_control",
)

PATH_PATTERNS = {
    "code_version": ("program.version", "program_version", "program.name", "program_name"),
    "xc": ("xc_functional", "exchange_correlation", "functional", "dft", "hubbard", "hybrid"),
    "pseudopotential": ("pseudopotential", "potcar", "atom_parameters", "core_electron", "valence_electron"),
    "spin": ("spin", "magnet", "nspin", "ispin"),
    "kpoints": ("k_mesh", "kpoint", "k_point", "sampling_method"),
    "encut": ("encut", "cutoff", "basis_set"),
    "smearing": ("smearing", "ismear", "sigma", "occupation"),
    "structure": ("lattice_vectors", "positions", "periodic", "atoms"),
    "grid_control": ("ngxf", "ngyf", "ngzf", "ngx", "ngy", "ngz", "fft", "grid", "precision", "prec"),
}

RAW_NAMES = ("INCAR", "KPOINTS", "POSCAR", "CONTCAR", "OUTCAR", "vasprun.xml")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_bytes(url: str, headers: dict[str, str] | None = None, timeout: int = 120, tries: int = 3) -> tuple[bytes | None, str]:
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    last = ""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:
                data = resp.read(MAX_RAW_BYTES + 1)
                if len(data) > MAX_RAW_BYTES:
                    return None, f"TOO_LARGE>{MAX_RAW_BYTES}"
                return data, f"HTTP_{getattr(resp, 'status', 200)}"
        except urllib.error.HTTPError as exc:
            last = f"HTTP_{exc.code}"
            if exc.code in (401, 403, 404):
                break
        except Exception as exc:  # network failures are recorded, not hidden
            last = f"{type(exc).__name__}:{exc}"
        if attempt + 1 < tries:
            time.sleep(2 ** attempt)
    return None, last or "UNKNOWN_ERROR"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def scalar_paths(obj: Any, path: str = "", out: list[tuple[str, Any]] | None = None, limit: int = 200_000) -> list[tuple[str, Any]]:
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            scalar_paths(v, f"{path}.{k}" if path else str(k), out, limit)
            if len(out) >= limit:
                break
    elif isinstance(obj, list):
        # Archive arrays can be large. Traverse structured lists fully up to limit,
        # but only the first 64 elements of very large scalar arrays.
        seq = obj if len(obj) <= 256 or any(isinstance(x, (dict, list)) for x in obj[:8]) else obj[:64]
        for i, v in enumerate(seq):
            scalar_paths(v, f"{path}[{i}]", out, limit)
            if len(out) >= limit:
                break
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        out.append((path, obj))
    return out


def compact_value(v: Any) -> str:
    s = str(v).replace("\n", " ").strip()
    return s[:240]


def path_candidates(paths: list[tuple[str, Any]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {k: [] for k in CATEGORIES}
    for p, v in paths:
        lp = p.lower()
        for cat, pats in PATH_PATTERNS.items():
            if any(token in lp for token in pats):
                item = {"source": "archive", "path": p, "value": compact_value(v)}
                if item not in out[cat] and len(out[cat]) < 30:
                    out[cat].append(item)
    return out


def merge_candidates(dst: dict[str, list[dict[str, str]]], src: dict[str, list[dict[str, str]]]) -> None:
    for cat in CATEGORIES:
        for item in src.get(cat, []):
            if item not in dst[cat] and len(dst[cat]) < 50:
                dst[cat].append(item)


def add_raw(dst: dict[str, list[dict[str, str]]], cat: str, filename: str, key: str, value: str) -> None:
    item = {"source": filename, "path": key, "value": compact_value(value)}
    if item not in dst[cat] and len(dst[cat]) < 50:
        dst[cat].append(item)


def parse_raw_text(filename: str, data: bytes, dst: dict[str, list[dict[str, str]]]) -> None:
    text = data.decode("utf-8", errors="replace")
    name = Path(filename).name
    upper = name.upper()
    if upper in {"POSCAR", "CONTCAR"}:
        add_raw(dst, "structure", name, "raw_structure_file", f"present sha256={sha256(data)}")
    if upper == "KPOINTS":
        add_raw(dst, "kpoints", name, "raw_kpoints_file", f"present sha256={sha256(data)}")
    if upper in {"INCAR", "OUTCAR"} or name == "vasprun.xml":
        patterns = {
            "encut": (r"\bENCUT\s*[=:]\s*([^\s;<]+)",),
            "smearing": (r"\bISMEAR\s*[=:]\s*([^\s;<]+)", r"\bSIGMA\s*[=:]\s*([^\s;<]+)"),
            "spin": (r"\bISPIN\s*[=:]\s*([^\s;<]+)", r"\bMAGMOM\s*[=:]\s*([^\n<]+)"),
            "xc": (r"\bMETAGGA\s*[=:]\s*([^\s;<]+)", r"\bGGA\s*[=:]\s*([^\s;<]+)", r"\bLHFCALC\s*[=:]\s*([^\s;<]+)", r"\bLDAU\s*[=:]\s*([^\s;<]+)"),
            "grid_control": (r"\bNGX[F]?\s*[=:]\s*([^\s;<]+)", r"\bNGY[F]?\s*[=:]\s*([^\s;<]+)", r"\bNGZ[F]?\s*[=:]\s*([^\s;<]+)", r"\bPREC\s*[=:]\s*([^\s;<]+)", r"\bADDGRID\s*[=:]\s*([^\s;<]+)"),
        }
        for cat, pats in patterns.items():
            for pat in pats:
                for m in re.finditer(pat, text, flags=re.IGNORECASE):
                    add_raw(dst, cat, name, pat, m.group(1)[:180])
                    if len(dst[cat]) >= 50:
                        break
        for m in re.finditer(r"\bvasp(?:\.|\s+)([0-9][0-9A-Za-z._-]*)", text, flags=re.IGNORECASE):
            add_raw(dst, "code_version", name, "vasp_version", m.group(1))
        for m in re.finditer(r"TITEL\s*=\s*([^\n\r]+)", text, flags=re.IGNORECASE):
            add_raw(dst, "pseudopotential", name, "POTCAR_TITEL", m.group(1))
    if name == "vasprun.xml":
        add_raw(dst, "structure", name, "vasprun_present", f"sha256={sha256(data)}")


def nomad_entry_id(url: str) -> str | None:
    m = re.search(r"/entries/([^/]+)/raw/", url)
    return m.group(1) if m else None


def mp_task_id(url: str) -> str | None:
    m = re.search(r"/chgcars/(mp-[0-9]+)\.json\.gz", url)
    return m.group(1) if m else None


def get_mainfile(archive: Any) -> str | None:
    for p, v in scalar_paths(archive, limit=20_000):
        if p.lower().endswith("metadata.mainfile") or p.lower().endswith("mainfile"):
            if isinstance(v, str) and v.strip():
                return v.strip()
    return None


def raw_sibling_paths(mainfile: str | None) -> list[str]:
    dirs = [""]
    if mainfile:
        parent = str(Path(mainfile).parent)
        if parent not in ("", "."):
            dirs.insert(0, parent)
    paths = []
    for d in dirs:
        for name in RAW_NAMES:
            p = f"{d}/{name}" if d else name
            if p not in paths:
                paths.append(p)
    if mainfile and mainfile not in paths:
        paths.insert(0, mainfile)
    return paths


def audit_nomad(meta: dict[str, str]) -> tuple[dict[str, list[dict[str, str]]], dict[str, Any]]:
    candidates = {k: [] for k in CATEGORIES}
    entry = nomad_entry_id(meta["url"])
    status: dict[str, Any] = {"entry_id": entry, "archive_status": "NOT_ATTEMPTED", "raw_files": []}
    if not entry:
        status["archive_status"] = "ENTRY_ID_PARSE_FAILED"
        return candidates, status
    data, st = request_bytes(f"{NOMAD_BASE}/entries/{entry}/archive")
    status["archive_status"] = st
    archive = None
    if data:
        try:
            archive = json.loads(data.decode("utf-8"))
            status["archive_sha256"] = sha256(data)
            merge_candidates(candidates, path_candidates(scalar_paths(archive)))
        except Exception as exc:
            status["archive_parse_error"] = f"{type(exc).__name__}: {exc}"
    mainfile = get_mainfile(archive) if archive is not None else None
    status["mainfile"] = mainfile
    for rel in raw_sibling_paths(mainfile):
        if Path(rel).name.upper() in {"CHGCAR", "WAVECAR", "POTCAR"}:
            continue
        quoted = "/".join(urllib.parse.quote(part) for part in rel.split("/"))
        raw, raw_status = request_bytes(f"{NOMAD_BASE}/entries/{entry}/raw/{quoted}", tries=2)
        rec: dict[str, Any] = {"path": rel, "status": raw_status}
        if raw:
            rec.update({"bytes": len(raw), "sha256": sha256(raw)})
            parse_raw_text(rel, raw, candidates)
        status["raw_files"].append(rec)
    # The analysed object is explicitly the archived CHGCAR total grid.
    add_raw(candidates, "charge_convention", "materials_metadata.csv", "analysed_source", "CHGCAR total density grid analysed via BaderKit Grid.total")
    return candidates, status


def audit_mp(meta: dict[str, str]) -> tuple[dict[str, list[dict[str, str]]], dict[str, Any]]:
    candidates = {k: [] for k in CATEGORIES}
    task = mp_task_id(meta["url"])
    key = os.environ.get("MP_API_KEY", "").strip()
    status: dict[str, Any] = {"task_id": task, "api_key_present": bool(key), "task_status": "NOT_ATTEMPTED"}
    add_raw(candidates, "structure", "parsed_CHGCAR", "structure", "final structure embedded in frozen pymatgen Chgcar")
    add_raw(candidates, "charge_convention", "materials_metadata.csv", "analysed_source", "CHGCAR total density grid analysed via BaderKit Grid.total")
    if not task:
        status["task_status"] = "TASK_ID_PARSE_FAILED"
        return candidates, status
    if not key:
        status["task_status"] = "MP_API_KEY_UNAVAILABLE"
        return candidates, status
    headers = {"X-API-KEY": key}
    urls = [
        f"{MP_NEW_BASE}/materials/tasks/?task_ids={urllib.parse.quote(task)}",
        f"{MP_LEGACY_BASE}/tasks/{urllib.parse.quote(task)}",
    ]
    for url in urls:
        data, st = request_bytes(url, headers=headers)
        status.setdefault("attempts", []).append({"endpoint_family": "new" if url.startswith(MP_NEW_BASE) else "legacy", "status": st})
        if not data:
            continue
        try:
            obj = json.loads(data.decode("utf-8"))
            merge_candidates(candidates, path_candidates(scalar_paths(obj)))
            status["task_status"] = "RETRIEVED"
            status["task_payload_sha256"] = sha256(data)
            break
        except Exception as exc:
            status["task_status"] = f"PARSE_ERROR:{type(exc).__name__}"
    return candidates, status


def category_presence(candidates: dict[str, list[dict[str, str]]]) -> dict[str, bool]:
    return {cat: bool(candidates.get(cat)) for cat in CATEGORIES}


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    root = a.repo_root.resolve(); out = a.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    panel_path = root / "validation/qsq_prospective/convergence_panel.csv"
    meta_path = root / "materials_metadata.csv"
    panel = read_csv(panel_path); meta = {r["material_id"]: r for r in read_csv(meta_path)}
    if len(panel) != 24 or len({r["material_id"] for r in panel}) != 24:
        raise RuntimeError("frozen P3B panel must contain 24 unique systems")

    inventory = []; evidence: dict[str, Any] = {}
    for i, p_row in enumerate(panel, 1):
        m = p_row["material_id"]
        mmeta = meta.get(m)
        if not mmeta:
            candidates = {k: [] for k in CATEGORIES}; source_status = {"status": "METADATA_MISSING"}
            source = "UNKNOWN"
        else:
            source = mmeta["source"]
            if source.startswith("NOMAD"):
                candidates, source_status = audit_nomad(mmeta)
            elif source == "Materials Project":
                candidates, source_status = audit_mp(mmeta)
            else:
                candidates = {k: [] for k in CATEGORIES}; source_status = {"status": "UNSUPPORTED_SOURCE"}
        present = category_presence(candidates)
        n_present = sum(present.values())
        auto = n_present == len(CATEGORIES)
        inventory.append({
            "material_id": m,
            "system_type": p_row["system_type"],
            "floor_band": p_row["floor_band"],
            "source": source,
            "required_categories_present": n_present,
            "required_categories_total": len(CATEGORIES),
            "auto_status": "AUTO_CANDIDATE_COMPLETE" if auto else "INCOMPLETE_PROVENANCE",
            **{f"has_{cat}": present[cat] for cat in CATEGORIES},
        })
        evidence[m] = {"source_status": source_status, "category_candidates": candidates}
        print(f"[{i:02d}/24] {m}: {n_present}/{len(CATEGORIES)} candidate categories", flush=True)

    fields = list(inventory[0].keys())
    with (out / "p3b_provenance_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(inventory)
    (out / "p3b_provenance_candidates.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    nomad = [r for r in inventory if r["source"].startswith("NOMAD")]
    mp = [r for r in inventory if r["source"] == "Materials Project"]
    complete = [r for r in inventory if r["auto_status"] == "AUTO_CANDIDATE_COMPLETE"]
    lines = [
        "# P3B provenance-recovery audit", "",
        f"Panel accounting: **{len(inventory)}/24 systems**. Automated candidate-complete: **{len(complete)}/24**. Human scientific review is still required before any DFT recomputation work order is frozen.", "",
        f"NOMAD systems: **{len(nomad)}**; Materials Project systems: **{len(mp)}**.", "",
        "| Material | Type | Source | Candidate categories | Auto status |",
        "|---|---|---|---:|---|",
    ]
    for r in inventory:
        lines.append(f"| {r['material_id']} | {r['system_type']} | {r['source']} | {r['required_categories_present']}/{r['required_categories_total']} | {r['auto_status']} |")
    lines += ["", "## Interpretation boundary", "", "`AUTO_CANDIDATE_COMPLETE` means only that the automated audit found evidence candidates for every required provenance category. It is not permission to run P3B until those candidates are reviewed for exactness and internal consistency. Missing provenance is reported honestly; no generic VASP defaults are substituted."]
    (out / "P3B_PROVENANCE_AUDIT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {
        "status": "AUDIT_COMPLETE",
        "panel_systems": len(inventory),
        "auto_candidate_complete": len(complete),
        "panel_sha256": sha256(panel_path.read_bytes()),
        "metadata_sha256": sha256(meta_path.read_bytes()),
        "mp_api_key_present": bool(os.environ.get("MP_API_KEY", "").strip()),
        "scientific_outputs_generated": False,
        "grid_recomputation_started": False,
    }
    (out / "execution_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
