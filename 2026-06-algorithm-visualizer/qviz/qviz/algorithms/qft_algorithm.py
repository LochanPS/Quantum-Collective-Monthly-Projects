"""Quantum Fourier Transform, wrapping qcsim's existing qft() builder.

Annotations here are intentionally generic -- qcsim.qft.qft() doesn't tag
which gate is "rotating qubit i relative to qubit j" vs "the final swap",
so step-by-step it just says "QFT gate". Writing precise per-gate
annotations for this one is a good Beginner-tier contribution (see the
challenge README) -- the gate sequence itself is already correct and
tested in qcsim.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from qcsim import QuantumCircuit
from qcsim.qft import qft


def qft_algorithm(
    num_qubits: int = 3, initial_state: Optional[str] = None
) -> Tuple[QuantumCircuit, List[str]]:
    """Build a QFT circuit and its (generic) step annotations.

    Args:
        num_qubits: Number of qubits to transform.
        initial_state: Optional bitstring to prepare before the QFT, e.g.
            "101". Defaults to |0...0>.

    Returns:
        (circuit, annotations) -- annotations has exactly one entry per
        gate in circuit's log, in order.
    """
    qc = QuantumCircuit(num_qubits)
    annotations: List[str] = []

    if initial_state:
        for q, bit in enumerate(initial_state):
            if bit == "1":
                qc.x(q)
                annotations.append(f"Prepare input: flip q{q} to |1> (part of |{initial_state}>)")

    before = len(qc._log)
    qft(qc, list(range(num_qubits)))
    added = len(qc._log) - before
    for _ in range(added):
        annotations.append("QFT step (Hadamard or controlled-phase rotation -- see qcsim.qft source)")

    return qc, annotations
