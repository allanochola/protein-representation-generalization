from __future__ import annotations

from pathlib import Path
import argparse
import os
import signal
import subprocess
import sys
import time


ENABLE_LIVE_PHASE_P_LAUNCH = False

SCIENTIFIC_HEAD = "5277f686ad09ead8921462cb9ed9a53324007c42"
RUNNER_SHA256 = "e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec"
TRACE_GATE_LINE = 3783

RUNNER_REL = (
    "experiments/04-depth-and-basis/"
    "phase_p_biological_probe/"
    "run_phase_p_biological_probe.py"
)

OUTPUT_REL = (
    "experiments/04-depth-and-basis/"
    "phase_p_biological_probe/output"
)

MANIFEST_FILENAME = "execution_manifest.json"


class LiveLauncherContractError(RuntimeError):
    pass


def process_is_stopped(
    pid: int,
) -> bool:
    status = Path(
        f"/proc/{pid}/status"
    )

    if not status.is_file():
        return False

    for line in status.read_text(
        encoding="utf-8"
    ).splitlines():
        if line.startswith("State:"):
            state = (
                line.split(
                    ":",
                    1,
                )[1].strip()
            )

            return state.startswith(
                "T"
            )

    return False


def wait_until_stopped(
    child: subprocess.Popen,
    *,
    timeout_seconds: float = 60.0,
) -> None:
    deadline = (
        time.monotonic()
        + float(timeout_seconds)
    )

    while (
        time.monotonic()
        <= deadline
    ):
        if child.poll() is not None:
            raise LiveLauncherContractError(
                "child exited before reaching trace gate"
            )

        if process_is_stopped(
            child.pid
        ):
            return

        time.sleep(
            0.005
        )

    raise LiveLauncherContractError(
        "timed out waiting for child trace gate"
    )


def build_trace_bootstrap(
    runner_path: Path,
    gate_line: int,
) -> str:
    runner_path = Path(
        runner_path
    ).resolve()

    return f"""
import os
import runpy
import signal
import sys

TARGET = {str(runner_path)!r}
GATE = {int(gate_line)}


def tracer(frame, event, arg):
    if (
        event == "line"
        and os.path.abspath(
            frame.f_code.co_filename
        ) == TARGET
        and frame.f_lineno == GATE
    ):
        sys.settrace(None)

        os.kill(
            os.getpid(),
            signal.SIGSTOP,
        )

    return tracer


sys.settrace(
    tracer
)

runpy.run_path(
    TARGET,
    run_name="__main__",
)
"""


def start_child_at_pre_sweep_gate(
    *,
    scientific_repo: Path,
) -> subprocess.Popen:
    scientific_repo = Path(
        scientific_repo
    )

    runner_path = (
        scientific_repo
        / RUNNER_REL
    ).resolve()

    bootstrap = (
        build_trace_bootstrap(
            runner_path,
            TRACE_GATE_LINE,
        )
    )

    child = subprocess.Popen(
        [
            sys.executable,
            "-c",
            bootstrap,
        ],
        cwd=scientific_repo,
    )

    wait_until_stopped(
        child
    )

    output_dir = (
        scientific_repo
        / OUTPUT_REL
    )

    manifest_path = (
        output_dir
        / MANIFEST_FILENAME
    )

    if not output_dir.is_dir():
        raise LiveLauncherContractError(
            "child reached gate without output directory"
        )

    if not manifest_path.is_file():
        raise LiveLauncherContractError(
            "child reached gate without execution manifest"
        )

    return child


def synthetic_trace_gate_test() -> None:
    import shutil
    import tempfile

    root = Path(
        tempfile.mkdtemp(
            prefix="exp04-trace-gate-"
        )
    )

    child = None

    try:
        dummy = root / "dummy_runner.py"
        marker = root / "crossed_gate.txt"

        dummy.write_text(
            "from pathlib import Path\n"
            "x = 1\n"
            "x = 2\n"
            f"Path({str(marker)!r}).write_text('crossed', encoding='utf-8')\n"
            "x = 3\n",
            encoding="utf-8",
            newline="\n",
        )

        bootstrap = build_trace_bootstrap(
            dummy,
            4,
        )

        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                bootstrap,
            ],
            cwd=root,
        )

        wait_until_stopped(
            child,
            timeout_seconds=10.0,
        )

        if marker.exists():
            raise LiveLauncherContractError(
                "child crossed gate before release"
            )

        print(
            "PASS — trace gate stopped child before gated line."
        )

        os.kill(
            child.pid,
            signal.SIGCONT,
        )

        rc = child.wait(
            timeout=10.0
        )

        if rc != 0:
            raise LiveLauncherContractError(
                f"dummy exited nonzero after release: {rc}"
            )

        if (
            marker.read_text(
                encoding="utf-8"
            )
            != "crossed"
        ):
            raise LiveLauncherContractError(
                "dummy marker mismatch after release"
            )

        print(
            "PASS — released child continued through gated line."
        )

    finally:
        if (
            child is not None
            and child.poll() is None
        ):
            try:
                os.kill(
                    child.pid,
                    signal.SIGKILL,
                )
            except ProcessLookupError:
                pass

            try:
                child.wait(
                    timeout=2.0
                )
            except Exception:
                pass

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
        synthetic_trace_gate_test()
        return

    if args.live:
        if not ENABLE_LIVE_PHASE_P_LAUNCH:
            raise LiveLauncherContractError(
                "LIVE Phase-P launch is hard-disabled."
            )

        raise LiveLauncherContractError(
            "LIVE integration unavailable at this source boundary."
        )

    raise LiveLauncherContractError(
        "No launcher mode selected."
    )


if __name__ == "__main__":
    main()
