"""Postprocess the independent exploratory study; never touches frozen tables."""
import collections,csv,json,pathlib,statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=pathlib.Path(__file__).resolve().parent
DEST=ROOT/'results'/'production'
panel=json.loads((ROOT/'panel.json').read_text())
rows=[json.loads(line) for p in sorted(DEST.glob('*/outcomes.jsonl')) for line in p.read_text().splitlines()]
lookup={(r['material_id'],r['variant'],r['solver']):r for r in rows}
solvers=['baderkit_ongrid','henkelman_ongrid','henkelman_neargrid']
labels=['BaderKit ongrid','Henkelman ongrid','Henkelman neargrid']
seeds=[20260905,1,2,3,4]
control_names=['global','shift','stratified']
cases=[r for r in panel if not r['sentinel']]
failures=[r for r in rows if r['status']!='SUCCESS']
expected_variants=['original','float32']+[f'noise_{s}' for s in seeds]
for codec in ['zfp','sz3','sperr']:
    expected_variants.extend(f'{codec}_{rel:g}' for rel in [1e-4,1e-3])
    expected_variants.extend(f'{codec}_0.0001_{control}_{seed}' for control in control_names for seed in [1701,1702,1703])
missing=[(c['material_id'],v,s) for c in panel for v in expected_variants for s in solvers if (c['material_id'],v,s) not in lookup]
def good(mid,v,s):
    r=lookup.get((mid,v,s));return r if r and r['status']=='SUCCESS' else None
def writecsv(name,data):
    with (DEST/name).open('w',newline='') as f:
        if data:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

floors=[]
for c in panel:
    mid=c['material_id']
    for s in solvers:
        rr=[good(mid,f'noise_{seed}',s) for seed in seeds]
        vals=[r['max_charge_error_e'] for r in rr if r]
        floors.append({'material':mid,'domain':c['domain'],'selection_role':c['selection_role'],'sentinel':c['sentinel'],'solver':s,'n_noise_success':len(vals),'max_noise_response_e':max(vals) if len(vals)==5 else None})
writecsv('mechanism_noise_floors.csv',floors)
paired=[]
for c in panel:
    mid=c['material_id']
    for s in solvers:
        for codec in ['zfp','sz3','sperr']:
            base=good(mid,f'{codec}_0.0001',s)
            if not base:continue
            for control in control_names:
                rr=[good(mid,f'{codec}_0.0001_{control}_{seed}',s) for seed in [1701,1702,1703]]
                if not all(rr):continue
                b=base['max_charge_error_e'];a=statistics.median(r['max_charge_error_e'] for r in rr)
                paired.append({'material':mid,'domain':c['domain'],'sentinel':c['sentinel'],'solver':s,'codec':codec,'control':control,'codec_error_e':b,'control_median_error_e':a,'difference_e':a-b,'ratio':a/b if min(a,b)>2e-6 else None,'relative_linf_mismatch_max':max(abs(r['diagnostics']['linf']-base['diagnostics']['linf'])/max(base['diagnostics']['linf'],1e-300) for r in rr),'max_added_negative_fraction':max(r['diagnostics']['negative_density_fraction']-base['diagnostics']['negative_density_fraction'] for r in rr)})
writecsv('mechanism_spatial_pairs.csv',paired)
decomp=[]
for r in rows:
    if r['status']!='SUCCESS' or 'decomposition' not in r:continue
    d=r['decomposition'];domain=float(np.max(np.abs(d['domain_atoms'])));integrand=float(np.max(np.abs(d['integrand_atoms'])))
    c=next(c for c in panel if c['material_id']==r['material_id'])
    decomp.append({'material':r['material_id'],'sentinel':c['sentinel'],'variant':r['variant'],'kind':r['info']['kind'],'domain_max_e':domain,'integrand_max_e':integrand,'total_max_e':r['max_charge_error_e'],'domain_to_integrand':domain/integrand if integrand>0 else None,'migration_fraction':d['migration_fraction'],'closure_max_e':d['closure_max_e']})
writecsv('mechanism_domain_decomposition.csv',decomp)
summary={'n_rows':len(rows),'n_unique':len(lookup),'n_expected':len(panel)*len(expected_variants)*len(solvers),'n_missing':len(missing),'n_failures':len(failures),'failure_status_counts':dict(collections.Counter(r['status'] for r in failures)),'missing':missing,'interpretation_scope':'Exploratory deliberately stratified development panel; sentinel separate, no population-prevalence inference, no frozen-table updates.'}
(DEST/'mechanism_audit.json').write_text(json.dumps(summary,indent=2))

plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(11,5))
for j,s in enumerate(solvers):
    yy=[]
    for c in cases:
        r=next(r for r in floors if r['material']==c['material_id'] and r['solver']==s)
        val=r['max_noise_response_e'];yy.append(max(val,1e-8) if val is not None else np.nan)
    ax.plot(np.arange(len(cases))+(j-1)*.12,yy,'o',label=labels[j],markersize=5)
for tau in [1e-4,1e-3,1e-2]:ax.axhline(tau,color='gray',linestyle=':',linewidth=.7)
ax.axhspan(1e-8,2e-6,color='gray',alpha=.10,label='Henkelman difference print-resolution region')
ax.set_yscale('log');ax.set_ylim(bottom=7e-9);ax.set_ylabel('Maximum response over five noise seeds (e)')
ax.set_xticks(range(len(cases)),[c['material_id'] for c in cases],rotation=45,ha='right')
ax.set_title('Independent-method perturbation response | 12 selected development systems')
ax.legend(fontsize=8);fig.tight_layout()
fig.savefig(DEST/'01_independent_stability.png',dpi=180);fig.savefig(DEST/'01_independent_stability.pdf');plt.close(fig)

fig,axes=plt.subplots(1,3,figsize=(13,4.8),sharex=True,sharey=True)
for ax,s,label in zip(axes,solvers,labels):
    for control,color in zip(control_names,['#4477aa','#ee7733','#228833']):
        rr=[r for r in paired if r['solver']==s and r['control']==control and not r['sentinel']]
        ax.scatter([max(r['codec_error_e'],1e-8) for r in rr],[max(r['control_median_error_e'],1e-8) for r in rr],s=20,alpha=.7,color=color,label=control)
    ax.plot([1e-8,100],[1e-8,100],color='gray',linestyle=':',linewidth=1)
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Original codec charge error (e)');ax.set_title(label)
axes[0].set_ylabel('Median charge error after rearrangement (e)');axes[-1].legend(fontsize=8)
fig.suptitle('Same error-value multiset, different spatial organization | paired by material and codec')
fig.tight_layout();fig.savefig(DEST/'02_spatial_controls.png',dpi=180);fig.savefig(DEST/'02_spatial_controls.pdf');plt.close(fig)

fig,ax=plt.subplots(figsize=(6,5))
for kind,color in [('codec','#4477aa'),('spatial_control','#ee7733')]:
    rr=[r for r in decomp if r['kind']==kind and not r['sentinel']]
    ax.scatter([max(r['integrand_max_e'],1e-10) for r in rr],[max(r['domain_max_e'],1e-10) for r in rr],s=18,alpha=.6,label=kind,color=color)
ax.plot([1e-10,100],[1e-10,100],color='gray',linestyle=':');ax.set_xscale('log');ax.set_yscale('log')
ax.set_xlabel('Max absolute fixed-domain integrand term (e)');ax.set_ylabel('Max absolute domain-migration term (e)');ax.set_title('BaderKit exact per-atom charge decomposition');ax.legend()
fig.tight_layout();fig.savefig(DEST/'03_domain_decomposition.png',dpi=180);fig.savefig(DEST/'03_domain_decomposition.pdf');plt.close(fig)
print(json.dumps({k:v for k,v in summary.items() if k!='missing'},indent=2))
