#!/usr/bin/env python3
"""Retrospective real-material analysis of Bader rank reversals and basin migration.

Not a causal identification of atom-wise boundary migration, which requires
per-atom basin integration arrays. Does not touch held-out material cohorts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SOURCE_SHA = 'fb6e77dc1ca1525918397415c1f3ef7dd17206b5f945ac6df8f9a2dc5f80a480'
CODES = ("SZ3", "SPERR")
PREDICTORS = {
    'reassignment_ratio': ('reassigned_fraction_SZ3', 'reassigned_fraction_SPERR'),
    'fixed_bader_ratio': ('Bader_fixed_error_SZ3_e', 'Bader_fixed_error_SPERR_e'),
    'density_linf_ratio': ('Linfinity_SZ3', 'Linfinity_SPERR'),
    'density_rmse_ratio': ('RMSE_SZ3', 'RMSE_SPERR'),
}


def sha256(path: Path) -> str:
    """SHA-256 of a text input with CR removed, so a CRLF checkout verifies the committed LF bytes."""
    return hashlib.sha256(path.read_bytes().replace(b'\r', b'')).hexdigest()


def paired_vectors(frame: pd.DataFrame) -> tuple[np.ndarray,dict[str,np.ndarray]]:
    if frame.material_id.duplicated().any():
        raise ValueError('One pair per material is required')
    if not {'material_id','system_type','Bader_resolved_error_SZ3_e','Bader_resolved_error_SPERR_e',
            *(name for pair in PREDICTORS.values() for name in pair)}.issubset(frame.columns):
        raise ValueError('Required columns missing')
    num_cols=['Bader_resolved_error_SZ3_e','Bader_resolved_error_SPERR_e'] + [n for pair in PREDICTORS.values() for n in pair]
    arr=frame[num_cols].to_numpy(dtype=float)
    if not np.isfinite(arr).all() or not (arr>0).all():
        raise ValueError('Nonpositive or nonfinite inputs')
    response=np.log10(frame['Bader_resolved_error_SZ3_e'].values/frame['Bader_resolved_error_SPERR_e'].values)
    predictors={key:np.log10(frame[a].values/frame[b].values) for key,(a,b) in PREDICTORS.items()}
    return response,predictors


def bootstrap_spearman(x:np.ndarray,y:np.ndarray,n:int=6000,seed:int=20261023):
    if len(x)<4:
        raise ValueError('Need at least 4 materials')
    observed=float(spearmanr(x,y).statistic)
    rng=np.random.default_rng(seed)
    boot=[]
    for i in range(n):
        idx=rng.integers(0,len(x),size=len(x))
        rho=float(spearmanr(x[idx],y[idx]).statistic)
        if np.isfinite(rho):
            boot.append(rho)
    lo,hi=np.quantile(boot,[.025,.975])
    return observed,[float(lo),float(hi)]


def wilson(k:int,n:int,z:float=1.959963984540054):
    p=k/n; w=z*z
    c=(p+w/(2*n))/(1+w/n)
    delta=z*np.sqrt(p*(1-p)/n+w/(4*n*n))/(1+w/n)
    return [float(c-delta),float(c+delta)]


def analyze(frame:pd.DataFrame):
    response,predictors=paired_vectors(frame)
    fixed_ratio=10**predictors['fixed_bader_ratio']
    recomputed_ratio=10**response
    flips=(fixed_ratio>1)&(recomputed_ratio<1)
    if int((fixed_ratio>1).sum())!=185 or len(frame)!=185 or int(flips.sum())!=109:
        raise AssertionError('Frozen scalar pair cohort drift')
    subsets={"all":np.ones(len(frame),dtype=bool),"bulk":frame.system_type.eq('bulk').values,
             "slab":frame.system_type.eq('slab').values}
    results={}
    for group,sel in subsets.items():
        stats={}
        for name,x in predictors.items():
            rho,ci=bootstrap_spearman(x[sel],response[sel],n=4000,seed=20261023)
            stats[name]={"rho":rho,"bootstrap95CI":ci,"asymptotic_p":float(spearmanr(x[sel],response[sel]).pvalue)}
        n=int(sel.sum()); k=int(flips[sel].sum())
        results[group]={"materials":n,"flips":k,"flip_fraction":k/n,"flip_wilson95CI":wilson(k,n),
                        "predictors_vs_rederived_error_ratio":stats,
                        "SZ3_lower_reassignment_fraction":int((predictors['reassignment_ratio'][sel]<0).sum())}
    per=frame[['material_id','formula','system_type','log10_Linf_mismatch_abs','log10_RMSE_mismatch_abs']].copy()
    for name,x in predictors.items():per['log10_'+name]=x
    per['log10_rederived_bader_ratio']=response
    per['rank_reversed']=flips
    if len(frame['system_type'].unique())!=2:
        raise AssertionError('Unexpected system types')
    return per, results


def plot(per:pd.DataFrame,stats:dict,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    style={'font.family':'DejaVu Sans','font.size':9.5,'axes.spines.top':False,
           'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'}
    with plt.rc_context(style):
        fig,(a,b)=plt.subplots(1,2,figsize=(10.5,4.35),dpi=180,gridspec_kw={'width_ratios':[1.22,.9]})
        palette={'bulk':'#315782','slab':'#70887A'}
        x=per.log10_reassignment_ratio.to_numpy()
        y=per.log10_rederived_bader_ratio.to_numpy()
        for subtype in ['bulk','slab']:
            sel=per.system_type.eq(subtype).to_numpy()
            a.scatter(x[sel],y[sel],s=23,alpha=.76,color=palette[subtype],rasterized=True,
                      label=f'{subtype.capitalize()} (n={sel.sum()})')
        a.axhline(0,color='#70767d',ls='--',lw=1)
        a.axvline(0,color='#70767d',ls='--',lw=1)
        allstats=stats['all']['predictors_vs_rederived_error_ratio']['reassignment_ratio']
        a.text(.03,.96,f'Spearman rho = {allstats["rho"]:.3f}\n95% bootstrap CI [{allstats["bootstrap95CI"][0]:.3f}, {allstats["bootstrap95CI"][1]:.3f}]',
               va='top',transform=a.transAxes,fontsize=9)
        a.set_xlabel('log10 (SZ3 / SPERR reassigned-voxel fraction)')
        a.set_ylabel('log10 (SZ3 / SPERR re-derived Bader error)')
        a.set_title('a   Basin reassignment and Bader errors',loc='left',fontweight='bold')
        a.legend(frameon=False,loc='lower right',fontsize=8.5)
        a.grid(alpha=.16,lw=.5)
        names=['Reassigned voxels','Fixed-basin error','Density RMSE','Density max error']
        keys=['reassignment_ratio','fixed_bader_ratio','density_rmse_ratio','density_linf_ratio']
        for j,(name,key) in enumerate(zip(names,keys)):
            obj=stats['all']['predictors_vs_rederived_error_ratio'][key]
            lo,hi=obj['bootstrap95CI']
            b.plot([lo,hi],[j,j],color='#3A5169',lw=2.3,solid_capstyle='round')
            b.plot(obj['rho'],j,marker='o',ms=6,color='#315782')
            b.text(min(1,hi+.03),j,f'{obj["rho"]:+.2f}',va='center',fontsize=9)
        b.axvline(0,color='#70767d',lw=1,ls='--')
        b.set_yticks(range(4),names)
        b.invert_yaxis()
        b.set_xlim(-.42,.94)
        b.set_xlabel('Spearman rho (material-level bootstrap 95% CI)')
        b.set_title('b   Correlates of Bader error',loc='left',fontweight='bold')
        b.grid(axis='x',alpha=.16,lw=.5)
        fig.subplots_adjust(left=.105,right=.97,bottom=.16,top=.91,wspace=.41)
        for ext in ['png','svg','pdf']:
            fig.savefig(out/('migration_coupling.'+ext),facecolor='white',dpi=220)
        plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pairs',type=Path,required=True)
    parser.add_argument('--results',type=Path,required=True)
    parser.add_argument('--figures',type=Path,required=True)
    args=parser.parse_args()
    if sha256(args.pairs)!=SOURCE_SHA:raise RuntimeError('Matched pair source hash mismatch')
    p=pd.read_csv(args.pairs)
    per,res=analyze(p)
    args.results.mkdir(parents=True,exist_ok=True)
    per.to_csv(args.results/'migration_coupling_per_material.csv',index=False)
    report={'dataset':'Frozen RhoCodec development pairs, retrospective',
            'sample':'185 selected materials, one SZ3/SPERR pair each, joint density L_inf and RMSE caliper 0.10 dex',
            'source_SHA256':SOURCE_SHA,
            'statistics':res,
            'limitations':['Associations are descriptive, not causally identified basin migration contributions.',
              'Per-atom basin coordinates are needed for an exact fixed-domain / domain-migration decomposition.',
              'No new independent confirmation materials were analyzed.',
              'Pair selection is not matched on compression size or rate.',
              'Reassigned voxel fraction is computed relative to the reference Bader partition.']}
    (args.results/'migration_coupling_summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    plot(per,res,args.figures)
    print(json.dumps({"n":res['all']['materials'],"reversals":res['all']['flips'],
                      "reassignment_rho":res['all']['predictors_vs_rederived_error_ratio']['reassignment_ratio']},indent=2))
if __name__=='__main__':main()
