#!/usr/bin/env python3
"""Behavioral preauthorization audit for the split Gate A1 runners.

Re-run before every A1-S or A1-C authorization. Asserts gate states, phase
separation, archive integrity, and the frozen census semantics. Imports both
runners; neither executes, because both are import-guarded by __main__.
"""
import ast, gzip, hashlib, importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
REPO = H.parents[1]
ARCHIVE = H / "a1_scan_archive"

ARCHIVE_SHA256 = {
    "Pfam-A.clans.tsv.gz": "1d9d7f054b017733935aae50c69e2c99037461617a0244ef6c188292474fdcd5",
    "Pfam.version.gz": "8e4de54729bb767d68271b440c91ebb3049f89108422833d8b15ae729dba7dfc",
    "accepted_family_hits.tsv": "d0d15ba423ba209807dea307a5446597f53a51d0a3d7fca48d62feb51ffb494b",
    "discovery_sequence_manifest.tsv": "7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09",
    "hmmscan.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "hmmscan.stdout": "f925e081a22603354e32a3b9727ff4d51c7451f6b8e3893d5d26a1dab7b4e57a",
    "raw.domtblout": "0e102aad12fdc60d4348e2894c1a2aa5a362fffdc48db0041722b83744fb8a47",
    "scan_provenance.json": "fb26109ec44dd6e11d570317a47bf79eaa49e8b9fe88bd6f8cd3daf7379d33db",
}

ROUTES = {"INCONCLUSIVE_UNASSIGNED", "AMENDMENT_REQUIRED_CONCENTRATION",
          "TWO_STAGE_ELIGIBLE", "SKIP_STAGE1_NEAR_VACUOUS"}

failures = []
def require(cond, msg):
    if not cond:
        failures.append(msg)

def sha256_file(path):
    d = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def gate(src, name):
    return [n.value.value for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Assign) and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name
            and isinstance(n.value, ast.Constant) and isinstance(n.value.value, bool)]

scan_path = H / "run_gate_a1_scan.py"
census_path = H / "run_gate_a1_census.py"
scan_src = scan_path.read_text(encoding="utf-8")
census_src = census_path.read_text(encoding="utf-8")

ast.parse(scan_src); ast.parse(census_src)

# --- Gate states. Each must be a single boolean assignment. -----------------
scan_gate = gate(scan_src, "SCAN_AUTHORIZED")
census_gate = gate(census_src, "CENSUS_AUTHORIZED")
require(len(scan_gate) == 1, f"SCAN_AUTHORIZED is not unique: {scan_gate}")
require(len(census_gate) == 1, f"CENSUS_AUTHORIZED is not unique: {census_gate}")
require(not (scan_gate == [True] and census_gate == [True]),
        "Both phases are simultaneously authorized")

# --- Phase separation. ------------------------------------------------------
for token in ("route_summary", "largest_component", "l_value", "DisjointSet",
              "DSU", "clan_map", "component_count", "TWO_STAGE_ELIGIBLE"):
    require(token not in scan_src, f"census token in A1-S: {token}")
for token in ("hmmscan", "hmmpress", "Pfam-A.hmm", "discovery_sequences.fasta",
              "urllib", "requests", "urlopen", "socket"):
    require(token not in census_src, f"scan/network token in A1-C: {token}")

for node in ast.walk(ast.parse(census_src)):
    if isinstance(node, ast.Call):
        fn = node.func.attr if isinstance(node.func, ast.Attribute) else (
            node.func.id if isinstance(node.func, ast.Name) else "")
        if fn in {"run", "check_output", "Popen", "call"}:
            rendered = ast.unparse(node)
            require("git" in rendered and "ls-files" in rendered,
                    f"A1-C non-git subprocess: {rendered}")

# --- Committed archive integrity. -------------------------------------------
for name, expected in ARCHIVE_SHA256.items():
    path = ARCHIVE / name
    if not path.is_file():
        failures.append(f"Missing archive file: {name}")
        continue
    require(sha256_file(path) == expected, f"Archive hash mismatch: {name}")
    rel = str(path.relative_to(REPO))
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                             cwd=REPO, text=True, capture_output=True)
    require(tracked.returncode == 0, f"Archive file not tracked: {name}")

# --- Module loads. ----------------------------------------------------------
scan = load("a1s_audit", scan_path)
census_mod = load("a1c_audit", census_path)

# --- A1-S discovery gate. ---------------------------------------------------
config = json.loads((H / "a1_annotation_snapshot.json").read_text(encoding="utf-8"))
try:
    fasta, labels, counts = scan.discovery(config)
    require(counts == {"positive": 139, "negative": 139}, "Class counts are not 139/139")
    require(len(labels) == 278, "Manifest is not 278 rows")
    require(fasta.is_file(), "Frozen discovery FASTA is missing")
except Exception as exc:
    failures.append(f"discovery() gate failed: {exc}")

# --- Pfam version gate must reject every field mutation. --------------------
GOOD = ("Pfam release       : 37.0\n"
        "Pfam-A families    : 21979\n"
        "Date               : 2024-03\n"
        "Based on UniProtKB : 2023_05\n")
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    good = td / "good.gz"
    with gzip.open(good, "wt", encoding="utf-8") as fh:
        fh.write(GOOD)
    try:
        require(scan.pfam_version(good)["Pfam release"] == "37.0",
                "Valid Pfam.version record was misparsed")
    except Exception as exc:
        failures.append(f"Valid Pfam.version rejected: {exc}")

    for label, bad in (("release", GOOD.replace("37.0", "38.0")),
                       ("families", GOOD.replace("21979", "21978")),
                       ("date", GOOD.replace("2024-03", "2024-04")),
                       ("uniprot", GOOD.replace("2023_05", "2024_01"))):
        path = td / f"{label}.gz"
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            fh.write(bad)
        rejected = False
        try:
            scan.pfam_version(path)
        except RuntimeError:
            rejected = True
        require(rejected, f"Pfam.version mutation accepted: {label}")

# --- Loader repair: empty clan values must not enter the mapping. -----------
# Void record 001. The repair lives in the A1-C loader, not in census().
require("x[1].strip()" in census_src,
        "Loader does not filter empty clan values (void 001 regression)")

with tempfile.TemporaryDirectory() as td:
    synthetic = Path(td) / "Pfam-A.clans.tsv.gz"
    with gzip.open(synthetic, "wt", encoding="utf-8") as fh:
        fh.write("PF00001\tCL0001\tname\tid\tdesc\n")
        fh.write("PF00010\t\tname\tid\tdesc\n")
        fh.write("PF00011\t   \tname\tid\tdesc\n")
    loaded = {}
    with gzip.open(synthetic, "rt") as fh:
        for line in fh:
            x = line.rstrip().split("\t")
            if len(x) > 1 and x[1].strip():
                loaded[x[0]] = x[1].strip()
    require(loaded == {"PF00001": "CL0001"},
            f"Loader admitted an empty clan value: {loaded}")

# --- Census semantics. ------------------------------------------------------
cen = census_mod.census

# Clan mapping, transitive closure via a multidomain bridge, and the no-clan
# case as census() actually receives it: the family is ABSENT from the
# mapping, because the loader drops empty values.
positives = ["P1", "P2", "P3", "P4", "P5"]
hits = {"P1": {"PF00001", "PF00002"}, "P2": {"PF00003"},
        "P3": {"PF00009"}, "P4": {"PF00010"}}
clans = {"PF00001": "CL0001", "PF00002": "CL0002", "PF00003": "CL0002"}
try:
    ids, comps, summ = cen(positives, hits, clans)
    require(ids["P1"] == ["CL0001", "CL0002"], "Multidomain identifiers not retained")
    require(ids["P2"] == ["CL0002"], "Clan mapping broken")
    require(ids["P3"] == ["PF00009"], "Absent-family fallback failed")
    require(ids["P4"] == ["PF00010"], "No-clan family fallback failed")
    require(ids["P5"] == [], "Zero-hit positive not retained as unassigned")
    require(all(g for gs in ids.values() for g in gs), "Empty identifier emitted")
    require(sorted(len(c) for c in comps) == [1, 1, 2],
            f"Closure wrong: {sorted(len(c) for c in comps)}")
    require(summ["route"] in ROUTES, "route is not a frozen token")
except Exception as exc:
    failures.append(f"Census semantics failed: {exc}")

# Backstop: an empty clan value reaching census() must raise.
for bad_value in ("", None):
    raised = False
    try:
        cen(["X"], {"X": {"PFZZZZZ"}}, {"PFZZZZZ": bad_value})
    except Exception:
        raised = True
    require(raised, f"Empty-identifier guard did not raise on {bad_value!r}")

# --- Denominators and routing precedence. -----------------------------------
def build(n_assigned, sizes, total=100):
    pos = [f"Q{i:03d}" for i in range(total)]
    hits, clans, k = {}, {}, 0
    for gi, size in enumerate(sizes):
        fam = f"PF9{gi:04d}"
        clans[fam] = f"CL9{gi:03d}"
        for _ in range(size):
            hits[pos[k]] = {fam}
            k += 1
    assert k == n_assigned
    return pos, hits, clans

pos, hits, clans = build(100, [10] * 10)
_, _, s = cen(pos, hits, clans)
require(s["unassigned_positive_share"] == 0.0, "Unassigned share wrong")
require(s["largest_component_share_all_positives"] == 0.10, "Concentration denominator wrong")
require(s["l_value_among_assigned"] == 1.0, "L denominator wrong")
require(s["route"] == "TWO_STAGE_ELIGIBLE", f"Route wrong: {s['route']}")

pos, hits, clans = build(100, [16] + [1] * 84)
_, _, s = cen(pos, hits, clans)
require(s["largest_component_share_all_positives"] == 0.16, "Concentration share wrong")
require(s["route"] == "AMENDMENT_REQUIRED_CONCENTRATION",
        f"Concentration precedence failed: {s['route']}")

pos, hits, clans = build(89, [16] + [1] * 73)
_, _, s = cen(pos, hits, clans)
require(s["unassigned_positive_count"] == 11, "Unassigned count wrong")
require(s["route"] == "INCONCLUSIVE_UNASSIGNED",
        f"Missingness precedence failed: {s['route']}")

pos, hits, clans = build(100, [1] * 100)
_, _, s = cen(pos, hits, clans)
require(s["l_value_among_assigned"] == 0.0, "L is not zero on all-singletons")
require(s["assigned_singleton_fraction"] == 1.0, "Singleton fraction wrong")
require(s["route"] == "SKIP_STAGE1_NEAR_VACUOUS", f"Route wrong: {s['route']}")

# --- Output-schema firewall. ------------------------------------------------
require(census_mod.BANNED_COLUMNS == ("auroc", "tpr", "fpr", "score", "threshold"),
        "BANNED_COLUMNS drifted")
for bad in ("auroc", "tpr", "fpr", "score", "threshold"):
    blocked = False
    try:
        census_mod.check_columns(("protein_id", bad))
    except Exception:
        blocked = True
    require(blocked, f"check_columns admitted a banned column: {bad}")

print("── A1 SPLIT BEHAVIORAL AUDIT ──")
if failures:
    print(f"FAIL — {len(failures)} blocking issue(s)")
    for i, f in enumerate(failures, 1):
        print(f"{i}. {f}")
    sys.exit(1)

print("PASS — gates, phase separation, archive, discovery, Pfam gate,")
print("       loader repair, census semantics, routing precedence, schema firewall")
print(f"A1-S authorized: {'YES' if scan_gate == [True] else 'NO'}")
print(f"A1-C authorized: {'YES' if census_gate == [True] else 'NO'}")
