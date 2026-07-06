"""Quantum Fourier Transform, wrapping qcsim's existing qft() builder.

Per-gate annotations are derived from the gate log: qcsim's qft() emits
Hadamards, controlled-phase (CP) rotations, and SWAPs, so we label each
by type and, for CP gates, spell out the rotation angle. Making these
even more precise (which qubit-pair frequency each CP encodes) is a good
Beginner-tier contribution -- see the challenge README.
"""

from __future__ import annotations

import math
from typing import Optional

from qcsim import QuantumCircuit
from qcsim.qft import qft

from .base import AlgorithmResult


def qft_algorithm(num_qubits: int = 3, initial_state: Optional[str] = None) -> AlgorithmResult:
    """Build a QFT run.

    Args:
        num_qubits: Number of qubits to transform.
        initial_state: Optional bitstring to prepare before the QFT, e.g.
            "101". Defaults to |0...0>.

    Returns:
        AlgorithmResult.
    """
    initial = initial_state or "0" * num_qubits
    qc = QuantumCircuit(num_qubits)
    annotations: list[str] = []

    if initial_state:
        for q, bit in enumerate(initial_state):
            if bit == "1":
                qc.x(q)
                annotations.append(f"Prepare input: flip q{q} to |1> (part of |{initial_state}>)")

    before = len(qc._log)
    qft(qc, list(range(num_qubits)))

    # Annotate the QFT gates by reading the log entries qft() just appended.
    for name, qubits, params in qc._log[before:]:
        if name == "H":
            annotations.append(
                f"Hadamard on q{qubits[0]}: spreads it into equal superposition -- the coarsest frequency split"
            )
        elif name in ("CP", "P"):
            lam = (params or {}).get("lam", 0.0)
            frac = lam / math.pi
            annotations.append(
                f"Controlled-phase ({frac:.3g}*pi rad) on q{qubits}: rotates the target's phase only when the control is |1>, "
                f"encoding a finer frequency component"
            )
        elif name == "SWAP":
            annotations.append(
                f"Swap q{qubits[0]} and q{qubits[1]}: QFT outputs qubits in reversed order, this puts them back"
            )
        else:
            annotations.append(f"{name} on q{qubits}: QFT sub-step")

    def summarize(step) -> str:
        return (
            f"QFT complete: input |{initial}> is now in the Fourier basis. "
            f"Every basis state carries (near) equal magnitude -- the information has moved entirely into the phases, "
            f"which encode |{initial}>'s frequency spectrum."
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Quantum Fourier Transform",
        info={
            "Input state": f"|{initial}>",
            "Qubits": str(num_qubits),
        },
        summarize=summarize,
    )
