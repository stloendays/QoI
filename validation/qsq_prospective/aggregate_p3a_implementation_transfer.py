#!/usr/bin/env python3
"""Aggregate the frozen 24-system P3A implementation-transfer experiment."""
from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np
from scipy.stats import spearmanr

SOLVERS = ("baderkit_ongrid", "henkelman_ongrid", "henkelman_neargrid")
HENKELMAN = SOLVERS[1:]
TAUS = (1e-4, 1e-3, 1e-2)
PRINT_TOL = 2e-6


def args():
    p=argparse.ArgumentParser(); p.add_argument("--panel",type=Path,required=True); p.add_argument("--shards-root",type=Path,required=True); p.add_argument("--output-dir",type=Path,required=True); return p.parse_args()

def read_csv(p:Path):
    with p.open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def write_csv(p:Path, rows:list[dict[str,Any]]):
    p.parent.mkdir(parents=True,exist_ok=True); fields=list(rows[0]) if rows else []
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def kappa(a:list[bool], b:list[bool]) -> float:
    if not a: return float("nan")
    po=sum(x==y for x,y in zip(a,b))/len(a); pa=sum(a)/len(a); pb=sum(b)/len(b); pe=pa*pb+(1-pa)*(1-pb)
    return (po-pe)/(1-pe) if pe < 1 else 1.0

def main():
    a=args(); panel=read_csv(a.panel); floors={r["material_id"]:float(r["stability_floor_A1_e"]) for r in panel}
    if len(panel)!=24 or len(floors)!=24: raise RuntimeError("P3A panel drift")
    outcomes=[]; failures=[]
    for p in sorted(a.shards_root.rglob("outcomes_shard_*.csv")): outcomes += read_csv(p)
    for p in sorted(a.shards_root.rglob("failures_shard_*.csv")): failures += read_csv(p)
    if len(outcomes)+len(failures)!=432: raise RuntimeError(f"P3A accounting must be 432; got {len(outcomes)+len(failures)}")
    def key(r): return (r.get("material_id",""),r.get("variant",""),r.get("seed",""),r.get("solver",""))
    keys=[key(r) for r in outcomes+failures]
    if len(keys)!=len(set(keys)): raise RuntimeError("duplicate P3A solver-evaluation key")

    by=defaultdict(list); base={}
    for r in outcomes:
        by[(r["material_id"],r["solver"])].append(r)
        if r.get("variant")=="baseline": base[(r["material_id"],r["solver"])]=np.array(json.loads(r["charges_json"]),dtype=float)
    material=[]
    for p in panel:
        m=p["material_id"]; frozen=floors[m]
        b0=base.get((m,"baderkit_ongrid"))
        for solver in SOLVERS:
            noise=[r for r in by.get((m,solver),[]) if r.get("variant")=="noise"]
            complete=len(noise)==5
            floor=max((float(r["response_e"]) for r in noise),default=float("nan"))
            baseline_delta=float("nan")
            if solver!="baderkit_ongrid" and b0 is not None and (m,solver) in base:
                q=base[(m,solver)]; baseline_delta=float(np.max(np.abs(q-b0))) if q.shape==b0.shape else float("nan")
            material.append({"material_id":m,"system_type":p["system_type"],"floor_band":p["floor_band"],"solver":solver,"complete_five_seed":complete,"frozen_baderkit_floor_e":frozen,"recreated_floor_e":floor,"frozen_recreated_abs_delta_e":abs(floor-frozen) if solver=="baderkit_ongrid" and complete else float("nan"),"baseline_max_abs_delta_vs_baderkit_e":baseline_delta})

    comparisons=[]
    for tau in TAUS:
        frozen_class={m:(f<tau) for m,f in floors.items()}
        for solver in HENKELMAN:
            aa=[];bb=[]; unresolved=ambiguous=switch_er=switch_re=0
            for r in material:
                if r["solver"]!=solver: continue
                m=r["material_id"]
                if not r["complete_five_seed"]: unresolved+=1; continue
                f=float(r["recreated_floor_e"])
                if abs(f-tau)<=PRINT_TOL: ambiguous+=1; continue
                h=f<tau; q=frozen_class[m]; aa.append(q);bb.append(h)
                if q and not h: switch_er+=1
                if (not q) and h: switch_re+=1
            comparisons.append({"tau_e":tau,"solver":solver,"panel_materials":24,"comparable_materials":len(aa),"unresolved_materials":unresolved,"ambiguous_materials":ambiguous,"agreement_fraction":sum(x==y for x,y in zip(aa,bb))/len(aa) if aa else float("nan"),"cohen_kappa":kappa(aa,bb),"eligible_to_rejected":switch_er,"rejected_to_eligible":switch_re})

    ranks=[]
    for solver in SOLVERS:
        rr=[r for r in material if r["solver"]==solver and r["complete_five_seed"]]
        if len(rr)>=3:
            rho,pv=spearmanr([r["frozen_baderkit_floor_e"] for r in rr],[r["recreated_floor_e"] for r in rr])
        else: rho=pv=float("nan")
        ranks.append({"solver":solver,"complete_materials":len(rr),"spearman_rho_vs_frozen_baderkit_floor":float(rho),"spearman_p_descriptive":float(pv)})

    a.output_dir.mkdir(parents=True,exist_ok=True)
    write_csv(a.output_dir/"p3a_material_floors.csv",material); write_csv(a.output_dir/"p3a_classification_transfer.csv",comparisons); write_csv(a.output_dir/"p3a_floor_rank_transfer.csv",ranks)
    max_recreate=max((float(r["frozen_recreated_abs_delta_e"]) for r in material if r["solver"]=="baderkit_ongrid" and r["complete_five_seed"]),default=float("nan"))
    report=["# P3A implementation-transfer validation","",f"Accounted solver evaluations: **{len(outcomes)+len(failures)}/432**; successful rows: **{len(outcomes)}**; failed rows: **{len(failures)}**.","",f"Maximum absolute difference between recreated and frozen BaderKit five-seed floors among complete cases: **{max_recreate:.6g} e**.","","## Classification transfer","","| tau | Independent implementation | Comparable | Ambiguous | Unresolved | Agreement | Cohen kappa | Eligible->rejected | Rejected->eligible |","|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in comparisons:
        report.append(f"| {r['tau_e']:.0e} e | {r['solver']} | {r['comparable_materials']} | {r['ambiguous_materials']} | {r['unresolved_materials']} | {100*r['agreement_fraction']:.1f}% | {r['cohen_kappa']:.3f} | {r['eligible_to_rejected']} | {r['rejected_to_eligible']} |")
    report += ["","## Floor-rank transfer","","| Solver | Complete materials | Spearman rho vs frozen BaderKit floor |","|---|---:|---:|"]
    for r in ranks: report.append(f"| {r['solver']} | {r['complete_materials']} | {r['spearman_rho_vs_frozen_baderkit_floor']:.3f} |")
    report += ["","## Interpretation boundary","","This 24-system panel is deterministically stratified for numerical robustness, not sampled for population prevalence. Agreement supports transfer of the low-risk/high-risk stratification across the tested analysis implementations; disagreement, especially when accompanied by large unperturbed charge differences, defines an implementation-sensitive boundary. P3A does not establish electronic-structure grid convergence or a unique physical Bader reference."]
    (a.output_dir/"P3A_IMPLEMENTATION_TRANSFER_REPORT.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    manifest={"status":"COMPLETE" if not failures else "COMPLETE_WITH_RECORDED_FAILURES","planned_solver_evaluations":432,"successful_rows":len(outcomes),"failed_rows":len(failures),"panel_materials":24,"original_qsq_gate_modified":False,"p2_modified":False}
    (a.output_dir/"execution_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("\n".join(report)); return 0

if __name__=="__main__": raise SystemExit(main())
