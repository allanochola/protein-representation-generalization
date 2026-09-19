"""Behavioral preauthorization audit for Gate A2-SR."""

import ast
import hashlib
import importlib.util
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"
RUNNER = EXP / "run_gate_a2_sequence_recovery.py"
SCAN_RUNNER = EXP / "run_gate_a2_scan.py"

EXPECTED_INTAKE_SHA = (
    "fe3e3b14bfc70bf79928975156a07fbd"
    "1ccd1e091a2a83880b01dc8e1c247f9e"
)
EXPECTED_HISTORICAL_SHA = (
    "42a08582492ff8ec9cd38604b425e20ee"
    "795c1479f4f3aa47a0949ebf52479e1"
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def gate(source, name):
    values = []

    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, bool)
        ):
            values.append(node.value.value)

    return values


def load_module():
    spec = importlib.util.spec_from_file_location(
        "a2sr_audit",
        RUNNER,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


print("── GATE A2-SR BEHAVIORAL PREAUTHORIZATION AUDIT ──")

source = RUNNER.read_text(encoding="utf-8")
scan_source = SCAN_RUNNER.read_text(encoding="utf-8")

ast.parse(source)
ast.parse(scan_source)

require(
    gate(source, "A2_SEQUENCE_RECOVERY_AUTHORIZED") == [False],
    "A2-SR is not uniquely disabled",
)
require(
    gate(scan_source, "A2_SCAN_AUTHORIZED") == [False],
    "A2-SS is not uniquely disabled",
)

module = load_module()

require(
    module.INTAKE_MANIFEST_SHA256 == EXPECTED_INTAKE_SHA,
    "A2-I manifest identity is not frozen",
)
require(
    module.HISTORICAL_POSITIVE_SHA256
    == EXPECTED_HISTORICAL_SHA,
    "Historical positive identity is not frozen",
)
require(module.EXPECTED_POSITIVES == 161, "Positive count")
require(module.EXPECTED_NEGATIVES == 3541, "Negative count")
require(module.EXPECTED_TOTAL == 3702, "Total count")
require(module.BATCH_SIZE == 100, "Batch size")
require(module.MAX_RETRIES == 5, "Retry count")

ordered = list(
    module.batches(["Z", "A", "M"])
)
require(
    ordered == [("A", "M", "Z")],
    "Accession ordering is not deterministic",
)

synthetic = (
    "Entry\tLength\tSequence\n"
    "P00001\t4\tACDE\n"
    "P00002\t3\tGGG\n"
).encode("utf-8")

parsed = module.parse_uniprot_tsv(synthetic)

require(
    tuple(parsed) == ("P00001", "P00002"),
    "Synthetic response parsing failed",
)
require(
    parsed["P00001"]["sequence"] == "ACDE",
    "Synthetic sequence changed",
)
require(
    parsed["P00002"]["current_length"] == 3,
    "Synthetic length changed",
)

fasta = module.canonical_fasta(
    {
        "P00002": parsed["P00002"],
        "P00001": parsed["P00001"],
    }
)

require(
    fasta == b">P00001\nACDE\n>P00002\nGGG\n",
    "Canonical FASTA serialization failed",
)

required_source_tokens = (
    "SEQUENCE_SNAPSHOT_DRIFT",
    "MISSING_ACCESSION",
    "EXTRA_ACCESSION",
    "MIXED_UNIPROT_RELEASE",
    "LENGTH_MISMATCH",
    "historical_claim_under_test",
    "confirmatory_outcomes_accessed",
    "pfam_scan_performed",
    "mmseqs_clustering_performed",
    "family_geometry_computed",
    "output_sha256",
)

for token in required_source_tokens:
    require(token in source, f"Missing contract token: {token}")

forbidden_capabilities = (
    "hmmscan",
    "hmmpress",
    "easy-cluster",
    "RandomForest",
    "predict_proba",
    "roc_auc",
    "components.tsv",
    "cross_label",
)

lowered = source.casefold()

for token in forbidden_capabilities:
    require(
        token.casefold() not in lowered,
        f"Forbidden A2-SR capability: {token}",
    )

with tempfile.TemporaryDirectory(prefix="a2sr_audit_") as temp:
    temp_path = Path(temp)
    input_path = temp_path / "manifest.tsv"
    historical_path = temp_path / "positive.tsv"

    input_path.write_text(
        "class_name\taccession\tfrozen_length\n"
        "positive\tP1\t4\n"
        "negative\tN1\t3\n",
        encoding="utf-8",
    )
    historical_path.write_text(
        "cluster_rep\trepresentative_length\t"
        "length_stratum_stage1\tannotation_status\n"
        "P1\t4\tx\tassigned\n",
        encoding="utf-8",
    )

    old_manifest = module.INPUT_MANIFEST
    old_historical = module.HISTORICAL_POSITIVE_SOURCE
    old_manifest_hash = module.INTAKE_MANIFEST_SHA256
    old_historical_hash = module.HISTORICAL_POSITIVE_SHA256
    old_positive = module.EXPECTED_POSITIVES
    old_negative = module.EXPECTED_NEGATIVES
    old_total = module.EXPECTED_TOTAL

    try:
        module.INPUT_MANIFEST = input_path
        module.HISTORICAL_POSITIVE_SOURCE = historical_path
        module.INTAKE_MANIFEST_SHA256 = module.digest(input_path)
        module.HISTORICAL_POSITIVE_SHA256 = module.digest(
            historical_path
        )
        module.EXPECTED_POSITIVES = 1
        module.EXPECTED_NEGATIVES = 1
        module.EXPECTED_TOTAL = 2

        intake = module.load_intake_manifest()
        claims = module.load_historical_annotation_claims()

        require(
            intake["P1"]["frozen_length"] == 4,
            "Synthetic intake loading failed",
        )
        require(
            claims == {"P1": "assigned"},
            "Historical claim loading failed",
        )

    finally:
        module.INPUT_MANIFEST = old_manifest
        module.HISTORICAL_POSITIVE_SOURCE = old_historical
        module.INTAKE_MANIFEST_SHA256 = old_manifest_hash
        module.HISTORICAL_POSITIVE_SHA256 = old_historical_hash
        module.EXPECTED_POSITIVES = old_positive
        module.EXPECTED_NEGATIVES = old_negative
        module.EXPECTED_TOTAL = old_total

require(
    not (EXP / "a2_sequence_recovery_archive").exists(),
    "A2-SR output exists before authorization",
)

print("PASS — both A2 scan phases remain disabled")
print("PASS — frozen membership and source identities")
print("PASS — deterministic batching and canonical FASTA")
print("PASS — strict release and snapshot-drift semantics")
print("PASS — historical annotation retained only as a claim")
print("PASS — no scanner, geometry, model or outcome capability")
print("A2-SR authorized: NO")
print("A2-SS authorized: NO")
print("Sequence retrieval performed: NO")
