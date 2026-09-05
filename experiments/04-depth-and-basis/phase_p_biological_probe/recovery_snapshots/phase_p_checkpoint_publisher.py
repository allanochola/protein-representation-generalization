#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from typing import Dict


CHECKPOINT_CADENCE = 10
MAIN_TOTAL = 2100
NULL_TOTAL = 100

DATASET_REF = "ocholla/exp04-phase-p-private-checkpoints"
DATASET_TITLE = "Experiment 04 Phase P Private Checkpoints"

SCIENTIFIC_HEAD = (
    "5277f686ad09ead8921462cb9ed9a53324007c42"
)

RUNNER_SHA256 = (
    "e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec"
)

ALLOWED_PRODUCTION_ARTIFACTS = (
    "execution_manifest.json",
    "main_per_perturbation.csv",
    "permutation_null_per_perturbation.csv",
    "RESULT.md",
)


class PublisherContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class Counts:
    main: int
    null: int


@dataclass(frozen=True)
class PublishDecision:
    publish: bool
    reason: str
    local: Counts
    remote: Counts


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def csv_data_row_count(path: Path) -> int:
    if not path.is_file():
        return 0

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.reader(f)

        try:
            header = next(reader)
        except StopIteration:
            raise PublisherContractError(
                f"CSV is empty: {path}"
            )

        if not header:
            raise PublisherContractError(
                f"CSV header empty: {path}"
            )

        count = 0

        for row in reader:
            if not row:
                raise PublisherContractError(
                    f"blank CSV record: {path}"
                )

            count += 1

    return count


def count_source_rows(source_dir: Path) -> Counts:
    main = csv_data_row_count(
        source_dir / "main_per_perturbation.csv"
    )

    null = csv_data_row_count(
        source_dir / "permutation_null_per_perturbation.csv"
    )

    if main < 0 or main > MAIN_TOTAL:
        raise PublisherContractError(
            f"main row count out of bounds: {main}"
        )

    if null < 0 or null > NULL_TOTAL:
        raise PublisherContractError(
            f"null row count out of bounds: {null}"
        )

    if null > 0 and main != MAIN_TOTAL:
        raise PublisherContractError(
            "null rows exist before main arm is complete."
        )

    return Counts(
        main=main,
        null=null,
    )


def checkpoint_due(
    local: Counts,
    remote: Counts,
    *,
    final_complete: bool = False,
) -> PublishDecision:

    if remote.main > local.main:
        raise PublisherContractError(
            "remote main count exceeds local durable count."
        )

    if remote.null > local.null:
        raise PublisherContractError(
            "remote null count exceeds local durable count."
        )

    if local.null > 0 and local.main != MAIN_TOTAL:
        raise PublisherContractError(
            "null rows exist before main completion."
        )

    main_delta = local.main - remote.main
    null_delta = local.null - remote.null

    if main_delta >= CHECKPOINT_CADENCE:
        return PublishDecision(
            True,
            "main-cadence",
            local,
            remote,
        )

    if (
        local.main == MAIN_TOTAL
        and remote.main < MAIN_TOTAL
    ):
        return PublishDecision(
            True,
            "main-boundary",
            local,
            remote,
        )

    if null_delta >= CHECKPOINT_CADENCE:
        return PublishDecision(
            True,
            "null-cadence",
            local,
            remote,
        )

    if (
        local.null == NULL_TOTAL
        and remote.null < NULL_TOTAL
    ):
        return PublishDecision(
            True,
            "null-boundary",
            local,
            remote,
        )

    if (
        final_complete
        and (
            local.main != remote.main
            or local.null != remote.null
        )
    ):
        return PublishDecision(
            True,
            "final-boundary",
            local,
            remote,
        )

    return PublishDecision(
        False,
        "not-due",
        local,
        remote,
    )


def exact_artifact_hashes(
    source_dir: Path,
) -> Dict[str, str]:

    hashes: Dict[str, str] = {}

    for name in ALLOWED_PRODUCTION_ARTIFACTS:
        path = source_dir / name

        if path.exists():
            if not path.is_file():
                raise PublisherContractError(
                    f"allowed artifact is not a file: {name}"
                )

            hashes[name] = sha256_file(path)

    unexpected = sorted(
        p.name
        for p in source_dir.iterdir()
        if (
            p.is_file()
            and p.name not in ALLOWED_PRODUCTION_ARTIFACTS
        )
    )

    if unexpected:
        raise PublisherContractError(
            "unexpected production-output file(s): "
            + ", ".join(unexpected)
        )

    return hashes


def stage_exact_snapshot(
    source_dir: Path,
    stage_dir: Path,
) -> Dict[str, str]:

    if any(stage_dir.iterdir()):
        raise PublisherContractError(
            "staging directory must begin empty."
        )

    before = exact_artifact_hashes(source_dir)

    for name in before:
        shutil.copyfile(
            source_dir / name,
            stage_dir / name,
        )

    after = {
        name: sha256_file(stage_dir / name)
        for name in before
    }

    if before != after:
        raise PublisherContractError(
            "staged bytes do not exactly match source bytes."
        )

    return before


def stable_exact_snapshot(
    source_dir: Path,
    *,
    settle_seconds: float = 0.25,
) -> Dict[str, str]:

    first_counts = count_source_rows(source_dir)
    first_hashes = exact_artifact_hashes(source_dir)

    time.sleep(settle_seconds)

    second_counts = count_source_rows(source_dir)
    second_hashes = exact_artifact_hashes(source_dir)

    if first_counts != second_counts:
        raise PublisherContractError(
            "source row counts changed during stability observation."
        )

    if first_hashes != second_hashes:
        raise PublisherContractError(
            "source bytes changed during stability observation."
        )

    return second_hashes


def checkpoint_note(
    *,
    sequence: int,
    decision: PublishDecision,
) -> str:

    return (
        "Exp 04 Phase-P checkpoint "
        f"sequence={sequence}; "
        f"reason={decision.reason}; "
        f"main_rows={decision.local.main}; "
        f"null_rows={decision.local.null}; "
        f"scientific_head={SCIENTIFIC_HEAD}"
    )


def write_dataset_metadata(
    stage_dir: Path,
) -> None:
    metadata = {
        "title": DATASET_TITLE,
        "id": DATASET_REF,
        "licenses": [
            {"name": "other"}
        ],
    }

    (
        stage_dir / "dataset-metadata.json"
    ).write_text(
        json.dumps(
            metadata,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )



def run_cli(cmd):
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def build_version_command(
    stage_dir: Path,
    message: str,
):
    """
    Build one append-history Dataset version command.

    Destructive old-version deletion flags are forbidden.
    """

    cmd = [
        "kaggle",
        "datasets",
        "version",
        "-p",
        str(stage_dir),
        "-m",
        message,
    ]

    forbidden = {
        "-d",
        "--delete-old-versions",
    }

    if any(
        token in forbidden
        for token in cmd
    ):
        raise PublisherContractError(
            "destructive old-version deletion "
            "flag present."
        )

    return cmd


def wait_until_dataset_ready(
    *,
    max_attempts: int = 120,
    sleep_seconds: float = 2.0,
) -> None:

    last = ""

    for _ in range(max_attempts):
        p = run_cli(
            [
                "kaggle",
                "datasets",
                "status",
                DATASET_REF,
            ]
        )

        text = (
            p.stdout
            + "\n"
            + p.stderr
        ).strip()

        last = text

        if (
            p.returncode == 0
            and "ready" in text.lower()
        ):
            return

        time.sleep(
            sleep_seconds
        )

    raise PublisherContractError(
        "dataset never reached ready state. "
        f"Last status: {last!r}"
    )


def list_remote_files_text() -> str:
    p = run_cli(
        [
            "kaggle",
            "datasets",
            "files",
            DATASET_REF,
            "--page-size",
            "200",
        ]
    )

    if p.returncode != 0:
        raise PublisherContractError(
            "remote file listing failed: "
            + (
                p.stderr.strip()
                or p.stdout.strip()
            )
        )

    return (
        p.stdout
        + "\n"
        + p.stderr
    )


def download_remote_file(
    *,
    filename: str,
    destination: Path,
) -> Path:

    p = run_cli(
        [
            "kaggle",
            "datasets",
            "download",
            DATASET_REF,
            "-f",
            filename,
            "-p",
            str(destination),
            "-o",
        ]
    )

    if p.returncode != 0:
        raise PublisherContractError(
            f"remote download failed for {filename}: "
            + (
                p.stderr.strip()
                or p.stdout.strip()
            )
        )

    matches = [
        x
        for x in destination.rglob(filename)
        if x.is_file()
    ]

    if len(matches) != 1:
        raise PublisherContractError(
            f"expected one downloaded {filename}; "
            f"observed={len(matches)}"
        )

    return matches[0]


def publish_stage_as_new_version(
    *,
    stage_dir: Path,
    message: str,
):
    """
    Create exactly one new Dataset version.

    A successful CLI return only means the version request was
    accepted. Remote durability requires later readiness + fresh
    download/hash verification.
    """

    cmd = build_version_command(
        stage_dir,
        message,
    )

    return run_cli(
        cmd
    )


def synthetic_self_test() -> None:
    root = Path(
        tempfile.mkdtemp(
            prefix="exp04-publisher-self-test-"
        )
    )

    try:
        source = root / "source"
        stage = root / "stage"

        source.mkdir()
        stage.mkdir()

        (
            source / "execution_manifest.json"
        ).write_bytes(
            b'{"synthetic":true,"protected":false}\n'
        )

        def write_csv(
            path: Path,
            n: int,
            payload_prefix: str,
        ) -> None:
            with path.open(
                "w",
                encoding="utf-8",
                newline="",
            ) as f:
                writer = csv.writer(
                    f,
                    lineterminator="\n",
                )

                writer.writerow(
                    [
                        "synthetic_row_id",
                        "opaque_payload",
                    ]
                )

                for i in range(n):
                    writer.writerow(
                        [
                            i,
                            payload_prefix
                            + "-"
                            + str(1000000 - i),
                        ]
                    )

        main_path = (
            source / "main_per_perturbation.csv"
        )

        null_path = (
            source / "permutation_null_per_perturbation.csv"
        )

        write_csv(main_path, 0, "A")

        d = checkpoint_due(
            count_source_rows(source),
            Counts(0, 0),
        )

        assert not d.publish
        assert d.reason == "not-due"

        write_csv(main_path, 9, "B")

        d = checkpoint_due(
            count_source_rows(source),
            Counts(0, 0),
        )

        assert not d.publish

        write_csv(main_path, 10, "C")

        local10 = count_source_rows(source)

        d10 = checkpoint_due(
            local10,
            Counts(0, 0),
        )

        assert d10.publish
        assert d10.reason == "main-cadence"

        stable_exact_snapshot(
            source,
            settle_seconds=0.01,
        )

        hashes10 = stage_exact_snapshot(
            source,
            stage,
        )

        assert (
            hashes10["main_per_perturbation.csv"]
            == sha256_file(
                stage / "main_per_perturbation.csv"
            )
        )

        for p in stage.iterdir():
            p.unlink()

        write_csv(
            main_path,
            10,
            "TOTALLY-DIFFERENT-OPAQUE-VALUE",
        )

        d10_values_changed = checkpoint_due(
            count_source_rows(source),
            Counts(0, 0),
        )

        assert d10_values_changed.publish == d10.publish
        assert d10_values_changed.reason == d10.reason

        write_csv(main_path, 19, "D")

        d19 = checkpoint_due(
            count_source_rows(source),
            Counts(10, 0),
        )

        assert not d19.publish

        write_csv(main_path, 20, "E")

        d20 = checkpoint_due(
            count_source_rows(source),
            Counts(10, 0),
        )

        assert d20.publish
        assert d20.reason == "main-cadence"

        write_csv(
            main_path,
            MAIN_TOTAL,
            "F",
        )

        dmain = checkpoint_due(
            count_source_rows(source),
            Counts(MAIN_TOTAL - 5, 0),
        )

        assert dmain.publish
        assert dmain.reason == "main-boundary"

        write_csv(null_path, 9, "G")

        dnull9 = checkpoint_due(
            count_source_rows(source),
            Counts(MAIN_TOTAL, 0),
        )

        assert not dnull9.publish

        write_csv(null_path, 10, "H")

        dnull10 = checkpoint_due(
            count_source_rows(source),
            Counts(MAIN_TOTAL, 0),
        )

        assert dnull10.publish
        assert dnull10.reason == "null-cadence"

        write_csv(
            null_path,
            NULL_TOTAL,
            "I",
        )

        dnull_boundary = checkpoint_due(
            count_source_rows(source),
            Counts(
                MAIN_TOTAL,
                NULL_TOTAL - 4,
            ),
        )

        assert dnull_boundary.publish
        assert dnull_boundary.reason == "null-boundary"

        dfinal_same = checkpoint_due(
            count_source_rows(source),
            Counts(
                MAIN_TOTAL,
                NULL_TOTAL,
            ),
            final_complete=True,
        )

        assert not dfinal_same.publish

        write_csv(
            null_path,
            NULL_TOTAL - 1,
            "J",
        )

        dfinal = checkpoint_due(
            count_source_rows(source),
            Counts(
                MAIN_TOTAL,
                NULL_TOTAL - 2,
            ),
            final_complete=True,
        )

        assert dfinal.publish
        assert dfinal.reason == "final-boundary"

        rejected = False

        try:
            checkpoint_due(
                Counts(5, 0),
                Counts(6, 0),
            )

        except PublisherContractError:
            rejected = True

        assert rejected

        rejected = False

        write_csv(
            main_path,
            MAIN_TOTAL - 1,
            "K",
        )

        write_csv(
            null_path,
            1,
            "L",
        )

        try:
            count_source_rows(source)

        except PublisherContractError:
            rejected = True

        assert rejected

        null_path.unlink()

        write_csv(
            main_path,
            10,
            "M",
        )

        unexpected = source / "unexpected.txt"
        unexpected.write_bytes(b"synthetic only\n")

        rejected = False

        try:
            exact_artifact_hashes(source)

        except PublisherContractError:
            rejected = True

        assert rejected

        unexpected.unlink()

        stable_exact_snapshot(
            source,
            settle_seconds=0.01,
        )

        final_hashes = stage_exact_snapshot(
            source,
            stage,
        )

        for name, expected_hash in final_hashes.items():
            assert (
                sha256_file(stage / name)
                == expected_hash
            )

        write_dataset_metadata(stage)

        note = checkpoint_note(
            sequence=1,
            decision=checkpoint_due(
                count_source_rows(source),
                Counts(0, 0),
            ),
        )

        assert "main_rows=10" in note
        assert "null_rows=0" in note

        print("SELFTEST PASS — 0-row state not due.")
        print("SELFTEST PASS — 9-row state not due.")
        print("SELFTEST PASS — 10-row main cadence due.")
        print(
            "SELFTEST PASS — publication decision invariant "
            "to opaque result-value changes."
        )
        print(
            "SELFTEST PASS — remote-baseline cadence comparison exact."
        )
        print(
            "SELFTEST PASS — main completion boundary exact."
        )
        print(
            "SELFTEST PASS — null cadence exact."
        )
        print(
            "SELFTEST PASS — null completion boundary exact."
        )
        print(
            "SELFTEST PASS — final boundary exact."
        )
        print(
            "SELFTEST PASS — duplicate checkpoint suppressed."
        )
        print(
            "SELFTEST PASS — impossible remote-ahead state rejected."
        )
        print(
            "SELFTEST PASS — null-before-main state rejected."
        )
        print(
            "SELFTEST PASS — unexpected output file rejected."
        )
        print(
            "SELFTEST PASS — exact-byte staging verified."
        )
        print(
            "SELFTEST PASS — no production artifact transformation."
        )

    finally:
        shutil.rmtree(
            root,
            ignore_errors=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--self-test",
        action="store_true",
    )

    parser.add_argument(
        "--dummy-live-transport-test",
        action="store_true",
    )

    args = parser.parse_args()

    if args.self_test:
        synthetic_self_test()
        return

    if args.dummy_live_transport_test:
        print(
            "DUMMY LIVE TRANSPORT MODE AVAILABLE — "
            "caller must provide the controlled staging/test harness."
        )
        return

    raise PublisherContractError(
        "Biological live publication mode remains disabled."
    )


if __name__ == "__main__":
    main()
