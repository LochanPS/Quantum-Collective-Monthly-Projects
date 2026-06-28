"""Replay a qcsim QuantumCircuit gate-by-gate, snapshotting state at every step.

A QuantumCircuit only exposes its final state by default -- this module
re-runs the circuit's gate log on a fresh state, one gate at a time, so
each intermediate step can be inspected and rendered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from qcsim import QuantumCircuit


@dataclass
class Step:
    """Snapshot of the circuit state immediately after applying one gate.

    Attributes:
        index: Position in the gate sequence (0-indexed). BARRIER entries
            are not assigned a step -- they're skipped during replay since
            they have no effect on the state.
        gate_name: Gate name as stored in the circuit's log (e.g. "H", "CNOT").
        qubits: Qubit indices the gate acted on.
        params: Gate parameters (e.g. {"theta": 0.5}), or None.
        statevector: Full state vector immediately after this gate.
        probabilities: |amplitude|^2 per basis state, keyed by bitstring.
        annotation: Human-readable description of what this step does,
            filled in by algorithm modules -- empty by default since the
            stepper itself has no notion of algorithm-level meaning.
    """

    index: int
    gate_name: str
    qubits: List[int]
    params: Optional[dict]
    statevector: np.ndarray
    probabilities: Dict[str, float]
    annotation: str = field(default="")


def apply_log_entry(
    working: QuantumCircuit, name: str, qubits: List[int], params: Optional[dict]
) -> bool:
    """Apply one (name, qubits, params) log entry to `working` in place.

    Shared by the stepper and by anything that needs to rebuild a partial
    circuit up to some step (e.g. rendering a circuit diagram that only
    shows gates applied so far).

    Returns:
        True if a step should be recorded for this entry, False if it was
        a no-op for visualization purposes (currently only BARRIER).
    """
    if name == "BARRIER":
        return False
    elif name == "MEASURE":
        working.measure(qubits[0])
    elif name == "RESET":
        working.reset(qubits[0] if qubits else None)
    else:
        working._replay_gate(name, qubits, params)
    return True


def step_through(circuit: QuantumCircuit) -> List[Step]:
    """Replay a circuit's gate log, returning one Step per applied gate.

    Args:
        circuit: A QuantumCircuit that has already had gates applied to it.
            This circuit is read-only here -- a fresh circuit is built and
            replayed instead, so the original's state is untouched.

    Returns:
        List of Step records, one per non-barrier gate, in execution order.
        The last step's statevector matches `circuit.statevector()` exactly
        (replay uses the same gate dispatch the circuit itself used).
    """
    working = QuantumCircuit(circuit.num_qubits, backend=circuit.backend)
    steps: List[Step] = []

    for name, qubits, params in circuit._log:
        if not apply_log_entry(working, name, list(qubits), params):
            continue  # BARRIER -- no state effect, nothing to snapshot

        steps.append(
            Step(
                index=len(steps),
                gate_name=name,
                qubits=list(qubits),
                params=params,
                statevector=working.statevector(),
                probabilities=working.probabilities(),
            )
        )

    return steps
