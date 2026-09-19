#!/usr/bin/env python3
"""A1-S: immutable Pfam scan archive, authorized but not yet executed."""
import csv, gzip, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

SCAN_AUTHORIZED = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = HERE / "a1_annotation_snapshot.json"
INPUT = HERE / "a1_input"
ARCHIVE = HERE / "a1_scan_archive"

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def require(path, expected):
    got=digest(path)
    if got != expected: raise RuntimeError(f"SHA-256 mismatch: {path}: {got}")

def pfam_version(path):
    values={}
    with gzip.open(path,"rt",encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                k,v=line.split(":",1); values[k.strip()]=v.strip()
    expected={"Pfam release":"37.0","Pfam-A families":"21979","Date":"2024-03","Based on UniProtKB":"2023_05"}
    if values != expected: raise RuntimeError(f"Pfam version gate failed: {values}")
    return values

def discovery(config):
    spec=config["discovery"]; fasta=REPO/spec["fasta_path"]; manifest=REPO/spec["manifest_path"]
    require(fasta,spec["fasta_sha256"]); require(manifest,spec["manifest_sha256"])
    rows=list(csv.DictReader(manifest.open(newline=""),delimiter="\t"))
    counts={x:sum(r["class_name"]==x for r in rows) for x in ("positive","negative")}
    if len(rows)!=278 or counts!={"positive":139,"negative":139}: raise RuntimeError("Discovery count gate failed")
    return fasta,{r["identifier"]:r["class_name"] for r in rows},counts

def main():
    config=json.loads(CONFIG.read_text())
    if not SCAN_AUTHORIZED: raise RuntimeError("A1-S is not authorized")
    fasta,labels,counts=discovery(config)
    names=("Pfam-A.hmm.gz","Pfam-A.clans.tsv.gz","Pfam-A.hmm.dat.gz","Pfam.version.gz")
    for name in names: require(INPUT/name,config["pfam"]["artifacts"][name]["sha256"])
    version=pfam_version(INPUT/"Pfam.version.gz")
    if ARCHIVE.exists(): raise RuntimeError("A1-S archive already exists")
    with tempfile.TemporaryDirectory(prefix="a1s_",dir=HERE) as td:
        work=Path(td); hmm=work/"Pfam-A.hmm"
        with gzip.open(INPUT/"Pfam-A.hmm.gz","rb") as src,hmm.open("wb") as dst: shutil.copyfileobj(src,dst)
        subprocess.run(["hmmpress",str(hmm)],check=True,cwd=work,capture_output=True)
        dom=work/"raw.domtblout"; out=work/"hmmscan.stdout"; err=work/"hmmscan.stderr"
        cmd=["hmmscan","--cut_ga","--noali","--domtblout",str(dom),str(hmm),str(fasta)]
        with out.open("wb") as o,err.open("wb") as e: subprocess.run(cmd,check=True,cwd=work,stdout=o,stderr=e)
        hits=[]
        for line in dom.read_text().splitlines():
            if not line or line.startswith("#"): continue
            f=line.split(maxsplit=22); query=f[3]; label,protein=query.split("|",1)
            if labels.get(protein)!=label: raise RuntimeError(f"Unknown query: {query}")
            hits.append((label,protein,f[1].split(".",1)[0],f[0]))
        stage=work/"archive"; stage.mkdir()
        manifest=REPO/config["discovery"]["manifest_path"]
        for source,name in ((dom,"raw.domtblout"),(out,"hmmscan.stdout"),(err,"hmmscan.stderr"),(manifest,"discovery_sequence_manifest.tsv"),(INPUT/"Pfam-A.clans.tsv.gz","Pfam-A.clans.tsv.gz"),(INPUT/"Pfam.version.gz","Pfam.version.gz")): shutil.copy2(source,stage/name)
        with (stage/"accepted_family_hits.tsv").open("w",newline="") as f:
            w=csv.writer(f,delimiter="\t",lineterminator="\n"); w.writerow(("class_name","protein_id","pfam_accession","model_name")); w.writerows(sorted(set(hits)))
        files={p.name:digest(p) for p in sorted(stage.iterdir())}
        provenance={"confirmatory_accessed":False,"discovery_counts":counts,"pfam_version":version,"acceptance_rule":"retain every domain accepted by curator-defined Pfam gathering thresholds via hmmscan --cut_ga; no global E-value cutoff","command":["hmmscan","--cut_ga","--noali","--domtblout","raw.domtblout","Pfam-A.hmm",config["discovery"]["fasta_path"]],"hmmer_version":subprocess.run(["hmmscan","-h"],text=True,capture_output=True,check=True).stdout.splitlines()[1],"session_binary_sha256":{"hmmscan":digest(shutil.which("hmmscan")),"hmmpress":digest(shutil.which("hmmpress")),"claim":"session identity only; not reproducible-build hashes"},"file_sha256":files}
        (stage/"scan_provenance.json").write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
        stage.rename(ARCHIVE)

if __name__=="__main__": main()
