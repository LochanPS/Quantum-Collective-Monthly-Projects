"""
Oracle utilities for Grover's search.

Currently supports the 2-qubit oracle used by Grover v1.

Designed so a future MCZ implementation can replace the CZ gate
without changing Grover itself.
"""

from __future__ import annotations

from qcsim import QuantumCircuit

from .base import PHASE_ORACLE


def apply_oracle(
    qc: QuantumCircuit,
    marked_state: str,
    annotations: list[str],
    phases: list[str],
    iteration: int | None = None,
) -> None:
    """
    Apply the Grover oracle.

    The marked state receives a phase flip.

    Parameters
    ----------
    qc
        Quantum circuit.

    marked_state
        Bitstring to mark.

    annotations
        Visualization annotations.

    phases
        Phase labels.

    iteration
        Optional iteration number for annotation.
    """

    tag = ""
    if iteration is not None:
        tag = f"[iter {iteration}] "

    # qcsim labels qubits opposite to string order
    target_bits = marked_state[::-1]

    #
    # Map target state onto |11>
    #
    for q, bit in enumerate(target_bits):
        if bit == "0":
            qc.x(q)
            annotations.append(
                f"{tag}Oracle: flip q{q} so target maps to |11>"
            )
            phases.append(PHASE_ORACLE)

    #
    # Phase flip
    #
    qc.cz(0, 1)

    annotations.append(
        f"{tag}Oracle: apply phase flip to |{marked_state}>"
    )
    phases.append(PHASE_ORACLE)

    #
    # Undo mapping
    #
    for q, bit in enumerate(target_bits):
        if bit == "0":
            qc.x(q)
            annotations.append(
                f"{tag}Oracle: restore original basis"
            )
            phases.append(PHASE_ORACLE)