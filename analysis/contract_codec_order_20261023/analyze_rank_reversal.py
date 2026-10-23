#!/usr/bin/env python3
"""Outcome-blind matching audit: fixed-partition vs rederived Bader ranks.

Uses frozen development benchmark only; no confirmatory population.
Every selected pair is checked against the SHA-verified original file, and
its minimum scalar-distortion matching score is recomputed independently.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SOURCE_SHA = 'd94839fd8b72e81ee2b06e80edb0e0e8c2967c51239a2d41fc166dbfd5b0b97a'
PAIRS_SHA = 'fb6e77dc1ca1525918397415c1f3ef7dd17206b5f945ac6df8f9a2dc5f80a480'


def sha256(path: Path) -> str:
    """SHA-256 of a text input with CR removed, so a CRLF checkout verifies the committed LF bytes."""
    return hashlib.sha256(path.read_bytes().replace(b'\r', b'')).hexdigest()


def match_one(g:pd.DataFrame,caliper:float):
    aa=g[g.codec.eq('SZ3')]
    bb=g[g.codec.eq('SPERR')]
    if aa.empty or bb.empty:return None
    a=aa[['realized_Linf','rmse']].to_numpy(dtype=float)
    b=bb[['realized_Linf','rmse']].to_numpy(dtype=float)
    with np.errstate(divide='ignore',invalid='ignore'):
        d=np.abs(np.log10(a[:,None,:]/b[None,:,:]))
    eligible=np.isfinite(d).all(axis=2)&(d<=caliper).all(axis=2)
    if not np.any(eligible):return None
    cost=np.where(eligible,d.sum(axis=2),np.inf)
    i,j=np.unravel_index(cost.argmin(),cost.shape)
    return aa.iloc[i],bb.iloc[j],d[i,j],cost[i,j]


def check_and_recompute(master:pd.DataFrame,pairs:pd.DataFrame,caliper:float):
    assert len(master)==6343 and master.material_id.nunique()==254
    assert pairs.material_id.nunique()==len(pairs)
    assert all(master.loc[int(k),'codec']==codec for k,codec in
               [(rid,'SZ3') for rid in pairs.row_id_SZ3]+[(rid,'SPERR') for rid in pairs.row_id_SPERR])
    count=0
    for mid,g in master.groupby('material_id',sort=True):
        x=match_one(g,caliper)
        sel=pairs.loc[pairs.material_id.eq(mid)]
        if x is None:
            assert sel.empty, f'Unexpected pair: {mid}'
            continue
        assert len(sel)==1,f'Expected exactly one matching pair: {mid}'
        a,b,d,score=x
        r=sel.iloc[0]
        assert int(a.name)==int(r.row_id_SZ3) and int(b.name)==int(r.row_id_SPERR),mid
        assert max(d)<=caliper+1e-12
        for source,target in [
            ('Bader_error_resolved_e','Bader_resolved_error'),
            ('Bader_error_fixed_e','Bader_fixed_error'),
            ('frac_voxels_reassigned','reassigned_fraction')]:
            for codec,row in [('SZ3',a),('SPERR',b)]:
                dst=r[f'{target}_{codec}'+('_e' if 'Bader' in target else '')]
                assert np.isclose(float(row[source]),float(dst),rtol=1e-11,atol=1e-15),(mid,source)
        assert np.isclose(float(r.log10_Linf_mismatch_abs),d[0],rtol=1e-10,atol=1e-14)
        assert np.isclose(float(r.log10_RMSE_mismatch_abs),d[1],rtol=1e-10,atol=1e-14)
        count+=1
    assert count==len(pairs), (count,len(pairs))
    return count


def wilson(k,n,z=1.95996398454):
    if n==0:return [None,None]
    p=k/n;z2=z*z
    c=(p+z2/(2*n))/(1+z2/n)
    r=z*math.sqrt((p*(1-p)+z2/(4*n))/n)/(1+z2/n)
    return [c-r,c+r]


def bootstrap_median(values,nboot=10000,seed=20261022):
    v=np.asarray(values,dtype=float)
    r=np.random.default_rng(seed)
    res=np.median(v[r.integers(0,len(v),size=(nboot,len(v)))],axis=1)
    return [float(np.quantile(res,.025)),float(np.quantile(res,.975))]


def compute(p):
    fs=p.Bader_fixed_error_SZ3_e.to_numpy(float)
    fp=p.Bader_fixed_error_SPERR_e.to_numpy(float)
    rs=p.Bader_resolved_error_SZ3_e.to_numpy(float)
    rp=p.Bader_resolved_error_SPERR_e.to_numpy(float)
    assert np.all(np.stack([fs,fp,rs,rp])>0)
    fixed=fs/fp; recomputed=rs/rp
    flips=((fixed>1)&(recomputed<1))|((fixed<1)&(recomputed>1))
    assert not np.any(fixed==1) and not np.any(recomputed==1)
    groups={}
    for name,s in [('all',p),('bulk',p[p.system_type.eq('bulk')]),('slab',p[p.system_type.eq('slab')])]:
        a=s.Bader_fixed_error_SZ3_e.to_numpy(float)/s.Bader_fixed_error_SPERR_e.to_numpy(float)
        b=s.Bader_resolved_error_SZ3_e.to_numpy(float)/s.Bader_resolved_error_SPERR_e.to_numpy(float)
        flip=(a>1)&(b<1)
        groups[name]={
            'n':len(s),
            'fixed_SPERR_better':int((a>1).sum()),
            'rederived_SPERR_better':int((b>1).sum()),
            'ranking_reversals':int(flip.sum()),
            'ranking_reversal_fraction':float(np.mean(flip)),
            'ranking_reversal_Wilson95CI':wilson(int(flip.sum()),len(s)),
            'median_fixed_SZ3_over_SPERR':float(np.median(a)),
            'median_fixed_ratio_bootstrap95CI':bootstrap_median(a),
            'median_rederived_SZ3_over_SPERR':float(np.median(b)),
            'median_rederived_ratio_bootstrap95CI':bootstrap_median(b),
            'geomean_fixed_SZ3_over_SPERR':float(np.exp(np.mean(np.log(a)))),
            'geomean_rederived_SZ3_over_SPERR':float(np.exp(np.mean(np.log(b))))
        }
    outcomes=[]
    for tol,col in [(1e-3,'QSQ_eligible_1e-3'),(1e-2,'QSQ_eligible_1e-2')]:
        elig=p[col].astype(bool).to_numpy()
        fixed_disc=((fs<tol)!=(fp<tol))&elig
        real_disc=((rs<tol)!=(rp<tol))&elig
        if elig.sum():
            assert not np.any(fixed_disc&real_disc), 'If both disagree, report intersection explicitly'
        outcomes.append({
            'tau_B_e':tol,'n_QSQ_eligible':int(elig.sum()),
            'fixed_basin_disagreement_n':int(fixed_disc.sum()),
            'fixed_basin_disagreement_rate':float(fixed_disc.sum()/elig.sum()),
            'fixed_basin_Wilson95CI':wilson(int(fixed_disc.sum()),int(elig.sum())),
            'rederived_basin_disagreement_n':int(real_disc.sum()),
            'rederived_basin_disagreement_rate':float(real_disc.sum()/elig.sum()),
            'rederived_basin_Wilson95CI':wilson(int(real_disc.sum()),int(elig.sum())),
            'note':'Fixed-basin classification is a DIAGNOSTIC, not the declared rederived Bader measurement contract.'
        })
    return groups,outcomes,flips


def sensitivity(master,calipers=(.05,.075,.10,.15,.20)):
    data=[]
    for caliper in calipers:
        rows=[]
        for mid,g in master.groupby('material_id',sort=True):
            z=match_one(g,caliper)
            if z is None:continue
            a,b,delta,_=z
            fixed=float(a.Bader_error_fixed_e/b.Bader_error_fixed_e)
            recalculated=float(a.Bader_error_resolved_e/b.Bader_error_resolved_e)
            rows.append((mid,delta.max(),fixed,recalculated))
        xx=np.array([z[3] for z in rows]); ff=np.array([z[2] for z in rows]); n=len(rows)
        data.append({'caliper_dex':caliper,'n_materials':n,
                     'n_fixed_SPERR_better':int((ff>1).sum()),
                     'n_rank_reversal':int((((ff>1)&(xx<1))|((ff<1)&(xx>1))).sum()),
                     'rank_reversal_fraction':float(np.mean(((ff>1)&(xx<1))|((ff<1)&(xx>1)))),
                     'median_fixed_ratio':float(np.median(ff)),
                     'median_rederived_ratio':float(np.median(xx))})
    return data


def plot(p,groups,outcomes,fig_dir):
    navy='#315782'; sage='#70887A'; amber='#B47B50'; slate='#5B6774'; pale='#D7DDE1'
    fixed=p.Bader_fixed_error_SZ3_e.to_numpy()/p.Bader_fixed_error_SPERR_e.to_numpy()
    recon=p.Bader_resolved_error_SZ3_e.to_numpy()/p.Bader_resolved_error_SPERR_e.to_numpy()
    lf=np.log10(fixed); lr=np.log10(recon)
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':9.5,'axes.spines.top':False,
                         'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'}):
        fig,ax=plt.subplots(1,3,figsize=(13.5,4.5),dpi=175,
                            gridspec_kw={'width_ratios':[1.12,1.05,1.1]})
        a,b,c=ax
        a.axhspan(min(-2.6,lr.min()-.2),0,color='#EEF0F1',zorder=0)
        a.axhline(0,lw=.9,ls='--',color=slate)
        for tp,color,zord in [('bulk',navy,2),('slab',sage,3)]:
            mask=p.system_type.eq(tp)
            a.scatter(lf[mask],lr[mask],s=19,c=color,alpha=.72,label=f'{tp.capitalize()}, n={int(mask.sum())}',
                      zorder=zord,rasterized=True)
        a.text(.98,.05,f'{groups["all"]["ranking_reversals"]}/{len(p)} rankings reversed',
               ha='right',va='bottom',transform=a.transAxes,color=slate,fontsize=8.9)
        a.set(xlabel=r'$\log_{10}(\mathrm{SZ3/SPERR})$, fixed basins',
              ylabel=r'$\log_{10}(\mathrm{SZ3/SPERR})$, re-derived basins',
              xlim=(max(0,float(lf.min())-.2),float(lf.max())+.25),
              ylim=(min(-2.0,float(lr.min())-.2),max(2.3,float(lr.max())+.2)))
        a.legend(frameon=False,fontsize=8,loc='upper right',handletextpad=.2)
        a.set_title('a   Matched density errors, reversed codec ranking',loc='left',fontweight='bold',fontsize=10.2)
        for vals,col,label in [(lf,navy,'Fixed partition'),(lr,amber,'Re-derived partition')]:
            xs=np.sort(vals)
            b.step(xs,np.arange(1,len(xs)+1)/len(xs),where='post',color=col,lw=2.1,label=label)
        b.axvline(0,color=slate,lw=.9,ls='--')
        b.text(.48,.09,'SZ3 better',transform=b.transAxes,ha='right',fontsize=8,color=slate)
        b.text(.53,.09,'SPERR better',transform=b.transAxes,ha='left',fontsize=8,color=slate)
        b.set(xlim=(-2.6,2.9),ylim=(0,1.02),xlabel=r'$\log_{10}$ ratio of Bader charge errors (SZ3/SPERR)',
              ylabel='Cumulative fraction of materials')
        b.set_title('b   The apparent advantage changes with partition',loc='left',fontweight='bold',fontsize=10.2)
        b.legend(frameon=False,fontsize=8.5,loc='upper left')
        ys=[3,2,1,0]
        plotted=[]
        for j,o in enumerate(outcomes):
            for k,typ in enumerate(['fixed','rederived']):
                key='fixed_basin' if typ=='fixed' else 'rederived_basin'
                rate=o[key+'_disagreement_rate']
                lo,hi=o[key+'_Wilson95CI']
                y=ys[2*j+k]
                col=navy if typ=='fixed' else amber
                c.hlines(y,lo,hi,lw=1.4,color=col)
                c.vlines([lo,hi],y-.10,y+.10,color=col,lw=1.2)
                c.scatter([rate],[y],s=55,color=col,zorder=3)
                c.text(min(.55,hi+.02),y,f'{o[key+"_disagreement_n"]}/{o["n_QSQ_eligible"]}',
                       va='center',ha='left',fontsize=8.4,color=col)
        c.set(yticks=ys,yticklabels=['Fixed, 1e-3 e','Re-derived, 1e-3 e','Fixed, 1e-2 e','Re-derived, 1e-2 e'],
              xlim=(0,.65),ylim=(-.4,3.4),xlabel='Disagreeing certification decisions / eligible materials')
        c.set_title('c   Diagnostic vs actual Bader certification',loc='left',fontweight='bold',fontsize=10.2)
        c.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,pos:f'{100*x:.0f}%'))
        for aa in ax:
            aa.grid(color='#E1E5E9',lw=.5,alpha=.6,axis='y')
        fig.subplots_adjust(left=.07,right=.99,bottom=.17,top=.91,wspace=.32)
        for ext in ('png','svg','pdf'):
            fig.savefig(fig_dir/f'partition_rank_reversal.{ext}',dpi=240,facecolor='white')
        plt.close(fig)


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('--master',type=Path,required=True)
    pa.add_argument('--pairs',type=Path,required=True)
    pa.add_argument('--output',type=Path,required=True)
    pa.add_argument('--figures',type=Path,required=True)
    a=pa.parse_args()
    assert sha256(a.master)==SOURCE_SHA, 'Frozen benchmark SHA mismatch'
    assert sha256(a.pairs)==PAIRS_SHA, 'Selected matched pairs SHA mismatch'
    master=pd.read_csv(a.master)
    pairs=pd.read_csv(a.pairs)
    n=check_and_recompute(master,pairs,.10)
    groups,outcomes,flips=compute(pairs)
    sens=sensitivity(master)
    assert n==185 and groups['all']['ranking_reversals']==109
    a.output.mkdir(parents=True,exist_ok=True);a.figures.mkdir(parents=True,exist_ok=True)
    d={'source':str(a.master),'source_SHA256':SOURCE_SHA,
       'matches_SHA256':PAIRS_SHA,'source_rows':len(master),
       'source_materials':int(master.material_id.nunique()),
       'independent_pair_selection_verified':n,
       'selection':'one pair per material, both realized L_inf/RMSE within 0.10 dex; minimize sum abs log10 mismatch; no Bader input',
       'cohort':'frozen development; post hoc engineering analysis; NOT independent confirmation',
       'results_by_system':groups,'certification_diagnostics':outcomes,
       'caliper_sensitivity':sens,
       'interpretation_limits':[
           'Fixed-basin and re-derived Bader errors refer to different measurement algorithms.',
           'Codec comparisons are not rate-matched; no compression advantage claim follows.',
           'The max-per-atom resolved/fixed error ratios are NOT an exact additive migration decomposition.',
           'A paired statistical association does not uniquely establish local topological mechanism.',
           'The materials were selected on scalar-error overlap and represent a selected development subpopulation.']}
    (a.output/'rank_reversal_summary.json').write_text(json.dumps(d,indent=2)+'\n')
    info=pairs.copy()
    info['fixed_SZ3_over_SPERR']=info.Bader_fixed_error_SZ3_e/info.Bader_fixed_error_SPERR_e
    info['rederived_SZ3_over_SPERR']=info.Bader_resolved_error_SZ3_e/info.Bader_resolved_error_SPERR_e
    info['rank_reversed']=flips
    info.to_csv(a.output/'material_level_rank_reversal.csv',index=False)
    pd.DataFrame(sens).to_csv(a.output/'rank_reversal_caliper_sensitivity.csv',index=False)
    plot(pairs,groups,outcomes,a.figures)
    print(json.dumps({"materials":len(pairs),"rank_flips":int(flips.sum()),
                      "fixed_median":groups['all']['median_fixed_SZ3_over_SPERR'],
                      "rederived_median":groups['all']['median_rederived_SZ3_over_SPERR'],
                      "eligibility":outcomes},indent=2))

if __name__=='__main__':main()
