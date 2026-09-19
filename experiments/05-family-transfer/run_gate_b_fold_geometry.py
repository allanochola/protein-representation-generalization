"""Gate B grouped-fold geometry disabled pending failure-path repair."""

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import sklearn
from sklearn.model_selection import StratifiedGroupKFold

FOLD_GEOMETRY_AUTHORIZED = False

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / "experiments/05-family-transfer"
ARCHIVE = EXP / "gate_b_discovery_grouping_archive"
MANIFEST = EXP / "a1_scan_archive/discovery_sequence_manifest.tsv"
OUTPUT = EXP / "gate_b_fold_geometry"

EXPECTED_SKLEARN = '1.6.1'
N_SPLITS = 5
CV_SEED = 20260829
BANNED = ("auroc", "tpr", "fpr", "score", "threshold")

ARCHIVE_HASHES = {'canonical_cluster_rows.tsv': 'e7327640018b749287416375190291226bc8d84085f5997f8e344f312f9bedf5', 'canonical_discovery_278.fasta': 'e54ddf390c9569857663c029ec4679a18f4a0384d391c9183f550be3e0ebe94d', 'canonical_partition.tsv': '4b3ce36350e289d1c0baa234ce3b2b234de02277ce00fa32acc0958412b54dfe', 'collision_edge_provenance.tsv': '9a978b7b640791528750590577fbb41ebc024aaba46215d34fd72ab42d931f72', 'collision_report.tsv': '2120c46494c6ae73b6c1d815ddeec5cc90a7a17e3b3409988347c83dfeb99f66', 'components.tsv': '967d45ebffff40053ba2b2791777f4f94982b09997b23d20c39b27d4aa412cef', 'edge_provenance.tsv': 'b52f7ebfdb4ee2c9f01d18f97350298f71f99c53ede78a58866685e187974748', 'grouping_provenance.json': 'c014ca1ffcf133b8b009a64f412237e15db6f8fb5cac362f762fb5d0b4c2b573', 'pfam_edges.tsv': '06152d0991d88a69f9c7bc4c5775eaf34f50573eed6fe00ad625bf8367ec8473', 'run_1.stderr': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'run_1.stdout': 'b7c9c6033a7ddabbc5cc69c3e6e53e8c264a09c5fa928981a3ea1ecbe6c99f02', 'run_1_raw_cluster.tsv': '863e4df696fac8b56967789dcf9b44ea7eca4156a1c686ef2bc950b89c292ca7', 'run_2.stderr': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'run_2.stdout': 'c17c013a76d1d737e7bd7d4a97ac489ad0dedacb6d3e9664b5602a34c872a0f6', 'run_2_raw_cluster.tsv': 'f67cd437f1f9f4cbda5120ef452e21d7c373dbfa5163070dcc3286a85921e2e2', 'summary.json': 'ef6b825bc722107895a467cdaf6d542abe751a76db8d81023b53a5db4c22794c'}
MANIFEST_SHA = '7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09'


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def tracked(relative):
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(relative)],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def check_columns(columns):
    for column in columns:
        lowered = column.lower()
        if any(token in lowered for token in BANNED):
            raise RuntimeError(f"Forbidden output column: {column}")


def main():
    if not FOLD_GEOMETRY_AUTHORIZED:
        raise SystemExit("STOP: Gate B fold geometry is not authorized")

    if sklearn.__version__ != EXPECTED_SKLEARN:
        raise RuntimeError("scikit-learn version mismatch")

    if OUTPUT.exists():
        raise RuntimeError("Fold-geometry output already exists")

    for name, expected in ARCHIVE_HASHES.items():
        path = ARCHIVE / name
        relative = path.relative_to(REPO)
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"Archive identity mismatch: {name}")
        if not tracked(relative):
            raise RuntimeError(f"Archive member is not tracked: {name}")

    if digest(MANIFEST) != MANIFEST_SHA:
        raise RuntimeError("Manifest identity mismatch")

    labels = {}
    with MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not {"class_name", "identifier"} <= set(reader.fieldnames or []):
            raise RuntimeError("Manifest schema mismatch")
        for row in reader:
            identifier = row["identifier"]
            label = row["class_name"]
            if identifier in labels:
                raise RuntimeError("Duplicate manifest identifier")
            if label not in {"positive", "negative"}:
                raise RuntimeError("Unexpected class label")
            labels[identifier] = label

    if len(labels) != 278 or Counter(labels.values()) != Counter(
        {"positive": 139, "negative": 139}
    ):
        raise RuntimeError("Frozen discovery membership mismatch")

    protein_to_component = {}
    component_members = {}

    with (ARCHIVE / "components.tsv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected = {
            "component_id", "class_name", "member_count", "member_ids"
        }
        if set(reader.fieldnames or []) != expected:
            raise RuntimeError("Component schema mismatch")

        for row in reader:
            component = row["component_id"]
            members = tuple(
                item for item in row["member_ids"].split(";") if item
            )
            if int(row["member_count"]) != len(members):
                raise RuntimeError("Component member-count mismatch")
            if component in component_members:
                raise RuntimeError("Duplicate component identifier")

            component_members[component] = members
            for member in members:
                if member in protein_to_component:
                    raise RuntimeError("Protein appears in multiple components")
                protein_to_component[member] = component

    if len(component_members) != 117:
        raise RuntimeError("Expected 117 discovery-wide components")
    if set(protein_to_component) != set(labels):
        raise RuntimeError("Components do not partition the 278 proteins")

    identifiers = np.array(sorted(labels), dtype=object)
    y = np.array(
        [1 if labels[item] == "positive" else 0 for item in identifiers],
        dtype=np.int8,
    )
    groups = np.array(
        [protein_to_component[item] for item in identifiers],
        dtype=object,
    )
    dummy = np.zeros((len(identifiers), 1), dtype=np.int8)

    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=CV_SEED,
    )

    validation_fold = {}
    summary_rows = []
    feasibility_violations = []

    for fold, (train_index, validation_index) in enumerate(
        splitter.split(dummy, y, groups),
        start=1,
    ):
        train_groups = set(groups[train_index])
        validation_groups = set(groups[validation_index])

        if train_groups & validation_groups:
            raise RuntimeError("Component leaked across train/validation")
        if set(y[train_index]) != {0, 1}:
            feasibility_violations.append({"fold": fold, "partition": "training", "reason": "MISSING_LABEL"})
        if set(y[validation_index]) != {0, 1}:
            feasibility_violations.append({"fold": fold, "partition": "validation", "reason": "MISSING_LABEL"})

        for index in validation_index:
            identifier = str(identifiers[index])
            if identifier in validation_fold:
                raise RuntimeError("Duplicate validation assignment")
            validation_fold[identifier] = fold

        summary_rows.append((
            fold,
            len(train_index),
            int(y[train_index].sum()),
            int(len(train_index) - y[train_index].sum()),
            len(train_groups),
            len(validation_index),
            int(y[validation_index].sum()),
            int(len(validation_index) - y[validation_index].sum()),
            len(validation_groups),
        ))

    if set(validation_fold) != set(labels):
        raise RuntimeError("Validation folds do not cover all proteins")

    for component, members in component_members.items():
        folds = {validation_fold[member] for member in members}
        if len(folds) != 1:
            raise RuntimeError(
                f"Component split across validation folds: {component}"
            )

    OUTPUT.mkdir()

    assignment_columns = (
        "protein_id", "class_name", "component_id", "validation_fold"
    )
    summary_columns = (
        "fold",
        "training_records",
        "training_positives",
        "training_negatives",
        "training_components",
        "validation_records",
        "validation_positives",
        "validation_negatives",
        "validation_components",
    )
    check_columns(assignment_columns)
    check_columns(summary_columns)

    assignments = OUTPUT / "fold_assignments.tsv"
    with assignments.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(
            handle, delimiter="\t", lineterminator="\n"
        )
        writer.writerow(assignment_columns)
        for identifier in sorted(labels):
            writer.writerow((
                identifier,
                labels[identifier],
                protein_to_component[identifier],
                validation_fold[identifier],
            ))

    fold_summary = OUTPUT / "fold_summary.tsv"
    with fold_summary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(
            handle, delimiter="\t", lineterminator="\n"
        )
        writer.writerow(summary_columns)
        writer.writerows(summary_rows)

    component_classes = Counter()
    for members in component_members.values():
        kinds = {labels[member] for member in members}
        if kinds == {"positive"}:
            component_classes["positive_only"] += 1
        elif kinds == {"negative"}:
            component_classes["negative_only"] += 1
        else:
            component_classes["mixed"] += 1

    geometry_ready = not feasibility_violations
    summary = {
        "status": "FOLD_GEOMETRY_READY" if geometry_ready else "FOLD_GEOMETRY_INFEASIBLE",
        "total_records": len(labels),
        "positive_records": sum(v == "positive" for v in labels.values()),
        "negative_records": sum(v == "negative" for v in labels.values()),
        "component_count": len(component_members),
        "positive_only_component_count":
            component_classes["positive_only"],
        "negative_only_component_count":
            component_classes["negative_only"],
        "mixed_component_count": component_classes["mixed"],
        "fold_count": N_SPLITS,
        "seed": CV_SEED,
        "all_components_intact": True,
        "all_folds_have_both_labels": geometry_ready,
        "feasibility_violation_count": len(feasibility_violations),
        "feasibility_violations": feasibility_violations,
    }

    summary_path = OUTPUT / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    output_hashes = {
        "fold_assignments.tsv": digest(assignments),
        "fold_summary.tsv": digest(fold_summary),
        "summary.json": digest(summary_path),
    }

    provenance = {
        "confirmatory_accessed": False,
        "grouping_archive_sha256": ARCHIVE_HASHES,
        "manifest_sha256": MANIFEST_SHA,
        "splitter": "StratifiedGroupKFold",
        "n_splits": N_SPLITS,
        "shuffle": True,
        "random_state": CV_SEED,
        "scikit_learn_version": sklearn.__version__,
        "feature_input": "constant dummy column; no biological features",
        "mixed_components_retained_intact": True,
        "feasibility_status": summary["status"],
        "output_sha256": output_hashes,
    }

    (OUTPUT / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
