"""Synthetic paired operational-group simulator. Import performs no I/O."""
import csv
import hashlib
import io
import json
import math
from fractions import Fraction
from statistics import NormalDist
import numpy as np

class UndefinedInference(RuntimeError):
    pass

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def stream(phase, cell, outer, purpose):
    tokens=[20260923, phase, cell['allocation'],
            *[format(cell[k], '.2f') for k in ('b','rho','r','delta')], int(outer), purpose]
    seed=int.from_bytes(hashlib.sha256(json.dumps(tokens,separators=(',',':')).encode()).digest()[:16],'big')
    return np.random.Generator(np.random.PCG64(seed))

def make_design(records):
    """records: (ID, group, partition, class). Stable order; no real data access."""
    records=sorted(records)
    require(len({r[0] for r in records})==len(records),'Duplicate design record')
    groups=sorted({r[1] for r in records}); lookup={g:i for i,g in enumerate(groups)}
    sides={}
    for _,g,s,y in records:
        require(s in ('calibration','evaluation') and y in ('positive','negative'),'Invalid design label')
        require(g not in sides or sides[g]==s,'Group crosses allocation sides')
        sides[g]=s
    gi=np.array([lookup[r[1]] for r in records],dtype=np.int64)
    positive=np.array([r[3]=='positive' for r in records])
    calibration=np.array([r[2]=='calibration' for r in records])
    cn=np.flatnonzero(calibration & ~positive)
    ei=np.flatnonzero(~calibration)
    cg=sorted(set(gi[cn].tolist()));eg=sorted(set(gi[ei].tolist()))
    require(cg and eg,'Allocation has empty negative-calibration or evaluation support')
    cm={g:i for i,g in enumerate(cg)};em={g:i for i,g in enumerate(eg)}
    cidx=np.array([cm[int(g)] for g in gi[cn]],dtype=np.int64)
    eidx=np.array([em[int(g)] for g in gi[ei]],dtype=np.int64)
    ep=positive[ei]
    nc=np.bincount(cidx,minlength=len(cg))
    en=np.bincount(eidx[~ep],minlength=len(eg));epp=np.bincount(eidx[ep],minlength=len(eg))
    require(np.any(en) and np.any(epp),'Evaluation lacks one label')
    return dict(records=records,groups=groups,gi=gi,positive=positive,cn=cn,ei=ei,
                cidx=cidx,eidx=eidx,ep=ep,nc=nc,en=en,epp=epp,C=len(cg),E=len(eg))

def generate(design,cell,rng):
    rho=cell['rho'];r=cell['r'];b=cell['b'];delta=cell['delta']
    require(0<=rho<=1 and -1<r<1 and 0<b<1 and 0<b+delta<1,'Invalid generator cell')
    def paired(n):
        z=rng.standard_normal((n,2));z[:,1]=r*z[:,0]+math.sqrt(1-r*r)*z[:,1];return z
    g=paired(len(design['groups']));e=paired(len(design['records']))
    scores=math.sqrt(rho)*g[design['gi']]+math.sqrt(1-rho)*e
    normal=NormalDist();z=normal.inv_cdf(.95)
    scores[design['positive']]+=np.array([z+normal.inv_cdf(b),z+normal.inv_cdf(b+delta)])
    return scores

def thresholds(scores, group_index, group_sizes, multiplicities):
    """Exact-rational correction near a 95% crossing; strict tail uses observed score."""
    require(scores.ndim==1 and np.isfinite(scores).all(),'Invalid calibration scores')
    require(np.all(group_sizes>0),'Empty calibration group')
    require(np.issubdtype(multiplicities.dtype,np.integer) and np.all(multiplicities>=0),'Invalid multiplicities')
    total=multiplicities.sum(axis=1)
    if np.any(total==0):raise UndefinedInference('No calibration groups in bootstrap draw')
    order=np.argsort(scores,kind='stable');s=scores[order];g=group_index[order]
    weights=multiplicities[:,g]/group_sizes[g]
    cumulative=np.cumsum(weights,axis=1);cut=.95*total
    crosses=cumulative>=cut[:,None]
    require(np.all(np.any(crosses,axis=1)),'Calibration CDF does not reach target')
    indices=np.argmax(crosses,axis=1)
    chosen=s[indices].copy()
    # Roundoff must not change an exact rational 19/20 crossing.
    for row,j in enumerate(indices):
        near=abs(cumulative[row,j]-cut[row])<1e-10*total[row]
        if j:near=near or abs(cumulative[row,j-1]-cut[row])<1e-10*total[row]
        if not near:continue
        unique=np.unique(s)
        at=int(np.searchsorted(unique,chosen[row]))
        target=Fraction(19*int(total[row]),20)
        def cdf(value):
            counts=np.bincount(group_index[scores<=value],minlength=len(group_sizes))
            return sum((Fraction(int(multiplicities[row,k])*int(counts[k]),int(group_sizes[k]))
                        for k in range(len(group_sizes))),Fraction(0))
        while at and cdf(unique[at-1])>=target:at-=1
        while cdf(unique[at])<target:
            at+=1;require(at<len(unique),'Exact quantile crossing missing')
        chosen[row]=unique[at]
    return chosen

def rates(scores, group_index, group_counts, mult, threshold):
    if not len(scores):raise UndefinedInference('No label support')
    bearing=group_counts>0
    denominator=mult[:,bearing].sum(axis=1)
    records=(mult*group_counts).sum(axis=1)
    if np.any(denominator==0) or np.any(records==0):
        raise UndefinedInference('Bootstrap evaluation sample lacks a label')
    calls=scores[None,:]>threshold[:,None]
    primary=(calls*(mult[:,group_index]/group_counts[group_index])).sum(axis=1)/denominator
    secondary=(calls*mult[:,group_index]).sum(axis=1)/records
    return primary,secondary

def evaluate(design,scores,cmult,emult):
    count=len(cmult);require(len(emult)==count,'Bootstrap pairing count mismatch')
    result={}
    for arm in range(2):
        cn=scores[design['cn'],arm]
        threshold=thresholds(cn,design['cidx'],design['nc'],cmult)
        es=scores[design['ei'],arm];p=design['ep']
        tpr,secondary_tpr=rates(es[p],design['eidx'][p],design['epp'],emult,threshold)
        fpr,secondary_fpr=rates(es[~p],design['eidx'][~p],design['en'],emult,threshold)
        cal_weights=cmult[:,design['cidx']]/design['nc'][design['cidx']]
        calden=cmult.sum(axis=1)
        cal_fpr=((cn[None,:]>threshold[:,None])*cal_weights).sum(axis=1)/calden
        jump=((cn[None,:]==threshold[:,None])*cal_weights).sum(axis=1)/calden
        result[arm]=dict(threshold=threshold,tpr=tpr,fpr=fpr,secondary_tpr=secondary_tpr,
                         secondary_fpr=secondary_fpr,calibration_fpr=cal_fpr,calibration_cdf_jump=jump)
    return result

def infer(design,scores,rng,bootstrap_replicates=999,batch=32):
    require(scores.shape==(len(design['records']),2),'Score shape mismatch')
    observed=evaluate(design,scores,np.ones((1,design['C']),dtype=np.int64),np.ones((1,design['E']),dtype=np.int64))
    # Draw all multiplicities before batching; execution batch size cannot alter RNG.
    cm=rng.multinomial(design['C'],np.full(design['C'],1/design['C']),size=bootstrap_replicates)
    em=rng.multinomial(design['E'],np.full(design['E'],1/design['E']),size=bootstrap_replicates)
    diffs=[];th=[[],[]]
    for start in range(0,bootstrap_replicates,batch):
        end=min(start+batch,bootstrap_replicates)
        b=evaluate(design,scores,cm[start:end],em[start:end])
        diffs.extend((b[1]['tpr']-b[0]['tpr']).tolist())
        for a in (0,1):th[a].extend(b[a]['threshold'].tolist())
    lower,upper=np.quantile(np.asarray(diffs),[.025,.975],method='linear')
    point=float(observed[1]['tpr'][0]-observed[0]['tpr'][0])
    out={'estimate':point,'lower':float(lower),'upper':float(upper),'half_width':float((upper-lower)/2),
         'secondary_estimate':float(observed[1]['secondary_tpr'][0]-observed[0]['secondary_tpr'][0])}
    for a,name in ((0,'comparator'),(1,'esm')):
        out[name]={k:float(v[0]) for k,v in observed[a].items()}
        out[name]['bootstrap_threshold_sd']=float(np.std(th[a],ddof=1))
        out[name]['threshold_error']=out[name]['threshold']-NormalDist().inv_cdf(.95)
        out[name]['evaluation_fpr_error']=out[name]['fpr']-.05
    pidx=np.flatnonzero(design['ep']);g=design['eidx'][pidx]
    ps=scores[design['ei'][pidx]]
    c=ps[:,0]>out['comparator']['threshold'];e=ps[:,1]>out['esm']['threshold']
    denom=np.count_nonzero(design['epp'])
    out['paired_positive_discordance']={
        'esm_only':float(np.sum((e & ~c)/design['epp'][g])/denom),
        'comparator_only':float(np.sum((c & ~e)/design['epp'][g])/denom)}
    return out

def outer(design,phase,cell,index,bootstrap_replicates=999):
    scores=generate(design,cell,stream(phase,cell,index,'generation'))
    try:
        result=infer(design,scores,stream(phase,cell,index,'bootstrap'),bootstrap_replicates)
        delta=cell['delta'];result.update(valid=True,outer_index=index,
            coverage=result['lower']<=delta<=result['upper'],
            null_rejection=result['lower']>0 or result['upper']<0,
            positive_rejection=result['lower']>0,error=result['estimate']-delta)
        return result
    except UndefinedInference as exc:
        return dict(valid=False,outer_index=index,reason=str(exc),coverage=False,null_rejection=False,positive_rejection=False)

def summarize(rows):
    n=len(rows);require(n>0,'No outer replicates');valid=[r for r in rows if r['valid']]
    def stats(values):
        a=np.asarray(values,dtype=float)
        return None if not len(a) else {'mean':float(a.mean()),'sd':float(a.std(ddof=1)) if len(a)>1 else None,
                'median':float(np.median(a)),'q025':float(np.quantile(a,.025,method='linear')),'q975':float(np.quantile(a,.975,method='linear'))}
    out={'requested_replicates':n,'valid_replicates':len(valid),'failure_count':n-len(valid),
         'failure_reasons':{},'median_half_width':float(np.median([r['half_width'] for r in valid])) if valid else None,
         'bias':float(np.mean([r['error'] for r in valid])) if valid else None}
    for r in rows:
        if not r['valid']:out['failure_reasons'][r['reason']]=out['failure_reasons'].get(r['reason'],0)+1
    for metric in ('coverage','null_rejection','positive_rejection'):
        p=sum(bool(r[metric]) for r in rows)/n
        out[metric]={'rate':p,'monte_carlo_se':math.sqrt(p*(1-p)/n)}
    out['estimate_distribution']=stats([r['estimate'] for r in valid])
    out['error_distribution']=stats([r['error'] for r in valid])
    out['secondary_estimate_distribution']=stats([r['secondary_estimate'] for r in valid])
    out['paired_positive_discordance']={k:stats([r['paired_positive_discordance'][k] for r in valid]) for k in ('esm_only','comparator_only')}
    for arm in ('comparator','esm'):
        out[arm]={k:stats([r[arm][k] for r in valid]) for k in
            ('threshold','threshold_error','bootstrap_threshold_sd','calibration_cdf_jump','calibration_fpr',
             'fpr','evaluation_fpr_error','tpr','secondary_tpr','secondary_fpr')}
    return out

def boundary_checks(design,allocation):
    result=[];n=len(design['records'])
    for fixture in ('perfect_separation','adjacent_negative_scores','tied_negative_scores'):
        scores=np.zeros((n,2));scores[design['positive']]=1.
        if fixture=='adjacent_negative_scores':
            neg=np.flatnonzero(~design['positive'])
            scores[neg]=np.arange(len(neg))[:,None]/max(len(neg),1)
            scores[design['positive']]=2.
        if fixture=='tied_negative_scores':
            p=np.flatnonzero(design['positive']);scores[p]=(np.arange(len(p))%2)[:,None]
        cell={'allocation':allocation,'b':.6,'rho':.3,'r':.5,'delta':0.}
        fit=infer(design,scores,stream('boundary',cell,len(result),'bootstrap'),999)
        require(fit['estimate']==fit['lower']==fit['upper']==0,'Identical-arm boundary difference')
        details={}
        for arm in ('comparator','esm'):
            if fixture!='adjacent_negative_scores':
                require(fit[arm]['threshold']==0 and fit[arm]['fpr']==0,'Tied/perfect threshold fixture')
            if fixture=='perfect_separation':require(fit[arm]['tpr']==1,'Perfect separation TPR')
        if fixture=='adjacent_negative_scores':
            x=scores[design['cn'],0];unique=np.unique(x);threshold=fit['comparator']['threshold']
            higher=unique[unique>threshold];require(len(higher)>0,'Adjacent fixture lacks upper score')
            midpoint=(threshold+float(higher[0]))/2
            require(np.array_equal(x>threshold,x>midpoint),'Calls changed inside calibration score gap')
            details={'observed_threshold':threshold,'next_calibration_score':float(higher[0]),'gap_midpoint':midpoint,
                     'scope':'Identical calibration calls; evaluation scores need not share the gap.'}
        result.append({'fixture':fixture,'passed':True,'estimate':fit['estimate'],'interval':[fit['lower'],fit['upper']],'details':details})
    return result
