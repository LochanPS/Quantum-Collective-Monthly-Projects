"""Density-matrix evolution engine.

Takes a qcsim circuit's gate log and replays it onto a density matrix. In this
phase the engine is *noiseless* — it exists to prove one thing: with no noise,
qnoise reproduces qcsim's exact result. That parity is the credibility anchor
for everything the noise model layers on top later.

How a gate's full-system unitary is obtained
--------------------------------------------
Rather than re-derive Kronecker/controlled-gate embedding (qcsim already does
this, correctly, and is the source of truth), we read each gate's full 2^N x 2^N
unitary straight out of qcsim: apply the gate to every basis state |j> and
collect the resulting state vectors as the columns of U. By construction this
matches qcsim's gate action bit-for-bit.
"""

from __future__ import annotations

from functools import reduce
from typing import List, Optional

import numpy as np
from qcsim import QuantumCircuit

from .channels import NoiseChannel
from .density import DensityMatrix

_I2 = np.eye(2, dtype=complex)

# Gate-name -> how to apply it to a qcsim circuit. Mirrors qcsim's own
# _replay_gate dispatch so we cover exactly the names that appear in qc._log.
_APPLY = {
    "I": lambda qc, q, p: qc.i(q[0]),
    "H": lambda qc, q, p: qc.h(q[0]),
    "X": lambda qc, q, p: qc.x(q[0]),
    "Y": lambda qc, q, p: qc.y(q[0]),
    "Z": lambda qc, q, p: qc.z(q[0]),
    "S": lambda qc, q, p: qc.s(q[0]),
    "Sdg": lambda qc, q, p: qc.sdg(q[0]),
    "T": lambda qc, q, p: qc.t(q[0]),
    "Tdg": lambda qc, q, p: qc.tdg(q[0]),
    "SX": lambda qc, q, p: qc.sx(q[0]),
    "SXdg": lambda qc, q, p: qc.sxdg(q[0]),
    "Rx": lambda qc, q, p: qc.rx(q[0], p["theta"]),
    "Ry": lambda qc, q, p: qc.ry(q[0], p["theta"]),
    "Rz": lambda qc, q, p: qc.rz(q[0], p["theta"]),
    "P": lambda qc, q, p: qc.p(q[0], p["lam"]),
    "U": lambda qc, q, p: qc.u(q[0], p["theta"], p["phi"], p["lam"]),
    "CNOT": lambda qc, q, p: qc.cnot(q[0], q[1]),
    "CY": lambda qc, q, p: qc.cy(q[0], q[1]),
    "CZ": lambda qc, q, p: qc.cz(q[0], q[1]),
    "SWAP": lambda qc, q, p: qc.swap(q[0], q[1]),
    "CP": lambda qc, q, p: qc.cp(q[0], q[1], p["lam"]),
    "CCX": lambda qc, q, p: qc.toffoli(q[0], q[1], q[2]),
}

# Operations in the log with no unitary. BARRIER is a pure marker; MEASURE is a
# non-collapsing sampling point in qcsim (sampling is done separately, via
# qnoise.measure), so both are skipped during evolution. RESET is not unitary
# but *is* a physical operation on rho, handled explicitly below.
_SKIP = {"BARRIER", "MEASURE"}

# Kraus operators that reset a single qubit to |0> regardless of input:
#   K0 = |0><0|, K1 = |0><1|.  (K0^dag K0 + K1^dag K1 = I, trace preserving.)
_RESET_KRAUS = [
    np.array([[1, 0], [0, 0]], dtype=complex),
    np.array([[0, 1], [0, 0]], dtype=complex),
]


def _apply_reset(dm: DensityMatrix, qubit: int) -> None:
    """Reset ``qubit`` to |0> in place via the reset Kraus channel."""
    rho = dm.matrix()
    new_rho = np.zeros_like(rho)
    for k in _RESET_KRAUS:
        K = embed_single(k, qubit, dm.num_qubits)
        new_rho += K @ rho @ K.conj().T
    dm.set(new_rho)


def gate_unitary(
    name: str,
    qubits: List[int],
    params: Optional[dict],
    num_qubits: int,
) -> np.ndarray:
    """Return the full 2^N x 2^N unitary for one logged gate, via qcsim.

    Args:
        name: Gate name as stored in ``qcsim`` gate logs (e.g. "H", "CNOT").
        qubits: Qubit indices the gate acts on (LSB convention).
        params: Parameter dict (e.g. ``{"theta": 0.5}``) or None.
        num_qubits: Total qubits in the system.

    Returns:
        A (2^N, 2^N) complex unitary matrix acting on the whole system.

    Raises:
        KeyError: If ``name`` is not a known unitary gate.
    """
    if name not in _APPLY:
        raise KeyError(f"unknown or non-unitary gate {name!r}")
    dim = 2**num_qubits
    p = params or {}
    U = np.zeros((dim, dim), dtype=complex)
    probe = QuantumCircuit(num_qubits)
    for j in range(dim):
        col = np.zeros(dim, dtype=complex)
        col[j] = 1.0
        probe._state.set(col)  # seed |j>
        _APPLY[name](probe, qubits, p)  # apply the single gate
        U[:, j] = probe._state.amplitudes()  # read the resulting column
    return U


def embed_single(op: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
    """Embed a 2x2 operator on ``qubit`` into the full 2^N space.

    Mirrors qcsim's LSB convention: qubit k sits at Kronecker position
    (N-1-k) from the left, so the full operator is
    ``I_{N-1} (x) ... (x) op_k (x) ... (x) I_0``.

    Args:
        op: 2x2 operator (unitary or a single Kraus operator).
        qubit: Target qubit (LSB convention).
        num_qubits: Total qubits in the system.

    Returns:
        A (2^N, 2^N) matrix acting as ``op`` on ``qubit`` and identity elsewhere.
    """
    ops: List[np.ndarray] = [_I2] * num_qubits
    ops[num_qubits - 1 - qubit] = op
    return reduce(np.kron, ops)


def apply_channel(dm: DensityMatrix, channel: NoiseChannel, qubit: int) -> None:
    """Apply a single-qubit noise channel to ``qubit`` in place.

    Embeds every Kraus operator on the target qubit and evolves
    ``rho -> sum_k K_k rho K_k^dagger``.

    Args:
        dm: The density matrix to modify in place.
        channel: The noise channel (provides 2x2 Kraus operators).
        qubit: Target qubit index (LSB convention).
    """
    rho = dm.matrix()
    new_rho = np.zeros_like(rho)
    for k in channel.kraus():
        K = embed_single(k, qubit, dm.num_qubits)
        new_rho += K @ rho @ K.conj().T
    dm.set(new_rho)


def run(qc: QuantumCircuit, noise_model=None) -> DensityMatrix:
    """Replay a circuit onto a density matrix, applying noise after each gate.

    For each unitary gate: evolve ``rho -> U rho U^dagger``, then, for every
    channel the noise model attaches to that gate, apply it to each qubit the
    gate touched. A ``None`` (or ideal) noise model reproduces :func:`run_ideal`.

    Args:
        qc: A qcsim circuit (its gate log is replayed).
        noise_model: A :class:`~qnoise.model.NoiseModel`, or None for no noise.

    Returns:
        The final (possibly mixed) DensityMatrix.
    """
    dm = DensityMatrix(qc.num_qubits)
    for name, qubits, params in qc._log:
        if name in _SKIP:
            continue
        if name == "RESET":
            _apply_reset(dm, qubits[0])
            continue
        U = gate_unitary(name, qubits, params, qc.num_qubits)
        dm.apply_unitary(U)
        if noise_model is not None:
            for channel in noise_model.channels_for(name):
                for q in qubits:
                    apply_channel(dm, channel, q)
    return dm


def run_ideal(qc: QuantumCircuit) -> DensityMatrix:
    """Replay a circuit onto a density matrix with **no noise**.

    For each unitary gate in the circuit's log, evolve ``rho -> U rho U^dagger``.
    Non-unitary log entries (BARRIER/MEASURE/RESET) are skipped in this phase.

    Args:
        qc: A qcsim circuit (its gate log is replayed).

    Returns:
        The final DensityMatrix. Its diagonal must match ``qc.probabilities()``.
    """
    dm = DensityMatrix(qc.num_qubits)
    for name, qubits, params in qc._log:
        if name in _SKIP:
            continue
        if name == "RESET":
            _apply_reset(dm, qubits[0])
            continue
        U = gate_unitary(name, qubits, params, qc.num_qubits)
        dm.apply_unitary(U)
    return dm
