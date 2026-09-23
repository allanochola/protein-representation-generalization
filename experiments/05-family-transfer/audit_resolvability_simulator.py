"""Synthetic-only correctness tests. No real allocation or statistical surface read."""
import ast
import itertools
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
import numpy as np
import resolvability_core as c
import resolvability_runtime as rt

EXP=Path(__file__).resolve().parent

def check(ok,msg):
    if not ok:raise RuntimeError(msg)

def synthetic():
    rows=[]
    for g in range(20):
        for i in range(1+g%3):rows.append((f'cn{g:02}_{i}',f'c{g:02}','calibration','negative'))
        if g%4==0:rows.append((f'cp{g:02}',f'c{g:02}','calibration','positive'))
    for g in range(20):
        rows.extend([(f'ep{g:02}',f'e{g:02}','evaluation','positive'),(f'en{g:02}',f'e{g:02}','evaluation','negative')])
    return c.make_design(rows)

def main():
    for phase in ('validation','surface'):
        path=EXP/f'run_resolvability_{phase}.py';tree=ast.parse(path.read_text())
        gates=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant)
            and any(isinstance(t,ast.Name) and t.id==f'RESOLVABILITY_{phase.upper()}_AUTHORIZED' for t in n.targets)]
        check(gates==[False],'Expected disabled phase')
        result=subprocess.run([sys.executable,'-B',str(path)],capture_output=True,text=True)
        check(result.returncode!=0 and 'not authorized' in result.stderr,'Disabled refusal failed')
    # Exact weighted 95th-percentile reference, including ties and duplicated groups.
    scores=np.array([0.,0.,1.,2.,3.,4.]);idx=np.array([0,0,1,1,1,2]);sizes=np.array([2,3,1])
    mult=np.array(list(itertools.product(range(3),repeat=3)),dtype=np.int64);mult=mult[mult.sum(axis=1)>0]
    got=c.thresholds(scores,idx,sizes,mult)
    for m,t in zip(mult,got):
        def exact(x):return sum((Fraction(int(m[g])*int(np.sum((idx==g)&(scores<=x))),int(sizes[g])) for g in range(3)),Fraction(0))
        want=next(x for x in np.unique(scores) if exact(x)>=Fraction(19*int(m.sum()),20))
        check(t==want,'Weighted quantile differs from exact rational result')
    check(c.thresholds(np.arange(20,dtype=float),np.arange(20),np.ones(20,dtype=int),np.ones((1,20),dtype=int))[0]==18,'Observed-score quantile rule')
    check(c.thresholds(np.zeros(20),np.arange(20),np.ones(20,dtype=int),np.ones((1,20),dtype=int))[0]==0,'Ties changed threshold')
    d=synthetic();cell={'allocation':'synthetic','b':.6,'rho':.3,'r':.5,'delta':.1}
    scores=c.generate(d,cell,c.stream('boundary',cell,0,'generation'))
    # Same stream, different computational batches must produce identical inference.
    a=c.infer(d,scores,c.stream('boundary',cell,0,'bootstrap'),49,batch=1)
    b=c.infer(d,scores,c.stream('boundary',cell,0,'bootstrap'),49,batch=17)
    check(a==b,'Batch size changes results')
    same=np.column_stack([scores[:,0],scores[:,0]])
    same_fit=c.infer(d,same,c.stream('boundary',cell,1,'bootstrap'),49)
    check(same_fit['estimate']==same_fit['lower']==same_fit['upper']==0,'Cross-arm pairing broken')
    # Explicit duplication: evaluate counts against an expanded-dataset reference.
    cm=np.array([[2 if i<10 else 0 for i in range(d['C'])]],dtype=int)
    em=np.array([[2 if i%2==0 else 0 for i in range(d['E'])]],dtype=int)
    ev=c.evaluate(d,scores,cm,em)
    for arm in (0,1):
        threshold=ev[arm]['threshold'][0]
        for label,count_key,mask in [('tpr','epp',d['ep']),('fpr','en',~d['ep'])]:
            means=[]
            for g,m in enumerate(em[0]):
                loc=mask & (d['eidx']==g)
                if np.any(loc):means.extend([float(np.mean(scores[d['ei'][loc],arm]>threshold))]*int(m))
            check(abs(ev[arm][label][0]-np.mean(means))<1e-14,'Group duplication/pairing mismatch')
    # Refit responds to calibration-group selection; evaluation is held fixed.
    controlled=np.zeros_like(scores);controlled[d['cn']]=d['cidx'][:,None]
    controlled[d['ei']]=10
    low=np.zeros((1,d['C']),int);high=low.copy();low[0,0]=d['C'];high[0,-1]=d['C']
    one=np.ones((1,d['E']),int)
    lo=c.evaluate(d,controlled,low,one);hi=c.evaluate(d,controlled,high,one)
    check(lo[0]['threshold'][0]!=hi[0]['threshold'][0] and lo[0]['tpr'][0]!=hi[0]['tpr'][0],'Calibration refit missing')
    # Group membership crosses labels without splitting; zero label support is defined failure.
    try:c.rates(np.array([1.]),np.array([0]),np.array([1,0]),np.array([[0,2]]),np.array([0.]))
    except c.UndefinedInference:pass
    else:raise RuntimeError('Undefined label sample silently accepted')
    check(c.make_design(list(reversed(d['records'])))['records']==d['records'],'Input order affects design')
    check(not np.array_equal(c.stream('validation_v1',cell,0,'generation').standard_normal(10),c.stream('surface',cell,0,'generation').standard_normal(10)),'Phase streams overlap')
    fixtures=c.boundary_checks(d,'synthetic')
    check(len(fixtures)==3 and all(x['passed'] for x in fixtures),'Boundary fixtures failed')
    # Synthetic firewall acceptance: one failed V1/V2/V3 prevents acceptance.
    spec={'allocations':['a','b'],'validation':{'comparator_tpr':.6,'within_group_latent_correlation':.3,
        'between_arm_latent_correlation':.5,'V1':{'effect':0.,'outer_replicates_per_allocation':10000,'type_I_bounds':[.03,.07]},
        'V2':{'effects':[.05,.1,.2],'outer_replicates_per_cell':2500,'coverage_bounds':[.93,.97]}}}
    summary={'cells':[],'boundaries':{x:fixtures for x in ['a','b']},'all_validation_passed':True}
    for v in rt.cells(spec,'validation'):
        summary['cells'].append({'cell':v,'metrics':{'requested_replicates':v['budget'],'null_rejection':{'rate':.05},'coverage':{'rate':.95}},'acceptance_passed':True})
    check(rt.validation_passes(summary,spec),'Synthetic passing archive blocked')
    summary['cells'][0]['metrics']['null_rejection']['rate']=.02
    summary['cells'][0]['acceptance_passed']=False;summary['all_validation_passed']=False
    check(not rt.validation_passes(summary,spec),'Failed V1 did not block surface')
    # V2 and V3 failures also block independently; no early pass through V1 alone.
    summary['cells'][0]['metrics']['null_rejection']['rate']=.05
    summary['cells'][0]['acceptance_passed']=True
    summary['cells'][1]['metrics']['coverage']['rate']=.90
    summary['cells'][1]['acceptance_passed']=False
    check(not rt.validation_passes(summary,spec),'Failed V2 did not block surface')
    summary['cells'][1]['metrics']['coverage']['rate']=.95
    summary['cells'][1]['acceptance_passed']=True
    summary['boundaries']['a']=[dict(r) for r in fixtures]
    summary['boundaries']['a'][0]['passed']=False
    check(not rt.validation_passes(summary,spec),'Failed V3 did not block surface')
    benchmark=EXP/'run_resolvability_benchmark.py'
    r=subprocess.run([sys.executable,'-B',str(benchmark)],capture_output=True,text=True)
    check(r.returncode!=0 and 'benchmark is not authorized' in r.stderr,'Benchmark refusal failed')
    # Missing committed validation archive must fail BEFORE allocation/design loading.
    old=rt.EXP
    with tempfile.TemporaryDirectory() as tmp:
        rt.EXP=Path(tmp)
        try:rt.verify_validation_archive({}, {})
        except RuntimeError:pass
        else:raise RuntimeError('Surface accepts missing validation archive')
        finally:rt.EXP=old
    for phase in ('validation','surface'):
        check(not (EXP/f'resolvability_{phase}_archive').exists(),'Unexpected real archive during disabled implementation audit')
    print('PASS — exact quantile/ties; nested refit; paired group multiplicities; batch/order invariance')
    print('PASS — synthetic boundary fixtures; undefined inference; validation/surface separation')
    print('Real geometry loaded: NO\nV1/V2 executed: NO\nResolvability surface generated: NO')

if __name__=='__main__':main()
