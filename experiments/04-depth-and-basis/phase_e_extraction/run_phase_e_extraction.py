#!/usr/bin/env python3
"""
Experiment 04 — Phase E discovery representation extraction.

STATUS
------
HARD-DISABLED.

This implementation is frozen before any fresh Experiment-04 biological
representation extraction.

While disabled, execution terminates before importing torch or transformers,
before loading ESM-2, and before computing any biological representation.

Phase E is extraction only. It must not perform probing, cross-validation,
AUROC computation, support analysis, recurrence analysis, label permutation,
or access any biological perturbation seed namespace.
"""

from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json
import os
import sys


# ============================================================================
# HARD DISABLE BOUNDARY
# ============================================================================

ENABLE_BIOLOGICAL_REPRESENTATION_EXTRACTION = False


# ============================================================================
# Frozen Experiment-04 Phase-E contract
# ============================================================================

MODEL_ID = "facebook/esm2_t33_650M_UR50D"
MODEL_REVISION = "08e4846e537177426273712802403f7ba8261b6c"

LAYERS = (1, 9, 18, 24, 30, 33)
HIDDEN_WIDTH = 1280

MIN_BIOLOGICAL_LENGTH = 1
MAX_BIOLOGICAL_LENGTH = 1022

POOLING = "coordinate_wise_residue_max"
ARCHIVE_DTYPE = "float32"

EXPECTED_N_ROWS = 278
EXPECTED_POSITIVE = 139
EXPECTED_NEGATIVE = 139

FASTA_REL = 'experiments/03-toxin-representation/stage1_model_blind/precontact_gate/discovery_sequences.fasta'
MANIFEST_REL = 'experiments/03-toxin-representation/stage1_model_contact/discovery_extraction/discovery_matrix_rows.tsv'

EXPECTED_FASTA_SHA256 = 'ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358'
EXPECTED_MANIFEST_SHA256 = 'ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e'

OUTPUT_DIR_REL = (
    "experiments/04-depth-and-basis/"
    "phase_e_extraction/output"
)

# Explicitly no probe-seed namespace exists in Phase E.


def fail(message: str) -> None:
    raise RuntimeError("STOP — " + message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_repo_root() -> Path:
    here = Path(__file__).resolve()

    for candidate in (here.parent, *here.parents):
        if (candidate / ".git").exists():
            return candidate

    fail("could not resolve repository root")


def parse_fasta(path: Path) -> dict[str, str]:
    """
    Parse the frozen discovery FASTA.

    UniProt-style header aliases are supported, but the final mapping must
    resolve every identifier in discovery_matrix_rows.tsv exactly once.
    """
    mapping: dict[str, str] = {}

    header = None
    chunks: list[str] = []

    def flush() -> None:
        nonlocal header, chunks

        if header is None:
            return

        sequence = "".join(chunks).replace(" ", "").strip()

        if not sequence:
            fail("empty FASTA sequence encountered")

        first = header.split()[0]

        aliases = {first}

        if "|" in first:
            aliases.update(
                part
                for part in first.split("|")
                if part
            )

        for alias in aliases:
            if alias in mapping and mapping[alias] != sequence:
                fail(
                    "ambiguous FASTA alias maps to different sequences: "
                    + alias
                )

            mapping[alias] = sequence

    with path.open(
        "r",
        encoding="utf-8",
        errors="strict",
    ) as handle:

        for raw_line in handle:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith(">"):
                flush()
                header = line[1:].strip()
                chunks = []
            else:
                chunks.append(line)

        flush()

    return mapping


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:

        reader = csv.DictReader(
            handle,
            delimiter="\t",
        )

        rows = list(reader)

        fields = set(reader.fieldnames or [])

    required = {
        "matrix_row",
        "class_name",
        "identifier",
        "retrieved_length",
        "sequence_sha256",
    }

    if not required.issubset(fields):
        fail(
            "row-manifest schema drift; missing: "
            + repr(sorted(required - fields))
        )

    return rows


def validate_frozen_inputs(
    repo: Path,
) -> tuple[list[dict[str, str]], dict[str, str]]:

    fasta_path = repo / FASTA_REL
    manifest_path = repo / MANIFEST_REL

    if not fasta_path.exists():
        fail("frozen discovery FASTA missing")

    if not manifest_path.exists():
        fail("frozen discovery row manifest missing")

    observed_fasta_sha = sha256_file(fasta_path)
    observed_manifest_sha = sha256_file(manifest_path)

    if observed_fasta_sha != EXPECTED_FASTA_SHA256:
        fail(
            "frozen discovery FASTA byte identity changed; "
            f"expected {EXPECTED_FASTA_SHA256}, "
            f"observed {observed_fasta_sha}"
        )

    if observed_manifest_sha != EXPECTED_MANIFEST_SHA256:
        fail(
            "frozen discovery row-manifest byte identity changed; "
            f"expected {EXPECTED_MANIFEST_SHA256}, "
            f"observed {observed_manifest_sha}"
        )

    rows = load_manifest(manifest_path)
    fasta = parse_fasta(fasta_path)

    if len(rows) != EXPECTED_N_ROWS:
        fail(
            f"expected {EXPECTED_N_ROWS} manifest rows, "
            f"observed {len(rows)}"
        )

    expected_matrix_rows = list(range(EXPECTED_N_ROWS))

    try:
        observed_matrix_rows = [
            int(row["matrix_row"])
            for row in rows
        ]
    except Exception as exc:
        fail(
            "matrix_row is not integer-valued: "
            + repr(exc)
        )

    if observed_matrix_rows != expected_matrix_rows:
        fail("matrix_row must be exactly 0..277")

    class_counts = {
        "positive": 0,
        "negative": 0,
    }

    identifiers: set[str] = set()

    for row in rows:

        class_name = row["class_name"].strip()
        identifier = row["identifier"].strip()

        if class_name not in class_counts:
            fail(
                "unexpected discovery class: "
                + class_name
            )

        class_counts[class_name] += 1

        if identifier in identifiers:
            fail(
                "duplicate discovery identifier: "
                + identifier
            )

        identifiers.add(identifier)

        if identifier not in fasta:
            fail(
                "manifest identifier absent from frozen FASTA: "
                + identifier
            )

        sequence = fasta[identifier]

        try:
            expected_length = int(
                row["retrieved_length"]
            )
        except Exception:
            fail(
                "invalid retrieved_length for "
                + identifier
            )

        if not (
            MIN_BIOLOGICAL_LENGTH
            <= expected_length
            <= MAX_BIOLOGICAL_LENGTH
        ):
            fail(
                "biological sequence length outside frozen "
                "eligibility range for "
                + identifier
            )

        if len(sequence) != expected_length:
            fail(
                "sequence-length mismatch for "
                + identifier
            )

        observed_sequence_sha = hashlib.sha256(
            sequence.encode("utf-8")
        ).hexdigest()

        expected_sequence_sha = (
            row["sequence_sha256"].strip()
        )

        if observed_sequence_sha != expected_sequence_sha:
            fail(
                "sequence SHA-256 mismatch for "
                + identifier
            )

    if class_counts["positive"] != EXPECTED_POSITIVE:
        fail(
            f"expected {EXPECTED_POSITIVE} positives, "
            f"observed {class_counts['positive']}"
        )

    if class_counts["negative"] != EXPECTED_NEGATIVE:
        fail(
            f"expected {EXPECTED_NEGATIVE} negatives, "
            f"observed {class_counts['negative']}"
        )

    return rows, fasta


def run_enabled_phase_e(
    repo: Path,
    rows: list[dict[str, str]],
    fasta: dict[str, str],
) -> None:
    """
    Biological Phase-E execution.

    This code is unreachable while
    ENABLE_BIOLOGICAL_REPRESENTATION_EXTRACTION == False.
    """

    # Imports are intentionally below the hard-disable boundary.
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer

    if torch.is_autocast_enabled():
        fail(
            "automatic mixed precision is active; "
            "Phase E requires no AMP"
        )

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
    )

    model = AutoModel.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        output_hidden_states=True,
    )

    model = model.to(device)
    model.eval()

    matrices = {
        layer: np.empty(
            (EXPECTED_N_ROWS, HIDDEN_WIDTH),
            dtype=np.float32,
        )
        for layer in LAYERS
    }

    extraction_rows = []

    with torch.no_grad():

        for manifest_row in rows:

            matrix_row = int(
                manifest_row["matrix_row"]
            )

            identifier = (
                manifest_row["identifier"].strip()
            )

            sequence = fasta[identifier]
            biological_length = len(sequence)

            encoded = tokenizer(
                sequence,
                return_tensors="pt",
                truncation=False,
                add_special_tokens=True,
            )

            encoded = {
                key: value.to(device)
                for key, value in encoded.items()
            }

            output = model(
                **encoded,
                output_hidden_states=True,
                return_dict=True,
            )

            hidden_states = output.hidden_states

            if hidden_states is None:
                fail(
                    "model returned no hidden states"
                )

            for layer in LAYERS:

                hidden = hidden_states[layer][0]

                # Frozen Experiment-04 token semantics:
                # biological residues only.
                residue_hidden = hidden[
                    1 : biological_length + 1
                ]

                expected_shape = (
                    biological_length,
                    HIDDEN_WIDTH,
                )

                if tuple(residue_hidden.shape) != expected_shape:
                    fail(
                        f"residue geometry mismatch for "
                        f"{identifier}, layer {layer}: "
                        f"expected {expected_shape}, "
                        f"observed "
                        f"{tuple(residue_hidden.shape)}"
                    )

                # No explicit float16 conversion.
                residue_hidden = residue_hidden.float()

                pooled = torch.max(
                    residue_hidden,
                    dim=0,
                ).values

                if tuple(pooled.shape) != (HIDDEN_WIDTH,):
                    fail(
                        f"pooled geometry mismatch for "
                        f"{identifier}, layer {layer}"
                    )

                pooled_np = (
                    pooled
                    .detach()
                    .cpu()
                    .numpy()
                    .astype(
                        np.float32,
                        copy=False,
                    )
                )

                if pooled_np.dtype != np.float32:
                    fail(
                        "pooled representation is not float32"
                    )

                if not np.isfinite(pooled_np).all():
                    fail(
                        f"non-finite pooled representation for "
                        f"{identifier}, layer {layer}"
                    )

                matrices[layer][matrix_row] = pooled_np

            extraction_rows.append(
                {
                    "matrix_row": matrix_row,
                    "class_name": manifest_row["class_name"],
                    "identifier": identifier,
                    "retrieved_length": biological_length,
                    "sequence_sha256": manifest_row["sequence_sha256"],
                }
            )

    # Final complete-matrix validation before any archive write.
    for layer, matrix in matrices.items():

        if matrix.shape != (
            EXPECTED_N_ROWS,
            HIDDEN_WIDTH,
        ):
            fail(
                f"final matrix shape mismatch for layer {layer}"
            )

        if matrix.dtype != np.float32:
            fail(
                f"final matrix dtype mismatch for layer {layer}"
            )

        if not np.isfinite(matrix).all():
            fail(
                f"final matrix contains non-finite values "
                f"for layer {layer}"
            )

    output_dir = repo / OUTPUT_DIR_REL

    # No partial archive is accepted.
    if output_dir.exists():
        fail(
            "Phase-E output directory already exists; "
            "refusing overwrite"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    matrix_records = []

    for layer in LAYERS:

        matrix_path = (
            output_dir
            / f"raw_esm_layer_{layer}.npy"
        )

        np.save(
            matrix_path,
            matrices[layer],
            allow_pickle=False,
        )

        matrix_records.append(
            {
                "layer": layer,
                "path": matrix_path.name,
                "shape": [
                    EXPECTED_N_ROWS,
                    HIDDEN_WIDTH,
                ],
                "dtype": "float32",
                "sha256": sha256_file(matrix_path),
            }
        )

    rows_path = (
        output_dir
        / "phase_e_matrix_rows.tsv"
    )

    with rows_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:

        fields = [
            "matrix_row",
            "class_name",
            "identifier",
            "retrieved_length",
            "sequence_sha256",
        ]

        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(extraction_rows)

    provenance = {
        "experiment": "04-depth-and-basis",
        "phase": "E",
        "status": "discovery-representation-extraction",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "layers": list(LAYERS),
        "layer_semantics": "output.hidden_states[k]",
        "biological_token_slice": "[1:L+1]",
        "pooling": POOLING,
        "hidden_width": HIDDEN_WIDTH,
        "archive_dtype": ARCHIVE_DTYPE,
        "expected_rows": EXPECTED_N_ROWS,
        "discovery_positive": EXPECTED_POSITIVE,
        "discovery_negative": EXPECTED_NEGATIVE,
        "fasta_path": FASTA_REL,
        "fasta_sha256": EXPECTED_FASTA_SHA256,
        "manifest_path": MANIFEST_REL,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "confirmatory_data_processed": False,
        "probe_seed_namespace_accessed": False,
        "cross_validation_performed": False,
        "probe_fit_performed": False,
        "auroc_computed": False,
        "support_statistics_computed": False,
        "matrices": matrix_records,
        "rows_manifest": {
            "path": rows_path.name,
            "sha256": sha256_file(rows_path),
        },
    }

    provenance_path = (
        output_dir
        / "PHASE_E_PROVENANCE.json"
    )

    provenance_path.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "PASS — Phase-E extraction completed."
    )
    print(
        "Fresh biological representations have now been computed."
    )
    print(
        "BIOLOGICAL PROBING: CLOSED"
    )


def main() -> None:

    repo = find_repo_root()

    # ------------------------------------------------------------------------
    # HARD DISABLE CHECK
    #
    # This check precedes:
    #   - frozen biological input validation,
    #   - torch import,
    #   - transformers import,
    #   - model loading,
    #   - tokenization,
    #   - biological representation computation.
    # ------------------------------------------------------------------------

    if not ENABLE_BIOLOGICAL_REPRESENTATION_EXTRACTION:

        print(
            "STOP — Experiment 04 Phase-E biological representation "
            "extraction is HARD-DISABLED."
        )

        print(
            "No model was loaded."
        )

        print(
            "No biological representation was computed."
        )

        print(
            "No probe seed namespace was accessed."
        )

        print(
            "BIOLOGICAL REPRESENTATION EXTRACTION: CLOSED"
        )

        print(
            "BIOLOGICAL PROBING: CLOSED"
        )

        return

    rows, fasta = validate_frozen_inputs(repo)

    run_enabled_phase_e(
        repo,
        rows,
        fasta,
    )


if __name__ == "__main__":
    main()
