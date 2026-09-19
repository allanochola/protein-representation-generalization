#!/usr/bin/env python3
"""Gate B discovery-wide grouping runner. Hard-disabled pending authorization."""

import csv
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

GROUPING_AUTHORIZED = False

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"

SOURCE_FASTA = (
    REPO
    / "experiments/03-toxin-representation/"
      "stage1_model_blind/precontact_gate/discovery_sequences.fasta"
)
MANIFEST = EXP / "a1_scan_archive/discovery_sequence_manifest.tsv"
PFAM_HITS = EXP / "a1_scan_archive/accepted_family_hits.tsv"
PFAM_CLANS = EXP / "a1_scan_archive/Pfam-A.clans.tsv.gz"
MMSEQS_SNAPSHOT = EXP / "a1_mmseqs_snapshot.json"
OUTPUT = EXP / "gate_b_discovery_grouping_archive"

SOURCE_FASTA_SHA256 = (
    "ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358"
)
MANIFEST_SHA256 = (
    "7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09"
)

FORBIDDEN_COLUMNS = (
    "auroc",
    "auprc",
    "tpr",
    "fpr",
    "score",
    "prediction",
    "probability",
    "threshold",
    "feature",
    "metric",
)

PARAMETERS = {
    "min_seq_id": "0.30",
    "coverage": "0.80",
    "coverage_mode": "1",
    "cluster_mode": "0",
    "sensitivity": "7.5",
    "threads": "8",
}


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def require_hash(path, expected):
    if not path.is_file():
        raise RuntimeError(f"Missing required input: {path}")
    observed = digest(path)
    if observed != expected:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: {observed} != {expected}"
        )


def resolve_mmseqs_binary(snapshot):
    """Resolve and validate this session's MMseqs2 executable.

    Binary bytes are session identity only. The committed durable identities
    are the source commit, source archive hash, and required version output.
    """
    required_version = snapshot["build"]["required_version_output"]
    source_commit = snapshot["source"]["commit"]

    if required_version != source_commit:
        raise RuntimeError(
            "MMseqs2 snapshot version/commit identity mismatch"
        )

    candidates = []

    configured = os.environ.get("EXP05_MMSEQS_BINARY")
    if configured:
        candidates.append(Path(configured))

    from_path = shutil.which("mmseqs")
    if from_path:
        candidates.append(Path(from_path))

    candidates.append(
        Path(
            "/kaggle/working/"
            "exp05-a1m-tools/install/bin/mmseqs"
        )
    )

    unique_candidates = []
    seen = set()

    for candidate in candidates:
        candidate = candidate.expanduser().resolve()
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)

    diagnostics = []

    for candidate in unique_candidates:
        if not candidate.is_file():
            diagnostics.append(f"{candidate}: absent")
            continue

        result = subprocess.run(
            [str(candidate), "version"],
            text=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        combined = "\n".join(
            part.strip()
            for part in (result.stdout, result.stderr)
            if part.strip()
        )

        if result.returncode != 0:
            diagnostics.append(
                f"{candidate}: version exited {result.returncode}"
            )
            continue

        if required_version not in combined:
            diagnostics.append(
                f"{candidate}: version identity mismatch"
            )
            continue

        return {
            "path": candidate,
            "sha256": digest(candidate),
            "version_output": combined,
        }

    raise RuntimeError(
        "No session MMseqs2 binary satisfies the frozen source identity: "
        + "; ".join(diagnostics)
    )


def read_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check_columns(columns):
    for column in columns:
        lowered = column.lower()
        if any(token in lowered for token in FORBIDDEN_COLUMNS):
            raise RuntimeError(f"Forbidden output column: {column}")


def load_manifest():
    require_hash(MANIFEST, MANIFEST_SHA256)
    rows = read_tsv(MANIFEST)

    required = {
        "class_name",
        "identifier",
        "frozen_length",
        "sequence_sha256",
    }
    if len(rows) != 278 or not rows:
        raise RuntimeError("Discovery manifest must contain exactly 278 rows")
    if not required.issubset(rows[0]):
        raise RuntimeError("Discovery manifest schema mismatch")

    result = {}
    class_counts = defaultdict(int)

    for row in rows:
        identifier = row["identifier"]
        label = row["class_name"]

        if identifier in result:
            raise RuntimeError(f"Duplicate manifest identifier: {identifier}")
        if label not in {"positive", "negative"}:
            raise RuntimeError(f"Unexpected class: {label}")

        result[identifier] = {
            "label": label,
            "length": int(row["frozen_length"]),
            "sequence_sha256": row["sequence_sha256"],
        }
        class_counts[label] += 1

    if dict(class_counts) != {"positive": 139, "negative": 139}:
        raise RuntimeError(f"Unexpected class counts: {dict(class_counts)}")

    return result


def resolve_identifier(header, required):
    tokens = [
        token
        for token in re.split(r"[|\s]+", header.strip())
        if token
    ]
    matches = sorted(set(tokens).intersection(required))

    if len(matches) != 1:
        raise RuntimeError(
            f"FASTA identifier resolution failed for header: {header}"
        )
    return matches[0]


def derive_canonical_fasta(manifest):
    require_hash(SOURCE_FASTA, SOURCE_FASTA_SHA256)

    required = set(manifest)
    records = {}
    header = None
    chunks = []

    def store():
        if header is None:
            return

        identifier = resolve_identifier(header, required)
        sequence = "".join(chunks).replace(" ", "").upper()

        if not sequence:
            raise RuntimeError(f"Empty sequence: {identifier}")
        if identifier in records:
            raise RuntimeError(f"Duplicate FASTA record: {identifier}")
        if len(sequence) != manifest[identifier]["length"]:
            raise RuntimeError(f"Sequence length mismatch: {identifier}")

        observed = hashlib.sha256(sequence.encode("ascii")).hexdigest()
        if observed != manifest[identifier]["sequence_sha256"]:
            raise RuntimeError(f"Sequence SHA-256 mismatch: {identifier}")

        records[identifier] = sequence

    with SOURCE_FASTA.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                store()
                header = line[1:]
                chunks = []
            else:
                if header is None:
                    raise RuntimeError("Sequence before FASTA header")
                chunks.append(line)

    store()

    if set(records) != required:
        raise RuntimeError("FASTA and manifest membership differ")

    data = "".join(
        f">{identifier}\n{records[identifier]}\n"
        for identifier in sorted(records)
    ).encode("ascii")

    return data, tuple(sorted(records))


def load_clan_map():
    mapping = {}

    with gzip.open(PFAM_CLANS, "rt", encoding="utf-8") as handle:
        for raw_line in handle:
            fields = raw_line.rstrip("\n").split("\t")
            if not fields or not fields[0]:
                continue
            family = fields[0]
            clan = fields[1] if len(fields) > 1 else ""
            mapping[family] = clan or family

    if not mapping:
        raise RuntimeError("Empty Pfam clan map")

    return mapping


class UnionFind:
    def __init__(self, members):
        self.parent = {member: member for member in members}
        self.rank = {member: 0 for member in members}

    def find(self, member):
        parent = self.parent[member]
        if parent != member:
            self.parent[member] = self.find(parent)
        return self.parent[member]

    def union(self, left, right):
        left_root = self.find(left)
        right_root = self.find(right)

        if left_root == right_root:
            return

        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root

        self.parent[right_root] = left_root

        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


def parse_cluster_rows(path, expected_members):
    rows = []

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            fields = raw_line.rstrip("\n").split("\t")
            if len(fields) != 2 or not all(fields):
                raise RuntimeError("Malformed MMseqs2 cluster row")
            rows.append(tuple(fields))

    if len(rows) != len(set(rows)):
        raise RuntimeError("Duplicate MMseqs2 row")

    member_to_representative = {}

    for representative, member in rows:
        if member in member_to_representative:
            raise RuntimeError(f"Duplicate member assignment: {member}")
        member_to_representative[member] = representative

    if set(member_to_representative) != set(expected_members):
        raise RuntimeError("MMseqs2 output is not a total 278-record partition")

    if set(member_to_representative.values()) - set(expected_members):
        raise RuntimeError("Unknown MMseqs2 representative")

    canonical = tuple(sorted(rows))

    by_representative = defaultdict(list)
    for member, representative in member_to_representative.items():
        by_representative[representative].append(member)

    stable_partition = {}

    for members in by_representative.values():
        members = tuple(sorted(members))
        cluster_id = hashlib.sha256(
            "\n".join(members).encode("utf-8")
        ).hexdigest()

        for member in members:
            stable_partition[member] = cluster_id

    return canonical, stable_partition


def run_mmseqs_once(binary, fasta, directory):
    directory.mkdir()
    prefix = directory / "clusters"
    temporary = directory / "tmp"
    stdout_path = directory / "stdout"
    stderr_path = directory / "stderr"

    command = [
        str(binary),
        "easy-cluster",
        str(fasta),
        str(prefix),
        str(temporary),
        "--min-seq-id",
        PARAMETERS["min_seq_id"],
        "-c",
        PARAMETERS["coverage"],
        "--cov-mode",
        PARAMETERS["coverage_mode"],
        "--cluster-mode",
        PARAMETERS["cluster_mode"],
        "-s",
        PARAMETERS["sensitivity"],
        "--threads",
        PARAMETERS["threads"],
    ]

    with (
        stdout_path.open("wb") as stdout_handle,
        stderr_path.open("wb") as stderr_handle,
    ):
        subprocess.run(
            command,
            cwd=directory,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=True,
        )

    raw = directory / "clusters_cluster.tsv"
    if not raw.is_file():
        alternate = directory / "clusters.tsv"
        if alternate.is_file():
            raw = alternate
        else:
            raise RuntimeError("MMseqs2 cluster TSV is absent")

    return command, raw, stdout_path, stderr_path


def build_components(manifest, partition):
    members = tuple(sorted(manifest))
    union_find = UnionFind(members)

    by_sequence_cluster = defaultdict(list)
    for protein_id, cluster_id in partition.items():
        by_sequence_cluster[cluster_id].append(protein_id)

    for cluster_members in by_sequence_cluster.values():
        anchor = cluster_members[0]
        for member in cluster_members[1:]:
            union_find.union(anchor, member)

    clans = load_clan_map()
    hits = read_tsv(PFAM_HITS)

    required_hit_columns = {
        "protein_id",
        "pfam_accession",
    }
    if hits and not required_hit_columns.issubset(hits[0]):
        raise RuntimeError("Pfam hit schema mismatch")

    identifiers_by_protein = defaultdict(set)
    proteins_by_identifier = defaultdict(set)

    for row in hits:
        protein_id = row["protein_id"]
        family = row["pfam_accession"]

        if protein_id not in manifest:
            raise RuntimeError(f"Unknown Pfam-hit protein: {protein_id}")
        if not family:
            raise RuntimeError(f"Empty Pfam family for: {protein_id}")

        identifier = clans.get(family, family)
        if not identifier:
            raise RuntimeError(f"Empty clan-first identifier: {protein_id}")

        identifiers_by_protein[protein_id].add(identifier)
        proteins_by_identifier[identifier].add(protein_id)

    for protein_id, identifiers in identifiers_by_protein.items():
        related = set()
        for identifier in identifiers:
            related.update(proteins_by_identifier[identifier])

        for other in related:
            union_find.union(protein_id, other)

    components = defaultdict(list)
    for member in members:
        components[union_find.find(member)].append(member)

    normalized = []
    collisions = []

    for component_members in components.values():
        component_members = tuple(sorted(component_members))
        component_id = hashlib.sha256(
            "\n".join(component_members).encode("utf-8")
        ).hexdigest()
        labels = sorted({
            manifest[member]["label"]
            for member in component_members
        })

        record = {
            "component_id": component_id,
            "member_ids": component_members,
            "labels": tuple(labels),
        }
        normalized.append(record)

        if len(labels) != 1:
            collisions.append(record)

    normalized.sort(key=lambda record: record["component_id"])
    collisions.sort(key=lambda record: record["component_id"])

    return normalized, collisions, identifiers_by_protein


def main():
    if not GROUPING_AUTHORIZED:
        print(
            "STOP: Gate B discovery-wide grouping is not authorized",
            file=sys.stderr,
        )
        return 2

    if OUTPUT.exists():
        raise RuntimeError(
            "Grouping archive already exists; refusing to overwrite"
        )

    # The remaining execution path is intentionally unreachable until a
    # separate authorization commit changes only GROUPING_AUTHORIZED.
    manifest = load_manifest()
    canonical_fasta, members = derive_canonical_fasta(manifest)

    snapshot = json.loads(
        MMSEQS_SNAPSHOT.read_text(encoding="utf-8")
    )
    toolchain = resolve_mmseqs_binary(snapshot)
    binary_path = toolchain["path"]
    observed_binary_hash = toolchain["sha256"]

    with tempfile.TemporaryDirectory(
        prefix="gate_b_discovery_grouping_"
    ) as temporary_name:
        temporary = Path(temporary_name)
        fasta = temporary / "discovery_278.fasta"
        fasta.write_bytes(canonical_fasta)

        command_1, raw_1, stdout_1, stderr_1 = run_mmseqs_once(
            binary_path,
            fasta,
            temporary / "run_1",
        )
        command_2, raw_2, stdout_2, stderr_2 = run_mmseqs_once(
            binary_path,
            fasta,
            temporary / "run_2",
        )

        canonical_1, partition_1 = parse_cluster_rows(raw_1, members)
        canonical_2, partition_2 = parse_cluster_rows(raw_2, members)

        if canonical_1 != canonical_2:
            raise RuntimeError("MMseqs2 canonical-row replay mismatch")
        if partition_1 != partition_2:
            raise RuntimeError("MMseqs2 partition replay mismatch")

        components, collisions, pfam_ids = build_components(
            manifest,
            partition_1,
        )

        OUTPUT.mkdir()

        # Output writing and provenance are implemented before authorization,
        # but no output can be created while the gate remains false.
        (OUTPUT / "canonical_discovery_278.fasta").write_bytes(
            canonical_fasta
        )

        for source, destination in (
            (raw_1, OUTPUT / "run_1_raw_cluster.tsv"),
            (raw_2, OUTPUT / "run_2_raw_cluster.tsv"),
            (stdout_1, OUTPUT / "run_1.stdout"),
            (stdout_2, OUTPUT / "run_2.stdout"),
            (stderr_1, OUTPUT / "run_1.stderr"),
            (stderr_2, OUTPUT / "run_2.stderr"),
        ):
            destination.write_bytes(source.read_bytes())

        cluster_columns = (
            "representative_id",
            "member_id",
        )
        check_columns(cluster_columns)
        with (OUTPUT / "canonical_cluster_rows.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(
                handle,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writerow(cluster_columns)
            writer.writerows(canonical_1)

        partition_columns = (
            "protein_id",
            "sequence_cluster_sha256",
        )
        check_columns(partition_columns)
        with (OUTPUT / "canonical_partition.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(
                handle,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writerow(partition_columns)
            writer.writerows(
                (protein_id, partition_1[protein_id])
                for protein_id in sorted(partition_1)
            )

        pfam_columns = (
            "protein_id",
            "group_identifiers",
        )
        check_columns(pfam_columns)
        with (OUTPUT / "pfam_edges.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(
                handle,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writerow(pfam_columns)
            writer.writerows(
                (
                    protein_id,
                    ";".join(sorted(pfam_ids.get(protein_id, set()))),
                )
                for protein_id in sorted(manifest)
            )

        component_columns = (
            "component_id",
            "class_name",
            "member_count",
            "member_ids",
        )
        check_columns(component_columns)
        with (OUTPUT / "components.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(
                handle,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writerow(component_columns)
            for component in components:
                writer.writerow((
                    component["component_id"],
                    (
                        component["labels"][0]
                        if len(component["labels"]) == 1
                        else "MIXED"
                    ),
                    len(component["member_ids"]),
                    ";".join(component["member_ids"]),
                ))

        collision_columns = (
            "component_id",
            "labels",
            "member_count",
            "member_ids",
        )
        check_columns(collision_columns)
        with (OUTPUT / "collision_report.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(
                handle,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writerow(collision_columns)
            for collision in collisions:
                writer.writerow((
                    collision["component_id"],
                    ";".join(collision["labels"]),
                    len(collision["member_ids"]),
                    ";".join(collision["member_ids"]),
                ))

        summary = {
            "total_records": len(manifest),
            "positive_records": sum(
                row["label"] == "positive"
                for row in manifest.values()
            ),
            "negative_records": sum(
                row["label"] == "negative"
                for row in manifest.values()
            ),
            "component_count": len(components),
            "mixed_label_component_count": len(collisions),
            "status": (
                "MIXED_LABEL_COMPONENT_COLLISION"
                if collisions
                else "GROUPING_READY"
            ),
        }
        (OUTPUT / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        member_hashes = {}
        for path in sorted(OUTPUT.iterdir()):
            if path.name != "grouping_provenance.json":
                member_hashes[path.name] = digest(path)

        provenance = {
            "confirmatory_accessed": False,
            "grouping_rule": (
                "full transitive closure over discovery-wide MMseqs2 "
                "clusters and existing Pfam clan-first/family-fallback edges"
            ),
            "source_fasta_sha256": SOURCE_FASTA_SHA256,
            "manifest_sha256": MANIFEST_SHA256,
            "mmseqs_source_commit": (
                "eec9c354be4276d2373996af2e50808b1390d527"
            ),
            "mmseqs_binary_path": str(binary_path),
            "mmseqs_binary_sha256": observed_binary_hash,
            "mmseqs_version_output": toolchain["version_output"],
            "binary_identity_scope": (
                "session identity only; source commit, source archive "
                "SHA-256, and required version output are durable"
            ),
            "parameters": PARAMETERS,
            "command_1": command_1,
            "command_2": command_2,
            "output_sha256": member_hashes,
        }
        (OUTPUT / "grouping_provenance.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if collisions:
        print(
            "STOP: MIXED_LABEL_COMPONENT_COLLISION",
            file=sys.stderr,
        )
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
