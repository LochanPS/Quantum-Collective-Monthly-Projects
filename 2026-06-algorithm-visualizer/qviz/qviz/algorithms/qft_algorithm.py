"""Quantum Fourier Transform, wrapping qcsim's existing qft() builder.

Per-gate annotations are derived from the gate log: qcsim's qft() emits
Hadamards, controlled-phase (CP) rotations, and SWAPs, so we label each
by type and spell out the CP rotation angle (in clean pi/n form, an idea
adopted from skgn07's PR). Naming *which* qubit-pair frequency each CP
encodes is a good Beginner-tier contribution -- see the challenge README.
"""

from __future__ import annotations

import math
from typing import Optional

from qcsim import QuantumCircuit
from qcsim.qft import qft

from .base import (
    PHASE_PREPARATION,
    PHASE_TRANSFORM,
    AlgorithmResult,
    ExecutionSummary,
)


def qft_algorithm(num_qubits: int = 3, initial_state: Optional[str] = None) -> AlgorithmResult:
    """Build a QFT run.

    Args:
        num_qubits: Number of qubits to transform.
        initial_state: Optional bitstring to prepare before the QFT.

    Returns:
        AlgorithmResult.
    """
    initial = initial_state or "0" * num_qubits
    qc = QuantumCircuit(num_qubits)
    annotations: list[str] = []
    phases: list[str] = []

    def add(note: str, phase: str) -> None:
        annotations.append(note)
        phases.append(phase)

    if initial_state:
        for q, bit in enumerate(initial_state):
            if bit == "1":
                qc.x(q)
                add(
                    f"Prepare input: flip q{q} to |1> (part of |{initial_state}>)",
                    PHASE_PREPARATION,
                )

    before = len(qc._log)
    qft(qc, list(range(num_qubits)))

    for name, qubits, params in qc._log[before:]:
        if name == "H":
            add(
                f"Hadamard on q{qubits[0]}: spreads it into equal superposition -- the coarsest frequency split",
                PHASE_TRANSFORM,
            )
        elif name in ("CP", "P"):
            lam = (params or {}).get("lam", 0.0)
            angle_str = f"pi/{round(math.pi / lam)}" if abs(lam) > 1e-12 else f"{lam:.3g} rad"
            add(
                f"Controlled-phase ({angle_str}) on q{qubits}: rotates the target's phase only when the control is |1>, "
                f"encoding a finer frequency component of the transform",
                PHASE_TRANSFORM,
            )
        elif name == "SWAP":
            add(
                f"Swap q{qubits[0]} and q{qubits[1]}: QFT outputs qubits in reversed order, this puts them back",
                PHASE_TRANSFORM,
            )
        else:
            add(f"{name} on q{qubits}: QFT sub-step", PHASE_TRANSFORM)

    def summarize(step) -> str:
        return (
            f"QFT complete: input |{initial}> is now in the Fourier basis. "
            f"Every basis state carries (near) equal magnitude -- the information has moved entirely into the phases, "
            f"which encode |{initial}>'s frequency spectrum."
        )

    def outcome(step) -> ExecutionSummary:
        # A QFT output is (for a basis-state input) a uniform-magnitude
        # superposition -- measurement gives every outcome ~equally often.
        # "Correctness" here = the magnitudes came out uniform.
        probs = list(step.probabilities.values())
        dim = 2**num_qubits
        uniform = len(probs) == dim and (max(probs) - min(probs)) < 1e-6
        return ExecutionSummary(
            measured=(
                "uniform magnitudes (info in the phases)" if uniform else "non-uniform magnitudes"
            ),
            expected="uniform magnitudes (info in the phases)",
            success=uniform,
            takeaway="The QFT moves information from amplitudes into phases -- the inverse QFT reads it back.",
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Quantum Fourier Transform",
        phases=phases,
        info={
            "Input state": f"|{initial}>",
            "Qubits": str(num_qubits),
        },
        registers={"qubits": list(range(num_qubits))},
        summarize=summarize,
        outcome=outcome,
    )
