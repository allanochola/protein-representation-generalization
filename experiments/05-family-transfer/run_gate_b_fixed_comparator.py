"""Authorized one-time Gate B fixed-comparator fit."""
import csv,hashlib,json,joblib,sklearn
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
COMPARATOR_FIT_AUTHORIZED=True
REPO=Path(__file__).resolve().parents[2]
EXP=REPO/'experiments/05-family-transfer'
MANIFEST=EXP/'a1_scan_archive/discovery_sequence_manifest.tsv'
FASTA=REPO/'experiments/03-toxin-representation/stage1_model_blind/precontact_gate/discovery_sequences.fasta'
OUT=EXP/'gate_b_fixed_comparator'
MANIFEST_SHA='7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09'; FASTA_SHA='ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358'; EXPECTED_SKLEARN='1.6.1'; EXPECTED_JOBLIB='1.5.3'
AA='ACDEFGHIKLMNPQRSTVWY'; FEATURES=('length',)+tuple(AA); PARAMS={'n_estimators': 300, 'criterion': 'gini', 'max_depth': None, 'min_samples_split': 2, 'min_samples_leaf': 2, 'min_weight_fraction_leaf': 0.0, 'max_features': 'sqrt', 'max_leaf_nodes': None, 'min_impurity_decrease': 0.0, 'bootstrap': True, 'oob_score': False, 'n_jobs': 1, 'random_state': 20260829, 'verbose': 0, 'warm_start': False, 'class_weight': None, 'ccp_alpha': 0.0, 'max_samples': None, 'monotonic_cst': None}
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def manifest():
 out={}
 with MANIFEST.open(newline='') as f:
  for r in csv.DictReader(f,delimiter='\t'):
   if r['identifier'] in out: raise RuntimeError('duplicate manifest identifier')
   out[r['identifier']]=(r['class_name'],r['sequence_sha256'])
 if len(out)!=278 or sum(v[0]=='positive' for v in out.values())!=139: raise RuntimeError('manifest geometry mismatch')
 return out
def resolve(header,required):
 first=header.split()[0]; candidates={first}
 if '|' in first: candidates.update(x for x in first.split('|') if x)
 hits=sorted(candidates & required)
 if len(hits)>1: raise RuntimeError('ambiguous FASTA identifier')
 return hits[0] if hits else None
def sequences(spec):
 records={}; header=None; chunks=[]; required=set(spec)
 def store():
  if header is None:return
  ident=resolve(header,required)
  if ident is None:return
  seq=''.join(chunks).replace(' ','').upper()
  if not seq or ident in records: raise RuntimeError('empty/duplicate sequence')
  if hashlib.sha256(seq.encode('ascii')).hexdigest()!=spec[ident][1]: raise RuntimeError('sequence hash mismatch')
  records[ident]=seq
 with FASTA.open() as f:
  for raw in f:
   line=raw.strip()
   if not line:continue
   if line.startswith('>'): store(); header=line[1:]; chunks=[]
   else:
    if header is None: raise RuntimeError('sequence before FASTA header')
    chunks.append(line)
 store()
 if set(records)!=required: raise RuntimeError('FASTA membership mismatch')
 return records
def main():
 if not COMPARATOR_FIT_AUTHORIZED: raise SystemExit('STOP: Gate B comparator fitting is not authorized')
 if sklearn.__version__!=EXPECTED_SKLEARN or joblib.__version__!=EXPECTED_JOBLIB: raise RuntimeError('library-version mismatch')
 if digest(MANIFEST)!=MANIFEST_SHA or digest(FASTA)!=FASTA_SHA: raise RuntimeError('input identity mismatch')
 if OUT.exists(): raise RuntimeError('output already exists')
 spec=manifest(); seqs=sequences(spec); ids=sorted(spec)
 X=[]; y=[]
 for ident in ids:
  seq=seqs[ident]; n=len(seq); X.append([n]+[seq.count(a)/n for a in AA]); y.append(1 if spec[ident][0]=='positive' else 0)
 X=np.asarray(X,dtype=np.float64); y=np.asarray(y,dtype=np.int8)
 if X.shape!=(278,21) or int(y.sum())!=139: raise RuntimeError('design matrix mismatch')
 OUT.mkdir()
 table=OUT/'feature_matrix.tsv'
 with table.open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n'); w.writerow(('protein_id','class_name',*FEATURES))
  for ident,row in zip(ids,X): w.writerow((ident,spec[ident][0],str(int(row[0])),*(format(v,'.17g') for v in row[1:])))
 model=RandomForestClassifier(**PARAMS); model.fit(X,y)
 artifact=OUT/'comparator.joblib'; joblib.dump(model,artifact,compress=0)
 hashes={'feature_matrix.tsv':digest(table),'comparator.joblib':digest(artifact)}
 provenance={'confirmatory_accessed':False,'development_predictions_computed':False,'development_metrics_computed':False,'cross_validation_performed':False,'candidate_comparison_performed':False,'manifest_sha256':MANIFEST_SHA,'source_fasta_sha256':FASTA_SHA,'feature_order':list(FEATURES),'noncanonical_rule':'included in full-length denominator; excluded from canonical numerators','label_encoding':{'negative':0,'positive':1},'classifier':'sklearn.ensemble.RandomForestClassifier','parameters':PARAMS,'scikit_learn_version':sklearn.__version__,'joblib_version':joblib.__version__,'record_count':278,'positive_count':139,'negative_count':139,'output_sha256':hashes}
 (OUT/'fit_provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
