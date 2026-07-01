"""Quantum Fourier Transform, wrapping qcsim's existing qft() builder.

Builds a QFT circuit together with descriptive per-gate annotations for
the algorithm visualizer. The underlying gate sequence comes directly
from qcsim.qft.qft(), ensuring the visualizer stays consistent with the
reference implementation.
"""

from __future__ import annotations

import math

from typing import List, Optional, Tuple

from qcsim import QuantumCircuit
from qcsim.qft import qft


def qft_algorithm(
    num_qubits: int = 3, initial_state: Optional[str] = None
) -> Tuple[QuantumCircuit, List[str]]:
    """Build a QFT circuit and its step annotations.

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
                annotations.append(
                    f"Prepare input: flip q{q} to |1> (part of |{initial_state}>)"
                )

    before = len(qc._log)
    qft(qc, list(range(num_qubits)))

    for gate, qubits, params in qc._log[before:]:
        if gate == "H":
            annotations.append(
                f"Apply a Hadamard gate to q{qubits[0]} to create an equal superposition."
            )

        elif gate == "CP":
            control, target = qubits
            angle = params["lam"]
            denominator = round(math.pi / angle)

            annotations.append(
                f"Apply a controlled phase rotation (π/{denominator}) from q{control} "
                f"to q{target}, encoding the relative phase needed for the Fourier transform."
            )

        elif gate == "SWAP":
            q1, q2 = qubits
            annotations.append(
                f"Swap q{q1} and q{q2} to restore the standard QFT output ordering."
            )

        else:
            annotations.append("QFT gate")

    return qc, annotations