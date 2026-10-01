#!/usr/bin/env python3
"""Aggregate the frozen JHTDB turbulence QSQ experiment."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
THRESHOLDS={
    "mask_response_1mIoU": (0.01,0.05,0.10),
    "enstrophy_relative_response": (0.001,0.01,0.05),
}
PRIMARY={"mask_response_1mIoU":0.05,"enstrophy_relative_response":0.01}
NBOOT=5000
RNG=np.random.default_rng(20261001)

def read(path):
    return list(csv.DictReader(path.open()))

def mean_ci_by_cluster(qrows, frows, metric, tau, eligible_ids, rejected_ids):
    fresh={}
    for r in frows:
        fresh.setdefault(r["sample_id"],[]).append(float(r[metric])>=tau)
    ids=sorted(fresh)
    def risk(group):
        vals=[x for sid in group for x in fresh[sid]]
        return float(np.mean(vals)) if vals else math.nan
    re=risk(eligible_ids); rr=risk(rejected_ids)
    diff=rr-re
    boots=[]
    for _ in range(NBOOT):
        draw=RNG.choice(ids,size=len(ids),replace=True)
        eg=[sid for sid in draw if sid in eligible_ids]
        rg=[sid for sid in draw if sid in rejected_ids]
        if not eg or not rg: continue
        boots.append(risk(rg)-risk(eg))
    lo,hi=(np.quantile(boots,[0.025,0.975]) if boots else (math.nan,math.nan))
    return re,rr,diff,float(lo),float(hi)

def kappa(a,b):
    a=np.asarray(a,bool); b=np.asarray(b,bool)
    po=float(np.mean(a==b))
    pa=float(np.mean(a)); pb=float(np.mean(b))
    pe=pa*pb+(1-pa)*(1-pb)
    return (po-pe)/(1-pe) if pe<1 else math.nan

def rankdata(x):
    x=np.asarray(x,float)
    order=np.argsort(x,kind="mergesort"); ranks=np.empty(len(x),float)
    i=0
    while i<len(x):
        j=i+1
        while j<len(x) and x[order[j]]==x[order[i]]: j+=1
        ranks[order[i:j]]=(i+j-1)/2+1
        i=j
    return ranks

def spearman(x,y):
    rx,ry=rankdata(x),rankdata(y)
    return float(np.corrcoef(rx,ry)[0,1])

def main():
    q=read(HERE/"qualification_probes.csv")
    f=read(HERE/"fresh_probes.csv")
    refs=read(HERE/"reference_metrics.csv")
    sample_ids=sorted({r["sample_id"] for r in q})
    floors={}
    rows=[]
    for metric,taus in THRESHOLDS.items():
        floors[metric]={}
        for sid in sample_ids:
            vals=[float(r[metric]) for r in q if r["sample_id"]==sid]
            floors[metric][sid]=max(vals)
        for tau in taus:
            eligible={sid for sid in sample_ids if floors[metric][sid] < tau}
            rejected=set(sample_ids)-eligible
            fresh_by_group={"eligible":[],"rejected":[]}
            cut_any={"eligible":0,"rejected":0}
            for group,ids in (("eligible",eligible),("rejected",rejected)):
                for sid in ids:
                    xs=[float(r[metric])>=tau for r in f if r["sample_id"]==sid]
                    fresh_by_group[group].extend(xs)
                    cut_any[group]+=int(any(xs))
            re=float(np.mean(fresh_by_group["eligible"])) if fresh_by_group["eligible"] else math.nan
            rr=float(np.mean(fresh_by_group["rejected"])) if fresh_by_group["rejected"] else math.nan
            ratio=(rr/re if re>0 else (math.inf if rr>0 else math.nan))
            _,_,diff,lo,hi=mean_ci_by_cluster(q,f,metric,tau,eligible,rejected)
            rows.append({
                "metric":metric,"tau":tau,"n_samples":len(sample_ids),
                "n_eligible":len(eligible),"n_rejected":len(rejected),
                "fresh_trials_eligible":len(fresh_by_group["eligible"]),
                "fresh_exceed_eligible":int(sum(fresh_by_group["eligible"])),
                "fresh_risk_eligible":re,
                "fresh_trials_rejected":len(fresh_by_group["rejected"]),
                "fresh_exceed_rejected":int(sum(fresh_by_group["rejected"])),
                "fresh_risk_rejected":rr,
                "risk_ratio_rejected_over_eligible":ratio,
                "risk_difference":diff,"risk_difference_ci_low":lo,"risk_difference_ci_high":hi,
                "cutouts_any_exceed_eligible":cut_any["eligible"],
                "cutouts_any_exceed_rejected":cut_any["rejected"],
            })
    with (HERE/"summary.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    mask_e=[floors["mask_response_1mIoU"][s] < PRIMARY["mask_response_1mIoU"] for s in sample_ids]
    ens_e=[floors["enstrophy_relative_response"][s] < PRIMARY["enstrophy_relative_response"] for s in sample_ids]
    floor_mask=[floors["mask_response_1mIoU"][s] for s in sample_ids]
    floor_ens=[floors["enstrophy_relative_response"][s] for s in sample_ids]
    cross={
        "agreement":float(np.mean(np.asarray(mask_e)==np.asarray(ens_e))),
        "kappa":kappa(mask_e,ens_e),
        "floor_spearman":spearman(floor_mask,floor_ens),
    }
    amp=np.array([float(r["gradient_amplification"]) for r in q],float)
    mechanism={
        "gradient_amplification_median":float(np.median(amp)),
        "gradient_amplification_p10":float(np.quantile(amp,0.10)),
        "gradient_amplification_p90":float(np.quantile(amp,0.90)),
    }
    primary=next(r for r in rows if r["metric"]=="mask_response_1mIoU" and abs(float(r["tau"])-0.05)<1e-12)
    accept=(
        int(primary["n_eligible"])>=10 and int(primary["n_rejected"])>=10 and
        float(primary["risk_ratio_rejected_over_eligible"])>=5 and
        float(primary["risk_difference_ci_low"])>0
    )
    result={
        "n_reference":len(refs),"n_samples":len(sample_ids),
        "primary_acceptance_met":bool(accept),
        "cross_qoi":cross,"mechanism":mechanism,
        "primary_mask":primary,
    }
    (HERE/"provenance.json").write_text(json.dumps(result,indent=2,allow_nan=True)+"\n",encoding="utf-8")
    lines=[
        "# WP-J — JHTDB turbulence QSQ generality",
        "",
        f"Completed cutouts: **{len(sample_ids)}/64**.",
        "",
        "## Primary vortex-mask endpoint",
        "",
        f"- Eligible: **{primary['n_eligible']}/64** at $\\tau_M=0.05$.",
        f"- Fresh exceedance risk: eligible **{100*float(primary['fresh_risk_eligible']):.3f}%**, rejected **{100*float(primary['fresh_risk_rejected']):.3f}%**.",
        f"- Rejected/eligible risk ratio: **{float(primary['risk_ratio_rejected_over_eligible']):.3g}**.",
        f"- Risk-difference cluster-bootstrap 95% interval: **[{float(primary['risk_difference_ci_low']):.4f}, {float(primary['risk_difference_ci_high']):.4f}]**.",
        f"- Pre-declared cross-domain acceptance criterion: **{'MET' if accept else 'NOT MET'}**.",
        "",
        "## Cross-QoI comparison",
        "",
        f"- Primary-threshold eligibility agreement: **{cross['agreement']:.3f}**.",
        f"- Cohen's kappa: **{cross['kappa']:.3f}**.",
        f"- Floor Spearman rho: **{cross['floor_spearman']:.3f}**.",
        "",
        "## Differential-operator audit",
        "",
        f"- Median gradient/noise L2 amplification: **{mechanism['gradient_amplification_median']:.3g}** (P10 {mechanism['gradient_amplification_p10']:.3g}, P90 {mechanism['gradient_amplification_p90']:.3g}).",
    ]
    (HERE/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,allow_nan=True))

if __name__=="__main__":
    main()
