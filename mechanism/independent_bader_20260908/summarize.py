import collections,csv,json,pathlib,statistics
from run_study import ROOT,TAUS,SOLVERS

def write_csv(path,rows):
    if not rows: path.write_text('');return
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def summarize(phase):
    dest=ROOT/'results'/phase;allrows=[]
    for p in sorted(dest.glob('*/outcomes.jsonl')):
        allrows.extend(json.loads(x) for x in p.read_text().splitlines())
    panel={r['material_id']:r for r in json.loads((ROOT/'panel.json').read_text())}
    grouped=collections.defaultdict(list)
    for r in allrows: grouped[r['material_id'],r['solver']].append(r)
    stability=[];geometry=[]
    for (mid,solver),rows in grouped.items():
        good={r['variant']:r for r in rows if r['status']=='SUCCESS'}
        noise=[r['max_charge_error_e'] for v,r in good.items() if v.startswith('noise_')]
        floor=max(noise) if noise else None
        stability.append({'material':mid,'domain':panel[mid]['domain'],'role':panel[mid]['selection_role'],'sentinel':panel[mid]['sentinel'],'solver':solver,'noise_seeds_complete':len(noise),'probe_response_max_e':floor,'f32_response_e':good.get('float32',{}).get('max_charge_error_e'),'failures':sum(r['status']!='SUCCESS' for r in rows),**{f'eligible_{tau:g}':('PRINT_PRECISION_AMBIGUOUS' if solver.startswith('henkelman') and abs(floor-tau)<=2e-6 else floor<tau) if floor is not None and len(noise)==5 else None for tau in TAUS}})
        groups=collections.defaultdict(list)
        for r in rows:
            if r['status']!='SUCCESS' or r.get('info',{}).get('kind')!='spatial_control':continue
            info=r['info'];base=good.get(info['base_variant'])
            if not base:continue
            a=r['max_charge_error_e'];b=base['max_charge_error_e']
            groups[info['codec'],info['control']].append((a,b,r))
        for (codec,control),vals in groups.items():
            ratios=[a/b for a,b,r in vals if b>2e-6 and a>2e-6]
            geometry.append({'material':mid,'domain':panel[mid]['domain'],'role':panel[mid]['selection_role'],'sentinel':panel[mid]['sentinel'],'solver':solver,'codec':codec,'control':control,'n_seeds':len(vals),'codec_error_e':vals[0][1],'control_error_median_e':statistics.median(a for a,b,r in vals),'paired_difference_median_e':statistics.median(a-b for a,b,r in vals),'ratio_median_above_2e_6':statistics.median(ratios) if ratios else None,'max_roundoff_delta_linf':max(r['diagnostics']['roundoff_delta_linf'] for a,b,r in vals)})
    write_csv(dest/'stability_comparison.csv',stability);write_csv(dest/'geometry_paired_effects.csv',geometry)
    summary={'phase':phase,'n_outcomes':len(allrows),'status_counts':dict(collections.Counter(r['status'] for r in allrows)),'materials_with_finished_marker':len(list(dest.glob('*/finished.json'))),'expected_panel_materials':2 if phase=='pilot' else len(panel),'interpretation':'Exploratory supplement; independent algorithm baselines, not revised confirmatory results.'}
    (dest/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':
    import sys
    summarize(sys.argv[1] if len(sys.argv)>1 else 'production')
