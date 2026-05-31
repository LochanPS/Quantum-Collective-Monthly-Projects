"""Circuit pattern recognition.

Identifies well-known quantum circuit patterns by:
1. Normalized fingerprint lookup against known_patterns.json
2. Structural rules as fallback

Returns the name of the recognized pattern or an empty string.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .fingerprint import compute as compute_fingerprint, jaccard_similarity


# ── Load known patterns ─────────────────────────────────────────────────────

def _find_patterns_file() -> Optional[Path]:
    """Find known_patterns.json in the circuit-library directory."""
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent.parent / "circuit-library" / "known_patterns.json",
        here.parent.parent / "circuit-library" / "known_patterns.json",
        Path.cwd() / "circuit-library" / "known_patterns.json",
        Path(os.environ.get("QCSIM_LIBRARY_PATH", "")) / "known_patterns.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _load_known_patterns() -> List[dict]:
    path = _find_patterns_file()
    if not path:
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("patterns", [])
    except Exception:
        return []


# ── Structural rule-based recognition ──────────────────────────────────────

def _structural_recognize(gates: List[dict], num_qubits: int) -> str:
    """Identify patterns from gate structure when fingerprint doesn't match."""
    gate_types = [g.get("gate", "") for g in gates]
    # Remove target/partner entries (only count control/primary sides)
    active = [g for g in gates if g.get("gate") not in ("CNOT_T", "SWAP_B")]
    types = [g.get("gate", "") for g in active]
    count = len(active)

    # Bell state: exactly H + CNOT on 2 qubits
    if (num_qubits == 2 and count == 2
            and "H" in types and "CNOT_C" in types):
        return "Bell State"

    # GHZ state: H + n-1 CNOTs on n qubits
    if (count == num_qubits
            and types.count("H") == 1
            and types.count("CNOT_C") == num_qubits - 1):
        return f"GHZ State ({num_qubits} qubits)"

    # Uniform superposition: all H gates
    if types and all(t == "H" for t in types) and len(types) == num_qubits:
        return "Uniform Superposition"

    # Bit flip: single X gate
    if count == 1 and types == ["X"]:
        return "Bit Flip (X gate)"

    # Swap test / bell basis
    if count == 1 and types == ["H"]:
        return "Hadamard (superposition)"

    return ""


# ── Main recognition function ───────────────────────────────────────────────

def recognize(gates: List[dict], num_qubits: int) -> str:
    """Attempt to recognize a circuit as a known pattern.

    First tries exact fingerprint lookup, then falls back to structural rules.

    Args:
        gates: List of gate dicts from CircuitGrid.to_json or circuit-library JSON.
        num_qubits: Number of qubits in the circuit.

    Returns:
        Name of the recognized pattern, or empty string if unrecognized.
    """
    if not gates:
        return ""

    # Phase 1: fingerprint lookup
    fp = compute_fingerprint(gates, num_qubits)
    known = _load_known_patterns()
    for pattern in known:
        if pattern.get("fingerprint") == fp:
            return pattern.get("name", "")

    # Phase 2: structural rules
    return _structural_recognize(gates, num_qubits)


def recognize_grid(grid) -> str:
    """Recognize a pattern from a CircuitGrid (TUI data model).

    Args:
        grid: qcsim.tui.CircuitGrid instance.

    Returns:
        Pattern name or empty string.
    """
    gates = []
    for row in range(grid.num_qubits):
        for col in range(grid.num_cols):
            cell = grid.cells[row][col]
            if cell.gate:
                entry = {"gate": cell.gate, "row": row, "col": col}
                if cell.linked_row >= 0:
                    entry["linked_row"] = cell.linked_row
                gates.append(entry)
    return recognize(gates, grid.num_qubits)
