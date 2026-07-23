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
from .diffuser import apply_diffuser
from .base import (
    PHASE_PREPARATION,
    AlgorithmResult,
    ExecutionSummary,
)


def grover(
    marked_state: str = "11",
    iterations: Optional[int] = None,
) -> AlgorithmResult:
    """Build a 2-qubit Grover search circuit."""

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
        for q in (0, 1):
            qc.h(q)
            add(note, phase)

    #
    # Preparation
    #
    h_all(
        "Hadamard: build uniform superposition -- every state starts at 25% probability",
        PHASE_PREPARATION,
    )

    if iterations is None:
        iterations = 1

    #
    # Grover iterations
    #
    for it in range(iterations):

        iteration = it + 1 if iterations > 1 else None

        apply_oracle(
            qc=qc,
            marked_state=marked_state,
            add=add,
            iteration=iteration,
        )

        apply_diffuser(
            qc=qc,
            add=add,
            iteration=iteration,
        )

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