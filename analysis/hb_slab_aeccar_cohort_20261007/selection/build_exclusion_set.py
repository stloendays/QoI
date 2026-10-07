#!/usr/bin/env python3
"""Rebuild the project-wide exclusion set for the HB slab AECCAR cohort (metadata only).

Union of
  (a) the frozen QOAC-FRESH-20261006 exclusion set: every id in `exclusion_ids_full.csv.gz` and every reduced formula
      in `exclusion_formulas.csv` (analysis/fresh_population_20261006/, built over 60 origin branches on 2026-10-06);
  (b) a new scan of every text-like data file on every `origin/*` branch now, with the identifier regexes, formula
      columns and pymatgen reduction of `analysis/fresh_population_20261006/scripts/build_exclusion.py` (imported, not
      copied). This picks up every manifest committed since (P1, P2, P3b, the WP-F sample, the external cohorts, the
      QOAC-HB slab run and every other branch).

Files that are listings of a candidate universe rather than usage records are skipped in (b), as the original rule
did for the WP-F bucket frame (whose `in_frozen_study = 1` rows are still read):
  nomad_frame_surface_vasp.csv.gz, s3_index_{chgcars,aeccar0s,aeccar2s}.csv.gz (the 2026-10-06 NOMAD / S3 listings),
  the exclusion tables themselves (exclusion_ids.csv, exclusion_ids_full.csv.gz, exclusion_formulas.csv,
  exclusion_summary.json) and the listing logs nomad_frame_log.json, s3_index_log.json, frame_counts.json.
Draw records (attempts.csv, p3b_attempts.csv) are usage records and are scanned.

Outputs (in --out-dir): exclusion_ids.csv, exclusion_formulas.csv, exclusion_set.json (branches with commit SHAs,
counts, SHA-256 of the two tables).

Usage: build_exclusion_set.py --repo <git checkout with origin/* fetched> --out-dir <dir>
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[2]
FRESH = Path("analysis/fresh_population_20261006")
LISTING_FILES = {
    "nomad_frame_surface_vasp.csv.gz", "s3_index_chgcars.csv.gz", "s3_index_aeccar0s.csv.gz",
    "s3_index_aeccar2s.csv.gz", "exclusion_ids.csv", "exclusion_ids_full.csv.gz", "exclusion_formulas.csv",
    "exclusion_summary.json", "nomad_frame_log.json", "s3_index_log.json", "frame_counts.json",
}


def load_be(repo: Path):
    spec = importlib.util.spec_from_file_location("build_exclusion", repo / FRESH / "scripts" / "build_exclusion.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(p: Path) -> str:
    """SHA-256 of the committed bytes: text files with LF line ends (a Windows checkout may hold CRLF)."""
    data = p.read_bytes()
    if not p.name.endswith(".gz"):
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    repo = a.repo.resolve()
    be = load_be(repo)

    # (a) frozen 2026-10-06 set
    ids: dict[str, dict] = {}
    formulas: dict[str, dict] = {}
    with gzip.open(repo / FRESH / "exclusion_ids_full.csv.gz", "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rec = ids.setdefault(r["id"], {"kinds": set(), "sources": set(), "branches": set(), "frozen_20261006": 1})
            rec["kinds"].add(r["kind"]); rec["sources"].add(r["source_file"]); rec["branches"].add(r["branch"])
    with open(repo / FRESH / "exclusion_formulas.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rec = formulas.setdefault(r["reduced_formula"], {"strings": set(), "sources": set(), "branches": set(), "frozen_20261006": 1})
            rec["strings"].add(r["formula"]); rec["sources"].add(r["example_source_file"]); rec["branches"].add(r["branch"])
    n_ids_frozen, n_f_frozen = len(ids), len(formulas)

    # (b) scan every origin/* branch now
    refs = [r for r in be.git(repo, "for-each-ref", "refs/remotes/origin", "--format=%(refname:short)").split()
            if r not in ("origin", "origin/HEAD")]
    ref_sha = {r: be.git(repo, "rev-parse", r).strip() for r in refs}
    blobs: dict[str, list[tuple[str, str]]] = defaultdict(list)
    skipped: set[str] = set()
    for ref in refs:
        for line in be.git(repo, "ls-tree", "-r", ref).splitlines():
            meta, path = line.split("\t", 1)
            _, typ, sha = meta.split()
            p = path.lower()
            if typ != "blob" or not (p.endswith(be.EXTS) or (p.endswith(".gz") and p[:-3].endswith(be.EXTS))):
                continue
            if path.rsplit("/", 1)[-1] in LISTING_FILES:
                skipped.add(path)
                continue
            blobs[sha].append((ref, path))

    proc = subprocess.Popen(["git", "-C", str(repo), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha in sorted(blobs):
        proc.stdin.write((sha + "\n").encode()); proc.stdin.flush()
        header = proc.stdout.readline().split()
        data = proc.stdout.read(int(header[2])); proc.stdout.read(1)
        locs = blobs[sha]
        path0 = locs[0][1]
        if path0.lower().endswith(".gz"):
            try:
                data = gzip.decompress(data)
            except OSError:
                continue
        text = data.decode("utf-8", "replace")
        if path0.rsplit("/", 1)[-1] in be.FRAME_FILES:
            rows = csv.DictReader(io.StringIO(text))
            text = "\n".join(r["key"] for r in rows if r.get("in_frozen_study") == "1")
        found: set[tuple[str, str]] = set()
        for m in be.S3_RE.finditer(text):
            found.add((m.group(2), "mp_task_id_s3_url"))
        task_ids = {i for i, _ in found}
        for m in be.MP_RE.finditer(text):
            if m.group(0) not in task_ids:
                found.add((m.group(0), "mp_id"))
        for m in be.NOMAD_ENTRY_RE.finditer(text):
            found.add((m.group(1), "nomad_entry_id"))
        for m in be.NOMAD_SHORT_RE.finditer(text):
            found.add(("nomad-" + m.group(1), "nomad_material_id"))
        for ident, kind in found:
            rec = ids.setdefault(ident, {"kinds": set(), "sources": set(), "branches": set(), "frozen_20261006": 0})
            rec["kinds"].add(kind)
            for ref, path in locs:
                rec["sources"].add(path); rec["branches"].add(ref)
        if path0.lower().removesuffix(".gz").endswith(be.STRUCTURED):
            for _, val in be.formula_values(path0, text):
                red = be.reduce_formula(val)
                if red is None:
                    continue
                rec = formulas.setdefault(red, {"strings": set(), "sources": set(), "branches": set(), "frozen_20261006": 0})
                rec["strings"].add(val)
                for ref, path in locs:
                    rec["sources"].add(path); rec["branches"].add(ref)
    proc.stdin.close(); proc.wait()

    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "exclusion_ids.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "kinds", "in_frozen_20261006_set", "n_source_files", "example_source_file", "n_branches"])
        for ident in sorted(ids):
            r = ids[ident]
            w.writerow([ident, ";".join(sorted(r["kinds"])), r["frozen_20261006"], len(r["sources"]),
                        sorted(r["sources"])[0], len(r["branches"])])
    with open(out / "exclusion_formulas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["reduced_formula", "in_frozen_20261006_set", "n_source_files", "example_source_file", "n_branches"])
        for red in sorted(formulas):
            r = formulas[red]
            w.writerow([red, r["frozen_20261006"], len(r["sources"]), sorted(r["sources"])[0], len(r["branches"])])
    by_kind: dict[str, int] = defaultdict(int)
    for r in ids.values():
        for k in r["kinds"]:
            by_kind[k] += 1
    summary = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "frozen_20261006_inputs": {"exclusion_ids_full.csv.gz": sha256_file(repo / FRESH / "exclusion_ids_full.csv.gz"),
                                   "exclusion_formulas.csv": sha256_file(repo / FRESH / "exclusion_formulas.csv"),
                                   "n_ids": n_ids_frozen, "n_reduced_formulas": n_f_frozen},
        "n_branches_scanned": len(refs),
        "branches": {r: ref_sha[r] for r in refs},
        "n_unique_blobs_scanned": len(blobs),
        "skipped_listing_paths": sorted(skipped),
        "n_ids_total": len(ids),
        "n_ids_new_since_20261006": sum(1 for r in ids.values() if not r["frozen_20261006"]),
        "n_ids_by_kind": dict(sorted(by_kind.items())),
        "n_reduced_formulas_total": len(formulas),
        "n_reduced_formulas_new_since_20261006": sum(1 for r in formulas.values() if not r["frozen_20261006"]),
        "sha256": {"exclusion_ids.csv": sha256_file(out / "exclusion_ids.csv"),
                   "exclusion_formulas.csv": sha256_file(out / "exclusion_formulas.csv")},
    }
    (out / "exclusion_set.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("branches", "skipped_listing_paths")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
