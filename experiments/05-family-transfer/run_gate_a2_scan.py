"""A2-SS raw Pfam/MMseqs2 scan scaffold. Hard-disabled."""

from pathlib import Path

A2_SCAN_AUTHORIZED = False

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / 'experiments/05-family-transfer'
RECOVERY_ARCHIVE = EXP / 'a2_sequence_recovery_archive'
OUTPUT = EXP / 'a2_scan_archive'

PFAM_RELEASE = '37.0'
PFAM_FAMILY_COUNT = 21979
PFAM_THRESHOLD_RULE = '--cut_ga'

MMSEQS_SOURCE_COMMIT = 'eec9c354be4276d2373996af2e50808b1390d527'
MMSEQS_PARAMETERS = {
    'min_seq_id': 0.30,
    'coverage': 0.80,
    'coverage_mode': 1,
    'cluster_mode': 0,
    'sensitivity': 7.5,
    'threads': 8,
    'independent_runs': 2,
}

FORBIDDEN_DERIVATIONS = (
    'clan_mapping',
    'combined_edges',
    'components',
    'concentration',
    'cross_label_relationships',
    'family_disjointness',
)


def main():
    if not A2_SCAN_AUTHORIZED:
        raise SystemExit(
            'STOP: Gate A2 raw scan is not authorized'
        )

    raise RuntimeError(
        'A2_SCAN_IMPLEMENTATION_NOT_YET_AUDITED'
    )


if __name__ == '__main__':
    main()
