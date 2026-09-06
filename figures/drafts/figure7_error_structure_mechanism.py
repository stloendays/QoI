"""Figure 7 draft — spatial error structure drives chemical error.

Uses the frozen mechanism/basin_error_decomposition_summary.csv. This is the
mechanistic figure: total Bader error is decomposed into integrand and domain
migration contributions and related to voxel reassignment.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
D=pd.read_csv(ROOT/'mechanism/basin_error_decomposition_summary.csv')
C={'verm':'#D55E00','orange':'#E69F00','warm':'#FDDBC7','lightblue':'#56B4E9','blue':'#0072B2','navy':'#003366','gray':'#B3B3B3','charcoal':'#1A1A1A','bg':'#FAFAF8'}
COL={'sperr':C['lightblue'],'sz3':C['blue'],'zfp':C['verm']}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})

fig,axs=plt.subplots(1,3,figsize=(10.7,3.8),facecolor=C['bg'])
for ax in axs: ax.set_facecolor(C['bg'])

# a — total chemical error versus reassigned voxels
ax=axs[0]
for codec,g in D.groupby('codec'):
    ax.scatter(g.frac_voxels_reassigned,g.dq_total_max_e,s=22,alpha=.68,
               color=COL.get(codec,C['gray']),label=codec.upper(),edgecolors='none')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Fraction of voxels reassigned')
ax.set_ylabel(r'Total Bader error, $\Delta Q_{total}$ (e)')
ax.set_title('Basin migration tracks chemical error',loc='left',fontweight='bold')
ax.legend(frameon=False,fontsize=8)

# b — integrand-only versus domain-migration contribution
ax=axs[1]
for codec,g in D.groupby('codec'):
    x=g.dq_integrand_max_e.clip(lower=1e-16); y=g.dq_domain_max_e.clip(lower=1e-16)
    ax.scatter(x,y,s=22,alpha=.68,color=COL.get(codec,C['gray']),edgecolors='none')
lo=1e-16; hi=max(D.dq_integrand_max_e.max(),D.dq_domain_max_e.max())
ax.plot([lo,hi],[lo,hi],ls='--',lw=1,color=C['gray'])
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel(r'Integrand contribution, $\Delta Q_{integrand}$ (e)')
ax.set_ylabel(r'Domain contribution, $\Delta Q_{domain}$ (e)')
ax.set_title('Domain motion often dominates value perturbation',loc='left',fontweight='bold')

# c — distribution of domain share, clipped only for visualization because cancellation can yield >1
ax=axs[2]
order=[c for c in ['sperr','sz3','zfp'] if c in set(D.codec)]
vals=[D.loc[D.codec==c,'domain_share_of_total'].dropna().clip(0,1.5).to_numpy() for c in order]
parts=ax.violinplot(vals,showmedians=True,showextrema=False)
for body,codec in zip(parts['bodies'],order):
    body.set_facecolor(COL.get(codec,C['gray'])); body.set_edgecolor('none'); body.set_alpha(.75)
parts['cmedians'].set_color(C['charcoal']); parts['cmedians'].set_linewidth(1.2)
ax.axhline(1,color=C['gray'],ls='--',lw=1)
ax.set_xticks(range(1,len(order)+1),[c.upper() for c in order])
ax.set_ylabel(r'$|\Delta Q_{domain}| / |\Delta Q_{total}|$')
ax.set_title('The dominant error channel is topological',loc='left',fontweight='bold')

for i,ax in enumerate(axs):
    ax.text(-.16,1.08,chr(97+i),transform=ax.transAxes,fontsize=14,fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.16,lw=.5); ax.set_axisbelow(True)
fig.suptitle('Figure 7 | Spatial error structure, not pointwise magnitude alone, controls Bader fidelity',
             x=.055,y=1.04,ha='left',fontsize=13.0,fontweight='bold')
fig.savefig(Path(__file__).with_suffix('.png'),dpi=400,bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.svg'),bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.pdf'),bbox_inches='tight')
