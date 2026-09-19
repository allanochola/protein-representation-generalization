#!/usr/bin/env python3
"""A1-M-C: authorized amended census over committed Pfam and MMseqs2 archives; not yet executed."""
import csv
import gzip
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

AMENDED_CENSUS_AUTHORIZED = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PFAM_ARCHIVE = HERE / "a1_scan_archive"
MMSEQS_ARCHIVE = HERE / "a1_mmseqs_scan_archive"
OUTPUT = HERE / "a1_amended_census_output"

BANNED_COLUMNS = ("auroc", "tpr", "fpr", "score", "threshold")
ROUTES = (
    "AMENDMENT_REQUIRED_CONCENTRATION",
    "TWO_STAGE_ELIGIBLE",
    "SKIP_STAGE1_NEAR_VACUOUS",
)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def check_columns(columns):
    for column in columns:
        if any(
            token in column.casefold()
            for token in BANNED_COLUMNS
        ):
            raise RuntimeError(
                f"Forbidden amended-census column: {column}"
            )


def tracked_paths():
    return set(
        subprocess.check_output(
            ["git", "ls-files"],
            cwd=REPO,
            text=True,
        ).splitlines()
    )


def relative(path):
    return str(Path(path).relative_to(REPO))


def verify_archive(archive, provenance_name, tracked):
    provenance = archive / provenance_name

    if relative(provenance) not in tracked:
        raise RuntimeError(
            f"Archive provenance is not committed: {provenance}"
        )

    metadata = json.loads(
        provenance.read_text(encoding="utf-8")
    )

    if metadata.get("confirmatory_accessed") is not False:
        raise RuntimeError(
            f"Archive does not certify confirmatory_accessed=false: {archive}"
        )

    file_hashes = metadata.get("file_sha256")

    if not isinstance(file_hashes, dict) or not file_hashes:
        raise RuntimeError(
            f"Archive has no member-hash contract: {archive}"
        )

    for name, expected in file_hashes.items():
        path = archive / name

        if relative(path) not in tracked:
            raise RuntimeError(
                f"Archive member is not committed: {path}"
            )

        observed = digest(path)
        if observed != expected:
            raise RuntimeError(
                f"Archive member hash mismatch: {path}: {observed}"
            )

    return metadata, provenance


class DSU:
    def __init__(self, members):
        self.parent = {
            member: member
            for member in members
        }

    def find(self, member):
        while self.parent[member] != member:
            self.parent[member] = self.parent[
                self.parent[member]
            ]
            member = self.parent[member]
        return member

    def union(self, left, right):
        left = self.find(left)
        right = self.find(right)

        if left != right:
            self.parent[max(left, right)] = min(left, right)


def amended_census(positives, pfam_identifiers, mmseqs_clusters):
    positives = sorted(positives)

    if len(positives) != 139 or len(set(positives)) != 139:
        raise RuntimeError(
            "Amended census requires exactly 139 unique positives"
        )

    positive_set = set(positives)

    if set(pfam_identifiers) != positive_set:
        raise RuntimeError(
            "Pfam identifier mapping does not cover all positives"
        )

    if set(mmseqs_clusters) != positive_set:
        raise RuntimeError(
            "MMseqs2 partition is not total over all positives"
        )

    if any(
        not cluster_id
        for cluster_id in mmseqs_clusters.values()
    ):
        raise RuntimeError("Empty MMseqs2 cluster identifier")

    if any(
        not identifier
        for identifiers in pfam_identifiers.values()
        for identifier in identifiers
    ):
        raise RuntimeError("Empty Pfam group identifier")

    dsu = DSU(positives)
    by_edge = defaultdict(list)

    for protein in positives:
        for identifier in pfam_identifiers[protein]:
            by_edge[f"PFAM:{identifier}"].append(protein)

        by_edge[
            f"MMSEQS:{mmseqs_clusters[protein]}"
        ].append(protein)

    for members in by_edge.values():
        anchor = members[0]
        for member in members[1:]:
            dsu.union(anchor, member)

    groups = defaultdict(list)

    for protein in positives:
        groups[dsu.find(protein)].append(protein)

    components = sorted(
        (sorted(members) for members in groups.values()),
        key=lambda members: (-len(members), members),
    )

    flattened = [
        member
        for component in components
        for member in component
    ]

    if (
        len(flattened) != 139
        or len(set(flattened)) != 139
        or set(flattened) != positive_set
    ):
        raise RuntimeError(
            "Amended components do not partition all 139 positives"
        )

    unassigned_count = sum(
        protein not in mmseqs_clusters
        for protein in positives
    )

    if unassigned_count != 0:
        raise RuntimeError(
            "Nonzero unassigned count in total sequence partition"
        )

    sizes = [len(component) for component in components]
    supported_count = sum(
        size
        for size in sizes
        if size >= 2
    )
    singleton_count = sum(
        size == 1
        for size in sizes
    )
    largest_count = max(sizes)

    total = len(positives)
    l_value = supported_count / total
    largest_share = largest_count / total

    if largest_share > 0.15:
        route = "AMENDMENT_REQUIRED_CONCENTRATION"
    elif l_value >= 0.25:
        route = "TWO_STAGE_ELIGIBLE"
    else:
        route = "SKIP_STAGE1_NEAR_VACUOUS"

    if route not in ROUTES:
        raise RuntimeError(f"Unknown amended route: {route}")

    summary = {
        "total_positive_count": total,
        "assigned_positive_count": total,
        "assigned_positive_fraction": 1.0,
        "unassigned_positive_count": 0,
        "unassigned_positive_share": 0.0,
        "component_count": len(components),
        "singleton_positive_count": singleton_count,
        "singleton_positive_fraction": singleton_count / total,
        "supported_positive_count": supported_count,
        "l_value_all_positives": l_value,
        "largest_component_count": largest_count,
        "largest_component_share_all_positives": largest_share,
        "route": route,
    }

    return components, summary


def load_inputs():
    tracked = tracked_paths()

    pfam_meta, pfam_provenance = verify_archive(
        PFAM_ARCHIVE,
        "scan_provenance.json",
        tracked,
    )
    mmseqs_meta, mmseqs_provenance = verify_archive(
        MMSEQS_ARCHIVE,
        "scan_provenance.json",
        tracked,
    )

    positives = []

    with (
        PFAM_ARCHIVE / "discovery_sequence_manifest.tsv"
    ).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["class_name"] == "positive":
                positives.append(row["identifier"])

    if len(positives) != 139 or len(set(positives)) != 139:
        raise RuntimeError("Archived positive-manifest gate failed")

    clans = {}

    with gzip.open(
        PFAM_ARCHIVE / "Pfam-A.clans.tsv.gz",
        "rt",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            fields = line.rstrip().split("\t")
            if len(fields) > 1 and fields[1].strip():
                clans[fields[0]] = fields[1].strip()

    family_hits = defaultdict(set)

    with (
        PFAM_ARCHIVE / "accepted_family_hits.tsv"
    ).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["class_name"] == "positive":
                family_hits[row["protein_id"]].add(
                    row["pfam_accession"]
                )

    positive_set = set(positives)

    if set(family_hits) - positive_set:
        raise RuntimeError(
            "Positive Pfam hit absent from archived manifest"
        )

    pfam_identifiers = {
        protein: sorted({
            clans.get(family, family)
            for family in family_hits.get(protein, set())
        })
        for protein in positives
    }

    if any(
        not identifier
        for identifiers in pfam_identifiers.values()
        for identifier in identifiers
    ):
        raise RuntimeError("Empty clan/family identifier")

    partition_path = MMSEQS_ARCHIVE / "canonical_partition.tsv"
    mmseqs_clusters = {}

    with partition_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle, delimiter="\t")

        if reader.fieldnames != [
            "protein_id",
            "cluster_sha256",
        ]:
            raise RuntimeError(
                "Unexpected MMseqs2 partition schema"
            )

        for row in reader:
            protein = row["protein_id"]
            cluster_id = row["cluster_sha256"]

            if protein in mmseqs_clusters:
                raise RuntimeError(
                    f"Duplicate MMseqs2 partition member: {protein}"
                )

            mmseqs_clusters[protein] = cluster_id

    if set(mmseqs_clusters) != positive_set:
        raise RuntimeError(
            "Committed MMseqs2 archive is not a total partition"
        )

    return (
        positives,
        pfam_identifiers,
        mmseqs_clusters,
        pfam_meta,
        mmseqs_meta,
        pfam_provenance,
        mmseqs_provenance,
    )


def main():
    if not AMENDED_CENSUS_AUTHORIZED:
        raise RuntimeError("A1-M-C is not authorized")

    if OUTPUT.exists():
        raise RuntimeError(
            "A1-M-C output already exists"
        )

    (
        positives,
        pfam_identifiers,
        mmseqs_clusters,
        pfam_meta,
        mmseqs_meta,
        pfam_provenance,
        mmseqs_provenance,
    ) = load_inputs()

    components, summary = amended_census(
        positives,
        pfam_identifiers,
        mmseqs_clusters,
    )

    OUTPUT.mkdir()

    assignment_columns = (
        "protein_id",
        "pfam_group_identifiers",
        "mmseqs_cluster_sha256",
    )
    check_columns(assignment_columns)

    with (OUTPUT / "assignments.tsv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writerow(assignment_columns)

        for protein in sorted(positives):
            writer.writerow((
                protein,
                ";".join(pfam_identifiers[protein]),
                mmseqs_clusters[protein],
            ))

    component_columns = (
        "component_id",
        "member_count",
        "member_ids",
    )
    check_columns(component_columns)

    with (OUTPUT / "components.tsv").open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writerow(component_columns)

        for members in components:
            component_id = "COMP_" + hashlib.sha256(
                "\n".join(members).encode("utf-8")
            ).hexdigest()[:16]

            writer.writerow((
                component_id,
                len(members),
                ";".join(members),
            ))

    summary_columns = tuple(summary)
    check_columns(summary_columns)

    (OUTPUT / "summary.json").write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    output_hashes = {
        name: digest(OUTPUT / name)
        for name in (
            "assignments.tsv",
            "components.tsv",
            "summary.json",
        )
    }

    provenance = {
        "confirmatory_accessed": False,
        "pfam_scan_provenance_sha256": digest(
            pfam_provenance
        ),
        "mmseqs_scan_provenance_sha256": digest(
            mmseqs_provenance
        ),
        "archives_verified_committed": True,
        "grouping_rule": (
            "full transitive closure over the union of committed "
            "Pfam clan-first/family-fallback edges and committed "
            "MMseqs2 cluster edges"
        ),
        "total_partition_asserted": True,
        "l_denominator": "all 139 discovery positives",
        "largest_component_share_denominator": (
            "all 139 discovery positives"
        ),
        "routing_precedence": [
            "largest_component_share > 0.15",
            "L >= 0.25",
            "otherwise",
        ],
        "output_sha256": output_hashes,
    }

    (OUTPUT / "census_provenance.json").write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
