#!/usr/bin/env python3
"""Audit reconstruction parity and the single compatibility exception."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/"analysis"/"hartree_qsq_full"/"results"
OUT=ROOT/"analysis"/"hartree_qsq_full"/"audit"
OUT.mkdir(parents=True,exist_ok=True)

rows=pd.read_csv(RES/"hartree_codec_rows.csv")
for col in ["realized_Linf_match","bound_respected","compressed_bytes_exact","scientific_reproduction_gate_pass"]:
    rows[col]=rows[col].astype(str).str.lower().isin(["true","1","t","yes"])

exc=rows[~rows["scientific_reproduction_gate_pass"]].copy()
exc.to_csv(OUT/"REPRODUCTION_EXCEPTIONS.csv",index=False)

summary=[]
for keys,g in rows.groupby(["codec"],dropna=False):
    summary.append({
        "codec":keys,
        "n_rows":len(g),
        "linf_match_fraction":float(g.realized_Linf_match.mean()),
        "bound_respected_fraction":float(g.bound_respected.mean()),
        "scientific_gate_pass_fraction":float(g.scientific_reproduction_gate_pass.mean()),
        "compressed_bytes_exact_fraction":float(g.compressed_bytes_exact.mean()),
        "n_compressed_bytes_exact":int(g.compressed_bytes_exact.sum()),
    })
pd.DataFrame(summary).to_csv(OUT/"RECONSTRUCTION_PARITY_BY_CODEC.csv",index=False)

domain=[]
for (codec,system),g in rows.groupby(["codec","system_type"],dropna=False):
    domain.append({
        "codec":codec,"system_type":system,"n_rows":len(g),
        "scientific_gate_pass_fraction":float(g.scientific_reproduction_gate_pass.mean()),
        "compressed_bytes_exact_fraction":float(g.compressed_bytes_exact.mean()),
    })
pd.DataFrame(domain).to_csv(OUT/"RECONSTRUCTION_PARITY_BY_CODEC_DOMAIN.csv",index=False)

# Recreate 0.10-dex matching only to quantify how many direct Bader/Hartree comparisons
# are exact-byte on both sides. This does not change the matched scientific estimates.
import math
from collections import defaultdict
PAIRS=(("ZFP","SZ3"),("ZFP","SPERR"),("SZ3","SPERR"))
CAL=0.10

valid=rows[rows.scientific_reproduction_gate_pass & (rows.reproduced_realized_Linf>0)].copy()
valid["_row_id"]=range(len(valid))

def dedupe(g):
    z=g.copy()
    z["_k"]=z.nominal_tolerance_absolute.astype(float).map(lambda x:round(math.log10(x),13))
    return z.sort_values(["reproduced_realized_Linf","_row_id"]).drop_duplicates("_k")

def match(a,b):
    cand=[]
    a=a.reset_index(drop=True); b=b.reset_index(drop=True)
    for ia,ra in a.iterrows():
        la=math.log10(float(ra.reproduced_realized_Linf))
        for ib,rb in b.iterrows():
            d=abs(la-math.log10(float(rb.reproduced_realized_Linf)))
            if d<=CAL+1e-15: cand.append((d,int(ra._row_id),int(rb._row_id),ia,ib))
    cand.sort(); ua=set(); ub=set(); out=[]
    for d,_,__,ia,ib in cand:
        if ia in ua or ib in ub: continue
        ua.add(ia); ub.add(ib); out.append((a.iloc[ia],b.iloc[ib],d))
    return out

pair_rows=[]
for ca,cb in PAIRS:
    n=exact=0; mats=set(); exact_mats=set()
    for mid,gm in valid.groupby("material_id"):
        ga=dedupe(gm[gm.codec==ca]); gb=dedupe(gm[gm.codec==cb])
        if len(ga)==0 or len(gb)==0: continue
        for ra,rb,d in match(ga,gb):
            n+=1; mats.add(mid)
            both=bool(ra.compressed_bytes_exact and rb.compressed_bytes_exact)
            if both: exact+=1; exact_mats.add(mid)
    pair_rows.append({
        "codec_a":ca,"codec_b":cb,"matched_pairs":n,"matched_materials":len(mats),
        "both_compressed_bytes_exact_pairs":exact,
        "both_compressed_bytes_exact_fraction":exact/n if n else float("nan"),
        "materials_with_at_least_one_exact_pair":len(exact_mats),
    })
pd.DataFrame(pair_rows).to_csv(OUT/"MATCHED_PAIR_PARITY.csv",index=False)

payload={
    "n_rows":int(len(rows)),
    "n_scientific_gate_fail":int((~rows.scientific_reproduction_gate_pass).sum()),
    "n_compressed_bytes_exact":int(rows.compressed_bytes_exact.sum()),
    "compressed_bytes_exact_fraction":float(rows.compressed_bytes_exact.mean()),
    "by_codec":summary,
    "matched_pair_parity":pair_rows,
    "direct_cross_operator_pairwise_interpretation_safe_only_when_both_reconstructions_exact":True,
}
(OUT/"SUMMARY.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

lines=["# Hartree-QSQ reconstruction parity audit","",
       f"Rows: **{len(rows)}**; scientific gate failures: **{payload['n_scientific_gate_fail']}**; compressed-byte exact rows: **{payload['n_compressed_bytes_exact']}/{len(rows)} ({payload['compressed_bytes_exact_fraction']:.1%})**.","",
       "## By codec","",
       "| Codec | rows | L∞ match | gate pass | compressed bytes exact |","|---|---:|---:|---:|---:|"]
for r in summary:
    lines.append(f"| {r['codec']} | {r['n_rows']} | {r['linf_match_fraction']:.2%} | {r['scientific_gate_pass_fraction']:.2%} | {r['compressed_bytes_exact_fraction']:.2%} |")
lines += ["","## Matched-pair parity","",
          "| Pair | pairs | both exact | exact fraction | materials with >=1 exact pair |","|---|---:|---:|---:|---:|"]
for r in pair_rows:
    lines.append(f"| {r['codec_a']}/{r['codec_b']} | {r['matched_pairs']} | {r['both_compressed_bytes_exact_pairs']} | {r['both_compressed_bytes_exact_fraction']:.2%} | {r['materials_with_at_least_one_exact_pair']} |")
lines += ["","Direct same-reconstruction Hartree/Bader pairwise interpretation is restricted to matched pairs for which both regenerated codec outputs are byte-count exact diagnostics; if exactness is insufficient, the follow-up mechanism audit must recompute Bader on the regenerated fields."]
(OUT/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"status":"PASS","gate_fail":payload["n_scientific_gate_fail"],"byte_exact_fraction":payload["compressed_bytes_exact_fraction"]}))
