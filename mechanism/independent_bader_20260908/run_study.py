from __future__ import annotations
import argparse,csv,datetime,gc,itertools,json,os,pathlib,subprocess,sys,tempfile,time,traceback
import numpy as np

ROOT=pathlib.Path(__file__).resolve().parent
BADER=ROOT/'reference_source'/'bader'
SOLVERS=['baderkit_ongrid','henkelman_ongrid','henkelman_neargrid']
TAUS=[1e-4,1e-3,1e-2]
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,x): p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def append(p,x):
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(x,allow_nan=False)+'\n');f.flush()
def integrate(field,labels,n):
    return np.bincount(np.asarray(labels,dtype=np.int64).ravel(order='F'),weights=field.ravel(order='F'),minlength=n+1)[:n]/field.size

def write_chgcar(path,field,lattice,frac,symbols):
    groups=[(s,len(list(g))) for s,g in itertools.groupby(symbols)]
    with path.open('w') as f:
        f.write('QoI independent Bader supplement\n1.0\n')
        np.savetxt(f,lattice,fmt='%.17g')
        f.write(' '.join(s for s,n in groups)+'\n'+' '.join(str(n) for s,n in groups)+'\nDirect\n')
        np.savetxt(f,frac,fmt='%.17g')
        f.write('\n'+' '.join(map(str,field.shape))+'\n')
        flat=field.ravel(order='F'); end=len(flat)//5*5
        np.savetxt(f,flat[:end].reshape(-1,5),fmt='%.17g')
        if end<len(flat): f.write(' '.join(format(v,'.17g') for v in flat[end:])+'\n')

def codec(name,field,bound,work):
    if name=='zfp':
        import zfpy
        blob=zfpy.compress_numpy(field,tolerance=bound)
        return zfpy.decompress_numpy(blob),len(blob)
    if name=='sz3':
        from pysz import sz,szConfig,szErrorBoundMode
        cfg=szConfig();cfg.errorBoundMode=szErrorBoundMode.ABS;cfg.absErrorBound=bound
        blob,_=sz.compress(field,cfg);recon,_=sz.decompress(blob,field.dtype.type,field.shape)
        return recon,int(np.asarray(blob).nbytes)
    import h5py,hdf5plugin
    p=work/'sperr.h5'
    with h5py.File(p,'w') as f:
        ds=f.create_dataset('density',data=field,chunks=field.shape,**hdf5plugin.Sperr(absolute=bound));f.flush();size=int(ds.id.get_storage_size())
    with h5py.File(p,'r') as f: recon=f['density'][()]
    p.unlink()
    return recon,size

def solve(name,field,lattice,frac,symbols,work,logdir):
    if name=='baderkit_ongrid':
        from baderkit import Bader,Grid
        from pymatgen.core import Structure
        st=Structure(lattice,symbols,frac)
        grid=Grid(structure=st,data={'total':field},data_type='charge')
        a=Bader(charge_grid=grid,total_charge_grid=grid,reference_grid=grid,method='ongrid',vacuum_tol=1e-3,persistence_tol=0.5,nna_cutoff=False)
        q=np.asarray(a.atom_charges,dtype=float);lab=np.asarray(a.atom_labels,dtype=np.int64)
        q_integrated=integrate(field,lab,len(symbols))
        mismatch=float(np.max(np.abs(q_integrated-q)))
        if mismatch>1e-7: raise RuntimeError(f'BaderKit label/charge mismatch {mismatch}')
        vac=float(a.vacuum_charge)
        return q,lab,{'vacuum_charge_e':vac,'n_maxima':len(a.maxima_frac),'charge_selfcheck_e':mismatch,'electron_accounting_error_e':float(q.sum()+vac-field.mean()),'zero_basin_atoms':int(sum(np.bincount(lab.ravel(),minlength=len(symbols)+1)[:len(symbols)]==0))}
    work.mkdir(exist_ok=True)
    inputpath=work/'CHGCAR'
    write_chgcar(inputpath,field,lattice,frac,symbols)
    mode=name.split('_')[1]
    command=[str(BADER),'CHGCAR','-b',mode,'-vac','0.001']
    with (logdir/f'{name}.log').open('w') as f:
        rc=subprocess.call(command,cwd=work,stdout=f,stderr=subprocess.STDOUT)
    if rc: raise RuntimeError(f'Henkelman exit {rc}; see solver log')
    acf=(work/'ACF.dat').read_text()
    (logdir/f'{name}_ACF.dat').write_text(acf)
    data=[];vac=0.
    for line in acf.splitlines():
        fields=line.split()
        if len(fields)>=7 and fields[0].isdigit(): data.append([float(x) for x in fields[:7]])
        if 'VACUUM CHARGE:' in line: vac=float(line.split(':')[1])
    if len(data)!=len(symbols): raise RuntimeError(f'ACF atoms {len(data)} != {len(symbols)}')
    if [int(x[0]) for x in data]!=list(range(1,len(symbols)+1)): raise RuntimeError('ACF atom order mismatch')
    q=np.array([x[4] for x in data])
    return q,None,{'vacuum_charge_e':vac,'electron_accounting_error_e':float(q.sum()+vac-field.mean()),'acf_print_precision_e':1e-6,'command':command,'zero_basin_atoms':sum(x[6]==0 for x in data)}

def diagnostics(field,delta,volume):
    recon=field+delta
    diffs=[]
    for ax in range(3):
        d0=np.roll(field,-1,axis=ax)-field;d1=np.roll(recon,-1,axis=ax)-recon
        diffs.append(int(np.count_nonzero(np.sign(d0)!=np.sign(d1))))
    vacuum=field/volume<1e-3
    energy=float(np.sum(delta*delta))
    return {'linf':float(np.max(np.abs(delta))),'rmse':float(np.sqrt(np.mean(delta*delta))),'mean_error':float(delta.mean()),'l1_mean':float(np.mean(np.abs(delta))),'negative_density_fraction':float(np.mean(recon<0)),'vacuum_error_energy_fraction':float(np.sum(delta[vacuum]**2)/energy) if energy else 0.,'periodic_axis_order_changes':diffs,'axis_error_product_mean':[float(np.mean(delta*np.roll(delta,-1,axis=ax))) for ax in range(3)]}

def variants(field,work,pilot):
    f32=field.astype(np.float32).astype(np.float64);amp=float(np.max(np.abs(f32-field)))
    yield 'float32',f32-field,{'kind':'float32','probe_amplitude':amp}
    for seed in ([20260905] if pilot else [20260905,1,2,3,4]):
        yield f'noise_{seed}',np.random.default_rng(seed).uniform(-amp,amp,field.shape),{'kind':'noise','seed':seed,'probe_amplitude':amp}
    for name in (['zfp'] if pilot else ['zfp','sz3','sperr']):
        for rel in ([1e-4] if pilot else [1e-4,1e-3]):
            recon,nbytes=codec(name,field,float(np.ptp(field)*rel),work)
            delta=np.asarray(recon,dtype=float)-field
            bound=float(np.ptp(field)*rel)
            info={'kind':'codec','codec':name,'relative_tolerance':rel,'requested_absolute_bound':bound,'compressed_bytes':nbytes,'compression_ratio':field.nbytes/nbytes,'bound_respected':bool(np.max(np.abs(delta))<=bound*(1+1e-6)+1e-15)}
            yield f'{name}_{rel:g}',delta,info
            if rel!=1e-4: continue
            flat=delta.ravel(order='F')
            positive=field>0;bins=np.zeros(field.shape,dtype=np.int8)
            if np.any(positive):
                logval=np.log10(field[positive]);edges=np.linspace(float(logval.min()),float(logval.max()),17)
                bins[positive]=np.clip(np.searchsorted(edges,logval,side='right'),1,16)
            for seed in ([1701] if pilot else [1701,1702,1703]):
                rng=np.random.default_rng(seed)
                shuffled=rng.permutation(flat).reshape(field.shape,order='F')
                common={'kind':'spatial_control','codec':name,'relative_tolerance':rel,'seed':seed,'base_variant':f'{name}_{rel:g}'}
                yield f'{name}_{rel:g}_global_{seed}',shuffled,{**common,'control':'global_permutation'}
                shifts=tuple(int(rng.integers(1,n)) for n in field.shape)
                yield f'{name}_{rel:g}_shift_{seed}',np.roll(delta,shifts,axis=(0,1,2)),{**common,'control':'periodic_translation','shifts':shifts}
                restricted=flat.copy();bf=bins.ravel(order='F')
                for i in range(17):
                    indices=np.flatnonzero(bf==i);restricted[indices]=rng.permutation(flat[indices])
                yield f'{name}_{rel:g}_stratified_{seed}',restricted.reshape(field.shape,order='F'),{**common,'control':'density_stratified_permutation'}

def run(mid,pilot):
    phase='pilot' if pilot else 'production'
    out=ROOT/'results'/phase/mid;out.mkdir(parents=True,exist_ok=True)
    outcomes=out/'outcomes.jsonl'
    done=set()
    if outcomes.exists():
        for line in outcomes.read_text().splitlines():
            r=json.loads(line);done.add((r['variant'],r['solver']))
    panel=json.loads((ROOT/'panel.json').read_text());case=next(x for x in panel if x['material_id']==mid)
    with np.load(ROOT/'data'/f'{mid}.npz',allow_pickle=False) as z:
        field=np.ascontiguousarray(z['grid'],dtype=np.float64);lattice=z['lattice'];frac=z['frac_coords'];symbols=[str(x) for x in z['symbols']]
    volume=float(abs(np.linalg.det(lattice)))
    dump(out/'runtime.json',{'start':utc(),'pid':os.getpid(),'python':sys.version,'case':case,'shape':field.shape,'n_atoms':len(symbols),'volume':volume,'total_electrons':float(field.mean()),'source_negative_fraction':float(np.mean(field<0)),'pbs_job_id':os.environ.get('PBS_JOBID'),'pbs_project':os.environ.get('PBS_ACCOUNT')})
    refs={}
    with tempfile.TemporaryDirectory(prefix=f'qoi_{mid}_',dir=ROOT/'temp') as td:
        work=pathlib.Path(td)
        if pilot:
            from validate_io_adapter import validate
            dump(out/'io_adapter_compatibility.json',validate(field,lattice,frac,symbols,work))
            from pymatgen.io.vasp.outputs import Chgcar
            p=work/'CHGCAR';write_chgcar(p,field,lattice,frac,symbols);read=Chgcar.from_file(p)
            check={'field_exact':bool(np.array_equal(read.data['total'],field)),'lattice_max_difference':float(np.max(np.abs(read.structure.lattice.matrix-lattice))),'frac_max_difference':float(np.max(np.abs(read.structure.frac_coords-frac))),'same_atom_order':[str(x) for x in read.structure.species]==symbols}
            dump(out/'input_roundtrip.json',check)
            if not(check['field_exact'] and check['same_atom_order'] and check['lattice_max_difference']<1e-12 and check['frac_max_difference']<1e-12): raise RuntimeError(f'Input roundtrip failed {check}')
        for solver in SOLVERS:
            logdir=out/'solver_logs'/'original';logdir.mkdir(parents=True,exist_ok=True)
            start=time.monotonic()
            try:
                q,labels,extra=solve(solver,field,lattice,frac,symbols,work/solver,logdir)
                refs[solver]=(q,labels)
                r={'material_id':mid,'variant':'original','solver':solver,'status':'SUCCESS','atom_charges':q.tolist(),**extra}
            except Exception:
                r={'material_id':mid,'variant':'original','solver':solver,'status':'SOLVER_FAILURE','error':traceback.format_exc()}
            r.update(elapsed_seconds=time.monotonic()-start,finished_at=utc())
            if ('original',solver) not in done: append(outcomes,r)
        dump(out/'baseline_disagreement.json',{a+'__'+b:float(np.max(np.abs(refs[a][0]-refs[b][0]))) for a,b in itertools.combinations(refs,2)})
        for variant,requested_delta,info in variants(field,work,pilot):
            recon=np.ascontiguousarray(field+requested_delta);delta=recon-field
            dg=diagnostics(field,delta,volume)
            dg['roundoff_delta_linf']=float(np.max(np.abs(delta-requested_delta)))
            for solver in SOLVERS:
                if (variant,solver) in done: continue
                r={'material_id':mid,'variant':variant,'solver':solver,'info':info,'diagnostics':dg,'start':utc()}
                start=time.monotonic()
                logdir=out/'solver_logs'/variant;logdir.mkdir(parents=True,exist_ok=True)
                if solver not in refs:
                    r.update(status='REFERENCE_FAILURE',elapsed_seconds=0);append(outcomes,r);continue
                try:
                    q,lab,extra=solve(solver,recon,lattice,frac,symbols,work/solver,logdir)
                    q0,lab0=refs[solver];dq=q-q0;err=float(np.max(np.abs(dq)))
                    precision=2e-6 if solver.startswith('henkelman') else 0.
                    verdicts={str(t):('PRINT_PRECISION_AMBIGUOUS' if abs(err-t)<=precision else 'PASS' if err<t else 'FAIL') for t in TAUS}
                    r.update(status='SUCCESS',atom_charges=q.tolist(),dq_atoms=dq.tolist(),max_charge_error_e=err,threshold_verdicts=verdicts,**extra)
                    if lab is not None:
                        qfixed=integrate(recon,lab0,len(symbols));di=qfixed-q0;dd=q-qfixed
                        migration=lab!=lab0
                        r['decomposition']={'integrand_atoms':di.tolist(),'domain_atoms':dd.tolist(),'closure_max_e':float(np.max(np.abs(di+dd-dq))),'migration_fraction':float(np.mean(migration)),'migrated_source_abs_charge_e':float(np.sum(np.abs(field[migration]))/field.size),'fixed_error_max_e':float(np.max(np.abs(di)))}
                except Exception:
                    r.update(status='SOLVER_FAILURE',error=traceback.format_exc())
                r.update(elapsed_seconds=time.monotonic()-start,finished_at=utc());append(outcomes,r)
                print(json.dumps({'material':mid,'variant':variant,'solver':solver,'status':r['status']}),flush=True)
                gc.collect()
    dump(out/'finished.json',{'finished_at':utc(),'phase':phase,'material_id':mid})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--material',required=True);p.add_argument('--pilot',action='store_true');args=p.parse_args()
    (ROOT/'temp').mkdir(exist_ok=True)
    run(args.material,args.pilot)
