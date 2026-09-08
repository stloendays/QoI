import csv, datetime, hashlib, json, os, pathlib, platform, subprocess, sys, time, traceback

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT / 'frozen_repo'
COMMIT = '893f931b3045b0b628329db81999c2f439d4e830'
MATERIALS = [('03','aflow-Cl1O12Pb5V3_ICSD_203074'),('09','aflow-B1C1F6K1_ICSD_1194'),('10','aflow-B6H2O13Sr3_ICSD_262541'),('16','aflow-Mo3Na1O16P3_ICSD_66877')]
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path, value): path.write_text(json.dumps(value, indent=2), encoding='utf-8')
def git(*args): return subprocess.check_output(['git', '-C', str(REPO), *args], text=True).strip()
def rows(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def main():
    assert git('rev-parse','HEAD') == COMMIT
    assert not git('diff','HEAD','--')
    assert sys.version_info[:3] == (3,12,14)
    os.environ['TEMP'] = os.environ['TMP'] = str(ROOT/'temp')
    os.environ['PYTHONUNBUFFERED'] = '1'
    prov = ROOT/'provenance'
    (prov/'pip_freeze.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True), encoding='utf-8')
    save(prov/'runtime.json', {'started_at':now(),'python':sys.version,'platform':platform.platform(),'scientific_commit':COMMIT,'requirements_sha256':hashlib.sha256((REPO/'validation/requirements-external-e2e.txt').read_bytes()).hexdigest(),'codecs':['zfp','sz3','sperr'],'timeout':None})
    subprocess.run([sys.executable,'-m','pip','check'],check=True)
    results=[]
    for slot,mid in MATERIALS:
        for attempt in range(1,4):
            out=ROOT/'results'/f'recovery_{slot}'/f'attempt_{attempt:02d}'
            out.mkdir(parents=True,exist_ok=False)
            log=ROOT/'logs'/f'recovery_{slot}_attempt_{attempt:02d}.log'
            command=[sys.executable,'validation/formal_external_e2e.py','--material-id',mid,'--codecs','zfp,sz3,sperr','--output-dir',str(out)]
            record={'slot':slot,'material_id':mid,'attempt':attempt,'start':now(),'command':command,'scientific_commit':COMMIT,'status':'RUNNING'}
            save(out/'execution.json',record)
            save(ROOT/'current_status.json',record)
            start=time.monotonic()
            with log.open('w',encoding='utf-8') as f:
                rc=subprocess.call(command,cwd=REPO,stdout=f,stderr=subprocess.STDOUT)
            record.update(end=now(),elapsed_seconds=time.monotonic()-start,exit_code=rc,status='FAILED')
            try:
                summary=json.loads((out/'summary.json').read_text())
                meta=json.loads((out/'run_metadata.json').read_text())
                success=rows(out/'formal_external_e2e_rows.csv')
                failures=rows(out/'formal_external_e2e_failures.csv')
                rowfail=rows(out/'formal_external_e2e_row_failures.csv')
                audit=rows(out/'material_audit.csv')
                assert meta['selected_materials']==[mid] and meta['codecs']==['zfp','sz3','sperr']
                assert all(r['material_id']==mid for r in success+failures+rowfail+audit)
                assert len(success)==summary['n_rows_retained'] and len(rowfail)==summary['n_row_failures']
                assert len(failures)==summary['n_material_failures']
                record.update(summary=summary,material_failures=failures,bader_row_failures=sum(r['category']=='bader_solver_failure' for r in rowfail))
                if rc==0 and summary['n_materials_complete']==1 and not failures and success:
                    assert {r['codec'] for r in success+rowfail}=={'ZFP','SZ3','SPERR'}
                    assert (out/f'{mid}_original_bader.json').is_file()
                    record['status']='SUCCESS'
            except Exception:
                record['verification_error']=traceback.format_exc()
            assert git('rev-parse','HEAD')==COMMIT and not git('diff','HEAD','--')
            save(out/'execution.json',record)
            results.append(record)
            save(ROOT/'recovery_status.json',results)
            save(ROOT/'current_status.json',record)
            if record['status']=='SUCCESS': break
            errors=' '.join(x.get('error','') for x in record.get('material_failures',[])).lower()
            transient=any(x in errors for x in ['http error 500','timed out','connection reset','connection aborted','temporary failure'])
            if slot not in ('03','09') or not transient: break
    save(ROOT/'finished.json',{'finished_at':now(),'results':results})

if __name__=='__main__':
    try: main()
    except BaseException:
        save(ROOT/'controller_failure.json',{'time':now(),'error':traceback.format_exc()})
        raise
