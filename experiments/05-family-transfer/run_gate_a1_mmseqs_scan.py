#!/usr/bin/env python3
"""A1-M-S: authorized two-run MMseqs2 immutable archive phase; not yet executed."""
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

MMSEQS_SCAN_AUTHORIZED = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SNAPSHOT = HERE / "a1_mmseqs_snapshot.json"
ARCHIVE = HERE / "a1_mmseqs_scan_archive"
SESSION_MANIFEST = Path(
    "/kaggle/working/exp05-a1m-tools/session_toolchain.json"
)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def require_hash(path, expected):
    observed = digest(path)
    if observed != expected:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: {observed}"
        )


def load_positive_manifest(snapshot):
    spec = snapshot["input"]
    path = REPO / spec["manifest_path"]
    require_hash(path, spec["manifest_sha256"])

    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    positives = {
        row["identifier"]: row["sequence_sha256"]
        for row in rows
        if row["class_name"] == "positive"
    }

    if len(rows) != 278 or len(positives) != 139:
        raise RuntimeError("Discovery manifest count gate failed")

    return positives


def resolve_identifier(header, required):
    token = header.split()[0]
    candidates = {token, token.split(".")[0]}

    for part in token.split("|"):
        if part:
            candidates.add(part)
            candidates.add(part.split(".")[0])

    matches = sorted(candidates & required)

    if len(matches) > 1:
        raise RuntimeError(
            "FASTA header resolves to multiple positive identifiers"
        )

    return matches[0] if matches else None


def derive_canonical_fasta(snapshot):
    spec = snapshot["input"]
    source = REPO / spec["source_fasta_path"]
    require_hash(source, spec["source_fasta_sha256"])

    expected = load_positive_manifest(snapshot)
    required = set(expected)
    records = {}
    header = None
    chunks = []

    def store():
        if header is None:
            return

        identifier = resolve_identifier(header, required)
        if identifier is None:
            return

        sequence = "".join(chunks).replace(" ", "").upper()

        if not sequence:
            raise RuntimeError(f"Empty sequence: {identifier}")
        if identifier in records:
            raise RuntimeError(f"Duplicate sequence: {identifier}")

        sequence_hash = hashlib.sha256(
            sequence.encode("ascii")
        ).hexdigest()

        if sequence_hash != expected[identifier]:
            raise RuntimeError(
                f"Sequence hash mismatch: {identifier}"
            )

        records[identifier] = sequence

    with source.open("r", encoding="utf-8") as handle:
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
                    raise RuntimeError(
                        "Sequence appeared before FASTA header"
                    )
                chunks.append(line)

    store()

    if set(records) != required:
        raise RuntimeError("Canonical FASTA membership mismatch")

    # Frozen byte-level ordering and serialization rule.
    data = "".join(
        f">{identifier}\n{records[identifier]}\n"
        for identifier in sorted(records)
    ).encode("ascii")

    if len(data) != spec["canonical_positive_fasta_bytes"]:
        raise RuntimeError("Canonical FASTA byte-count mismatch")

    if (
        hashlib.sha256(data).hexdigest()
        != spec["canonical_positive_fasta_sha256"]
    ):
        raise RuntimeError("Canonical FASTA SHA-256 mismatch")

    return data, tuple(sorted(records))


def verify_toolchain(snapshot):
    if not SESSION_MANIFEST.is_file():
        raise RuntimeError("Session toolchain manifest is missing")

    session = json.loads(
        SESSION_MANIFEST.read_text(encoding="utf-8")
    )

    if session["source_commit"] != snapshot["source"]["commit"]:
        raise RuntimeError("MMseqs2 source commit mismatch")

    if (
        session["source_archive_sha256"]
        != snapshot["source"]["git_archive_sha256"]
    ):
        raise RuntimeError("MMseqs2 source archive mismatch")

    binary = Path(session["binary_path"]).resolve()

    if not binary.is_file():
        raise RuntimeError("MMseqs2 binary is missing")

    if digest(binary) != session["binary_sha256"]:
        raise RuntimeError("MMseqs2 session binary hash mismatch")

    version = subprocess.run(
        [str(binary), "version"],
        text=True,
        check=True,
        capture_output=True,
    ).stdout.strip()

    if version != snapshot["build"]["required_version_output"]:
        raise RuntimeError(f"MMseqs2 version mismatch: {version}")

    return binary, session


def parse_partition(raw_path, expected_members):
    rows = []

    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 2 or not all(fields):
                raise RuntimeError("Malformed MMseqs2 cluster row")
            rows.append(tuple(fields))

    if len(rows) != len(set(rows)):
        raise RuntimeError("Duplicate MMseqs2 cluster row")

    member_to_representative = {}

    for representative, member in rows:
        if member in member_to_representative:
            raise RuntimeError(
                f"Duplicate MMseqs2 member assignment: {member}"
            )
        member_to_representative[member] = representative

    if set(member_to_representative) != set(expected_members):
        raise RuntimeError(
            "MMseqs2 output is not a total positive partition"
        )

    if (
        set(member_to_representative.values())
        - set(expected_members)
    ):
        raise RuntimeError("Unknown MMseqs2 representative")

    canonical_rows = "".join(
        f"{representative}\t{member}\n"
        for representative, member in sorted(rows)
    ).encode("utf-8")

    by_representative = defaultdict(list)
    for member, representative in member_to_representative.items():
        by_representative[representative].append(member)

    partition = []

    for members in by_representative.values():
        members = sorted(members)
        stable_cluster_id = hashlib.sha256(
            "\n".join(members).encode("utf-8")
        ).hexdigest()

        partition.extend(
            (member, stable_cluster_id)
            for member in members
        )

    partition.sort()

    partition_bytes = (
        "protein_id\tcluster_sha256\n"
        + "".join(
            f"{member}\t{cluster_id}\n"
            for member, cluster_id in partition
        )
    ).encode("utf-8")

    return canonical_rows, partition_bytes


def run_once(binary, fasta, directory, parameters):
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
        str(parameters["min_seq_id"]),
        "-c",
        str(parameters["coverage"]),
        "--cov-mode",
        str(parameters["coverage_mode"]),
        "--cluster-mode",
        str(parameters["cluster_mode"]),
        "-s",
        str(parameters["sensitivity"]),
        "--threads",
        str(parameters["threads"]),
    ]

    with (
        stdout_path.open("wb") as stdout,
        stderr_path.open("wb") as stderr,
    ):
        subprocess.run(
            command,
            cwd=directory,
            stdout=stdout,
            stderr=stderr,
            check=True,
        )

    raw = directory / "clusters_cluster.tsv"
    if not raw.is_file():
        alternative = directory / "clusters.tsv"
        if alternative.is_file():
            raw = alternative
        else:
            raise RuntimeError("MMseqs2 cluster TSV is missing")

    return command, raw, stdout_path, stderr_path


def main():
    if not MMSEQS_SCAN_AUTHORIZED:
        raise RuntimeError("A1-M-S is not authorized")

    if ARCHIVE.exists():
        raise RuntimeError("A1-M-S archive already exists")

    snapshot = json.loads(
        SNAPSHOT.read_text(encoding="utf-8")
    )
    fasta_bytes, members = derive_canonical_fasta(snapshot)
    binary, session = verify_toolchain(snapshot)
    parameters = snapshot["scientific_definition"]

    with tempfile.TemporaryDirectory(
        prefix="a1ms_",
        dir=HERE,
    ) as temp_name:
        work = Path(temp_name)
        fasta = work / "canonical_positive.fasta"
        fasta.write_bytes(fasta_bytes)

        results = []

        for index in (1, 2):
            command, raw, stdout, stderr = run_once(
                binary,
                fasta,
                work / f"run_{index}",
                parameters,
            )
            canonical, partition = parse_partition(raw, members)
            results.append({
                "command": command,
                "raw": raw,
                "stdout": stdout,
                "stderr": stderr,
                "canonical": canonical,
                "partition": partition,
            })

        if results[0]["canonical"] != results[1]["canonical"]:
            raise RuntimeError(
                "REPAIRABLE_IMPLEMENTATION_FAILURE: "
                "canonical row sets differ"
            )

        if results[0]["partition"] != results[1]["partition"]:
            raise RuntimeError(
                "REPAIRABLE_IMPLEMENTATION_FAILURE: "
                "partitions differ"
            )

        stage = work / "archive"
        stage.mkdir()

        shutil.copy2(
            fasta,
            stage / "canonical_positive.fasta",
        )

        for index, result in enumerate(results, start=1):
            shutil.copy2(
                result["raw"],
                stage / f"run_{index}_raw_cluster.tsv",
            )
            shutil.copy2(
                result["stdout"],
                stage / f"run_{index}.stdout",
            )
            shutil.copy2(
                result["stderr"],
                stage / f"run_{index}.stderr",
            )

        (stage / "canonical_cluster_rows.tsv").write_bytes(
            results[0]["canonical"]
        )
        (stage / "canonical_partition.tsv").write_bytes(
            results[0]["partition"]
        )

        file_hashes = {
            path.name: digest(path)
            for path in sorted(stage.iterdir())
        }

        provenance = {
            "confirmatory_accessed": False,
            "snapshot_sha256": digest(SNAPSHOT),
            "source_commit": snapshot["source"]["commit"],
            "source_archive_sha256": (
                snapshot["source"]["git_archive_sha256"]
            ),
            "mmseqs_version": session["mmseqs_version"],
            "session_binary_sha256": session["binary_sha256"],
            "binary_hash_claim": (
                "session identity only; not a reproducible-build guarantee"
            ),
            "scientific_definition": parameters,
            "commands": [
                result["command"]
                for result in results
            ],
            "replay_gate": {
                "independent_runs": 2,
                "canonical_row_sets_identical": True,
                "partitions_identical": True,
            },
            "file_sha256": file_hashes,
        }

        (stage / "scan_provenance.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )

        stage.rename(ARCHIVE)


if __name__ == "__main__":
    main()
