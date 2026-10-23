"""
Diffusion operator for Grover's search.

Currently supports the 2-qubit implementation.

Designed so future N-qubit diffusion operators can be implemented
without modifying grover.py.
"""

from __future__ import annotations

from typing import Callable

from qcsim import QuantumCircuit

from .base import PHASE_DIFFUSION


def apply_diffuser(
    qc: QuantumCircuit,
    add: Callable[[str, str], None],
    iteration: int | None = None,
) -> None:
    """Apply the 2-qubit Grover diffusion operator."""

    tag = f"[iter {iteration}] " if iteration is not None else ""

    # Hadamard into |+> basis
    for q in (0, 1):
        qc.h(q)
        add(
            f"{tag}Diffusion: Hadamard into the |+> basis",
            PHASE_DIFFUSION,
        )

    # X gates
    qc.x(0)
    add(f"{tag}Diffusion: X on q0", PHASE_DIFFUSION)

    qc.x(1)
    add(f"{tag}Diffusion: X on q1", PHASE_DIFFUSION)

    # Reflection
    qc.cz(0, 1)
    add(
        f"{tag}Diffusion: reflect amplitudes about their average -- "
        "the negative target grows, the rest shrink "
        "(amplitude amplification)",
        PHASE_DIFFUSION,
    )

    # Undo X
    qc.x(0)
    add(f"{tag}Diffusion: undo X on q0", PHASE_DIFFUSION)

    qc.x(1)
    add(f"{tag}Diffusion: undo X on q1", PHASE_DIFFUSION)

    # Return to computational basis
    for q in (0, 1):
        qc.h(q)
        add(
            f"{tag}Diffusion: Hadamard back to the computational basis",
            PHASE_DIFFUSION,
        )