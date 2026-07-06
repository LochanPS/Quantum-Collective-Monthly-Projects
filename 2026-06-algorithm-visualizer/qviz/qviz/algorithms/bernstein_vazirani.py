"""Bernstein-Vazirani algorithm: recover a hidden bitstring `s` from an
oracle computing f(x) = s.x (mod 2) in a single query.
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


def bernstein_vazirani(secret: str) -> AlgorithmResult:
    """Build a Bernstein-Vazirani run.

    Args:
        secret: The hidden bitstring, e.g. "101". Qubit i corresponds to
            secret[i]. Measuring the input qubits recovers it exactly.

    Returns:
        AlgorithmResult.

    Raises:
        ValueError: If secret is empty or contains characters other than 0/1.
    """
    if not secret or any(b not in "01" for b in secret):
        raise ValueError(f"secret must be a non-empty string of 0s and 1s, got {secret!r}")

    n = len(secret)
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

    for i, bit in enumerate(secret):
        if bit == "1":
            qc.cnot(i, ancilla)
            add(
                f"Oracle: secret bit {i} is 1 -> CNOT(q{i} -> ancilla) kicks a phase onto q{i}, tagging it",
                PHASE_ORACLE,
            )

    for q in range(n):
        qc.h(q)
        add(
            f"Hadamard: interference collapses q{q} straight onto secret bit {q} -- no guessing needed",
            PHASE_INTERFERENCE,
        )

    def _recovered(step) -> str:
        top_label, _ = max(step.probabilities.items(), key=lambda kv: kv[1])
        return input_register(top_label, n)

    def summarize(step) -> str:
        recovered = _recovered(step)
        _, top_prob = max(step.probabilities.items(), key=lambda kv: kv[1])
        match = "matches the hidden string" if recovered == secret else f"MISMATCH vs {secret}"
        return (
            f"Recovered secret: {recovered} ({match}), read out with {top_prob * 100:.0f}% probability. "
            f"One query did it; classically you'd need {n} queries (one per bit)."
        )

    def outcome(step) -> ExecutionSummary:
        recovered = _recovered(step)
        return ExecutionSummary(
            measured=recovered,
            expected=secret,
            success=recovered == secret,
            takeaway=f"Recovered the {n}-bit secret in a single query vs {n} classical queries.",
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Bernstein-Vazirani",
        phases=phases,
        info={
            "Hidden secret": secret,
            "Secret length": str(n),
            "Ancilla qubit": f"q{ancilla}",
        },
        registers={"input": list(range(n)), "ancilla": [ancilla]},
        summarize=summarize,
        outcome=outcome,
    )
