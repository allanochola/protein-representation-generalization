"""Controlled synthetic reset test 001. Disabled pending isolated authorization."""
RESET_TEST_AUTHORIZED = False

def main():
    if not RESET_TEST_AUTHORIZED:raise SystemExit('STOP: reset test is not authorized')
    import argparse,hashlib,json,platform,subprocess,sys
    from pathlib import Path
    import numpy as np
    import resolvability_candidate2_core as c
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output);c.require(not output.exists(),'Checkpoint exists; do not recompute')
    exp=Path(__file__).resolve().parent;repo=exp.parents[1]
    settings_path=exp/'candidate2_reset_test_001.json';settings=json.loads(settings_path.read_text())
    c.require(platform.python_version()=='3.12.13' and np.__version__=='2.0.2','Environment mismatch')
    for name,h in settings['input_sha256'].items():
        data=(exp/name).read_bytes();c.require(c.digest(data)==h,'Input hash mismatch: '+name)
        committed=subprocess.run(['git','show','HEAD:'+str((exp/name).relative_to(repo))],cwd=repo,check=True,capture_output=True).stdout
        c.require(data==committed,'Input not committed')
    rows=[]
    for side,total,groups,first in [('calibration',1771,276,469),('evaluation',1770,280,7)]:
        sizes=[first]+[(total-first)//(groups-1)+(i<(total-first)%(groups-1)) for i in range(groups-1)]
        for g,n in enumerate(sizes):rows.extend((f'{side}_n_{g:04d}_{i:04d}',f'{side}_g_{g:04d}',side,'negative') for i in range(n))
    rows.extend((f'evaluation_p_{i:04d}',f'evaluation_pg_{i:04d}','evaluation','positive') for i in range(155))
    design=c.make_design(rows)
    cell=dict(allocation='synthetic_reset_001',b=.6,rho=.3,r=.5,delta=.1)
    results=[]
    for i in range(6):
        generation=c.stream('controlled_reset_001',cell,i,'generation')
        bootstrap=c.stream('controlled_reset_001',cell,i,'bootstrap')
        scores=c.generate(design,cell,generation)
        fit=c.infer(design,scores,bootstrap,999)
        fit.update(valid=True,outer_index=i,**c.decisions(fit['lower'],fit['upper'],cell['delta']),error=fit['estimate']-cell['delta'])
        results.append({'outer_index':i,'inference':fit,'generation_final_rng_state':generation.bit_generator.state,
                        'bootstrap_final_rng_state':bootstrap.bit_generator.state})
        print(f'Synthetic reset test: completed {i+1}/6; inference values withheld',flush=True)
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,check=True,capture_output=True,text=True).stdout.strip()
    data={'schema':'exp05_candidate2_controlled_reset_checkpoint_v1','execution_head':head,
          'runner_sha256':c.digest(Path(__file__).read_bytes()),'settings_sha256':c.digest(settings_path.read_bytes()),
          'python_version':platform.python_version(),'numpy_version':np.__version__,
          'synthetic_only':True,'confirmatory_outcomes_accessed':False,'cell':cell,'fixture_records':len(rows),
          'completed_outer_indices':list(range(6)),'next_outer_index':6,'total_outer_slots':12,'results':results}
    payload=(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    temporary=output.with_suffix('.partial');c.require(not temporary.exists(),'Partial checkpoint exists')
    with temporary.open('xb') as handle:
        import os
        handle.write(payload);handle.flush();os.fsync(handle.fileno())
    temporary.rename(output)
    print('PASS — six actual synthetic inferences saved; stop before session reset',flush=True)

if __name__=='__main__':main()
