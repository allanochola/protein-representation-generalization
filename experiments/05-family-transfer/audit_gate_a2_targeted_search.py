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
