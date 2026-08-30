"""
config.py — ALL frozen design parameters for the Tox-Prot Pre-Protocol Census.

These values were derived from the estimand before any Tox-Prot data were seen.
They must not change once the pull begins. Any change requires a new census
with a versioned config file and a recorded justification.

Source: Tox-Prot Target-Selection and Pre-Protocol Census Plan §§4, 6, 7, 8.
"""

import os

# ── UniProt pull ─────────────────────────────────────────────────────────────
UNIPROT_QUERY    = "reviewed:true AND keyword:KW-0800"
UNIPROT_PAGE_SIZE = 500
UNIPROT_FIELDS   = [
    "accession", "reviewed", "id", "protein_name", "gene_names",
    "organism_name", "organism_id", "lineage",
    "length", "sequence", "mass", "fragment",
    "keyword", "protein_existence", "annotation_score",
    "cc_function", "cc_subcellular_location",
    "ft_signal", "ft_propep", "ft_chain",
    "xref_pfam", "xref_interpro",
]

# ── Sequence cleaning (§2, §3) ───────────────────────────────────────────────
EXCLUDE_FRAGMENTS         = True   # any ft_fragment annotation → excluded
MAX_NONSTANDARD_FRACTION  = 0.01   # >1% X/B/Z → excluded
MIN_LENGTH                = 5      # residues (after mature-chain trimming where applied)
MAX_LENGTH                = 5000   # residues

# ── MMseqs2 clustering (§4.1) ────────────────────────────────────────────────
# Frozen before data pull. Coverage mode 1: shorter sequence must be ≥80% covered.
# Rationale for cov-mode 1: toxin lengths span 10–1000+ residues; bidirectional
# coverage would exclude all short-peptide clusters.
MMSEQS2_MIN_SEQ_ID    = 0.30
MMSEQS2_COVERAGE      = 0.80
MMSEQS2_COV_MODE      = 1      # shorter sequence coverage
MMSEQS2_CLUSTER_MODE  = 0      # greedy set cover
MMSEQS2_THREADS       = 8
MMSEQS2_SENSITIVITY   = 7.5    # high sensitivity for low-identity search

# ── Divergence rule (§4.2) ───────────────────────────────────────────────────
DIVERGENCE_IDENTITY_CUTOFF = 0.30  # same cutoff as clustering

# ── Family-disjoint classification (§4.3, §7) ────────────────────────────────
# A divergent cluster is family-disjoint when no member of the reference set
# shares the same Pfam family accession (e.g. PF00012, not just clan CL0001).
# Missing annotations are treated as NOT establishing disjointness — they are
# recorded separately and never silently counted as family-independent.
FAMILY_DISJOINT_LEVEL = "pfam_family"   # narrow level for the primary claim

# ── Diagnostic burn partition (§6) ───────────────────────────────────────────
# Assignment is deterministic: md5(accession_of_cluster_representative)
# Clusters with first_md5_byte < BURN_THRESHOLD_BYTE are burned.
DIAGNOSTIC_BURN_FRAC          = 0.15
DIAGNOSTIC_BURN_THRESHOLD_BYTE = int(0.15 * 256)   # = 38

# ── Fixed-FPR operating points (§8.2) ────────────────────────────────────────
FPR_PRIMARY            = 0.05
FPR_SECONDARY          = 0.01   # secondary, reported only if neg support adequate

# ── Gates (§8) ───────────────────────────────────────────────────────────────
GATE_A_STRICT_MIN         = 90    # sequence-divergent AND family-disjoint, after burns
GATE_A_REDESIGN_FLOOR     = 300   # total positive clusters below this → redesign
GATE_B_MAX_FAMILY_FRAC    = 0.25  # no single family > 25% of divergent clusters
GATE_C_PRIMARY_MIN_NEG    = 1000  # held-out matched negatives at FPR_PRIMARY
GATE_C_SECONDARY_MIN_NEG  = 3000  # at FPR_SECONDARY
TARGET_HW                 = 0.10  # primary ±0.10 half-width on ΔTPR

# Planning-only assumptions (never imposed on observed data)
PLAN_DIVERGENT_FRAC   = 0.20    # Exp 01 geometry; replaced by observed value
PLAN_DTPR_TRUE        = 0.15    # planning assumed true ΔTPR

# ── Randomisation ────────────────────────────────────────────────────────────
RANDOM_SEED = 20260829

# ── Paths (override with environment variables) ──────────────────────────────
DATA_DIR    = os.environ.get("CENSUS_DATA_DIR",    "data")
RESULTS_DIR = os.environ.get("CENSUS_RESULTS_DIR", "results")
