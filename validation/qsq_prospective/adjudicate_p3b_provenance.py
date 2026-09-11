#!/usr/bin/env python3
"""Strictly adjudicate the frozen P3B provenance-audit candidates.

This is a deterministic post-audit filter. It rejects broad keyword hits that
are not sufficient to reconstruct a VASP static calculation.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from typing import Any

CATS=("code_version","xc","pseudopotential","spin","kpoints","encut","smearing","structure","charge_convention","grid_control")

def read_csv(p:Path):
    with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def low(x:Any)->str:return str(x).lower()
def evidence(items:list[dict[str,str]],pred)->list[dict[str,str]]:return [x for x in items if pred(low(x.get("source","")),low(x.get("path","")),low(x.get("value","")))]

def judge(c:dict[str,list[dict[str,str]]])->dict[str,dict[str,Any]]:
    out={}
    out["code_version"]={"ok":bool(evidence(c["code_version"],lambda s,p,v:(s=="archive" and p.endswith("program.version")) or (s=="outcar" and "vasp_version" in p))),"rule":"archive program.version or OUTCAR VASP header"}
    out["xc"]={"ok":bool(evidence(c["xc"],lambda s,p,v:(s=="archive" and ".dft.xc_functional.name" in p) or (s in {"incar","outcar"} and any(k in p for k in ("gga","metagga","lhfcalc","ldau"))))),"rule":"normalized dft.xc_functional.name or explicit raw XC setting"}
    out["pseudopotential"]={"ok":bool(evidence(c["pseudopotential"],lambda s,p,v:"pseudopotential_name" in p or (s=="outcar" and "potcar_titel" in p))),"rule":"archive pseudopotential_name or OUTCAR POTCAR TITEL"}
    out["spin"]={"ok":bool(evidence(c["spin"],lambda s,p,v:(s in {"incar","outcar"} and "ispin" in p) or (s=="archive" and p.endswith("spin_polarized")))),"rule":"raw ISPIN or normalized spin_polarized"}
    out["kpoints"]={"ok":bool(evidence(c["kpoints"],lambda s,p,v:s=="kpoints" and "raw_kpoints_file" in p)),"rule":"raw KPOINTS file required at this adjudication stage"}
    out["encut"]={"ok":bool(evidence(c["encut"],lambda s,p,v:(s in {"incar","outcar"} and "encut" in p) or (s=="archive" and "planewave_cutoff" in p))),"rule":"raw ENCUT or normalized plane-wave cutoff"}
    raw_smear=evidence(c["smearing"],lambda s,p,v:s in {"incar","outcar"} and ("ismear" in p or "sigma" in p))
    has_ismear=any("ismear" in low(x.get("path","")) for x in raw_smear);has_sigma=any("sigma" in low(x.get("path","")) for x in raw_smear)
    archive_smear=evidence(c["smearing"],lambda s,p,v:s=="archive" and "smearing" in p and "occupation" not in p)
    out["smearing"]={"ok":bool((has_ismear and has_sigma) or archive_smear),"rule":"raw ISMEAR+SIGMA pair or explicit normalized smearing object"}
    out["structure"]={"ok":bool(c["structure"]),"rule":"frozen CHGCAR structure is accepted; raw POSCAR/CONTCAR is additional evidence"}
    out["charge_convention"]={"ok":bool(evidence(c["charge_convention"],lambda s,p,v:"chgcar" in v and "grid.total" in v)),"rule":"frozen analysed CHGCAR total-density convention"}
    out["grid_control"]={"ok":bool(evidence(c["grid_control"],lambda s,p,v:s in {"incar","outcar"} and any(k in p for k in ("prec","ngx","ngy","ngz","addgrid")))),"rule":"raw PREC/NG*/ADDGRID evidence required; generic archive grid fingerprints do not count"}
    return out

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",type=Path,required=True);ap.add_argument("--output-dir",type=Path,required=True);a=ap.parse_args()
    root=a.repo_root.resolve();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    panel=read_csv(root/"validation/qsq_prospective/convergence_panel.csv")
    slabs=[r for r in panel if r["system_type"]=="slab"]
    if len(slabs)!=12:raise RuntimeError("expected 12 frozen slab systems")
    audit=json.loads((root/"validation/qsq_prospective/p3b_provenance_audit/p3b_provenance_candidates.json").read_text(encoding="utf-8"))
    rows=[];details={}
    for p in slabs:
        m=p["material_id"];c=audit[m]["category_candidates"];j=judge(c);ok=sum(bool(j[k]["ok"]) for k in CATS);complete=ok==len(CATS)
        src=audit[m]["source_status"]
        raw=src.get("raw_files",[]);raw200=[x.get("path","") for x in raw if x.get("status")=="HTTP_200"]
        rows.append({"material_id":m,"floor_band":p["floor_band"],"strict_categories_pass":ok,"strict_categories_total":len(CATS),"raw_files_http200":" | ".join(raw200),"strict_status":"STRICT_REVIEW_READY" if complete else "STRICT_INCOMPLETE",**{f"has_{k}":bool(j[k]["ok"]) for k in CATS}})
        details[m]={"judgement":j,"source_status":src}
    fields=list(rows[0])
    with (out/"p3b_strict_provenance_inventory.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    (out/"p3b_strict_provenance_details.json").write_text(json.dumps(details,indent=2)+"\n",encoding="utf-8")
    ready=[r for r in rows if r["strict_status"]=="STRICT_REVIEW_READY"]
    bands={b:sum(r["strict_status"]=="STRICT_REVIEW_READY" and r["floor_band"]==b for r in rows) for b in sorted({r["floor_band"] for r in rows})}
    lines=["# P3B strict provenance adjudication","",f"Frozen NOMAD slab candidates: **12/12**; strict review-ready: **{len(ready)}/12**.","","This adjudication deliberately rejects broad keyword hits. Occupation arrays do not count as smearing settings; eigenvalue k-point coordinates do not replace a raw KPOINTS file in this stage; generic archive grid fingerprints do not replace explicit `PREC/NG*/ADDGRID` evidence.","","| Material | Floor band | Strict categories | Raw input files exposed | Status |","|---|---|---:|---|---|"]
    for r in rows:lines.append(f"| {r['material_id']} | {r['floor_band']} | {r['strict_categories_pass']}/10 | {r['raw_files_http200']} | {r['strict_status']} |")
    lines += ["","## Ready systems by frozen QSQ-floor band",""]+[f"- `{b}`: **{n}**" for b,n in bands.items()]+["","A strict-incomplete system remains in the frozen panel and is not replaced. Further recovery may use the published NOMAD upload directory or exact normalized archive objects, but any relaxation of an extraction rule must be documented before a DFT work order is frozen."]
    (out/"P3B_STRICT_PROVENANCE_REVIEW.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    manifest={"status":"STRICT_ADJUDICATION_COMPLETE","slab_candidates":12,"strict_review_ready":len(ready),"ready_by_floor_band":bands,"grid_recomputation_started":False,"panel_sha256":hashlib.sha256((root/"validation/qsq_prospective/convergence_panel.csv").read_bytes()).hexdigest()}
    (out/"execution_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("\n".join(lines));return 0
if __name__=="__main__":raise SystemExit(main())
