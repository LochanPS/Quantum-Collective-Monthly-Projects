"""Deutsch-Jozsa algorithm: determine if an oracle is constant or balanced
in a single query, where a classical algorithm would need up to 2^(n-1)+1.
"""

from __future__ import annotations

from qcsim import QuantumCircuit

from .base import AlgorithmResult, input_register


def deutsch_jozsa(num_input_qubits: int = 2, oracle: str = "balanced") -> AlgorithmResult:
    """Build a Deutsch-Jozsa run.

    Args:
        num_input_qubits: Number of input qubits (the ancilla is one more).
        oracle: "constant_0" (oracle always outputs 0, does nothing),
            "constant_1" (always outputs 1, flips the ancilla
            unconditionally), or "balanced" (outputs 1 for exactly half
            the inputs, implemented as CNOT from every input to the
            ancilla).

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

    qc.x(ancilla)
    annotations.append(
        "Initialise ancilla to |1> so it starts in (|0>-|1>)/sqrt(2) after the next step"
    )

    for q in range(n + 1):
        qc.h(q)
        if q < n:
            annotations.append(f"Hadamard: input qubit q{q} enters uniform superposition")
        else:
            annotations.append("Hadamard: ancilla becomes (|0> - |1>)/sqrt(2) for phase kickback")

    if oracle == "balanced":
        for q in range(n):
            qc.cnot(q, ancilla)
            annotations.append(
                f"Oracle (balanced): CNOT(q{q} -> ancilla) -- output depends on input, kicks a phase onto q{q}"
            )
    elif oracle == "constant_1":
        qc.x(ancilla)
        annotations.append(
            "Oracle (constant-1): flip ancilla unconditionally -- same phase on every input, so no info leaks to the inputs"
        )
    # constant_0: oracle is the identity, no gates added

    for q in range(n):
        qc.h(q)
        annotations.append(
            f"Hadamard: interfere q{q} -- constant oracle refocuses it to |0>, balanced scatters it away from |0>"
        )

    def summarize(step) -> str:
        zero = "0" * n
        zero_prob = sum(
            p for s, p in step.probabilities.items() if input_register(s, n) == zero
        )
        verdict = "CONSTANT" if zero_prob > 0.5 else "BALANCED"
        detail = (
            f"input register reads all-zeros with {zero_prob * 100:.0f}% probability"
            if verdict == "CONSTANT"
            else f"input register avoids all-zeros ({(1 - zero_prob) * 100:.0f}% non-zero)"
        )
        return f"Result: the oracle is {verdict} -- {detail}. One query settled it; a classical test could need up to 2^(n-1)+1."

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Deutsch-Jozsa",
        info={
            "Oracle type": oracle,
            "Input qubits": str(n),
            "Ancilla qubit": f"q{ancilla}",
        },
        summarize=summarize,
    )
