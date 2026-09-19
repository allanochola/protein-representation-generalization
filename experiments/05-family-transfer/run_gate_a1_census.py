#!/usr/bin/env python3
"""A1-C: census from a committed A1-S archive. Disabled until authorization."""
import csv,gzip,hashlib,json,subprocess
from collections import defaultdict
from pathlib import Path

CENSUS_AUTHORIZED=False
HERE=Path(__file__).resolve().parent; ARCHIVE=HERE/"a1_scan_archive"; OUTPUT=HERE/"a1_census_output"
BANNED_COLUMNS=("auroc","tpr","fpr","score","threshold")
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check_columns(columns):
    for column in columns:
        if any(token in column.casefold() for token in BANNED_COLUMNS):
            raise RuntimeError(f"Forbidden A1-C output column: {column}")
class DSU:
    def __init__(self,x): self.p={i:i for i in x}
    def find(self,x):
        while self.p[x]!=x: self.p[x]=self.p[self.p[x]]; x=self.p[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b: self.p[max(a,b)]=min(a,b)
def census(positives,hits,clans):
    ids={p:sorted({clans.get(f,f) for f in hits.get(p,set())}) for p in positives}
    assigned=[p for p in positives if ids[p]]; d=DSU(assigned); by=defaultdict(list)
    for p in assigned:
        for i in ids[p]: by[i].append(p)
    for members in by.values():
        for p in members[1:]: d.union(members[0],p)
    groups=defaultdict(list)
    for p in assigned: groups[d.find(p)].append(p)
    components=sorted((sorted(v) for v in groups.values()),key=lambda v:(-len(v),v))
    n=len(positives); a=len(assigned); sizes=[len(x) for x in components]
    unassigned=n-a; supported=sum(x for x in sizes if x>=2); largest=max(sizes,default=0); single=sum(x==1 for x in sizes)
    L=supported/a if a else None; largest_share=largest/n; unassigned_share=unassigned/n
    if unassigned_share>.10: route="INCONCLUSIVE_UNASSIGNED"
    elif largest_share>.15: route="AMENDMENT_REQUIRED_CONCENTRATION"
    elif L is not None and L>=.25: route="TWO_STAGE_ELIGIBLE"
    else: route="SKIP_STAGE1_NEAR_VACUOUS"
    return ids,components,{"total_positive_count":n,"assigned_positive_count":a,"assigned_positive_fraction":a/n,"unassigned_positive_count":unassigned,"unassigned_positive_share":unassigned_share,"component_count":len(sizes),"largest_component_count":largest,"largest_component_share_all_positives":largest_share,"assigned_singleton_count":single,"assigned_singleton_fraction":single/a if a else None,"l_value_among_assigned":L,"route":route}
def main():
    if not CENSUS_AUTHORIZED: raise RuntimeError("A1-C is not authorized")
    tracked=set(subprocess.check_output(["git","ls-files"],cwd=HERE.parents[1],text=True).splitlines())
    rel=lambda p:str(p.relative_to(HERE.parents[1]))
    provenance=ARCHIVE/"scan_provenance.json"
    if rel(provenance) not in tracked: raise RuntimeError("A1-S archive is not committed")
    meta=json.loads(provenance.read_text())
    for name,sha in meta["file_sha256"].items():
        p=ARCHIVE/name
        if rel(p) not in tracked or digest(p)!=sha: raise RuntimeError(f"Archive integrity failure: {name}")
    clans={}
    with gzip.open(ARCHIVE/"Pfam-A.clans.tsv.gz","rt") as f:
        for line in f:
            x=line.rstrip().split("\t"); clans[x[0]]=x[1]
    positives=[]
    with (ARCHIVE/"discovery_sequence_manifest.tsv").open() as f:
        for r in csv.DictReader(f,delimiter="\t"):
            if r["class_name"]=="positive": positives.append(r["identifier"])
    if len(positives)!=139 or len(set(positives))!=139: raise RuntimeError("Archived positive manifest gate failed")
    hits=defaultdict(set)
    with (ARCHIVE/"accepted_family_hits.tsv").open() as f:
        for r in csv.DictReader(f,delimiter="\t"):
            if r["class_name"]=="positive": hits[r["protein_id"]].add(r["pfam_accession"])
    if set(hits)-set(positives): raise RuntimeError("Positive hit absent from archived manifest")
    ids,components,summary=census(positives,hits,clans)
    if OUTPUT.exists(): raise RuntimeError("A1-C output already exists")
    OUTPUT.mkdir()
    assignment_columns=("protein_id","group_identifiers"); check_columns(assignment_columns)
    with (OUTPUT/"assignments.tsv").open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t",lineterminator="\n"); w.writerow(assignment_columns); w.writerows((p,";".join(ids[p]) or "UNASSIGNED") for p in sorted(positives))
    component_columns=("component_id","member_count","member_ids"); check_columns(component_columns)
    with (OUTPUT/"components.tsv").open("w",newline="") as f:
        w=csv.writer(f,delimiter="\t",lineterminator="\n"); w.writerow(component_columns)
        for members in components:
            cid="COMP_"+hashlib.sha256("\n".join(members).encode()).hexdigest()[:16]; w.writerow((cid,len(members),";".join(members)))
    (OUTPUT/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    output_sha256={name:digest(OUTPUT/name) for name in ("assignments.tsv","components.tsv","summary.json")}
    census_provenance={"confirmatory_accessed":False,"scan_provenance_sha256":digest(provenance),"archive_members_verified_tracked":True,"grouping_rule":"all accepted clan-first/family-fallback identifiers; full transitive closure","l_denominator":"assigned discovery positives","largest_component_share_denominator":"all 139 discovery positives","unassigned_share_denominator":"all 139 discovery positives","output_sha256":output_sha256}
    (OUTPUT/"census_provenance.json").write_text(json.dumps(census_provenance,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
