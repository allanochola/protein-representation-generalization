"""Candidate 2 synthetic profiling and checkpoint plumbing. Disabled."""
EXECUTION_PREP_AUTHORIZED = True

import hashlib
import json
from pathlib import Path

def need(ok,message):
    if not ok:raise RuntimeError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()

def portable_roundtrip(rt,c):
    """Exercise actual phase I/O with stub outer rows, exclusively in owned temp dirs."""
    import contextlib,io,tempfile,zipfile
    saved={k:getattr(rt,k) for k in ['EXP','REPO','SPEC','IMPLEMENTATION','Path','git','contract','designs','cells','read_committed']}
    old_outer=c.outer;old_boundary=c.boundary_checks
    fixture_cell={'allocation':'synthetic','b':.6,'rho':.3,'r':.5,'delta':0.,'budget':101,'validation':'V1'}
    fixture_spec={'allocations':['synthetic'],'validation':{'V1':{'type_I_bounds':[.03,.07]}}}
    fixtures=[{'fixture':name,'passed':True,'estimate':0.,'interval':[0.,0.],'details':{}}
              for name in ['perfect_separation','adjacent_negative_scores','tied_negative_scores']]
    class Interrupted(RuntimeError):pass
    try:
        with tempfile.TemporaryDirectory(prefix='candidate2_portability_fixture_') as tmp:
            root=Path(tmp);called=[];stop=[False];head=['fixture-execution-identity']
            def stub_outer(design,phase,cell,i,budget):
                if stop[0] and i==100:raise Interrupted('Deliberate interruption after first durable chunk')
                called.append(i)
                return dict(valid=False,outer_index=i,reason='SYNTHETIC_PLUMBING_STUB',coverage=False,null_rejection=False,positive_rejection=False)
            c.outer=stub_outer;c.boundary_checks=lambda d,a:fixtures
            rt.contract=lambda:(fixture_spec,{})
            rt.designs=lambda:{'synthetic':None}
            rt.cells=lambda spec,phase:[fixture_cell]
            def fake_git(*args):
                if args[0]=='status':return b''
                if args==('rev-parse','HEAD'):return head[0].encode()
                raise RuntimeError('Unexpected fixture git operation')
            rt.git=fake_git
            rt.read_committed=lambda path,expected=None: (b'CANDIDATE2_SURFACE_AUTHORIZED = False\n' if path.name=='run_resolvability_candidate2_surface.py' else b'OTHER_AUTHORIZED = False\n')
            def configure(name):
                session=root/name;exp=session/'experiments/05-family-transfer';exp.mkdir(parents=True)
                for filename in ['settings.json','implementation.json','runner.py']:(exp/filename).write_bytes(b'fixture identity\n')
                cp=session/'checkpoints'
                rt.EXP=exp;rt.REPO=session;rt.SPEC=exp/'settings.json';rt.IMPLEMENTATION=exp/'implementation.json'
                rt.Path=lambda value:cp if str(value)=='/kaggle/working/exp05-resolvability-candidate2-checkpoints' else Path(value)
                return exp,cp
            exp,cp=configure('uninterrupted')
            with contextlib.redirect_stdout(io.StringIO()):rt.phase_run('validation',exp/'runner.py')
            baseline={str(p.relative_to(exp/'resolvability_candidate2_validation_archive')):p.read_bytes()
                      for p in (exp/'resolvability_candidate2_validation_archive').rglob('*') if p.is_file()}
            need(called==list(range(101)),'Uninterrupted scheduler membership mismatch')
            exp,cp=configure('first_session');called.clear();stop[0]=True
            try:
                with contextlib.redirect_stdout(io.StringIO()):rt.phase_run('validation',exp/'runner.py')
            except Interrupted:pass
            else:raise RuntimeError('Fixture interruption not raised')
            need(called==list(range(100)),'Unexpected interrupted scheduler membership')
            dirs=list(cp.iterdir());need(len(dirs)==1,'Fixture checkpoint ambiguous');checkpoint=dirs[0]
            members={p.name:p.read_bytes() for p in checkpoint.iterdir()}
            need(set(members)=={'ledger.json','cell_000_00000.jsonl'},'Unexpected export members')
            manifest={name:digest(data) for name,data in members.items()}
            bundle=root/'export.zip'
            with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr('manifest.json',canonical(manifest))
                for name,data in members.items():z.writestr(name,data)
            # New session root has no access path to the old checkpoint tree.
            exp,cp=configure('restored_session');restored=cp/checkpoint.name;restored.mkdir(parents=True)
            with zipfile.ZipFile(bundle) as z:
                need(set(z.namelist())==set(manifest)|{'manifest.json'} and len(z.namelist())==3,'Unsafe/duplicate export member')
                exported=json.loads(z.read('manifest.json'));need(exported==manifest,'Export manifest changed')
                for name,h in exported.items():
                    need(Path(name).name==name,'Unsafe checkpoint path')
                    data=z.read(name);need(digest(data)==h,'Restore hash mismatch');(restored/name).write_bytes(data)
            stop[0]=False;called.clear()
            # Corruption must be rejected before any new outer work.
            chunk=restored/'cell_000_00000.jsonl';original=chunk.read_bytes();chunk.write_bytes(original+b'corrupt')
            try:rt.phase_run('validation',exp/'runner.py',resume=True)
            except RuntimeError as error:need('Checkpoint hash mismatch' in str(error),'Wrong corruption failure')
            else:raise RuntimeError('Corrupt checkpoint accepted')
            need(not called,'Work ran before corrupt-checkpoint rejection');chunk.write_bytes(original)
            head[0]='different-execution-identity'
            try:rt.phase_run('validation',exp/'runner.py',resume=True)
            except RuntimeError as error:need('No checkpoint exists to resume' in str(error),'Wrong identity failure')
            else:raise RuntimeError('Changed execution identity accepted')
            need(not called,'Work ran under changed execution identity');head[0]='fixture-execution-identity'
            with contextlib.redirect_stdout(io.StringIO()):rt.phase_run('validation',exp/'runner.py',resume=True)
            need(called==[100],'Restored scheduler reran completed work or skipped work')
            archive=exp/'resolvability_candidate2_validation_archive'
            actual={str(p.relative_to(archive)):p.read_bytes() for p in archive.rglob('*') if p.is_file()}
            need(actual==baseline,'Resumed outputs differ byte-for-byte from uninterrupted fixture')
            return {'fixture_only':True,'outer_inference_stubbed':True,'outer_slots':101,'durable_before_interrupt':100,
                    'computed_after_restore':[100],'all_archive_bytes_match':True,'corruption_rejected_before_work':True,
                    'changed_execution_identity_rejected_before_work':True,
                    'export_bundle_sha256':digest(bundle.read_bytes()),
                    'limitation':'Synthetic checkpoint plumbing in distinct local roots; not a live Kaggle reset or durable remote backup service.'}
    finally:
        c.outer=old_outer;c.boundary_checks=old_boundary
        for k,v in saved.items():setattr(rt,k,v)

def profile_fixture(c,name,cgroups,egroups,positives,cfirst,efirst):
    import cProfile,pstats,time
    rows=[]
    for side,total,groups,first in [('calibration',1771,cgroups,cfirst),('evaluation',1770,egroups,efirst)]:
        sizes=[first]+[(total-first)//(groups-1)+(i<(total-first)%(groups-1)) for i in range(groups-1)]
        for g,size in enumerate(sizes):
            rows.extend((f'{side}_n_{g:04d}_{i:04d}',f'{side}_g_{g:04d}',side,'negative') for i in range(size))
    rows.extend((f'evaluation_p_{i:04d}',f'evaluation_pg_{i:04d}','evaluation','positive') for i in range(positives))
    d=c.make_design(rows);cell={'allocation':name,'b':.6,'rho':.3,'r':.5,'delta':.1}
    # Profiling has its own namespace; no production or prior benchmark stream reused.
    scores=c.generate(d,cell,c.stream('execution_prep_profile',cell,0,'generation'))
    rng=c.stream('execution_prep_profile',cell,0,'bootstrap')
    profiler=cProfile.Profile();start=time.perf_counter();profiler.enable()
    result=c.infer(d,scores,rng,999)
    profiler.disable();elapsed=time.perf_counter()-start;del result,scores
    stats=pstats.Stats(profiler);records=[]
    for (path,line,function),(primitive,total,self_time,cumulative,callers) in stats.stats.items():
        records.append({'file':Path(path).name,'line':line,'function':function,'primitive_calls':primitive,
                        'total_calls':total,'self_seconds':self_time,'cumulative_seconds':cumulative})
    records.sort(key=lambda x:(-x['cumulative_seconds'],x['file'],x['line'],x['function']))
    return {'fixture':name,'record_count':len(rows),'calibration_groups':cgroups,'evaluation_groups':d['E'],
            'bootstrap_replicates':999,'outer_datasets':1,'profiled_elapsed_seconds':elapsed,'functions':records,
            'limitation':'cProfile adds overhead; cumulative times overlap and must not be summed.'}

def main():
    if not EXECUTION_PREP_AUTHORIZED:raise SystemExit('STOP: execution preparation is not authorized')
    import os,platform,subprocess,tempfile
    import numpy as np
    import resolvability_candidate2_core as c
    import resolvability_candidate2_runtime as rt
    exp=Path(__file__).resolve().parent;repo=exp.parents[1]
    def git(*args):return subprocess.run(['git',*args],cwd=repo,capture_output=True,check=True).stdout
    need(not git('status','--porcelain','--untracked-files=all'),'Clean checkout required')
    pin=json.loads((exp/'resolvability_candidate2_execution_prep_snapshot.json').read_text())
    for name,h in pin['input_sha256'].items():
        data=(exp/name).read_bytes();need(digest(data)==h,'Pinned source changed: '+name)
        need(data==git('show','HEAD:'+str((exp/name).relative_to(repo))),'Input differs from committed source')
    need(platform.python_version()==pin['python_version'] and np.__version__==pin['numpy_version'],'Environment mismatch')
    for prefix in ['run_resolvability_','run_resolvability_candidate2_']:
        rt.require_closed([prefix+phase+'.py' for phase in ['benchmark','validation','surface']])
    output=exp/'resolvability_candidate2_execution_prep_archive';need(not output.exists(),'Archive exists; no repeat')
    portability=portable_roundtrip(rt,c);print('PASS — synthetic checkpoint export/restore matches uninterrupted bytes',flush=True)
    profiles=[]
    for args in [('synthetic_dominant_calibration',276,280,155,469,7),('synthetic_dominant_evaluation',281,275,154,7,469)]:
        print('BEGIN — synthetic profile:',args[0],flush=True);profiles.append(profile_fixture(c,*args))
    report={'synthetic_only':True,'real_geometry_accessed':False,'confirmatory_outcomes_accessed':False,
            'production_validation_executed':False,'portability':portability,'profiles':profiles}
    with tempfile.TemporaryDirectory(prefix='.c2_execution_prep_',dir=exp) as tmp:
        stage=Path(tmp)/'archive';stage.mkdir();data=canonical(report);(stage/'report.json').write_bytes(data)
        provenance={'execution_head':git('rev-parse','HEAD').decode().strip(),'runner_sha256':digest(Path(__file__).read_bytes()),
                    'snapshot_sha256':digest((exp/'resolvability_candidate2_execution_prep_snapshot.json').read_bytes()),
                    'synthetic_only':True,'confirmatory_outcomes_accessed':False,'output_sha256':{'report.json':digest(data)}}
        (stage/'provenance.json').write_bytes(canonical(provenance));stage.rename(output)
    print('PASS — execution-preparation archive published; audit before interpretation',flush=True)

if __name__=='__main__':main()
