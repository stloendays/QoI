"""Figure 2 draft — fixed-basin metrics understate downstream Bader error.

Reads benchmark/master_benchmark_full.csv directly. This is a scientific-content
pass: preserve data fidelity first; final typography/layout comes later.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DF = pd.read_csv(ROOT / 'benchmark' / 'master_benchmark_full.csv')

C = {
    'SPERR': '#003366',
    'SZ3': '#0072B2',
    'ZFP': '#D55E00',
    'gray': '#B3B3B3',
    'charcoal': '#1A1A1A',
    'bg': '#FAFAF8',
    'warm': '#FDDBC7',
}
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.linewidth': .8,
    'pdf.fonttype': 42,
    'svg.fonttype': 'none',
})

req = ['codec','Bader_error_fixed_e','Bader_error_resolved_e','fixed_basin_understatement','frac_voxels_reassigned']
d = DF[req].replace([np.inf, -np.inf], np.nan).dropna(subset=['Bader_error_fixed_e','Bader_error_resolved_e']).copy()
d = d[(d.Bader_error_fixed_e > 0) & (d.Bader_error_resolved_e > 0)]
d['ratio'] = d['Bader_error_resolved_e'] / d['Bader_error_fixed_e']

fig, axs = plt.subplots(1, 3, figsize=(11.2, 3.8), facecolor=C['bg'])
for ax in axs:
    ax.set_facecolor(C['bg'])

# a — paired metric comparison
ax = axs[0]
for codec in ['SPERR','SZ3','ZFP']:
    q = d[d.codec == codec]
    ax.scatter(q.Bader_error_fixed_e, q.Bader_error_resolved_e,
               s=11, alpha=.36, linewidths=0, color=C[codec], label=codec)
lo = min(d.Bader_error_fixed_e.min(), d.Bader_error_resolved_e.min())
hi = max(d.Bader_error_fixed_e.max(), d.Bader_error_resolved_e.max())
ax.plot([lo,hi],[lo,hi],ls='--',lw=1.0,color=C['gray'])
ax.fill_between([lo,hi],[2*lo,2*hi],[hi,hi],color=C['warm'],alpha=.24)
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlim(lo,hi); ax.set_ylim(lo,hi)
ax.set_xlabel(r'Fixed-basin error, $\Delta Q_{fixed}$ (e)')
ax.set_ylabel(r'Resolved-basin error, $\Delta Q_{resolved}$ (e)')
ax.set_title('Re-resolving Bader basins exposes hidden error',loc='left',fontweight='bold')
ax.legend(frameon=False,fontsize=8)

# b — understatement-factor distribution
ax = axs[1]
r = d['ratio'].replace([np.inf,-np.inf],np.nan).dropna()
logbins = np.logspace(np.floor(np.log10(max(r.min(),1e-2))), np.ceil(np.log10(r.max())), 42)
for codec in ['SPERR','SZ3','ZFP']:
    z = d.loc[d.codec==codec,'ratio'].replace([np.inf,-np.inf],np.nan).dropna()
    if len(z):
        ax.hist(z,bins=logbins,histtype='step',lw=1.7,color=C[codec],label=codec)
ax.axvline(1,color=C['gray'],ls='--',lw=1)
ax.axvline(2,color='#777777',ls=':',lw=1)
ax.set_xscale('log')
ax.set_xlabel(r'Understatement factor, $\Delta Q_{resolved}/\Delta Q_{fixed}$')
ax.set_ylabel('Benchmark points')
ax.set_title('Fixed basins can suppress the apparent error',loc='left',fontweight='bold')

# c — topology link
ax = axs[2]
q = d.dropna(subset=['frac_voxels_reassigned'])
for codec in ['SPERR','SZ3','ZFP']:
    z = q[q.codec==codec]
    ax.scatter(100*z.frac_voxels_reassigned, z.ratio,
               s=11, alpha=.34, linewidths=0,color=C[codec])
ax.axhline(1,color=C['gray'],ls='--',lw=1)
ax.set_yscale('log')
ax.set_xlabel('Reassigned voxels (%)')
ax.set_ylabel('Understatement factor')
ax.set_title('Error inflation tracks basin migration',loc='left',fontweight='bold')

for i,ax in enumerate(axs):
    ax.text(-.13,1.08,chr(97+i),transform=ax.transAxes,fontsize=14,fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=.16,lw=.5)
    ax.set_axisbelow(True)

fig.suptitle('Figure 2 | A fixed integration domain hides chemically relevant topology changes',
             x=.055,y=1.04,ha='left',fontsize=13.2,fontweight='bold')
fig.savefig(Path(__file__).with_suffix('.png'),dpi=400,bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.svg'),bbox_inches='tight')
fig.savefig(Path(__file__).with_suffix('.pdf'),bbox_inches='tight')
