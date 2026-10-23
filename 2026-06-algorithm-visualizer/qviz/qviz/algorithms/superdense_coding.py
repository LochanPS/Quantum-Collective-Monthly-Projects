"""Superdense coding: send two classical bits by transmitting one qubit.

Alice and Bob share a Bell pair ahead of time. Alice encodes a 2-bit
message by applying I, X, Z or ZX to *her* qubit only, then sends that one
qubit to Bob. Bob undoes the entanglement (CNOT then H) and reads both
bits with certainty.

Qubit roles: q0 is Alice's half of the pair (the one that gets sent),
q1 is Bob's half. The message is written the way qcsim labels states
(q1 q0), so the state Bob ends up with reads exactly as the message:
the left bit comes from Alice's X, the right bit from her Z.
"""

from __future__ import annotations

from qcsim import QuantumCircuit

from .base import PHASE_INTERFERENCE, PHASE_PREPARATION, AlgorithmResult, ExecutionSummary

PHASE_ENCODING = "Encoding"

_ENCODING_NAME = {"00": "I", "10": "X", "01": "Z", "11": "ZX"}


def superdense_coding(message: str = "10") -> AlgorithmResult:
    """Build a superdense-coding run.

    Args:
        message: The two classical bits Alice sends, e.g. "10". The left bit
            is carried by an X on Alice's qubit, the right bit by a Z. Bob's
            final state label equals this string.

    Returns:
        AlgorithmResult.

    Raises:
        ValueError: If message is not exactly two characters of 0/1.
    """
    if len(message) != 2 or any(b not in "01" for b in message):
        raise ValueError(f"message must be two bits like '10', got {message!r}")

    alice, bob = 0, 1
    x_bit, z_bit = message[0], message[1]
    qc = QuantumCircuit(2)
    annotations: list[str] = []
    phases: list[str] = []

    def add(note: str, phase: str) -> None:
        annotations.append(note)
        phases.append(phase)

    qc.h(alice)
    add("Hadamard on Alice's qubit q0: start building the shared Bell pair", PHASE_PREPARATION)
    qc.cnot(alice, bob)
    add(
        "CNOT(q0 -> q1): Alice and Bob now share (|00> + |11>)/sqrt(2); "
        "neither qubit alone holds any information",
        PHASE_PREPARATION,
    )

    if x_bit == "0" and z_bit == "0":
        qc.i(alice)
        add("Message 00: Alice leaves her qubit alone (identity)", PHASE_ENCODING)
    if x_bit == "1":
        qc.x(alice)
        add(
            "Left bit is 1: Alice applies X to her qubit only, flipping which pair of "
            "states is entangled",
            PHASE_ENCODING,
        )
    if z_bit == "1":
        qc.z(alice)
        add(
            "Right bit is 1: Alice applies Z to her qubit only, flipping the sign between "
            "the two entangled states",
            PHASE_ENCODING,
        )

    qc.cnot(alice, bob)
    add(
        "Bob receives q0 and applies CNOT(q0 -> q1): q1 now holds the left bit directly",
        PHASE_INTERFERENCE,
    )
    qc.h(alice)
    add(
        "Hadamard on q0: the sign Alice's Z added becomes a definite 0/1 on q0, "
        "so both bits are now readable",
        PHASE_INTERFERENCE,
    )

    def _decoded(step) -> str:
        top_label, _ = max(step.probabilities.items(), key=lambda kv: kv[1])
        return top_label

    def summarize(step) -> str:
        decoded = _decoded(step)
        _, top_prob = max(step.probabilities.items(), key=lambda kv: kv[1])
        match = "matches Alice's message" if decoded == message else f"MISMATCH vs {message}"
        return (
            f"Bob decoded {decoded} ({match}) with {top_prob * 100:.0f}% probability. "
            "Two classical bits arrived by sending a single qubit."
        )

    def outcome(step) -> ExecutionSummary:
        decoded = _decoded(step)
        return ExecutionSummary(
            measured=decoded,
            expected=message,
            success=decoded == message,
            takeaway="One transmitted qubit + prior shared entanglement carried two classical bits.",
        )

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="Superdense coding",
        phases=phases,
        info={
            "Message": message,
            "Alice's encoding": _ENCODING_NAME[message],
            "Alice's qubit (sent)": f"q{alice}",
            "Bob's qubit (kept)": f"q{bob}",
        },
        registers={"qubits": [alice, bob]},
        summarize=summarize,
        outcome=outcome,
    )
