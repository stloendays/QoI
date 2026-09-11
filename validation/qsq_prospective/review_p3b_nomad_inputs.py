#!/usr/bin/env python3
"""Review exact raw NOMAD VASP inputs for the 12 provenance-complete P3B slab candidates."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, ssl, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from typing import Any

UA="QoI-QSQ-P3B-exact-input-review/1.0"
BASE="https://nomad-lab.eu/prod/v1/api/v1"
RAW_FILES=("INCAR","KPOINTS","OUTCAR")
RELEVANT_INCAR=(
    "ENCUT","PREC","ADDGRID","NGX","NGY","NGZ","NGXF","NGYF","NGZF",
    "ISPIN","MAGMOM","NUPDOWN","ISMEAR","SIGMA","GGA","METAGGA","LHFCALC",
    "LDAU","LDAUTYPE","LDAUL","LDAUU","LDAUJ","LASPH","LREAL","EDIFF","NELM",
    "ALGO","ICHARG","ISTART","LCHARG","LWAVE","IBRION","NSW","ISIF"
)

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def get(url:str,tries:int=3)->bytes:
    last=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=90,context=ssl.create_default_context()) as r:return r.read()
        except Exception as exc:
            last=exc
            if isinstance(exc,urllib.error.HTTPError) and exc.code in (401,403,404):break
            if i+1<tries:time.sleep(2**i)
    raise RuntimeError(f"GET failed {url}: {type(last).__name__}: {last}")

def rows(p:Path):
    with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def entry_id(url:str)->str:
    m=re.search(r"/entries/([^/]+)/raw/",url)
    if not m:raise RuntimeError(f"cannot parse NOMAD entry id: {url}")
    return m.group(1)

def parse_incar(data:bytes)->dict[str,str]:
    text=data.decode("utf-8",errors="replace")
    out={}
    for line in text.splitlines():
        line=re.split(r"[#!]",line,1)[0]
        for part in line.split(";"):
            if "=" not in part:continue
            k,v=part.split("=",1);k=k.strip().upper();v=v.strip()
            if k:out[k]=v
    return out

def parse_kpoints(data:bytes)->dict[str,Any]:
    text=data.decode("utf-8",errors="replace")
    clean=[x.strip() for x in text.splitlines() if x.strip()]
    out={"sha256":sha(data),"line_count":len(clean),"comment":clean[0] if clean else ""}
    if len(clean)>=4:
        try:n=int(clean[1].split()[0])
        except Exception:n=-1
        out["declared_count"]=n
        out["mode"]=clean[2]
        if n==0:
            out["mesh"]=clean[3]
            out["shift"]=clean[4] if len(clean)>=5 else ""
        else:
            out["explicit_point_lines"]=max(0,min(n,len(clean)-3))
            out["first_point"]=clean[3] if len(clean)>3 else ""
    return out

def outcar_summary(data:bytes)->dict[str,Any]:
    text=data.decode("utf-8",errors="replace")
    versions=[]
    for line in text.splitlines()[:80]:
        m=re.search(r"\bvasp\.([0-9][0-9A-Za-z._-]*)",line,re.I)
        if m and m.group(1) not in versions:versions.append(m.group(1))
    titles=[]
    for m in re.finditer(r"TITEL\s*=\s*([^\n\r]+)",text,re.I):
        x=m.group(1).strip()
        if x not in titles:titles.append(x)
    return {"sha256":sha(data),"vasp_versions_header":versions,"potcar_titles":titles}

def xc_descriptor(inc:dict[str,str])->str:
    keys=["GGA","METAGGA","LHFCALC","LDAU","LDAUTYPE","LDAUL","LDAUU","LDAUJ"]
    return "; ".join(f"{k}={inc[k]}" for k in keys if k in inc) or "NO_EXPLICIT_XC_TOKEN"

def main()->int:
    a=argparse.ArgumentParser();a.add_argument("--repo-root",type=Path,required=True);a.add_argument("--output-dir",type=Path,required=True);z=a.parse_args()
    root=z.repo_root.resolve();out=z.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    panel=rows(root/"validation/qsq_prospective/convergence_panel.csv");meta={r["material_id"]:r for r in rows(root/"materials_metadata.csv")}
    selected=[r for r in panel if r["system_type"]=="slab"]
    if len(selected)!=12:raise RuntimeError(f"expected 12 frozen slab candidates, got {len(selected)}")
    detail={};table=[]
    for i,p in enumerate(selected,1):
        m=p["material_id"];mm=meta[m]
        if not mm["source"].startswith("NOMAD"):raise RuntimeError(f"slab candidate is not NOMAD: {m}")
        eid=entry_id(mm["url"]); blobs={}
        for name in RAW_FILES:
            u=f"{BASE}/entries/{eid}/raw/{urllib.parse.quote(name)}";blobs[name]=get(u)
        inc=parse_incar(blobs["INCAR"]);kp=parse_kpoints(blobs["KPOINTS"]);oc=outcar_summary(blobs["OUTCAR"])
        relevant={k:inc[k] for k in RELEVANT_INCAR if k in inc}
        has_encut="ENCUT" in inc
        has_spin="ISPIN" in inc
        has_smear="ISMEAR" in inc and "SIGMA" in inc
        has_xc=any(k in inc for k in ("GGA","METAGGA","LHFCALC","LDAU"))
        has_grid=any(k in inc for k in ("PREC","NGX","NGY","NGZ","NGXF","NGYF","NGZF"))
        has_pseudo=bool(oc["potcar_titles"])
        has_version=bool(oc["vasp_versions_header"])
        has_kpoints=bool(kp.get("line_count",0)>=4)
        complete=all((has_encut,has_spin,has_smear,has_xc,has_grid,has_pseudo,has_version,has_kpoints))
        static_source=(int(float(inc.get("NSW","0").split()[0]))==0) if re.match(r"^[+-]?[0-9.]+",inc.get("NSW","0")) else False
        rec={
            "material_id":m,"formula":mm["formula"],"floor_band":p["floor_band"],"entry_id":eid,
            "native_ngrid":mm["ngrid"],"source_chgcar_sha256":mm["sha256"],"incar_sha256":sha(blobs["INCAR"]),
            "kpoints_sha256":sha(blobs["KPOINTS"]),"outcar_sha256":sha(blobs["OUTCAR"]),
            "vasp_version":" | ".join(oc["vasp_versions_header"]),"encut":inc.get("ENCUT",""),
            "ispin":inc.get("ISPIN",""),"magmom":inc.get("MAGMOM",""),"ismear":inc.get("ISMEAR",""),"sigma":inc.get("SIGMA",""),
            "xc_tokens":xc_descriptor(inc),"prec":inc.get("PREC",""),"addgrid":inc.get("ADDGRID",""),
            "explicit_grid_tokens":"; ".join(f"{k}={inc[k]}" for k in ("NGX","NGY","NGZ","NGXF","NGYF","NGZF") if k in inc),
            "kpoints_mode":str(kp.get("mode","")),"kpoints_mesh":str(kp.get("mesh","")),"kpoints_shift":str(kp.get("shift","")),
            "potcar_titles":" | ".join(oc["potcar_titles"]),"source_nsw":inc.get("NSW",""),"source_ibrion":inc.get("IBRION",""),
            "source_run_static":static_source,"exact_input_review":"PASS" if complete else "FAIL"
        }
        table.append(rec);detail[m]={"incar_relevant":relevant,"kpoints":kp,"outcar":oc,"review_flags":{"has_encut":has_encut,"has_spin":has_spin,"has_smearing_pair":has_smear,"has_xc_token":has_xc,"has_grid_control":has_grid,"has_pseudopotential_titles":has_pseudo,"has_vasp_version":has_version,"has_kpoints":has_kpoints,"complete":complete}}
        print(f"[{i:02d}/12] {m} {rec['exact_input_review']} VASP={rec['vasp_version']} ENCUT={rec['encut']}",flush=True)
    fields=list(table[0])
    with (out/"p3b_nomad_exact_inputs.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(table)
    (out/"p3b_nomad_exact_inputs.json").write_text(json.dumps(detail,indent=2)+"\n",encoding="utf-8")
    passed=[r for r in table if r["exact_input_review"]=="PASS"]
    lines=["# P3B NOMAD exact-input review","",f"Frozen slab candidates reviewed: **{len(table)}/12**; exact-input review PASS: **{len(passed)}/12**.","","This review uses raw NOMAD `INCAR`, `KPOINTS`, and `OUTCAR` files, while the final cell/atom ordering for any later static rerun remains tied to the frozen CHGCAR itself. POTCAR contents are not downloaded or redistributed; only `TITEL` identity strings parsed from OUTCAR are recorded.","","| Material | Formula | Floor band | VASP | ENCUT | ISPIN | ISMEAR/SIGMA | PREC | KPOINTS | Review |","|---|---|---|---|---:|---:|---|---|---|---|"]
    for r in table:lines.append(f"| {r['material_id']} | {r['formula']} | {r['floor_band']} | {r['vasp_version']} | {r['encut']} | {r['ispin']} | {r['ismear']}/{r['sigma']} | {r['prec']} | {r['kpoints_mode']} {r['kpoints_mesh']} | {r['exact_input_review']} |")
    lines += ["","## Execution boundary","","PASS means the exact raw input/output evidence needed to construct a later static grid-refinement work order is present. It does not mean the required VASP version or matching PAW datasets are available on the execution cluster. Cluster executable and pseudopotential availability must be checked before P3B is authorized. If the source run was a relaxation (`NSW > 0`), P3B will use the frozen CHGCAR geometry in a declared static single-point recomputation; it will not rerun ionic relaxation."]
    (out/"P3B_NOMAD_EXACT_INPUT_REVIEW.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    manifest={"status":"REVIEW_COMPLETE","slab_candidates":12,"exact_input_pass":len(passed),"potcar_contents_downloaded":False,"grid_recomputation_started":False,"panel_sha256":sha((root/"validation/qsq_prospective/convergence_panel.csv").read_bytes())}
    (out/"execution_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return 0
if __name__=="__main__":raise SystemExit(main())
