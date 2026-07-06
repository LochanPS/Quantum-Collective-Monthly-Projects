"""Grover's search: find a marked state in O(sqrt(N)) oracle queries
instead of the O(N) a classical search would need.

v1 supports 2 qubits only -- a general N-qubit oracle needs a
multi-controlled-Z, which qcsim doesn't expose directly yet. Generalizing
this is a good Advanced-tier contribution (see the challenge README).
"""

from __future__ import annotations

from typing import Optional

from qcsim import QuantumCircuit

from .base import AlgorithmResult


def grover(marked_state: str = "11", iterations: Optional[int] = None) -> AlgorithmResult:
    """Build a 2-qubit Grover's search run.

    Args:
        marked_state: The 2-bit target state to search for, e.g. "11".
        iterations: Number of Grover iterations. Defaults to 1, the
            optimal count for a 2-qubit (4-state) search space.

    Returns:
        AlgorithmResult.

    Raises:
        ValueError: If marked_state isn't a 2-character string of 0s/1s.
    """
    if len(marked_state) != 2 or any(b not in "01" for b in marked_state):
        raise ValueError(
            f"grover() v1 only supports 2-qubit marked states (e.g. '11'), got {marked_state!r}"
        )

    qc = QuantumCircuit(2)
    annotations: list[str] = []

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

    _h_both("Hadamard: build uniform superposition -- every state starts at 25% probability")

    if iterations is None:
        iterations = 1  # optimal: floor(pi/4 * sqrt(4)) == 1

    for it in range(iterations):
        tag = f"[iter {it + 1}] " if iterations > 1 else ""
        _x_unmarked_zeros(f"{tag}Oracle: map target |{marked_state}> onto |11> by flipping its 0-bits")
        qc.cz(0, 1)
        annotations.append(
            f"{tag}Oracle: phase-flip the target -- it now has a negative amplitude, invisible to probability but visible to interference"
        )
        _x_unmarked_zeros(f"{tag}Oracle: undo the flip, restoring the original basis")

        _h_both(f"{tag}Diffusion: Hadamard into the |+> basis")
        qc.x(0)
        annotations.append(f"{tag}Diffusion: X on q0")
        qc.x(1)
        annotations.append(f"{tag}Diffusion: X on q1")
        qc.cz(0, 1)
        annotations.append(
            f"{tag}Diffusion: reflect all amplitudes about their average -- the negative target grows, the rest shrink (amplitude amplification)"
        )
        qc.x(0)
        annotations.append(f"{tag}Diffusion: undo X on q0")
        qc.x(1)
        annotations.append(f"{tag}Diffusion: undo X on q1")
        _h_both(f"{tag}Diffusion: Hadamard back to the computational basis")

    def summarize(step) -> str:
        top_label, top_prob = max(step.probabilities.items(), key=lambda kv: kv[1])
        found = top_label == marked_state
        verdict = "FOUND" if found else "not yet dominant"
        return (
            f"Target |{marked_state}> {verdict}: measured |{top_label}> with {top_prob * 100:.0f}% probability. "
            f"Grover reached it in ~sqrt(4)=2 steps of work vs up to 4 classical checks."
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Grover's search",
        info={
            "Marked state": f"|{marked_state}>",
            "Iterations": str(iterations),
            "Search space": "4 states (2 qubits)",
        },
        summarize=summarize,
    )
