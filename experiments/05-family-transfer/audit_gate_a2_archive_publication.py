"""Synthetic A2-SS archive-publication regression test; no scanning."""
import ast
import tempfile
from pathlib import Path

def check():
    exp = Path(__file__).resolve().parent
    runner = exp / "run_gate_a2_scan.py"
    tree = ast.parse(runner.read_text(encoding="utf-8"))

    gates = [
        ast.literal_eval(n.value)
        for n in ast.walk(tree)
        if isinstance(n, ast.Assign)
        and len(n.targets) == 1
        and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id == "A2_SCAN_AUTHORIZED"
    ]
    if gates != [False]:
        raise RuntimeError("This preauthorization test requires a disabled gate")

    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name)
        and n.func.value.id == "tempfile"
        and n.func.attr == "TemporaryDirectory"
        and any(
            k.arg == "prefix"
            and isinstance(k.value, ast.Constant)
            and k.value.value == "exp05_a2ss_"
            for k in n.keywords
        )
    ]
    if len(calls) != 1:
        raise RuntimeError("Staging call is not unique")
    dirs = [k.value for k in calls[0].keywords if k.arg == "dir"]
    expected = ast.parse("OUTPUT.parent", mode="eval").body
    if len(dirs) != 1 or ast.dump(dirs[0]) != ast.dump(expected):
        raise RuntimeError("Staging does not use OUTPUT.parent")

    # Synthetic bytes only; both directories are on the repo filesystem.
    with tempfile.TemporaryDirectory(
        prefix="a2ss_publication_test_", dir=exp
    ) as root:
        destination = Path(root) / "archive"
        with tempfile.TemporaryDirectory(
            prefix="stage_", dir=destination.parent
        ) as temporary:
            stage = Path(temporary) / "archive"
            stage.mkdir()
            (stage / "synthetic.txt").write_bytes(b"synthetic-only\n")
            if stage.stat().st_dev != destination.parent.stat().st_dev:
                raise RuntimeError("Staging crossed filesystems")
            stage.rename(destination)
        if (destination / "synthetic.txt").read_bytes() != b"synthetic-only\n":
            raise RuntimeError("Published synthetic archive differs")

    print("PASS — same-filesystem publication regression")
    print("A2-SS authorized: NO")
    print("Scanning performed: NO")

if __name__ == "__main__":
    check()
