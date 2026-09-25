# Approved orchestration only. Each subprocess retains the frozen <=120-minute cap.
run_deadline=min(time.monotonic()+600*60,read_at+(remaining-30)*60)
completed_before=5900
launch_number=0
next_mode=mode
last_export=67
last_storage=storage_head
while True:
    available=remaining-(time.monotonic()-read_at)/60
    total_remaining=(run_deadline-time.monotonic())/60
    budget=min(120,total_remaining,available-30)
    # Avoid a no-progress launch when less than the observed chunk admission cost remains.
    durations=manifest['completed_chunk_seconds']
    need(all(isinstance(x,(int,float)) and x>=0 for x in durations),'Invalid recorded durations')
    admission_minutes=1.25*max([100*6.437716234999925]+durations)/60
    if budget<max(15,admission_minutes+1):
        print('STOP — insufficient aggregate budget for another complete chunk and export',flush=True)
        break
    need(remote(branch)==head and remote(storage)==last_storage,'Remote changed between launches')
    need(git('rev-parse','HEAD')==head and not git('status','--porcelain','--untracked-files=all'),'Experiment changed between launches')
    launch_number+=1
    logs=Path(tempfile.mkdtemp(prefix=f'candidate2_tenhour_{launch_number:02d}_',dir='/kaggle/working'))
    command=[sys.executable,'-B',str(uploader),'--storage-parent',last_storage,'--remaining-minutes',str(available),'--budget-minutes',str(budget),*next_mode]
    (logs/'launch.json').write_bytes(canonical({'execution_head':head,'storage_parent':last_storage,'export':last_export,
        'operation_receipt_commit':operation_commit,'launch_number':launch_number,'remaining_minutes_derived_from_initial_reading':available,
        'budget_minutes':budget,'automatic_retry':False}))
    stdout=logs/'stdout.log';stderr=logs/'stderr.log';childenv=os.environ.copy();childenv['PYTHONDONTWRITEBYTECODE']='1'
    print('BEGIN launch',launch_number,'budget minutes',round(budget,2),'logs',logs,flush=True)
    offset=0;pending=''
    def show_progress():
        global_unused=None
        # Reading complete lines only avoids dropping a checkpoint receipt split across writes.
        with stdout.open('r') as f:
            f.seek(progress_state['offset']);data=f.read();progress_state['offset']=f.tell()
        text=progress_state['pending']+data;lines=text.split('\n');progress_state['pending']=lines.pop()
        for line in lines:
            if line.startswith(('Transport recovery directory:','Durable export verified:','validation:','Stopped at a verified','Last verified storage commit:','Validation progress','Archive published;')):print(line,flush=True)
    progress_state={'offset':0,'pending':''}
    with stdout.open('wb') as out,stderr.open('wb') as err:
        process=subprocess.Popen(command,cwd=repo,env=childenv,stdout=out,stderr=err);started=time.monotonic()
        while True:
            try:code=process.wait(timeout=30);show_progress();break
            except subprocess.TimeoutExpired:
                show_progress();print('Launch',launch_number,'running',int(time.monotonic()-started),'seconds; values withheld',flush=True)
    print('END launch',launch_number,'exit',code,flush=True)
    need(code==0,'Launch failed. No automatic retry. Preserve local logs/checkpoints and inspect before reset.')
    text=stdout.read_text()
    receipts=re.findall(r'^Durable export verified: ([0-9a-f]{40}) export ([0-9]+) values withheld$',text,re.M)
    need(bool(receipts),'No verified export receipt; stop for inspection')
    next_storage,next_export=receipts[-1][0],int(receipts[-1][1])
    need(next_export>last_export and remote(storage)==next_storage,'Storage progress mismatch')
    # Independently fetch the exact next checkpoint; never infer progress from a heartbeat.
    run(['git','-c','credential.helper=','fetch','--depth','1',url,'refs/heads/'+storage],reader)
    need(run(['git','rev-parse','FETCH_HEAD'],reader).decode().strip()==next_storage,'Fetch identity mismatch')
    mb=blob(namespace+f'/exports/{next_export:06d}.json');manifest=json.loads(mb)
    need(manifest['sequence']==next_export and manifest['binding']==binding,'Export binding changed')
    need(sha(blob(namespace+f'/exports/{next_export-1:06d}.json'))==manifest['previous_manifest_sha256'],'Export chain changed')
    files={}
    for name,h in manifest['member_sha256'].items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts and re.fullmatch('[0-9a-f]{64}',h),'Invalid export member')
        data=blob(namespace+'/objects/'+h);need(sha(data)==h,'Export member hash mismatch');files[name]=data
    last_storage=next_storage;last_export=next_export
    if manifest['kind']=='archive':
        need((exp/'resolvability_candidate2_validation_archive').exists(),'Remote final archive missing locally')
        print('Validation archive published. STOP for independent audit; no statistical summary read.',flush=True)
        break
    need(manifest['kind']=='checkpoint','Unexpected export kind')
    ledger=json.loads(files['ledger.json']);need(ledger['binding']==binding,'Ledger binding changed')
    budgets=[10000,10000,2500,2500,2500,2500,2500,2500]
    slots=[(f'cell_{ci:03d}_{st:05d}.jsonl',st,min(st+100,b)) for ci,b in enumerate(budgets) for st in range(0,b,100)]
    names=sorted(ledger['chunks']);need(names==[x[0] for x in slots[:len(names)]],'Non-prefix/unknown checkpoint chunks')
    need(set(files)=={'ledger.json'}|set(names),'Checkpoint membership mismatch')
    count=0
    for name,st,en in slots[:len(names)]:
        need(sha(files[name])==ledger['chunks'][name],'Ledger member hash mismatch')
        rows=[json.loads(line) for line in files[name].splitlines()]
        need([r['outer_index'] for r in rows]==list(range(st,en)),'Slot continuity mismatch');count+=en-st
    need(count>completed_before,'No completed-slot progress; no repeated launch')
    need(checkpoint.is_dir() and not checkpoint.is_symlink(),'Local checkpoint missing')
    need(all(p.is_file() and not p.is_symlink() for p in checkpoint.iterdir()),'Invalid local checkpoint member')
    need({p.name:p.read_bytes() for p in checkpoint.iterdir()}==files,'Local/remote checkpoint mismatch')
    need('Stopped at a verified chunk boundary' in text,'Missing controlled-stop confirmation')
    completed_before=count;next_mode=['--resume-local']
    print('PASS — durable completed outer slots:',count,'; latest export:',last_export,flush=True)
print('── TEN-HOUR ORCHESTRATION STOPPED ──')
print('Experiment authorization HEAD:',head)
print('Last verified storage commit:',last_storage)
print('Last verified export:',last_export)
print('Last verified checkpoint slot count:',completed_before)
print('Surface authorized: NO; confirmatory outcomes accessed: NO')
print('Retain these identities. No automatic restart, error retry or statistical interpretation occurred.')
