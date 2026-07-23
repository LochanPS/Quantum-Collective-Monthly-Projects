"""
Grover's search: find a marked state in O(sqrt(N)) oracle queries
instead of the O(N) a classical search would need.

v1 supports 2 qubits only -- a general N-qubit oracle needs a
multi-controlled-Z, which qcsim doesn't expose directly yet.
"""

from __future__ import annotations

from typing import Optional

from qcsim import QuantumCircuit

from .oracle import apply_oracle
from .base import (
    PHASE_DIFFUSION,
    PHASE_PREPARATION,
    AlgorithmResult,
    ExecutionSummary,
)


def grover(
    marked_state: str = "11",
    iterations: Optional[int] = None,
) -> AlgorithmResult:
    """Build a 2-qubit Grover search circuit.

    Args:
        marked_state:
            The target computational basis state
            (e.g. "11").

        iterations:
            Number of Grover iterations.
            Defaults to 1 which is optimal for 2 qubits.

    Returns
    -------
    AlgorithmResult
    """

    if len(marked_state) != 2 or any(bit not in "01" for bit in marked_state):
        raise ValueError(
            f"grover() v1 only supports 2-qubit marked states "
            f"(e.g. '11'), got {marked_state!r}"
        )

    qc = QuantumCircuit(2)

    annotations: list[str] = []
    phases: list[str] = []

    def add(note: str, phase: str) -> None:
        annotations.append(note)
        phases.append(phase)

    def h_all(note: str, phase: str) -> None:
        """Apply Hadamard to every qubit."""
        for q in (0, 1):
            qc.h(q)
            add(note, phase)

    #
    # State preparation
    #
    h_all(
        "Hadamard: build uniform superposition -- every state starts at 25% probability",
        PHASE_PREPARATION,
    )

    if iterations is None:
        # floor(pi/4 * sqrt(4))
        iterations = 1

    #
    # Grover iterations
    #
    for it in range(iterations):

        tag = f"[iter {it + 1}] " if iterations > 1 else ""

        #
        # Oracle
        #
        apply_oracle(
            qc=qc,
            marked_state=marked_state,
            add=add,
            iteration=it + 1 if iterations > 1 else None,
        )

        #
        # Diffusion operator
        #
        h_all(
            f"{tag}Diffusion: Hadamard into the |+> basis",
            PHASE_DIFFUSION,
        )

        qc.x(0)
        add(
            f"{tag}Diffusion: X on q0",
            PHASE_DIFFUSION,
        )

        qc.x(1)
        add(
            f"{tag}Diffusion: X on q1",
            PHASE_DIFFUSION,
        )

        qc.cz(0, 1)
        add(
            f"{tag}Diffusion: reflect amplitudes about their average -- "
            "the negative target grows, the rest shrink "
            "(amplitude amplification)",
            PHASE_DIFFUSION,
        )

        qc.x(0)
        add(
            f"{tag}Diffusion: undo X on q0",
            PHASE_DIFFUSION,
        )

        qc.x(1)
        add(
            f"{tag}Diffusion: undo X on q1",
            PHASE_DIFFUSION,
        )

        h_all(
            f"{tag}Diffusion: Hadamard back to the computational basis",
            PHASE_DIFFUSION,
        )

    #
    # Visualization summary
    #
    def summarize(step) -> str:
        top_label, top_prob = max(
            step.probabilities.items(),
            key=lambda kv: kv[1],
        )

        verdict = (
            "FOUND"
            if top_label == marked_state
            else "not yet dominant"
        )

        return (
            f"Target |{marked_state}> {verdict}: "
            f"measured |{top_label}> with "
            f"{top_prob * 100:.0f}% probability. "
            "Grover reached it in ~sqrt(4)=2 steps of work "
            "vs up to 4 classical checks."
        )

    def outcome(step) -> ExecutionSummary:
        top_label, _ = max(
            step.probabilities.items(),
            key=lambda kv: kv[1],
        )

        return ExecutionSummary(
            measured=top_label,
            expected=marked_state,
            success=(top_label == marked_state),
            takeaway=(
                "Amplitude amplification concentrates "
                "probability on the marked state "
                "in O(sqrt(N)) queries."
            ),
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
        registers={
            "search": [0, 1],
        },
        summarize=summarize,
        outcome=outcome,
    )