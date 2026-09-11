#!/usr/bin/env python3
"""Merge immutable first-run P4 successes with engineering-only retry successes.

The first run's 72 successful cells are reused from its archived shard artifacts;
retry is required to supply exactly the 144 preclassified failed keys. The
result is then passed through the frozen P4 policy analysis, with a CSV writer
that preserves the union of row fields for complete auditability.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,sys,tempfile
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
import aggregate_p4_chemical_decisions as base


def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def write_union(p:Path,rows:list[dict[str,Any]],fallback:list[str]):
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields:fields.append(k)
    if not fields:fields=fallback
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def key(r):return (r.get('material_id',''),r.get('codec',''),float(r.get('relative_tolerance',0)),r.get('solver',''))

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--reference-valid-pairs',type=Path,required=True);ap.add_argument('--stability-per-seed',type=Path,required=True);ap.add_argument('--first-shards-root',type=Path,required=True);ap.add_argument('--retry-shards-root',type=Path,required=True);ap.add_argument('--classified-failures',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    first_rows=[];first_fail=[];retry_rows=[];retry_fail=[]
    for p in sorted(a.first_shards_root.rglob('compressed_rows_shard_*.csv')):first_rows+=read_csv(p)
    for p in sorted(a.first_shards_root.rglob('compressed_failures_shard_*.csv')):first_fail+=read_csv(p)
    for p in sorted(a.retry_shards_root.rglob('retry_rows_shard_*.csv')):retry_rows+=read_csv(p)
    for p in sorted(a.retry_shards_root.rglob('retry_failures_shard_*.csv')):retry_fail+=read_csv(p)
    frozen_fail=read_csv(a.classified_failures)
    if len(first_rows)!=72 or len(first_fail)!=144:raise RuntimeError(f'first-run accounting drift: {len(first_rows)} success {len(first_fail)} fail')
    if len(frozen_fail)!=144:raise RuntimeError('taxonomy drift')
    first_success_keys={key(r) for r in first_rows};first_fail_keys={key(r) for r in first_fail};tax_keys={key(r) for r in frozen_fail};retry_success_keys={key(r) for r in retry_rows};retry_fail_keys={key(r) for r in retry_fail}
    if first_fail_keys!=tax_keys:raise RuntimeError('taxonomy keys differ from immutable first-run failures')
    if retry_success_keys|retry_fail_keys!=tax_keys:raise RuntimeError('retry did not account for exactly the frozen failed keys')
    if retry_success_keys&first_success_keys:raise RuntimeError('retry touched a first-run success key')
    if retry_fail:raise RuntimeError(f'{len(retry_fail)} retry failures remain; resolved primary analysis blocked')
    merged=first_rows+retry_rows
    if len(merged)!=216 or len({key(r) for r in merged})!=216:raise RuntimeError('resolved merged P4 must contain exactly 216 unique successful solver cells')

    with tempfile.TemporaryDirectory(prefix='qoi_p4_resolved_') as td:
        stage=Path(td);write_union(stage/'compressed_rows_shard_00.csv',merged,['material_id','codec','relative_tolerance','solver','status']);write_union(stage/'compressed_failures_shard_00.csv',[],['material_id','codec','relative_tolerance','solver','status','stage','error'])
        # Preserve all variable fields in derived trial CSVs; original writer used first-row keys only.
        base.write_csv=write_union
        old=sys.argv
        sys.argv=['aggregate_p4_chemical_decisions.py','--reference-valid-pairs',str(a.reference_valid_pairs),'--stability-per-seed',str(a.stability_per_seed),'--shards-root',str(stage),'--output-dir',str(a.output_dir)]
        try:base.main()
        finally:sys.argv=old

    manifest_path=a.output_dir/'execution_manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));manifest.update({
        'status':'COMPLETE_RESOLVED','first_run_id':34617416199,'first_run_success_rows_reused':72,'first_run_failed_rows_preserved':144,'retry_success_rows':144,'retry_failed_rows':0,'final_successful_solver_rows':216,'final_failed_solver_rows':0,'retry_changed_scientific_definition':False,'retry_scope':'exact 144 preclassified first-run failure keys','first_run_artifact_source':'GitHub Actions run 34617416199',
    });manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    provenance={'first_run_rows_sha256':hashlib.sha256(('\n'.join(sorted('|'.join(map(str,key(r))) for r in first_rows))).encode()).hexdigest(),'taxonomy_sha256':hashlib.sha256(a.classified_failures.read_bytes()).hexdigest(),'retry_rows':len(retry_rows),'merged_rows':len(merged),'github_retry_run_id':os.environ.get('GITHUB_RUN_ID','')}
    (a.output_dir/'RESOLVED_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    report=a.output_dir/'P4_CHEMICAL_DECISION_REPORT.md';text=report.read_text(encoding='utf-8');prefix="# P4 resolved engineering-retry note\n\nThe primary scientific design is unchanged. The immutable first run produced 72 successful cells and 144 path-engineering failures. A pre-retry taxonomy assigned all 144 failures to missing work-directory creation. The retry executed exactly those failed keys and returned 144/144 successes; final policy analysis therefore uses 216/216 successful solver cells.\n\n"
    report.write_text(prefix+text,encoding='utf-8')
    print(json.dumps(manifest,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
