from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
import argparse
import hashlib
import shutil
import tempfile


ENABLE_LIVE_PHASE_P_CHECKPOINT_ADAPTER = False

KNOWN_SUPERVISOR_REASONS = frozenset(
    {
        "cadence",
        "main_completion",
        "null_completion",
        "final",
    }
)


class AdapterContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class TransportHooks:
    assert_private: Callable[[], None]
    publish_version: Callable[[Path, str], object]
    wait_ready: Callable[[], None]
    list_remote_files_text: Callable[[], str]
    download_remote_file: Callable[[str, Path], Path]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with Path(path).open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def _reason_string(
    reasons: Iterable[str],
) -> str:
    reasons = tuple(reasons)

    if not reasons:
        raise AdapterContractError(
            "checkpoint reasons may not be empty"
        )

    unknown = sorted(
        set(reasons)
        - KNOWN_SUPERVISOR_REASONS
    )

    if unknown:
        raise AdapterContractError(
            "unknown supervisor checkpoint reason(s): "
            + ", ".join(unknown)
        )

    if (
        "final" in reasons
        and reasons != ("final",)
    ):
        raise AdapterContractError(
            "final checkpoint must be a distinct boundary"
        )

    return "+".join(reasons)


def _remote_listing_has_exact_name(
    listing_text: str,
    filename: str,
) -> bool:
    for line in listing_text.splitlines():
        fields = line.split()

        if filename in fields:
            return True

        if line.strip() == filename:
            return True

    return False


def publish_verified_checkpoint(
    *,
    publisher,
    source_dir: Path,
    expected_counts,
    reasons: tuple[str, ...],
    remote_verified,
    sequence: int,
    transport: TransportHooks,
):
    """
    Publish one supervisor-authorized durable checkpoint.

    The supervisor owns WHEN publication is mandatory.

    This adapter does not call publisher.checkpoint_due(), because
    the frozen recovery contract requires a distinct final version
    even when the terminal row-count state was already published as
    null_completion.

    All decisions are result-value blind.
    """

    reason_text = _reason_string(
        reasons
    )

    source_dir = Path(
        source_dir
    )

    if not source_dir.is_dir():
        raise AdapterContractError(
            "checkpoint source directory missing"
        )

    if sequence <= 0:
        raise AdapterContractError(
            "checkpoint sequence must be positive"
        )

    local = publisher.Counts(
        main=int(expected_counts.main),
        null=int(expected_counts.null),
    )

    remote = publisher.Counts(
        main=int(remote_verified.main),
        null=int(remote_verified.null),
    )

    observed = publisher.count_source_rows(
        source_dir
    )

    if observed != local:
        raise AdapterContractError(
            "supervisor durable counts do not match "
            "publisher source census"
        )

    # Remote may never be ahead.
    if remote.main > local.main:
        raise AdapterContractError(
            "remote main count exceeds local durable count"
        )

    if remote.null > local.null:
        raise AdapterContractError(
            "remote null count exceeds local durable count"
        )

    # Non-final publication must advance row-count state.
    if (
        reasons != ("final",)
        and local == remote
    ):
        raise AdapterContractError(
            "non-final duplicate checkpoint state"
        )

    # FINAL is intentionally the sole permitted same-count duplicate.
    if reasons == ("final",):
        if (
            local.main != publisher.MAIN_TOTAL
            or local.null != publisher.NULL_TOTAL
        ):
            raise AdapterContractError(
                "final publication requires exact terminal census"
            )

    transport.assert_private()

    # Prove bytes/counts stable while the supervisor has the child
    # quiescent (or after the child has exited at final).
    publisher.stable_exact_snapshot(
        source_dir
    )

    with tempfile.TemporaryDirectory(
        prefix="exp04-phase-p-checkpoint-stage-"
    ) as stage_tmp:
        stage_dir = Path(
            stage_tmp
        )

        expected_hashes = (
            publisher.stage_exact_snapshot(
                source_dir,
                stage_dir,
            )
        )

        publisher.write_dataset_metadata(
            stage_dir
        )

        decision = publisher.PublishDecision(
            publish=True,
            reason=reason_text,
            local=local,
            remote=remote,
        )

        message = publisher.checkpoint_note(
            sequence=sequence,
            decision=decision,
        )

        result = transport.publish_version(
            stage_dir,
            message,
        )

        returncode = getattr(
            result,
            "returncode",
            0,
        )

        if returncode != 0:
            stderr = getattr(
                result,
                "stderr",
                "",
            )

            stdout = getattr(
                result,
                "stdout",
                "",
            )

            raise AdapterContractError(
                "Dataset version request failed: "
                + (
                    str(stderr).strip()
                    or str(stdout).strip()
                    or f"returncode={returncode}"
                )
            )

        transport.wait_ready()
        transport.assert_private()

        listing = (
            transport.list_remote_files_text()
        )

        for filename in expected_hashes:
            if not _remote_listing_has_exact_name(
                listing,
                filename,
            ):
                raise AdapterContractError(
                    "expected checkpoint artifact absent "
                    f"from remote listing: {filename}"
                )

        with tempfile.TemporaryDirectory(
            prefix="exp04-phase-p-checkpoint-download-"
        ) as download_tmp:
            download_root = Path(
                download_tmp
            )

            for filename, expected_sha in (
                expected_hashes.items()
            ):
                destination = (
                    download_root
                    / filename
                )

                destination.mkdir(
                    parents=True,
                    exist_ok=False,
                )

                downloaded = (
                    transport.download_remote_file(
                        filename,
                        destination,
                    )
                )

                got_sha = sha256_file(
                    downloaded
                )

                if got_sha != expected_sha:
                    raise AdapterContractError(
                        "fresh remote checkpoint bytes "
                        f"do not match local durable bytes: "
                        f"{filename}"
                    )

    transport.assert_private()

    return local


def _write_csv(
    path: Path,
    n: int,
    prefix: str,
) -> None:
    import csv

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
                "synthetic_id",
                "opaque_payload",
            ]
        )

        for i in range(n):
            writer.writerow(
                [
                    i,
                    f"{prefix}-{10000000 - i}",
                ]
            )


def synthetic_self_test(
    *,
    publisher,
    supervisor,
) -> None:
    print(
        "── CHECKPOINT ADAPTER SYNTHETIC SELF-TEST ──"
    )

    root = Path(
        tempfile.mkdtemp(
            prefix="exp04-adapter-self-test-"
        )
    )

    try:
        source = root / "source"
        fake_remote = root / "fake_remote"

        source.mkdir()
        fake_remote.mkdir()

        (
            source / "execution_manifest.json"
        ).write_bytes(
            b'{"synthetic":true,"protected":false}\n'
        )

        main_path = (
            source
            / "main_per_perturbation.csv"
        )

        null_path = (
            source
            / "permutation_null_per_perturbation.csv"
        )

        versions = []
        privacy_checks = []
        current_remote_files = {}

        class FakeResult:
            returncode = 0
            stdout = "synthetic accepted"
            stderr = ""

        def assert_private():
            privacy_checks.append(True)

        def publish_version(
            stage_dir: Path,
            message: str,
        ):
            snapshot = {}

            for path in Path(stage_dir).iterdir():
                if (
                    path.is_file()
                    and path.name
                    != "dataset-metadata.json"
                ):
                    snapshot[path.name] = (
                        path.read_bytes()
                    )

            current_remote_files.clear()
            current_remote_files.update(
                snapshot
            )

            versions.append(
                {
                    "message": message,
                    "files": {
                        name: hashlib.sha256(
                            payload
                        ).hexdigest()
                        for name, payload
                        in snapshot.items()
                    },
                }
            )

            return FakeResult()

        def wait_ready():
            return None

        def list_remote_files_text():
            return "\n".join(
                sorted(
                    current_remote_files
                )
            )

        def download_remote_file(
            filename: str,
            destination: Path,
        ):
            if filename not in current_remote_files:
                raise AdapterContractError(
                    "synthetic remote file absent"
                )

            out = (
                Path(destination)
                / filename
            )

            out.write_bytes(
                current_remote_files[
                    filename
                ]
            )

            return out

        transport = TransportHooks(
            assert_private=assert_private,
            publish_version=publish_version,
            wait_ready=wait_ready,
            list_remote_files_text=list_remote_files_text,
            download_remote_file=download_remote_file,
        )

        remote = publisher.Counts(
            main=0,
            null=0,
        )

        sequence = 0

        def emit(
            main: int,
            null: int,
            reasons: tuple[str, ...],
            payload: str,
        ):
            nonlocal remote, sequence

            _write_csv(
                main_path,
                main,
                payload,
            )

            if null > 0:
                _write_csv(
                    null_path,
                    null,
                    payload + "-NULL",
                )
            elif null_path.exists():
                null_path.unlink()

            sequence += 1

            local = publish_verified_checkpoint(
                publisher=publisher,
                source_dir=source,
                expected_counts=supervisor.RowCounts(
                    main=main,
                    null=null,
                ),
                reasons=reasons,
                remote_verified=remote,
                sequence=sequence,
                transport=transport,
            )

            remote = local

        emit(
            10,
            0,
            ("cadence",),
            "A",
        )

        emit(
            publisher.MAIN_TOTAL,
            0,
            ("main_completion",),
            "B",
        )

        emit(
            publisher.MAIN_TOTAL,
            10,
            ("cadence",),
            "C",
        )

        emit(
            publisher.MAIN_TOTAL,
            publisher.NULL_TOTAL,
            ("null_completion",),
            "D",
        )

        # Mandatory distinct final publication at IDENTICAL row counts.
        emit(
            publisher.MAIN_TOTAL,
            publisher.NULL_TOTAL,
            ("final",),
            "D",
        )

        if len(versions) != 5:
            raise AdapterContractError(
                "expected exactly five synthetic versions"
            )

        if (
            "reason=null_completion"
            not in versions[-2]["message"]
        ):
            raise AdapterContractError(
                "penultimate version must be null_completion"
            )

        if (
            "reason=final"
            not in versions[-1]["message"]
        ):
            raise AdapterContractError(
                "last version must be explicit final"
            )

        if (
            versions[-2]["files"]
            != versions[-1]["files"]
        ):
            raise AdapterContractError(
                "terminal null/final versions must contain "
                "identical durable production bytes"
            )

        # Non-final same-count duplicate MUST be rejected.
        rejected = False

        try:
            publish_verified_checkpoint(
                publisher=publisher,
                source_dir=source,
                expected_counts=supervisor.RowCounts(
                    main=publisher.MAIN_TOTAL,
                    null=publisher.NULL_TOTAL,
                ),
                reasons=("cadence",),
                remote_verified=publisher.Counts(
                    main=publisher.MAIN_TOTAL,
                    null=publisher.NULL_TOTAL,
                ),
                sequence=sequence + 1,
                transport=transport,
            )

        except AdapterContractError:
            rejected = True

        if not rejected:
            raise AdapterContractError(
                "non-final duplicate checkpoint was accepted"
            )

        if not privacy_checks:
            raise AdapterContractError(
                "privacy assertion hook was never exercised"
            )

        print(
            "PASS — supervisor-authorized cadence checkpoint."
        )
        print(
            "PASS — mandatory main-completion checkpoint."
        )
        print(
            "PASS — null-arm cadence checkpoint."
        )
        print(
            "PASS — mandatory null-completion checkpoint."
        )
        print(
            "PASS — explicit final checkpoint emitted as "
            "a distinct fifth version."
        )
        print(
            "PASS — terminal null/final versions preserve "
            "identical production bytes."
        )
        print(
            "PASS — non-final duplicate state rejected."
        )
        print(
            "PASS — exact-byte fresh-download verification "
            "exercised for every synthetic version."
        )
        print(
            "PASS — privacy assertion hook exercised before/"
            "after synthetic publication."
        )
        print(
            "PASS — publication decisions remain row-count/"
            "process-boundary only."
        )
        print(
            "FINAL PASS — checkpoint adapter synthetic "
            "self-test passed."
        )

    finally:
        shutil.rmtree(
            root,
            ignore_errors=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--synthetic-self-test",
        action="store_true",
    )

    parser.add_argument(
        "--live",
        action="store_true",
    )

    args = parser.parse_args()

    if args.synthetic_self_test:
        raise AdapterContractError(
            "synthetic self-test requires controlled caller "
            "to inject exact frozen modules"
        )

    if args.live:
        if not ENABLE_LIVE_PHASE_P_CHECKPOINT_ADAPTER:
            raise AdapterContractError(
                "LIVE Phase-P checkpoint adapter is hard-disabled."
            )

        raise AdapterContractError(
            "LIVE Phase-P checkpoint adapter has no wired "
            "transport entrypoint yet."
        )

    raise AdapterContractError(
        "No adapter mode selected."
    )


if __name__ == "__main__":
    main()
