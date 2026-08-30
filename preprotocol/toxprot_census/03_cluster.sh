#!/usr/bin/env bash
# 03_cluster.sh — Run MMseqs2 clustering at frozen 30%-identity parameters (§4.1)
#
# Frozen parameters (config.py):
#   --min-seq-id  0.30   identity cutoff
#   -c            0.80   coverage
#   --cov-mode    1      shorter sequence must be ≥80% covered
#   --cluster-mode 0     greedy set cover
#   -s            7.5    sensitivity
#
# Inputs:  data/cleaned_precursor.fasta
#          data/cleaned_mature.fasta        (sensitivity analysis)
# Outputs: results/clusters_precursor.tsv
#          results/clusters_mature.tsv

set -euo pipefail

DATA="data"
RESULTS="results"
THREADS=8

# ── version check ─────────────────────────────────────────────────────────────
MMSEQS_VER=$(mmseqs version 2>/dev/null || echo "NOT_FOUND")
echo "MMseqs2 version: ${MMSEQS_VER}"
if [[ "${MMSEQS_VER}" == "NOT_FOUND" ]]; then
    echo "ERROR: mmseqs2 not found. Install from https://github.com/soedinglab/MMseqs2"
    exit 1
fi

# Record version for provenance
echo "${MMSEQS_VER}" > "${RESULTS}/mmseqs2_version.txt"

PARAMS="--min-seq-id 0.30 -c 0.80 --cov-mode 1 --cluster-mode 0 -s 7.5 --threads ${THREADS}"

cluster_fasta() {
    local LABEL="$1"
    local FASTA="${DATA}/$2"
    local TMPDIR="${DATA}/mmseqs_tmp_${LABEL}"
    local OUTPFX="${DATA}/mmseqs_${LABEL}"
    local OUTTSV="${RESULTS}/clusters_${LABEL}.tsv"

    echo ""
    echo "── Clustering: ${LABEL} (${FASTA}) ────────────────────────────────"
    echo "   Parameters: ${PARAMS}"
    mkdir -p "${TMPDIR}"

    mmseqs easy-cluster \
        "${FASTA}" \
        "${OUTPFX}" \
        "${TMPDIR}" \
        ${PARAMS}

    # easy-cluster writes <prefix>_cluster.tsv (rep_seq  member_seq)
    if [[ -f "${OUTPFX}_cluster.tsv" ]]; then
        cp "${OUTPFX}_cluster.tsv" "${OUTTSV}"
    elif [[ -f "${OUTPFX}.tsv" ]]; then
        cp "${OUTPFX}.tsv" "${OUTTSV}"
    else
        echo "ERROR: cluster TSV not found for ${LABEL}"
        exit 1
    fi

    N_MEMBERS=$(wc -l < "${OUTTSV}")
    N_CLUSTERS=$(cut -f1 "${OUTTSV}" | sort -u | wc -l)
    echo "   ${N_CLUSTERS} clusters  |  ${N_MEMBERS} member rows → ${OUTTSV}"

    # cleanup tmp
    rm -rf "${TMPDIR}" "${OUTPFX}"_*
}

mkdir -p "${RESULTS}"

# Primary: full precursor sequences
cluster_fasta "precursor" "cleaned_precursor.fasta"

# Sensitivity analysis: mature chains only
cluster_fasta "mature" "cleaned_mature.fasta"

echo ""
echo "Clustering complete. Record the MMseqs2 version above for provenance."
echo "Next: python3 04_divergence.py"
