from pathlib import Path
import csv
import hashlib
import json
import os
import tempfile

import numpy as np


REPO = Path(__file__).resolve().parents[3]

EXPECTED_CONTRACT_COMMIT = (
    "f62fc78a3b424c20b1587e8e3b61ae853a60a63e"
)

CONTRACT_REL = (
    "experiments/04-depth-and-basis/"
    "ARM_B_PHASE_P_BASELINE_21D_DERIVATION_AND_ROW_CORRESPONDENCE_CONTRACT.md"
)

EXPECTED_CONTRACT_SHA = (
    "952313de005fbcbd5c7a922a7d0b7d798124102fb2b52f551dcefd6ea7b8a5fc"
)

MATRIX_MANIFEST_REL = (
    "experiments/03-toxin-representation/"
    "stage1_model_contact/discovery_extraction/"
    "discovery_matrix_rows.tsv"
)

EXPECTED_MATRIX_MANIFEST_SHA = (
    "ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e"
)

SEQUENCE_MANIFEST_REL = (
    "experiments/03-toxin-representation/"
    "stage1_model_blind/precontact_gate/"
    "discovery_sequence_manifest.tsv"
)

EXPECTED_SEQUENCE_MANIFEST_SHA = (
    "7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09"
)

FASTA_REL = (
    "experiments/03-toxin-representation/"
    "stage1_model_blind/precontact_gate/"
    "discovery_sequences.fasta"
)

EXPECTED_FASTA_SHA = (
    "ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358"
)

OUTPUT_DIR_REL = (
    "experiments/04-depth-and-basis/"
    "phase_p_biological_probe/input"
)

BASELINE_REL = OUTPUT_DIR_REL + "/baseline_21d.npy"
PROVENANCE_REL = OUTPUT_DIR_REL + "/BASELINE_21D_PROVENANCE.json"

CANONICAL_AA = tuple("ACDEFGHIKLMNPQRSTVWY")

FEATURE_NAMES = (
    "length",
    *tuple(f"fraction_{aa}" for aa in CANONICAL_AA),
)

EXPECTED_N = 278
EXPECTED_D = 21

Q6RX08_ROW = 212
Q6RX08_EXPECTED_LENGTH = 842
Q6RX08_EXPECTED_CANONICAL_SUM = 0.998812351543943


def stop(message):
    raise RuntimeError("STOP — " + message)


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_sequence(sequence):
    return hashlib.sha256(sequence.encode("utf-8")).hexdigest()


def read_tsv(path):
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        fields = tuple(reader.fieldnames or ())
    return fields, rows


def parse_fasta(path):
    records = []
    header = None
    chunks = []

    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()

            if not line:
                continue

            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(chunks)))

                header = line[1:]
                chunks = []

            else:
                if header is None:
                    stop("FASTA sequence occurred before first header")

                chunks.append(line)

    if header is not None:
        records.append((header, "".join(chunks)))

    return records


def canonical_json_bytes(payload):
    return (
        json.dumps(
            payload,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def atomic_write_bytes(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".tmp.",
        dir=str(path.parent),
    )

    tmp_path = Path(tmp_name)

    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp_path, path)

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def atomic_save_npy(path, array):
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".tmp.",
        suffix=".npy",
        dir=str(path.parent),
    )

    os.close(fd)
    tmp_path = Path(tmp_name)

    try:
        with tmp_path.open("wb") as handle:
            np.save(
                handle,
                array,
                allow_pickle=False,
            )
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp_path, path)

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def column_descriptives(array):
    if array.shape != (EXPECTED_N, EXPECTED_D):
        stop("descriptive-statistics input has wrong shape")

    result = []

    for j, name in enumerate(FEATURE_NAMES):
        column = array[:, j]

        result.append(
            {
                "column_index": j,
                "feature": name,
                "min": float(np.min(column)),
                "max": float(np.max(column)),
                "mean": float(np.mean(column, dtype=np.float64)),
                "std_population": float(
                    np.std(
                        column,
                        dtype=np.float64,
                        ddof=0,
                    )
                ),
            }
        )

    return result


def main():
    contract = REPO / CONTRACT_REL
    matrix_manifest = REPO / MATRIX_MANIFEST_REL
    sequence_manifest = REPO / SEQUENCE_MANIFEST_REL
    fasta = REPO / FASTA_REL

    output_dir = REPO / OUTPUT_DIR_REL
    baseline_path = REPO / BASELINE_REL
    provenance_path = REPO / PROVENANCE_REL

    # ------------------------------------------------------------------
    # Frozen-source verification
    # ------------------------------------------------------------------

    source_checks = (
        (
            contract,
            EXPECTED_CONTRACT_SHA,
            "derivation contract",
        ),
        (
            matrix_manifest,
            EXPECTED_MATRIX_MANIFEST_SHA,
            "authoritative matrix manifest",
        ),
        (
            sequence_manifest,
            EXPECTED_SEQUENCE_MANIFEST_SHA,
            "precontact sequence manifest",
        ),
        (
            fasta,
            EXPECTED_FASTA_SHA,
            "frozen FASTA",
        ),
    )

    for path, expected_sha, label in source_checks:
        if not path.exists():
            stop(f"{label} missing: {path}")

        actual_sha = sha256_file(path)

        if actual_sha != expected_sha:
            stop(
                f"{label} SHA mismatch: "
                f"expected={expected_sha}, actual={actual_sha}"
            )

    if baseline_path.exists():
        stop("baseline_21d.npy already exists; refusing overwrite")

    if provenance_path.exists():
        stop(
            "BASELINE_21D_PROVENANCE.json already exists; "
            "refusing overwrite"
        )

    # ------------------------------------------------------------------
    # Frozen inputs
    # ------------------------------------------------------------------

    matrix_fields, matrix_rows = read_tsv(matrix_manifest)
    sequence_fields, sequence_rows = read_tsv(sequence_manifest)
    fasta_records = parse_fasta(fasta)

    expected_matrix_fields = (
        "matrix_row",
        "class_name",
        "identifier",
        "retrieved_length",
        "sequence_sha256",
    )

    if matrix_fields != expected_matrix_fields:
        stop("authoritative matrix-manifest schema mismatch")

    if len(matrix_rows) != EXPECTED_N:
        stop("matrix manifest row count is not 278")

    if len(sequence_rows) != EXPECTED_N:
        stop("sequence manifest row count is not 278")

    if len(fasta_records) != EXPECTED_N:
        stop("FASTA record count is not 278")

    # ------------------------------------------------------------------
    # Correspondence proof
    # ------------------------------------------------------------------

    parsed_fasta = []

    correspondence = {
        "expected_rows": EXPECTED_N,
        "matrix_row_exact_0_to_277": True,
        "fasta_header_exact_class_pipe_identifier": True,
        "class_name_matches_all_rows": True,
        "identifier_matches_all_rows": True,
        "retrieved_length_matches_all_rows": True,
        "sequence_sha256_matches_all_rows": True,
        "rows_checked": 0,
        "passed": False,
    }

    for i, (header, sequence) in enumerate(fasta_records):
        parts = header.split("|")

        if len(parts) != 2:
            stop(
                f"FASTA header row {i} is not exactly "
                "class_name|identifier"
            )

        class_name, identifier = parts

        parsed_fasta.append(
            {
                "class_name": class_name,
                "identifier": identifier,
                "sequence": sequence,
                "length": len(sequence),
                "sequence_sha256": sha256_sequence(sequence),
            }
        )

    for i in range(EXPECTED_N):
        matrix_row = matrix_rows[i]
        sequence_row = sequence_rows[i]
        fasta_row = parsed_fasta[i]

        try:
            matrix_index = int(matrix_row["matrix_row"])
        except Exception:
            stop(f"invalid matrix_row at row {i}")

        if matrix_index != i:
            correspondence["matrix_row_exact_0_to_277"] = False
            stop(
                f"matrix_row mismatch at row {i}: "
                f"found {matrix_index}"
            )

        for field in (
            "class_name",
            "identifier",
            "retrieved_length",
            "sequence_sha256",
        ):
            if sequence_row[field] != matrix_row[field]:
                stop(
                    "precontact manifest / authoritative manifest "
                    f"mismatch at row {i}, field {field}"
                )

        if fasta_row["class_name"] != matrix_row["class_name"]:
            correspondence["class_name_matches_all_rows"] = False
            stop(f"class mismatch at row {i}")

        if fasta_row["identifier"] != matrix_row["identifier"]:
            correspondence["identifier_matches_all_rows"] = False
            stop(f"identifier mismatch at row {i}")

        if str(fasta_row["length"]) != matrix_row["retrieved_length"]:
            correspondence["retrieved_length_matches_all_rows"] = False
            stop(f"retrieved-length mismatch at row {i}")

        if (
            fasta_row["sequence_sha256"]
            != matrix_row["sequence_sha256"]
        ):
            correspondence["sequence_sha256_matches_all_rows"] = False
            stop(f"sequence-SHA mismatch at row {i}")

        correspondence["rows_checked"] += 1

    correspondence["passed"] = (
        correspondence["rows_checked"] == EXPECTED_N
        and correspondence["matrix_row_exact_0_to_277"]
        and correspondence["fasta_header_exact_class_pipe_identifier"]
        and correspondence["class_name_matches_all_rows"]
        and correspondence["identifier_matches_all_rows"]
        and correspondence["retrieved_length_matches_all_rows"]
        and correspondence["sequence_sha256_matches_all_rows"]
    )

    if not correspondence["passed"]:
        stop("row-correspondence proof did not pass completely")

    # ------------------------------------------------------------------
    # Label-authority census only
    # ------------------------------------------------------------------

    label_map = {
        "negative": 0,
        "positive": 1,
    }

    label_counts = {
        "negative": 0,
        "positive": 0,
    }

    for i, row in enumerate(matrix_rows):
        class_name = row["class_name"]

        if class_name not in label_map:
            stop(
                f"unexpected class_name at row {i}: "
                f"{class_name!r}"
            )

        label_counts[class_name] += 1

    if label_counts != {
        "negative": 139,
        "positive": 139,
    }:
        stop(
            "label census mismatch: "
            + repr(label_counts)
        )

    # ------------------------------------------------------------------
    # Compute in float64
    # ------------------------------------------------------------------

    baseline64 = np.empty(
        (EXPECTED_N, EXPECTED_D),
        dtype=np.float64,
    )

    for i, fasta_row in enumerate(parsed_fasta):
        sequence = fasta_row["sequence"]
        length = len(sequence)

        if length <= 0:
            stop(f"zero-length sequence at row {i}")

        baseline64[i, 0] = float(length)

        for j, aa in enumerate(CANONICAL_AA, start=1):
            baseline64[i, j] = (
                sequence.count(aa) / length
            )

    if baseline64.shape != (EXPECTED_N, EXPECTED_D):
        stop("float64 construction has wrong shape")

    if baseline64.dtype != np.float64:
        stop("construction is not float64")

    if not np.isfinite(baseline64).all():
        stop("float64 construction contains nonfinite values")

    # ------------------------------------------------------------------
    # Frozen sentinel before cast
    # ------------------------------------------------------------------

    if matrix_rows[Q6RX08_ROW]["identifier"] != "Q6RX08":
        stop("Q6RX08 is not at frozen row 212")

    q_sequence = parsed_fasta[Q6RX08_ROW]["sequence"]

    if len(q_sequence) != Q6RX08_EXPECTED_LENGTH:
        stop("Q6RX08 length mismatch")

    q_noncanonical = {
        aa: q_sequence.count(aa)
        for aa in sorted(
            set(q_sequence) - set(CANONICAL_AA)
        )
    }

    if q_noncanonical != {"X": 1}:
        stop(
            "Q6RX08 noncanonical sentinel mismatch: "
            + repr(q_noncanonical)
        )

    q_sum64 = float(
        baseline64[Q6RX08_ROW, 1:].sum()
    )

    if not np.isclose(
        q_sum64,
        Q6RX08_EXPECTED_CANONICAL_SUM,
        rtol=0.0,
        atol=1e-15,
    ):
        stop(
            "Q6RX08 float64 canonical-fraction sum mismatch"
        )

    # ------------------------------------------------------------------
    # FINAL numeric operation: float64 -> float32
    # ------------------------------------------------------------------

    baseline32 = baseline64.astype(
        np.float32,
        copy=True,
    )

    if baseline32.dtype != np.float32:
        stop("final baseline is not float32")

    if baseline32.shape != (EXPECTED_N, EXPECTED_D):
        stop("final float32 baseline has wrong shape")

    if not np.isfinite(baseline32).all():
        stop("final float32 baseline contains nonfinite values")

    # Lengths <= 1022 are exactly representable here.
    expected_lengths32 = np.asarray(
        [
            len(row["sequence"])
            for row in parsed_fasta
        ],
        dtype=np.float32,
    )

    if not np.array_equal(
        baseline32[:, 0],
        expected_lengths32,
    ):
        stop("float32 length column is not exact")

    q_sum32 = float(
        np.sum(
            baseline32[Q6RX08_ROW, 1:],
            dtype=np.float64,
        )
    )

    if f"{q_sum32:.4f}" != "0.9988":
        stop(
            "persistable float32 Q6RX08 sentinel "
            "does not round to 0.9988"
        )

    # ------------------------------------------------------------------
    # Write matrix atomically
    # ------------------------------------------------------------------

    atomic_save_npy(
        baseline_path,
        baseline32,
    )

    baseline_sha = sha256_file(
        baseline_path
    )

    # ------------------------------------------------------------------
    # Reload exact persisted matrix before describing it
    # ------------------------------------------------------------------

    persisted = np.load(
        baseline_path,
        allow_pickle=False,
    )

    if persisted.shape != (EXPECTED_N, EXPECTED_D):
        stop("persisted baseline shape mismatch")

    if persisted.dtype != np.float32:
        stop("persisted baseline dtype is not float32")

    if not np.isfinite(persisted).all():
        stop("persisted baseline contains nonfinite values")

    if not np.array_equal(
        persisted,
        baseline32,
    ):
        stop(
            "persisted baseline differs from final float32 construction"
        )

    # ------------------------------------------------------------------
    # Per-column descriptives of ACTUAL persisted artifact
    # ------------------------------------------------------------------

    descriptives = column_descriptives(
        persisted
    )

    if len(descriptives) != EXPECTED_D:
        stop("did not produce exactly 21 column descriptives")

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    provenance = {
        "artifact": {
            "path": BASELINE_REL,
            "sha256": baseline_sha,
            "shape": [
                EXPECTED_N,
                EXPECTED_D,
            ],
            "dtype": "float32",
            "finite": True,
        },
        "construction": {
            "compute_dtype": "float64",
            "final_persisted_dtype": "float32",
            "final_numeric_operation": "astype(np.float32)",
            "feature_order": list(FEATURE_NAMES),
            "fraction_formula": (
                "count(canonical_amino_acid) / full_sequence_length"
            ),
            "fraction_denominator": "full_sequence_length",
            "canonical_fraction_renormalization": False,
            "scaling": False,
            "standardization": False,
            "centering": False,
            "pca": False,
            "imputation": False,
            "generator_seeded": False,
            "model_used": False,
        },
        "frozen_sources": {
            "derivation_contract": {
                "path": CONTRACT_REL,
                "sha256": EXPECTED_CONTRACT_SHA,
                "commit": EXPECTED_CONTRACT_COMMIT,
            },
            "authoritative_matrix_manifest": {
                "path": MATRIX_MANIFEST_REL,
                "sha256": EXPECTED_MATRIX_MANIFEST_SHA,
            },
            "precontact_sequence_manifest": {
                "path": SEQUENCE_MANIFEST_REL,
                "sha256": EXPECTED_SEQUENCE_MANIFEST_SHA,
            },
            "fasta": {
                "path": FASTA_REL,
                "sha256": EXPECTED_FASTA_SHA,
            },
        },
        "label_authority": {
            "source": (
                "authoritative matrix manifest class_name"
            ),
            "mapping": {
                "negative": 0,
                "positive": 1,
            },
            "census": label_counts,
            "used_for_model_execution": False,
        },
        "correspondence_proof": correspondence,
        "q6rx08_sentinel": {
            "matrix_row": Q6RX08_ROW,
            "identifier": "Q6RX08",
            "length": Q6RX08_EXPECTED_LENGTH,
            "noncanonical_counts": {
                "X": 1,
            },
            "canonical_fraction_sum_float64": q_sum64,
            "canonical_fraction_sum_float32_persisted": q_sum32,
            "float32_sum_rounded_4dp": f"{q_sum32:.4f}",
        },
        "column_descriptive_statistics": descriptives,
        "preexecution_interpretation_note": {
            "status": "prospective",
            "text": (
                "The baseline is intentionally unstandardized. "
                "Its length feature is numerically much larger and more "
                "variable than individual composition fractions, so an "
                "L1-penalized probe may preferentially use length. "
                "Accordingly, later baseline predictive performance must "
                "not automatically be attributed to amino-acid composition. "
                "If raw ESM only matches this baseline, the result may be "
                "consistent with information recoverable from sequence "
                "length and simple composition. Raw ESM performance clearly "
                "above the paired baseline is the relevant excess beyond "
                "this control."
            ),
        },
        "biological_phase_p_execution_authorized": False,
    }

    atomic_write_bytes(
        provenance_path,
        canonical_json_bytes(provenance),
    )

    provenance_sha = sha256_file(
        provenance_path
    )

    # ------------------------------------------------------------------
    # Provenance roundtrip
    # ------------------------------------------------------------------

    with provenance_path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        loaded_provenance = json.load(handle)

    if loaded_provenance != provenance:
        stop("provenance JSON roundtrip mismatch")

    if (
        loaded_provenance["correspondence_proof"]["passed"]
        is not True
    ):
        stop(
            "persisted provenance does not record "
            "successful correspondence proof"
        )

    if (
        loaded_provenance[
            "biological_phase_p_execution_authorized"
        ]
        is not False
    ):
        stop(
            "provenance incorrectly authorizes biological execution"
        )

    print("PASS — baseline_21d generated under frozen contract.")
    print("baseline path   :", BASELINE_REL)
    print("baseline SHA256 :", baseline_sha)
    print("baseline dtype  :", persisted.dtype)
    print("baseline shape  :", persisted.shape)
    print("provenance path :", PROVENANCE_REL)
    print("provenance SHA  :", provenance_sha)
    print(
        "PASS — correspondence proof persisted for all 278 rows."
    )
    print(
        "PASS — 21 persisted float32 column descriptives recorded."
    )
    print(
        "PASS — biological execution remains unauthorized."
    )


if __name__ == "__main__":
    main()
