"""Shared return type for algorithm modules.

Each algorithm module builds a qcsim circuit and returns an
AlgorithmResult carrying everything the visualizer needs to explain it:
the circuit, one annotation per gate, a human title, an always-displayed
info panel (the algorithm's defining parameters -- Grover's marked state,
BV's secret, DJ's oracle type), and a summarize() that reads the final
step and states the algorithm's answer in plain English.

Contributors adding a new algorithm return one of these. The stepper and
renderer stay algorithm-agnostic -- all algorithm-specific meaning lives
here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from qcsim import QuantumCircuit

# Imported lazily in type hints only to avoid a circular import with stepper.
Step = "qviz.stepper.Step"


@dataclass
class AlgorithmResult:
    """Everything the visualizer needs to present one algorithm run.

    Attributes:
        circuit: The built circuit, gates already applied.
        annotations: One string per gate in circuit._log order, describing
            that gate's *purpose in this algorithm* (not just its operation).
        title: Display name, e.g. "Grover's search".
        info: Always-displayed key facts, e.g. {"Marked state": "|11>"}.
            Shown on every step so the user never loses the setup context.
        summarize: Given the final Step, return a one-to-few-line plain-English
            statement of what the algorithm concluded (Balanced/Constant,
            recovered secret, target found, etc.). Defaults to a generic
            no-op if an algorithm doesn't provide one.
    """

    circuit: QuantumCircuit
    annotations: List[str]
    title: str
    info: Dict[str, str] = field(default_factory=dict)
    summarize: Optional[Callable[["Step"], str]] = None

    def summary(self, final_step: "Step") -> str:
        if self.summarize is None:
            return ""
        return self.summarize(final_step)


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
