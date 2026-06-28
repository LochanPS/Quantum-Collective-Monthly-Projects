"""Deutsch-Jozsa algorithm: determine if an oracle is constant or balanced
in a single query, where a classical algorithm would need up to 2^(n-1)+1.
"""

from __future__ import annotations

from typing import List, Tuple

from qcsim import QuantumCircuit


def deutsch_jozsa(
    num_input_qubits: int = 1, oracle: str = "balanced"
) -> Tuple[QuantumCircuit, List[str]]:
    """Build a Deutsch-Jozsa circuit and its step annotations.

    Args:
        num_input_qubits: Number of input qubits (the ancilla is one more).
        oracle: "constant_0" (oracle always outputs 0, does nothing),
            "constant_1" (always outputs 1, flips the ancilla
            unconditionally), or "balanced" (outputs 1 for exactly half
            the inputs, implemented as CNOT from every input to the
            ancilla).

    Returns:
        (circuit, annotations) -- annotations has exactly one entry per
        gate in circuit's log, in order.

    Raises:
        ValueError: If oracle is not one of the three supported kinds.
    """
    if oracle not in ("constant_0", "constant_1", "balanced"):
        raise ValueError(f"oracle must be 'constant_0', 'constant_1', or 'balanced', got {oracle!r}")

    n = num_input_qubits
    ancilla = n
    qc = QuantumCircuit(n + 1)
    annotations: List[str] = []

    qc.x(ancilla)
    annotations.append("Initialise ancilla to |1> so it starts in (|0>-|1>)/sqrt(2) after the next step")

    for q in range(n + 1):
        qc.h(q)
        if q < n:
            annotations.append(f"Hadamard: input qubit q{q} enters uniform superposition")
        else:
            annotations.append("Hadamard: ancilla becomes (|0> - |1>)/sqrt(2)")

    if oracle == "balanced":
        for q in range(n):
            qc.cnot(q, ancilla)
            annotations.append(f"Oracle (balanced): CNOT(q{q} -> ancilla) -- output depends on input")
    elif oracle == "constant_1":
        qc.x(ancilla)
        annotations.append("Oracle (constant-1): flip ancilla unconditionally -- output ignores input")
    # constant_0: oracle is the identity, no gates added

    for q in range(n):
        qc.h(q)
        annotations.append(
            f"Hadamard: interfere q{q} -- constant oracle leaves it at |0>, balanced leaves it away from |0>"
        )

    return qc, annotations
