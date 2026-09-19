#!/usr/bin/env python3
import ast
from pathlib import Path
H=Path(__file__).resolve().parent
scan=(H/"run_gate_a1_scan.py").read_text(); census=(H/"run_gate_a1_census.py").read_text()
ast.parse(scan); ast.parse(census)
assert "SCAN_AUTHORIZED = True" in scan
assert "CENSUS_AUTHORIZED=False" in census
for token in ("route_summary","largest_component","l_value","DisjointSet","clan_map"):
    assert token not in scan, f"census token in A1-S: {token}"
for token in ("hmmscan","hmmpress","discovery_sequences.fasta","urllib","requests"):
    assert token not in census, f"scan/network token in A1-C: {token}"
print("PASS — A1-S is authorized, A1-C remains disabled, and phase separation holds")
