#!/usr/bin/env python3
"""
Experiment 04 Phase-P recovery-side execution supervisor.

This file is operational recovery infrastructure only.

It MUST NOT:
- import the scientific Phase-P runner as a module;
- inspect AUROC, selected C, supports, signs, or any result value;
- change scientific mechanics;
- mutate production result files;
- publish anything while LIVE supervision is hard-disabled.

Durability handshake
--------------------
The frozen scientific runner writes each result row as:

    writer.writerow(...)
    handle.flush()
    os.fsync(handle.fileno())
    [writable handle closes]

Linux IN_CLOSE_WRITE is therefore downstream of the successful fsync return
for this exact frozen synchronous writer.

When a checkpoint is due, the supervisor stops the child process, waits until
Linux reports it stopped, invokes the checkpoint callback against quiescent
source bytes, and resumes the exact same child only after the callback returns
successfully.

The checkpoint decision depends only on durable row counts and frozen boundary
counts. Result values are opaque.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional
import argparse
import csv
import ctypes
import hashlib
import os
import select
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time


# ---------------------------------------------------------------------------
# HARD LIVE LOCK
# ---------------------------------------------------------------------------

ENABLE_LIVE_PHASE_P_SUPERVISION = False


# ---------------------------------------------------------------------------
# FROZEN PRODUCTION SHAPE
# ---------------------------------------------------------------------------

CHECKPOINT_CADENCE = 10

PRODUCTION_MAIN_TOTAL = 2100
PRODUCTION_NULL_TOTAL = 100

MAIN_FILENAME = "main_per_perturbation.csv"
NULL_FILENAME = "permutation_null_per_perturbation.csv"

IN_CLOSE_WRITE = 0x00000008
IN_CREATE = 0x00000100
IN_MOVED_TO = 0x00000080

WATCH_MASK = (
    IN_CLOSE_WRITE
    | IN_CREATE
    | IN_MOVED_TO
)

EVENT_STRUCT = struct.Struct("iIII")


class SupervisorContractError(RuntimeError):
    """Recovery-side supervisor contract failure."""


@dataclass(frozen=True)
class RowCounts:
    main: int
    null: int

    @property
    def total(self) -> int:
        return int(self.main + self.null)


@dataclass(frozen=True)
class VerifiedCheckpoint:
    counts: RowCounts
    reason: str


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
    """
    Count CSV data rows only.

    No result value is interpreted.
    """

    if not path.exists():
        return 0

    if not path.is_file():
        raise SupervisorContractError(
            f"CSV path is not a regular file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.reader(f)

        try:
            header = next(reader)
        except StopIteration:
            raise SupervisorContractError(
                f"CSV is empty: {path}"
            )

        if not header:
            raise SupervisorContractError(
                f"CSV header is empty: {path}"
            )

        count = 0

        for row in reader:
            if len(row) != len(header):
                raise SupervisorContractError(
                    f"Malformed CSV row in {path.name}"
                )

            count += 1

    return int(count)


def count_rows(
    source_dir: Path,
    *,
    main_filename: str = MAIN_FILENAME,
    null_filename: str = NULL_FILENAME,
) -> RowCounts:
    return RowCounts(
        main=csv_data_row_count(
            source_dir / main_filename
        ),
        null=csv_data_row_count(
            source_dir / null_filename
        ),
    )


def validate_counts(
    counts: RowCounts,
    *,
    main_total: int,
    null_total: int,
) -> None:
    if counts.main < 0 or counts.null < 0:
        raise SupervisorContractError(
            "negative row count impossible"
        )

    if counts.main > main_total:
        raise SupervisorContractError(
            f"main rows exceed frozen total: "
            f"{counts.main}>{main_total}"
        )

    if counts.null > null_total:
        raise SupervisorContractError(
            f"null rows exceed frozen total: "
            f"{counts.null}>{null_total}"
        )

    if (
        counts.null > 0
        and counts.main != main_total
    ):
        raise SupervisorContractError(
            "null rows appeared before exact main completion"
        )


def checkpoint_reasons(
    *,
    current: RowCounts,
    last_verified: RowCounts,
    main_total: int,
    null_total: int,
    cadence: int,
    final: bool,
) -> tuple[str, ...]:
    """
    Pure result-blind checkpoint decision.

    Only row counts and frozen boundaries are permitted.
    """

    validate_counts(
        current,
        main_total=main_total,
        null_total=null_total,
    )

    validate_counts(
        last_verified,
        main_total=main_total,
        null_total=null_total,
    )

    if current.total < last_verified.total:
        raise SupervisorContractError(
            "current durable row count moved backward"
        )

    reasons = []

    if (
        current.total
        - last_verified.total
        >= cadence
    ):
        reasons.append("cadence")

    if (
        current.main == main_total
        and last_verified.main < main_total
    ):
        reasons.append("main_completion")

    if (
        current.null == null_total
        and last_verified.null < null_total
    ):
        reasons.append("null_completion")

    if (
        final
        and current.main == main_total
        and current.null == null_total
        and current != last_verified
    ):
        reasons.append("final")

    return tuple(reasons)


def parse_inotify_buffer(
    data: bytes,
) -> list[dict[str, object]]:
    events = []
    offset = 0

    while offset < len(data):
        if (
            len(data) - offset
            < EVENT_STRUCT.size
        ):
            raise SupervisorContractError(
                "truncated inotify event header"
            )

        (
            wd,
            mask,
            cookie,
            name_len,
        ) = EVENT_STRUCT.unpack_from(
            data,
            offset,
        )

        offset += EVENT_STRUCT.size

        if (
            len(data) - offset
            < name_len
        ):
            raise SupervisorContractError(
                "truncated inotify event name"
            )

        raw_name = data[
            offset:
            offset + name_len
        ]

        offset += name_len

        name = (
            raw_name
            .split(b"\x00", 1)[0]
            .decode(
                "utf-8",
                errors="strict",
            )
        )

        events.append(
            {
                "wd": int(wd),
                "mask": int(mask),
                "cookie": int(cookie),
                "name": name,
            }
        )

    return events


def open_inotify_watch(
    directory: Path,
) -> int:
    libc = ctypes.CDLL(
        None,
        use_errno=True,
    )

    init = libc.inotify_init1
    init.argtypes = [ctypes.c_int]
    init.restype = ctypes.c_int

    add_watch = libc.inotify_add_watch
    add_watch.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint32,
    ]
    add_watch.restype = ctypes.c_int

    fd = init(
        os.O_NONBLOCK
    )

    if fd < 0:
        err = ctypes.get_errno()

        raise SupervisorContractError(
            "inotify_init1 failed: "
            f"errno={err} {os.strerror(err)}"
        )

    wd = add_watch(
        fd,
        os.fsencode(
            str(directory)
        ),
        WATCH_MASK,
    )

    if wd < 0:
        err = ctypes.get_errno()
        os.close(fd)

        raise SupervisorContractError(
            "inotify_add_watch failed: "
            f"errno={err} {os.strerror(err)}"
        )

    return fd


def process_is_stopped(
    pid: int,
) -> bool:
    status = Path(
        f"/proc/{pid}/status"
    )

    if not status.exists():
        return False

    text = status.read_text(
        encoding="utf-8"
    )

    for line in text.splitlines():
        if line.startswith("State:"):
            state = (
                line.split(
                    ":",
                    1,
                )[1]
                .strip()
            )

            return state.startswith(
                ("T", "t")
            )

    raise SupervisorContractError(
        f"could not determine process state for pid={pid}"
    )


def stop_child_and_wait(
    child: subprocess.Popen,
    *,
    timeout_seconds: float = 5.0,
) -> bool:
    """
    Stop a live child and prove it entered Linux stopped state.

    Returns False when the child had already exited.
    """

    if child.poll() is not None:
        return False

    os.kill(
        child.pid,
        signal.SIGSTOP,
    )

    deadline = (

        None

        if timeout_seconds is None

        else (

            time.monotonic()

            + float(timeout_seconds)

        )

    )

    while (
        time.monotonic()
        < deadline
    ):
        if child.poll() is not None:
            return False

        if process_is_stopped(
            child.pid
        ):
            return True

        time.sleep(0.005)

    raise SupervisorContractError(
        "child did not enter stopped state"
    )


def resume_child(
    child: subprocess.Popen,
) -> None:
    if child.poll() is not None:
        return

    os.kill(
        child.pid,
        signal.SIGCONT,
    )


def source_hashes(
    source_dir: Path,
    names: Iterable[str],
) -> Dict[str, str]:
    out = {}

    for name in names:
        path = source_dir / name

        if path.exists():
            if not path.is_file():
                raise SupervisorContractError(
                    f"source artifact is not file: {name}"
                )

            out[name] = sha256_file(
                path
            )

    return out


def supervise_child(
    *,
    child: subprocess.Popen,
    source_dir: Path,
    publish_callback: Callable[
        [RowCounts, tuple[str, ...]],
        None,
    ],
    main_total: int,
    null_total: int,
    cadence: int,
    main_filename: str = MAIN_FILENAME,
    null_filename: str = NULL_FILENAME,
    initial_verified: Optional[RowCounts] = None,
    timeout_seconds: Optional[float] = 60.0,
    child_initially_stopped: bool = False,
) -> list[VerifiedCheckpoint]:
    """
    Observe one already-started child.

    The supervisor never inspects result values. It reacts only to
    IN_CLOSE_WRITE on the two permitted CSV filenames and to child exit.
    """

    if cadence <= 0:
        raise SupervisorContractError(
            "checkpoint cadence must be positive"
        )

    source_dir = Path(
        source_dir
    )

    if not source_dir.is_dir():
        raise SupervisorContractError(
            "source directory must exist before supervision"
        )

    last_verified = (
        initial_verified
        if initial_verified is not None
        else RowCounts(
            main=0,
            null=0,
        )
    )

    validate_counts(
        last_verified,
        main_total=main_total,
        null_total=null_total,
    )

    permitted_names = {
        main_filename,
        null_filename,
    }

    checkpoints = []
    fd = open_inotify_watch(
        source_dir
    )

    if child_initially_stopped:
        if child.poll() is not None:
            os.close(fd)
            raise SupervisorContractError(
                "initially-stopped child already exited"
            )

        if not process_is_stopped(
            child.pid
        ):
            os.close(fd)
            raise SupervisorContractError(
                "child_initially_stopped=True but child is not stopped"
            )

        resume_child(
            child
        )

    deadline = (
        None
        if timeout_seconds is None
        else (
            time.monotonic()
            + float(timeout_seconds)
        )
    )

    try:
        while True:
            if (
                deadline is not None
                and time.monotonic()
                > deadline
            ):
                raise SupervisorContractError(
                    "supervision timeout"
                )

            child_exited = (
                child.poll()
                is not None
            )

            readable, _, _ = select.select(
                [fd],
                [],
                [],
                0.05,
            )

            relevant_close = False

            if readable:
                data = os.read(
                    fd,
                    65536,
                )

                events = parse_inotify_buffer(
                    data
                )

                for event in events:
                    if (
                        event["name"]
                        in permitted_names
                        and (
                            int(
                                event["mask"]
                            )
                            & IN_CLOSE_WRITE
                        )
                    ):
                        relevant_close = True

            if relevant_close:
                # First count only determines whether a checkpoint could be due.
                preliminary = count_rows(
                    source_dir,
                    main_filename=main_filename,
                    null_filename=null_filename,
                )

                validate_counts(
                    preliminary,
                    main_total=main_total,
                    null_total=null_total,
                )

                preliminary_reasons = checkpoint_reasons(
                    current=preliminary,
                    last_verified=last_verified,
                    main_total=main_total,
                    null_total=null_total,
                    cadence=cadence,
                    final=False,
                )

                if preliminary_reasons:
                    stopped = stop_child_and_wait(
                        child
                    )

                    quiescent_ok = False

                    try:
                        # Recount only after the process is proven quiescent.
                        stable_counts = count_rows(
                            source_dir,
                            main_filename=main_filename,
                            null_filename=null_filename,
                        )

                        reasons = checkpoint_reasons(
                            current=stable_counts,
                            last_verified=last_verified,
                            main_total=main_total,
                            null_total=null_total,
                            cadence=cadence,
                            final=False,
                        )

                        if reasons:
                            publish_callback(
                                stable_counts,
                                reasons,
                            )

                            checkpoints.append(
                                VerifiedCheckpoint(
                                    counts=stable_counts,
                                    reason="+".join(
                                        reasons
                                    ),
                                )
                            )

                            last_verified = (

                                stable_counts

                            )


                        quiescent_ok = True

                    finally:
                        if stopped and quiescent_ok:
                            resume_child(
                                child
                            )

            if child_exited:
                # Drain any events already queued before final census.
                while True:
                    readable, _, _ = select.select(
                        [fd],
                        [],
                        [],
                        0,
                    )

                    if not readable:
                        break

                    data = os.read(
                        fd,
                        65536,
                    )

                    # Parsing is still required to reject malformed kernel data.
                    parse_inotify_buffer(
                        data
                    )

                final_counts = count_rows(
                    source_dir,
                    main_filename=main_filename,
                    null_filename=null_filename,
                )

                validate_counts(
                    final_counts,
                    main_total=main_total,
                    null_total=null_total,
                )

                # FINAL is a mandatory execution boundary independent
                # of whether the exact terminal row-count state was already
                # checkpointed as null_completion.
                #
                # This decision remains result-value blind: it depends only
                # on child exit plus exact frozen terminal row counts.
                if final_counts != RowCounts(
                    main=main_total,
                    null=null_total,
                ):
                    raise SupervisorContractError(
                        "child exited before exact final census"
                    )

                final_reasons = ("final",)

                publish_callback(
                    final_counts,
                    final_reasons,
                )

                checkpoints.append(
                    VerifiedCheckpoint(
                        counts=final_counts,
                        reason="final",
                    )
                )

                break

        if child.returncode != 0:
            raise SupervisorContractError(
                f"child exited nonzero: {child.returncode}"
            )

        final_counts = count_rows(
            source_dir,
            main_filename=main_filename,
            null_filename=null_filename,
        )

        if final_counts != RowCounts(
            main=main_total,
            null=null_total,
        ):
            raise SupervisorContractError(
                "child exited without exact synthetic/production census"
            )

        return checkpoints

    finally:
        os.close(
            fd
        )


def _synthetic_child_code() -> str:
    return r"""
from pathlib import Path
import csv
import os
import sys
import time

source_dir = Path(sys.argv[1])
payload = sys.argv[2]
main_total = int(sys.argv[3])
null_total = int(sys.argv[4])

main_path = source_dir / "main_per_perturbation.csv"
null_path = source_dir / "permutation_null_per_perturbation.csv"

def append_row(path, fieldnames, row):
    new_file = not path.exists()

    with path.open(
        "a",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="raise",
        )

        if new_file:
            writer.writeheader()

        writer.writerow(row)
        handle.flush()
        os.fsync(handle.fileno())

    time.sleep(0.06)

for i in range(1, main_total + 1):
    append_row(
        main_path,
        ("id", "opaque_payload"),
        {
            "id": i,
            "opaque_payload": f"{payload}-MAIN-{i}",
        },
    )

for i in range(1, null_total + 1):
    append_row(
        null_path,
        ("id", "opaque_payload"),
        {
            "id": i,
            "opaque_payload": f"{payload}-NULL-{i}",
        },
    )
"""


def _run_one_synthetic_case(
    *,
    payload: str,
) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int, str], ...],
]:
    main_total = 23
    null_total = 7
    cadence = 10

    with tempfile.TemporaryDirectory(
        prefix="exp04-supervisor-selftest-"
    ) as tmp:
        source_dir = Path(tmp)
        callback_records = []

        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _synthetic_child_code(),
                str(source_dir),
                payload,
                str(main_total),
                str(null_total),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        def fake_publish(
            counts: RowCounts,
            reasons: tuple[str, ...],
        ) -> None:
            # At callback entry the child must be stopped or already exited.
            if (
                child.poll() is None
                and not process_is_stopped(
                    child.pid
                )
            ):
                raise SupervisorContractError(
                    "checkpoint callback observed a running child"
                )

            before = source_hashes(
                source_dir,
                (
                    MAIN_FILENAME,
                    NULL_FILENAME,
                ),
            )

            time.sleep(0.08)

            after = source_hashes(
                source_dir,
                (
                    MAIN_FILENAME,
                    NULL_FILENAME,
                ),
            )

            if before != after:
                raise SupervisorContractError(
                    "source changed while checkpoint callback was active"
                )

            callback_records.append(
                (
                    counts.main,
                    counts.null,
                    "+".join(
                        reasons
                    ),
                )
            )

        checkpoints = supervise_child(
            child=child,
            source_dir=source_dir,
            publish_callback=fake_publish,
            main_total=main_total,
            null_total=null_total,
            cadence=cadence,
            timeout_seconds=30.0,
        )

        stdout, stderr = child.communicate(
            timeout=2.0
        )

        if stdout:
            raise SupervisorContractError(
                "synthetic child unexpectedly wrote stdout"
            )

        if stderr:
            raise SupervisorContractError(
                "synthetic child unexpectedly wrote stderr"
            )

        checkpoint_counts = tuple(
            (
                item.counts.main,
                item.counts.null,
            )
            for item in checkpoints
        )

        callback_tuple = tuple(
            callback_records
        )

        if not checkpoint_counts:
            raise SupervisorContractError(
                "synthetic supervisor emitted no checkpoints"
            )

        # Required durable states.
        if (10, 0) not in checkpoint_counts:
            raise SupervisorContractError(
                "10-row cadence checkpoint missing"
            )

        if (20, 0) not in checkpoint_counts:
            raise SupervisorContractError(
                "20-row cadence checkpoint missing"
            )

        if (23, 0) not in checkpoint_counts:
            raise SupervisorContractError(
                "main-completion checkpoint missing"
            )

        if checkpoint_counts.count(
            (23, 7)
        ) != 2:
            raise SupervisorContractError(
                "expected separate null-completion and final "
                "checkpoints at terminal state"
            )

        terminal_reasons = [
            reason
            for m, n, reason
            in callback_tuple
            if (m, n) == (23, 7)
        ]

        if terminal_reasons != [
            "null_completion",
            "final",
        ]:
            raise SupervisorContractError(
                "terminal checkpoint reasons must be exactly "
                "null_completion then final"
            )

        # The terminal row-count state MUST occur twice:
        #   1. null_completion
        #   2. explicit final completion
        #
        # No other row-count state may be duplicated.
        terminal_state = (
            main_total,
            null_total,
        )

        terminal_occurrences = sum(
            1
            for state in checkpoint_counts
            if state == terminal_state
        )

        if terminal_occurrences != 2:
            raise SupervisorContractError(
                "terminal state must be checkpointed exactly twice: "
                "null_completion then final"
            )

        nonterminal_states = [
            state
            for state in checkpoint_counts
            if state != terminal_state
        ]

        if (
            len(nonterminal_states)
            != len(set(nonterminal_states))
        ):
            raise SupervisorContractError(
                "nonterminal duplicate checkpoint state emitted"
            )

        # Every callback corresponds exactly to a recorded checkpoint.
        if tuple(
            (m, n)
            for m, n, _reason
            in callback_tuple
        ) != checkpoint_counts:
            raise SupervisorContractError(
                "callback/checkpoint state mismatch"
            )

        return (
            checkpoint_counts,
            callback_tuple,
        )


def synthetic_self_test() -> None:
    print(
        "── SUPERVISOR SYNTHETIC SELF-TEST ──"
    )

    # Pure decision tests.
    zero = RowCounts(
        main=0,
        null=0,
    )

    nine = RowCounts(
        main=9,
        null=0,
    )

    ten = RowCounts(
        main=10,
        null=0,
    )

    if checkpoint_reasons(
        current=nine,
        last_verified=zero,
        main_total=23,
        null_total=7,
        cadence=10,
        final=False,
    ):
        raise SupervisorContractError(
            "9 rows must not trigger cadence"
        )

    reasons_10 = checkpoint_reasons(
        current=ten,
        last_verified=zero,
        main_total=23,
        null_total=7,
        cadence=10,
        final=False,
    )

    if "cadence" not in reasons_10:
        raise SupervisorContractError(
            "10 rows must trigger cadence"
        )

    print(
        "PASS — 9-row not-due / 10-row due contract."
    )

    main_done_reasons = checkpoint_reasons(
        current=RowCounts(
            main=23,
            null=0,
        ),
        last_verified=RowCounts(
            main=20,
            null=0,
        ),
        main_total=23,
        null_total=7,
        cadence=10,
        final=False,
    )

    if "main_completion" not in main_done_reasons:
        raise SupervisorContractError(
            "main completion boundary missing"
        )

    print(
        "PASS — mandatory main-completion boundary."
    )

    try:
        checkpoint_reasons(
            current=RowCounts(
                main=22,
                null=1,
            ),
            last_verified=RowCounts(
                main=20,
                null=0,
            ),
            main_total=23,
            null_total=7,
            cadence=10,
            final=False,
        )
    except SupervisorContractError:
        pass
    else:
        raise SupervisorContractError(
            "null-before-main state was accepted"
        )

    print(
        "PASS — null-before-main rejected."
    )

    counts_a, records_a = (
        _run_one_synthetic_case(
            payload="OPAQUE-A",
        )
    )

    print(
        f"Case A checkpoint states: "
        f"{counts_a!r}"
    )

    print(
        f"Case A callback records : "
        f"{records_a!r}"
    )

    counts_b, records_b = (
        _run_one_synthetic_case(
            payload="COMPLETELY-DIFFERENT-B",
        )
    )

    print(
        f"Case B checkpoint states: "
        f"{counts_b!r}"
    )

    print(
        f"Case B callback records : "
        f"{records_b!r}"
    )

    if counts_a != counts_b:
        raise SupervisorContractError(
            "checkpoint decisions changed when only opaque values changed"
        )

    reasons_a = tuple(
        reason
        for _m, _n, reason
        in records_a
    )

    reasons_b = tuple(
        reason
        for _m, _n, reason
        in records_b
    )

    if reasons_a != reasons_b:
        raise SupervisorContractError(
            "checkpoint reasons changed when only opaque values changed"
        )

    print(
        "PASS — checkpoint decisions are result-value blind."
    )

    print(
        "PASS — child was quiescent during every synthetic checkpoint callback."
    )

    print(
        "PASS — cadence + main boundary + null/final boundary exercised."
    )

    print(
        "PASS — nonterminal duplicate checkpoint states suppressed."
    )

    print(
        "PASS — explicit final checkpoint emitted separately "
        "after null completion."
    )

    print(
        "FINAL PASS — recovery-side supervisor synthetic self-test passed."
    )


def main() -> int:
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

    if args.live:
        if not ENABLE_LIVE_PHASE_P_SUPERVISION:
            raise SupervisorContractError(
                "LIVE Phase-P supervision is hard-disabled."
            )

        raise SupervisorContractError(
            "LIVE Phase-P supervision has no enabled implementation "
            "at this source boundary."
        )

    if args.synthetic_self_test:
        synthetic_self_test()
        return 0

    raise SupervisorContractError(
        "No action selected. Only --synthetic-self-test is "
        "authorized at this source boundary."
    )


if __name__ == "__main__":
    sys.exit(
        main()
    )
