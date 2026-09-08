import pathlib,subprocess,numpy as np

def validate(field,lattice,frac,symbols,work):
    from run_study import write_chgcar,BADER
    base=work/'legacy_header';base.mkdir()
    p=base/'CHGCAR';write_chgcar(p,field,lattice,frac,symbols)
    lines=p.read_text().splitlines()
    for i in range(3):lines[2+i]=''.join(f'{x:13.6f}' for x in lattice[i])
    for i,row in enumerate(frac):lines[8+i]=''.join(f'{x:10.6f}' for x in row)
    p.write_text('\n'.join(lines)+'\n')
    results={}
    for mode in ['ongrid','neargrid']:
        charges=[]
        for label,binary in [('installed','/nfs/home/svu/junbotong/opt/bader-1.05/bader'),('io_adapter',str(BADER))]:
            log=base/f'{label}_{mode}.log'
            with log.open('w') as stream:
                rc=subprocess.call([binary,'CHGCAR','-b',mode,'-vac','0.001'],cwd=base,stdout=stream,stderr=subprocess.STDOUT)
            if rc:raise RuntimeError(f'Legacy IO comparison failed: {label}/{mode}: {log.read_text()}')
            rows=[line.split() for line in (base/'ACF.dat').read_text().splitlines()]
            q=np.array([float(row[4]) for row in rows if len(row)>=7 and row[0].isdigit()])
            if len(q)!=len(symbols):raise RuntimeError('Legacy IO comparison atom count mismatch')
            charges.append(q)
        difference=float(np.max(np.abs(charges[0]-charges[1])))
        results[mode]={'max_charge_difference_e':difference,'installed_charges':charges[0].tolist(),'adapter_charges':charges[1].tolist()}
        if difference>2e-6:raise RuntimeError(f'Legacy binary/source discrepancy: {results}')
    return {'description':'Both executables on the SAME legacy six-decimal geometry header and full-precision density; production uses the full-precision geometry. Algorithms unmodified, source reader only changed to free-format input.','results':results,'accepted':True}
