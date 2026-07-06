"""Bernstein-Vazirani algorithm: recover a hidden bitstring `s` from an
oracle computing f(x) = s.x (mod 2) in a single query.
"""

from __future__ import annotations

from qcsim import QuantumCircuit

from .base import AlgorithmResult, input_register


def bernstein_vazirani(secret: str) -> AlgorithmResult:
    """Build a Bernstein-Vazirani run.

    Args:
        secret: The hidden bitstring, e.g. "101". Qubit i corresponds to
            secret[i]. After running, measuring the input qubits recovers
            this string with probability 1.

    Returns:
        AlgorithmResult.

    Raises:
        ValueError: If secret is empty or contains characters other than
            "0"/"1".
    """
    if not secret or any(b not in "01" for b in secret):
        raise ValueError(f"secret must be a non-empty string of 0s and 1s, got {secret!r}")

    n = len(secret)
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

    for i, bit in enumerate(secret):
        if bit == "1":
            qc.cnot(i, ancilla)
            annotations.append(
                f"Oracle: secret bit {i} is 1 -> CNOT(q{i} -> ancilla) kicks a phase onto q{i}, tagging it"
            )

    for q in range(n):
        qc.h(q)
        annotations.append(
            f"Hadamard: interference collapses q{q} straight onto secret bit {q} -- no guessing needed"
        )

    def summarize(step) -> str:
        top_label, top_prob = max(step.probabilities.items(), key=lambda kv: kv[1])
        recovered = input_register(top_label, n)  # q0..q(n-1), same order as `secret`
        match = "matches the hidden string" if recovered == secret else f"MISMATCH vs {secret}"
        return (
            f"Recovered secret: {recovered} ({match}), read out with {top_prob * 100:.0f}% probability. "
            f"One query did it; classically you'd need {n} queries (one per bit)."
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Bernstein-Vazirani",
        info={
            "Hidden secret": secret,
            "Secret length": str(n),
            "Ancilla qubit": f"q{ancilla}",
        },
        summarize=summarize,
    )
