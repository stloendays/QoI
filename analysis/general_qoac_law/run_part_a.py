#!/usr/bin/env python3
"""Part A of the General-QOAC law confirmation: the frozen v0.3 engineering arms A0-A6 on a fresh manifest.

Reuses analysis/qoac_v03_rdo/run_engineering.py unchanged (its `material` function); only the manifest differs.
"""
from __future__ import annotations
import argparse,csv,sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"qoac_v03_rdo"))
import run_engineering as eng

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True); p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True); p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True); p.add_argument("--only",default=""); p.add_argument("--workers",type=int,default=1)
    a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); a.cache_dir.mkdir(parents=True,exist_ok=True)
    man=list(csv.DictReader(open(a.manifest,encoding="utf-8")))
    if a.only: man=[m for m in man if m["material_id"] in a.only.split(",")]
    jobs=[(m,str(a.repo_root.resolve()),str(a.frozen_root.resolve()),str(a.cache_dir.resolve())) for m in man]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for mid,rows,fails,secs in ex.map(eng.material,jobs):
            for name,data in (("rows",rows),("failures",fails)):
                if data:
                    f=list(dict.fromkeys(k for r in data for k in r))
                    with (a.output_dir/f"{name}_{mid}.csv").open("w",newline="",encoding="utf-8") as fh:
                        w=csv.DictWriter(fh,fieldnames=f); w.writeheader(); w.writerows(data)
            print(f"PARTA_DONE {mid} rows={len(rows)} failures={len(fails)} seconds={secs:.0f}",flush=True)

if __name__=="__main__": raise SystemExit(main())
