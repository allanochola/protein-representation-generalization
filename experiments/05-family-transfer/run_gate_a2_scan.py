"""A2-SS: immutable raw joint Pfam/MMseqs2 scan. Hard-disabled.

Scope (GATE_A2_JOINT_SCAN_AMENDMENT_001):
  - derive the namespaced joint FASTA and identifier mapping in-process and
    reproduce both frozen hashes;
  - verify committed A2-SR recovery inputs and frozen discovery bytes;
  - scan both universes under the frozen Pfam 37 --cut_ga rule and the frozen
    MMseqs2 parameters, with two-run replay on the derived partition;
  - archive only an explicit allowlist, excluding MMseqs2 scratch databases.

It does not map clans, build combined edges, compute components or
concentration, relate labels across universes, or decide family
disjointness. Those remain confined to separately authorized A2-C.
"""

import csv
import gzip
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path


A2_SCAN_AUTHORIZED = False

EXPECTED_DISCOVERY = 278
EXPECTED_CONFIRMATORY = 3702
EXPECTED_POSITIVES = 161
EXPECTED_NEGATIVES = 3541
EXPECTED_JOINT = 3980

DISCOVERY_NAMESPACE = "discovery"
CONFIRMATORY_NAMESPACE = "confirmatory"

JOINT_FASTA_BYTES = 1472280
JOINT_FASTA_SHA256 = (
    "bbfa145c37287f33f102fbdba0e163c2"
    "58aa079d7ef5c120543a3a8b82f79efe"
)
JOINT_MAPPING_SHA256 = (
    "877b255acc77df84607e546078c42686"
    "d4184f0f08b9204892f016f54661a037"
)

DISCOVERY_FASTA_SHA256 = (
    "e54ddf390c9569857663c029ec4679a1"
    "8f4a0384d391c9183f550be3e0ebe94d"
)
DISCOVERY_MANIFEST_SHA256 = (
    "7ac8d253d06ab86b67f2f3d42d7b5ad0"
    "c770360a2d4959dc8d325bed00b9ce09"
)

PFAM_RELEASE = "37.0"
PFAM_FAMILY_COUNT = 21979
PFAM_THRESHOLD_RULE = "--cut_ga"
PFAM_PRESSED_SUFFIXES = (".h3f", ".h3i", ".h3m", ".h3p")

MMSEQS_SOURCE_COMMIT = (
    "eec9c354be4276d2373996af2e50808b1390d527"
)
MMSEQS_SOURCE_ARCHIVE_SHA256 = (
    "de5085207c04902c4b8810ab3092859c"
    "5a8e22ab70d56427f54001be4e554379"
)
MMSEQS_PARAMETERS = {
    "min_seq_id": "0.30",
    "coverage": "0.80",
    "coverage_mode": "1",
    "cluster_mode": "0",
    "sensitivity": "7.5",
    "threads": "8",
    "independent_runs": 2,
}

EXPECTED_SESSION_MANIFEST_SHA256 = (
    "957aef98a65d5dc646cdc33a02fd352bf"
    "8b7d8d0afd9d6c4500013acd8873d2e"
)

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"
RECOVERY = EXP / "a2_sequence_recovery_archive"
OUTPUT = EXP / "a2_scan_archive"

DISCOVERY_FASTA = (
    EXP / "gate_b_discovery_grouping_archive/canonical_discovery_278.fasta"
)
DISCOVERY_MANIFEST = EXP / "a1_scan_archive/discovery_sequence_manifest.tsv"
PFAM_CLANS = EXP / "a1_scan_archive/Pfam-A.clans.tsv.gz"
PFAM_VERSION = EXP / "a1_scan_archive/Pfam.version.gz"

SESSION_ROOT = Path("/kaggle/working/exp05-a2-tools")
SESSION_MANIFEST = SESSION_ROOT / "a2_session_toolchain.json"

BANNED_OUTPUT_COLUMN_TOKENS = (
    "auroc",
    "auprc",
    "tpr",
    "fpr",
    "score",
    "prediction",
    "probability",
    "threshold",
    "embedding",
    "activation",
    "component",
    "concentration",
    "disjoint",
    "cross_label",
)

ARCHIVE_ALLOWLIST = (
    "canonical_joint.fasta",
    "joint_identifier_map.tsv",
    "canonical_cluster_rows.tsv",
    "canonical_partition.tsv",
    "pfam/raw.domtblout",
    "pfam/hmmscan.stdout",
    "pfam/hmmscan.stderr",
    "pfam/accepted_family_hits.tsv",
    "pfam/Pfam-A.clans.tsv.gz",
    "pfam/Pfam.version.gz",
    "mmseqs/run_1_raw_cluster.tsv",
    "mmseqs/run_1.stdout",
    "mmseqs/run_1.stderr",
    "mmseqs/run_2_raw_cluster.tsv",
    "mmseqs/run_2.stdout",
    "mmseqs/run_2.stderr",
)

PROVENANCE_MEMBER = "scan_provenance.json"

MAPPING_COLUMNS = (
    "identifier",
    "universe",
    "class_name",
    "accession",
)

ACCEPTED_HIT_COLUMNS = (
    "identifier",
    "universe",
    "class_name",
    "accession",
    "pfam_accession",
    "model_name",
)


def digest_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def digest(path):
    result = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            result.update(chunk)

    return result.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def require_hash(path, expected):
    actual = digest(path)
    require(
        actual == expected,
        f"SHA-256 mismatch: {path}: {actual} != {expected}",
    )


def write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def tracked(path):
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            str(path.relative_to(REPO)),
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def check_columns(columns):
    for column in columns:
        lowered = column.casefold()

        for token in BANNED_OUTPUT_COLUMN_TOKENS:
            require(
                token not in lowered,
                f"Forbidden output column: {column}",
            )


def read_fasta(path):
    records = {}
    header = None
    chunks = []

    def store():
        if header is None:
            return

        require(
            bool(header)
            and not any(character.isspace() for character in header),
            f"Noncanonical FASTA header: {header!r}",
        )

        sequence = "".join(chunks).upper()
        require(bool(sequence), f"Empty FASTA sequence: {header}")
        require(header not in records, f"Duplicate FASTA identifier: {header}")
        records[header] = sequence

    with path.open("r", encoding="ascii") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")

            if line.startswith(">"):
                store()
                header = line[1:]
                chunks = []
            else:
                require(header is not None, "Sequence before FASTA header")
                chunks.append(line)

    store()
    return records


def load_recovery():
    required_members = {
        "confirmatory_sequences.fasta",
        "sequence_manifest.tsv",
        "historical_annotation_claims.tsv",
        "snapshot_drift.tsv",
        "summary.json",
        "recovery_provenance.json",
    }

    require(RECOVERY.is_dir(), "Committed A2-SR archive is absent")

    provenance_path = RECOVERY / "recovery_provenance.json"
    summary_path = RECOVERY / "summary.json"

    require(
        provenance_path.is_file() and summary_path.is_file(),
        "A2-SR archive is incomplete",
    )

    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    require(provenance.get("status") == "PASS", "A2-SR status is not PASS")
    require(summary.get("status") == "PASS", "A2-SR summary status is not PASS")
    require(
        summary.get("positive_count") == EXPECTED_POSITIVES,
        "A2-SR positive count mismatch",
    )
    require(
        summary.get("negative_count") == EXPECTED_NEGATIVES,
        "A2-SR negative count mismatch",
    )
    require(
        summary.get("recovered_count") == EXPECTED_CONFIRMATORY,
        "A2-SR recovery count mismatch",
    )

    hashes = provenance.get("output_sha256")
    require(
        isinstance(hashes, dict),
        "A2-SR output hash object is absent",
    )

    observed = {path.name for path in RECOVERY.iterdir() if path.is_file()}
    require(
        required_members <= observed,
        "A2-SR required member is absent",
    )

    for relative, expected in hashes.items():
        path = RECOVERY / relative
        require(path.is_file(), f"A2-SR hashed member missing: {relative}")
        require(tracked(path), f"A2-SR member is not committed: {relative}")
        require_hash(path, expected)

    require(
        tracked(provenance_path),
        "A2-SR provenance is not committed",
    )

    return provenance, summary


def load_confirmatory():
    path = RECOVERY / "sequence_manifest.tsv"

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")

        require(
            reader.fieldnames
            == [
                "class_name",
                "accession",
                "frozen_length",
                "current_length",
                "length_matches_frozen",
                "sequence_sha256",
                "uniprot_release",
                "uniprot_release_date",
            ],
            "A2-SR sequence-manifest schema mismatch",
        )

        rows = list(reader)

    require(
        len(rows) == EXPECTED_CONFIRMATORY,
        "A2-SR sequence-manifest count mismatch",
    )

    metadata = {}

    for row in rows:
        accession = row["accession"]
        require(
            accession not in metadata,
            f"Duplicate recovered accession: {accession}",
        )
        require(
            row["length_matches_frozen"] == "true",
            f"Nonmatching recovered length: {accession}",
        )
        metadata[accession] = row

    positives = sum(
        1 for row in metadata.values() if row["class_name"] == "positive"
    )
    negatives = sum(
        1 for row in metadata.values() if row["class_name"] == "negative"
    )
    require(positives == EXPECTED_POSITIVES, "Confirmatory positive count")
    require(negatives == EXPECTED_NEGATIVES, "Confirmatory negative count")

    fasta_path = RECOVERY / "confirmatory_sequences.fasta"
    records = read_fasta(fasta_path)

    require(
        set(records) == set(metadata),
        "Recovered FASTA membership mismatch",
    )

    canonical = "".join(
        f">{accession}\n{records[accession]}\n"
        for accession in sorted(records)
    ).encode("ascii")
    require(
        canonical == fasta_path.read_bytes(),
        "Recovered FASTA is not canonical",
    )

    for accession, sequence in records.items():
        row = metadata[accession]
        require(
            len(sequence) == int(row["current_length"]),
            f"Recovered FASTA length mismatch: {accession}",
        )
        require(
            digest_bytes(sequence.encode("ascii")) == row["sequence_sha256"],
            f"Recovered sequence hash mismatch: {accession}",
        )

    return records, metadata


def load_discovery():
    require_hash(DISCOVERY_FASTA, DISCOVERY_FASTA_SHA256)
    require_hash(DISCOVERY_MANIFEST, DISCOVERY_MANIFEST_SHA256)
    require(tracked(DISCOVERY_FASTA), "Discovery FASTA is not committed")
    require(tracked(DISCOVERY_MANIFEST), "Discovery manifest is not committed")

    with DISCOVERY_MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        require(
            {"class_name", "identifier", "frozen_length", "sequence_sha256"}
            <= set(reader.fieldnames or ()),
            "Discovery manifest schema mismatch",
        )
        rows = list(reader)

    require(
        len(rows) == EXPECTED_DISCOVERY,
        "Discovery manifest count mismatch",
    )

    metadata = {}

    for row in rows:
        accession = row["identifier"]
        require(
            accession not in metadata,
            f"Duplicate discovery accession: {accession}",
        )
        metadata[accession] = row

    records = read_fasta(DISCOVERY_FASTA)
    require(
        set(records) == set(metadata),
        "Discovery FASTA membership mismatch",
    )

    for accession, sequence in records.items():
        row = metadata[accession]
        require(
            len(sequence) == int(row["frozen_length"]),
            f"Discovery length mismatch: {accession}",
        )
        require(
            digest_bytes(sequence.encode("ascii")) == row["sequence_sha256"],
            f"Discovery sequence hash mismatch: {accession}",
        )

    return records, metadata


def build_joint(
    discovery_records,
    discovery_metadata,
    confirmatory_records,
    confirmatory_metadata,
):
    """Derive the namespaced joint FASTA and identifier mapping."""

    check_columns(MAPPING_COLUMNS)

    entries = []

    for accession, sequence in discovery_records.items():
        entries.append(
            (
                f"{DISCOVERY_NAMESPACE}::{accession}",
                DISCOVERY_NAMESPACE,
                discovery_metadata[accession]["class_name"],
                accession,
                sequence,
            )
        )

    for accession, sequence in confirmatory_records.items():
        entries.append(
            (
                f"{CONFIRMATORY_NAMESPACE}::{accession}",
                CONFIRMATORY_NAMESPACE,
                confirmatory_metadata[accession]["class_name"],
                accession,
                sequence,
            )
        )

    require(
        len(entries) == EXPECTED_JOINT,
        f"Joint record count is {len(entries)}, expected {EXPECTED_JOINT}",
    )

    identifiers = [entry[0] for entry in entries]
    require(
        len(set(identifiers)) == len(identifiers),
        "Duplicate namespaced identifier",
    )

    entries.sort(key=lambda entry: entry[0].encode("ascii"))

    fasta = "".join(
        f">{identifier}\n{sequence}\n"
        for identifier, _, _, _, sequence in entries
    ).encode("ascii")

    mapping = (
        "\t".join(MAPPING_COLUMNS)
        + "\n"
        + "".join(
            f"{identifier}\t{universe}\t{class_name}\t{accession}\n"
            for identifier, universe, class_name, accession, _ in entries
        )
    ).encode("utf-8")

    require(
        len(fasta) == JOINT_FASTA_BYTES,
        f"Joint FASTA is {len(fasta)} bytes, expected {JOINT_FASTA_BYTES}",
    )
    require(
        digest_bytes(fasta) == JOINT_FASTA_SHA256,
        "Joint FASTA does not reproduce the frozen hash",
    )
    require(
        digest_bytes(mapping) == JOINT_MAPPING_SHA256,
        "Joint identifier mapping does not reproduce the frozen hash",
    )

    records = {
        identifier: sequence
        for identifier, _, _, _, sequence in entries
    }
    index = {
        identifier: (universe, class_name, accession)
        for identifier, universe, class_name, accession, _ in entries
    }

    return records, index, fasta, mapping


def verify_session():
    require(
        SESSION_MANIFEST.is_file(),
        "Session toolchain manifest is absent",
    )
    require_hash(SESSION_MANIFEST, EXPECTED_SESSION_MANIFEST_SHA256)

    session = json.loads(SESSION_MANIFEST.read_text(encoding="utf-8"))

    identity = session["pfam"]["release_identity"]
    require(
        identity["Pfam release"] == PFAM_RELEASE,
        "Session Pfam release mismatch",
    )
    require(
        int(identity["Pfam-A families"]) == PFAM_FAMILY_COUNT,
        "Session Pfam family count mismatch",
    )
    require(
        session["mmseqs2"]["source_commit"] == MMSEQS_SOURCE_COMMIT,
        "MMseqs2 source commit mismatch",
    )
    require(
        session["mmseqs2"]["source_git_archive_sha256"]
        == MMSEQS_SOURCE_ARCHIVE_SHA256,
        "MMseqs2 source archive mismatch",
    )

    hmmscan = Path(session["hmmer"]["hmmscan_path"])
    mmseqs = Path(session["mmseqs2"]["binary_path"])
    pfam_hmm = Path(
        session["pfam"]["prepared_database"]["Pfam-A.hmm"]["path"]
    )

    for path in (hmmscan, mmseqs, pfam_hmm):
        require(path.is_file(), f"Session tool is absent: {path}")

    require_hash(hmmscan, session["hmmer"]["hmmscan_sha256"])
    require_hash(mmseqs, session["mmseqs2"]["binary_sha256"])
    require_hash(
        pfam_hmm,
        session["pfam"]["prepared_database"]["Pfam-A.hmm"]["sha256"],
    )

    for suffix in PFAM_PRESSED_SUFFIXES:
        pressed = Path(str(pfam_hmm) + suffix)
        require(
            pressed.is_file(),
            f"Pressed Pfam member absent: {pressed}",
        )

    with gzip.open(PFAM_VERSION, "rt") as handle:
        version_text = handle.read()

    require(
        f"Pfam release       : {PFAM_RELEASE}" in version_text
        or f"Pfam release: {PFAM_RELEASE}" in version_text,
        "Archived Pfam release identity mismatch",
    )

    version = subprocess.run(
        [str(mmseqs), "version"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    require(
        version == MMSEQS_SOURCE_COMMIT,
        "MMseqs2 version output mismatch",
    )

    return session, hmmscan, mmseqs, pfam_hmm


def run_hmmscan(hmmscan, pfam_hmm, fasta, directory):
    domtblout = directory / "raw.domtblout"
    stdout_path = directory / "hmmscan.stdout"
    stderr_path = directory / "hmmscan.stderr"

    command = [
        str(hmmscan),
        PFAM_THRESHOLD_RULE,
        "--domtblout",
        str(domtblout),
        str(pfam_hmm),
        str(fasta),
    ]

    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        subprocess.run(
            command,
            cwd=directory,
            stdout=stdout,
            stderr=stderr,
            check=True,
        )

    require(domtblout.is_file(), "hmmscan produced no domtblout")

    return command, domtblout, stdout_path, stderr_path


def accepted_hits(domtblout, index, destination):
    check_columns(ACCEPTED_HIT_COLUMNS)

    rows = []
    seen = set()

    with domtblout.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue

            fields = line.split()
            require(len(fields) >= 23, "Malformed hmmscan domtblout row")

            model_name = fields[0]
            pfam_accession = fields[1]
            identifier = fields[3]

            require(
                identifier in index,
                f"Unknown hmmscan query: {identifier}",
            )

            universe, class_name, accession = index[identifier]
            seen.add(identifier)

            rows.append(
                (
                    identifier,
                    universe,
                    class_name,
                    accession,
                    pfam_accession,
                    model_name,
                )
            )

    rows.sort()

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(ACCEPTED_HIT_COLUMNS)
        writer.writerows(rows)

    return rows, seen


def run_mmseqs(mmseqs, fasta, directory):
    directory.mkdir(parents=True)
    prefix = directory / "clusters"
    temporary = directory / "tmp"
    stdout_path = directory / "stdout"
    stderr_path = directory / "stderr"

    command = [
        str(mmseqs),
        "easy-cluster",
        str(fasta),
        str(prefix),
        str(temporary),
        "--min-seq-id",
        MMSEQS_PARAMETERS["min_seq_id"],
        "-c",
        MMSEQS_PARAMETERS["coverage"],
        "--cov-mode",
        MMSEQS_PARAMETERS["coverage_mode"],
        "--cluster-mode",
        MMSEQS_PARAMETERS["cluster_mode"],
        "-s",
        MMSEQS_PARAMETERS["sensitivity"],
        "--threads",
        MMSEQS_PARAMETERS["threads"],
    ]

    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
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
        require(alternative.is_file(), "MMseqs2 cluster TSV is absent")
        raw = alternative

    return command, raw, stdout_path, stderr_path


def canonicalize_partition(raw_path, expected_members):
    rows = []

    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            require(
                len(fields) == 2 and all(fields),
                "Malformed MMseqs2 cluster row",
            )
            rows.append(tuple(fields))

    require(len(rows) == len(set(rows)), "Duplicate MMseqs2 cluster row")

    member_to_representative = {}

    for representative, member in rows:
        require(
            member not in member_to_representative,
            f"Duplicate MMseqs2 member: {member}",
        )
        member_to_representative[member] = representative

    require(
        set(member_to_representative) == set(expected_members),
        "MMseqs2 output is not a total partition",
    )
    require(
        not (
            set(member_to_representative.values()) - set(expected_members)
        ),
        "Unknown MMseqs2 representative",
    )

    canonical_rows = (
        "representative_id\tmember_id\n"
        + "".join(
            f"{representative}\t{member}\n"
            for representative, member in sorted(rows)
        )
    ).encode("utf-8")

    groups = defaultdict(list)

    for member, representative in member_to_representative.items():
        groups[representative].append(member)

    partition_rows = []

    for members in groups.values():
        ordered = sorted(members)
        cluster_id = digest_bytes("\n".join(ordered).encode("utf-8"))

        for member in ordered:
            partition_rows.append((member, cluster_id))

    partition_rows.sort()

    partition = (
        "protein_id\tsequence_cluster_sha256\n"
        + "".join(
            f"{member}\t{cluster_id}\n"
            for member, cluster_id in partition_rows
        )
    ).encode("utf-8")

    return canonical_rows, partition


def publish_allowlist(stage):
    """Reject any staged file outside the allowlist; require every member."""

    observed = {
        str(path.relative_to(stage))
        for path in stage.rglob("*")
        if path.is_file()
    }
    allowed = set(ARCHIVE_ALLOWLIST) | {PROVENANCE_MEMBER}

    unexpected = sorted(observed - allowed)
    require(not unexpected, f"Unexpected archive member: {unexpected}")

    missing = sorted(allowed - observed)
    require(not missing, f"Missing archive member: {missing}")

    return observed


def main():
    if not A2_SCAN_AUTHORIZED:
        raise SystemExit("STOP: Gate A2 raw scan is not authorized")

    require(
        not OUTPUT.exists(),
        "A2-SS output exists; refusing to overwrite",
    )

    recovery_provenance, recovery_summary = load_recovery()
    confirmatory_records, confirmatory_metadata = load_confirmatory()
    discovery_records, discovery_metadata = load_discovery()

    joint_records, index, joint_fasta, joint_mapping = build_joint(
        discovery_records,
        discovery_metadata,
        confirmatory_records,
        confirmatory_metadata,
    )

    session, hmmscan, mmseqs, pfam_hmm = verify_session()

    # Scratch lives OUTSIDE the stage so MMseqs2 databases are never
    # archivable; the stage lives under OUTPUT.parent so publication by
    # rename stays on the destination filesystem.
    with tempfile.TemporaryDirectory(prefix="exp05_a2ss_scratch_") as scratch:
        scratch_root = Path(scratch)

        with tempfile.TemporaryDirectory(
            prefix="exp05_a2ss_",
            dir=OUTPUT.parent,
        ) as temporary:
            stage = Path(temporary) / OUTPUT.name
            stage.mkdir()

            fasta_path = stage / "canonical_joint.fasta"
            fasta_path.write_bytes(joint_fasta)
            (stage / "joint_identifier_map.tsv").write_bytes(joint_mapping)

            pfam_directory = stage / "pfam"
            pfam_directory.mkdir()

            (
                hmmscan_command,
                domtblout,
                hmmscan_stdout,
                hmmscan_stderr,
            ) = run_hmmscan(hmmscan, pfam_hmm, fasta_path, pfam_directory)

            hit_rows, scanned = accepted_hits(
                domtblout,
                index,
                pfam_directory / "accepted_family_hits.tsv",
            )

            shutil.copy2(
                PFAM_CLANS,
                pfam_directory / "Pfam-A.clans.tsv.gz",
            )
            shutil.copy2(
                PFAM_VERSION,
                pfam_directory / "Pfam.version.gz",
            )

            mmseqs_directory = stage / "mmseqs"
            mmseqs_directory.mkdir()

            run_outputs = []

            for run_index in (1, 2):
                (
                    command,
                    raw,
                    stdout_path,
                    stderr_path,
                ) = run_mmseqs(
                    mmseqs,
                    fasta_path,
                    scratch_root / f"mmseqs_run_{run_index}",
                )

                canonical_rows, partition = canonicalize_partition(
                    raw,
                    joint_records,
                )

                shutil.copy2(
                    raw,
                    mmseqs_directory / f"run_{run_index}_raw_cluster.tsv",
                )
                shutil.copy2(
                    stdout_path,
                    mmseqs_directory / f"run_{run_index}.stdout",
                )
                shutil.copy2(
                    stderr_path,
                    mmseqs_directory / f"run_{run_index}.stderr",
                )

                run_outputs.append(
                    {
                        "index": run_index,
                        "command": command,
                        "canonical_rows": canonical_rows,
                        "partition": partition,
                    }
                )

            require(
                run_outputs[0]["canonical_rows"]
                == run_outputs[1]["canonical_rows"],
                "MMseqs2 canonical row replay mismatch",
            )
            require(
                run_outputs[0]["partition"] == run_outputs[1]["partition"],
                "MMseqs2 partition replay mismatch",
            )

            (stage / "canonical_cluster_rows.tsv").write_bytes(
                run_outputs[0]["canonical_rows"]
            )
            (stage / "canonical_partition.tsv").write_bytes(
                run_outputs[0]["partition"]
            )

            provenance = {
                "schema": "exp05_gate_a2_joint_raw_scan_v1",
                "confirmatory_metadata_accessed": True,
                "confirmatory_sequence_accessed": True,
                "confirmatory_outcomes_accessed": False,
                "scan_input_scope": "joint discovery + confirmatory",
                "joint_record_count": EXPECTED_JOINT,
                "discovery_record_count": EXPECTED_DISCOVERY,
                "confirmatory_record_count": EXPECTED_CONFIRMATORY,
                "joint_fasta_sha256": JOINT_FASTA_SHA256,
                "joint_fasta_bytes": JOINT_FASTA_BYTES,
                "joint_identifier_map_sha256": JOINT_MAPPING_SHA256,
                "namespaces": [
                    DISCOVERY_NAMESPACE,
                    CONFIRMATORY_NAMESPACE,
                ],
                "discovery_fasta_sha256": DISCOVERY_FASTA_SHA256,
                "discovery_manifest_sha256": DISCOVERY_MANIFEST_SHA256,
                "recovery_provenance_sha256": digest(
                    RECOVERY / "recovery_provenance.json"
                ),
                "recovery_summary_sha256": digest(RECOVERY / "summary.json"),
                "recovery_status": recovery_summary["status"],
                "pfam_release": PFAM_RELEASE,
                "pfam_family_count": PFAM_FAMILY_COUNT,
                "pfam_threshold_rule": PFAM_THRESHOLD_RULE,
                "hmmscan_command": hmmscan_command,
                "accepted_hit_rows": len(hit_rows),
                "queries_with_accepted_hits": len(scanned),
                "mmseqs_source_commit": MMSEQS_SOURCE_COMMIT,
                "mmseqs_parameters": MMSEQS_PARAMETERS,
                "mmseqs_commands": [
                    output["command"] for output in run_outputs
                ],
                "mmseqs_replay": {
                    "canonical_row_set_identical": True,
                    "stable_partition_identical": True,
                    "raw_byte_identity_required": False,
                },
                "archive_allowlist": list(ARCHIVE_ALLOWLIST),
                "mmseqs_scratch_archived": False,
                "clan_mapping_performed": False,
                "combined_edges_computed": False,
                "family_geometry_computed": False,
                "cross_label_relationships_computed": False,
                "family_disjointness_computed": False,
                "concentration_computed": False,
                "session_manifest_sha256": (
                    EXPECTED_SESSION_MANIFEST_SHA256
                ),
                "session_binary_identity": {
                    "hmmscan_sha256": session["hmmer"]["hmmscan_sha256"],
                    "mmseqs_sha256": session["mmseqs2"]["binary_sha256"],
                    "scope": (
                        "session identity only; commensurability with A1-M "
                        "and Gate B rests on source-commit identity, not on "
                        "binary bytes"
                    ),
                },
                "output_sha256": {},
            }

            hashes = {
                relative: digest(stage / relative)
                for relative in sorted(ARCHIVE_ALLOWLIST)
            }
            provenance["output_sha256"] = hashes

            write_json(stage / PROVENANCE_MEMBER, provenance)

            publish_allowlist(stage)

            stage.rename(OUTPUT)


if __name__ == "__main__":
    main()
