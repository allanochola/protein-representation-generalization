"""A2-SR: deterministic UniProt sequence recovery. Authorized for one execution."""

import csv
import hashlib
import io
import json
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


A2_SEQUENCE_RECOVERY_AUTHORIZED = True

EXPECTED_POSITIVES = 161
EXPECTED_NEGATIVES = 3541
EXPECTED_TOTAL = 3702

BATCH_SIZE = 100
MAX_RETRIES = 5
REQUEST_TIMEOUT_SECONDS = 120
RETRY_DELAY_SECONDS = 5

ENDPOINT = "https://rest.uniprot.org/uniprotkb/accessions"
USER_AGENT = "protein-representation-generalization-exp05-a2sr/1"

INTAKE_MANIFEST_SHA256 = (
    "fe3e3b14bfc70bf79928975156a07fbd"
    "1ccd1e091a2a83880b01dc8e1c247f9e"
)
HISTORICAL_POSITIVE_SHA256 = (
    "42a08582492ff8ec9cd38604b425e20ee"
    "795c1479f4f3aa47a0949ebf52479e1"
)

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"

INPUT_MANIFEST = (
    EXP / "a2_intake_archive/confirmatory_accession_manifest.tsv"
)
HISTORICAL_POSITIVE_SOURCE = (
    REPO
    / "experiments/03-toxin-representation/stage1_model_blind/"
      "confirmatory_positive_universe.tsv"
)
OUTPUT = EXP / "a2_sequence_recovery_archive"

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
            f"Input SHA-256 mismatch: {path}: {actual} != {expected}"
        )


def check_columns(columns):
    for column in columns:
        lowered = column.casefold()

        for token in BANNED_OUTPUT_COLUMN_TOKENS:
            if token in lowered:
                raise RuntimeError(
                    f"Forbidden output column: {column}"
                )


def load_intake_manifest():
    require_hash(INPUT_MANIFEST, INTAKE_MANIFEST_SHA256)

    with INPUT_MANIFEST.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle, delimiter="\t")

        expected = [
            "class_name",
            "accession",
            "frozen_length",
        ]

        if reader.fieldnames != expected:
            raise RuntimeError(
                f"Unexpected A2-I manifest schema: {reader.fieldnames}"
            )

        rows = list(reader)

    if len(rows) != EXPECTED_TOTAL:
        raise RuntimeError("A2-I manifest count mismatch")

    records = {}
    counts = {"positive": 0, "negative": 0}

    for row in rows:
        class_name = row["class_name"]
        accession = row["accession"].strip()
        frozen_length = int(row["frozen_length"])

        if class_name not in counts:
            raise RuntimeError(
                f"Unexpected class name: {class_name}"
            )

        if not accession or frozen_length <= 0:
            raise RuntimeError("Invalid A2-I membership row")

        if accession in records:
            raise RuntimeError(
                f"Duplicate A2-I accession: {accession}"
            )

        records[accession] = {
            "class_name": class_name,
            "frozen_length": frozen_length,
        }
        counts[class_name] += 1

    if counts != {
        "positive": EXPECTED_POSITIVES,
        "negative": EXPECTED_NEGATIVES,
    }:
        raise RuntimeError(
            f"A2-I class-count mismatch: {counts}"
        )

    return records


def load_historical_annotation_claims():
    require_hash(
        HISTORICAL_POSITIVE_SOURCE,
        HISTORICAL_POSITIVE_SHA256,
    )

    with HISTORICAL_POSITIVE_SOURCE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle, delimiter="\t")

        expected = [
            "cluster_rep",
            "representative_length",
            "length_stratum_stage1",
            "annotation_status",
        ]

        if reader.fieldnames != expected:
            raise RuntimeError(
                "Historical positive schema mismatch"
            )

        rows = list(reader)

    if len(rows) != EXPECTED_POSITIVES:
        raise RuntimeError(
            "Historical positive count mismatch"
        )

    claims = {}

    for row in rows:
        accession = row["cluster_rep"].strip()

        if not accession:
            raise RuntimeError(
                "Empty historical positive accession"
            )

        if accession in claims:
            raise RuntimeError(
                f"Duplicate historical positive: {accession}"
            )

        claims[accession] = row["annotation_status"]

    return claims


def batches(accessions):
    ordered = tuple(sorted(accessions))

    for start in range(0, len(ordered), BATCH_SIZE):
        yield ordered[start:start + BATCH_SIZE]


def request_url(accessions):
    query = urllib.parse.urlencode(
        {
            "accessions": ",".join(accessions),
            "format": "tsv",
            "fields": "accession,length,sequence",
        }
    )
    return f"{ENDPOINT}?{query}"


def fetch_batch(accessions):
    url = request_url(accessions)
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "text/tab-separated-values",
                "User-Agent": USER_AGENT,
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=REQUEST_TIMEOUT_SECONDS,
            ) as response:
                body = response.read()
                headers = {
                    key.casefold(): value
                    for key, value in response.headers.items()
                }

            return {
                "url": url,
                "body": body,
                "headers": headers,
                "attempt": attempt,
            }

        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
        ) as error:
            last_error = error

            if attempt == MAX_RETRIES:
                break

            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(
        f"UniProt batch retrieval failed: {last_error}"
    )


def normalize_header(name):
    return (
        name.strip()
        .casefold()
        .replace(" ", "_")
        .replace("-", "_")
    )


def resolve_column(fieldnames, aliases):
    mapping = {}

    for original in fieldnames:
        normalized = normalize_header(original)

        if normalized in mapping:
            raise RuntimeError(
                f"Normalized duplicate column: {normalized}"
            )

        mapping[normalized] = original

    matches = [
        mapping[alias]
        for alias in aliases
        if alias in mapping
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"Column resolution failed for {aliases}: "
            f"{fieldnames}"
        )

    return matches[0]


def parse_uniprot_tsv(body):
    text = body.decode("utf-8-sig")

    reader = csv.DictReader(
        io.StringIO(text),
        delimiter="\t",
    )

    if reader.fieldnames is None:
        raise RuntimeError("UniProt response has no header")

    accession_column = resolve_column(
        reader.fieldnames,
        ("entry", "accession"),
    )
    length_column = resolve_column(
        reader.fieldnames,
        ("length",),
    )
    sequence_column = resolve_column(
        reader.fieldnames,
        ("sequence",),
    )

    parsed = {}

    for row in reader:
        accession = row[accession_column].strip()
        sequence = (
            row[sequence_column]
            .replace(" ", "")
            .replace("\n", "")
            .upper()
        )
        reported_length = int(row[length_column])

        if not accession or not sequence:
            raise RuntimeError(
                "UniProt returned an empty accession or sequence"
            )

        if any(character.isspace() for character in sequence):
            raise RuntimeError(
                f"Whitespace in sequence: {accession}"
            )

        if len(sequence) != reported_length:
            raise RuntimeError(
                f"UniProt length field disagrees with sequence: "
                f"{accession}"
            )

        if accession in parsed:
            raise RuntimeError(
                f"Duplicate accession in response: {accession}"
            )

        parsed[accession] = {
            "sequence": sequence,
            "current_length": reported_length,
        }

    return parsed


def canonical_fasta(records):
    return "".join(
        f">{accession}\n{records[accession]['sequence']}\n"
        for accession in sorted(records)
    ).encode("ascii")


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


def write_outputs(
    stage,
    intake,
    claims,
    recovered,
    release,
    release_date,
    raw_batches,
    drift,
):
    raw_directory = stage / "raw_batches"
    raw_directory.mkdir()

    for item in raw_batches:
        index = item["index"]
        stem = f"batch_{index:04d}"

        (raw_directory / f"{stem}.tsv").write_bytes(
            item["body"]
        )
        write_json(
            raw_directory / f"{stem}.headers.json",
            item["headers"],
        )
        write_json(
            raw_directory / f"{stem}.request.json",
            {
                "accessions": list(item["accessions"]),
                "attempt": item["attempt"],
                "url": item["url"],
            },
        )

    fasta_bytes = canonical_fasta(recovered)
    (stage / "confirmatory_sequences.fasta").write_bytes(
        fasta_bytes
    )

    manifest_columns = (
        "class_name",
        "accession",
        "frozen_length",
        "current_length",
        "length_matches_frozen",
        "sequence_sha256",
        "uniprot_release",
        "uniprot_release_date",
    )
    check_columns(manifest_columns)

    with (stage / "sequence_manifest.tsv").open(
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

        for accession in sorted(recovered):
            sequence = recovered[accession]["sequence"]
            frozen_length = intake[accession]["frozen_length"]
            current_length = recovered[accession]["current_length"]

            writer.writerow(
                (
                    intake[accession]["class_name"],
                    accession,
                    frozen_length,
                    current_length,
                    str(
                        frozen_length == current_length
                    ).lower(),
                    hashlib.sha256(
                        sequence.encode("ascii")
                    ).hexdigest(),
                    release,
                    release_date,
                )
            )

    claim_columns = (
        "accession",
        "historical_annotation_status",
        "claim_role",
    )
    check_columns(claim_columns)

    with (stage / "historical_annotation_claims.tsv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writerow(claim_columns)

        for accession in sorted(claims):
            writer.writerow(
                (
                    accession,
                    claims[accession],
                    "historical_claim_under_test",
                )
            )

    status = (
        "PASS"
        if not drift
        else "SEQUENCE_SNAPSHOT_DRIFT"
    )

    summary = {
        "status": status,
        "positive_count": sum(
            row["class_name"] == "positive"
            for row in intake.values()
        ),
        "negative_count": sum(
            row["class_name"] == "negative"
            for row in intake.values()
        ),
        "requested_count": len(intake),
        "recovered_count": len(recovered),
        "drift_count": len(drift),
        "uniprot_release": release,
        "uniprot_release_date": release_date,
    }
    write_json(stage / "summary.json", summary)

    drift_columns = (
        "accession",
        "reason",
        "frozen_value",
        "current_value",
    )
    check_columns(drift_columns)

    with (stage / "snapshot_drift.tsv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writerow(drift_columns)

        for row in sorted(
            drift,
            key=lambda value: (
                value["accession"],
                value["reason"],
            ),
        ):
            writer.writerow(
                (
                    row["accession"],
                    row["reason"],
                    row["frozen_value"],
                    row["current_value"],
                )
            )

    output_sha256 = {}

    for path in sorted(stage.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "recovery_provenance.json":
            continue

        output_sha256[
            str(path.relative_to(stage))
        ] = digest(path)

    provenance = {
        "schema": "exp05_gate_a2_sequence_recovery_v1",
        "confirmatory_metadata_accessed": True,
        "confirmatory_sequence_accessed": True,
        "confirmatory_outcomes_accessed": False,
        "input_manifest_sha256": INTAKE_MANIFEST_SHA256,
        "historical_positive_source_sha256": (
            HISTORICAL_POSITIVE_SHA256
        ),
        "endpoint": ENDPOINT,
        "batch_size": BATCH_SIZE,
        "membership_order": "bytewise accession order",
        "fasta_serialization": (
            "identifier-only header; one unwrapped uppercase "
            "sequence line; LF endings; final LF"
        ),
        "uniprot_release": release,
        "uniprot_release_date": release_date,
        "status": status,
        "historical_annotation_status_role": (
            "historical_claim_under_test"
        ),
        "pfam_scan_performed": False,
        "mmseqs_clustering_performed": False,
        "family_geometry_computed": False,
        "output_sha256": output_sha256,
    }
    write_json(stage / "recovery_provenance.json", provenance)

    return status


def main():
    if not A2_SEQUENCE_RECOVERY_AUTHORIZED:
        raise SystemExit(
            "STOP: Gate A2 sequence recovery is not authorized"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            "A2-SR output exists; refusing to overwrite"
        )

    intake = load_intake_manifest()
    claims = load_historical_annotation_claims()

    if set(claims) != {
        accession
        for accession, record in intake.items()
        if record["class_name"] == "positive"
    }:
        raise RuntimeError(
            "Historical positive claims do not match A2-I positives"
        )

    retrieved = {}
    raw_batches = []
    releases = set()
    release_dates = set()
    drift = []

    for index, accession_batch in enumerate(
        batches(intake),
        start=1,
    ):
        response = fetch_batch(accession_batch)
        parsed = parse_uniprot_tsv(response["body"])

        requested = set(accession_batch)
        returned = set(parsed)

        for accession in sorted(requested - returned):
            drift.append(
                {
                    "accession": accession,
                    "reason": "MISSING_ACCESSION",
                    "frozen_value": "present",
                    "current_value": "missing",
                }
            )

        for accession in sorted(returned - requested):
            drift.append(
                {
                    "accession": accession,
                    "reason": "EXTRA_ACCESSION",
                    "frozen_value": "absent",
                    "current_value": "present",
                }
            )

        overlap = requested & returned

        for accession in sorted(overlap):
            if accession in retrieved:
                raise RuntimeError(
                    f"Duplicate recovered accession: {accession}"
                )

            retrieved[accession] = parsed[accession]

        release = response["headers"].get(
            "x-uniprot-release"
        )
        release_date = response["headers"].get(
            "x-uniprot-release-date"
        )

        if not release or not release_date:
            raise RuntimeError(
                "UniProt release headers are absent"
            )

        releases.add(release)
        release_dates.add(release_date)

        raw_batches.append(
            {
                "index": index,
                "accessions": accession_batch,
                "url": response["url"],
                "body": response["body"],
                "headers": response["headers"],
                "attempt": response["attempt"],
            }
        )

    if len(releases) != 1 or len(release_dates) != 1:
        for accession in sorted(intake):
            drift.append(
                {
                    "accession": accession,
                    "reason": "MIXED_UNIPROT_RELEASE",
                    "frozen_value": "one_release",
                    "current_value": (
                        ",".join(sorted(releases))
                        + "|"
                        + ",".join(sorted(release_dates))
                    ),
                }
            )

    for accession in sorted(set(intake) & set(retrieved)):
        frozen = intake[accession]["frozen_length"]
        current = retrieved[accession]["current_length"]

        if frozen != current:
            drift.append(
                {
                    "accession": accession,
                    "reason": "LENGTH_MISMATCH",
                    "frozen_value": str(frozen),
                    "current_value": str(current),
                }
            )

    if set(retrieved) != set(intake):
        # The detailed missing/extra records above carry the identity.
        pass

    release = (
        next(iter(releases))
        if len(releases) == 1
        else "MIXED"
    )
    release_date = (
        next(iter(release_dates))
        if len(release_dates) == 1
        else "MIXED"
    )

    with tempfile.TemporaryDirectory(
        prefix="exp05_a2sr_"
    ) as temporary:
        stage = Path(temporary) / OUTPUT.name
        stage.mkdir()

        status = write_outputs(
            stage,
            intake,
            claims,
            retrieved,
            release,
            release_date,
            raw_batches,
            drift,
        )

        stage.rename(OUTPUT)

    if status != "PASS":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
