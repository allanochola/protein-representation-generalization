#!/usr/bin/env bash
# run_census.sh — Execute the Tox-Prot census pipeline end-to-end.
#
# Steps run in order:
#   01_pull.py       → data/raw_toxprot.jsonl
#   02_clean.py      → results/cleaned_entries.tsv + FASTAs
#   03_cluster.sh    → results/clusters_precursor.tsv (requires mmseqs2 on PATH)
#   04_divergence.py → results/divergence_assignment.tsv
#   05_families.py   → results/gatev2_audit.tsv, family_concentration.tsv
#   06_negatives.py  → results/negative_pool_counts.tsv
#   07_diagnostics.py→ results/shortcut_diagnostic_results.tsv
#   08_gates.py      → results/census_decision.txt
#
# No ESM-2 embeddings, SAE activations, or toxin classifier scores are
# produced or examined at any point.
#
# Usage:
#   cd census/
#   bash run_census.sh 2>&1 | tee results/census_run.log

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

mkdir -p data results

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

log "=== Tox-Prot Census Pipeline ==="

log "Step 1: Pull UniProt Tox-Prot entries"
python3 01_pull.py

log "Step 2: Clean sequences and apply evidence filters"
python3 02_clean.py

log "Step 3: MMseqs2 clustering at 30% identity"
bash 03_cluster.sh

log "Step 4: Assign divergence (§4.2 corpus-wide rule)"
python3 04_divergence.py

log "Step 5: Family annotation and Gate V2 audit"
python3 05_families.py

log "Step 6: Construct and count matched-negative pools"
python3 06_negatives.py

log "Step 7: Shortcut diagnostics on burned partition"
python3 07_diagnostics.py

log "Step 8: Evaluate all gates and issue census decision"
python3 08_gates.py

log ""
log "=== Census complete ==="
log "Decision: $(grep '^CENSUS DECISION' results/census_decision.txt || echo 'see census_decision.txt')"
log ""
log "Required §11 outputs:"
for f in \
    "results/cleaned_entries.tsv" \
    "results/evidence_summary.tsv" \
    "results/duplicate_report.tsv" \
    "results/clusters_precursor.tsv" \
    "results/family_concentration.tsv" \
    "results/length_composition.tsv" \
    "results/negative_pool_counts.tsv" \
    "results/shortcut_diagnostic_results.tsv" \
    "results/mature_chain_sensitivity.tsv" \
    "results/precision_check.tsv" \
    "results/census_decision.txt"; do
    if [[ -f "${f}" ]]; then
        log "  ✓ ${f}"
    else
        log "  ✗ ${f}  MISSING"
    fi
done
