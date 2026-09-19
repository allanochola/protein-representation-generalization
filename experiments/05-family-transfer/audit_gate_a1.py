#!/usr/bin/env python3
"""Static audit confirming the superseded combined A1 runner is disabled."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUNNER = HERE / "run_gate_a1.py"
SNAPSHOT = HERE / "a1_annotation_snapshot.json"
BANNED_IMPORT_FRAGMENTS = {
    "torch", "tensorflow", "sklearn", "transformers", "esm", "interplm",
    "sae", "probe", "numpy.random", "random", "requests", "urllib", "httpx",
}
BANNED_CALL_NAMES = {"SeedSequence", "fit", "fit_transform", "predict", "predict_proba", "score"}
BANNED_COLUMNS = ("auroc", "tpr", "fpr", "score", "threshold")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


source = RUNNER.read_text(encoding="utf-8")
tree = ast.parse(source, filename=str(RUNNER))
snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

if snapshot["execution_authorized"] is not False:
    raise RuntimeError("Superseded snapshot execution gate is not false")

authorization_values = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "EXECUTION_AUTHORIZED":
                authorization_values.append(ast.literal_eval(node.value))
if authorization_values != [False]:
    raise RuntimeError("Superseded runner gate is absent, duplicated, or not false")

for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        names = [alias.name for alias in node.names]
    elif isinstance(node, ast.ImportFrom):
        names = [node.module or ""]
    else:
        names = []
    for name in names:
        lowered = name.casefold()
        if any(fragment in lowered for fragment in BANNED_IMPORT_FRAGMENTS):
            raise RuntimeError(f"Forbidden runner import: {name}")
    if isinstance(node, ast.Call):
        called = dotted_name(node.func)
        if called.split(".")[-1] in BANNED_CALL_NAMES:
            raise RuntimeError(f"Forbidden runner call: {called}")

path_literals = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        lowered = node.value.casefold()
        if "/" in lowered or "\\" in lowered or lowered.endswith((".tsv", ".fasta", ".json")):
            path_literals.append(lowered)
for literal in path_literals:
    if "confirmatory" in literal:
        raise RuntimeError(f"Confirmatory path reachable in runner: {literal}")

if "subprocess.run([\"curl\"" in source or "subprocess.run([\"wget\"" in source:
    raise RuntimeError("Network retrieval code found in runner")

if "reject_banned_columns(columns)" not in source:
    raise RuntimeError("Output schema rejection is not called")
for token in BANNED_COLUMNS:
    if token not in source:
        raise RuntimeError(f"Missing banned-column token: {token}")

discovery = snapshot["discovery"]
for path_key, hash_key in (
    ("fasta_path", "fasta_sha256"),
    ("manifest_path", "manifest_sha256"),
    ("manifest_json_path", "manifest_json_sha256"),
):
    path = REPO / discovery[path_key]
    observed = sha256_path(path)
    if observed != discovery[hash_key]:
        raise RuntimeError(f"Frozen repository input mismatch: {path}")

if snapshot["annotation_classification"] != "fresh_annotation":
    raise RuntimeError("Annotation classification must be fresh_annotation")
if snapshot["pfam"]["release"] != "37.0":
    raise RuntimeError("Unexpected Pfam release")
if snapshot["grouping"]["definition_id"] != "exp05_a1_pfam37_clan_first_v1":
    raise RuntimeError("Unexpected family-definition identifier")
expected_routing = {
    "l_min": 0.25,
    "l_denominator": "assigned discovery positives",
    "largest_component_share_max": 0.15,
    "largest_component_share_denominator": "all 139 discovery positives",
    "unassigned_share_max": 0.10,
    "unassigned_share_denominator": "all 139 discovery positives",
}
if snapshot["routing"] != expected_routing:
    raise RuntimeError("Frozen routing thresholds or denominators changed")

print("PASS — superseded combined Gate A1 runner is statically clean and disabled")
print("Runner SHA-256:", sha256_path(RUNNER))
print("Snapshot SHA-256:", sha256_path(SNAPSHOT))
