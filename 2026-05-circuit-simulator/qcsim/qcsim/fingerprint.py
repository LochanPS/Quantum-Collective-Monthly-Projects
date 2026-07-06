"""Circuit fingerprinting utilities.

Provides a normalized fingerprint for structural duplicate detection
and a Jaccard similarity score for circuit comparison.

Normalization rules applied before hashing:
    1. Empty columns stripped (column index does not matter, only order).
    2. Gates within each column sorted by row index (canonical order).
    3. Parametric angles rounded to 3 decimal places.
    4. Qubit count always included (2q Bell != 3q Bell).

This means circuits that are structurally identical but placed in
different column positions are treated as the same circuit.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from typing import Any, Dict, List, Tuple


def _round_angle(v: Any) -> Any:
    """Round a numeric angle to 3 decimal places for stable fingerprinting."""
    try:
        return round(float(v), 3)
    except (TypeError, ValueError):
        return v


def _normalize_gate(gate: dict) -> dict:
    """Produce a canonical, normalized representation of a gate entry."""
    out: Dict[str, Any] = {
        "gate": gate.get("gate", ""),
        "row": int(gate.get("row", 0)),
    }
    if "linked_row" in gate and gate["linked_row"] >= 0:
        out["linked_row"] = int(gate["linked_row"])
    # Normalize parametric angles
    for key in ("theta", "phi", "lam", "angle"):
        if key in gate:
            out[key] = _round_angle(gate[key])
    return out


def _compress_columns(gates: List[dict]) -> List[dict]:
    """Strip empty columns: remap col indices to a compact sequence.

    Gates in the same original column keep the same new column index.
    Empty columns are discarded.
    """
    if not gates:
        return []
    used_cols = sorted({g.get("col", 0) for g in gates})
    col_map = {old: new for new, old in enumerate(used_cols)}
    out = []
    for g in gates:
        ng = dict(g)
        ng["col"] = col_map[g.get("col", 0)]
        out.append(ng)
    return out


def _canonical_gates(gates: List[dict]) -> List[dict]:
    """Return fully normalized and sorted gate list.

    1. Compress empty columns.
    2. Normalize each gate entry.
    3. Sort by (col, row) for a canonical order.
    """
    compressed = _compress_columns(gates)
    normalized = [_normalize_gate(g) for g in compressed]
    # Sort by column then row for canonical ordering
    normalized.sort(key=lambda g: (g.get("col", 0), g.get("row", 0)))
    return normalized


def compute(gates: List[dict], num_qubits: int) -> str:
    """Compute a 16-hex-char normalized fingerprint for a circuit.

    Args:
        gates: List of gate dicts (from CircuitGrid.to_json or circuit-library JSON).
        num_qubits: Number of qubits in the circuit.

    Returns:
        16-character lowercase hex string.
    """
    canonical = _canonical_gates(gates)
    payload = json.dumps(
        {"num_qubits": int(num_qubits), "gates": canonical},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def compute_from_log(log: list, num_qubits: int) -> str:
    """Compute fingerprint from a QuantumCircuit._log list.

    Args:
        log: List of (name, qubits, params) tuples from QuantumCircuit._log.
        num_qubits: Number of qubits.

    Returns:
        16-character lowercase hex string.
    """
    gates = []
    for col, (name, qubits, params) in enumerate(log):
        if name == "BARRIER":
            continue
        entry: Dict[str, Any] = {"gate": name, "row": qubits[0], "col": col}
        if len(qubits) > 1:
            entry["linked_row"] = qubits[1]
        if params:
            for k, v in params.items():
                if k not in ("matrix_shape",):
                    entry[k] = _round_angle(v)
        gates.append(entry)
    return compute(gates, num_qubits)


# ── Similarity ─────────────────────────────────────────────────────────────


def _gate_type_multiset(gates: List[dict]) -> Counter:
    """Build a Counter of gate type names (ignoring position/params)."""
    return Counter(g.get("gate", "") for g in gates)


def jaccard_similarity(gates_a: List[dict], gates_b: List[dict]) -> float:
    """Compute Jaccard similarity between two circuits' gate type multisets.

    Jaccard = |A ∩ B| / |A ∪ B|

    This measures how similar two circuits are in terms of the gates they
    use, regardless of position. A score of 1.0 = identical gate types and
    counts. A score of 0.0 = no gate types in common.

    Args:
        gates_a: Gate list from circuit A.
        gates_b: Gate list from circuit B.

    Returns:
        Float between 0.0 and 1.0.
    """
    if not gates_a and not gates_b:
        return 1.0
    if not gates_a or not gates_b:
        return 0.0

    ms_a = _gate_type_multiset(gates_a)
    ms_b = _gate_type_multiset(gates_b)

    all_types = set(ms_a) | set(ms_b)
    intersection = sum(min(ms_a.get(t, 0), ms_b.get(t, 0)) for t in all_types)
    union = sum(max(ms_a.get(t, 0), ms_b.get(t, 0)) for t in all_types)

    return intersection / union if union > 0 else 0.0
