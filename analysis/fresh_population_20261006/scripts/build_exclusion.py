"""Collect every material identifier and formula used on any origin/* branch.

Scans every text-like data file (csv, tsv, json, jsonl, md, txt, yaml, py and
their .gz variants) on every remote-tracking branch. Identifiers are taken by
regex from the full file text; formulas are taken from CSV columns / JSON keys
whose name contains "formula" and reduced with pymatgen.

Usage: build_exclusion.py <repo_root> <out_dir>
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from pymatgen.core import Composition

EXTS = (".csv", ".tsv", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml", ".py")
FRAME_FILES = {"frame.csv.gz"}
STRUCTURED = (".csv", ".tsv", ".json", ".jsonl")

S3_RE = re.compile(r"(chgcars|aeccar0s|aeccar2s)/(mp-\d+)\.json")
MP_RE = re.compile(r"(?<![A-Za-z0-9_])mp-\d+(?!\d)")
NOMAD_ENTRY_RE = re.compile(r"entries/([A-Za-z0-9_\-]{28})(?![A-Za-z0-9_\-])")
NOMAD_SHORT_RE = re.compile(r"(?<![A-Za-z0-9_])nomad-([A-Za-z0-9_\-]{10,28})")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True).stdout.decode("utf-8", "replace")


def iter_formula_values_json(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "formula" in str(k).lower() and isinstance(v, str):
                yield v
            else:
                yield from iter_formula_values_json(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_formula_values_json(v)


def formula_values(path: str, text: str):
    base = path[:-3] if path.endswith(".gz") else path
    if base.endswith((".csv", ".tsv")):
        delim = "\t" if base.endswith(".tsv") else ","
        try:
            reader = csv.DictReader(io.StringIO(text), delimiter=delim)
            cols = [c for c in (reader.fieldnames or []) if c and "formula" in c.lower()]
            if not cols:
                return
            for row in reader:
                for c in cols:
                    v = row.get(c)
                    if v:
                        yield c, v
        except csv.Error:
            return
    elif base.endswith(".json"):
        try:
            obj = json.loads(text)
        except ValueError:
            return
        for v in iter_formula_values_json(obj):
            yield "json", v
    elif base.endswith(".jsonl"):
        for line in text.splitlines():
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            for v in iter_formula_values_json(obj):
                yield "json", v


def reduce_formula(s: str) -> str | None:
    s = s.strip()
    if not s or len(s) > 80 or not re.fullmatch(r"[A-Za-z0-9().\[\]]+", s):
        return None
    if not re.match(r"[A-Z(\[]", s):
        return None
    try:
        comp = Composition(s)
        if comp.num_atoms <= 0 or not all(e.Z > 0 for e in comp.elements):
            return None
        return comp.reduced_formula
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    repo, out = Path(sys.argv[1]), Path(sys.argv[2])
    refs = [r for r in git(repo, "for-each-ref", "refs/remotes/origin",
                          "--format=%(refname:short)").split() if r != "origin"]
    blobs: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for ref in refs:
        for line in git(repo, "ls-tree", "-r", ref).splitlines():
            meta, path = line.split("\t", 1)
            _, typ, sha = meta.split()
            p = path.lower()
            if typ == "blob" and (p.endswith(EXTS) or p[:-3].endswith(EXTS) and p.endswith(".gz")):
                blobs[sha].append((ref, path))

    ids: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    formulas: dict[tuple[str, str], dict] = {}
    unparsed: dict[str, int] = defaultdict(int)

    shas = sorted(blobs)
    proc = subprocess.Popen(["git", "-C", str(repo), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha in shas:
        proc.stdin.write((sha + "\n").encode())
        proc.stdin.flush()
        header = proc.stdout.readline().split()
        size = int(header[2])
        data = proc.stdout.read(size)
        proc.stdout.read(1)
        locs = blobs[sha]
        path0 = locs[0][1]
        if path0.lower().endswith(".gz"):
            try:
                data = gzip.decompress(data)
            except OSError:
                continue
        text = data.decode("utf-8", "replace")
        if path0.rsplit("/", 1)[-1] in FRAME_FILES:
            # Whole-bucket sampling frame (WP-F): only the rows flagged as used
            # by a frozen study identify materials; the rest is an S3 listing.
            rows = csv.DictReader(io.StringIO(text))
            text = "\n".join(r["key"] for r in rows if r.get("in_frozen_study") == "1")
        found: set[tuple[str, str]] = set()
        for m in S3_RE.finditer(text):
            found.add((m.group(2), "mp_task_id_s3_url"))
        task_ids = {i for i, _ in found}
        for m in MP_RE.finditer(text):
            if m.group(0) not in task_ids:
                found.add((m.group(0), "mp_id"))
        for m in NOMAD_ENTRY_RE.finditer(text):
            found.add((m.group(1), "nomad_entry_id"))
        for m in NOMAD_SHORT_RE.finditer(text):
            found.add(("nomad-" + m.group(1), "nomad_material_id"))
        for ref, path in locs:
            for ident, kind in found:
                ids[(ident, kind, path)].add(ref)
        if path0.lower().removesuffix(".gz").endswith(STRUCTURED):
            for col, val in formula_values(path0, text):
                red = reduce_formula(val)
                if red is None:
                    unparsed[val] += 1
                    continue
                key = (val, red)
                rec = formulas.setdefault(key, {"files": set(), "branches": set()})
                for ref, path in locs:
                    rec["files"].add(path)
                    rec["branches"].add(ref)
    proc.stdin.close()
    proc.wait()

    out.mkdir(parents=True, exist_ok=True)
    # Compact table: first branch (alphabetical) + branch count; the full
    # id x file x branch mapping goes to the gzipped companion file.
    with (out / "exclusion_ids.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "kind", "source_file", "branch", "n_branches"])
        for (ident, kind, path), refs_ in sorted(ids.items()):
            w.writerow([ident, kind, path, sorted(refs_)[0], len(refs_)])
    with gzip.open(out / "exclusion_ids_full.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "kind", "source_file", "branch"])
        for (ident, kind, path), refs_ in sorted(ids.items()):
            for ref in sorted(refs_):
                w.writerow([ident, kind, path, ref])
    with (out / "exclusion_formulas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["formula", "reduced_formula", "n_source_files", "example_source_file", "branch", "n_branches"])
        for (val, red), rec in sorted(formulas.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            w.writerow([val, red, len(rec["files"]), sorted(rec["files"])[0],
                        sorted(rec["branches"])[0], len(rec["branches"])])
    summary = {
        "n_branches_scanned": len(refs),
        "branches": refs,
        "n_unique_blobs_scanned": len(shas),
        "n_unique_ids_by_kind": {},
        "n_unique_ids_total": len({i for i, _, _ in ids}),
        "n_formula_strings": len(formulas),
        "n_unique_reduced_formulas": len({r for _, r in formulas}),
        "n_formula_strings_unparsed": len(unparsed),
        "unparsed_formula_examples": sorted(unparsed)[:50],
    }
    by_kind: dict[str, set[str]] = defaultdict(set)
    for ident, kind, _ in ids:
        by_kind[kind].add(ident)
    summary["n_unique_ids_by_kind"] = {k: len(v) for k, v in sorted(by_kind.items())}
    (out / "exclusion_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "branches"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
