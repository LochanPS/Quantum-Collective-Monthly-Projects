"""Bernstein-Vazirani algorithm: recover a hidden bitstring `s` from an
oracle computing f(x) = s.x (mod 2) in a single query.
"""

from __future__ import annotations

from typing import List, Tuple

from qcsim import QuantumCircuit


def bernstein_vazirani(secret: str) -> Tuple[QuantumCircuit, List[str]]:
    """Build a Bernstein-Vazirani circuit and its step annotations.

    Args:
        secret: The hidden bitstring, e.g. "101". Qubit i corresponds to
            secret[i]. After running, measuring the input qubits recovers
            this string with probability 1.

    Returns:
        (circuit, annotations) -- annotations has exactly one entry per
        gate in circuit's log, in order.

    Raises:
        ValueError: If secret is empty or contains characters other than
            "0"/"1".
    """
    if not secret or any(b not in "01" for b in secret):
        raise ValueError(f"secret must be a non-empty string of 0s and 1s, got {secret!r}")

    n = len(secret)
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

    for i, bit in enumerate(secret):
        if bit == "1":
            qc.cnot(i, ancilla)
            annotations.append(f"Oracle: secret bit {i} is 1 -> CNOT(q{i} -> ancilla) imprints a phase kick")

    for q in range(n):
        qc.h(q)
        annotations.append(f"Hadamard: interference collapses q{q} directly to secret bit {q}")

    return qc, annotations
