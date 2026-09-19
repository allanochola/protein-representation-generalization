#!/usr/bin/env python3
"""Behavioral preauthorization audit for the amended Gate A1 instrument."""
import ast
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

SNAPSHOT = HERE / "a1_mmseqs_snapshot.json"
ORIGINAL_SCAN = HERE / "run_gate_a1_scan.py"
ORIGINAL_CENSUS = HERE / "run_gate_a1_census.py"
MMSEQS_SCAN = HERE / "run_gate_a1_mmseqs_scan.py"
AMENDED_CENSUS = HERE / "run_gate_a1_amended_census.py"

EXPECTED_SNAPSHOT_SHA = (
    "bbed2977a2a2e1419e8c77d0375e7a563b0b8cc07739085fad03b3475273f1f2"
)
EXPECTED_CANONICAL_FASTA_SHA = (
    "35a18f81eec471904c6bceb8671e7531db1ddaeb610bbf34e8b2f2efa6126878"
)

failures = []


def require(condition, message):
    if not condition:
        failures.append(message)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate_values(source, name):
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


print("── A1-M BEHAVIORAL PREAUTHORIZATION AUDIT ──")

for path in (
    SNAPSHOT,
    ORIGINAL_SCAN,
    ORIGINAL_CENSUS,
    MMSEQS_SCAN,
    AMENDED_CENSUS,
):
    require(path.is_file(), f"Missing required file: {path.name}")

if failures:
    for failure in failures:
        print("FAIL —", failure)
    sys.exit(1)

snapshot_source = SNAPSHOT.read_text(encoding="utf-8")
original_scan_source = ORIGINAL_SCAN.read_text(encoding="utf-8")
original_census_source = ORIGINAL_CENSUS.read_text(encoding="utf-8")
scan_source = MMSEQS_SCAN.read_text(encoding="utf-8")
census_source = AMENDED_CENSUS.read_text(encoding="utf-8")

for name, source in (
    ("original A1-S", original_scan_source),
    ("original A1-C", original_census_source),
    ("A1-M-S", scan_source),
    ("A1-M-C", census_source),
):
    try:
        ast.parse(source)
    except Exception as error:
        failures.append(f"{name} does not parse: {error}")

original_scan_gate = gate_values(
    original_scan_source,
    "SCAN_AUTHORIZED",
)
original_census_gate = gate_values(
    original_census_source,
    "CENSUS_AUTHORIZED",
)
mmseqs_scan_gate = gate_values(
    scan_source,
    "MMSEQS_SCAN_AUTHORIZED",
)
amended_census_gate = gate_values(
    census_source,
    "AMENDED_CENSUS_AUTHORIZED",
)

require(
    original_scan_gate == [False],
    f"Original A1-S is not closed: {original_scan_gate}",
)
require(
    original_census_gate == [False],
    f"Original A1-C is not closed: {original_census_gate}",
)
require(
    len(mmseqs_scan_gate) == 1,
    f"MMSEQS_SCAN_AUTHORIZED is not unique: {mmseqs_scan_gate}",
)
require(
    len(amended_census_gate) == 1,
    "AMENDED_CENSUS_AUTHORIZED is not unique: "
    f"{amended_census_gate}",
)
require(
    not (
        mmseqs_scan_gate == [True]
        and amended_census_gate == [True]
    ),
    "A1-M-S and A1-M-C are simultaneously authorized",
)

require(
    digest(SNAPSHOT) == EXPECTED_SNAPSHOT_SHA,
    "Committed MMseqs2 snapshot SHA-256 drifted",
)

snapshot = json.loads(snapshot_source)

require(
    snapshot["input"]["canonical_positive_fasta_sha256"]
    == EXPECTED_CANONICAL_FASTA_SHA,
    "Canonical FASTA hash drifted",
)
require(
    snapshot["input"]["canonical_positive_fasta_bytes"] == 31481,
    "Canonical FASTA byte count drifted",
)
require(
    snapshot["input"]["canonical_positive_count"] == 139,
    "Canonical positive count drifted",
)
require(
    snapshot["execution_contract"]["independent_runs"] == 2,
    "Two-run replay requirement drifted",
)
require(
    snapshot["execution_contract"]["confirmatory_accessed"] is False,
    "Snapshot does not certify confirmatory_accessed=false",
)

# Phase separation: A1-M-S may scan and partition but cannot route.
for token in (
    "TWO_STAGE_ELIGIBLE",
    "SKIP_STAGE1_NEAR_VACUOUS",
    "AMENDMENT_REQUIRED_CONCENTRATION",
    "largest_component",
    "l_value",
    "0.15",
    "0.25",
):
    require(
        token not in scan_source,
        f"Census/routing token in A1-M-S: {token}",
    )

# A1-M-C may read archives and git tracking state, but cannot scan,
# stage inputs, contact a network, or reach model/probe code.
for token in (
    "easy-cluster",
    "SESSION_MANIFEST",
    "source_fasta_path",
    "urllib",
    "requests",
    "urlopen",
    "socket",
    "esm",
    "sae",
    "seedsequence",
    "probe",
):
    require(
        token.casefold() not in census_source.casefold(),
        f"Forbidden scanner/network/model token in A1-M-C: {token}",
    )

# Every A1-M-C subprocess must be the read-only git ls-files query.
for node in ast.walk(ast.parse(census_source)):
    if not isinstance(node, ast.Call):
        continue

    function = (
        node.func.attr
        if isinstance(node.func, ast.Attribute)
        else node.func.id
        if isinstance(node.func, ast.Name)
        else ""
    )

    if function in {
        "run",
        "check_output",
        "Popen",
        "call",
    }:
        rendered = ast.unparse(node)
        require(
            "git" in rendered and "ls-files" in rendered,
            f"A1-M-C non-git subprocess: {rendered}",
        )

scan_module = load("a1ms_audit", MMSEQS_SCAN)
census_module = load("a1mc_audit", AMENDED_CENSUS)

# The runner itself must derive the frozen FASTA from tracked sources.
try:
    fasta_bytes, identifiers = scan_module.derive_canonical_fasta(
        snapshot
    )
    require(
        len(identifiers) == 139,
        "Runner did not derive exactly 139 positive identifiers",
    )
    require(
        len(fasta_bytes) == 31481,
        "Runner-derived canonical FASTA byte count is wrong",
    )
    require(
        hashlib.sha256(fasta_bytes).hexdigest()
        == EXPECTED_CANONICAL_FASTA_SHA,
        "Runner-derived canonical FASTA hash is wrong",
    )
except Exception as error:
    failures.append(f"Canonical FASTA derivation failed: {error}")

# Synthetic partition canonicalization.
with tempfile.TemporaryDirectory() as temporary_name:
    temporary = Path(temporary_name)

    first = temporary / "first.tsv"
    first.write_text(
        "P1\tP1\n"
        "P1\tP2\n"
        "P3\tP3\n",
        encoding="utf-8",
    )

    second = temporary / "second.tsv"
    second.write_text(
        "P2\tP2\n"
        "P3\tP3\n"
        "P2\tP1\n",
        encoding="utf-8",
    )

    try:
        canonical_first, partition_first = (
            scan_module.parse_partition(
                first,
                ("P1", "P2", "P3"),
            )
        )
        canonical_second, partition_second = (
            scan_module.parse_partition(
                second,
                ("P1", "P2", "P3"),
            )
        )

        require(
            canonical_first != canonical_second,
            "Synthetic representative mutation did not alter row identity",
        )
        require(
            partition_first == partition_second,
            "Stable cluster IDs depend on representative labels",
        )
    except Exception as error:
        failures.append(
            f"Representative-independent partition test failed: {error}"
        )

    missing = temporary / "missing.tsv"
    missing.write_text(
        "P1\tP1\n"
        "P1\tP2\n",
        encoding="utf-8",
    )

    rejected = False
    try:
        scan_module.parse_partition(
            missing,
            ("P1", "P2", "P3"),
        )
    except RuntimeError:
        rejected = True

    require(
        rejected,
        "A1-M-S admitted an incomplete MMseqs2 partition",
    )

# Synthetic amended-census construction over the frozen N=139.
positives = [
    f"P{index:03d}"
    for index in range(139)
]


def empty_pfam():
    return {
        protein: []
        for protein in positives
    }


def singleton_mmseqs():
    return {
        protein: f"C_{protein}"
        for protein in positives
    }


# All singletons: Stage 1 is near-vacuous.
try:
    components, summary = census_module.amended_census(
        positives,
        empty_pfam(),
        singleton_mmseqs(),
    )
    require(
        len(components) == 139,
        "All-singleton component count is wrong",
    )
    require(
        summary["l_value_all_positives"] == 0.0,
        "All-singleton L is not zero",
    )
    require(
        summary["route"] == "SKIP_STAGE1_NEAR_VACUOUS",
        f"All-singleton route is wrong: {summary['route']}",
    )
except Exception as error:
    failures.append(f"All-singleton census failed: {error}")

# Combined-edge transitive closure:
# P000--P001 via MMseqs2 and P001--P002 via Pfam.
try:
    pfam = empty_pfam()
    pfam["P001"] = ["CL_BRIDGE"]
    pfam["P002"] = ["CL_BRIDGE"]

    mmseqs = singleton_mmseqs()
    mmseqs["P000"] = "M_BRIDGE"
    mmseqs["P001"] = "M_BRIDGE"

    components, summary = census_module.amended_census(
        positives,
        pfam,
        mmseqs,
    )

    require(
        any(
            component == ["P000", "P001", "P002"]
            for component in components
        ),
        "Pfam/MMseqs union did not receive transitive closure",
    )
except Exception as error:
    failures.append(f"Combined-edge closure failed: {error}")

# Two-stage route: 18 disjoint pairs = 36 supported positives,
# largest component 2/139, L=36/139.
try:
    mmseqs = singleton_mmseqs()

    for pair_index in range(18):
        left = positives[2 * pair_index]
        right = positives[2 * pair_index + 1]
        cluster = f"PAIR_{pair_index:02d}"
        mmseqs[left] = cluster
        mmseqs[right] = cluster

    _, summary = census_module.amended_census(
        positives,
        empty_pfam(),
        mmseqs,
    )

    require(
        summary["l_value_all_positives"] == 36 / 139,
        "Two-stage synthetic L is wrong",
    )
    require(
        summary["route"] == "TWO_STAGE_ELIGIBLE",
        f"Two-stage route is wrong: {summary['route']}",
    )
except Exception as error:
    failures.append(f"Two-stage routing test failed: {error}")

# Concentration takes precedence over a high L.
try:
    mmseqs = singleton_mmseqs()

    for index in range(22):
        mmseqs[positives[index]] = "GIANT"

    for pair_index in range(22, 58, 2):
        cluster = f"PAIR_{pair_index:03d}"
        mmseqs[positives[pair_index]] = cluster
        mmseqs[positives[pair_index + 1]] = cluster

    _, summary = census_module.amended_census(
        positives,
        empty_pfam(),
        mmseqs,
    )

    require(
        summary["largest_component_share_all_positives"]
        == 22 / 139,
        "Concentration synthetic share is wrong",
    )
    require(
        summary["l_value_all_positives"] >= 0.25,
        "Concentration case did not also exercise the L limb",
    )
    require(
        summary["route"]
        == "AMENDMENT_REQUIRED_CONCENTRATION",
        "Concentration did not take precedence over L",
    )
except Exception as error:
    failures.append(f"Concentration precedence test failed: {error}")

# A missing MMseqs2 member must raise, never route.
try:
    incomplete = singleton_mmseqs()
    incomplete.pop("P138")

    rejected = False
    try:
        census_module.amended_census(
            positives,
            empty_pfam(),
            incomplete,
        )
    except RuntimeError:
        rejected = True

    require(
        rejected,
        "A1-M-C admitted a non-total sequence partition",
    )
except Exception as error:
    failures.append(f"Total-partition rejection test failed: {error}")

require(
    census_module.BANNED_COLUMNS
    == ("auroc", "tpr", "fpr", "score", "threshold"),
    "Amended-census banned-column contract drifted",
)

for forbidden_column in census_module.BANNED_COLUMNS:
    rejected = False

    try:
        census_module.check_columns(
            ("protein_id", forbidden_column)
        )
    except RuntimeError:
        rejected = True

    require(
        rejected,
        f"Schema firewall admitted {forbidden_column}",
    )

require(
    census_module.ROUTES
    == (
        "AMENDMENT_REQUIRED_CONCENTRATION",
        "TWO_STAGE_ELIGIBLE",
        "SKIP_STAGE1_NEAR_VACUOUS",
    ),
    "Amended route token set drifted",
)

if failures:
    print(f"FAIL — {len(failures)} blocking issue(s)")
    for index, failure in enumerate(failures, start=1):
        print(f"{index}. {failure}")
    sys.exit(1)

print("PASS — original phases closed; new phases separated")
print("PASS — canonical FASTA derivation and frozen identity")
print("PASS — total MMseqs2 partition and stable cluster identity")
print("PASS — combined-edge closure and amended routing precedence")
print("PASS — schema firewall and confirmatory separation")
print(
    "A1-M-S authorized:",
    "YES" if mmseqs_scan_gate == [True] else "NO",
)
print(
    "A1-M-C authorized:",
    "YES" if amended_census_gate == [True] else "NO",
)
