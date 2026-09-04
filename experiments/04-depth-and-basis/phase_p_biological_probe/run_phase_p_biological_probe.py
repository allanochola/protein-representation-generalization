#!/usr/bin/env python3
"""
Experiment 04 — Arm-B Phase-P biological probe runner.

STATUS:
    HARD-DISABLED BEFORE BIOLOGICAL PROBE EXECUTION.

Governed by:

    experiments/04-depth-and-basis/
    ARM_B_PHASE_P_BIOLOGICAL_PROBING_INHERITANCE_CONTRACT.md

Certified contract SHA-256:

    bac4bcf0933a12e149abfa52fd84d3c310c338bdb59b32ca21dfbdaf63952dbe

Authoritative corrected Arm-B mechanics source:

    experiments/04-depth-and-basis/
    diagnose_arm_b_post_failure_architecture.py

Certified mechanics-source SHA-256:

    a15420b8a7528eeae9d2d7faf811ccbd19708793fe2e3562306c64c1b377166d

Scientific firewall while disabled:

- Phase-E matrices must not be loaded.
- Biological labels must not be loaded for probing.
- No biological perturbation seed may be generated or materialized.
- sklearn must not be imported.
- No probe may be fit.
- No CV may run.
- No AUROC may be computed.
- No support statistic may be computed.
- Confirmatory data must not be accessed.
- 4000-4099 remains UNOPENED.
- 2000-2099 remains SEALED.
- 910001-910100 is CONSUMED / CLOSED.
- 920001-920100 is CONSUMED / CLOSED.
- 930001-930100 is CONSUMED / CLOSED.
- No 940001-940100 namespace exists.

The biological perturbation namespace is deliberately unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final
import hashlib
import sys


# ============================================================================
# HARD EXECUTION GATE
# ============================================================================

ENABLE_PHASE_P_BIOLOGICAL_PROBING: Final[bool] = False


# ============================================================================
# Frozen repository provenance
# ============================================================================

HERE: Final[Path] = Path(__file__).resolve().parent
REPO_ROOT: Final[Path] = HERE.parents[2]

CONTRACT_REL: Final[str] = (
    "experiments/04-depth-and-basis/"
    "ARM_B_PHASE_P_BIOLOGICAL_PROBING_INHERITANCE_CONTRACT.md"
)

CONTRACT_SHA256: Final[str] = (
    "bac4bcf0933a12e149abfa52fd84d3c310c338bdb59b32ca21dfbdaf63952dbe"
)

AUTHORITATIVE_MECHANICS_REL: Final[str] = (
    "experiments/04-depth-and-basis/"
    "diagnose_arm_b_post_failure_architecture.py"
)

AUTHORITATIVE_MECHANICS_SHA256: Final[str] = (
    "a15420b8a7528eeae9d2d7faf811ccbd19708793fe2e3562306c64c1b377166d"
)

PHASE_E_OUTPUT_REL: Final[str] = (
    "experiments/04-depth-and-basis/"
    "phase_e_extraction/output"
)


# ============================================================================
# Frozen Phase-E representation identities
# ============================================================================

LAYERS: Final[tuple[int, ...]] = (
    1,
    9,
    18,
    24,
    30,
    33,
)

N_DISCOVERY_PER_CLASS: Final[int] = 139
N_DISCOVERY_TOTAL: Final[int] = 278
ESM_WIDTH: Final[int] = 1280

PHASE_E_MATRIX_SHA256: Final[dict[int, str]] = {
    1: "204b2d0901b805ce9221b8318883e29dfe2c9a2c1aa18f37b6fc831ef3b08c15",
    9: "7eb08b17232cbf34c23ac8e246dbeb07bec2197904d4bb24e6717a93c1d03683",
    18: "c4e408db0963a0cbb90996ebb59b5e83cd86a9120de1a968cd4b7d80f5fa440e",
    24: "78c34e2c4419fb1ba850e383ab56b06b864412e65ba5046379983ff9e1190336",
    30: "ebc98537034ea7946b4c634d4a0a3fff18f503428b3f182c79360a604159c98b",
    33: "64e626858aa8e2a0a323af5121520f969f942679f8cbec4d27c7116bc8501f0d",
}

PHASE_E_ROWS_SHA256: Final[str] = (
    "ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e"
)

PHASE_E_PROVENANCE_SHA256: Final[str] = (
    "655ea47a8300f1056656378238402cf12dc5a024b96c18117397bb804b02e6dd"
)


# ============================================================================
# Frozen biological geometry
# ============================================================================

TARGET_N_VALUES: Final[tuple[int, ...]] = (
    100,
    120,
    139,
)

STABILITY_FRACTION: Final[float] = 0.80

STABILITY_PER_CLASS: Final[dict[int, int]] = {
    100: 80,
    120: 96,
    139: 111,
}


# ============================================================================
# Frozen L1 probe family
# ============================================================================

C_GRID: Final[tuple[float, ...]] = (
    1e-4,
    3e-4,
    1e-3,
    3e-3,
    1e-2,
    3e-2,
    1e-1,
    3e-1,
    1.0,
)

N_CV_FOLDS: Final[int] = 5

PROBE_PENALTY: Final[str] = "l1"
PROBE_SOLVER: Final[str] = "liblinear"
PROBE_FIT_INTERCEPT: Final[bool] = True
PROBE_MAX_ITER: Final[int] = 10000
PROBE_TOL: Final[float] = 1e-6

FEATURE_STANDARDIZATION_ENABLED: Final[bool] = False


# ============================================================================
# Frozen stream identities inherited from corrected architecture
#
# These are stream IDs only.
# They do NOT authorize a biological perturbation seed namespace.
# ============================================================================

STREAM_SUBSAMPLE: Final[int] = 21
STREAM_STAGE_A_SPLIT: Final[int] = 22
STREAM_CV: Final[int] = 23
STREAM_STAGE_A_FIT: Final[int] = 24
STREAM_STAGE_B_FIT: Final[int] = 25
STREAM_STABILITY_SUBSAMPLE: Final[int] = 26
STREAM_STABILITY_FIT: Final[int] = 27


# ============================================================================
# Seed firewall
# ============================================================================

CONSUMED_CLOSED_SEED_RANGES: Final[tuple[str, ...]] = (
    "910001-910100",
    "920001-920100",
    "930001-930100",
)

UNOPENED_SEED_RANGE: Final[str] = "4000-4099"
SEALED_VALIDATION_SEED_RANGE: Final[str] = "2000-2099"

# Intentionally no biological perturbation seed range is defined here.
# Intentionally no 940001-940100 range is defined here.


# ============================================================================
# Frozen simple-sequence baseline
# ============================================================================

CANONICAL_AA_ORDER: Final[tuple[str, ...]] = tuple(
    "ACDEFGHIKLMNPQRSTVWY"
)

BASELINE_DIM: Final[int] = 21


# ============================================================================
# Frozen schema
# ============================================================================

@dataclass(frozen=True)
class FrozenProbeSpec:
    penalty: str
    solver: str
    fit_intercept: bool
    max_iter: int
    tol: float
    c_grid: tuple[float, ...]
    n_cv_folds: int
    stability_fraction: float


FROZEN_PROBE_SPEC: Final[FrozenProbeSpec] = FrozenProbeSpec(
    penalty=PROBE_PENALTY,
    solver=PROBE_SOLVER,
    fit_intercept=PROBE_FIT_INTERCEPT,
    max_iter=PROBE_MAX_ITER,
    tol=PROBE_TOL,
    c_grid=C_GRID,
    n_cv_folds=N_CV_FOLDS,
    stability_fraction=STABILITY_FRACTION,
)


class PhasePContractError(RuntimeError):
    """Frozen Phase-P source/provenance violation."""


def sha256_file(path: Path) -> str:
    """Hash a non-biological repository source/provenance file."""
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def validate_static_contract_only() -> None:
    """
    Validate non-biological static source/provenance only.

    Does not load:
    - Phase-E matrices;
    - biological labels;
    - biological perturbation seeds.
    """
    contract_path = REPO_ROOT / CONTRACT_REL
    mechanics_path = REPO_ROOT / AUTHORITATIVE_MECHANICS_REL

    if not contract_path.is_file():
        raise PhasePContractError(
            f"Missing Phase-P inheritance contract: {CONTRACT_REL}"
        )

    if not mechanics_path.is_file():
        raise PhasePContractError(
            "Missing authoritative mechanics source: "
            f"{AUTHORITATIVE_MECHANICS_REL}"
        )

    if sha256_file(contract_path) != CONTRACT_SHA256:
        raise PhasePContractError(
            "Phase-P inheritance contract SHA drift."
        )

    if sha256_file(mechanics_path) != AUTHORITATIVE_MECHANICS_SHA256:
        raise PhasePContractError(
            "Authoritative mechanics source SHA drift."
        )

    if LAYERS != (1, 9, 18, 24, 30, 33):
        raise PhasePContractError("Frozen layer tuple changed.")

    if TARGET_N_VALUES != (100, 120, 139):
        raise PhasePContractError("Frozen target-N tuple changed.")

    if C_GRID != (
        1e-4,
        3e-4,
        1e-3,
        3e-3,
        1e-2,
        3e-2,
        1e-1,
        3e-1,
        1.0,
    ):
        raise PhasePContractError("Frozen C grid changed.")

    if STABILITY_PER_CLASS != {
        100: 80,
        120: 96,
        139: 111,
    }:
        raise PhasePContractError(
            "Frozen stability sample sizes changed."
        )

    if FEATURE_STANDARDIZATION_ENABLED is not False:
        raise PhasePContractError(
            "Feature standardization unexpectedly enabled."
        )

    if BASELINE_DIM != 21:
        raise PhasePContractError(
            "Frozen baseline dimension changed."
        )

    if len(CANONICAL_AA_ORDER) != 20:
        raise PhasePContractError(
            "Canonical amino-acid order must contain 20 residues."
        )


# ============================================================================
# ENABLED-ONLY boundary
#
# No biological implementation exists at this repository boundary.
# ============================================================================

def run_enabled_phase_p() -> None:
    """Future separately authorized biological execution path."""
    raise PhasePContractError(
        "Phase-P biological implementation is not authorized at this freeze."
    )


def main() -> int:
    """
    Hard-disabled execution entrypoint.

    Gate is checked before static validation and before the enabled placeholder.
    """
    if not ENABLE_PHASE_P_BIOLOGICAL_PROBING:
        print("PHASE-P BIOLOGICAL PROBING: HARD-DISABLED")
        print("No Phase-E matrix was loaded.")
        print("No biological label was loaded for probing.")
        print("No perturbation seed namespace was accessed.")
        print("No sklearn model was imported or fit.")
        print("No CV was performed.")
        print("No AUROC was computed.")
        print("No support statistic was computed.")
        print("No confirmatory data was accessed.")
        print("4000-4099: UNOPENED")
        print("2000-2099: SEALED")
        return 0

    validate_static_contract_only()
    run_enabled_phase_p()

    return 0


if __name__ == "__main__":
    sys.exit(main())
