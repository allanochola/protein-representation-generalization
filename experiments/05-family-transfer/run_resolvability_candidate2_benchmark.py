"""Synthetic runtime benchmark. HARD-DISABLED; never reads archived geometry."""
CANDIDATE2_BENCHMARK_AUTHORIZED = False

def main():
    if not CANDIDATE2_BENCHMARK_AUTHORIZED:raise SystemExit('STOP: synthetic benchmark is not authorized')
    import json, os, platform, tempfile, time
    from pathlib import Path
    import numpy as np
    import resolvability_candidate2_core as c
    # Source/dependency checks only. The benchmark does not call runtime.designs/contract.
    exp=Path(__file__).resolve().parent
    output=exp/'resolvability_candidate2_benchmark_archive'
    c.require(not output.exists(),'Benchmark output exists; inspect rather than overwrite')
    pin=json.loads((exp/'resolvability_candidate2_implementation_snapshot.json').read_text())
    c.require(platform.python_version()==pin['python_version'] and np.__version__==pin['numpy_version'],'Dependency pin mismatch')
    for name,h in pin['source_sha256'].items():c.require(c.digest((exp/name).read_bytes())==h,'Source hash mismatch')
    from resolvability_candidate2_runtime import require_closed, read_committed
    require_closed(['run_resolvability_validation.py','run_resolvability_surface.py','run_resolvability_benchmark.py','run_resolvability_candidate2_validation.py','run_resolvability_candidate2_surface.py'])
    for name,h in pin['source_sha256'].items():read_committed(exp/name,h)
    scenarios=[('synthetic_dominant_calibration',276,280,155,469,7),('synthetic_dominant_evaluation',281,275,154,7,469)]
    timing=[]
    for name,cgroups,egroups,positives,cfirst,efirst in scenarios:
        rows=[]
        for side,total,groups,first in [('calibration',1771,cgroups,cfirst),('evaluation',1770,egroups,efirst)]:
            sizes=[first]+[(total-first)//(groups-1)+(i<(total-first)%(groups-1)) for i in range(groups-1)]
            for g,size in enumerate(sizes):
                rows.extend((f'{side}_n_{g:04d}_{i:04d}',f'{side}_g_{g:04d}',side,'negative') for i in range(size))
        # Fabricated positive-only evaluation groups; not a biological allocation.
        rows.extend((f'evaluation_p_{i:04d}',f'evaluation_pg_{i:04d}','evaluation','positive') for i in range(positives))
        d=c.make_design(rows);cell={'allocation':name,'b':.6,'rho':.3,'r':.5,'delta':.1}
        samples=[]
        for i in range(4):
            start=time.perf_counter()
            scores=c.generate(d,cell,c.stream('benchmark',cell,i,'generation'))
            # Discard all numerical inference results; timings only.
            c.infer(d,scores,c.stream('benchmark',cell,i,'bootstrap'),999)
            samples.append(time.perf_counter()-start)
            print(f'{name}: synthetic timing {i+1}/4 finished; inference values discarded',flush=True)
        timing.append({'fixture':name,'record_count':len(rows),'calibration_groups':d['C'],'evaluation_groups':d['E'],
                       'seconds_per_outer_including_999_bootstraps':samples})
    values=[t for row in timing for t in row['seconds_per_outer_including_999_bootstraps']]
    report={'synthetic_geometry_only':True,'real_geometry_accessed':False,'confirmatory_outcomes_accessed':False,
        'benchmark_results':timing,'cpu_count':os.cpu_count(),'platform':platform.platform(),
        'python_version':platform.python_version(),'numpy_version':np.__version__,
        'illustrative_serial_hours_validation':float(np.median(values)*35000/3600),
        'illustrative_serial_hours_surface':float(np.median(values)*120000/3600),
        'limitation':'Synthetic timing extrapolation only; real geometry, checkpoint I/O and contention can change runtime.'}
    with tempfile.TemporaryDirectory(prefix='.resolvability_benchmark_',dir=exp) as tmp:
        stage=Path(tmp)/'archive';stage.mkdir()
        data=(json.dumps(report,sort_keys=True,indent=2)+'\n').encode();(stage/'timing.json').write_bytes(data)
        provenance={'runner_sha256':c.digest(Path(__file__).read_bytes()),'implementation_snapshot_sha256':c.digest((exp/'resolvability_candidate2_implementation_snapshot.json').read_bytes()),
                    'confirmatory_outcomes_accessed':False,'output_sha256':{'timing.json':c.digest(data)}}
        (stage/'provenance.json').write_text(json.dumps(provenance,sort_keys=True,indent=2)+'\n')
        stage.rename(output)
    print('Timing archive created; audit and commit before deciding execution resources.')

if __name__=='__main__':main()
