from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROWS = HERE / 'rows.csv'
OUT_SUM = HERE / 'group_summary.csv'
OUT_MAT = HERE / 'material_smoothness.csv'
OUT_BIN = HERE / 'matched_error_dispersion.csv'
OUT_GATE = HERE / 'gate_failures.csv'
OUT_RES = HERE / 'RESULTS.md'

REQ = ['material_id','system_type','codec','realized_Linf','potential_rel_RMSE',
       'Bader_error_resolved_e','reproduction_gate_pass']


def logfit(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    m=np.isfinite(x)&np.isfinite(y)&(x>0)&(y>0)
    if m.sum()<3:return (np.nan,np.nan,np.nan,np.nan)
    lx=np.log10(x[m]); ly=np.log10(y[m])
    p=np.polyfit(lx,ly,1); yh=np.polyval(p,lx)
    ss=((ly-ly.mean())**2).sum(); r2=1-((ly-yh)**2).sum()/ss if ss>0 else np.nan
    pe=float(pd.Series(lx).corr(pd.Series(ly),method='pearson'))
    sp=float(pd.Series(lx).corr(pd.Series(ly),method='spearman'))
    return float(p[0]),float(r2),pe,sp


def summarize_group(g):
    sv,r2v,pv,spv=logfit(g.realized_Linf,g.potential_rel_RMSE)
    sb,r2b,pb,spb=logfit(g.realized_Linf,g.Bader_error_resolved_e)
    return pd.Series(dict(n_rows=len(g),n_materials=g.material_id.nunique(),
        hartree_slope=sv,hartree_R2=r2v,hartree_pearson=pv,hartree_spearman=spv,
        bader_slope=sb,bader_R2=r2b,bader_pearson=pb,bader_spearman=spb,
        median_potential_rel_RMSE=float(g.potential_rel_RMSE.median()),
        median_Bader_error_e=float(g.Bader_error_resolved_e.median())))


def main():
    df=pd.read_csv(ROWS,low_memory=False)
    miss=[c for c in REQ if c not in df.columns]
    if miss: raise SystemExit(f'missing required columns: {miss}')
    gate=df['reproduction_gate_pass'].astype(bool)
    df.loc[~gate].to_csv(OUT_GATE,index=False)
    v=df[gate & np.isfinite(df.realized_Linf) & np.isfinite(df.potential_rel_RMSE) & np.isfinite(df.Bader_error_resolved_e)].copy()

    groups=[]
    for keys,g in v.groupby(['codec','system_type'],dropna=False):
        s=summarize_group(g); s['codec'],s['system_type']=keys; groups.append(s)
    for codec,g in v.groupby('codec'):
        s=summarize_group(g); s['codec']=codec; s['system_type']='ALL'; groups.append(s)
    gs=pd.DataFrame(groups)
    cols=['codec','system_type']+[c for c in gs.columns if c not in ['codec','system_type']]
    gs=gs[cols]; gs.to_csv(OUT_SUM,index=False)

    mats=[]
    for (mid,codec,stype),g in v.groupby(['material_id','codec','system_type']):
        g=g.sort_values('realized_Linf')
        if len(g)<5: continue
        x=g.realized_Linf.to_numpy(float); vh=g.potential_rel_RMSE.to_numpy(float); b=g.Bader_error_resolved_e.to_numpy(float)
        sv,r2v,_,_=logfit(x,vh); sb,r2b,_,_=logfit(x,b)
        dv=np.diff(vh); db=np.diff(b); dx=np.diff(np.log10(x))
        with np.errstate(divide='ignore',invalid='ignore'):
            ev=np.diff(np.log10(np.maximum(vh,1e-300)))/dx
            eb=np.diff(np.log10(np.maximum(b,1e-12)))/dx
        mats.append(dict(material_id=mid,codec=codec,system_type=stype,n_rows=len(g),
            hartree_monotone=bool(np.all(dv>=0)),hartree_n_decreases=int((dv<0).sum()),
            hartree_slope=sv,hartree_R2=r2v,
            hartree_local_elasticity_min=float(np.nanmin(ev)),hartree_local_elasticity_max=float(np.nanmax(ev)),
            bader_monotone=bool(np.all(db>=0)),bader_n_decreases=int((db<0).sum()),
            bader_slope=sb,bader_R2=r2b,
            bader_local_elasticity_min=float(np.nanmin(eb)),bader_local_elasticity_max=float(np.nanmax(eb)),
            bader_max_consecutive_jump=float(np.nanmax(b[1:]/np.maximum(b[:-1],1e-12)))))
    md=pd.DataFrame(mats); md.to_csv(OUT_MAT,index=False)

    bins=[]
    vv=v[(v.potential_rel_RMSE>0)&(v.Bader_error_resolved_e>0)].copy()
    vv['hartree_bin']=np.floor(np.log10(vv.potential_rel_RMSE)*2)/2
    for (codec,stype,hb),g in vv.groupby(['codec','system_type','hartree_bin']):
        if len(g)<10: continue
        q10=float(g.Bader_error_resolved_e.quantile(.1)); q90=float(g.Bader_error_resolved_e.quantile(.9))
        mn=float(g.Bader_error_resolved_e.min()); mx=float(g.Bader_error_resolved_e.max())
        bins.append(dict(codec=codec,system_type=stype,hartree_log10_bin_left=hb,n=len(g),
            bader_p10=q10,bader_p90=q90,bader_p90_over_p10=q90/max(q10,1e-12),
            bader_min=mn,bader_max=mx,bader_max_over_min=mx/max(mn,1e-12)))
    bd=pd.DataFrame(bins); bd.to_csv(OUT_BIN,index=False)

    gate_rates=df.groupby('codec').reproduction_gate_pass.mean().to_dict()
    criteria={}
    criteria['gate_each_codec_ge_095']=all(float(gate_rates.get(c,0))>=.95 for c in ['ZFP','SZ3','SPERR'])
    medr2=md.groupby('codec').hartree_R2.median().to_dict() if len(md) else {}
    criteria['median_hartree_R2_each_codec_ge_095']=all(float(medr2.get(c,0))>=.95 for c in ['ZFP','SZ3','SPERR'])
    fr=md.groupby('codec').agg(H=('hartree_monotone','mean'),B=('bader_monotone','mean')) if len(md) else pd.DataFrame()
    criteria['monotonicity_gap_each_codec_ge_030']=all((c in fr.index and float(fr.loc[c,'H']-fr.loc[c,'B'])>=.30) for c in ['ZFP','SZ3','SPERR'])
    rb=[]
    for c in ['ZFP','SZ3','SPERR']:
        for s in ['bulk','slab']:
            q=gs[(gs.codec==c)&(gs.system_type==s)]
            rb.append(len(q)==1 and float(q.iloc[0].hartree_R2)>float(q.iloc[0].bader_R2))
    criteria['hartree_R2_gt_bader_R2_bulk_slab_all_codecs']=all(rb)
    strongbins=bd[bd.bader_p90_over_p10>=10] if len(bd) else bd
    criteria['matched_hartree_bins_ge_1decade_in_two_codecs']=strongbins.codec.nunique()>=2 if len(strongbins) else False
    recommendation='PROMOTE_TO_MAIN_TEXT' if all(criteria.values()) else 'KEEP_IN_SI'

    lines=['# Hartree-potential QoI full expansion results','',f'- gate-passing rows: **{len(v)} / {len(df)}**',
           f'- materials represented: **{v.material_id.nunique()}**','', '## Pre-declared promotion criteria']
    for k,val in criteria.items(): lines.append(f'- {k}: **{"PASS" if val else "FAIL"}**')
    lines += ['', '## Recommendation', '', recommendation, '']
    OUT_RES.write_text('\n'.join(lines),encoding='utf-8')
    print('\n'.join(lines))

if __name__=='__main__': main()
