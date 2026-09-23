"""Synthetic allocation audit; never loads or allocates the real geometry."""
import ast, importlib.util, subprocess, sys
from pathlib import Path
EXP=Path(__file__).resolve().parent
p=EXP/'run_resolvability_allocation.py';source=p.read_text();tree=ast.parse(source)
gates=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)
       and any(isinstance(t,ast.Name) and t.id=='ALLOCATION_AUTHORIZED' for t in n.targets)]
if gates!=[False]:raise RuntimeError('Expected uniquely disabled allocation gate')
spec=importlib.util.spec_from_file_location('synthetic_allocation',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
g={'a':{'positive':1,'negative':4,'discovery_member_count':2},
   'b':{'positive':0,'negative':2,'discovery_member_count':0},
   'c':{'positive':0,'negative':2,'discovery_member_count':0},
   'd':{'positive':3,'negative':0,'discovery_member_count':0}}
a,dominant=m.allocate(g,'dominant_to_calibration')
check(dominant=='a' and a=={'a':'calibration','b':'evaluation','c':'evaluation','d':'evaluation'},'Calibration scenario')
b,_=m.allocate(g,'dominant_to_evaluation')
check(b=={'a':'evaluation','b':'calibration','c':'calibration','d':'evaluation'},'Evaluation scenario')
for scenario in m.SCENARIOS:
    check(m.allocate(g,scenario)==m.allocate(dict(reversed(list(g.items()))),scenario),'Insertion-order dependence')
    allocation,_=m.allocate(g,scenario);s=m.summarize(g,allocation)
    check(sum(s[x]['classes']['negative']['record_count'] for x in s)==8,'Negative conservation')
    check(sum(s[x]['classes']['positive']['record_count'] for x in s)==4,'Positive conservation')
check(m.summarize(g,a)['calibration']['classes']['positive']['records_in_discovery_overlapping_groups']==1,'Overlap reporting')
# Tie in largest groups chooses stable ID; subsequent equal-load tie goes calibration.
tie={h:{'positive':0,'negative':n,'discovery_member_count':0} for h,n in [('b',2),('a',2),('c',1)]}
z,d=m.allocate(tie,'dominant_to_calibration')
check(d=='a' and z['c']=='calibration','Deterministic dominant/load tie rule')
one={'x':{'positive':1,'negative':2,'discovery_member_count':0}}
z,_=m.allocate(one,'dominant_to_calibration');s=m.summarize(one,z)
check(s['evaluation']['classes']['negative']['largest_intersection_share'] is None,'Empty side handling')
for groups,scenario in [({},m.SCENARIOS[0]),({'x':{'positive':1,'negative':0}},m.SCENARIOS[0]),(g,'unknown')]:
    try:m.allocate(groups,scenario)
    except RuntimeError:pass
    else:raise RuntimeError('Malformed allocation accepted')
r=subprocess.run([sys.executable,'-B',str(p)],capture_output=True,text=True)
check(r.returncode!=0 and 'allocation is not authorized' in r.stderr,'Disabled refusal')
check(not m.OUTPUT.exists(),'Unexpected real allocation archive')
print('PASS — both placement scenarios, mixed-group conservation, deterministic ties, positive-only evaluation, empty-side handling')
print('PASS — disabled refusal; real geometry never loaded by audit')
