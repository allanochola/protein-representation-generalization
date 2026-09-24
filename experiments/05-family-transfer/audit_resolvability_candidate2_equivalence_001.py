"""Synthetic exact-equivalence audit; no production geometry or performance surface."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import resolvability_candidate2_core as current

EXP=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise RuntimeError(msg)

def identical(a,b):
    if isinstance(a,np.ndarray):
        return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and a.tobytes()==b.tobytes()
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(identical(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(identical(x,y) for x,y in zip(a,b))
    if isinstance(a,float):return isinstance(b,float) and a.hex()==b.hex()
    return type(a)==type(b) and a==b

def main():
    reference_path=EXP/'resolvability_candidate2_core_reference_001.py'
    spec=importlib.util.spec_from_file_location('candidate2_reference_001',reference_path)
    ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
    # Only evaluation array construction may change. All other definitions must match.
    def structural(path):
        t=ast.parse(path.read_text());t.body=[n for n in t.body if not (isinstance(n,ast.FunctionDef) and n.name=='evaluate_draw')]
        return ast.dump(t,include_attributes=False)
    need(structural(reference_path)==structural(EXP/'resolvability_candidate2_core.py'),'Changes outside evaluate_draw')
    for name in ['run_resolvability_candidate2_benchmark.py','run_resolvability_candidate2_validation.py','run_resolvability_candidate2_surface.py','run_candidate2_execution_prep.py']:
        tree=ast.parse((EXP/name).read_text())
        gates=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and
               any(isinstance(t,ast.Name) and t.id.endswith('_AUTHORIZED') for t in n.targets)]
        need(gates==[False],'Execution gate open: '+name)
    total_draws=0
    for fixture in range(3):
        rows=[]
        for g in range(20):
            for i in range(1+(g%4 if fixture else 0)):
                rows.append((f'cn{g:02}_{i:02}',f'c{g:02}','calibration','negative'))
            for y,prefix in [('positive','p'),('negative','n')]:
                count=1+(g%3 if fixture else 0)
                if fixture==2 and g%5==0 and y=='positive':count=0
                if fixture==2 and g%5==1 and y=='negative':count=0
                for i in range(count):rows.append((f'e{prefix}{g:02}_{i:02}',f'e{g:02}','evaluation',y))
        d=current.make_design(rows);rd=ref.make_design(list(reversed(rows)))
        need(identical(d,rd),'Design mismatch')
        cell=dict(allocation=f'equivalence_{fixture}',b=.6,rho=.3,r=.5,delta=.1)
        a=current.stream('synthetic_equivalence',cell,0,'generation');b=ref.stream('synthetic_equivalence',cell,0,'generation')
        scores=current.generate(d,cell,a);other=ref.generate(rd,cell,b)
        need(identical(scores,other) and identical(a.bit_generator.state,b.bit_generator.state),'Generator mismatch')
        if fixture==1:scores=np.round(scores,0) # ties
        a=current.stream('synthetic_equivalence',cell,1,'bootstrap');b=ref.stream('synthetic_equivalence',cell,1,'bootstrap')
        for _ in range(80):
            draw=current.draw_hierarchy(d,current.prepare_strata(d),a)
            rdraw=ref.draw_hierarchy(rd,ref.prepare_strata(rd),b)
            need(identical(draw,rdraw) and identical(a.bit_generator.state,b.bit_generator.state),'Draw/RNG mismatch')
            # Capture all constructed local arrays as well as every evaluation output.
            captures=[];old_current=current.evaluate;old_ref=ref.evaluate
            def wrap(function):
                def captured(local,sc,cm,em):
                    captures.append((local,cm,em));return function(local,sc,cm,em)
                return captured
            current.evaluate=wrap(old_current);ref.evaluate=wrap(old_ref)
            try:left=current.evaluate_draw(d,scores,draw);right=ref.evaluate_draw(rd,scores,rdraw)
            finally:current.evaluate=old_current;ref.evaluate=old_ref
            need(identical(captures[0],captures[1]) and identical(left,right),'Arrays/thresholds/rates differ')
            total_draws+=1
        for batch in [1,17]:
            a=current.stream('synthetic_equivalence',cell,2,'bootstrap');b=ref.stream('synthetic_equivalence',cell,2,'bootstrap')
            left=current.infer(d,scores,a,99,batch=batch);right=ref.infer(rd,scores,b,99,batch=batch)
            need(identical(left,right) and identical(a.bit_generator.state,b.bit_generator.state),'Full inference/RNG mismatch')
        # Identical arms must retain zero difference, including endpoint non-rejection.
        pair=np.column_stack([scores[:,0],scores[:,0]])
        a=current.stream('synthetic_equivalence',cell,3,'bootstrap');b=ref.stream('synthetic_equivalence',cell,3,'bootstrap')
        left=current.infer(d,pair,a,99);right=ref.infer(rd,pair,b,99)
        need(identical(left,right) and left['lower']==left['upper']==0,'Pairing or endpoints changed')
        need(identical(a.bit_generator.state,b.bit_generator.state),'Identical-arm RNG mismatch')
        # Explicit absent-label draw returns the same declared failure type and message.
        draw=current.draw_hierarchy(d,current.prepare_strata(d),a)
        bad=(draw[0],[(np.array([],dtype=np.int64),o[1]) for o in draw[1]])
        failures=[]
        for module in [current,ref]:
            try:module.evaluate_draw(d,scores,bad)
            except module.UndefinedInference as exc:failures.append((type(exc).__name__,str(exc)))
            else:raise RuntimeError('Missing label accepted')
        need(failures[0]==failures[1],'Failure semantics changed')
    print('PASS — exact synthetic draw indices, constructed arrays, thresholds, intervals, outputs and final RNG state')
    print('PASS — singleton/mixed/unequal strata, ties, batching and absent-label behavior')
    print('Draws compared:',total_draws,'; full inference comparisons: 9')
    print('Production geometry loaded: NO\nProduction validation executed: NO\nRuntime benchmark executed: NO')

if __name__=='__main__':main()
