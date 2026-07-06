"""Deutsch-Jozsa algorithm: determine if an oracle is constant or balanced
in a single query, where a classical algorithm would need up to 2^(n-1)+1.
"""

from __future__ import annotations

from qcsim import QuantumCircuit

from .base import (
    PHASE_INTERFERENCE,
    PHASE_ORACLE,
    PHASE_PREPARATION,
    AlgorithmResult,
    ExecutionSummary,
    input_register,
)


def deutsch_jozsa(num_input_qubits: int = 2, oracle: str = "balanced") -> AlgorithmResult:
    """Build a Deutsch-Jozsa run.

    Args:
        num_input_qubits: Number of input qubits (the ancilla is one more).
        oracle: "constant_0", "constant_1", or "balanced".

    Returns:
        AlgorithmResult.

    Raises:
        ValueError: If oracle is not one of the three supported kinds.
    """
    if oracle not in ("constant_0", "constant_1", "balanced"):
        raise ValueError(
            f"oracle must be 'constant_0', 'constant_1', or 'balanced', got {oracle!r}"
        )

    n = num_input_qubits
    ancilla = n
    qc = QuantumCircuit(n + 1)
    annotations: list[str] = []
    phases: list[str] = []

    def add(note: str, phase: str) -> None:
        annotations.append(note)
        phases.append(phase)

    qc.x(ancilla)
    add(
        "Initialise ancilla to |1> so it starts in (|0>-|1>)/sqrt(2) after the next step",
        PHASE_PREPARATION,
    )

    for q in range(n + 1):
        qc.h(q)
        if q < n:
            add(f"Hadamard: input qubit q{q} enters uniform superposition", PHASE_PREPARATION)
        else:
            add(
                "Hadamard: ancilla becomes (|0> - |1>)/sqrt(2) for phase kickback",
                PHASE_PREPARATION,
            )

    if oracle == "balanced":
        for q in range(n):
            qc.cnot(q, ancilla)
            add(
                f"Oracle (balanced): CNOT(q{q} -> ancilla) -- output depends on input, kicks a phase onto q{q}",
                PHASE_ORACLE,
            )
    elif oracle == "constant_1":
        qc.x(ancilla)
        add(
            "Oracle (constant-1): flip ancilla unconditionally -- same phase on every input, so no info leaks to the inputs",
            PHASE_ORACLE,
        )
    # constant_0: identity oracle, no gates. Still counts as the Oracle phase
    # conceptually, but there's nothing to render.

    for q in range(n):
        qc.h(q)
        add(
            f"Hadamard: interfere q{q} -- constant oracle refocuses it to |0>, balanced scatters it away from |0>",
            PHASE_INTERFERENCE,
        )

    expected_class = "CONSTANT" if oracle.startswith("constant") else "BALANCED"

    def _measured_class(step) -> str:
        zero = "0" * n
        zero_prob = sum(p for s, p in step.probabilities.items() if input_register(s, n) == zero)
        return "CONSTANT" if zero_prob > 0.5 else "BALANCED"

    def summarize(step) -> str:
        verdict = _measured_class(step)
        zero = "0" * n
        zero_prob = sum(p for s, p in step.probabilities.items() if input_register(s, n) == zero)
        detail = (
            f"input register reads all-zeros with {zero_prob * 100:.0f}% probability"
            if verdict == "CONSTANT"
            else f"input register avoids all-zeros ({(1 - zero_prob) * 100:.0f}% non-zero)"
        )
        return f"Result: the oracle is {verdict} -- {detail}."

    def outcome(step) -> ExecutionSummary:
        measured = _measured_class(step)
        return ExecutionSummary(
            measured=measured,
            expected=expected_class,
            success=measured == expected_class,
            takeaway="One oracle query classifies it; a classical test could need up to 2^(n-1)+1 queries.",
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Deutsch-Jozsa",
        phases=phases,
        info={
            "Oracle type": oracle,
            "Input qubits": str(n),
            "Ancilla qubit": f"q{ancilla}",
        },
        registers={"input": list(range(n)), "ancilla": [ancilla]},
        summarize=summarize,
        outcome=outcome,
    )
