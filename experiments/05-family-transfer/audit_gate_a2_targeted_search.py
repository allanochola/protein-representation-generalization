"""Preparation audit: input derivation and synthetic parser checks only."""
import ast, importlib.util, json, subprocess, sys
from pathlib import Path
EXP=Path(__file__).resolve().parent
p=EXP/'run_gate_a2_targeted_search.py'
tree=ast.parse(p.read_text())
gates=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TARGETED_SEARCH_AUTHORIZED' for t in n.targets)]
if gates != [False]: raise RuntimeError('Expected uniquely disabled gate')
spec=importlib.util.spec_from_file_location('a2_search_audit_module',p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
snapshot=json.loads((EXP/'a2_targeted_search_snapshot.json').read_text())
files,q,t=m.derive(snapshot)
assert len(q)==687 and len(t)==9
assert m.validate_hits(b'',{'n'},{'p'})==[]
assert m.validate_hits(b'n\tp\t0.30\n',{'n'},{'p'})==[('n','p',0.3)]
for raw in (b'n\tp\tnan\n',b'n\tp\t30\n',b'x\tp\t0.3\n',b'n\tp\n'):
    try: m.validate_hits(raw,{'n'},{'p'})
    except (RuntimeError,ValueError): pass
    else: raise RuntimeError('Malformed hit accepted')
r=subprocess.run([sys.executable,str(p)],capture_output=True,text=True)
if r.returncode==0 or 'targeted search is not authorized' not in r.stderr: raise RuntimeError('Disabled refusal failed')
if m.OUTPUT.exists(): raise RuntimeError('Unexpected search archive')
print('PASS — disabled refusal, pinned input derivation, membership and synthetic hit parser')
print('Sequence search performed: NO')


# Independently verify per-pair lengths from the canonical query/target FASTAs.
def fasta_lengths(raw):
    lengths={}; current=None
    for line in raw.decode('ascii').splitlines():
        if line.startswith('>'):
            current=line[1:]
            if current in lengths: raise RuntimeError('Duplicate FASTA identifier')
            lengths[current]=0
        else:
            if current is None: raise RuntimeError('FASTA sequence before header')
            lengths[current]+=len(line)
    return lengths
import csv, io
nlen=fasta_lengths(files['negative_queries.fasta'])
plen=fasta_lengths(files['positive_targets.fasta'])
reader=csv.DictReader(io.StringIO(files['selected_pairs.tsv'].decode()),delimiter='\t')
if reader.fieldnames != ['negative_id','positive_id','sequence_cluster_sha256','negative_length','positive_length','shorter_sequence']:
    raise RuntimeError('Unexpected selected-pair schema')
pair_rows=list(reader)
if len(pair_rows)!=687: raise RuntimeError('Selected pair count changed')
for row in pair_rows:
    nl=nlen[row['negative_id']]; pl=plen[row['positive_id']]
    shorter='negative' if nl<pl else 'positive' if pl<nl else 'equal'
    if (int(row['negative_length']),int(row['positive_length']),row['shorter_sequence']) != (nl,pl,shorter):
        raise RuntimeError('Incorrect selected-pair length metadata')
expected=['--min-seq-id','0.30','-c','0.80','--cov-mode','1','-s','7.5','--threads','8',
          '--alignment-mode','3','--format-output','query,target,fident','-e','1e-3']
if snapshot['search_arguments']!=expected: raise RuntimeError('Search arguments changed')
if m.validate_hits(b'n\tp\t0.299\nn\tp\t0.30\n',{'n'},{'p'}) != [('n','p',0.299),('n','p',0.30)]:
    raise RuntimeError('Raw-hit preservation changed')
print('PASS — independent pair lengths, exact search arguments and raw-hit preservation')
