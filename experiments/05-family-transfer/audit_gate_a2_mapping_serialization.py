"""Reproduce the original frozen joint serialization without scanning."""
import ast
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"
FREEZE = "3eb736a5173ae0a41d5d319b40e5665adb4f0e86"

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def committed(relative):
    data = subprocess.run(
        ["git", "show", f"{FREEZE}:{relative}"],
        cwd=REPO, check=True, capture_output=True,
    ).stdout
    head = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=REPO, check=True, capture_output=True,
    ).stdout
    require(head == data == (REPO / relative).read_bytes(),
            f"Frozen input differs: {relative}")
    return data

def fasta(data):
    records = {}
    identifier = None
    chunks = []
    def store():
        if identifier is not None:
            require(identifier not in records, "Duplicate FASTA ID")
            sequence = "".join(chunks)
            require(sequence and sequence.isascii() and sequence.isalpha()
                    and sequence == sequence.upper(), "Noncanonical sequence")
            records[identifier] = sequence
    for line in data.decode("ascii").splitlines():
        if line.startswith(">"):
            store()
            identifier = line[1:]
            require(identifier and not any(c.isspace() for c in identifier),
                    "Noncanonical identifier")
            chunks = []
        else:
            require(identifier is not None and line, "Malformed FASTA")
            chunks.append(line)
    store()
    require(
        "".join(f">{k}\n{records[k]}\n" for k in sorted(records)).encode("ascii")
        == data,
        "Noncanonical FASTA bytes",
    )
    return records

def manifest(data, id_key, length_key, records, expected_counts):
    reader = csv.DictReader(io.StringIO(data.decode()), delimiter="\t")
    require(reader.fieldnames and len(reader.fieldnames) == len(set(reader.fieldnames)),
            "Invalid manifest header")
    result = {}
    counts = {"positive": 0, "negative": 0}
    for row in reader:
        require(None not in row and all(v is not None for v in row.values()),
                "Malformed manifest row")
        identifier = row[id_key]
        require(identifier not in result and identifier in records, "Manifest membership")
        require(row["class_name"] in counts, "Unexpected label")
        sequence = records[identifier]
        require(len(sequence) == int(row[length_key]) == int(row["frozen_length"]),
                "Length mismatch")
        require(sha(sequence.encode("ascii")) == row["sequence_sha256"],
                "Sequence digest mismatch")
        counts[row["class_name"]] += 1
        result[identifier] = row
    require(set(result) == set(records) and counts == expected_counts,
            "Manifest count mismatch")
    return result

prefix = "experiments/05-family-transfer"
snapshot = json.loads(committed(f"{prefix}/a2_joint_input_snapshot.json"))
inputs = {}
for relative, expected in snapshot["sources"].items():
    inputs[relative] = committed(relative)
    require(sha(inputs[relative]) == expected, "Source digest mismatch")

d = fasta(inputs[f"{prefix}/gate_b_discovery_grouping_archive/canonical_discovery_278.fasta"])
c = fasta(inputs[f"{prefix}/a2_sequence_recovery_archive/confirmatory_sequences.fasta"])
dm = manifest(inputs[f"{prefix}/a1_scan_archive/discovery_sequence_manifest.tsv"],
              "identifier", "retrieved_length", d, {"positive":139, "negative":139})
cm = manifest(inputs[f"{prefix}/a2_sequence_recovery_archive/sequence_manifest.tsv"],
              "accession", "current_length", c, {"positive":161, "negative":3541})

source = (EXP / "run_gate_a2_scan.py").read_text()
tree = ast.parse(source)
gate = [
    node.value.value for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "A2_SCAN_AUTHORIZED"
            for t in node.targets)
    and isinstance(node.value, ast.Constant)
]
require(gate == [False], "Audit requires disabled A2-SS")

# Extract only the pure builder and literal constants; never import the runner.
names = {
    "MAPPING_COLUMNS", "DISCOVERY_NAMESPACE", "CONFIRMATORY_NAMESPACE",
    "EXPECTED_JOINT", "JOINT_FASTA_BYTES", "JOINT_FASTA_SHA256",
    "JOINT_MAPPING_SHA256",
}
namespace = {"require": require, "digest_bytes": sha}

def check_columns(columns):
    require(tuple(columns) == (
        "protein_id", "universe", "class_name", "accession",
        "sequence_length", "sequence_sha256",
    ), "Mapping columns differ from original freeze")

namespace["check_columns"] = check_columns
found = set()
for node in tree.body:
    if (
        isinstance(node, ast.Assign) and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in names
    ):
        name = node.targets[0].id
        namespace[name] = ast.literal_eval(node.value)
        found.add(name)
require(found == names, "Builder constants missing")
builders = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build_joint"]
require(len(builders) == 1, "Builder not unique")
module = ast.Module(body=builders, type_ignores=[])
exec(compile(ast.fix_missing_locations(module), "<pure-build-joint>", "exec"), namespace)

records, index, joint_fasta, mapping = namespace["build_joint"](d, dm, c, cm)
require(len(records) == len(index) == 3980, "Joint membership mismatch")
require(len(joint_fasta) == snapshot["canonical_joint_fasta"]["bytes"] == 1472280,
        "FASTA byte count")
require(sha(joint_fasta) == snapshot["canonical_joint_fasta"]["sha256"],
        "FASTA digest")
require(len(mapping) == snapshot["canonical_mapping"]["bytes"] == 472162,
        "Mapping byte count")
require(sha(mapping) == snapshot["canonical_mapping"]["sha256"]
        == "877b255acc77df84607e546078c42686d4184f0f08b9204892f016f54661a037",
        "Mapping digest")
require(mapping.isascii(), "Mapping is not ASCII")
require(all(len(line.split(b"\t")) == 6 for line in mapping.splitlines()),
        "Mapping row width")

# Reversing insertion order must preserve the exact output.
reverse = lambda value: dict(reversed(list(value.items())))
again = namespace["build_joint"](reverse(d), reverse(dm), reverse(c), reverse(cm))
require(again[2:] == (joint_fasta, mapping), "Serialization depends on input order")

print("PASS — production build_joint reproduces both frozen hashes")
print("PASS — 3,980 mapping rows, six columns, 472,162 bytes")
print("PASS — input insertion order does not affect serialization")
print("A2-SS authorized: NO")
print("Scanner or full runner executed: NO")
