"""A2-SS: immutable raw Pfam/MMseqs2 scan. Hard-disabled."""

import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path


A2_SCAN_AUTHORIZED = False

EXPECTED_TOTAL = 3702
EXPECTED_POSITIVES = 161
EXPECTED_NEGATIVES = 3541

PFAM_RELEASE = "37.0"
PFAM_FAMILY_COUNT = 21979
PFAM_THRESHOLD_RULE = "--cut_ga"

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

SESSION_ROOT = Path("/kaggle/working/exp05-a2-tools")
SESSION_MANIFEST = SESSION_ROOT / "a2_session_toolchain.json"

PFAM_CLANS = EXP / "a1_scan_archive/Pfam-A.clans.tsv.gz"
PFAM_VERSION = EXP / "a1_scan_archive/Pfam.version.gz"

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


def digest(path):
    result = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            result.update(chunk)

    return result.hexdigest()


def require_hash(path, expected):
    actual = digest(path)

    if actual != expected:
        raise RuntimeError(
            f"SHA-256 mismatch: {path}: {actual} != {expected}"
        )


def write_json(path, value):
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def tracked(path):
    relative = str(path.relative_to(REPO))

    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            relative,
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
            if token in lowered:
                raise RuntimeError(
                    f"Forbidden output column: {column}"
                )


def load_recovery():
    required = {
        "confirmatory_sequences.fasta",
        "sequence_manifest.tsv",
        "historical_annotation_claims.tsv",
        "snapshot_drift.tsv",
        "summary.json",
        "recovery_provenance.json",
    }

    if not RECOVERY.is_dir():
        raise RuntimeError(
            "Committed A2-SR archive is absent"
        )

    provenance_path = RECOVERY / "recovery_provenance.json"
    summary_path = RECOVERY / "summary.json"

    if not provenance_path.is_file() or not summary_path.is_file():
        raise RuntimeError("A2-SR archive is incomplete")

    provenance = json.loads(
        provenance_path.read_text(encoding="utf-8")
    )
    summary = json.loads(
        summary_path.read_text(encoding="utf-8")
    )

    if provenance.get("status") != "PASS":
        raise RuntimeError(
            "A2-SR status is not PASS"
        )

    if summary.get("status") != "PASS":
        raise RuntimeError(
            "A2-SR summary status is not PASS"
        )

    if summary.get("positive_count") != EXPECTED_POSITIVES:
        raise RuntimeError("A2-SR positive count mismatch")

    if summary.get("negative_count") != EXPECTED_NEGATIVES:
        raise RuntimeError("A2-SR negative count mismatch")

    if summary.get("recovered_count") != EXPECTED_TOTAL:
        raise RuntimeError("A2-SR recovery count mismatch")

    hashes = provenance.get("output_sha256")

    if not isinstance(hashes, dict):
        raise RuntimeError(
            "A2-SR output hash object is absent"
        )

    observed_top_level = {
        path.name
        for path in RECOVERY.iterdir()
        if path.is_file()
    }

    if not required <= observed_top_level:
        raise RuntimeError(
            "A2-SR required member is absent"
        )

    for relative, expected in hashes.items():
        path = RECOVERY / relative

        if not path.is_file():
            raise RuntimeError(
                f"A2-SR hashed member missing: {relative}"
            )

        if not tracked(path):
            raise RuntimeError(
                f"A2-SR member is not committed: {relative}"
            )

        require_hash(path, expected)

    if not tracked(provenance_path):
        raise RuntimeError(
            "A2-SR provenance is not committed"
        )

    return provenance, summary


def load_sequence_manifest():
    path = RECOVERY / "sequence_manifest.tsv"

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle, delimiter="\t")

        expected = [
            "class_name",
            "accession",
            "frozen_length",
            "current_length",
            "length_matches_frozen",
            "sequence_sha256",
            "uniprot_release",
            "uniprot_release_date",
        ]

        if reader.fieldnames != expected:
            raise RuntimeError(
                "A2-SR sequence-manifest schema mismatch"
            )

        rows = list(reader)

    if len(rows) != EXPECTED_TOTAL:
        raise RuntimeError(
            "A2-SR sequence-manifest count mismatch"
        )

    records = {}

    for row in rows:
        accession = row["accession"]

        if accession in records:
            raise RuntimeError(
                f"Duplicate recovered accession: {accession}"
            )

        if row["length_matches_frozen"] != "true":
            raise RuntimeError(
                f"Nonmatching recovered length: {accession}"
            )

        records[accession] = row

    return records


def read_fasta(path):
    records = {}
    header = None
    chunks = []

    def store():
        if header is None:
            return

        if not header or any(character.isspace() for character in header):
            raise RuntimeError(
                f"Noncanonical FASTA header: {header!r}"
            )

        sequence = "".join(chunks).upper()

        if not sequence:
            raise RuntimeError(
                f"Empty FASTA sequence: {header}"
            )

        if header in records:
            raise RuntimeError(
                f"Duplicate FASTA identifier: {header}"
            )

        records[header] = sequence

    with path.open("r", encoding="ascii") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")

            if line.startswith(">"):
                store()
                header = line[1:]
                chunks = []
            else:
                if header is None:
                    raise RuntimeError(
                        "Sequence before FASTA header"
                    )
                chunks.append(line)

    store()
    return records


def verify_recovered_sequences(manifest):
    fasta_path = RECOVERY / "confirmatory_sequences.fasta"
    records = read_fasta(fasta_path)

    if set(records) != set(manifest):
        raise RuntimeError(
            "Recovered FASTA membership mismatch"
        )

    canonical = "".join(
        f">{accession}\n{records[accession]}\n"
        for accession in sorted(records)
    ).encode("ascii")

    if canonical != fasta_path.read_bytes():
        raise RuntimeError(
            "Recovered FASTA is not canonical"
        )

    for accession, sequence in records.items():
        row = manifest[accession]

        if len(sequence) != int(row["current_length"]):
            raise RuntimeError(
                f"Recovered FASTA length mismatch: {accession}"
            )

        sequence_hash = hashlib.sha256(
            sequence.encode("ascii")
        ).hexdigest()

        if sequence_hash != row["sequence_sha256"]:
            raise RuntimeError(
                f"Recovered sequence hash mismatch: {accession}"
            )

    return records


def verify_session():
    require_hash(
        SESSION_MANIFEST,
        EXPECTED_SESSION_MANIFEST_SHA256,
    )

    session = json.loads(
        SESSION_MANIFEST.read_text(encoding="utf-8")
    )

    if (
        session["pfam"]["release_identity"]["Pfam release"]
        != PFAM_RELEASE
    ):
        raise RuntimeError("Session Pfam release mismatch")

    if int(
        session["pfam"]["release_identity"]["Pfam-A families"]
    ) != PFAM_FAMILY_COUNT:
        raise RuntimeError("Session Pfam family count mismatch")

    if (
        session["mmseqs2"]["source_commit"]
        != MMSEQS_SOURCE_COMMIT
    ):
        raise RuntimeError("MMseqs2 source commit mismatch")

    if (
        session["mmseqs2"]["source_git_archive_sha256"]
        != MMSEQS_SOURCE_ARCHIVE_SHA256
    ):
        raise RuntimeError("MMseqs2 source archive mismatch")

    hmmscan = Path(session["hmmer"]["hmmscan_path"])
    mmseqs = Path(session["mmseqs2"]["binary_path"])
    pfam_hmm = Path(
        session["pfam"]["prepared_database"][
            "Pfam-A.hmm"
        ]["path"]
    )

    for path in (hmmscan, mmseqs, pfam_hmm):
        if not path.is_file():
            raise RuntimeError(
                f"Session tool is absent: {path}"
            )

    require_hash(
        hmmscan,
        session["hmmer"]["hmmscan_sha256"],
    )
    require_hash(
        mmseqs,
        session["mmseqs2"]["binary_sha256"],
    )
    require_hash(
        pfam_hmm,
        session["pfam"]["prepared_database"][
            "Pfam-A.hmm"
        ]["sha256"],
    )

    for suffix in (".h3f", ".h3i", ".h3m", ".h3p"):
        pressed = Path(str(pfam_hmm) + suffix)

        if not pressed.is_file():
            raise RuntimeError(
                f"Pressed Pfam member absent: {pressed}"
            )

    version = subprocess.run(
        [str(mmseqs), "version"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()

    if version != MMSEQS_SOURCE_COMMIT:
        raise RuntimeError(
            "MMseqs2 version output mismatch"
        )

    return session, hmmscan, mmseqs, pfam_hmm


def run_hmmscan(
    hmmscan,
    pfam_hmm,
    fasta,
    directory,
):
    domtblout = directory / "raw.domtblout"
    stdout_path = directory / "hmmscan.stdout"
    stderr_path = directory / "hmmscan.stderr"

    command = [
        str(hmmscan),
        "--cut_ga",
        "--domtblout",
        str(domtblout),
        str(pfam_hmm),
        str(fasta),
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

    if not domtblout.is_file():
        raise RuntimeError(
            "hmmscan produced no domtblout"
        )

    return command, domtblout, stdout_path, stderr_path


def accepted_hits(domtblout, manifest, destination):
    columns = (
        "class_name",
        "protein_id",
        "pfam_accession",
        "model_name",
    )
    check_columns(columns)

    rows = []

    with domtblout.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue

            fields = line.split()

            if len(fields) < 23:
                raise RuntimeError(
                    "Malformed hmmscan domtblout row"
                )

            model_name = fields[0]
            pfam_accession = fields[1]
            protein_id = fields[3]

            if protein_id not in manifest:
                raise RuntimeError(
                    f"Unknown hmmscan query: {protein_id}"
                )

            rows.append(
                (
                    manifest[protein_id]["class_name"],
                    protein_id,
                    pfam_accession,
                    model_name,
                )
            )

    rows.sort()

    with destination.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writerow(columns)
        writer.writerows(rows)

    return rows


def run_mmseqs(mmseqs, fasta, directory):
    directory.mkdir()
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
            raise RuntimeError(
                "MMseqs2 cluster TSV is absent"
            )

    return command, raw, stdout_path, stderr_path


def canonicalize_partition(raw_path, expected_members):
    rows = []

    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")

            if len(fields) != 2 or not all(fields):
                raise RuntimeError(
                    "Malformed MMseqs2 cluster row"
                )

            rows.append(tuple(fields))

    if len(rows) != len(set(rows)):
        raise RuntimeError(
            "Duplicate MMseqs2 cluster row"
        )

    member_to_representative = {}

    for representative, member in rows:
        if member in member_to_representative:
            raise RuntimeError(
                f"Duplicate MMseqs2 member: {member}"
            )

        member_to_representative[member] = representative

    if set(member_to_representative) != set(expected_members):
        raise RuntimeError(
            "MMseqs2 output is not a total partition"
        )

    if (
        set(member_to_representative.values())
        - set(expected_members)
    ):
        raise RuntimeError(
            "Unknown MMseqs2 representative"
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
        cluster_id = hashlib.sha256(
            "\n".join(ordered).encode("utf-8")
        ).hexdigest()

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


def copy(path, destination):
    shutil.copy2(path, destination)


def main():
    if not A2_SCAN_AUTHORIZED:
        raise SystemExit(
            "STOP: Gate A2 raw scan is not authorized"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            "A2-SS output exists; refusing to overwrite"
        )

    recovery_provenance, recovery_summary = load_recovery()
    manifest = load_sequence_manifest()
    records = verify_recovered_sequences(manifest)
    session, hmmscan, mmseqs, pfam_hmm = verify_session()

    with tempfile.TemporaryDirectory(
        prefix="exp05_a2ss_"
    ) as temporary:
        stage = Path(temporary) / OUTPUT.name
        stage.mkdir()

        fasta = RECOVERY / "confirmatory_sequences.fasta"

        pfam_directory = stage / "pfam"
        pfam_directory.mkdir()

        (
            hmmscan_command,
            domtblout,
            hmmscan_stdout,
            hmmscan_stderr,
        ) = run_hmmscan(
            hmmscan,
            pfam_hmm,
            fasta,
            pfam_directory,
        )

        accepted_path = pfam_directory / "accepted_family_hits.tsv"
        accepted_hits(
            domtblout,
            manifest,
            accepted_path,
        )

        copy(
            PFAM_CLANS,
            pfam_directory / "Pfam-A.clans.tsv.gz",
        )
        copy(
            PFAM_VERSION,
            pfam_directory / "Pfam.version.gz",
        )

        run_outputs = []

        for index in (1, 2):
            directory = stage / f"mmseqs_run_{index}"

            (
                command,
                raw,
                stdout_path,
                stderr_path,
            ) = run_mmseqs(
                mmseqs,
                fasta,
                directory,
            )

            canonical_rows, partition = canonicalize_partition(
                raw,
                records,
            )

            run_outputs.append(
                {
                    "index": index,
                    "command": command,
                    "raw": raw,
                    "stdout": stdout_path,
                    "stderr": stderr_path,
                    "canonical_rows": canonical_rows,
                    "partition": partition,
                }
            )

        if (
            run_outputs[0]["canonical_rows"]
            != run_outputs[1]["canonical_rows"]
        ):
            raise RuntimeError(
                "MMseqs2 canonical row replay mismatch"
            )

        if (
            run_outputs[0]["partition"]
            != run_outputs[1]["partition"]
        ):
            raise RuntimeError(
                "MMseqs2 partition replay mismatch"
            )

        (
            stage / "canonical_cluster_rows.tsv"
        ).write_bytes(
            run_outputs[0]["canonical_rows"]
        )
        (
            stage / "canonical_partition.tsv"
        ).write_bytes(
            run_outputs[0]["partition"]
        )

        output_hashes = {}

        for path in sorted(stage.rglob("*")):
            if path.is_file():
                output_hashes[
                    str(path.relative_to(stage))
                ] = digest(path)

        provenance = {
            "schema": "exp05_gate_a2_raw_scan_v1",
            "confirmatory_metadata_accessed": True,
            "confirmatory_sequence_accessed": True,
            "confirmatory_outcomes_accessed": False,
            "recovery_provenance_sha256": digest(
                RECOVERY / "recovery_provenance.json"
            ),
            "recovery_summary_sha256": digest(
                RECOVERY / "summary.json"
            ),
            "recovery_status": recovery_summary["status"],
            "sequence_count": len(records),
            "pfam_release": PFAM_RELEASE,
            "pfam_family_count": PFAM_FAMILY_COUNT,
            "pfam_threshold_rule": PFAM_THRESHOLD_RULE,
            "hmmscan_command": hmmscan_command,
            "mmseqs_source_commit": MMSEQS_SOURCE_COMMIT,
            "mmseqs_parameters": MMSEQS_PARAMETERS,
            "mmseqs_commands": [
                output["command"]
                for output in run_outputs
            ],
            "mmseqs_replay": {
                "canonical_row_set_identical": True,
                "stable_partition_identical": True,
                "raw_byte_identity_required": False,
            },
            "clan_mapping_performed": False,
            "combined_edges_computed": False,
            "family_geometry_computed": False,
            "cross_label_relationships_computed": False,
            "family_disjointness_computed": False,
            "session_manifest_sha256": (
                EXPECTED_SESSION_MANIFEST_SHA256
            ),
            "session_binary_identity": {
                "hmmscan_sha256": session["hmmer"][
                    "hmmscan_sha256"
                ],
                "mmseqs_sha256": session["mmseqs2"][
                    "binary_sha256"
                ],
                "scope": "session identity only",
            },
            "output_sha256": output_hashes,
        }

        write_json(
            stage / "scan_provenance.json",
            provenance,
        )

        stage.rename(OUTPUT)


if __name__ == "__main__":
    main()
