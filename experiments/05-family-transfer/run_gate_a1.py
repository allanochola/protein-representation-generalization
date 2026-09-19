#!/usr/bin/env python3
"""Deterministic Gate-A1 census runner authorized for its one A1 execution."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


EXECUTION_AUTHORIZED = True
EXPECTED_BANNED_COLUMNS = ("auroc", "tpr", "fpr", "score", "threshold")
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SNAPSHOT_PATH = HERE / "a1_annotation_snapshot.json"
PFAM_INPUT = HERE / "a1_input"
OUTPUT = HERE / "a1_output"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def require_hash(path: Path, expected: str) -> None:
    observed = sha256_path(path)
    if observed != expected:
        raise RuntimeError(f"SHA-256 mismatch for {path}: {observed} != {expected}")


def reject_banned_columns(columns: list[str]) -> None:
    for column in columns:
        lowered = column.casefold()
        if any(token in lowered for token in EXPECTED_BANNED_COLUMNS):
            raise RuntimeError(f"Forbidden A1 output column: {column}")


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    current: str | None = None
    chunks: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current is not None:
                    records[current] = "".join(chunks)
                header = line[1:]
                parts = header.split("|", 1)
                if len(parts) != 2 or parts[0] not in {"positive", "negative"}:
                    raise RuntimeError(f"Unexpected discovery FASTA header: {header}")
                current = parts[1]
                if current in records:
                    raise RuntimeError(f"Duplicate discovery FASTA identifier: {current}")
                chunks = []
            elif current is None:
                raise RuntimeError("Sequence before first FASTA header")
            else:
                chunks.append(line)
    if current is not None:
        records[current] = "".join(chunks)
    return records


def validate_discovery(snapshot: dict[str, object]) -> tuple[Path, list[str]]:
    spec = snapshot["discovery"]
    assert isinstance(spec, dict)
    fasta = REPO / str(spec["fasta_path"])
    manifest = REPO / str(spec["manifest_path"])
    manifest_json = REPO / str(spec["manifest_json_path"])
    require_hash(fasta, str(spec["fasta_sha256"]))
    require_hash(manifest, str(spec["manifest_sha256"]))
    require_hash(manifest_json, str(spec["manifest_json_sha256"]))

    sequences = read_fasta(fasta)
    positives: list[str] = []
    counts = defaultdict(int)
    with manifest.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"class_name", "identifier", "sequence_sha256", "uniprot_release"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise RuntimeError("Discovery manifest schema mismatch")
        for row in reader:
            label = row["class_name"]
            identifier = row["identifier"]
            if identifier not in sequences:
                raise RuntimeError(f"Manifest identifier absent from FASTA: {identifier}")
            sequence_hash = hashlib.sha256(sequences[identifier].encode("ascii")).hexdigest()
            if sequence_hash != row["sequence_sha256"]:
                raise RuntimeError(f"Per-sequence hash mismatch: {identifier}")
            if row["uniprot_release"] != spec["uniprot_release"]:
                raise RuntimeError(f"UniProt release mismatch: {identifier}")
            counts[label] += 1
            if label == "positive":
                positives.append(identifier)
    if sum(counts.values()) != spec["expected_rows"]:
        raise RuntimeError("Discovery row-count invariant failed")
    if counts["positive"] != spec["expected_positive_rows"]:
        raise RuntimeError("Discovery positive-count invariant failed")
    if counts["negative"] != spec["expected_negative_rows"]:
        raise RuntimeError("Discovery negative-count invariant failed")
    if len(sequences) != spec["expected_rows"]:
        raise RuntimeError("Discovery FASTA-count invariant failed")
    return fasta, sorted(positives)


def read_clan_map(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        for raw in handle:
            fields = raw.rstrip("\n").split("\t")
            if len(fields) < 2:
                raise RuntimeError("Malformed Pfam clan row")
            family, clan = fields[0], fields[1]
            if family in mapping and mapping[family] != clan:
                raise RuntimeError(f"Conflicting clan mapping: {family}")
            mapping[family] = clan
    return mapping


def parse_domtbl(path: Path) -> dict[str, set[str]]:
    hits: dict[str, set[str]] = defaultdict(set)
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in handle:
            if raw.startswith("#") or not raw.strip():
                continue
            fields = raw.split(maxsplit=22)
            if len(fields) < 22:
                raise RuntimeError("Malformed HMMER domain-table row")
            family = fields[1].split(".", 1)[0]
            query = fields[3]
            query_parts = query.split("|", 1)
            if len(query_parts) != 2 or query_parts[0] not in {"positive", "negative"}:
                raise RuntimeError(f"Unexpected discovery query identifier: {query}")
            protein = query_parts[1]
            if not family.startswith("PF"):
                raise RuntimeError(f"Unexpected Pfam accession: {fields[1]}")
            hits[protein].add(family)
    return hits


class DisjointSet:
    def __init__(self, members: list[str]) -> None:
        self.parent = {member: member for member in members}

    def find(self, item: str) -> str:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: str, right: str) -> None:
        a, b = self.find(left), self.find(right)
        if a != b:
            first, second = sorted((a, b))
            self.parent[second] = first


def build_components(
    positives: list[str], family_hits: dict[str, set[str]], clan_map: dict[str, str]
) -> tuple[dict[str, list[str]], dict[str, str]]:
    identifiers: dict[str, list[str]] = {}
    assigned: list[str] = []
    for protein in positives:
        resolved = sorted({clan_map.get(family, family) for family in family_hits.get(protein, set())})
        identifiers[protein] = resolved
        if resolved:
            assigned.append(protein)

    sets = DisjointSet(assigned)
    by_identifier: dict[str, list[str]] = defaultdict(list)
    for protein in assigned:
        for identifier in identifiers[protein]:
            by_identifier[identifier].append(protein)
    for members in by_identifier.values():
        anchor = min(members)
        for member in members:
            sets.union(anchor, member)

    grouped: dict[str, list[str]] = defaultdict(list)
    for protein in assigned:
        grouped[sets.find(protein)].append(protein)
    components: dict[str, list[str]] = {}
    membership: dict[str, str] = {}
    for members in sorted((sorted(value) for value in grouped.values())):
        component = "COMP_" + hashlib.sha256("\n".join(members).encode("utf-8")).hexdigest()[:16]
        components[component] = members
        for protein in members:
            membership[protein] = component
    return components, membership


def write_tsv(path: Path, columns: list[str], rows: list[list[object]]) -> None:
    reject_banned_columns(columns)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def route_summary(
    positives: list[str], identifiers: dict[str, list[str]], components: dict[str, list[str]],
    routing: dict[str, object]
) -> dict[str, object]:
    total = len(positives)
    assigned = sum(bool(identifiers[protein]) for protein in positives)
    unassigned = total - assigned
    sizes = sorted((len(members) for members in components.values()), reverse=True)
    supported = sum(size for size in sizes if size >= 2)
    largest = sizes[0] if sizes else 0
    singleton = sum(size for size in sizes if size == 1)
    assigned_fraction = assigned / total
    unassigned_share = unassigned / total
    l_value = supported / assigned if assigned else None
    largest_share = largest / total
    singleton_fraction = singleton / assigned if assigned else None
    if unassigned_share > routing["unassigned_share_max"]:
        route = "INCONCLUSIVE_UNASSIGNED"
    elif assigned == 0 or largest_share is None or l_value is None:
        route = "INCONCLUSIVE_NO_ASSIGNED"
    elif largest_share > routing["largest_component_share_max"]:
        route = "AMENDMENT_REQUIRED_CONCENTRATION"
    elif l_value >= routing["l_min"]:
        route = "TWO_STAGE_ELIGIBLE"
    else:
        route = "SKIP_STAGE1_NEAR_VACUOUS"
    return {
        "total_positive_count": total,
        "assigned_positive_count": assigned,
        "assigned_positive_fraction": assigned_fraction,
        "unassigned_positive_count": unassigned,
        "unassigned_positive_share": unassigned_share,
        "component_count": len(sizes),
        "largest_component_count": largest,
        "largest_component_share_all_positives": largest_share,
        "assigned_singleton_count": singleton,
        "assigned_singleton_fraction": singleton_fraction,
        "l_value_among_assigned": l_value,
        "route": route,
        "scope": "L and Stage 1 apply only to annotation-assigned discovery positives"
    }


def verify_hmmer(snapshot: dict[str, object]) -> None:
    result = subprocess.run(["hmmscan", "-h"], text=True, capture_output=True, check=True)
    expected = str(snapshot["hmmer"]["required_version_fragment"])
    if expected not in result.stdout:
        raise RuntimeError(f"HMMER version mismatch; required {expected}")


def execute() -> None:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if not EXECUTION_AUTHORIZED or not snapshot.get("execution_authorized", False):
        raise RuntimeError("Gate A1 execution is not authorized")

    fasta, positives = validate_discovery(snapshot)
    for name, spec in snapshot["pfam"]["artifacts"].items():
        if name in {"Pfam-A.hmm.gz", "Pfam-A.clans.tsv.gz", "Pfam-A.hmm.dat.gz"}:
            require_hash(PFAM_INPUT / name, spec["sha256"])
    verify_hmmer(snapshot)

    with tempfile.TemporaryDirectory(prefix="exp05_a1_") as temp_name:
        work = Path(temp_name)
        hmm = work / "Pfam-A.hmm"
        with gzip.open(PFAM_INPUT / "Pfam-A.hmm.gz", "rb") as source, hmm.open("wb") as target:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                target.write(block)
        subprocess.run(["hmmpress", str(hmm)], check=True, cwd=work)
        domtbl = work / "discovery.domtblout"
        command = ["hmmscan", "--cut_ga", "--noali", "--domtblout", str(domtbl), str(hmm), str(fasta)]
        subprocess.run(command, check=True, cwd=work, stdout=subprocess.DEVNULL)
        hits = parse_domtbl(domtbl)

    # The scan covers all frozen discovery records, but A1 reads positives only.
    clan_map = read_clan_map(PFAM_INPUT / "Pfam-A.clans.tsv.gz")
    identifiers = {
        protein: sorted({clan_map.get(family, family) for family in hits.get(protein, set())})
        for protein in positives
    }
    components, membership = build_components(positives, hits, clan_map)
    summary = route_summary(positives, identifiers, components, snapshot["routing"])

    OUTPUT.mkdir(parents=False, exist_ok=False)
    assignment_rows = [
        [protein, ";".join(identifiers[protein]) or "UNASSIGNED", membership.get(protein, "UNASSIGNED")]
        for protein in positives
    ]
    write_tsv(OUTPUT / "assignments.tsv", ["protein_id", "group_identifiers", "component_id"], assignment_rows)
    component_rows = [[component, len(members), ";".join(members)] for component, members in sorted(components.items())]
    write_tsv(OUTPUT / "components.tsv", ["component_id", "member_count", "member_ids"], component_rows)
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    definition_hash = hashlib.sha256(canonical_json(snapshot["grouping"]).encode("utf-8")).hexdigest()
    source_hash = sha256_path(Path(__file__))
    outputs = {path.name: sha256_path(path) for path in sorted(OUTPUT.iterdir())}
    bundle_hash = hashlib.sha256(
        canonical_json({"definition_sha256": definition_hash, "output_sha256": outputs}).encode("utf-8")
    ).hexdigest()
    provenance = {
        "annotation_classification": snapshot["annotation_classification"],
        "confirmatory_accessed": False,
        "definition_id": snapshot["grouping"]["definition_id"],
        "definition_sha256": definition_hash,
        "definition_and_outputs_sha256": bundle_hash,
        "runner_sha256": source_hash,
        "snapshot_sha256": sha256_path(SNAPSHOT_PATH),
        "discovery_fasta_sha256": snapshot["discovery"]["fasta_sha256"],
        "discovery_manifest_sha256": snapshot["discovery"]["manifest_sha256"],
        "pfam_release": snapshot["pfam"]["release"],
        "hmmer_version": snapshot["hmmer"]["version"],
        "scan_arguments": snapshot["scan"]["arguments"],
        "output_sha256": outputs
    }
    (OUTPUT / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        execute()
    except Exception as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        raise SystemExit(2)
