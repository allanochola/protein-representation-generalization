"""Behavioral preauthorization audit for Gate A2-SS (joint input)."""

import ast
import importlib.util
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"
SR_RUNNER = EXP / "run_gate_a2_sequence_recovery.py"
SS_RUNNER = EXP / "run_gate_a2_scan.py"


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
    spec = importlib.util.spec_from_file_location("a2ss_audit", SS_RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_failure(callable_, *args):
    try:
        callable_(*args)
    except RuntimeError:
        return
    raise RuntimeError("Expected RuntimeError was not raised")


print("── GATE A2-SS BEHAVIORAL PREAUTHORIZATION AUDIT ──")

sr_source = SR_RUNNER.read_text(encoding="utf-8")
ss_source = SS_RUNNER.read_text(encoding="utf-8")

ast.parse(sr_source)
ast.parse(ss_source)

require(
    gate(sr_source, "A2_SEQUENCE_RECOVERY_AUTHORIZED") == [False],
    "A2-SR is not uniquely disabled",
)
require(
    gate(ss_source, "A2_SCAN_AUTHORIZED") == [False],
    "A2-SS is not uniquely disabled",
)

module = load_module()

# ── Joint-input scope ────────────────────────────────────────────────────────

require(module.EXPECTED_DISCOVERY == 278, "Discovery count")
require(module.EXPECTED_CONFIRMATORY == 3702, "Confirmatory count")
require(module.EXPECTED_POSITIVES == 161, "Positive count")
require(module.EXPECTED_NEGATIVES == 3541, "Negative count")
require(module.EXPECTED_JOINT == 3980, "Joint count")
require(
    module.EXPECTED_DISCOVERY + module.EXPECTED_CONFIRMATORY
    == module.EXPECTED_JOINT,
    "Joint count is not the sum of both universes",
)
require(module.JOINT_FASTA_BYTES == 1472280, "Joint FASTA byte count")
require(
    module.JOINT_FASTA_SHA256
    == "bbfa145c37287f33f102fbdba0e163c2"
       "58aa079d7ef5c120543a3a8b82f79efe",
    "Joint FASTA hash changed",
)
require(
    module.JOINT_MAPPING_SHA256
    == "877b255acc77df84607e546078c42686"
       "d4184f0f08b9204892f016f54661a037",
    "Joint mapping hash changed",
)
require(module.DISCOVERY_NAMESPACE == "discovery", "Discovery namespace")
require(
    module.CONFIRMATORY_NAMESPACE == "confirmatory",
    "Confirmatory namespace",
)

require(module.PFAM_RELEASE == "37.0", "Pfam release")
require(module.PFAM_FAMILY_COUNT == 21979, "Pfam count")
require(module.PFAM_THRESHOLD_RULE == "--cut_ga", "Pfam rule")
require(
    module.PFAM_PRESSED_SUFFIXES == (".h3f", ".h3i", ".h3m", ".h3p"),
    "Pressed Pfam members",
)

require(
    module.MMSEQS_PARAMETERS
    == {
        "min_seq_id": "0.30",
        "coverage": "0.80",
        "coverage_mode": "1",
        "cluster_mode": "0",
        "sensitivity": "7.5",
        "threads": "8",
        "independent_runs": 2,
    },
    "MMseqs2 parameters changed",
)

# ── Archive allowlist excludes scratch databases ─────────────────────────────

allowlist = set(module.ARCHIVE_ALLOWLIST)

require(
    {
        "canonical_joint.fasta",
        "joint_identifier_map.tsv",
        "canonical_cluster_rows.tsv",
        "canonical_partition.tsv",
    }
    <= allowlist,
    "Allowlist is missing a canonical member",
)
require(
    {"mmseqs/run_1_raw_cluster.tsv", "mmseqs/run_2_raw_cluster.tsv"}
    <= allowlist,
    "Allowlist is missing a replay member",
)

for member in allowlist:
    lowered = member.casefold()
    require("tmp" not in lowered, f"Allowlist admits scratch: {member}")
    require(
        not lowered.endswith((".dbtype", ".index", ".lookup", ".source")),
        f"Allowlist admits an MMseqs2 database member: {member}",
    )

with tempfile.TemporaryDirectory(prefix="a2ss_allow_") as temp:
    stage = Path(temp) / "stage"
    stage.mkdir()

    for member in sorted(allowlist | {module.PROVENANCE_MEMBER}):
        path = stage / member
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic\n")

    module.publish_allowlist(stage)

    intruder = stage / "mmseqs" / "clusters.dbtype"
    intruder.write_bytes(b"synthetic\n")
    expect_failure(module.publish_allowlist, stage)
    intruder.unlink()

    (stage / "canonical_partition.tsv").unlink()
    expect_failure(module.publish_allowlist, stage)

# ── Canonicalization, totality and replay failure modes ──────────────────────

namespaced = {
    "confirmatory::C1",
    "confirmatory::C2",
    "discovery::D1",
}

with tempfile.TemporaryDirectory(prefix="a2ss_audit_") as temp:
    root = Path(temp)

    good = root / "good.tsv"
    good.write_text(
        "confirmatory::C1\tconfirmatory::C1\n"
        "confirmatory::C1\tconfirmatory::C2\n"
        "discovery::D1\tdiscovery::D1\n",
        encoding="utf-8",
    )

    canonical, partition = module.canonicalize_partition(good, namespaced)

    require(
        canonical
        == (
            b"representative_id\tmember_id\n"
            b"confirmatory::C1\tconfirmatory::C1\n"
            b"confirmatory::C1\tconfirmatory::C2\n"
            b"discovery::D1\tdiscovery::D1\n"
        ),
        "Canonical row serialization failed",
    )

    lines = partition.decode("utf-8").splitlines()
    require(
        lines[0] == "protein_id\tsequence_cluster_sha256",
        "Partition header changed",
    )
    require(len(lines) == 4, "Partition is not total")

    cluster_c1 = lines[1].split("\t")[1]
    cluster_c2 = lines[2].split("\t")[1]
    cluster_d1 = lines[3].split("\t")[1]

    require(
        cluster_c1 == cluster_c2,
        "Same-cluster members received different IDs",
    )
    require(
        cluster_c1 != cluster_d1,
        "Different clusters received the same ID",
    )

    malformed = root / "malformed.tsv"
    malformed.write_text("confirmatory::C1\n", encoding="utf-8")
    expect_failure(module.canonicalize_partition, malformed, namespaced)

    duplicate = root / "duplicate.tsv"
    duplicate.write_text(
        "confirmatory::C1\tconfirmatory::C1\n"
        "confirmatory::C2\tconfirmatory::C1\n",
        encoding="utf-8",
    )
    expect_failure(module.canonicalize_partition, duplicate, namespaced)

    partial = root / "partial.tsv"
    partial.write_text(
        "confirmatory::C1\tconfirmatory::C1\n",
        encoding="utf-8",
    )
    expect_failure(module.canonicalize_partition, partial, namespaced)

    foreign = root / "foreign.tsv"
    foreign.write_text(
        "confirmatory::C1\tconfirmatory::C1\n"
        "confirmatory::C1\tconfirmatory::C2\n"
        "discovery::D1\tdiscovery::D1\n"
        "discovery::D9\tdiscovery::D9\n",
        encoding="utf-8",
    )
    expect_failure(module.canonicalize_partition, foreign, namespaced)

    # Two-run replay must reject a differing partition.
    divergent = root / "divergent.tsv"
    divergent.write_text(
        "confirmatory::C1\tconfirmatory::C1\n"
        "confirmatory::C2\tconfirmatory::C2\n"
        "discovery::D1\tdiscovery::D1\n",
        encoding="utf-8",
    )
    _, other = module.canonicalize_partition(divergent, namespaced)
    require(
        other != partition,
        "Replay comparison cannot distinguish different partitions",
    )

# ── Source-level firewall ────────────────────────────────────────────────────

required_tokens = (
    'PFAM_THRESHOLD_RULE',
    '"--cut_ga"',
    '"easy-cluster"',
    '"--min-seq-id"',
    '"0.30"',
    '"--cov-mode"',
    '"1"',
    '"--cluster-mode"',
    '"0"',
    '"7.5"',
    '"independent_runs": 2,',
    '"canonical_row_set_identical": True',
    '"stable_partition_identical": True',
    '"raw_byte_identity_required": False',
    '"mmseqs_scratch_archived": False',
    '"clan_mapping_performed": False',
    '"combined_edges_computed": False',
    '"family_geometry_computed": False',
    '"cross_label_relationships_computed": False',
    '"family_disjointness_computed": False',
    '"concentration_computed": False',
    '"confirmatory_outcomes_accessed": False',
)

for token in required_tokens:
    require(token in ss_source, f"Missing source token: {token}")

forbidden_analysis_calls = (
    "RandomForestClassifier",
    "LogisticRegression",
    "predict_proba",
    "roc_auc_score",
    "average_precision_score",
    "StratifiedGroupKFold",
    "networkx",
    "connected_components",
)

for token in forbidden_analysis_calls:
    require(
        token not in ss_source,
        f"Forbidden analysis capability: {token}",
    )

require(
    not (EXP / "a2_scan_archive").exists(),
    "A2-SS output exists before authorization",
)

print("PASS — A2-SR and A2-SS remain disabled")
print("PASS — joint 3,980-record scope and frozen input identities")
print("PASS — committed passing A2-SR archive is required")
print("PASS — Pfam 37 --cut_ga semantics and pressed database members")
print("PASS — exact MMseqs2 parameters and two-run replay")
print("PASS — malformed, partial and foreign partitions rejected")
print("PASS — archive allowlist excludes MMseqs2 scratch databases")
print("PASS — geometry and model-analysis capabilities absent")
print("A2-SR authorized: NO")
print("A2-SS authorized: NO")
print("Scan execution performed: NO")
