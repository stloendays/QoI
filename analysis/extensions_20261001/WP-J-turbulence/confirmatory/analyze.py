#!/usr/bin/env python3
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
RNG=np.random.default_rng(20261001); NBOOT=5000
TARGETS={"mask_response_1mIoU":0.01,"enstrophy_relative_response":1e-4}

def read(name): return list(csv.DictReader((HERE/name).open()))

def kappa(a,b):
    a=np.asarray(a,bool); b=np.asarray(b,bool); po=float(np.mean(a==b))
    pa,pb=float(a.mean()),float(b.mean()); pe=pa*pb+(1-pa)*(1-pb)
    return (po-pe)/(1-pe) if pe<1 else math.nan

def ranks(x):
    x=np.asarray(x,float); o=np.argsort(x,kind="mergesort"); r=np.empty(len(x)); i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[o[j]]==x[o[i]]: j+=1
        r[o[i:j]]=(i+j-1)/2+1; i=j
    return r

q=read("qualification_probes.csv"); f=read("fresh_probes.csv")
ids=sorted({r["sample_id"] for r in q})
floors={m:{sid:max(float(r[m]) for r in q if r["sample_id"]==sid) for sid in ids} for m in TARGETS}
rows=[]
for metric,tau in TARGETS.items():
    elig={sid for sid in ids if floors[metric][sid]<tau}; rej=set(ids)-elig
    fresh={sid:[float(r[metric])>=tau for r in f if r["sample_id"]==sid] for sid in ids}
    risk=lambda group: float(np.mean([x for sid in group for x in fresh[sid]])) if group else math.nan
    re,rr=risk(elig),risk(rej); diff=rr-re
    boots=[]
    for _ in range(NBOOT):
        draw=RNG.choice(ids,size=len(ids),replace=True)
        eg=[x for x in draw if x in elig]; rg=[x for x in draw if x in rej]
        if eg and rg: boots.append(risk(rg)-risk(eg))
    lo,hi=(np.quantile(boots,[.025,.975]) if boots else (math.nan,math.nan))
    ratio=rr/re if re>0 else (math.inf if rr>0 else math.nan)
    accept=len(elig)>=10 and len(rej)>=10 and ratio>=5 and lo>0
    rows.append({"metric":metric,"tau":tau,"n_eligible":len(elig),"n_rejected":len(rej),
                 "fresh_risk_eligible":re,"fresh_risk_rejected":rr,"risk_ratio":ratio,
                 "risk_difference":diff,"ci_low":float(lo),"ci_high":float(hi),"acceptance_met":accept,
                 "eligible_any_exceed":sum(any(fresh[s]) for s in elig),
                 "rejected_any_exceed":sum(any(fresh[s]) for s in rej)})
with (HERE/"summary.csv").open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
me=[floors["mask_response_1mIoU"][s]<0.01 for s in ids]
ee=[floors["enstrophy_relative_response"][s]<1e-4 for s in ids]
cross={"agreement":float(np.mean(np.asarray(me)==np.asarray(ee))),
       "kappa":kappa(me,ee),
       "floor_spearman":float(np.corrcoef(ranks([floors["mask_response_1mIoU"][s] for s in ids]),
                                         ranks([floors["enstrophy_relative_response"][s] for s in ids]))[0,1])}
out={"n_samples":len(ids),"vortex_confirmed":bool(rows[0]["acceptance_met"]),
     "enstrophy_confirmed":bool(rows[1]["acceptance_met"]),"cross_qoi":cross,"endpoints":rows}
(HERE/"provenance.json").write_text(json.dumps(out,indent=2,allow_nan=True)+"\n")
lines=["# Independent JHTDB confirmation",""]
for r in rows:
    lines += [f"## {r['metric']}",f"- eligible/rejected: **{r['n_eligible']}/{r['n_rejected']}**",
              f"- fresh risks: **{100*r['fresh_risk_eligible']:.3f}% vs {100*r['fresh_risk_rejected']:.3f}%**",
              f"- rejected/eligible RR: **{r['risk_ratio']:.3g}**",
              f"- risk-difference 95% cluster-bootstrap CI: **[{r['ci_low']:.4f}, {r['ci_high']:.4f}]**",
              f"- acceptance: **{'MET' if r['acceptance_met'] else 'NOT MET'}**",""]
lines += ["## Cross-QoI",f"- agreement: **{cross['agreement']:.3f}**",f"- kappa: **{cross['kappa']:.3f}**",f"- floor Spearman rho: **{cross['floor_spearman']:.3f}**"]
(HERE/"RESULTS.md").write_text("\n".join(lines)+"\n")
print(json.dumps(out,indent=2,allow_nan=True))
