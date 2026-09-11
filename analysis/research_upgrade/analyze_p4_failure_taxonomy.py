#!/usr/bin/env python3
"""Classify every first-run P4 compressed-stage failure before any retry."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_TOTAL = 144
EXPECTED_FAMILIES = {
    "SPERR_WORKDIR_NOT_CREATED": 72,
    "HENKELMAN_WORKDIR_NOT_CREATED": 72,
}


def read_csv(p: Path):
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify(r):
    codec = r.get("codec", "")
    solver = r.get("solver", "")
    stage = r.get("stage", "")
    err = r.get("error", "")
    if codec == "SPERR" and stage == "codec" and "sperr.h5" in err and "No such file or directory" in err:
        return "SPERR_WORKDIR_NOT_CREATED"
    if solver == "henkelman_ongrid" and stage == "henkelman" and "No such file or directory" in err and "/henkelman/" in err:
        return "HENKELMAN_WORKDIR_NOT_CREATED"
    return "UNCLASSIFIED"


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--failures",type=Path,required=True); ap.add_argument("--output-dir",type=Path,required=True); a=ap.parse_args()
    rows=read_csv(a.failures); out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    if len(rows)!=EXPECTED_TOTAL: raise RuntimeError(f"expected {EXPECTED_TOTAL} failures; got {len(rows)}")
    seen=set(); classified=[]; fam=Counter(); stage=Counter(); codec=Counter(); solver=Counter(); mats=defaultdict(set)
    for r in rows:
        key=(r["material_id"],r["codec"],r["relative_tolerance"],r["solver"])
        if key in seen: raise RuntimeError(f"duplicate failure key {key}")
        seen.add(key)
        f=classify(r); fam[f]+=1; stage[r["stage"]]+=1; codec[r["codec"]]+=1; solver[r["solver"]]+=1; mats[f].add(r["material_id"])
        classified.append({**r,"failure_family":f})
    if dict(fam)!=EXPECTED_FAMILIES: raise RuntimeError(f"unexpected failure taxonomy: {dict(fam)}")
    if fam.get("UNCLASSIFIED",0): raise RuntimeError("unclassified P4 failures remain")
    # Exact combinatorial pattern: 9 states. SPERR fails before both solvers (9*4*2=72);
    # ZFP/SZ3 each fail only at Henkelman output path (9*2*4=72).
    all_mats={r["material_id"] for r in rows}
    if len(all_mats)!=9: raise RuntimeError(f"expected failures on 9 unique states; got {len(all_mats)}")
    if codec != Counter({"SPERR":72,"SZ3":36,"ZFP":36}): raise RuntimeError(f"unexpected codec counts {codec}")
    if solver != Counter({"henkelman_ongrid":108,"baderkit_ongrid":36}): raise RuntimeError(f"unexpected solver counts {solver}")
    if stage != Counter({"codec":72,"henkelman":72}): raise RuntimeError(f"unexpected stage counts {stage}")
    fields=list(classified[0]);
    with (out/"P4_FIRST_RUN_FAILURES_CLASSIFIED.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(classified)
    manifest={
        "status":"FAILURE_TAXONOMY_COMPLETE_BEFORE_RETRY",
        "first_run_failures":len(rows),"unclassified_failures":fam.get("UNCLASSIFIED",0),
        "failure_family_counts":dict(fam),"stage_counts":dict(stage),"codec_counts":dict(codec),"solver_counts":dict(solver),
        "unique_affected_states":len(all_mats),
        "scientific_parameter_change_authorized":False,
        "allowed_engineering_fixes":["create SPERR codec work directory before frozen codec_roundtrip","create Henkelman solver work directory before validated adapter call"],
    }
    (out/"execution_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    report=[
        "# P4 first-run compressed-stage failure taxonomy","",
        "Status: **COMPLETE_BEFORE_RETRY**","",
        f"All **{len(rows)}/{len(rows)}** recorded failures were assigned to one of two pre-solver/solver-path engineering families; **0 unclassified failures** remain.","",
        "| Failure family | Count | Scientific computation reached? | Authorized fix |","|---|---:|---|---|",
        f"| SPERR work directory not created | {fam['SPERR_WORKDIR_NOT_CREATED']} | Codec did not start | Create the per-condition parent directory, then call the unchanged frozen SPERR codec |",
        f"| Henkelman work directory not created | {fam['HENKELMAN_WORKDIR_NOT_CREATED']} | Reconstruction exists; independent solver did not start | Create the per-condition solver directory, then call the unchanged validated Henkelman adapter |","",
        f"Affected states: **{len(all_mats)}**. Codec counts: SPERR 72, SZ3 36, ZFP 36. Solver counts: Henkelman 108, BaderKit 36.","",
        "## Retry boundary","",
        "The first run remains immutable. Retry may execute only the 144 recorded failure keys. No candidate pair, target atom, reference margin, codec, codec tolerance, QSQ threshold, solver definition, or decision policy may change. Previously successful 72 cells must be reused, not rerun for primary accounting.",
    ]
    (out/"P4_FAILURE_TAXONOMY.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__": main()
