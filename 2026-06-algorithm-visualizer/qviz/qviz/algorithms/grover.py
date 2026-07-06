"""Grover's search: find a marked state in O(sqrt(N)) oracle queries
instead of the O(N) a classical search would need.

v1 supports 2 qubits only -- a general N-qubit oracle needs a
multi-controlled-Z, which qcsim doesn't expose directly yet. Generalizing
this is a good Advanced-tier contribution (see the challenge README).
"""

from __future__ import annotations

from typing import Optional

from qcsim import QuantumCircuit

from .base import (
    PHASE_DIFFUSION,
    PHASE_ORACLE,
    PHASE_PREPARATION,
    AlgorithmResult,
    ExecutionSummary,
)


def grover(marked_state: str = "11", iterations: Optional[int] = None) -> AlgorithmResult:
    """Build a 2-qubit Grover's search run.

    Args:
        marked_state: The 2-bit target state to search for, e.g. "11".
        iterations: Number of Grover iterations. Defaults to 1 (optimal
            for a 2-qubit / 4-state search space).

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
    phases: list[str] = []

    def add(note: str, phase: str) -> None:
        annotations.append(note)
        phases.append(phase)

    # qcsim labels bitstrings as q(n-1)...q0 (leftmost = highest qubit) --
    # reverse so target_bits[i] lines up with qubit i directly.
    target_bits = marked_state[::-1]

    def _h_both(note: str, phase: str) -> None:
        for q in (0, 1):
            qc.h(q)
            add(note, phase)

    def _x_zeros(note: str, phase: str) -> None:
        for q, bit in enumerate(target_bits):
            if bit == "0":
                qc.x(q)
                add(note, phase)

    _h_both(
        "Hadamard: build uniform superposition -- every state starts at 25% probability",
        PHASE_PREPARATION,
    )

    if iterations is None:
        iterations = 1  # optimal: floor(pi/4 * sqrt(4)) == 1

    for it in range(iterations):
        tag = f"[iter {it + 1}] " if iterations > 1 else ""
        _x_zeros(
            f"{tag}Oracle: map target |{marked_state}> onto |11> by flipping its 0-bits",
            PHASE_ORACLE,
        )
        qc.cz(0, 1)
        add(
            f"{tag}Oracle: phase-flip the target -- negative amplitude now, invisible to probability but visible to interference",
            PHASE_ORACLE,
        )
        _x_zeros(f"{tag}Oracle: undo the flip, restoring the original basis", PHASE_ORACLE)

        _h_both(f"{tag}Diffusion: Hadamard into the |+> basis", PHASE_DIFFUSION)
        qc.x(0)
        add(f"{tag}Diffusion: X on q0", PHASE_DIFFUSION)
        qc.x(1)
        add(f"{tag}Diffusion: X on q1", PHASE_DIFFUSION)
        qc.cz(0, 1)
        add(
            f"{tag}Diffusion: reflect amplitudes about their average -- the negative target grows, the rest shrink (amplitude amplification)",
            PHASE_DIFFUSION,
        )
        qc.x(0)
        add(f"{tag}Diffusion: undo X on q0", PHASE_DIFFUSION)
        qc.x(1)
        add(f"{tag}Diffusion: undo X on q1", PHASE_DIFFUSION)
        _h_both(f"{tag}Diffusion: Hadamard back to the computational basis", PHASE_DIFFUSION)

    def summarize(step) -> str:
        top_label, top_prob = max(step.probabilities.items(), key=lambda kv: kv[1])
        verdict = "FOUND" if top_label == marked_state else "not yet dominant"
        return (
            f"Target |{marked_state}> {verdict}: measured |{top_label}> with {top_prob * 100:.0f}% probability. "
            f"Grover reached it in ~sqrt(4)=2 steps of work vs up to 4 classical checks."
        )

    def outcome(step) -> ExecutionSummary:
        top_label, _ = max(step.probabilities.items(), key=lambda kv: kv[1])
        return ExecutionSummary(
            measured=top_label,
            expected=marked_state,
            success=top_label == marked_state,
            takeaway="Amplitude amplification concentrates probability on the marked state in O(sqrt(N)) queries.",
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Grover's search",
        phases=phases,
        info={
            "Marked state": f"|{marked_state}>",
            "Iterations": str(iterations),
            "Search space": "4 states (2 qubits)",
        },
        registers={"search": [0, 1]},
        summarize=summarize,
        outcome=outcome,
    )
