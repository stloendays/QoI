#!/usr/bin/env python3
"""Exclusion union for the self-computed slab cohort (metadata only).

Union of
  (a) analysis/hb_slab_aeccar_cohort_20261007/selection/exclusion_ids.csv and exclusion_formulas.csv (committed at
      bab69ec; 1,053 ids and 690 reduced formulas, built over 76 origin branches on 2026-10-07 09:15 UTC);
  (b) a new scan, now, of every text-like data file on every `origin/*` branch and every local branch of this
      checkout (local branches hold commits that could not be pushed), with the identifier regexes, formula columns
      and pymatgen reduction of analysis/fresh_population_20261006/scripts/build_exclusion.py (imported; plus a regex
      for the letter-format MP ids of the 2026 build, e.g. mp-aaahgjou) and the
      listing-file skip list of analysis/hb_slab_aeccar_cohort_20261007/selection/build_exclusion_set.py (imported),
      extended by the candidate listings of the wide NOMAD cohort (candidates.csv, relisted_entries.csv) and its
      exclusion tables. This covers every committed manifest: P1, P2, P3b, the N = 4 cohort, the wide NOMAD cohort,
      the WP-F sample and checkpoints (origin/research/wpf-cloud-completion-20261007), the external cohorts;
  (c) the reduced formula, in the MP summary collection of this cohort, of every Materials Project id in (a) or (b)
      (matched on `material_id` or on membership in `task_ids`), so that a used MP id whose file carries no formula
      column still excludes its formula.

Outputs (in --out-dir): exclusion_ids_union.csv, exclusion_formulas_union.csv, exclusion_union.json.

Usage: build_exclusion_union.py --repo <checkout with origin/* fetched> --summary <parquet> --out-dir <dir>
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
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[2]
COHORT4 = Path("analysis/hb_slab_aeccar_cohort_20261007/selection")
EXTRA_LISTINGS = {"candidates.csv", "relisted_entries.csv", "exclusion_nomad_ids.csv", "exclusion_slab_formulas.csv",
                  "exclusion_sets.json", "exclusion_ids_union.csv", "exclusion_formulas_union.csv",
                  "exclusion_union.json", "funnel_meta.json", "relist_log.json"}
# The 2026 MP build also issues letter-format ids (e.g. mp-aaahgjou), which build_exclusion.MP_RE does not match.
MP_NEW_RE = re.compile(r"(?<![A-Za-z0-9_])mp-[a-z]{6,12}(?![A-Za-z0-9_])")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_text_file(p: Path) -> str:
    """SHA-256 of the committed bytes (LF line ends; a Windows checkout may hold CRLF)."""
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=REPO_DEFAULT)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    repo = a.repo.resolve()
    be = load("build_exclusion", repo / "analysis/fresh_population_20261006/scripts/build_exclusion.py")
    bes = load("build_exclusion_set", repo / COHORT4 / "build_exclusion_set.py")
    listing = set(bes.LISTING_FILES) | EXTRA_LISTINGS

    ids: dict[str, dict] = {}
    formulas: dict[str, dict] = {}

    def add_id(ident, kind, src, path=None, ref=None):
        rec = ids.setdefault(ident, {"kinds": set(), "sources": set(), "files": set(), "branches": set()})
        rec["kinds"].add(kind); rec["sources"].add(src)
        if path:
            rec["files"].add(path)
        if ref:
            rec["branches"].add(ref)

    def add_formula(red, src, path=None, ref=None):
        rec = formulas.setdefault(red, {"sources": set(), "files": set(), "branches": set()})
        rec["sources"].add(src)
        if path:
            rec["files"].add(path)
        if ref:
            rec["branches"].add(ref)

    # (a) committed exclusion set of the N = 4 cohort
    in_ids, in_f = repo / COHORT4 / "exclusion_ids.csv", repo / COHORT4 / "exclusion_formulas.csv"
    for r in csv.DictReader(open(in_ids, encoding="utf-8")):
        for k in r["kinds"].split(";"):
            add_id(r["id"], k, "a:cohort4_exclusion_ids", r["example_source_file"])
    for r in csv.DictReader(open(in_f, encoding="utf-8")):
        add_formula(r["reduced_formula"], "a:cohort4_exclusion_formulas", r["example_source_file"])
    n_a_ids, n_a_f = len(ids), len(formulas)

    # (b) scan every origin/* and local branch now
    refs = [r for r in be.git(repo, "for-each-ref", "refs/remotes/origin", "refs/heads",
                              "--format=%(refname:short)").split() if r not in ("origin", "origin/HEAD")]
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
            if path.rsplit("/", 1)[-1] in listing:
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
        for m in MP_NEW_RE.finditer(text):
            found.add((m.group(0), "mp_id_letter_format"))
        for m in be.NOMAD_ENTRY_RE.finditer(text):
            found.add((m.group(1), "nomad_entry_id"))
        for m in be.NOMAD_SHORT_RE.finditer(text):
            found.add(("nomad-" + m.group(1), "nomad_material_id"))
        for ident, kind in found:
            for ref, path in locs:
                add_id(ident, kind, "b:branch_scan", path, ref)
        if path0.lower().removesuffix(".gz").endswith(be.STRUCTURED):
            for _, val in be.formula_values(path0, text):
                red = be.reduce_formula(val)
                if red is None:
                    continue
                for ref, path in locs:
                    add_formula(red, "b:branch_scan", path, ref)
    proc.stdin.close(); proc.wait()
    n_ab_f = len(formulas)

    # (c) formulas of every excluded MP id, from the cohort's MP summary collection
    import pyarrow.parquet as pq
    from pymatgen.core import Composition
    t = pq.read_table(a.summary, columns=["material_id", "task_ids", "formula_pretty"]).to_pylist()
    mp_ids = {i for i, r in ids.items() if i.startswith("mp-")}
    n_mp_matched = 0
    for row in t:
        hit = {row["material_id"]} | set(row["task_ids"] or [])
        hit &= mp_ids
        if not hit:
            continue
        n_mp_matched += 1
        red = Composition(row["formula_pretty"]).reduced_formula
        for i in sorted(hit):
            add_formula(red, "c:mp_summary_formula_of_excluded_id", f"{i} -> {row['material_id']}")
    del t

    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "exclusion_ids_union.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "kinds", "sources", "n_source_files", "example_source_file", "n_branches"])
        for ident in sorted(ids):
            r = ids[ident]
            w.writerow([ident, ";".join(sorted(r["kinds"])), ";".join(sorted(r["sources"])), len(r["files"]),
                        sorted(r["files"])[0] if r["files"] else "", len(r["branches"])])
    with open(out / "exclusion_formulas_union.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["reduced_formula", "sources", "n_source_files", "example_source_file", "n_branches"])
        for red in sorted(formulas):
            r = formulas[red]
            w.writerow([red, ";".join(sorted(r["sources"])), len(r["files"]),
                        sorted(r["files"])[0] if r["files"] else "", len(r["branches"])])
    by_src_ids: dict[str, int] = defaultdict(int)
    for r in ids.values():
        for s in r["sources"]:
            by_src_ids[s] += 1
    by_src_f: dict[str, int] = defaultdict(int)
    for r in formulas.values():
        for s in r["sources"]:
            by_src_f[s] += 1
    by_kind: dict[str, int] = defaultdict(int)
    for r in ids.values():
        for k in r["kinds"]:
            by_kind[k] += 1
    summary = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "cohort4_exclusion_ids.csv": {"path": str(COHORT4 / "exclusion_ids.csv").replace("\\", "/"),
                                          "sha256": sha256_text_file(in_ids), "n": n_a_ids},
            "cohort4_exclusion_formulas.csv": {"path": str(COHORT4 / "exclusion_formulas.csv").replace("\\", "/"),
                                               "sha256": sha256_text_file(in_f), "n": n_a_f},
            "mp_summary_parquet": {"name": a.summary.name, "sha256": hashlib.sha256(a.summary.read_bytes()).hexdigest()},
        },
        "n_refs_scanned": len(refs),
        "refs": {r: ref_sha[r] for r in refs},
        "n_unique_blobs_scanned": len(blobs),
        "skipped_listing_paths": sorted(skipped),
        "n_ids_total": len(ids),
        "n_ids_by_kind": dict(sorted(by_kind.items())),
        "n_ids_by_source": dict(sorted(by_src_ids.items())),
        "n_mp_ids": len(mp_ids),
        "n_mp_summary_rows_matched": n_mp_matched,
        "n_reduced_formulas_total": len(formulas),
        "n_reduced_formulas_after_a": n_a_f,
        "n_reduced_formulas_after_a_b": n_ab_f,
        "n_reduced_formulas_by_source": dict(sorted(by_src_f.items())),
        "sha256": {"exclusion_ids_union.csv": sha256_text_file(out / "exclusion_ids_union.csv"),
                   "exclusion_formulas_union.csv": sha256_text_file(out / "exclusion_formulas_union.csv")},
    }
    (out / "exclusion_union.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("refs", "skipped_listing_paths")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
