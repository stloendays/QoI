"""Figure 3 draft — certification landscape under Protocol A.1.

Reads benchmark/master_benchmark_full.csv directly. Headline certification uses
certified_at_* columns, which already encode eligibility ∧ resolved-Bader error < tau.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DF = pd.read_csv(ROOT / 'benchmark/master_benchmark_full.csv')

C = {
    'verm':'#D55E00','orange':'#E69F00','warm':'#FDDBC7',
    'lightblue':'#56B4E9','blue':'#0072B2','navy':'#003366',
    'gray':'#B3B3B3','charcoal':'#1A1A1A','bg':'#FAFAF8','white':'#FFFFFF'
}
CODEC_COLORS = {'SPERR':C['lightblue'], 'SZ3':C['blue'], 'ZFP':C['verm']}
TAUS = [('0.0001',1e-4),('0.001',1e-3),('0.01',1e-2)]

plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':9,'axes.linewidth':.8,
    'pdf.fonttype':42,'svg.fonttype':'none'
})

# Collapse repeated ladder rows to the material-codec level: a material is certifiable
# for a codec at tau if any tested operating point is certified.
rows=[]
for codec, g in DF.groupby('codec'):
    for tau_s, tau in TAUS:
        cert_col=f'certified_at_{tau_s}'
        elig_col=f'eligible_A1_at_{tau_s}'
        ign_col=f'certified_at_{tau_s}_ignoring_eligibility'
        m=g.groupby('material_id').agg(
            certified=(cert_col,'max'),
            eligible=(elig_col,'max'),
            ignoring_eligibility=(ign_col,'max')
        ).reset_index()
        rows.append({
            'codec':codec,'tau':tau,
            'certified_pct':100*m['certified'].mean(),
            'eligible_pct':100*m['eligible'].mean(),
            'ignoring_pct':100*m['ignoring_eligibility'].mean(),
            'n_materials':len(m)
        })
S=pd.DataFrame(rows)

fig, axs = plt.subplots(1,3,figsize=(10.4,3.7),facecolor=C['bg'])
for ax in axs: ax.set_facecolor(C['bg'])

# a — headline certification rate by codec and chemical tolerance
ax=axs[0]
x=np.arange(len(TAUS)); width=.23
codecs=[c for c in ['SPERR','SZ3','ZFP'] if c in set(S.codec)]
for j,codec in enumerate(codecs):
    y=[S[(S.codec==codec)&(S.tau==t)].certified_pct.iloc[0] for _,t in TAUS]
    ax.bar(x+(j-(len(codecs)-1)/2)*width,y,width=width,label=codec,
           color=CODEC_COLORS.get(codec,C['gray']),edgecolor='none')
ax.set_xticks(x,[r'$10^{-4}$',r'$10^{-3}$',r'$10^{-2}$'])
ax.set_xlabel('Chemical tolerance, τ (e)')
ax.set_ylabel('Certified materials (%)')
ax.set_ylim(0,100)
ax.set_title('Protocol A.1 certification',loc='left',fontweight='bold')
ax.legend(frameon=False,fontsize=8)

# b — eligibility ceiling: how much of the corpus is even judgeable at each tau
ax=axs[1]
for codec in codecs:
    y=[S[(S.codec==codec)&(S.tau==t)].eligible_pct.iloc[0] for _,t in TAUS]
    ax.plot(x,y,marker='o',lw=1.8,ms=5,label=codec,color=CODEC_COLORS.get(codec,C['gray']))
ax.set_xticks(x,[r'$10^{-4}$',r'$10^{-3}$',r'$10^{-2}$'])
ax.set_xlabel('Chemical tolerance, τ (e)')
ax.set_ylabel('Eligible materials (%)')
ax.set_ylim(0,100)
ax.set_title('Stability floor sets a certification ceiling',loc='left',fontweight='bold')

# c — show how misleading the answer would be if eligibility were ignored
ax=axs[2]
for codec in codecs:
    sub=S[S.codec==codec].sort_values('tau')
    true=sub.certified_pct.to_numpy()
    ign=sub.ignoring_pct.to_numpy()
    gap=ign-true
    ax.plot(x,gap,marker='o',lw=1.8,ms=5,label=codec,color=CODEC_COLORS.get(codec,C['gray']))
ax.axhline(0,color=C['gray'],lw=1,ls='--')
ax.set_xticks(x,[r'$10^{-4}$',r'$10^{-3}$',r'$10^{-2}$'])
ax.set_xlabel('Chemical tolerance, τ (e)')
ax.set_ylabel('Overstatement if eligibility ignored (pp)')
ax.set_title('Ignoring stability inflates apparent success',loc='left',fontweight='bold')

for i,ax in enumerate(axs):
    ax.text(-.16,1.08,chr(97+i),transform=ax.transAxes,fontsize=14,fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.18,lw=.5); ax.set_axisbelow(True)

fig.suptitle('Figure 3 | Certification is jointly limited by codec error and observable stability',
             x=.06,y=1.04,ha='left',fontsize=13.2,fontweight='bold')
fig.savefig(Path(__file__).with_suffix('.png'),dpi=400,bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.svg'),bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.pdf'),bbox_inches='tight')
