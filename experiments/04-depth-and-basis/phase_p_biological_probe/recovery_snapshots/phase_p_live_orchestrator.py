from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ENABLE_LIVE_PHASE_P_ORCHESTRATION = True

DATASET_REF = "ocholla/exp04-phase-p-private-checkpoints"

SCIENTIFIC_HEAD = (
    "5277f686ad09ead8921462cb9ed9a53324007c42"
)

RUNNER_SHA256 = (
    "e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec"
)

MAIN_TOTAL = 2100
NULL_TOTAL = 100
CADENCE = 10

BASE = Path(__file__).resolve().parent

PUBLISHER_PATH = BASE / "phase_p_checkpoint_publisher.py"
ADAPTER_PATH = BASE / "phase_p_live_checkpoint_adapter.py"
SUPERVISOR_PATH = BASE / "phase_p_execution_supervisor.py"
LAUNCHER_PATH = BASE / "phase_p_live_launcher.py"


class OrchestratorContractError(RuntimeError):
    pass


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise OrchestratorContractError(
            f"cannot load recovery module: {path}"
        )

    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)

    return mod


def run_cli(cmd):
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def assert_private_dataset() -> None:
    """
    Fail closed unless the exact authorized Kaggle Dataset is PRIVATE.

    Compatible with the frozen Kaggle client 2.0.2.
    Read only.
    """

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()

        items = list(
            api.dataset_list(
                mine=True,
                search="exp04-phase-p-private-checkpoints",
            )
        )

    except Exception as exc:
        raise OrchestratorContractError(
            "private Dataset metadata lookup failed"
        ) from exc

    exact = []

    for item in items:
        data = {}

        if hasattr(
            item,
            "to_dict",
        ):
            try:
                candidate = item.to_dict()

                if isinstance(
                    candidate,
                    dict,
                ):
                    data = candidate

            except Exception:
                pass

        ref = (
            getattr(
                item,
                "ref",
                None,
            )
            or getattr(
                item,
                "datasetRef",
                None,
            )
            or getattr(
                item,
                "dataset_ref",
                None,
            )
            or data.get(
                "ref"
            )
            or data.get(
                "datasetRef"
            )
            or data.get(
                "dataset_ref"
            )
        )

        if str(
            ref
        ) == DATASET_REF:
            exact.append(
                (item, data)
            )

    if len(
        exact
    ) != 1:
        raise OrchestratorContractError(
            "exact authorized private Dataset did not resolve uniquely"
        )

    item, data = exact[0]

    private_candidates = (
        getattr(
            item,
            "isPrivate",
            None,
        ),
        getattr(
            item,
            "is_private",
            None,
        ),
        getattr(
            item,
            "private",
            None,
        ),
        data.get(
            "isPrivate"
        ),
        data.get(
            "is_private"
        ),
        data.get(
            "private"
        ),
    )

    if not any(
        value is True
        for value in private_candidates
    ):
        raise OrchestratorContractError(
            "authorized checkpoint Dataset is not explicitly PRIVATE"
        )


def make_transport(
    publisher,
    adapter,
):
    """
    Concrete transport hooks backed only by the frozen publisher.
    """

    def publish_version(
        stage_dir: Path,
        message: str,
    ):
        return publisher.publish_stage_as_new_version(
            stage_dir=stage_dir,
            message=message,
        )

    def download_remote_file(
        filename: str,
        destination: Path,
    ):
        return publisher.download_remote_file(
            filename=filename,
            destination=destination,
        )

    return adapter.TransportHooks(
        assert_private=assert_private_dataset,
        publish_version=publish_version,
        wait_ready=publisher.wait_until_dataset_ready,
        list_remote_files_text=publisher.list_remote_files_text,
        download_remote_file=download_remote_file,
    )


def make_checkpoint_callback(
    *,
    publisher,
    adapter,
    source_dir: Path,
    remote_verified,
    transport,
):
    """
    Stateful result-blind supervisor callback.

    State advances only AFTER the adapter has completed:
      version request
      readiness
      privacy recheck
      remote file visibility
      fresh-download SHA verification
      final privacy recheck.
    """

    state = {
        "remote_verified": remote_verified,
        "sequence": 0,
    }

    def callback(
        counts,
        reasons,
    ):
        sequence = (
            int(state["sequence"])
            + 1
        )

        verified = adapter.publish_verified_checkpoint(
            publisher=publisher,
            source_dir=source_dir,
            expected_counts=counts,
            reasons=tuple(reasons),
            remote_verified=state["remote_verified"],
            sequence=sequence,
            transport=transport,
        )

        # Advance only after full remote verification returns.
        state["remote_verified"] = verified
        state["sequence"] = sequence

    return callback, state


def validate_frozen_contracts(
    publisher,
    launcher,
):
    if publisher.DATASET_REF != DATASET_REF:
        raise OrchestratorContractError(
            "publisher Dataset ref mismatch"
        )

    if publisher.SCIENTIFIC_HEAD != SCIENTIFIC_HEAD:
        raise OrchestratorContractError(
            "publisher scientific HEAD mismatch"
        )

    if publisher.RUNNER_SHA256 != RUNNER_SHA256:
        raise OrchestratorContractError(
            "publisher runner SHA mismatch"
        )

    if publisher.MAIN_TOTAL != MAIN_TOTAL:
        raise OrchestratorContractError(
            "publisher main total mismatch"
        )

    if publisher.NULL_TOTAL != NULL_TOTAL:
        raise OrchestratorContractError(
            "publisher null total mismatch"
        )

    if publisher.CHECKPOINT_CADENCE != CADENCE:
        raise OrchestratorContractError(
            "publisher cadence mismatch"
        )

    if launcher.ENABLE_LIVE_PHASE_P_LAUNCH is not False:
        raise OrchestratorContractError(
            "frozen launcher unexpectedly enabled"
        )

    if launcher.TRACE_GATE_LINE != 3783:
        raise OrchestratorContractError(
            "trace gate mismatch"
        )


def synthetic_self_test() -> None:
    """
    Local-only integration test.

    No Kaggle command.
    No scientific runner.
    No biological data.
    """

    publisher = load_module(
        PUBLISHER_PATH,
        "exp04_orch_test_publisher",
    )

    adapter = load_module(
        ADAPTER_PATH,
        "exp04_orch_test_adapter",
    )

    launcher = load_module(
        LAUNCHER_PATH,
        "exp04_orch_test_launcher",
    )

    validate_frozen_contracts(
        publisher,
        launcher,
    )

    calls = []

    class FakeCounts:
        def __init__(
            self,
            main,
            null,
        ):
            self.main = main
            self.null = null

        def __eq__(
            self,
            other,
        ):
            return (
                self.main == other.main
                and self.null == other.null
            )

        def __repr__(self):
            return (
                f"FakeCounts(main={self.main}, "
                f"null={self.null})"
            )

    # Test state-transition semantics without invoking the real adapter
    # transport or Kaggle.
    remote0 = FakeCounts(
        0,
        0,
    )

    verified10 = FakeCounts(
        10,
        0,
    )

    class FakeAdapter:
        def publish_verified_checkpoint(
            self,
            **kwargs,
        ):
            calls.append(
                (
                    kwargs["expected_counts"].main,
                    kwargs["expected_counts"].null,
                    kwargs["reasons"],
                    kwargs["sequence"],
                    kwargs["remote_verified"].main,
                    kwargs["remote_verified"].null,
                )
            )

            return verified10

    callback, state = make_checkpoint_callback(
        publisher=object(),
        adapter=FakeAdapter(),
        source_dir=Path("/synthetic/not/read"),
        remote_verified=remote0,
        transport=object(),
    )

    callback(
        FakeCounts(
            10,
            0,
        ),
        ("cadence",),
    )

    expected = [
        (
            10,
            0,
            ("cadence",),
            1,
            0,
            0,
        )
    ]

    if calls != expected:
        raise OrchestratorContractError(
            f"callback wiring mismatch: {calls!r}"
        )

    if state["sequence"] != 1:
        raise OrchestratorContractError(
            "sequence did not advance after successful verification"
        )

    if state["remote_verified"] != verified10:
        raise OrchestratorContractError(
            "remote baseline did not advance after success"
        )

    # Failure must NOT advance either state field.
    class FailingAdapter:
        def publish_verified_checkpoint(
            self,
            **kwargs,
        ):
            raise RuntimeError(
                "synthetic verification failure"
            )

    callback2, state2 = make_checkpoint_callback(
        publisher=object(),
        adapter=FailingAdapter(),
        source_dir=Path("/synthetic/not/read"),
        remote_verified=remote0,
        transport=object(),
    )

    try:
        callback2(
            FakeCounts(
                10,
                0,
            ),
            ("cadence",),
        )

    except RuntimeError:
        pass

    else:
        raise OrchestratorContractError(
            "synthetic failure did not propagate"
        )

    if state2["sequence"] != 0:
        raise OrchestratorContractError(
            "sequence advanced after failed verification"
        )

    if state2["remote_verified"] != remote0:
        raise OrchestratorContractError(
            "remote baseline advanced after failed verification"
        )

    print(
        "PASS — frozen publisher/launcher contract identities."
    )
    print(
        "PASS — supervisor callback maps counts/reasons exactly."
    )
    print(
        "PASS — checkpoint sequence begins at 1."
    )
    print(
        "PASS — remote baseline advances only after verified publication."
    )
    print(
        "PASS — failed publication leaves sequence/baseline unchanged."
    )
    print(
        "PASS — synthetic integration made no Kaggle call."
    )
    print(
        "FINAL PASS — hard-disabled live orchestrator synthetic test."
    )


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def process_is_stopped(pid: int) -> bool:
    status = Path(
        f"/proc/{pid}/status"
    )

    if not status.is_file():
        return False

    for line in status.read_text(
        encoding="utf-8"
    ).splitlines():

        if line.startswith("State:"):
            return "\\tT" in line or " T " in line

    return False


def wait_until_stopped(
    child,
    *,
    timeout_seconds=None,
) -> None:

    deadline = (
        None
        if timeout_seconds is None
        else (
            __import__("time").monotonic()
            + float(timeout_seconds)
        )
    )

    while (
        deadline is None
        or __import__("time").monotonic()
        < deadline
    ):
        if child.poll() is not None:
            raise OrchestratorContractError(
                "scientific child exited before pre-sweep gate"
            )

        if process_is_stopped(
            child.pid
        ):
            return

        __import__("time").sleep(
            0.05
        )

    raise OrchestratorContractError(
        "scientific child did not reach pre-sweep SIGSTOP gate"
    )


def assert_exact_scientific_identity(
    *,
    scientific_repo: Path,
    runner_path: Path,
) -> None:

    p = run_cli(
        [
            "git",
            "-C",
            str(scientific_repo),
            "rev-parse",
            "HEAD",
        ]
    )

    if (
        p.returncode != 0
        or p.stdout.strip() != SCIENTIFIC_HEAD
    ):
        raise OrchestratorContractError(
            "scientific HEAD mismatch at live boundary"
        )

    p = run_cli(
        [
            "git",
            "-C",
            str(scientific_repo),
            "status",
            "--porcelain",
        ]
    )

    if p.returncode != 0:
        raise OrchestratorContractError(
            "scientific worktree status command failed at live boundary"
        )

    if p.stdout != "":
        resume_lines = [
            line
            for line in p.stdout.splitlines()
            if line
        ]

        resume_output = (
            scientific_repo
            / "experiments/04-depth-and-basis/phase_p_biological_probe/output"
        )

        resume_manifest = (
            resume_output
            / "execution_manifest.json"
        )

        exact_manifest_only_resume = (
            resume_lines
            == [
                "?? experiments/04-depth-and-basis/phase_p_biological_probe/output/"
            ]
            and resume_output.is_dir()
            and sorted(
                item.name
                for item in resume_output.iterdir()
            )
            == ["execution_manifest.json"]
            and resume_manifest.is_file()
            and sha256_file(
                resume_manifest
            )
            == "f5049a77f210b53e58ded918d8cbce9444444fd141df86f61a94dc8aa460e7ba"
        )

        if not exact_manifest_only_resume:
            raise OrchestratorContractError(
                "scientific worktree not clean at live boundary"
            )

    if sha256_file(
        runner_path
    ) != RUNNER_SHA256:
        raise OrchestratorContractError(
            "scientific runner SHA mismatch at live boundary"
        )


def assert_remote_zero_baseline(
    publisher,
):
    listing = (
        publisher.list_remote_files_text()
    )

    forbidden = (
        "execution_manifest.json",
        "main_per_perturbation.csv",
        "permutation_null_per_perturbation.csv",
        "RESULT.md",
    )

    for filename in forbidden:
        if filename in listing:
            raise OrchestratorContractError(
                "remote production checkpoint baseline "
                f"is not zero; observed {filename}"
            )

    return publisher.Counts(
        main=0,
        null=0,
    )


def start_scientific_child_at_gate(
    *,
    launcher,
    scientific_repo: Path,
    runner_path: Path,
    output_dir: Path,
):
    """
    Use the frozen trace-bootstrap itself.

    stdout/stderr are inherited intentionally.
    """

    bootstrap = launcher.build_trace_bootstrap(
        runner_path,
        launcher.TRACE_GATE_LINE,
    )

    child = subprocess.Popen(
        [
            sys.executable,
            "-c",
            bootstrap,
        ],
        cwd=scientific_repo,
    )

    try:
        wait_until_stopped(
            child,
            timeout_seconds=None,
        )

        if not output_dir.is_dir():
            raise OrchestratorContractError(
                "output directory absent at pre-sweep gate"
            )

        manifest = (
            output_dir
            / "execution_manifest.json"
        )

        if not manifest.is_file():
            raise OrchestratorContractError(
                "execution manifest absent at pre-sweep gate"
            )

        return child

    except Exception:
        if child.poll() is None:
            child.kill()
            child.wait()
        raise


def live_main() -> None:
    if not ENABLE_LIVE_PHASE_P_ORCHESTRATION:
        raise OrchestratorContractError(
            "LIVE Phase-P orchestration is hard-disabled."
        )

    publisher = load_module(
        PUBLISHER_PATH,
        "exp04_live_publisher",
    )

    adapter = load_module(
        ADAPTER_PATH,
        "exp04_live_adapter",
    )

    supervisor = load_module(
        SUPERVISOR_PATH,
        "exp04_live_supervisor",
    )

    launcher = load_module(
        LAUNCHER_PATH,
        "exp04_live_launcher",
    )

    validate_frozen_contracts(
        publisher,
        launcher,
    )

    scientific_repo = Path(
        "/kaggle/working/protein-representation-generalization"
    )

    runner_path = (
        scientific_repo
        / "experiments"
        / "04-depth-and-basis"
        / "phase_p_biological_probe"
        / "run_phase_p_biological_probe.py"
    )

    output_dir = (
        scientific_repo
        / "experiments"
        / "04-depth-and-basis"
        / "phase_p_biological_probe"
        / "output"
    )

    assert_exact_scientific_identity(
        scientific_repo=scientific_repo,
        runner_path=runner_path,
    )

    if output_dir.exists():
        resume_manifest = (
            output_dir
            / "execution_manifest.json"
        )

        exact_manifest_only_resume = (
            output_dir.is_dir()
            and sorted(
                item.name
                for item in output_dir.iterdir()
            )
            == ["execution_manifest.json"]
            and resume_manifest.is_file()
            and sha256_file(
                resume_manifest
            )
            == "f5049a77f210b53e58ded918d8cbce9444444fd141df86f61a94dc8aa460e7ba"
        )

        if not exact_manifest_only_resume:
            raise OrchestratorContractError(
                "production output is neither absent nor exact "
                "manifest-only resume state"
            )

    assert_private_dataset()

    remote_verified = (
        assert_remote_zero_baseline(
            publisher
        )
    )

    transport = make_transport(
        publisher,
        adapter,
    )

    child = start_scientific_child_at_gate(
        launcher=launcher,
        scientific_repo=scientific_repo,
        runner_path=runner_path,
        output_dir=output_dir,
    )

    initial_verified = (
        supervisor.RowCounts(
            main=0,
            null=0,
        )
    )

    callback, state = (
        make_checkpoint_callback(
            publisher=publisher,
            adapter=adapter,
            source_dir=output_dir,
            remote_verified=remote_verified,
            transport=transport,
        )
    )

    try:
        checkpoints = (
            supervisor.supervise_child(
                child=child,
                source_dir=output_dir,
                publish_callback=callback,
                main_total=MAIN_TOTAL,
                null_total=NULL_TOTAL,
                cadence=CADENCE,
                initial_verified=initial_verified,
                timeout_seconds=None,
                child_initially_stopped=True,
            )
        )

    except Exception:
        # Supervisor is contractually fail-closed at publication failure.
        # Never SIGCONT here.
        raise

    if child.returncode != 0:
        raise OrchestratorContractError(
            f"scientific child exited with returncode={child.returncode}"
        )

    if (
        state["remote_verified"].main != MAIN_TOTAL
        or state["remote_verified"].null != NULL_TOTAL
    ):
        raise OrchestratorContractError(
            "final remotely verified checkpoint census incomplete"
        )

    print(
        "FINAL PASS — protected Phase-P execution completed "
        "under private verified checkpoint supervision."
    )
    print(
        f"verified checkpoint count={len(checkpoints)}"
    )


def main():
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
        synthetic_self_test()
        return

    if args.live:
        live_main()
        return

    raise OrchestratorContractError(
        "choose --synthetic-self-test or --live"
    )


if __name__ == "__main__":
    main()
