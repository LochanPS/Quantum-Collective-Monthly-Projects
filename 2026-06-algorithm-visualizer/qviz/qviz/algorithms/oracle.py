"""
Oracle utilities for Grover's search.

Currently supports the 2-qubit oracle used by Grover v1.

Designed so a future MCZ implementation can replace the CZ gate
without changing Grover itself.
"""

from __future__ import annotations

from typing import Callable

from qcsim import QuantumCircuit

from .base import PHASE_ORACLE


def apply_oracle(
    qc: QuantumCircuit,
    marked_state: str,
    add: Callable[[str, str], None],
    iteration: int | None = None,
) -> None:
    """
    Apply the Grover oracle.
    """

    tag = f"[iter {iteration}] " if iteration is not None else ""

    # qcsim labels bitstrings opposite to qubit order
    target_bits = marked_state[::-1]

    # Map target state onto |11>
    for q, bit in enumerate(target_bits):
        if bit == "0":
            qc.x(q)
            add(
                f"{tag}Oracle: flip q{q} so target maps to |11>",
                PHASE_ORACLE,
            )

    # Phase flip
    qc.cz(0, 1)
    add(
        f"{tag}Oracle: apply phase flip to |{marked_state}>",
        PHASE_ORACLE,
    )

    # Undo mapping
    for q, bit in enumerate(target_bits):
        if bit == "0":
            qc.x(q)
            add(
                f"{tag}Oracle: restore original basis",
                PHASE_ORACLE,
            )