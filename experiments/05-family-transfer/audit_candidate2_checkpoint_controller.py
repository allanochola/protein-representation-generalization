"""Synthetic scheduling and local-Git transport tests; no production geometry."""
import ast,copy,importlib.util,json,subprocess,tempfile,types
from pathlib import Path
import candidate2_checkpoint_controller as cc
import resolvability_candidate2_core as core
import resolvability_candidate2_runtime as runtime

def reject(f):
    try:f()
    except (RuntimeError,KeyError,ValueError):return
    raise RuntimeError('Expected fail-closed rejection')
def main():
    source=Path(runtime.__file__).read_text()
    assert 'range(0,cell[\'budget\'],100)' in source
    assert 'controller.before_chunk()' in source and 'controller.after_chunk()' in source
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);experiment=root/'exp';experiment.mkdir();cp=root/'checkpoints'
        # Clone only for the audit: production chunk size remains 100; small fixture size is 2.
        test_source=source.replace("range(0,cell['budget'],100)","range(0,cell['budget'],2)").replace('min(start+100,','min(start+2,')
        test_source=test_source.replace("Path('/kaggle/working/exp05-resolvability-candidate2-checkpoints')",'TEST_CHECKPOINT_ROOT')
        ns={'__file__':str(experiment/'runtime.py'),'TEST_CHECKPOINT_ROOT':cp};exec(compile(test_source,'synthetic_runtime','exec'),ns)
        impl=experiment/'implementation.json';impl.write_text('{}');settings=experiment/'settings.json';settings.write_text('{}')
        runner=experiment/'run.py';runner.write_text('authorized test fixture')
        ns.update(EXP=experiment,IMPLEMENTATION=impl,SPEC=settings,git=lambda *a:b'' if a[0]=='status' else b'synthetic-head',
                  require_closed=lambda *a:None,read_committed=lambda p: b'CANDIDATE2_SURFACE_AUTHORIZED = False')
        rows=[]
        for side in ['calibration','evaluation']:
            for g in range(24):
                for label in ['negative','positive']:rows.append((f'{side}_{g}_{label}',f'{side}_{g}',side,label))
        design=core.make_design(rows);cell={'allocation':'synthetic','validation':'V1','budget':4,'b':.6,'rho':.3,'r':.5,'delta':0.}
        ns.update(contract=lambda:({'validation':{'V1':{'type_I_bounds':[0,1]}}},{}),designs=lambda:{'synthetic':design},cells=lambda *_:[cell],validation_passes=lambda *_:None)
        clock=[0.];exports=[]
        def export(files,binding,durations,session,kind):
            exports.append((copy.deepcopy(files),copy.deepcopy(binding),kind))
            if len(exports)==2:clock[0]=4000.
            return cc.digest(cc.canonical({k:cc.digest(v) for k,v in files.items()}))
        original_stream=core.stream;rngs={}
        def tracked_stream(phase,cell,index,purpose):
            r=original_stream(phase,cell,index,purpose)
            if phase=='validation_v1':rngs[(index,purpose)]=r
            return r
        core.stream=tracked_stream
        ctl=cc.Controller(export,120,60,clock=lambda:clock[0],chunk_size=2,baseline_seconds=0)
        try:ns['phase_run']('validation',str(runner),controller=ctl)
        except cc.SessionComplete:pass
        else:raise RuntimeError('Budget stop failed')
        assert len(exports)==2
        files,binding,kind=exports[-1];ledger=cc.validate_checkpoint(files,binding,[cell],2)
        assert len(ledger['chunks'])==1
        assert len([json.loads(x) for x in files[next(iter(ledger['chunks']))].splitlines()])==2
        reject(lambda:cc.validate_checkpoint(files,{**binding,'head':'wrong'},[cell],2))
        bad=dict(files);bad['orphan']=b'x';reject(lambda:cc.validate_checkpoint(bad,binding,[cell],2))
        name=next(iter(ledger['chunks']));bad=dict(files);bad[name]+=b'x';reject(lambda:cc.validate_checkpoint(bad,binding,[cell],2))
        bad=dict(files);del bad[name];reject(lambda:cc.validate_checkpoint(bad,binding,[cell],2))
        duplicate=[json.loads(x) for x in files[name].splitlines()];duplicate[1]['outer_index']=0
        bad=dict(files);bad[name]=b''.join((json.dumps(x)+'\n').encode() for x in duplicate)
        bl=copy.deepcopy(ledger);bl['chunks'][name]=cc.digest(bad[name]);bad['ledger.json']=cc.canonical(bl)
        reject(lambda:cc.validate_checkpoint(bad,binding,[cell],2))
        new=root/'restored';cc.publish_restore(new,files,binding,[cell],2)
        assert cc.read_files(new)==files
        reject(lambda:cc.publish_restore(new,files,binding,[cell],2))
        ns['TEST_CHECKPOINT_ROOT']=root/'new_session';destination=ns['TEST_CHECKPOINT_ROOT']/('validation-'+core.digest(cc.canonical(binding)))
        cc.publish_restore(destination,files,binding,[cell],2)
        def ok_export(f,b,d,s,k):return cc.digest(cc.canonical({n:cc.digest(v) for n,v in f.items()}))
        resumed=cc.Controller(ok_export,120,60,chunk_size=2,baseline_seconds=0)
        ns['phase_run']('validation',str(runner),resume=True,controller=resumed)
        out=experiment/'resolvability_candidate2_validation_archive'
        actual=[json.loads(x) for x in (out/'replicates/cell_000.jsonl').read_text().splitlines()]
        resumed_states={k:copy.deepcopy(v.bit_generator.state) for k,v in rngs.items()}
        reference=[core.outer(design,'validation_v1',cell,i,999) for i in range(4)]
        assert cc.canonical(actual)==cc.canonical(reference)
        assert resumed_states=={k:v.bit_generator.state for k,v in rngs.items()}
        core.stream=original_stream
        blocked=cc.Controller(lambda *_: (_ for _ in ()).throw(RuntimeError('failed export')),120,60,chunk_size=2)
        blocked.bind(new,binding,[cell]);reject(blocked.before_chunk);reject(blocked.export);reject(blocked.before_chunk)
        recovered=cc.Controller(ok_export,120,60,chunk_size=2);recovered.bind(new,binding,[cell]);recovered.export()
        # Real Git export and independent fetch, using a local bare repository only.
        bare=root/'remote.git';subprocess.run(['git','init','--bare',str(bare)],check=True,capture_output=True)
        seed=root/'seed';subprocess.run(['git','clone',str(bare),str(seed)],check=True,capture_output=True)
        def git(*a):return subprocess.run(['git',*a],cwd=seed,check=True,capture_output=True).stdout.decode().strip()
        git('checkout','-b','storage');git('config','user.name','Synthetic audit');git('config','user.email','synthetic@example.invalid')
        (seed/'storage_contract.json').write_bytes(cc.canonical({'production_checkpoint_upload_authorized':True,'production_execution_head':'synthetic-head'}))
        git('add','.');git('commit','-m','synthetic storage contract');git('push','origin','storage');parent=git('rev-parse','HEAD')
        transport=root/'transport';transport.mkdir();namespace='production/candidate2/validation/'+'a'*64
        store=cc.GitStorage(transport,str(bare),'storage',parent,None,'synthetic-head',namespace)
        receipt=store(files,binding,[],{},'checkpoint');assert receipt==cc.digest(cc.canonical({k:cc.digest(v) for k,v in files.items()}))
        stored,mb=cc.GitStorage.fetch(transport,str(bare),'storage',store.parent,namespace,0,None);assert stored==files
        git('pull','--ff-only','origin','storage');(seed/'external').write_text('move');git('add','.');git('commit','-m','external movement');git('push','origin','storage')
        reject(lambda:store(files,binding,[],{},'checkpoint'))
    print('PASS — actual synthetic production scheduling; verified pause/ack, bounded stop, restore/skip, exact inference results')
    print('PASS — corrupt/missing/orphan/duplicate/foreign rejection; failed-export blocking and export-only recovery')
    print('PASS — local bare-Git push and independent fetch; remote-parent movement rejected')
    print('Production geometry loaded: NO; production simulation executed: NO; GitHub uploads performed by audit: NO')
if __name__=='__main__':main()
