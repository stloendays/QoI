from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_output"
OUT.mkdir(exist_ok=True)
RNG_SEED = 20260906


def bootstrap_material_median(matches: pd.DataFrame, n_boot: int = 5000):
    mat = matches.groupby("material_id")["qoi_ratio"].median().dropna()
    vals = mat.to_numpy(float)
    if len(vals) == 0:
        return np.nan, np.nan, np.nan, np.nan
    rng = np.random.default_rng(RNG_SEED)
    boots = np.median(rng.choice(vals, size=(n_boot, len(vals)), replace=True), axis=1)
    return float(np.median(vals)), float(np.quantile(boots, .025)), float(np.quantile(boots, .975)), float((vals > 1).mean())


def mutual_nearest(g: pd.DataFrame, codec_a: str, codec_b: str, max_dex: float):
    rows = []
    for mid, mg in g.groupby("material_id", sort=False):
        a = mg[(mg.codec == codec_a) & (mg.realized_Linf > 0)].copy().reset_index(drop=True)
        b = mg[(mg.codec == codec_b) & (mg.realized_Linf > 0)].copy().reset_index(drop=True)
        if a.empty or b.empty:
            continue
        la = np.log10(a.realized_Linf.to_numpy(float))
        lb = np.log10(b.realized_Linf.to_numpy(float))
        d = np.abs(la[:, None] - lb[None, :])
        nearest_b = d.argmin(axis=1)
        nearest_a = d.argmin(axis=0)
        for ia, ib in enumerate(nearest_b):
            if nearest_a[ib] != ia or d[ia, ib] > max_dex:
                continue
            ra, rb = a.iloc[ia], b.iloc[ib]
            qa = max(float(ra.Bader_error_resolved_e), 1e-15)
            qb = max(float(rb.Bader_error_resolved_e), 1e-15)
            rows.append({
                "material_id": mid,
                "system_type": ra.system_type,
                "codec_a": codec_a,
                "codec_b": codec_b,
                "linf_a": float(ra.realized_Linf),
                "linf_b": float(rb.realized_Linf),
                "linf_ratio": float(ra.realized_Linf / rb.realized_Linf),
                "abs_log10_linf_diff": float(d[ia, ib]),
                "qoi_a": qa,
                "qoi_b": qb,
                "qoi_ratio": qa / qb,
                "ladder_a": ra.ladder,
                "ladder_b": rb.ladder,
                "nominal_rel_a": float(ra.nominal_tolerance_relative),
                "nominal_rel_b": float(rb.nominal_tolerance_relative),
            })
    return pd.DataFrame(rows)


def fixed_effect(df: pd.DataFrame):
    import statsmodels.formula.api as smf
    if df.material_id.nunique() < 10:
        return []
    ranges = df.groupby("codec").realized_Linf.agg(["min", "max"])
    lo, hi = float(ranges["min"].max()), float(ranges["max"].min())
    d = df[(df.realized_Linf >= lo) & (df.realized_Linf <= hi)].copy()
    d["logL"] = np.log10(d.realized_Linf.astype(float))
    center = float(d.logL.median())
    d["logL_c"] = d.logL - center
    d["logQ"] = np.log10(np.clip(d.Bader_error_resolved_e.astype(float), 1e-15, None))
    model = smf.ols("logQ ~ logL_c * C(codec, Treatment(reference='ZFP')) + C(material_id)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d.material_id}
    )
    out=[]
    for codec in ["SZ3", "SPERR"]:
        term=f"C(codec, Treatment(reference='ZFP'))[T.{codec}]"
        if term not in model.params:
            continue
        beta=float(model.params[term]); se=float(model.bse[term]); p=float(model.pvalues[term])
        out.append({"codec":codec,"n_rows":len(d),"n_materials":d.material_id.nunique(),"support_lo":lo,"support_hi":hi,"center_log10_linf":center,"beta_log10":beta,"effect_x":10**beta,"ci_lo_x":10**(beta-1.96*se),"ci_hi_x":10**(beta+1.96*se),"p":p})
    return out


master=pd.read_csv(ROOT/"benchmark/master_benchmark_full.csv")
master["codec"]=master.codec.str.upper()

summary=[]
reg_rows=[]
for tau, eligibility_col in [(1e-4,"eligible_A1_at_0.0001"),(1e-3,"eligible_A1_at_0.001"),(1e-2,"eligible_A1_at_0.01")]:
    admitted=master[master[eligibility_col].astype(bool)].copy()
    for a,b in [("SZ3","ZFP"),("SPERR","ZFP")]:
        for dex in [0.10,0.15,0.20]:
            m=mutual_nearest(admitted,a,b,dex)
            est,lo,hi,frac=bootstrap_material_median(m)
            summary.append({"eligibility_tau_e":tau,"codec_a":a,"codec_b":b,"max_match_dex":dex,"n_pairs":len(m),"n_materials":m.material_id.nunique() if len(m) else 0,"median_linf_ratio":m.groupby('material_id').linf_ratio.median().median() if len(m) else np.nan,"median_qoi_ratio":est,"ci_lo":lo,"ci_hi":hi,"fraction_materials_a_worse":frac})
            if dex == 0.10:
                m.to_csv(OUT/f"matched_realized_linf_A1_{tau:g}_{a.lower()}_vs_{b.lower()}_010dex.csv",index=False)
    reg_rows.extend([{**r,"eligibility_tau_e":tau} for r in fixed_effect(admitted)])

pd.DataFrame(summary).to_csv(OUT/"matched_realized_linf_A1_sensitivity.csv",index=False)
pd.DataFrame(reg_rows).to_csv(OUT/"realized_linf_fixed_effect_A1_sensitivity.csv",index=False)

lines=["# Stability-qualified realized-Linf sensitivity","", "All analyses below first restrict materials to Protocol A.1 eligibility at the stated Bader-charge contract, then compare codecs over the full available base+tight ladders.",""]
for z in summary:
    if z["max_match_dex"] != 0.10:
        continue
    lines.append(f"- A.1 eligible at tau={z['eligibility_tau_e']:g} e; {z['codec_a']}/{z['codec_b']}; <=0.10 dex: {z['n_pairs']} pairs, {z['n_materials']} materials; median realized-Linf ratio {z['median_linf_ratio']:.3f}; median resolved-Bader error ratio **{z['median_qoi_ratio']:.2f}x** [95% bootstrap CI {z['ci_lo']:.2f}, {z['ci_hi']:.2f}]; A worse in {100*z['fraction_materials_a_worse']:.1f}% of materials.")
lines += ["", "## Material-fixed-effect regression at matched realized-Linf scale", ""]
for r in reg_rows:
    lines.append(f"- A.1 eligible at tau={r['eligibility_tau_e']:g} e; {r['codec']} vs ZFP: **{r['effect_x']:.2f}x** [95% CI {r['ci_lo_x']:.2f}, {r['ci_hi_x']:.2f}], p={r['p']:.3g}, n={r['n_rows']} rows / {r['n_materials']} materials.")
(OUT/"stability_qualified_structure_effect.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("\n".join(lines))
