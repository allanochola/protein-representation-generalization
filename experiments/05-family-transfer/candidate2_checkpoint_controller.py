"""Bounded checkpoint controller; importing this module performs no I/O."""
import hashlib,json,os,re,subprocess,tempfile,time
from pathlib import Path

def require(ok,message):
    if not ok:raise RuntimeError(message)
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
class SessionComplete(Exception):pass

def validate_checkpoint(files,binding,cells,chunk_size=100):
    require('ledger.json' in files,'Missing ledger')
    ledger=json.loads(files['ledger.json'])
    require(set(ledger)=={'binding','chunks'} and ledger['binding']==binding,'Checkpoint binding/schema mismatch')
    require(set(files)=={'ledger.json'}|set(ledger['chunks']),'Orphan/missing checkpoint member')
    expected=[]
    for ci,cell in enumerate(cells):
        for start in range(0,cell['budget'],chunk_size):
            expected.append((f'cell_{ci:03d}_{start:05d}.jsonl',start,min(start+chunk_size,cell['budget'])))
    names=sorted(ledger['chunks'])
    require(names==[r[0] for r in expected[:len(names)]],'Checkpoint chunks are not an exact ordered prefix')
    for name,start,end in expected[:len(names)]:
        require(digest(files[name])==ledger['chunks'][name],'Corrupt chunk')
        rows=[json.loads(line) for line in files[name].splitlines()]
        require([r['outer_index'] for r in rows]==list(range(start,end)),'Wrong, missing or duplicate outer slots')
    return ledger

def read_files(path):
    require(path.is_dir() and not path.is_symlink(),'Invalid checkpoint directory')
    require(all(p.is_file() and not p.is_symlink() for p in path.iterdir()),'Non-file checkpoint member')
    return {p.name:p.read_bytes() for p in path.iterdir()}

def publish_restore(destination,files,binding,cells,chunk_size=100):
    validate_checkpoint(files,binding,cells,chunk_size)
    require(not destination.exists(),'Restore destination exists; inspect without overwrite')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.restore_',dir=destination.parent) as tmp:
        stage=Path(tmp)/'checkpoint';stage.mkdir()
        for name,b in files.items():
            require(Path(name).name==name,'Unsafe checkpoint path')
            with (stage/name).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
        validate_checkpoint(read_files(stage),binding,cells,chunk_size);stage.rename(destination)

class Controller:
    def __init__(self,exporter,remaining_minutes,budget_minutes,observed_seconds=(),clock=time.monotonic,chunk_size=100,baseline_seconds=6.437716234999925):
        require(0<budget_minutes<=120 and remaining_minutes>=budget_minutes+30,'Invalid fresh session allowance/budget')
        require(all(x>=0 for x in observed_seconds),'Invalid timing history')
        self.exporter=exporter;self.clock=clock;self.started=clock();self.deadline=self.started+budget_minutes*60
        self.chunk_size=chunk_size;self.baseline=baseline_seconds*chunk_size;self.durations=list(observed_seconds)
        self.ack=None;self.inflight=False;self.bound=False
        self.session={'remaining_minutes_user_reported':remaining_minutes,'budget_minutes':budget_minutes,'cpu_quota':'NOT_DISPLAYED'}
    def bind(self,path,binding,cells):
        self.path=path;self.binding=binding;self.cells=cells;self.bound=True
        validate_checkpoint(read_files(path),binding,cells,self.chunk_size)
    def export(self):
        require(self.bound and not self.inflight,'Cannot export during inference')
        files=read_files(self.path);validate_checkpoint(files,self.binding,self.cells,self.chunk_size)
        receipt=self.exporter(files,self.binding,self.durations,self.session,'checkpoint')
        require(receipt==digest(canonical({k:digest(v) for k,v in files.items()})),'Export acknowledgement mismatch')
        self.ack=digest(files['ledger.json'])
    def before_chunk(self):
        require(self.bound and not self.inflight,'Controller state violation')
        require(self.ack==digest((self.path/'ledger.json').read_bytes()),'No verified export acknowledgement for current ledger')
        if self.clock()+1.25*max([self.baseline]+self.durations)>self.deadline:raise SessionComplete('Stopped at a verified chunk boundary')
        self.chunk_started=self.clock();self.inflight=True
    def after_chunk(self):
        require(self.inflight,'No chunk in flight');self.durations.append(self.clock()-self.chunk_started);self.inflight=False
        self.export()
    def final_archive(self,path):
        require(not self.inflight,'Inference in flight')
        files={str(p.relative_to(path)):p.read_bytes() for p in path.rglob('*') if p.is_file()}
        receipt=self.exporter(files,self.binding,self.durations,self.session,'archive')
        require(receipt==digest(canonical({k:digest(v) for k,v in files.items()})),'Final archive acknowledgement mismatch')

class GitStorage:
    def __init__(self,root,url,branch,expected_parent,env,authorization_head,namespace):
        require(re.fullmatch('[0-9a-f]{40}',expected_parent) is not None,'Expected storage commit required')
        self.root=Path(root);self.url=url;self.branch=branch;self.parent=expected_parent;self.env=env;self.auth=authorization_head
        self.namespace=namespace;self.previous=None;self.serial=0
        self.work=self.root/'writer';self.run(['git','-c','credential.helper=','clone','--single-branch','--branch',branch,url,str(self.work)],self.root)
        require(self.git('rev-parse','HEAD')==expected_parent,'Storage parent moved')
        self.git('config','user.name','Allan Ochola');self.git('config','user.email','allanochola4@gmail.com')
        contract=json.loads((self.work/'storage_contract.json').read_bytes())
        require(contract.get('production_checkpoint_upload_authorized') is True,'Production storage adoption has not been separately authorized')
        require(contract.get('production_execution_head')==authorization_head,'Storage authorization identity mismatch')
        folder=self.work/namespace/'exports'
        if folder.exists():
            exports=sorted(folder.glob('*.json'));require([p.name for p in exports]==[f'{i:06d}.json' for i in range(len(exports))],'Non-contiguous exports')
            if exports:self.serial=len(exports);self.previous=digest(exports[-1].read_bytes())
    def run(self,args,cwd):return subprocess.run(args,cwd=cwd,env=self.env,check=True,capture_output=True).stdout
    def git(self,*args):return self.run(['git',*args],self.work).decode().strip()
    def remote(self):
        lines=self.run(['git','-c','credential.helper=','ls-remote',self.url,'refs/heads/'+self.branch],self.root).decode().splitlines()
        require(len(lines)==1,'Remote branch ambiguity');return lines[0].split()[0]
    def __call__(self,files,binding,durations,session,kind):
        receipt_path=self.root/f'pending_export_{self.serial:06d}.json'
        receipt_path.write_bytes(canonical({'binding':binding,'member_sha256':{k:digest(v) for k,v in files.items()},'completed_chunk_seconds':durations}))
        require(self.remote()==self.parent,'Remote parent moved; no inference retry')
        require(not self.git('status','--porcelain','--untracked-files=all'),'Storage worktree dirty; recover export only')
        ns=self.work/self.namespace;objects=ns/'objects';objects.mkdir(parents=True,exist_ok=True)
        hashes={name:digest(b) for name,b in files.items()}
        for name,b in files.items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Unsafe member path')
            p=objects/hashes[name]
            if p.exists():require(p.read_bytes()==b,'Content-address collision')
            else:p.write_bytes(b)
        manifest={'schema':'candidate2_production_export_v1','kind':kind,'binding':binding,'sequence':self.serial,
                  'previous_manifest_sha256':self.previous,'member_sha256':hashes,'completed_chunk_seconds':durations,'session':session}
        exports=ns/'exports';exports.mkdir(exist_ok=True);m=exports/f'{self.serial:06d}.json';require(not m.exists(),'Export would overwrite history');m.write_bytes(canonical(manifest))
        self.git('add','--',self.namespace)
        require(all(p.startswith(self.namespace+'/') for p in self.git('diff','--cached','--name-only').splitlines()),'Storage mutation outside execution namespace')
        self.git('commit','-m',f'Checkpoint Candidate 2 {kind} export {self.serial:06d}')
        head=self.git('rev-parse','HEAD');require(self.remote()==self.parent,'Remote moved; retain local storage checkout')
        self.git('-c','credential.helper=','push',self.url,'HEAD:refs/heads/'+self.branch)
        require(self.remote()==head,'Push verification failed; inference remains paused')
        fetched,fb=self.fetch(self.root,self.url,self.branch,head,self.namespace,self.serial,self.env)
        require(fb==canonical(manifest) and fetched==files,'Independent fetch mismatch')
        self.parent=head;self.previous=digest(fb);self.serial+=1
        print('Durable export verified:',head,'export',self.serial-1,'values withheld',flush=True)
        return digest(canonical(hashes))
    @staticmethod
    def fetch(root,url,branch,commit,namespace,number,env):
        require(re.fullmatch('[0-9a-f]{40}',commit) is not None,'Invalid storage commit')
        require(re.fullmatch(r'production/candidate2/validation/[0-9a-f]{64}',namespace) is not None,'Invalid storage namespace')
        with tempfile.TemporaryDirectory(prefix='independent_fetch_',dir=root) as tmp:
            def run(args):return subprocess.run(args,cwd=tmp,env=env,check=True,capture_output=True).stdout
            run(['git','init']);run(['git','-c','credential.helper=','fetch','--depth','1',url,'refs/heads/'+branch])
            require(run(['git','rev-parse','FETCH_HEAD']).decode().strip()==commit,'Fetched branch is not pinned storage commit')
            def blob(path):return run(['git','show','FETCH_HEAD:'+path])
            mb=blob(namespace+f'/exports/{number:06d}.json');m=json.loads(mb)
            require(m['sequence']==number,'Export sequence mismatch')
            if number:
                previous=blob(namespace+f'/exports/{number-1:06d}.json');require(digest(previous)==m['previous_manifest_sha256'],'Export chain mismatch')
            else:require(m['previous_manifest_sha256'] is None,'First export has parent')
            files={}
            for name,h in m['member_sha256'].items():
                require(re.fullmatch('[0-9a-f]{64}',h) is not None,'Invalid member hash')
                b=blob(namespace+'/objects/'+h);require(digest(b)==h,'Corrupt remote member');files[name]=b
            return files,mb

def launch(runner_file):
    import argparse,ast,platform
    parser=argparse.ArgumentParser()
    parser.add_argument('--storage-parent',required=True)
    parser.add_argument('--remaining-minutes',type=float,required=True)
    parser.add_argument('--budget-minutes',type=float,required=True)
    parser.add_argument('--restore-export',type=int)
    parser.add_argument('--export-only',action='store_true')
    parser.add_argument('--resume-local',action='store_true')
    parser.add_argument('--timing-receipt',type=Path)
    args=parser.parse_args()
    require(0<args.budget_minutes<=120 and args.remaining_minutes>=args.budget_minutes+30,'Fresh session allowance must exceed chosen budget by 30 minutes')
    from kaggle_secrets import UserSecretsClient
    exp=Path(runner_file).resolve().parent;repo=exp.parents[1]
    def git(*a):return subprocess.run(['git',*a],cwd=repo,check=True,capture_output=True).stdout
    require(not git('status','--porcelain','--untracked-files=all'),'Worktree not clean')
    validation=exp/'run_resolvability_candidate2_validation.py'
    values=[n.value.value for n in ast.parse(validation.read_bytes()).body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)
            and any(isinstance(t,ast.Name) and t.id=='CANDIDATE2_VALIDATION_AUTHORIZED' for t in n.targets)]
    require(values==[True],'Validation is not separately authorized')
    import resolvability_candidate2_runtime as runtime
    # contract() checks environment, committed sources and normalized phase gates before execution.
    spec,implementation=runtime.contract()
    binding={'candidate':'hierarchical_v2','phase':'validation','head':git('rev-parse','HEAD').decode().strip(),
        'runner_sha256':digest(validation.read_bytes()),'implementation_snapshot_sha256':digest(runtime.IMPLEMENTATION.read_bytes()),
        'statistical_settings_sha256':digest(runtime.SPEC.read_bytes()),'validation_provenance_sha256':None}
    # Environment and session-controller behavior are transitively pinned by the implementation snapshot.
    require(platform.python_version()==implementation['python_version'],'Python identity mismatch')
    identity=digest(canonical(binding));namespace='production/candidate2/validation/'+identity
    path=Path('/kaggle/working/exp05-resolvability-candidate2-checkpoints')/('validation-'+identity)
    phase_cells=runtime.cells(spec,'validation')
    token=UserSecretsClient().get_secret('GITHUB_PAT');require(bool(token),'GITHUB_PAT unavailable')
    # Persistent local workspace retains failed commits for export-only recovery.
    root=Path(tempfile.mkdtemp(prefix='candidate2_checkpoint_transport_',dir='/kaggle/working'))
    print('Transport recovery directory:',root,flush=True)
    with tempfile.TemporaryDirectory(prefix='checkpoint_auth_') as auth:
        ask=Path(auth)/'askpass.sh';ask.write_text('#!/bin/sh\ncase "$1" in\n*Username*) printf "%s\\n" x-access-token;;\n*) printf "%s\\n" "$EXP05_PUSH_TOKEN";;\nesac\n');ask.chmod(0o700)
        env=os.environ.copy();env.update(GIT_ASKPASS=str(ask),EXP05_PUSH_TOKEN=token,GIT_TERMINAL_PROMPT='0')
        try:
            url='https://github.com/allanochola/protein-representation-generalization.git';branch='exp05-candidate2-checkpoint-storage'
            durations=[]
            if args.restore_export is not None:
                require(args.restore_export>=0,'Invalid export number')
                files,mb=GitStorage.fetch(root,url,branch,args.storage_parent,namespace,args.restore_export,env)
                m=json.loads(mb);require(m['kind']=='checkpoint' and m['binding']==binding,'Foreign export')
                publish_restore(path,files,binding,phase_cells);durations=m['completed_chunk_seconds']
            elif path.exists():
                require(args.export_only or args.resume_local,'Existing local state requires explicit resume-local or export-only')
                validate_checkpoint(read_files(path),binding,phase_cells)
            store=GitStorage(root,url,branch,args.storage_parent,env,binding['head'],namespace)
            if args.resume_local:
                require(args.restore_export is None and path.exists() and store.serial>0,'Invalid local resume')
                prior,mb=GitStorage.fetch(root,url,branch,args.storage_parent,namespace,store.serial-1,env)
                m=json.loads(mb);require(m['kind']=='checkpoint' and m['binding']==binding,'Local resume identity mismatch')
                require(prior==read_files(path),'Local state differs from last verified export; use export-only recovery')
                durations=m['completed_chunk_seconds']
            if args.export_only:
                require(args.timing_receipt is not None,'Export-only requires the retained pending-export timing receipt')
                receipt=json.loads(args.timing_receipt.read_bytes())
                require(receipt['binding']==binding and receipt['member_sha256']=={k:digest(v) for k,v in read_files(path).items()},'Timing receipt does not match local checkpoint')
                durations=receipt['completed_chunk_seconds']
            if store.serial and args.restore_export is not None:require(args.restore_export==store.serial-1,'Restore must use latest pinned export')
            if store.serial and args.restore_export is None and not args.export_only and not args.resume_local:raise RuntimeError('Remote execution exists; explicit restoration required')
            ctl=Controller(store,args.remaining_minutes,args.budget_minutes,durations)
            if args.export_only:
                require(path.exists(),'No local checkpoint to export');ctl.bind(path,binding,phase_cells);ctl.export()
                print('Export-only recovery complete. No inference executed.');return
            try:runtime.phase_run('validation',str(validation),resume=path.exists(),controller=ctl)
            except SessionComplete as exc:print(str(exc),flush=True)
            print('Last verified storage commit:',store.parent)
            print('Validation progress values withheld; surface remains disabled.',flush=True)
        finally:env.pop('EXP05_PUSH_TOKEN',None);token=None
