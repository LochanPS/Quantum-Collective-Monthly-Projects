"""Circuit analysis utilities for the info panel.

CircuitAnalyzer computes metrics from a CircuitGrid (the TUI data model)
or from a QuantumCircuit log. All computations are O(gates) — trivial cost,
safe to run on every grid change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass  # avoid circular imports


# Gate categories for classification
_TWO_QUBIT_GATES = {"CNOT_C", "CNOT", "CX", "CY", "CZ", "SWAP_A", "SWAP", "CP", "CCX"}
_T_GATES = {"T", "Tdg"}
_SINGLE_QUBIT_GATES = {"H", "X", "Y", "Z", "S", "Sdg", "SX", "SXdg", "Rx", "Ry", "Rz", "P", "U", "I"}
_CLIFFORD_GATES = {"H", "X", "Y", "Z", "S", "Sdg", "SX", "SXdg", "CNOT", "CNOT_C", "CX", "CZ", "SWAP_A", "SWAP"}


@dataclass
class CircuitMetrics:
    """All computed metrics for a circuit."""

    num_qubits: int = 0
    gate_count: int = 0          # total gates placed
    depth: int = 0               # max occupied column index + 1
    single_qubit_count: int = 0
    two_qubit_count: int = 0
    t_gate_count: int = 0        # T + Tdg (fault-tolerance cost)
    non_clifford_count: int = 0  # non-Clifford gates (cost on fault-tolerant QPU)
    entangled: bool = False      # any 2-qubit gate present?
    qubits_used: int = 0         # number of qubits with at least one gate
    utilization_pct: float = 0.0 # qubits_used / num_qubits * 100
    empty: bool = True           # no gates at all

    def summary_line(self) -> str:
        """One-line human-readable summary for the TUI info panel."""
        if self.empty:
            return "  Circuit empty — place gates to begin."

        parts = [
            f"Gates: {self.gate_count}",
            f"Depth: {self.depth}",
            f"2-qubit: {self.two_qubit_count}",
            f"T-gates: {self.t_gate_count}",
            f"Qubits used: {self.qubits_used}/{self.num_qubits}",
            f"Entangled: {'YES' if self.entangled else 'no'}",
        ]
        return "  " + "  |  ".join(parts)


def analyze_grid(grid) -> CircuitMetrics:
    """Compute metrics from a CircuitGrid (TUI data model).

    Args:
        grid: qcsim.tui.CircuitGrid instance.

    Returns:
        CircuitMetrics with all fields populated.
    """
    m = CircuitMetrics(num_qubits=grid.num_qubits)
    qubits_with_gates = set()
    max_col_used = -1

    for row in range(grid.num_qubits):
        for col in range(grid.num_cols):
            cell = grid.cells[row][col]
            if not cell.gate:
                continue

            gate = cell.gate
            # Don't double-count two-qubit pairs (count only the _C / _A side)
            if gate in ("CNOT_T", "SWAP_B"):
                continue

            m.gate_count += 1
            qubits_with_gates.add(row)
            if cell.linked_row >= 0:
                qubits_with_gates.add(cell.linked_row)
            if col > max_col_used:
                max_col_used = col

            if gate in _TWO_QUBIT_GATES:
                m.two_qubit_count += 1
                m.entangled = True
            elif gate in _SINGLE_QUBIT_GATES:
                m.single_qubit_count += 1

            if gate in _T_GATES:
                m.t_gate_count += 1

            if gate not in _CLIFFORD_GATES:
                m.non_clifford_count += 1

    m.depth = max_col_used + 1 if max_col_used >= 0 else 0
    m.qubits_used = len(qubits_with_gates)
    m.utilization_pct = (m.qubits_used / m.num_qubits * 100) if m.num_qubits > 0 else 0.0
    m.empty = m.gate_count == 0

    return m


def analyze_log(log: list, num_qubits: int) -> CircuitMetrics:
    """Compute metrics from a QuantumCircuit._log list.

    Args:
        log: List of (name, qubits, params) tuples.
        num_qubits: Number of qubits in the circuit.

    Returns:
        CircuitMetrics with all fields populated.
    """
    m = CircuitMetrics(num_qubits=num_qubits)
    qubits_with_gates: set = set()

    for col, (name, qubits, params) in enumerate(log):
        if name == "BARRIER":
            continue

        m.gate_count += 1
        qubits_with_gates.update(qubits)

        if name in ("CNOT", "CX", "CY", "CZ", "SWAP", "CP"):
            m.two_qubit_count += 1
            m.entangled = True
        elif name in ("CCX",):
            m.two_qubit_count += 1
            m.entangled = True
        else:
            m.single_qubit_count += 1

        if name in ("T", "Tdg"):
            m.t_gate_count += 1

        if name not in _CLIFFORD_GATES:
            m.non_clifford_count += 1

    m.depth = sum(1 for name, _, _ in log if name != "BARRIER")
    m.qubits_used = len(qubits_with_gates)
    m.utilization_pct = (m.qubits_used / num_qubits * 100) if num_qubits > 0 else 0.0
    m.empty = m.gate_count == 0

    return m
