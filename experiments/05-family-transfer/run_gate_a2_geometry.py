'A2-C: joint family geometry archived; execution closed.'
import ast
import csv
import gzip
import hashlib
import io
import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

A2_CENSUS_AUTHORIZED = False
REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"
ARCHIVE = EXP / "a2_scan_archive"
OUTPUT = EXP / "a2_geometry_output"
CONTRACT = EXP / "GATE_A2_GEOMETRY_SPECIFICATION_001.md"
CONTRACT_SHA256 = "6c662de33c2f84a2d33ce3b5157705a83b58ebf0ef748836cfbe6828c64a1bf0"
ARCHIVE_COMMIT = "978b9be0df7c909c18d606774074b692090a0cec"
HISTORICAL = EXP / "a2_sequence_recovery_archive/historical_annotation_claims.tsv"
HISTORICAL_SHA256 = "6a39892018be1a75fb3d52bff11d2daf5efeea9e15d02557ede95c91da571722"
BANNED = ("auroc", "auprc", "tpr", "fpr", "score", "prediction", "probability", "threshold", "embedding", "activation")

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git_bytes(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, check=True).stdout

def committed(path, revision="HEAD"):
    relative = path.relative_to(REPO).as_posix()
    data = git_bytes("show", f"{revision}:{relative}")
    require(path.is_file() and not path.is_symlink() and path.read_bytes() == data,
            f"Working input differs: {relative}")
    require(git_bytes("show", f"HEAD:{relative}") == data, f"Input changed in HEAD: {relative}")
    return data

def check_columns(columns):
    require(not any(token in c.casefold() for c in columns for token in BANNED), "Forbidden derived column")

def rows(data, columns):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8")), delimiter="\t")
    require(reader.fieldnames == columns, "Input TSV schema mismatch")
    result = list(reader)
    require(all(None not in r and all(v is not None for v in r.values()) for r in result), "Malformed TSV")
    return result

def family_token(accession, clans):
    family = accession.split(".", 1)[0]
    require(family in clans, "Accepted family absent from pinned mapping")
    return clans[family] or family

def geometry(metadata, clusters, tokens):
    require(set(metadata) == set(clusters) == set(tokens), "Grouping membership mismatch")
    require(all(r["universe"] in ("discovery", "confirmatory") and r["class_name"] in ("positive", "negative")
                for r in metadata.values()), "Unexpected class or universe")
    require(all(clusters[p] and all(tokens[p]) for p in metadata), "Empty grouping identifier")
    parent = {p:p for p in metadata}
    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p
    def union(a,b):
        a,b = find(a),find(b)
        if a != b:
            parent[max(a,b)] = min(a,b)
    sequence_groups = defaultdict(list)
    pfam_groups = defaultdict(list)
    for p in sorted(metadata):
        sequence_groups[clusters[p]].append(p)
        for token in sorted(set(tokens[p])):
            pfam_groups[token].append(p)
    for groups in (sequence_groups, pfam_groups):
        for members in groups.values():
            for member in members[1:]:
                union(members[0], member)
    by_root = defaultdict(list)
    for p in sorted(metadata):
        by_root[find(p)].append(p)
    components = {sha("\n".join(members).encode("ascii")):members for members in by_root.values()}
    require(sum(map(len,components.values())) == len(metadata), "Component integrity failure")
    assignment = {p:c for c,members in components.items() for p in members}
    populations = {}
    for universe in ("discovery", "confirmatory"):
        for label in ("all", "positive", "negative"):
            selected = {p for p,r in metadata.items() if r["universe"] == universe
                        and (label == "all" or r["class_name"] == label)}
            sizes = Counter(assignment[p] for p in selected)
            largest = max(sizes.values(), default=0)
            assigned = sum(bool(tokens[p]) for p in selected)
            populations[universe + "_" + label] = {
                "record_count":len(selected), "bearing_component_count":len(sizes),
                "intersection_size_distribution":dict(sorted(Counter(sizes.values()).items())),
                "largest_intersection_count":largest,
                "largest_intersection_share":largest/len(selected) if selected else None,
                "singleton_intersection_count":sum(s == 1 for s in sizes.values()),
                "pfam_assigned_count":assigned,
                "pfam_assigned_fraction":assigned/len(selected) if selected else None,
            }
    cp = {p for p,r in metadata.items() if r["universe"] == "confirmatory" and r["class_name"] == "positive"}
    dp = {p for p,r in metadata.items() if r["universe"] == "discovery" and r["class_name"] == "positive"}
    discovery = {p for p,r in metadata.items() if r["universe"] == "discovery"}
    dp_components = {assignment[p] for p in dp}
    discovery_components = {assignment[p] for p in discovery}
    cp_sizes = Counter(assignment[p] for p in cp)
    cross_unique = {k:set() for k in ("discovery_only","confirmatory_only","cross_universe")}
    cross_incidence = Counter()
    for members in pfam_groups.values():
        positives = [p for p in members if metadata[p]["class_name"] == "positive"]
        negatives = [p for p in members if metadata[p]["class_name"] == "negative"]
        for a in positives:
            for b in negatives:
                ua,ub = metadata[a]["universe"],metadata[b]["universe"]
                scope = ua + "_only" if ua == ub else "cross_universe"
                cross_incidence[scope] += 1
                cross_unique[scope].add(tuple(sorted((a,b))))
    hash_groups = defaultdict(list)
    for p,r in metadata.items():
        hash_groups[r["sequence_sha256"]].append(p)
    duplicate_pairs = 0
    duplicate_records = set()
    for members in hash_groups.values():
        d = [p for p in members if metadata[p]["universe"] == "discovery"]
        c = [p for p in members if metadata[p]["universe"] == "confirmatory"]
        if d and c:
            duplicate_pairs += len(d)*len(c)
            duplicate_records.update(c)
    summary = {
        "total_records":len(metadata), "joint_component_count":len(components),
        "populations":populations,
        "confirmatory_positive_disjointness":{
            "distinct_joint_components":len(cp_sizes) == len(cp),
            "records_in_components_with_multiple_confirmatory_positives":sum(n for n in cp_sizes.values() if n>1),
            "records_sharing_discovery_positive_component":sum(assignment[p] in dp_components for p in cp),
            "records_sharing_any_discovery_component":sum(assignment[p] in discovery_components for p in cp),
        },
        "direct_cross_label_pfam_relationships":{
            k:{"unique_pair_count":len(cross_unique[k]), "pair_token_incidence_count":cross_incidence[k]}
            for k in sorted(cross_unique)
        },
        "exact_sequence_identity_across_universes":{
            "pair_count":duplicate_pairs,"confirmatory_record_count":len(duplicate_records)},
        "interpretation":"Operational joint groups; no historical filter-failure or biological-label-error inference.",
    }
    return assignment, components, pfam_groups, summary

def load_inputs():
    definition = committed(CONTRACT)
    require(sha(definition) == CONTRACT_SHA256, "Definition hash mismatch")
    audit_path = EXP / "GATE_A2_SCAN_ARCHIVE_AUDIT_001.json"
    audit_bytes = committed(audit_path, ARCHIVE_COMMIT)
    audit = json.loads(audit_bytes)
    hashes = audit["archive_member_sha256"]
    require(hashes and all(not Path(n).is_absolute() and ".." not in Path(n).parts for n in hashes), "Unsafe archive path")
    paths = list(ARCHIVE.rglob("*"))
    require(not any(p.is_symlink() for p in paths), "Archive symlink")
    require({p.relative_to(ARCHIVE).as_posix() for p in paths if p.is_file()} == set(hashes), "Archive membership differs")
    for name,digest in hashes.items():
        require(sha(committed(ARCHIVE/name, ARCHIVE_COMMIT)) == digest, "Archive digest mismatch")
    provenance = json.loads((ARCHIVE/"scan_provenance.json").read_bytes())
    require(provenance["output_sha256"] == {k:v for k,v in hashes.items() if k != "scan_provenance.json"},
            "Scan provenance hashes differ")
    require(provenance["confirmatory_outcomes_accessed"] is False, "Outcome seal provenance")
    require(sha(committed(HISTORICAL)) == HISTORICAL_SHA256, "Historical claim identity differs")
    mapping = rows((ARCHIVE/"joint_identifier_map.tsv").read_bytes(),
                   ["protein_id","universe","class_name","accession","sequence_length","sequence_sha256"])
    metadata = {r["protein_id"]:r for r in mapping}
    require(len(metadata) == len(mapping) == 3980, "Joint count mismatch")
    require(Counter((r["universe"],r["class_name"]) for r in mapping) ==
            {("discovery","positive"):139,("discovery","negative"):139,
             ("confirmatory","positive"):161,("confirmatory","negative"):3541}, "Population counts differ")
    parts = rows((ARCHIVE/"canonical_partition.tsv").read_bytes(),["protein_id","sequence_cluster_sha256"])
    clusters = {r["protein_id"]:r["sequence_cluster_sha256"] for r in parts}
    require(len(parts) == len(clusters) == 3980, "Partition row count")
    clans = {}
    with gzip.open(ARCHIVE/"pfam/Pfam-A.clans.tsv.gz","rt") as f:
        for line in f:
            fields = line.rstrip("\r\n").split("\t")
            require(len(fields) == 5 and fields[0] and fields[0] not in clans, "Pfam mapping schema")
            clans[fields[0]] = fields[1].strip()
    require(len(clans) == 21979, "Pfam mapping family count")
    hits = rows((ARCHIVE/"pfam/accepted_family_hits.tsv").read_bytes(),
                ["identifier","universe","class_name","accession","pfam_accession","model_name"])
    tokens = {p:set() for p in metadata}
    for hit in hits:
        p = hit["identifier"]
        require(p in metadata, "Unknown accepted-hit protein")
        require(all(hit[k] == metadata[p][k] for k in ("universe","class_name","accession")), "Hit label mapping differs")
        tokens[p].add(family_token(hit["pfam_accession"],clans))
    return metadata,clusters,tokens,hashes,sha(audit_bytes)

def write_tsv(path, columns, data):
    check_columns(columns)
    with path.open("w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f,delimiter="\t",lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(data)

def main():
    if not A2_CENSUS_AUTHORIZED:
        raise SystemExit("STOP: Gate A2-C geometry is not authorized")
    require(not OUTPUT.exists() and not OUTPUT.is_symlink(), "Geometry output already exists")
    scan_source = committed(EXP/"run_gate_a2_scan.py")
    gates = [ast.literal_eval(n.value) for n in ast.walk(ast.parse(scan_source)) if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id == "A2_SCAN_AUTHORIZED" for t in n.targets)]
    require(gates == [False], "A2-SS must be closed")
    metadata,clusters,tokens,input_hashes,audit_hash = load_inputs()
    assignment,components,pfam_groups,summary = geometry(metadata,clusters,tokens)
    with tempfile.TemporaryDirectory(prefix="exp05_a2c_",dir=OUTPUT.parent) as temp:
        stage = Path(temp)/OUTPUT.name
        stage.mkdir()
        write_tsv(stage/"assignments.tsv",["protein_id","universe","class_name","component_id","pfam_identifiers"],
                  ((p,metadata[p]["universe"],metadata[p]["class_name"],assignment[p],";".join(sorted(tokens[p]))) for p in sorted(metadata)))
        write_tsv(stage/"components.tsv",["component_id","member_count","member_ids"],
                  ((c,len(components[c]),";".join(components[c])) for c in sorted(components)))
        write_tsv(stage/"pfam_memberships.tsv",["pfam_identifier","protein_id"],
                  ((token,p) for token in sorted(pfam_groups) for p in sorted(pfam_groups[token])))
        (stage/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        outputs = {p.name:sha(p.read_bytes()) for p in sorted(stage.iterdir())}
        provenance = {
            "schema":"exp05_a2_geometry_v1", "definition_sha256":CONTRACT_SHA256,
            "runner_sha256":sha(committed(Path(__file__).resolve())),
            "execution_commit":git_bytes("rev-parse","HEAD").decode().strip(),
            "archive_commit":ARCHIVE_COMMIT,"input_sha256":input_hashes,
            "archive_audit_sha256":audit_hash,
            "historical_annotation_claims":{"path":HISTORICAL.relative_to(REPO).as_posix(),
                                            "sha256":HISTORICAL_SHA256,"used_for_grouping":False},
            "confirmatory_metadata_accessed":True,"confirmatory_outcomes_accessed":False,
            "family_geometry_computed":True,"output_sha256":outputs,
        }
        (stage/"geometry_provenance.json").write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
        require(not OUTPUT.exists(),"Output appeared during execution")
        stage.rename(OUTPUT)

if __name__ == "__main__":
    main()
