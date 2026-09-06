"""Figure 4 draft — Protocol A.1 stability floor.
Reads frozen stability outputs directly from the repository.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
A1 = pd.read_csv(ROOT/'stability/stability_floor_A1.csv')
A0 = pd.read_csv(ROOT/'stability/stability_floor_A_archived_float32.csv')

C={'verm':'#D55E00','orange':'#E69F00','warm':'#FDDBC7','lightblue':'#56B4E9','blue':'#0072B2','navy':'#003366','gray':'#B3B3B3','charcoal':'#1A1A1A','bg':'#FAFAF8'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})

fig,axs=plt.subplots(1,2,figsize=(9.2,3.9),facecolor=C['bg'])
for ax in axs: ax.set_facecolor(C['bg'])

# a: distribution of the physically meaningful A.1 floor
v=A1['stability_floor_A1_e'].dropna().to_numpy()
bins=np.logspace(np.floor(np.log10(v[v>0].min())),np.ceil(np.log10(v.max())),35)
axs[0].hist(v,bins=bins,color=C['blue'],edgecolor='white',linewidth=.4)
axs[0].set_xscale('log')
axs[0].axvline(1e-4,color=C['verm'],ls='--',lw=1.2,label=r'$10^{-4}$ e')
axs[0].axvline(1e-3,color=C['orange'],ls='--',lw=1.2,label=r'$10^{-3}$ e')
axs[0].axvline(1e-2,color=C['navy'],ls='--',lw=1.2,label=r'$10^{-2}$ e')
axs[0].set_xlabel('Protocol A.1 stability floor (e)')
axs[0].set_ylabel('Materials')
axs[0].set_title('Chemical observables have a material-dependent floor',loc='left',fontweight='bold')
axs[0].legend(frameon=False,fontsize=8)

# b: compare archived A against A.1 after material join; discover archived value column robustly
idcol='material_id'
val0=[c for c in A0.columns if 'floor' in c.lower() and c!=idcol][0]
m=A1[[idcol,'stability_floor_A1_e']].merge(A0[[idcol,val0]],on=idcol,how='inner').dropna()
x=m[val0].to_numpy(); y=m['stability_floor_A1_e'].to_numpy()
mask=(x>0)&(y>0); x=x[mask]; y=y[mask]
axs[1].scatter(x,y,s=13,alpha=.58,color=C['blue'],edgecolors='none')
lo=min(x.min(),y.min()); hi=max(x.max(),y.max())
axs[1].plot([lo,hi],[lo,hi],ls='--',lw=1,color=C['gray'])
axs[1].set_xscale('log'); axs[1].set_yscale('log')
axs[1].set_xlabel('Archived Protocol A floor (e)')
axs[1].set_ylabel('Protocol A.1 floor (e)')
axs[1].set_title('Probe semantics change the inferred stability floor',loc='left',fontweight='bold')
ratio=np.median(y/x)
axs[1].text(.04,.95,f'median A.1 / A = {ratio:.2g}×',transform=axs[1].transAxes,va='top',fontweight='bold',color=C['verm'])

for i,ax in enumerate(axs):
    ax.text(-.14,1.08,chr(97+i),transform=ax.transAxes,fontsize=14,fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.18,lw=.5); ax.set_axisbelow(True)
fig.suptitle('Figure 4 | Stability floor is part of the measurement protocol',x=.07,y=1.04,ha='left',fontsize=13.5,fontweight='bold')
fig.savefig(Path(__file__).with_suffix('.png'),dpi=400,bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.svg'),bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.pdf'),bbox_inches='tight')
