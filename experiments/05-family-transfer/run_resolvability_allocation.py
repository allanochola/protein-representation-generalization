"""Formal Gate B allocation metadata. HARD-DISABLED pending separate authorization."""
import csv, hashlib, io, json, subprocess, tempfile
from collections import Counter, defaultdict
from pathlib import Path

ALLOCATION_AUTHORIZED = False
EXP=Path(__file__).resolve().parent
REPO=EXP.parents[1]
OUTPUT=EXP/'resolvability_allocation_archive'
SNAPSHOT=EXP/'resolvability_allocation_snapshot.json'
SPEC=EXP/'RESOLVABILITY_ALLOCATION_SPEC_001.md'
SCENARIOS=('dominant_to_calibration','dominant_to_evaluation')

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

def digest(b):return hashlib.sha256(b).hexdigest()

def git_bytes(*args):
    return subprocess.run(['git',*args],cwd=REPO,check=True,capture_output=True).stdout

def load_groups(snapshot):
    raw={}
    require(digest(SPEC.read_bytes())==snapshot['specification_sha256'],'Specification hash mismatch')
    for key,spec in snapshot['inputs'].items():
        path=REPO/spec['path'];data=path.read_bytes()
        require(digest(data)==spec['sha256'],'Input hash mismatch: '+key)
        require(data==git_bytes('show','HEAD:'+spec['path']),'Input not committed unchanged')
        raw[key]=data
    def table(key,columns):
        reader=csv.DictReader(io.StringIO(raw[key].decode()),delimiter='\t')
        require(reader.fieldnames==columns,'Unexpected '+key+' schema')
        rows=list(reader)
        require(all(set(r)==set(columns) and all(r[c] is not None for c in columns) for r in rows),'Malformed table')
        return rows
    rows=table('mapping',['protein_id','universe','class_name','accession','sequence_length','sequence_sha256'])
    meta={r['protein_id']:r for r in rows}
    require(len(rows)==len(meta)==3980,'Joint membership count/uniqueness')
    counts=Counter((r['universe'],r['class_name']) for r in rows)
    require(counts=={('discovery','positive'):139,('discovery','negative'):139,
                    ('confirmatory','positive'):161,('confirmatory','negative'):3541},'Unexpected label/universe counts')
    for r in rows:
        require(r['protein_id']==r['universe']+'::'+r['accession'],'Identifier namespace mismatch')
    partition=table('partition',['protein_id','sequence_cluster_sha256'])
    joint=defaultdict(list);seen=set()
    for r in partition:
        p=r['protein_id'];require(p in meta and p not in seen,'Foreign or repeated partition member')
        seen.add(p);joint[r['sequence_cluster_sha256']].append(p)
    require(seen==set(meta),'Incomplete partition')
    groups={}
    for h,members in joint.items():
        require(digest('\n'.join(sorted(members)).encode())==h,'Cluster hash mismatch')
        confirm=sorted(p for p in members if meta[p]['universe']=='confirmatory')
        if confirm:
            groups[h]={'members':confirm,
                'positive':sum(meta[p]['class_name']=='positive' for p in confirm),
                'negative':sum(meta[p]['class_name']=='negative' for p in confirm),
                'discovery_member_count':sum(meta[p]['universe']=='discovery' for p in members)}
    return groups,meta

def allocate(groups,scenario):
    require(scenario in SCENARIOS,'Unknown scenario')
    require(bool(groups),'Empty group universe')
    for h,g in groups.items():
        require(isinstance(h,str) and h and all(isinstance(g[k],int) and g[k]>=0 for k in ('positive','negative')),'Malformed group counts')
        require(g['positive']+g['negative']>0,'Empty group')
    order=sorted((h for h in groups if groups[h]['negative']>0),key=lambda h:(-groups[h]['negative'],h))
    require(bool(order),'No negative-bearing group')
    dominant=order[0]
    side='calibration' if scenario=='dominant_to_calibration' else 'evaluation'
    allocation={dominant:side};counts={'calibration':0,'evaluation':0}
    counts[side]=groups[dominant]['negative']
    for h in order[1:]:
        side='calibration' if counts['calibration']<=counts['evaluation'] else 'evaluation'
        allocation[h]=side;counts[side]+=groups[h]['negative']
    for h in sorted(groups):
        if h not in allocation:allocation[h]='evaluation'
    require(set(allocation)==set(groups),'Allocation incomplete')
    return allocation,dominant

def summarize(groups,allocation):
    out={}
    for side in ('calibration','evaluation'):
        subset={h:g for h,g in groups.items() if allocation[h]==side}
        classes={}
        for label in ('positive','negative'):
            sizes=[g[label] for g in subset.values() if g[label]>0];n=sum(sizes)
            classes[label]={'record_count':n,'bearing_group_count':len(sizes),
                'intersection_size_distribution':dict(sorted(Counter(sizes).items())),
                'largest_intersection_count':max(sizes,default=0),
                'largest_intersection_share':max(sizes)/n if n else None,
                'singleton_intersection_count':sizes.count(1),
                'records_in_discovery_overlapping_groups':sum(g[label] for g in subset.values() if g['discovery_member_count']>0)}
        out[side]={'group_count':len(subset),'mixed_label_group_count':sum(g['positive']>0 and g['negative']>0 for g in subset.values()),
            'discovery_overlapping_group_count':sum(g['discovery_member_count']>0 for g in subset.values()),'classes':classes}
    return out

def tsv(columns,rows):
    s=io.StringIO(newline='');writer=csv.writer(s,delimiter='\t',lineterminator='\n')
    writer.writerow(columns);writer.writerows(rows);return s.getvalue().encode()

def main():
    if not ALLOCATION_AUTHORIZED:raise SystemExit('STOP: allocation is not authorized')
    require(not OUTPUT.exists(),'Allocation archive exists; refusing rerun')
    require(not git_bytes('status','--porcelain','--untracked-files=all'),'Worktree must be clean')
    snapshot=json.loads(SNAPSHOT.read_text());groups,meta=load_groups(snapshot)
    assignments=[];group_rows=[];summary={}
    for scenario in SCENARIOS:
        allocation,dominant=allocate(groups,scenario)
        summary[scenario]={'dominant_group_id':dominant,'populations':summarize(groups,allocation),
            'interpretation':'Operational grouping; no effective-sample-size or admissibility claim.'}
        for h in sorted(groups):
            g=groups[h];side=allocation[h]
            group_rows.append((scenario,h,side,g['positive'],g['negative'],g['discovery_member_count']))
            assignments.extend((scenario,p,meta[p]['class_name'],h,side) for p in g['members'])
        # Do not silently repair a support failure; report it.
        summary[scenario]['support_conditions']={
            'calibration_has_negatives':summary[scenario]['populations']['calibration']['classes']['negative']['record_count']>0,
            'evaluation_has_negatives':summary[scenario]['populations']['evaluation']['classes']['negative']['record_count']>0,
            'evaluation_has_positives':summary[scenario]['populations']['evaluation']['classes']['positive']['record_count']>0}
    files={'assignments.tsv':tsv(['scenario','protein_id','class_name','sequence_cluster_sha256','partition'],sorted(assignments)),
        'group_allocations.tsv':tsv(['scenario','sequence_cluster_sha256','partition','positive_count','negative_count','discovery_member_count'],group_rows),
        'summary.json':(json.dumps(summary,sort_keys=True,indent=2)+'\n').encode()}
    provenance={'input_sha256':{k:s['sha256'] for k,s in snapshot['inputs'].items()},
        'snapshot_sha256':digest(SNAPSHOT.read_bytes()),'specification_sha256':digest(SPEC.read_bytes()),
        'runner_sha256':digest(Path(__file__).read_bytes()),'execution_head':git_bytes('rev-parse','HEAD').decode().strip(),
        'confirmatory_metadata_accessed':True,'confirmatory_outcomes_accessed':False,
        'simulation_executed':False,'output_sha256':{n:digest(b) for n,b in files.items()}}
    with tempfile.TemporaryDirectory(prefix='.allocation_',dir=EXP) as temp:
        stage=Path(temp)/'archive';stage.mkdir()
        for name,b in files.items():(stage/name).write_bytes(b)
        (stage/'allocation_provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
        stage.rename(OUTPUT)

if __name__=='__main__':main()
