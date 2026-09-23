"""A2 targeted sequence-search diagnostic. Authorized for one execution."""
import csv, hashlib, io, json, math, subprocess, tempfile
from collections import defaultdict
from pathlib import Path

TARGETED_SEARCH_AUTHORIZED = True
REPO = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
SNAPSHOT = EXP / 'a2_targeted_search_snapshot.json'
OUTPUT = EXP / 'a2_targeted_search_archive'

def require(ok, message):
    if not ok: raise RuntimeError(message)

def digest(data): return hashlib.sha256(data).hexdigest()

def derive(snapshot):
    data={}
    for key,spec in snapshot['inputs'].items():
        p=REPO/spec['path']; b=p.read_bytes()
        require(digest(b)==spec['sha256'],'Input SHA mismatch: '+key)
        committed=subprocess.run(['git','show','HEAD:'+spec['path']],cwd=REPO,check=True,capture_output=True).stdout
        require(b==committed,'Input differs from committed bytes: '+key)
        data[key]=b
    def table(key):
        return list(csv.DictReader(io.StringIO(data[key].decode()),delimiter='\t'))
    m=table('mapping'); meta={r['protein_id']:r for r in m}
    require(len(m)==len(meta)==3980,'Mapping count/uniqueness')
    part=table('partition'); groups=defaultdict(list); seen=set()
    for r in part:
        p=r['protein_id']; require(p in meta and p not in seen,'Partition membership'); seen.add(p)
        groups[r['sequence_cluster_sha256']].append(p)
    require(seen==set(meta),'Incomplete partition')
    pairs=[]; positives=set(); negatives=set()
    for h,ids in groups.items():
        require(digest('\n'.join(sorted(ids)).encode())==h,'Stable partition identity')
        ps=[p for p in ids if meta[p]['universe']=='confirmatory' and meta[p]['class_name']=='positive']
        ns=[p for p in ids if meta[p]['universe']=='confirmatory' and meta[p]['class_name']=='negative']
        if ps and ns:
            positives.update(ps); negatives.update(ns)
            pairs.extend((n,p,h) for n in ns for p in ps)
    require(len(positives)==9 and len(negatives)==687 and len(pairs)==687,'Frozen diagnostic membership mismatch')
    seq={}; current=None
    for line in data['fasta'].decode('ascii').splitlines():
        if line.startswith('>'):
            current=line[1:]; require(current not in seq,'Duplicate FASTA ID'); seq[current]=''
        else:
            require(current is not None,'FASTA sequence before header'); seq[current]+=line
    require(set(seq)==set(meta),'FASTA/mapping membership mismatch')
    for p,s in seq.items():
        require(len(s)==int(meta[p]['sequence_length']) and digest(s.encode())==meta[p]['sequence_sha256'],'FASTA sequence identity mismatch')
    def fasta(ids): return ''.join('>'+p+'\n'+seq[p]+'\n' for p in sorted(ids)).encode('ascii')
    files={'negative_queries.fasta':fasta(negatives),'positive_targets.fasta':fasta(positives),
           'selected_pairs.tsv':(
               'negative_id\tpositive_id\tsequence_cluster_sha256\tnegative_length\tpositive_length\tshorter_sequence\n'
               + ''.join(
                   '\t'.join((n, p, h, str(len(seq[n])), str(len(seq[p])),
                       'negative' if len(seq[n]) < len(seq[p]) else
                       'positive' if len(seq[p]) < len(seq[n]) else 'equal')) + '\n'
                   for n, p, h in sorted(pairs)
               )).encode()}
    if 'derived_sha256' in snapshot:
        require({n:digest(b) for n,b in files.items()}==snapshot['derived_sha256'],'Frozen search input identity mismatch')
    return files, negatives, positives

def validate_hits(raw, queries, targets):
    rows=[]
    for line in raw.decode('utf-8').splitlines():
        fields=line.split('\t'); require(len(fields)==3,'Malformed search row')
        q,t,f=fields; require(q in queries and t in targets,'Foreign search identifier')
        value=float(f); require(math.isfinite(value) and 0<=value<=1,'Invalid fident fraction')
        rows.append((q,t,value))
    return rows

def main():
    if not TARGETED_SEARCH_AUTHORIZED:
        raise SystemExit('STOP: targeted search is not authorized')
    require(not OUTPUT.exists(),'Output exists; refusing rerun')
    require(not subprocess.run(['git','status','--porcelain','--untracked-files=all'],cwd=REPO,check=True,capture_output=True).stdout,'Worktree not clean')
    snapshot=json.loads(SNAPSHOT.read_text()); files,queries,targets=derive(snapshot)
    binary=Path(snapshot['session_toolchain']['binary_path'])
    require(digest(binary.read_bytes())==snapshot['session_toolchain']['binary_sha256'],'Session binary identity mismatch')
    require(subprocess.run([str(binary),'version'],check=True,capture_output=True,text=True).stdout.strip()==snapshot['source_commit'],'Executable version mismatch')
    with tempfile.TemporaryDirectory(prefix='.a2_search_',dir=EXP) as tmp:
        root=Path(tmp); stage=root/'archive'; stage.mkdir()
        for n,b in files.items(): (stage/n).write_bytes(b)
        command=[str(binary),'easy-search',str(stage/'negative_queries.fasta'),str(stage/'positive_targets.fasta'),
                 str(stage/'raw_hits.tsv'),str(root/'scratch'),*snapshot['search_arguments']]
        with (stage/'stdout.log').open('wb') as out,(stage/'stderr.log').open('wb') as err:
            result=subprocess.run(command,cwd=root,stdout=out,stderr=err,check=False)
        valid=False; error=None
        if result.returncode==0 and (stage/'raw_hits.tsv').is_file():
            try: validate_hits((stage/'raw_hits.tsv').read_bytes(),queries,targets); valid=True
            except Exception as exc: error=str(exc)
        provenance={'command':command,'returncode':result.returncode,'valid_search_output':valid,'validation_error':error,
            'confirmatory_outcomes_accessed':False,'sequence_metadata_accessed':True,
            'snapshot_sha256':digest(SNAPSHOT.read_bytes()),'runner_sha256':digest(Path(__file__).read_bytes()),
            'execution_head':subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,check=True,capture_output=True,text=True).stdout.strip(),
            'interpretation':'Current-sequence targeted diagnostic; no historical filter-failure inference.',
            'qualification_rule':'Returned fident >= 0.30; classification follows independent archival.',
            'coverage_rule':'Negative query, positive target; cov-mode 1 and c=0.80 apply coverage to the positive target.',
            'null_result_limit':'No qualifying hit means not detected by this targeted diagnostic. It does not disprove an alignment or establish what the historical filter would have done.',
            'historical_evidence_limit':'Historical executable identity and cleaned_precursor.fasta bytes have not been recovered from inspected evidence; target database scope also differs.',
            'pair_length_scope':'Lengths describe asymmetry only; they do not establish alignment validity.',
            'output_sha256':{p.name:digest(p.read_bytes()) for p in sorted(stage.iterdir())}}
        (stage/'search_provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
        stage.rename(OUTPUT)
    if not valid: raise SystemExit('STOP: EXECUTION_OR_PROVENANCE_UNRESOLVED; archive retained; do not rerun')

if __name__=='__main__': main()
