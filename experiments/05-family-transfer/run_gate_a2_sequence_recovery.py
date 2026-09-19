"""A2-SR sequence recovery scaffold. Hard-disabled."""

from pathlib import Path

A2_SEQUENCE_RECOVERY_AUTHORIZED = False

EXPECTED_POSITIVES = 161
EXPECTED_NEGATIVES = 3541
EXPECTED_TOTAL = 3702
BATCH_SIZE = 100
MAX_RETRIES = 5
REQUEST_TIMEOUT_SECONDS = 120

REPO = Path(__file__).resolve().parents[2]
EXP = REPO / 'experiments/05-family-transfer'
INPUT_MANIFEST = (
    EXP / 'a2_intake_archive/confirmatory_accession_manifest.tsv'
)
HISTORICAL_POSITIVE_SOURCE = (
    REPO / 'experiments/03-toxin-representation/'
    'stage1_model_blind/confirmatory_positive_universe.tsv'
)
OUTPUT = EXP / 'a2_sequence_recovery_archive'

FROZEN_RULES = {
    'membership_order': 'bytewise accession order',
    'fasta_serialization': (
        'identifier-only header; one unwrapped uppercase sequence line; '
        'LF endings; final LF'
    ),
    'mixed_release_action': 'SEQUENCE_SNAPSHOT_DRIFT',
    'missing_accession_action': 'SEQUENCE_SNAPSHOT_DRIFT',
    'extra_accession_action': 'SEQUENCE_SNAPSHOT_DRIFT',
    'length_mismatch_action': 'SEQUENCE_SNAPSHOT_DRIFT',
    'historical_annotation_status_role': 'claim_under_test',
    'confirmatory_outcomes_accessed': False,
}


def main():
    if not A2_SEQUENCE_RECOVERY_AUTHORIZED:
        raise SystemExit(
            'STOP: Gate A2 sequence recovery is not authorized'
        )

    raise RuntimeError(
        'A2_SEQUENCE_RECOVERY_IMPLEMENTATION_NOT_YET_AUDITED'
    )


if __name__ == '__main__':
    main()
