import json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
issues=[];cases=[]
for mid in ['mp-631399','nomad-FPTBoTAPMQA8']:
    p=root/'results'/'pilot'/mid
    if not (p/'finished.json').exists():
        issues.append(mid+': unfinished');continue
    rt=json.loads((p/'input_roundtrip.json').read_text())
    runtime=json.loads((p/'runtime.json').read_text())
    compat=json.loads((p/'io_adapter_compatibility.json').read_text())
    if not compat['accepted']:issues.append(mid+': IO adapter compatibility failed')
    rows=[json.loads(x) for x in (p/'outcomes.jsonl').read_text().splitlines()]
    keys={(r['variant'],r['solver']) for r in rows}
    if not rt['field_exact'] or not rt['same_atom_order'] or rt['lattice_max_difference']>1e-12 or rt['frac_max_difference']>1e-12:issues.append(mid+': input mismatch')
    if len(rows)!=21 or len(keys)!=21:issues.append(mid+': expected 21 unique outcomes')
    if any(r['status']!='SUCCESS' for r in rows):issues.append(mid+': solver failure; inspect original error')
    tol=2e-6*(runtime['n_atoms']+1)
    for r in rows:
        if r['status']=='SUCCESS' and abs(r['electron_accounting_error_e'])>tol:issues.append(mid+': electron accounting '+r['solver']+'/'+r['variant'])
    cases.append({'material_id':mid,'rows':len(rows),'roundtrip':rt,'pbs_job_id':runtime['pbs_job_id'],'accounting_tolerance_e':tol})
report={'accepted':not issues,'issues':issues,'cases':cases,'criterion':'Input identity, executable success and electron accounting only. No acceptance gate on the size or direction of scientific effects.'}
(root/'pilot_acceptance.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if issues:sys.exit(1)
(root/'PILOT_ACCEPTED').write_text('See pilot_acceptance.json\n')
