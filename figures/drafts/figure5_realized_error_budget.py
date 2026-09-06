"""Figure 5 draft — requested versus realized L-infinity error budget.

Reads benchmark/master_benchmark_full.csv. This figure is intentionally focused on
what each codec actually spends from the nominal pointwise-error budget.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DF = pd.read_csv(ROOT/'benchmark/master_benchmark_full.csv')

C={'verm':'#D55E00','orange':'#E69F00','warm':'#FDDBC7','lightblue':'#56B4E9',
   'blue':'#0072B2','navy':'#003366','gray':'#B3B3B3','charcoal':'#1A1A1A','bg':'#FAFAF8'}
CODEC_COLORS={'SPERR':C['lightblue'],'SZ3':C['blue'],'ZFP':C['verm']}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})

fig,axs=plt.subplots(1,3,figsize=(10.6,3.8),facecolor=C['bg'])
for ax in axs: ax.set_facecolor(C['bg'])

# a — realized versus nominal pointwise bound
ax=axs[0]
for codec,g in DF.groupby('codec'):
    ax.scatter(g['nominal_tolerance_absolute'],g['realized_Linf'],s=7,alpha=.22,
               color=CODEC_COLORS.get(codec,C['gray']),label=codec,edgecolors='none')
lo=max(DF['nominal_tolerance_absolute'].replace(0,np.nan).min(),1e-12)
hi=DF['nominal_tolerance_absolute'].max()
ax.plot([lo,hi],[lo,hi],ls='--',lw=1,color=C['charcoal'])
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Nominal absolute tolerance')
ax.set_ylabel(r'Realized $L_\infty$ error')
ax.set_title('The requested bound is not equally consumed',loc='left',fontweight='bold')
ax.legend(frameon=False,fontsize=8)

# b — budget-utilization distribution
ax=axs[1]
order=[c for c in ['SPERR','SZ3','ZFP'] if c in set(DF.codec)]
data=[DF.loc[DF.codec==c,'realized_Linf_over_nominal'].dropna().to_numpy() for c in order]
parts=ax.violinplot(data,showmedians=True,showextrema=False)
for body,codec in zip(parts['bodies'],order):
    body.set_facecolor(CODEC_COLORS.get(codec,C['gray'])); body.set_edgecolor('none'); body.set_alpha(.75)
parts['cmedians'].set_color(C['charcoal']); parts['cmedians'].set_linewidth(1.2)
ax.axhline(1,color=C['gray'],ls='--',lw=1)
ax.set_xticks(range(1,len(order)+1),order)
ax.set_ylabel(r'Realized / nominal $L_\infty$')
ax.set_title('ZFP systematically under-spends the bound',loc='left',fontweight='bold')

# c — report robust median and IQR, not a single hand-picked number
ax=axs[2]
med=[]; q1=[]; q3=[]
for codec in order:
    v=DF.loc[DF.codec==codec,'realized_Linf_over_nominal'].dropna().to_numpy()
    med.append(np.nanmedian(v)); q1.append(np.nanpercentile(v,25)); q3.append(np.nanpercentile(v,75))
y=np.arange(len(order))
ax.errorbar(med,y,xerr=[np.array(med)-np.array(q1),np.array(q3)-np.array(med)],fmt='o',
            color=C['charcoal'],ecolor=C['gray'],capsize=3)
for yy,codec,m in zip(y,order,med):
    ax.scatter([m],[yy],s=55,color=CODEC_COLORS.get(codec,C['gray']),zorder=3)
    ax.text(m,yy+.22,f'{m:.3f}×',ha='center',va='bottom',fontsize=8,fontweight='bold')
ax.axvline(1,color=C['gray'],ls='--',lw=1)
ax.set_yticks(y,order)
ax.set_xlabel(r'Median realized / nominal $L_\infty$')
ax.set_title('Codec chemistry comparisons must use realized error',loc='left',fontweight='bold')

for i,ax in enumerate(axs):
    ax.text(-.16,1.08,chr(97+i),transform=ax.transAxes,fontsize=14,fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.16,lw=.5); ax.set_axisbelow(True)

fig.suptitle('Figure 5 | Nominal tolerance and realized pointwise error are not interchangeable',
             x=.055,y=1.04,ha='left',fontsize=13.2,fontweight='bold')
fig.savefig(Path(__file__).with_suffix('.png'),dpi=400,bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.svg'),bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.pdf'),bbox_inches='tight')
