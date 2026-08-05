"""Small demo circuits for the CLI and examples.

Each builder returns a fresh qcsim ``QuantumCircuit``. Kept dependency-free
(no qviz import) so qnoise stands alone; contributors can add more here.
"""

from __future__ import annotations

from typing import Callable, Dict

import numpy as np
from qcsim import QuantumCircuit


def bell() -> QuantumCircuit:
    """2-qubit Bell state: (|00> + |11>) / sqrt(2)."""
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    return qc


def ghz3() -> QuantumCircuit:
    """3-qubit GHZ state: (|000> + |111>) / sqrt(2)."""
    qc = QuantumCircuit(3)
    qc.h(0).cnot(0, 1).cnot(1, 2)
    return qc


def ghz4() -> QuantumCircuit:
    """4-qubit GHZ state."""
    qc = QuantumCircuit(4)
    qc.h(0).cnot(0, 1).cnot(1, 2).cnot(2, 3)
    return qc


def plus_layer() -> QuantumCircuit:
    """3 independent |+> qubits (uniform superposition) — a clean target for
    seeing dephasing/readout error distort an even distribution."""
    qc = QuantumCircuit(3)
    qc.h(0).h(1).h(2)
    return qc


def grover2() -> QuantumCircuit:
    """2-qubit Grover search marking |11>. One iteration finds it with certainty
    in the ideal case, so noise shows up as a drop in the |11> peak."""
    qc = QuantumCircuit(2)
    qc.h(0).h(1)          # uniform superposition
    qc.cz(0, 1)           # oracle marks |11>
    qc.h(0).h(1)          # diffusion
    qc.x(0).x(1)
    qc.cz(0, 1)
    qc.x(0).x(1)
    qc.h(0).h(1)
    return qc


#: Named demo circuits, in menu order.
DEMOS: Dict[str, Callable[[], QuantumCircuit]] = {
    "bell": bell,
    "ghz3": ghz3,
    "ghz4": ghz4,
    "plus": plus_layer,
    "grover2": grover2,
}
