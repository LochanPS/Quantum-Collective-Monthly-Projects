"""Grover's search: find a marked state in O(sqrt(N)) oracle queries
instead of the O(N) a classical search would need.

v1 supports 2 qubits only -- a general N-qubit oracle needs a
multi-controlled-Z, which qcsim doesn't expose directly yet. Generalizing
this is a good Advanced-tier contribution (see the challenge README).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from qcsim import QuantumCircuit


def grover(
    marked_state: str = "11", iterations: Optional[int] = None
) -> Tuple[QuantumCircuit, List[str]]:
    """Build a 2-qubit Grover's search circuit and its step annotations.

    Args:
        marked_state: The 2-bit target state to search for, e.g. "11".
        iterations: Number of Grover iterations. Defaults to 1, the
            optimal count for a 2-qubit (4-state) search space.

    Returns:
        (circuit, annotations) -- annotations has exactly one entry per
        gate in circuit's log, in order.

    Raises:
        ValueError: If marked_state isn't a 2-character string of 0s/1s.
    """
    if len(marked_state) != 2 or any(b not in "01" for b in marked_state):
        raise ValueError(
            f"grover() v1 only supports 2-qubit marked states (e.g. '11'), got {marked_state!r}"
        )

    qc = QuantumCircuit(2)
    annotations: List[str] = []

    # qcsim labels bitstrings as q(n-1)...q0 (leftmost char = highest-index
    # qubit) -- reverse so target_bits[i] lines up with qubit i directly.
    target_bits = marked_state[::-1]

    def _h_both(label: str) -> None:
        for q in (0, 1):
            qc.h(q)
            annotations.append(label)

    def _x_unmarked_zeros(label: str) -> None:
        for q, bit in enumerate(target_bits):
            if bit == "0":
                qc.x(q)
                annotations.append(label)

    _h_both("Hadamard: build uniform superposition over all 4 basis states")

    if iterations is None:
        iterations = 1  # optimal: floor(pi/4 * sqrt(4)) == 1

    for _ in range(iterations):
        _x_unmarked_zeros(f"Oracle: map target |{marked_state}> onto |11> by flipping its 0-bits")
        qc.cz(0, 1)
        annotations.append(f"Oracle: phase-flip |11> -- in this basis that marks |{marked_state}>")
        _x_unmarked_zeros("Oracle: undo the flip, restoring the original basis")

        _h_both("Diffusion: Hadamard into the |+> basis")
        qc.x(0)
        annotations.append("Diffusion: X on q0")
        qc.x(1)
        annotations.append("Diffusion: X on q1")
        qc.cz(0, 1)
        annotations.append("Diffusion: phase-flip |00> (now |11> after the X's) -- inverts about the mean")
        qc.x(0)
        annotations.append("Diffusion: undo X on q0")
        qc.x(1)
        annotations.append("Diffusion: undo X on q1")
        _h_both("Diffusion: Hadamard back to the computational basis")

    return qc, annotations
