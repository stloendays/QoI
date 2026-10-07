#!/usr/bin/env python3
"""Exclusion sets of the wide NOMAD slab cohort, built from files committed on every origin/* branch (metadata only).

1. NOMAD entry ids (`exclusion_nomad_ids.csv`): every NOMAD entry id and every `nomad-<prefix>` material id that
   appears in any committed text data file (csv, tsv, json, jsonl, md, txt, yaml, py and their .gz) on any branch:
   - `entries/<28 characters>` in any text (the regex of `fresh_population_20261006/scripts/build_exclusion.py`);
   - `nomad-<10..28 characters>` in any text (same source);
   - a bare 28-character value in a CSV column named `entry_id`, `task_id` or `nomad_entry_id` (draw records and
     manifests that store the bare id).
   Draw records (attempts tables) are included. Candidate-universe listings are skipped (LISTINGS below).
2. Reduced formulas of NOMAD or slab sets (`exclusion_slab_formulas.csv`): the pymatgen reduced formula of every
   `*formula*` value in a CSV/TSV row, or JSON object, that is a NOMAD or slab record: it carries a NOMAD marker (a
   `nomad-` id, a `nomad-lab.eu` URL, a `source`/`corpus` value containing `NOMAD`, or a bare 28-character
   `entry_id`/`task_id`) or has `system_type` `slab`. Formulas that occur only in Materials Project or AFLOW bulk
   rows are not collected. Draw records (attempts tables, which list rejected candidates) and listings are skipped.

Each output row carries its source files (`source_files`, `;`-joined, all of them) and the number of branches.
`exclusion_sets.json` records the branches with their commit SHAs, the counts, the SHA-256 of both tables, and the
counts of the strict rule of the previous cohorts (all ids and all formulas of any set) for comparison.

Usage: build_exclusion_sets.py --repo <checkout with origin/* fetched> [--out-dir <dir>]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[2]
FRESH = Path("analysis/fresh_population_20261006")
LISTINGS = {
    # candidate-universe listings and their logs
    "nomad_frame_surface_vasp.csv.gz", "nomad_frame_log.json", "frame_counts.json", "frame.csv.gz",
    "s3_index_chgcars.csv.gz", "s3_index_aeccar0s.csv.gz", "s3_index_aeccar2s.csv.gz", "s3_index_log.json",
    "relisted_entries.csv", "relist_log.json", "frame_headers.csv",
    # exclusion tables (derived from the files scanned here)
    "exclusion_ids.csv", "exclusion_ids_full.csv.gz", "exclusion_formulas.csv", "exclusion_summary.json",
    "exclusion_set.json", "exclusion_nomad_ids.csv", "exclusion_slab_formulas.csv", "exclusion_sets.json",
}
DRAW_RECORDS = {"attempts.csv", "p3b_attempts.csv", "check_entries.csv"}
ID_COLS = {"entry_id", "task_id", "nomad_entry_id"}
BARE_ID = re.compile(r"[A-Za-z0-9_\-]{28}")
NOMAD_SHORT = re.compile(r"(?<![A-Za-z0-9_])nomad-[A-Za-z0-9_\-]{10,28}")


def load_be(repo: Path):
    spec = importlib.util.spec_from_file_location("build_exclusion", repo / FRESH / "scripts" / "build_exclusion.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_lf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def is_nomad_or_slab(rec: dict) -> bool:
    for k, v in rec.items():
        if not isinstance(v, str):
            continue
        kl = str(k).lower()
        if NOMAD_SHORT.search(v) or "nomad-lab.eu" in v:
            return True
        if kl in ("source", "corpus", "database", "provider") and "nomad" in v.lower():
            return True
        if kl in ID_COLS and BARE_ID.fullmatch(v.strip()):
            return True
        if kl == "system_type" and v.strip().lower() == "slab":
            return True
    return False


def json_records(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from json_records(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from json_records(v)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    ap.add_argument("--out-dir", type=Path, default=HERE)
    a = ap.parse_args(argv)
    repo = a.repo.resolve()
    be = load_be(repo)
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
            if path.rsplit("/", 1)[-1] in LISTINGS:
                skipped.add(path)
                continue
            blobs[sha].append((ref, path))

    ids: dict[str, dict] = {}
    forms: dict[str, dict] = {}

    def add_id(ident, kind, locs):
        r = ids.setdefault(ident, {"kinds": set(), "sources": set(), "branches": set()})
        r["kinds"].add(kind)
        for ref, path in locs:
            r["sources"].add(path); r["branches"].add(ref)

    def add_formula(val, locs):
        red = be.reduce_formula(val)
        if red is None:
            return
        r = forms.setdefault(red, {"strings": set(), "sources": set(), "branches": set()})
        r["strings"].add(val)
        for ref, path in locs:
            r["sources"].add(path); r["branches"].add(ref)

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
        base = path0.lower().removesuffix(".gz")
        name = path0.rsplit("/", 1)[-1]
        # 1. ids, from any text
        for m in be.NOMAD_ENTRY_RE.finditer(text):
            add_id(m.group(1), "nomad_entry_id", locs)
        for m in NOMAD_SHORT.finditer(text):
            add_id(m.group(0), "nomad_material_id", locs)
        rows = []
        if base.endswith((".csv", ".tsv")):
            try:
                rows = list(csv.DictReader(io.StringIO(text), delimiter="\t" if base.endswith(".tsv") else ","))
            except csv.Error:
                rows = []
            for r in rows:
                for k in ID_COLS & set(r):
                    v = (r.get(k) or "").strip()
                    if BARE_ID.fullmatch(v) and not v.startswith("mp-"):
                        add_id(v, "nomad_entry_id_bare", locs)
        elif base.endswith(".json"):
            try:
                rows = [d for d in json_records(json.loads(text))]
            except ValueError:
                rows = []
        elif base.endswith(".jsonl"):
            for line in text.splitlines():
                try:
                    rows.extend(json_records(json.loads(line)))
                except ValueError:
                    continue
        # 2. formulas of NOMAD / slab records
        if name in DRAW_RECORDS:
            continue
        for r in rows:
            if not isinstance(r, dict) or not is_nomad_or_slab(r):
                continue
            for k, v in r.items():
                if "formula" in str(k).lower() and isinstance(v, str) and v:
                    add_formula(v, locs)
    proc.stdin.close(); proc.wait()

    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "exclusion_nomad_ids.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "kinds", "n_source_files", "n_branches", "source_files"])
        for ident in sorted(ids):
            r = ids[ident]
            w.writerow([ident, ";".join(sorted(r["kinds"])), len(r["sources"]), len(r["branches"]),
                        ";".join(sorted(r["sources"]))])
    with open(out / "exclusion_slab_formulas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["reduced_formula", "formula_strings", "n_source_files", "n_branches", "source_files"])
        for red in sorted(forms):
            r = forms[red]
            w.writerow([red, ";".join(sorted(r["strings"])), len(r["sources"]), len(r["branches"]),
                        ";".join(sorted(r["sources"]))])
    by_kind: dict[str, int] = defaultdict(int)
    for r in ids.values():
        for k in r["kinds"]:
            by_kind[k] += 1
    strict = json.loads((repo / "analysis/hb_slab_aeccar_cohort_20261007/selection/exclusion_set.json").read_text())
    summary = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_branches_scanned": len(refs), "branches": {r: ref_sha[r] for r in refs},
        "n_unique_blobs_scanned": len(blobs), "skipped_listing_paths": sorted(skipped),
        "n_nomad_ids": len(ids), "n_nomad_ids_by_kind": dict(sorted(by_kind.items())),
        "n_entry_ids_28": sum(1 for i in ids if BARE_ID.fullmatch(i)),
        "n_material_ids_nomad_prefix": sum(1 for i in ids if i.startswith("nomad-")),
        "n_slab_formulas": len(forms),
        "strict_rule_previous_cohort": {"source": "analysis/hb_slab_aeccar_cohort_20261007/selection/exclusion_set.json",
                                        "n_ids_total": strict["n_ids_total"],
                                        "n_ids_by_kind": strict["n_ids_by_kind"],
                                        "n_reduced_formulas_total": strict["n_reduced_formulas_total"]},
        "sha256": {"exclusion_nomad_ids.csv": sha256_lf(out / "exclusion_nomad_ids.csv"),
                   "exclusion_slab_formulas.csv": sha256_lf(out / "exclusion_slab_formulas.csv")},
    }
    (out / "exclusion_sets.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("branches", "skipped_listing_paths")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
