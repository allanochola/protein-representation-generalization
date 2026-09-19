"""Authorized one-time Gate A2-I confirmatory-membership intake."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

A2_INTAKE_AUTHORIZED = False

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"

POSITIVE_INPUT = (
    REPO
    / "experiments/03-toxin-representation/stage1_model_blind"
    / "confirmatory_positive_universe.tsv"
)
NEGATIVE_INPUT = (
    REPO
    / "experiments/03-toxin-representation/stage1_model_blind"
    / "confirmatory_negative_universe.tsv"
)
DISCOVERY_MANIFEST = (
    EXP / "a1_scan_archive/discovery_sequence_manifest.tsv"
)
OUTPUT = EXP / "a2_intake_archive"

EXPECTED_POSITIVES = 161
EXPECTED_NEGATIVES = 3541
EXPECTED_DISCOVERY = 278

ACCESSION_ALIASES = ('accession', 'identifier', 'protein_id', 'uniprot_accession', 'cluster_rep')
LENGTH_ALIASES = ('length', 'frozen_length', 'sequence_length', 'retrieved_length', 'representative_length')
BANNED = ('auroc', 'auprc', 'tpr', 'fpr', 'score', 'prediction', 'probability', 'threshold', 'embedding', 'activation')


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def tracked(path):
    relative = str(Path(path).relative_to(REPO))
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def resolve_header(fieldnames, aliases, semantic_name, required):
    matches = [name for name in aliases if name in fieldnames]

    if len(matches) > 1:
        raise RuntimeError(
            "A2_INTAKE_SCHEMA_MISMATCH: ambiguous "
            + semantic_name
            + " columns: "
            + repr(matches)
        )

    if required and len(matches) != 1:
        raise RuntimeError(
            "A2_INTAKE_SCHEMA_MISMATCH: missing "
            + semantic_name
            + " column"
        )

    return matches[0] if matches else None


def reject_banned(fieldnames):
    for field in fieldnames:
        lowered = field.lower()
        if any(token in lowered for token in BANNED):
            raise RuntimeError(
                "A2_INTAKE_SCHEMA_MISMATCH: prohibited column "
                + field
            )


def load_membership(path, class_name, expected_count):
    if not path.is_file() or not tracked(path):
        raise RuntimeError("Frozen membership input missing or untracked")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = tuple(reader.fieldnames or ())

        if not fields or len(fields) != len(set(fields)):
            raise RuntimeError(
                "A2_INTAKE_SCHEMA_MISMATCH: invalid header"
            )

        reject_banned(fields)

        accession_column = resolve_header(
            fields,
            ACCESSION_ALIASES,
            "accession",
            True,
        )
        length_column = resolve_header(
            fields,
            LENGTH_ALIASES,
            "length",
            False,
        )

        rows = []
        seen = set()

        for row in reader:
            accession = row[accession_column].strip()

            if not accession:
                raise RuntimeError("Empty accession")
            if accession in seen:
                raise RuntimeError("Duplicate accession within membership")

            seen.add(accession)

            frozen_length = ""
            if length_column is not None:
                raw_length = row[length_column].strip()
                if raw_length:
                    frozen_length = int(raw_length)
                    if frozen_length <= 0:
                        raise RuntimeError("Nonpositive frozen length")

            rows.append((
                class_name,
                accession,
                frozen_length,
            ))

    if len(rows) != expected_count:
        raise RuntimeError(
            f"Membership count mismatch for {class_name}: "
            f"{len(rows)} != {expected_count}"
        )

    return {
        "rows": rows,
        "header": fields,
        "accession_column": accession_column,
        "length_column": length_column,
    }


def main():
    if not A2_INTAKE_AUTHORIZED:
        raise SystemExit("STOP: Gate A2-I intake is not authorized")

    if OUTPUT.exists():
        raise RuntimeError("A2-I output already exists")

    positive = load_membership(
        POSITIVE_INPUT,
        "positive",
        EXPECTED_POSITIVES,
    )
    negative = load_membership(
        NEGATIVE_INPUT,
        "negative",
        EXPECTED_NEGATIVES,
    )

    positive_ids = {
        row[1] for row in positive["rows"]
    }
    negative_ids = {
        row[1] for row in negative["rows"]
    }

    if positive_ids & negative_ids:
        raise RuntimeError(
            "Confirmatory positive/negative accession overlap"
        )

    with DISCOVERY_MANIFEST.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        discovery_reader = csv.DictReader(
            handle,
            delimiter="\t",
        )

        if "identifier" not in (
            discovery_reader.fieldnames or ()
        ):
            raise RuntimeError("Discovery manifest schema mismatch")

        discovery_ids = {
            row["identifier"]
            for row in discovery_reader
        }

    if len(discovery_ids) != EXPECTED_DISCOVERY:
        raise RuntimeError("Discovery manifest count mismatch")

    all_rows = sorted(
        positive["rows"] + negative["rows"],
        key=lambda row: (row[1], row[0]),
    )

    if len(all_rows) != (
        EXPECTED_POSITIVES + EXPECTED_NEGATIVES
    ):
        raise RuntimeError("Combined intake count mismatch")

    OUTPUT.mkdir()

    manifest_path = OUTPUT / "confirmatory_accession_manifest.tsv"
    manifest_columns = (
        "class_name",
        "accession",
        "frozen_length",
    )

    with manifest_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writerow(manifest_columns)
        writer.writerows(all_rows)

    summary = {
        "status": "A2_INTAKE_COMPLETE",
        "positive_count": len(positive["rows"]),
        "negative_count": len(negative["rows"]),
        "total_count": len(all_rows),
        "positive_negative_accession_overlap": 0,
        "discovery_positive_accession_overlap": len(
            discovery_ids & positive_ids
        ),
        "discovery_negative_accession_overlap": len(
            discovery_ids & negative_ids
        ),
        "positive_length_column_present":
            positive["length_column"] is not None,
        "negative_length_column_present":
            negative["length_column"] is not None,
    }

    summary_path = OUTPUT / "intake_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    output_hashes = {
        "confirmatory_accession_manifest.tsv":
            digest(manifest_path),
        "intake_summary.json":
            digest(summary_path),
    }

    provenance = {
        "confirmatory_metadata_accessed": True,
        "confirmatory_outcomes_accessed": False,
        "models_loaded": False,
        "predictions_computed": False,
        "scores_computed": False,
        "geometry_computed": False,
        "positive_input_path": str(
            POSITIVE_INPUT.relative_to(REPO)
        ),
        "negative_input_path": str(
            NEGATIVE_INPUT.relative_to(REPO)
        ),
        "positive_input_sha256": digest(POSITIVE_INPUT),
        "negative_input_sha256": digest(NEGATIVE_INPUT),
        "positive_input_header": list(positive["header"]),
        "negative_input_header": list(negative["header"]),
        "positive_accession_column":
            positive["accession_column"],
        "negative_accession_column":
            negative["accession_column"],
        "positive_length_column":
            positive["length_column"],
        "negative_length_column":
            negative["length_column"],
        "accession_aliases_frozen":
            list(ACCESSION_ALIASES),
        "length_aliases_frozen":
            list(LENGTH_ALIASES),
        "output_sha256": output_hashes,
    }

    (OUTPUT / "intake_provenance.json").write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
