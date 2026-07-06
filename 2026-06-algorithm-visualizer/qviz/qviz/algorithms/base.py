"""Shared return type for algorithm modules.

Each algorithm module builds a qcsim circuit and returns an
AlgorithmResult carrying everything the visualizer needs to explain it:
the circuit, one annotation per gate, a per-gate phase label (which
conceptual stage of the algorithm the gate belongs to), a human title,
an always-displayed info panel, register groupings (input / ancilla /
output), a summarize() for the plain-English answer, and an outcome()
that returns a structured measured/expected/success verdict.

Contributors adding a new algorithm return one of these. The stepper and
renderer stay algorithm-agnostic -- all algorithm-specific meaning lives
here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from qcsim import QuantumCircuit

# Canonical phase names, used for the progress indicator. Algorithms tag
# each gate with one of these (free-form strings are allowed too, but
# sticking to these keeps the progress bar consistent across algorithms).
PHASE_PREPARATION = "Preparation"
PHASE_ORACLE = "Oracle"
PHASE_DIFFUSION = "Diffusion"
PHASE_INTERFERENCE = "Interference"
PHASE_TRANSFORM = "Transform"
PHASE_MEASUREMENT = "Measurement"


@dataclass
class ExecutionSummary:
    """Structured verdict for the end-of-run summary.

    Attributes:
        measured: The meaningful register's value as read from the final
            state (the answer the algorithm produced).
        expected: What that value should be if the algorithm is correct.
        success: measured == expected.
        takeaway: One-line "what this demonstrates" note.
    """

    measured: str
    expected: str
    success: bool
    takeaway: str


@dataclass
class AlgorithmResult:
    """Everything the visualizer needs to present one algorithm run.

    Attributes:
        circuit: The built circuit, gates already applied.
        annotations: One string per gate in circuit._log order, describing
            that gate's *purpose in this algorithm* (not just its operation).
        title: Display name, e.g. "Grover's search".
        phases: One phase label per gate (parallel to annotations). Drives
            the progress indicator and the windowed circuit view. Empty
            list = no phase info (renderer falls back to plain steps).
        info: Always-displayed key facts, e.g. {"Marked state": "|11>"}.
        registers: Named qubit groups, e.g. {"input": [0, 1], "ancilla":
            [2]}. Used to label/split the state display. Empty = no split.
        summarize: Given the final Step, return the plain-English answer.
        outcome: Given the final Step, return a structured ExecutionSummary
            (measured / expected / success / takeaway).
    """

    circuit: QuantumCircuit
    annotations: List[str]
    title: str
    phases: List[str] = field(default_factory=list)
    info: Dict[str, str] = field(default_factory=dict)
    registers: Dict[str, List[int]] = field(default_factory=dict)
    summarize: Optional[Callable[["object"], str]] = None
    outcome: Optional[Callable[["object"], ExecutionSummary]] = None

    def summary(self, final_step: "object") -> str:
        if self.summarize is None:
            return ""
        return self.summarize(final_step)

    def execution_summary(self, final_step: "object") -> Optional[ExecutionSummary]:
        if self.outcome is None:
            return None
        return self.outcome(final_step)


def input_register(bitstring: str, num_input_qubits: int) -> str:
    """Extract the input-register bits from a full qcsim label.

    qcsim labels states as q(n-1)...q0 with the ancilla as the highest
    qubit (leftmost char). The input register is the rightmost
    `num_input_qubits` characters. Returned in qubit order q0..q(k-1)
    (i.e. reversed from the label's high-to-low ordering) so it reads the
    same direction the algorithm's parameters were given.

    Args:
        bitstring: Full state label, e.g. "0101" (ancilla + 3 input bits).
        num_input_qubits: How many trailing bits form the input register.

    Returns:
        The input register as a bitstring in q0..q(k-1) order.
    """
    input_part = bitstring[-num_input_qubits:]
    return input_part[::-1]
