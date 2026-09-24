"""Shared phase I/O; no execution on import. Production gates live in each runner."""
import ast
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
import resolvability_candidate2_core as core

EXP=Path(__file__).resolve().parent
REPO=EXP.parents[1]
SPEC=EXP/'resolvability_candidate_2_settings.json'
IMPLEMENTATION=EXP/'resolvability_candidate2_implementation_snapshot.json'

def require(ok,msg):core.require(ok,msg)
def canonical(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def git(*args):return subprocess.run(['git',*args],cwd=REPO,check=True,capture_output=True).stdout

def read_committed(path,expected=None):
    data=path.read_bytes()
    require(not path.is_symlink(),'Symlink input prohibited')
    require(data==git('show','HEAD:'+str(path.relative_to(REPO))),'Input differs from committed bytes: '+path.name)
    if expected:require(core.digest(data)==expected,'SHA mismatch: '+path.name)
    return data

def normalized_runner(data):
    tree=ast.parse(data.decode())
    if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):tree.body.pop(0)
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id.endswith('_AUTHORIZED') for t in n.targets):
            require(isinstance(n.value,ast.Constant) and isinstance(n.value.value,bool),'Invalid gate')
            n.value=ast.Constant(False)
    return core.digest(ast.dump(tree,include_attributes=False).encode())

def require_closed(names):
    for name in names:
        tree=ast.parse(read_committed(EXP/name).decode())
        gates=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and
               isinstance(n.value,ast.Constant) and any(isinstance(t,ast.Name) and
               t.id.endswith('_AUTHORIZED') for t in n.targets)]
        require(gates==[False],'Other phase not uniquely closed: '+name)

def contract():
    implementation=json.loads(read_committed(IMPLEMENTATION))
    require(sys.version.split()[0]==implementation['python_version'],'Python version differs from pinned environment')
    require(np.__version__==implementation['numpy_version'],'NumPy version differs from pinned environment')
    for name,h in implementation['source_sha256'].items():read_committed(EXP/name,h)
    for name,h in implementation['runner_normalized_ast_sha256'].items():
        require(normalized_runner(read_committed(EXP/name))==h,'Runner behavior changed beyond authorization')
    candidate=json.loads(read_committed(SPEC,implementation['statistical_settings_sha256']))
    require(candidate['candidate']=='hierarchical_v2','Wrong candidate')
    read_committed(EXP/'RESOLVABILITY_CANDIDATE_2_SPECIFICATION.md',candidate['specification_sha256'])
    read_committed(EXP/'RESOLVABILITY_CANDIDATE_2_EXPOSURE_RECORD.md',candidate['exposure_record_sha256'])
    spec=candidate['inherited_settings']
    for path,h in spec['input_sha256'].items():read_committed(REPO/path,h)
    read_committed(EXP/'RESOLVABILITY_STATISTICAL_SPEC_001.md',spec['specification_sha256'])
    require(spec['bootstrap_replicates']==999,'Unexpected bootstrap budget')
    return spec,implementation

def designs():
    path=EXP/'resolvability_allocation_archive/assignments.tsv'
    reader=csv.DictReader(io.StringIO(read_committed(path).decode()),delimiter='\t')
    require(reader.fieldnames==['scenario','protein_id','class_name','sequence_cluster_sha256','partition'],'Allocation schema mismatch')
    data={}
    for row in reader:data.setdefault(row['scenario'],[]).append((row['protein_id'],row['sequence_cluster_sha256'],row['partition'],row['class_name']))
    require(set(data)=={'dominant_to_calibration','dominant_to_evaluation'},'Unexpected allocation scenarios')
    out={name:core.make_design(records) for name,records in data.items()}
    for name,d in out.items():
        require(len(d['records'])==3702 and int(d['positive'].sum())==161,'Full allocation counts mismatch')
        expected=155 if name=='dominant_to_calibration' else 154
        require(int(d['ep'].sum())==expected and len(d['cn'])==1771,'Retained evaluation/calibration counts mismatch')
    return out

def cells(spec,phase):
    result=[]
    if phase=='validation':
        v=spec['validation']
        for allocation in spec['allocations']:
            for validation,delta,budget in [('V1',v['V1']['effect'],v['V1']['outer_replicates_per_allocation'])]+[
                    ('V2',d,v['V2']['outer_replicates_per_cell']) for d in v['V2']['effects']]:
                result.append({'allocation':allocation,'b':v['comparator_tpr'],'rho':v['within_group_latent_correlation'],
                    'r':v['between_arm_latent_correlation'],'delta':delta,'budget':budget,'validation':validation})
    else:
        for allocation in spec['allocations']:
            for b in spec['comparator_population_tpr_grid']:
                for rho in spec['within_group_latent_correlation_grid']:
                    for r in spec['between_arm_latent_correlation_grid']:
                        for delta in spec['effect_grid']:
                            result.append({'allocation':allocation,'b':b,'rho':rho,'r':r,'delta':delta,
                                           'budget':spec['surface_outer_replicates_per_cell']})
    return result

def validation_passes(summary,spec):
    expected=cells(spec,'validation')
    require(len(summary['cells'])==len(expected),'Validation cell count mismatch')
    all_ok=True
    for saved,cell in zip(summary['cells'],expected):
        require(saved['cell']==cell,'Validation cell mismatch')
        metrics=saved['metrics'];require(metrics['requested_replicates']==cell['budget'],'Validation budget mismatch')
        key='null_rejection' if cell['validation']=='V1' else 'coverage'
        limits=spec['validation'][cell['validation']]['type_I_bounds' if key=='null_rejection' else 'coverage_bounds']
        okay=limits[0]<=metrics[key]['rate']<=limits[1]
        require(saved['acceptance_passed']==okay,'Inconsistent validation acceptance flag')
        all_ok=all_ok and okay
    require(set(summary['boundaries'])==set(spec['allocations']),'Boundary allocation coverage mismatch')
    for rows in summary['boundaries'].values():
        require([r['fixture'] for r in rows]==['perfect_separation','adjacent_negative_scores','tied_negative_scores'],'Boundary fixtures missing')
        all_ok=all_ok and all(r['passed'] is True for r in rows)
    require(summary['all_validation_passed'] is all_ok,'Validation aggregate mismatch')
    return all_ok

def verify_validation_archive(spec,implementation):
    archive=EXP/'resolvability_candidate2_validation_archive'
    require(archive.is_dir(),'Committed validation archive required before any surface generation')
    prov=json.loads(read_committed(archive/'provenance.json'))
    expected=set(prov['output_sha256'])|{'provenance.json'}
    actual={str(p.relative_to(archive)) for p in archive.rglob('*') if p.is_file()}
    require(actual==expected,'Validation archive membership mismatch')
    for relative,h in prov['output_sha256'].items():
        p=Path(relative);require(not p.is_absolute() and '..' not in p.parts,'Invalid archive path')
        read_committed(archive/p,h)
    require(prov.get('candidate')=='hierarchical_v2','Wrong candidate archive')
    require(prov['phase']=='validation' and prov['confirmatory_outcomes_accessed'] is False,'Invalid validation provenance')
    require(prov['implementation_snapshot_sha256']==core.digest(IMPLEMENTATION.read_bytes()),'Validation implementation mismatch')
    require(prov['statistical_settings_sha256']==core.digest(SPEC.read_bytes()),'Validation settings mismatch')
    summary=json.loads((archive/'summary.json').read_text())
    # Recompute the acceptance metrics from archived per-replicate records.
    for item in summary['cells']:
        rows=[json.loads(s) for s in (archive/item['replicates_file']).read_text().splitlines()]
        require([r['outer_index'] for r in rows]==list(range(item['cell']['budget'])),'Validation replicate order/budget mismatch')
        metrics=core.summarize(rows);metrics.pop('positive_rejection');metrics['power_status']='NOT_EVALUATED_VALIDATION_ONLY'
        require(metrics==item['metrics'],'Validation metrics do not reproduce')
    require(validation_passes(summary,spec),'V1-V3 have not all passed; surface blocked')
    return core.digest((archive/'provenance.json').read_bytes())

def durable_write(path,data):
    temp=path.with_name(path.name+'.partial')
    require(not temp.exists(),'Partial checkpoint exists; inspect rather than overwrite')
    with temp.open('xb') as handle:handle.write(data);handle.flush();os.fsync(handle.fileno())
    temp.rename(path)

def phase_run(phase,runner_file,resume=False,controller=None):
    if phase=='validation':require(controller is not None,'Validation requires the bounded checkpoint controller')
    require(phase in ('validation','surface'),'Invalid phase')
    require(not git('status','--porcelain','--untracked-files=all'),'Clean worktree required')
    spec,implementation=contract()
    require_closed(['run_resolvability_validation.py','run_resolvability_surface.py','run_resolvability_benchmark.py','run_resolvability_candidate2_benchmark.py'])
    other='surface' if phase=='validation' else 'validation'
    tree=ast.parse(read_committed(EXP/('run_resolvability_candidate2_'+other+'.py')).decode())
    other_gate=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)
                and any(isinstance(t,ast.Name) and t.id=='CANDIDATE2_'+other.upper()+'_AUTHORIZED' for t in n.targets)]
    require(other_gate==[False],'Other phase must be closed before execution')
    validation_identity=verify_validation_archive(spec,implementation) if phase=='surface' else None
    output=EXP/('resolvability_candidate2_'+phase+'_archive')
    require(not output.exists(),'Archive exists; refusing repeat execution')
    phase_cells=cells(spec,phase)
    binding={'candidate':'hierarchical_v2','phase':phase,'head':git('rev-parse','HEAD').decode().strip(),
        'runner_sha256':core.digest(Path(runner_file).read_bytes()),
        'implementation_snapshot_sha256':core.digest(IMPLEMENTATION.read_bytes()),
        'statistical_settings_sha256':core.digest(SPEC.read_bytes()),'validation_provenance_sha256':validation_identity}
    identity=core.digest(canonical(binding))
    checkpoint=Path('/kaggle/working/exp05-resolvability-candidate2-checkpoints')/(phase+'-'+identity)
    if checkpoint.exists():
        require(resume,'Checkpoint exists. Explicit --resume required; do not start again')
        ledger=json.loads((checkpoint/'ledger.json').read_text())
        require(ledger['binding']==binding,'Checkpoint binding mismatch')
        require({p.name for p in checkpoint.iterdir()}=={'ledger.json'}|set(ledger['chunks']),'Orphan/partial checkpoint: inspect without rerunning')
        for name,h in ledger['chunks'].items():require(core.digest((checkpoint/name).read_bytes())==h,'Checkpoint hash mismatch')
    else:
        require(not resume,'No checkpoint exists to resume')
        checkpoint.mkdir(parents=True);ledger={'binding':binding,'chunks':{}}
        durable_write(checkpoint/'ledger.json',canonical(ledger))
    if controller is not None:
        controller.bind(checkpoint,binding,phase_cells)
        controller.export()
    design=designs()
    summaries=[]
    for cell_index,cell in enumerate(phase_cells):
        phase_name='surface' if phase=='surface' else ('validation_v1' if cell['validation']=='V1' else 'validation_v2')
        for start in range(0,cell['budget'],100):
            end=min(start+100,cell['budget']);name=f'cell_{cell_index:03d}_{start:05d}.jsonl'
            if name not in ledger['chunks']:
                if controller is not None:controller.before_chunk()
                rows=[core.outer(design[cell['allocation']],phase_name,cell,i,999) for i in range(start,end)]
                payload=b''.join((json.dumps(r,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode() for r in rows)
                durable_write(checkpoint/name,payload)
                ledger['chunks'][name]=core.digest(payload)
                # Ledger replacement is atomic. Interrupted orphan chunks require inspection.
                temp=checkpoint/'ledger.next'
                with temp.open('xb') as f:f.write(canonical(ledger));f.flush();os.fsync(f.fileno())
                os.replace(temp,checkpoint/'ledger.json')
                if controller is not None:controller.after_chunk()
            print(f'{phase}: cell {cell_index+1}/{len(phase_cells)}, outer {end}/{cell["budget"]}; values withheld',flush=True)
        rows=[]
        for start in range(0,cell['budget'],100):
            rows.extend(json.loads(line) for line in (checkpoint/f'cell_{cell_index:03d}_{start:05d}.jsonl').read_text().splitlines())
        require([r['outer_index'] for r in rows]==list(range(cell['budget'])),'Checkpoint replicate membership mismatch')
        metrics=core.summarize(rows)
        if phase=='validation':
            metrics.pop('positive_rejection');metrics['power_status']='NOT_EVALUATED_VALIDATION_ONLY'
        item={'cell':cell,'metrics':metrics,'replicates_file':f'replicates/cell_{cell_index:03d}.jsonl'}
        if phase=='validation':
            key='null_rejection' if cell['validation']=='V1' else 'coverage'
            limits=spec['validation'][cell['validation']]['type_I_bounds' if key=='null_rejection' else 'coverage_bounds']
            item['acceptance_passed']=limits[0]<=metrics[key]['rate']<=limits[1]
        elif cell['delta']==.10:
            item['target_status']='INCONCLUSIVE_INFERENCE_FAILURE' if metrics['failure_count'] else (
                'CLEARS_TARGETS' if metrics['positive_rejection']['rate']>=.80 and metrics['median_half_width']<=.10 else 'DOES_NOT_CLEAR_TARGETS')
        summaries.append(item)
    summary={'phase':phase,'cells':summaries}
    if phase=='validation':
        summary['boundaries']={name:core.boundary_checks(d,name) for name,d in design.items()}
        summary['all_validation_passed']=all(i['acceptance_passed'] for i in summaries) and all(
            r['passed'] for rows in summary['boundaries'].values() for r in rows)
        validation_passes(summary,spec)
    else:
        summary['allocation_conclusions']={}
        for name in spec['allocations']:
            statuses=[i['target_status'] for i in summaries if i['cell']['allocation']==name and i['cell']['delta']==.10]
            require(len(statuses)==12,'Missing surface target cells')
            summary['allocation_conclusions'][name]=('INCONCLUSIVE_INFERENCE_FAILURE' if 'INCONCLUSIVE_INFERENCE_FAILURE' in statuses
                else 'ROBUSTLY_ADEQUATE_WITHIN_GRID' if all(s=='CLEARS_TARGETS' for s in statuses)
                else 'REGIME_DEPENDENT' if any(s=='CLEARS_TARGETS' for s in statuses) else 'NO_CELL_CLEARS_TARGETS_WITHIN_GRID')
    with tempfile.TemporaryDirectory(prefix='.resolvability_publish_',dir=EXP) as temp:
        stage=Path(temp)/'archive';(stage/'replicates').mkdir(parents=True)
        for i,cell in enumerate(phase_cells):
            with (stage/f'replicates/cell_{i:03d}.jsonl').open('wb') as target:
                for start in range(0,cell['budget'],100):
                    with (checkpoint/f'cell_{i:03d}_{start:05d}.jsonl').open('rb') as source:shutil.copyfileobj(source,target)
        (stage/'summary.json').write_bytes(canonical(summary))
        (stage/'checkpoint_ledger.json').write_bytes(canonical(ledger))
        prov={**binding,'confirmatory_metadata_accessed':True,'confirmatory_outcomes_accessed':False,
              'synthetic_scores_only':True,'output_sha256':{str(p.relative_to(stage)):core.digest(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file()}}
        (stage/'provenance.json').write_bytes(canonical(prov));stage.rename(output)
    if controller is not None:controller.final_archive(output)
    print('Archive published; independently audit and commit before interpreting results.',flush=True)
