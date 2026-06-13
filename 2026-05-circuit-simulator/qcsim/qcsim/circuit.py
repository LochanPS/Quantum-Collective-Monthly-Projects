"""QuantumCircuit: the primary public API for qcsim."""

from __future__ import annotations

import warnings
from collections import Counter
from functools import reduce
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import gates as G
from .exceptions import CircuitCompositionError, GateError, QubitIndexError
from .state import QuantumState

_MAX_QUBITS = 20  # 2^20 = ~16 MB — practical limit on a standard laptop

# Projectors used when building controlled gates via Kronecker expansion
_I2 = np.eye(2, dtype=complex)
_P0 = np.array([[1, 0], [0, 0]], dtype=complex)  # |0⟩⟨0|
_P1 = np.array([[0, 0], [0, 1]], dtype=complex)  # |1⟩⟨1|


# ------------------------------------------------------------------ #
#  Type alias for the internal gate log
# ------------------------------------------------------------------ #
GateEntry = Tuple[str, List[int], Optional[dict]]


class QuantumCircuit:
    """State-vector quantum circuit simulator.

    Qubit convention — LSB (Qiskit-compatible):
        - Qubit 0 is the least significant bit (rightmost in bitstrings).
        - '01' means q1=0, q0=1.

    Gate application method — Kronecker product expansion:
        - All gates are expanded to the full 2^N × 2^N unitary, then applied.
        - Exact simulation. Memory scales as O(4^N) for the unitary build step
          but only O(2^N) for the state vector.
        - Practical limit: 20 qubits on a standard laptop.

    State after measurement — preserved:
        - ``measure_all()`` samples from the distribution without collapsing
          the state vector. Call it multiple times safely.

    Method chaining:
        All gate methods return ``self`` so you can write:
        ``qc.h(0).cnot(0, 1).measure_all(1024)``

    Example:
        >>> qc = QuantumCircuit(2)
        >>> qc.h(0).cnot(0, 1)
        >>> print(qc.draw())
        >>> print(qc.measure_all(shots=1000))
    """

    def __init__(self, num_qubits: int, backend: str = "kronecker") -> None:
        """Create a circuit with all qubits initialised to |0⟩.

        Args:
            num_qubits: Number of qubits. Must be between 1 and 20.
            backend: Simulation method. 'kronecker' (default, readable) or
                'tensor' (faster for large circuits, no full matrix built).

        Raises:
            QubitIndexError: If num_qubits is outside the valid range.
            ValueError: If backend is not 'kronecker' or 'tensor'.
        """
        if not (1 <= num_qubits <= _MAX_QUBITS):
            raise QubitIndexError(
                f"num_qubits must be between 1 and {_MAX_QUBITS}, got {num_qubits}."
            )
        if backend not in ("kronecker", "tensor"):
            raise ValueError(f"backend must be 'kronecker' or 'tensor', got '{backend}'.")
        self.num_qubits = num_qubits
        self.backend = backend
        self._state = QuantumState(num_qubits)
        self._log: List[GateEntry] = []  # (name, qubit_list, params_dict)

    # ================================================================== #
    #  Internal helpers
    # ================================================================== #

    def _check(self, qubit: int, label: str = "qubit") -> None:
        """Validate a qubit index. Warns and raises on failure.

        Args:
            qubit: Index to validate.
            label: Descriptive name used in the error message.

        Raises:
            QubitIndexError: If the index is out of range.
        """
        if not (0 <= qubit < self.num_qubits):
            msg = (
                f"Invalid {label} index {qubit}. "
                f"Circuit has {self.num_qubits} qubits "
                f"(valid indices: 0–{self.num_qubits - 1})."
            )
            warnings.warn(msg, stacklevel=3)
            raise QubitIndexError(msg)

    def _check_distinct(self, *qubits: int) -> None:
        """Raise if any two qubit indices are identical.

        Args:
            *qubits: Qubit indices to check.

        Raises:
            QubitIndexError: If any two indices are the same.
        """
        seen: set[int] = set()
        for q in qubits:
            if q in seen:
                msg = f"Qubit indices must be distinct; found duplicate: {q}."
                warnings.warn(msg, stacklevel=3)
                raise QubitIndexError(msg)
            seen.add(q)

    # ------------------------------------------------------------------ #
    #  Kronecker expansion helpers (LSB convention)
    # ------------------------------------------------------------------ #

    def _expand_single(self, gate: np.ndarray, qubit: int) -> np.ndarray:
        """Expand a 2×2 gate to the full 2^N × 2^N operator.

        In LSB convention qubit k sits at Kronecker position (N-1-k) from
        the left — qubit 0 is the rightmost factor.

        Full operator = I_{N-1} ⊗ ... ⊗ Gate_k ⊗ ... ⊗ I_0

        Args:
            gate: 2×2 gate matrix (complex128).
            qubit: Target qubit index (0-indexed, LSB).

        Returns:
            2^N × 2^N unitary matrix.
        """
        n = self.num_qubits
        ops: List[np.ndarray] = [_I2] * n
        ops[n - 1 - qubit] = gate  # qubit 0 → rightmost Kronecker factor
        return reduce(np.kron, ops)

    def _expand_controlled(
        self, target_gate: np.ndarray, control: int, target: int
    ) -> np.ndarray:
        """Build the 2^N × 2^N matrix for a controlled single-qubit gate.

        Uses the projector decomposition:
            U = |0⟩⟨0|_ctrl ⊗ I_tgt + |1⟩⟨1|_ctrl ⊗ Gate_tgt
        expanded to the full N-qubit space. Works for any control/target
        positions including non-adjacent qubits.

        Args:
            target_gate: 2×2 gate applied to target when control is |1⟩.
            control: Control qubit index.
            target: Target qubit index.

        Returns:
            2^N × 2^N unitary matrix.
        """
        n = self.num_qubits

        # Term 1: control = |0⟩⟨0|, all others = I
        ops0: List[np.ndarray] = [_I2] * n
        ops0[n - 1 - control] = _P0
        term0 = reduce(np.kron, ops0)

        # Term 2: control = |1⟩⟨1|, target = gate, all others = I
        ops1: List[np.ndarray] = [_I2] * n
        ops1[n - 1 - control] = _P1
        ops1[n - 1 - target] = target_gate
        term1 = reduce(np.kron, ops1)

        return term0 + term1

    def _expand_toffoli(self, ctrl0: int, ctrl1: int, target: int) -> np.ndarray:
        """Build the 2^N × 2^N matrix for the Toffoli (CCX) gate.

        Flips target when BOTH controls are |1⟩.

        Args:
            ctrl0: First control qubit index.
            ctrl1: Second control qubit index.
            target: Target qubit index.

        Returns:
            2^N × 2^N unitary matrix.
        """
        n = self.num_qubits
        X = G.X()

        # 4 terms: |c0 c1⟩⟨c0 c1| ⊗ (X if c0=c1=1 else I)
        result = np.zeros((2 ** n, 2 ** n), dtype=complex)
        for c0 in range(2):
            for c1 in range(2):
                ops: List[np.ndarray] = [_I2] * n
                ops[n - 1 - ctrl0] = _P1 if c0 else _P0
                ops[n - 1 - ctrl1] = _P1 if c1 else _P0
                ops[n - 1 - target] = X if (c0 and c1) else _I2
                result += reduce(np.kron, ops)
        return result

    def _expand_swap(self, a: int, b: int) -> np.ndarray:
        """Build the 2^N × 2^N SWAP matrix via three CNOTs.

        SWAP(a,b) = CNOT(a→b) · CNOT(b→a) · CNOT(a→b)

        Args:
            a: First qubit index.
            b: Second qubit index.

        Returns:
            2^N × 2^N unitary matrix.
        """
        c1 = self._expand_controlled(G.X(), a, b)
        c2 = self._expand_controlled(G.X(), b, a)
        return c1 @ c2 @ c1

    def _apply(self, U: np.ndarray) -> None:
        """Apply a 2^N × 2^N unitary to the current state vector.

        Args:
            U: Unitary matrix of shape (2^N, 2^N).
        """
        sv = self._state.amplitudes()
        self._state.set(U @ sv)

    # ================================================================== #
    #  Tensor backend — no full matrix built, O(2^N) per gate
    # ================================================================== #

    def _tensor_single(self, gate: np.ndarray, qubit: int) -> None:
        """Apply a 2x2 gate via tensor axis permutation (tensor backend).

        Reshapes the state vector to (2,)*N, contracts along the target
        qubit's axis, then reshapes back. Avoids building the 2^N×2^N matrix.

        Args:
            gate: 2x2 gate matrix.
            qubit: Target qubit index (LSB: axis = N-1-qubit).
        """
        n = self.num_qubits
        sv = self._state.amplitudes().reshape([2] * n)
        axis = n - 1 - qubit
        sv = np.tensordot(gate, sv, axes=[[1], [axis]])
        sv = np.moveaxis(sv, 0, axis)
        self._state.set(sv.reshape(2 ** n))

    def _tensor_cnot(self, ctrl: int, tgt: int) -> None:
        """Apply CNOT via tensor slicing (tensor backend).

        Selects the ctrl=1 slice of the state tensor and flips the target
        axis within that slice. No matrix construction at all.

        Args:
            ctrl: Control qubit index.
            tgt: Target qubit index.
        """
        n = self.num_qubits
        sv = self._state.amplitudes().reshape([2] * n)
        ctrl_ax = n - 1 - ctrl
        tgt_ax = n - 1 - tgt

        # Index that selects ctrl=1 across all other axes
        idx: List = [slice(None)] * n
        idx[ctrl_ax] = 1
        sv_ctrl1 = sv[tuple(idx)]

        # In the ctrl=1 slice (n-1 dims), find the adjusted target axis
        adj_tgt = tgt_ax if tgt_ax < ctrl_ax else tgt_ax - 1
        sv[tuple(idx)] = np.flip(sv_ctrl1, axis=adj_tgt).copy()
        self._state.set(sv.reshape(2 ** n))

    def _tensor_swap(self, a: int, b: int) -> None:
        """Apply SWAP via np.swapaxes (tensor backend).

        Swapping two qubit axes in the tensor IS the SWAP gate.

        Args:
            a: First qubit index.
            b: Second qubit index.
        """
        n = self.num_qubits
        sv = self._state.amplitudes().reshape([2] * n)
        sv = np.swapaxes(sv, n - 1 - a, n - 1 - b)
        self._state.set(sv.reshape(2 ** n).copy())

    def _tensor_toffoli(self, ctrl0: int, ctrl1: int, tgt: int) -> None:
        """Apply Toffoli via tensor slicing (tensor backend).

        Selects the ctrl0=1, ctrl1=1 slice and flips the target axis.

        Args:
            ctrl0: First control qubit index.
            ctrl1: Second control qubit index.
            tgt: Target qubit index.
        """
        n = self.num_qubits
        sv = self._state.amplitudes().reshape([2] * n)
        c0_ax = n - 1 - ctrl0
        c1_ax = n - 1 - ctrl1
        tgt_ax = n - 1 - tgt

        idx: List = [slice(None)] * n
        idx[c0_ax] = 1
        idx[c1_ax] = 1
        sv_slice = sv[tuple(idx)]

        # Adjust tgt_ax for the two removed axes
        adj = tgt_ax
        for removed in sorted([c0_ax, c1_ax]):
            if removed < adj:
                adj -= 1

        sv[tuple(idx)] = np.flip(sv_slice, axis=adj).copy()
        self._state.set(sv.reshape(2 ** n))

    def _gate_single(self, gate: np.ndarray, qubit: int) -> None:
        """Dispatch single-qubit gate to the active backend."""
        if self.backend == "tensor":
            self._tensor_single(gate, qubit)
        else:
            self._apply(self._expand_single(gate, qubit))

    def _gate_cnot(self, ctrl: int, tgt: int) -> None:
        """Dispatch CNOT to the active backend."""
        if self.backend == "tensor":
            self._tensor_cnot(ctrl, tgt)
        else:
            self._apply(self._expand_controlled(G.X(), ctrl, tgt))

    def _gate_swap(self, a: int, b: int) -> None:
        """Dispatch SWAP to the active backend."""
        if self.backend == "tensor":
            self._tensor_swap(a, b)
        else:
            self._apply(self._expand_swap(a, b))

    def _gate_controlled(self, gate: np.ndarray, ctrl: int, tgt: int) -> None:
        """Dispatch generic controlled gate to the active backend."""
        if self.backend == "tensor":
            # Generic controlled: apply gate to tgt slice where ctrl=1
            n = self.num_qubits
            sv = self._state.amplitudes().reshape([2] * n)
            ctrl_ax = n - 1 - ctrl
            tgt_ax = n - 1 - tgt
            idx: List = [slice(None)] * n
            idx[ctrl_ax] = 1
            sv_ctrl1 = sv[tuple(idx)]
            adj_tgt = tgt_ax if tgt_ax < ctrl_ax else tgt_ax - 1
            sv_ctrl1 = np.tensordot(gate, sv_ctrl1, axes=[[1], [adj_tgt]])
            sv_ctrl1 = np.moveaxis(sv_ctrl1, 0, adj_tgt)
            sv[tuple(idx)] = sv_ctrl1
            self._state.set(sv.reshape(2 ** n))
        else:
            self._apply(self._expand_controlled(gate, ctrl, tgt))

    def cy(self,control: int,target: int) -> "QuantumCircuit":
        """Apply Controlled-Y gate."""

        self._check(control, "control")
        self._check(target, "target")
        self._check_distinct(control, target)

        self._gate_controlled(
            G.Y(),
            control,
            target
        )

        self._log.append(
            ("CY", [control, target], None)
        )

        return self
    def cp(self,control: int,target: int,lam: float) -> "QuantumCircuit":
        """Apply controlled phase gate."""

        self._check(control, "control")
        self._check(target, "target")
        self._check_distinct(control, target)

        self._gate_controlled(
            G.P(lam),
            control,
            target
        )

        self._log.append(
            (
                "CP",
                [control, target],
                {"lambda": lam}
            )
        )

        return self

    def _gate_toffoli(self, c0: int, c1: int, tgt: int) -> None:
        """Dispatch Toffoli to the active backend."""
        if self.backend == "tensor":
            self._tensor_toffoli(c0, c1, tgt)
        else:
            self._apply(self._expand_toffoli(c0, c1, tgt))

    # ================================================================== #
    #  Single-qubit gates
    # ================================================================== #

    def i(self, qubit: int) -> "QuantumCircuit":
        """Apply the Identity gate (no-op, useful as a circuit placeholder).

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._log.append(("I", [qubit], None))
        return self

    def h(self, qubit: int) -> "QuantumCircuit":
        """Apply the Hadamard gate. Creates equal superposition.

        H|0⟩ = (|0⟩ + |1⟩)/√2

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.H(), qubit)
        self._log.append(("H", [qubit], None))
        return self

    def x(self, qubit: int) -> "QuantumCircuit":
        """Apply the Pauli-X (NOT) gate. Flips |0⟩ ↔ |1⟩.

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.X(), qubit)
        self._log.append(("X", [qubit], None))
        return self

    def y(self, qubit: int) -> "QuantumCircuit":
        """Apply the Pauli-Y gate.

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Y(), qubit)
        self._log.append(("Y", [qubit], None))
        return self

    def z(self, qubit: int) -> "QuantumCircuit":
        """Apply the Pauli-Z gate. Phase flip on |1⟩.

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Z(), qubit)
        self._log.append(("Z", [qubit], None))
        return self

    def s(self, qubit: int) -> "QuantumCircuit":
        """Apply the S gate (phase gate, √Z).

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.S(), qubit)
        self._log.append(("S", [qubit], None))
        return self

    def sdg(self, qubit: int) -> "QuantumCircuit":
        """Apply the S-dagger gate (inverse of S, S†).

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Sdg(), qubit)
        self._log.append(("Sdg", [qubit], None))
        return self

    def t(self, qubit: int) -> "QuantumCircuit":
        """Apply the T gate (π/8 gate, √S).

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.T(), qubit)
        self._log.append(("T", [qubit], None))
        return self

    def tdg(self, qubit: int) -> "QuantumCircuit":
        """Apply the T-dagger gate (inverse of T, T†).

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Tdg(), qubit)
        self._log.append(("Tdg", [qubit], None))
        return self

    def sx(self, qubit: int) -> "QuantumCircuit":
        """Apply the SX gate (√X gate).

        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.SX(), qubit)
        self._log.append(("SX", [qubit], None))
        return self

    def sxdg(self, qubit: int) -> "QuantumCircuit":
        """Apply the SX-dagger gate (inverse of SX).
        Args:
            qubit: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.SXdg(), qubit)
        self._log.append(("SXdg", [qubit], None))
        return self

    # ------------------------------------------------------------------ #
    #  Parametric single-qubit gates
    # ------------------------------------------------------------------ #

    def rx(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Apply Rx(θ) — rotation around X-axis by angle theta (radians).

        Args:
            qubit: Target qubit index.
            theta: Rotation angle in radians.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Rx(theta), qubit)
        self._log.append(("Rx", [qubit], {"theta": theta}))
        return self

    def ry(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Apply Ry(θ) — rotation around Y-axis by angle theta (radians).

        Args:
            qubit: Target qubit index.
            theta: Rotation angle in radians.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Ry(theta), qubit)
        self._log.append(("Ry", [qubit], {"theta": theta}))
        return self

    def rz(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Apply Rz(θ) — rotation around Z-axis by angle theta (radians).

        Args:
            qubit: Target qubit index.
            theta: Rotation angle in radians.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.Rz(theta), qubit)
        self._log.append(("Rz", [qubit], {"theta": theta}))
        return self

    def p(self, qubit: int, lam: float) -> "QuantumCircuit":
        """Apply P(λ) — phase gate. Adds phase e^(iλ) to |1⟩.

        Args:
            qubit: Target qubit index.
            lam: Phase angle lambda in radians.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.P(lam), qubit)
        self._log.append(("P", [qubit], {"lam": lam}))
        return self

    def u(self, qubit: int, theta: float, phi: float, lam: float) -> "QuantumCircuit":
        """Apply U(θ,φ,λ) — the generic single-qubit unitary gate.

        Args:
            qubit: Target qubit index.
            theta: Polar angle in radians.
            phi: Azimuthal start angle in radians.
            lam: Azimuthal end angle in radians.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If the qubit index is out of range.
        """
        self._check(qubit)
        self._gate_single(G.U(theta, phi, lam), qubit)
        self._log.append(("U", [qubit], {"theta": theta, "phi": phi, "lam": lam}))
        return self

    # ================================================================== #
    #  Two-qubit gates
    # ================================================================== #

    def cnot(self, control: int, target: int) -> "QuantumCircuit":
        """Apply CNOT (Controlled-X) gate. Flips target when control is |1⟩.

        Args:
            control: Control qubit index.
            target: Target qubit index. Must differ from control.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If either index is out of range or control == target.
        """
        self._check(control, "control")
        self._check(target, "target")
        self._check_distinct(control, target)
        self._gate_cnot(control, target)
        self._log.append(("CNOT", [control, target], None))
        return self

    # Alias
    cx = cnot

    def cy(self, control: int, target: int) -> "QuantumCircuit":
        """Apply CY gate (Controlled-Y).

        Args:
            control: Control qubit index.
            target: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If either index is out of range or control == target.
        """
        self._check(control, "control")
        self._check(target, "target")
        self._check_distinct(control, target)
        self._gate_controlled(G.Y(), control, target)
        self._log.append(("CY", [control, target], None))
        return self

    def cz(self, control: int, target: int) -> "QuantumCircuit":
        """Apply CZ gate (Controlled-Z). Phase flip when both qubits are |1⟩.

        Args:
            control: Control qubit index.
            target: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If either index is out of range or control == target.
        """
        self._check(control, "control")
        self._check(target, "target")
        self._check_distinct(control, target)
        self._gate_controlled(G.Z(), control, target)
        self._log.append(("CZ", [control, target], None))
        return self

    def swap(self, a: int, b: int) -> "QuantumCircuit":
        """Apply SWAP gate. Exchanges the states of two qubits.

        Args:
            a: First qubit index.
            b: Second qubit index. Must differ from a.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If either index is out of range or a == b.
        """
        self._check(a, "qubit a")
        self._check(b, "qubit b")
        self._check_distinct(a, b)
        self._gate_swap(a, b)
        self._log.append(("SWAP", [a, b], None))
        return self

    def cp(self, control: int, target: int, lam: float) -> "QuantumCircuit":
        """Apply Controlled-Phase gate. Adds phase e^(iλ) when both qubits are |1⟩.

        Args:
            control: Control qubit index.
            target: Target qubit index.
            lam: Phase angle lambda in radians.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If either index is out of range or control == target.
        """
        self._check(control, "control")
        self._check(target, "target")
        self._check_distinct(control, target)
        self._gate_controlled(G.P(lam), control, target)
        self._log.append(("CP", [control, target], {"lam": lam}))
        return self

    # ================================================================== #
    #  Three-qubit gates
    # ================================================================== #

    def toffoli(self, ctrl0: int, ctrl1: int, target: int) -> "QuantumCircuit":
        """Apply the Toffoli (CCX) gate. Flips target when BOTH controls are |1⟩.

        Args:
            ctrl0: First control qubit index.
            ctrl1: Second control qubit index.
            target: Target qubit index.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If any index is out of range or indices are not distinct.
        """
        self._check(ctrl0, "ctrl0")
        self._check(ctrl1, "ctrl1")
        self._check(target, "target")
        self._check_distinct(ctrl0, ctrl1, target)
        self._gate_toffoli(ctrl0, ctrl1, target)
        self._log.append(("CCX", [ctrl0, ctrl1, target], None))
        return self

    # Alias
    ccx = toffoli

    # ================================================================== #
    #  Custom gate
    # ================================================================== #

    def unitary(
        self, matrix: np.ndarray, qubits: Sequence[int], label: str = "U"
    ) -> "QuantumCircuit":
        """Apply an arbitrary unitary matrix to a set of qubits.

        The matrix must be 2^k × 2^k for k qubits, and must be unitary
        (U†U = I) — this is not verified for performance reasons.

        Args:
            matrix: Complex numpy array of shape (2^k, 2^k).
            qubits: Sequence of k qubit indices to act on.
            label: Display label for the gate diagram. Defaults to 'U'.

        Returns:
            Self, for method chaining.

        Raises:
            QubitIndexError: If any qubit index is out of range or indices repeat.
            GateError: If the matrix dimensions do not match the number of qubits.
        """
        k = len(qubits)
        expected = 2 ** k
        mat = np.asarray(matrix, dtype=complex)
        if mat.shape != (expected, expected):
            raise GateError(
                f"Matrix shape {mat.shape} does not match {k} qubit(s) "
                f"(expected ({expected}, {expected}))."
            )
        for q in qubits:
            self._check(q, "qubit")
        self._check_distinct(*qubits)

        # Build full operator by embedding via Kronecker expansion
        n = self.num_qubits
        if k == 1:
            full_U = self._expand_single(mat, qubits[0])
        else:
            # For multi-qubit custom gates: permute qubits to front, apply, permute back
            full_U = self._embed_unitary(mat, list(qubits))

        self._apply(full_U)
        self._log.append((label, list(qubits), {"matrix_shape": mat.shape}))
        return self

    def _embed_unitary(self, mat: np.ndarray, qubits: List[int]) -> np.ndarray:
        """Embed a k-qubit unitary into the full N-qubit space.

        Uses the projector sum method: sum over all computational basis states
        of the control qubits.

        Args:
            mat: 2^k × 2^k unitary matrix.
            qubits: List of k qubit indices (in order, MSB first for the matrix).

        Returns:
            2^N × 2^N unitary matrix.
        """
        n = self.num_qubits
        k = len(qubits)
        dim = 2 ** n
        result = np.zeros((dim, dim), dtype=complex)
        # Sum over all 2^k input/output basis state pairs
        for row_idx in range(2 ** k):
            for col_idx in range(2 ** k):
                amp = mat[row_idx, col_idx]
                if abs(amp) < 1e-15:
                    continue
                # Build a rank-1 contribution |row_idx⟩⟨col_idx| on the target qubits
                # and identity on all others
                ops: List[np.ndarray] = [_I2] * n
                # Decompose row_idx and col_idx into single-qubit projectors
                # across the k qubits (MSB of index = first qubit in list)
                projector = np.zeros((2, 2), dtype=complex)
                # We accumulate outer products qubit by qubit
                # Actually easier: build as outer product across all N qubits
                state_row = np.zeros(dim, dtype=complex)
                state_col = np.zeros(dim, dtype=complex)
                # ... this approach gets complex. Use reshape method instead.
                pass
        # Fallback: use statevector reshaping for correctness
        # Build full unitary column by column
        result = np.eye(dim, dtype=complex)
        # Apply mat to the subspace of the specified qubits
        # Use a basis-by-basis approach
        for basis_idx in range(dim):
            # Express basis_idx in terms of bits
            bits = [(basis_idx >> (n - 1 - i)) & 1 for i in range(n)]
            # Extract bits for our target qubits (LSB: qubit j is bit n-1-j from MSB)
            tgt_bits = [(basis_idx >> (n - 1 - (n - 1 - q))) & 1 for q in qubits]
            # That simplifies to: bit for qubit q in LSB = (basis_idx >> q) & 1
            tgt_input = sum(((basis_idx >> q) & 1) << (k - 1 - i)
                            for i, q in enumerate(qubits))
            new_state = np.zeros(dim, dtype=complex)
            for tgt_out in range(2 ** k):
                coeff = mat[tgt_out, tgt_input]
                if abs(coeff) < 1e-15:
                    continue
                # Build new basis index: same as basis_idx but with tgt qubits = tgt_out
                new_idx = basis_idx
                for i, q in enumerate(qubits):
                    bit = (tgt_out >> (k - 1 - i)) & 1
                    # Set bit q in new_idx
                    new_idx = (new_idx & ~(1 << q)) | (bit << q)
                result[new_idx, basis_idx] += coeff
        return result

    # ================================================================== #
    #  Circuit operations
    # ================================================================== #

    def barrier(self, label: str = "") -> "QuantumCircuit":
        """Insert a visual barrier in the circuit diagram (no physical effect).

        Args:
            label: Optional label displayed on the barrier.

        Returns:
            Self, for method chaining.
        """
        self._log.append(("BARRIER", list(range(self.num_qubits)), {"label": label}))
        return self

    def reset(self) -> "QuantumCircuit":
        """Reset all qubits to |0⟩ and clear the gate log.

        Returns:
            Self, for method chaining.
        """
        self._state.reset()
        self._log.clear()
        return self

    def compose(self, other: "QuantumCircuit") -> "QuantumCircuit":
        """Append another circuit's gates to this circuit (in-place).

        Both circuits must have the same number of qubits.

        Args:
            other: Circuit whose gates are appended after this circuit's gates.

        Returns:
            Self, for method chaining.

        Raises:
            CircuitCompositionError: If qubit counts do not match.
        """
        if other.num_qubits != self.num_qubits:
            raise CircuitCompositionError(
                f"Cannot compose circuits with {self.num_qubits} and "
                f"{other.num_qubits} qubits."
            )
        # Re-apply all gates from `other` to this circuit's state
        for name, qubits, params in other._log:
            if name == "BARRIER":
                self.barrier(params.get("label", "") if params else "")
            else:
                # Apply via the gate dispatch
                self._replay_gate(name, qubits, params)
        return self

    def _replay_gate(
        self, name: str, qubits: List[int], params: Optional[dict]
    ) -> None:
        """Replay a single gate from a log entry onto this circuit."""
        p = params or {}
        dispatch = {
            "I": lambda: self.i(qubits[0]),
            "H": lambda: self.h(qubits[0]),
            "X": lambda: self.x(qubits[0]),
            "Y": lambda: self.y(qubits[0]),
            "Z": lambda: self.z(qubits[0]),
            "S": lambda: self.s(qubits[0]),
            "Sdg": lambda: self.sdg(qubits[0]),
            "T": lambda: self.t(qubits[0]),
            "Tdg": lambda: self.tdg(qubits[0]),
            "SX": lambda: self.sx(qubits[0]),
            "SXdg": lambda: self.sxdg(qubits[0]),
            "Rx": lambda: self.rx(qubits[0], p["theta"]),
            "Ry": lambda: self.ry(qubits[0], p["theta"]),
            "Rz": lambda: self.rz(qubits[0], p["theta"]),
            "P": lambda: self.p(qubits[0], p["lam"]),
            "CNOT": lambda: self.cnot(qubits[0], qubits[1]),
            "CY": lambda: self.cy(qubits[0], qubits[1]),
            "CZ": lambda: self.cz(qubits[0], qubits[1]),
            "SWAP": lambda: self.swap(qubits[0], qubits[1]),
            "CP": lambda: self.cp(qubits[0], qubits[1], p["lam"]),
            "CCX": lambda: self.toffoli(qubits[0], qubits[1], qubits[2]),
        }
        if name in dispatch:
            dispatch[name]()

    # ================================================================== #
    #  Readout
    # ================================================================== #

    def statevector(self) -> np.ndarray:
        """Return the current state vector.

        The circuit state is NOT modified.

        Returns:
            Complex128 numpy array of shape (2^N,).
        """
        return self._state.amplitudes()

    def probabilities(self) -> Dict[str, float]:
        """Return measurement probabilities for each basis state.

        Only states with probability > 1e-10 are included.
        The circuit state is NOT modified.

        Returns:
            Dict mapping bitstring (e.g. '01') to float probability.
        """
        return self._state.probabilities_dict()

    def measure_all(self, shots: int = 1024) -> Dict[str, int]:
        """Sample measurement outcomes from the probability distribution.

        The circuit state is NOT modified — sampling is purely classical
        (drawn from the distribution, no wavefunction collapse). Safe to
        call multiple times.

        Args:
            shots: Number of samples. Must be >= 1.

        Returns:
            Dict mapping bitstring to count. E.g. {'00': 507, '11': 517}.

        Raises:
            ValueError: If shots < 1.
        """
        if shots < 1:
            raise ValueError(f"shots must be >= 1, got {shots}.")
        probs = self._state.probabilities()
        probs /= probs.sum()  # guard floating-point drift
        indices = np.random.choice(len(probs), size=shots, p=probs)
        labels = [self._state.label(int(i)) for i in indices]
        return dict(Counter(labels))

    def expectation_value(self, observable: np.ndarray) -> float:
        """Compute ⟨ψ|O|ψ⟩ for a Hermitian observable O.

        Args:
            observable: Hermitian matrix of shape (2^N, 2^N).

        Returns:
            Real expectation value as a float.
        """
        sv = self._state.amplitudes()
        return float(np.real(sv.conj() @ observable @ sv))

    # ================================================================== #
    #  Display
    # ================================================================== #

    def draw(self) -> str:
        """Return an ASCII circuit diagram.

        Returns:
            Multi-line string. Pass to print() for display.
        """
        from .visualize import draw_circuit
        return draw_circuit(self)

    def __str__(self) -> str:
        return self.draw()

    def __repr__(self) -> str:
        return (
            f"QuantumCircuit(num_qubits={self.num_qubits}, "
            f"gates={len(self._log)})"
        )

    def summary(self) -> str:
        """Return a one-line summary of the circuit.

        Returns:
            String describing qubit count, gate count, and depth.
        """
        gate_names = [e[0] for e in self._log if e[0] != "BARRIER"]
        return (
            f"QuantumCircuit  {self.num_qubits} qubit(s)  "
            f"{len(gate_names)} gate(s)  "
            f"depth {len(gate_names)}"
        )

    # ================================================================== #
    #  Qiskit export
    # ================================================================== #

    def to_qiskit_code(self, var: str = "qc") -> str:
        """Export this circuit as runnable Qiskit Python code.

        Every gate in the circuit log is converted to its Qiskit equivalent.
        The returned string is a complete Python script — save it as a .py
        file and run it directly with ``python circuit.py``.

        Args:
            var: Variable name for the QuantumCircuit in the output code.
                 Defaults to 'qc'.

        Returns:
            String of valid Python code.

        Example:
            >>> qc = QuantumCircuit(2)
            >>> qc.h(0).cnot(0, 1)
            >>> print(qc.to_qiskit_code())
        """
        # Map qcsim gate names → Qiskit method names (no-param single-qubit)
        _SIMPLE: Dict[str, str] = {
            "I": "id", "H": "h", "X": "x", "Y": "y", "Z": "z",
            "S": "s", "Sdg": "sdg", "T": "t", "Tdg": "tdg",
            "SX": "sx", "SXdg": "sxdg",
        }

        def _fmt(val: float) -> str:
            """Format a float cleanly (strip trailing zeros, cap precision)."""
            rounded = round(val, 8)
            s = f"{rounded:.8f}".rstrip("0").rstrip(".")
            return s

        def _gate_line(name: str, qubits: List[int], params: Optional[dict]) -> str:
            p = params or {}
            q = qubits

            if name in _SIMPLE:
                return f"{var}.{_SIMPLE[name]}({q[0]})"

            # Rotation / phase gates — Qiskit arg order: (angle, qubit)
            if name == "Rx":
                return f"{var}.rx({_fmt(p['theta'])}, {q[0]})"
            if name == "Ry":
                return f"{var}.ry({_fmt(p['theta'])}, {q[0]})"
            if name == "Rz":
                return f"{var}.rz({_fmt(p['theta'])}, {q[0]})"
            if name == "P":
                return f"{var}.p({_fmt(p['lam'])}, {q[0]})"
            if name == "U":
                return (
                    f"{var}.u({_fmt(p['theta'])}, {_fmt(p['phi'])}, "
                    f"{_fmt(p['lam'])}, {q[0]})"
                )

            # Two-qubit gates
            if name in ("CNOT", "CX"):
                return f"{var}.cx({q[0]}, {q[1]})"
            if name == "CY":
                return f"{var}.cy({q[0]}, {q[1]})"
            if name == "CZ":
                return f"{var}.cz({q[0]}, {q[1]})"
            if name == "SWAP":
                return f"{var}.swap({q[0]}, {q[1]})"
            if name == "CP":
                # Qiskit: cp(theta, control, target)
                return f"{var}.cp({_fmt(p['lam'])}, {q[0]}, {q[1]})"

            # Three-qubit
            if name in ("CCX", "Toffoli"):
                return f"{var}.ccx({q[0]}, {q[1]}, {q[2]})"

            # Barrier
            if name == "BARRIER":
                return f"{var}.barrier()"

            # Unknown — emit comment so file still runs
            return f"# Unsupported gate: {name} on qubits {q}"

        n = self.num_qubits
        lines: List[str] = [
            "# Generated by qcsim",
            "# https://github.com/LochanPS/Quantum-Collective-Monthly-Projects",
            "#",
            "# Setup (one-time):",
            "#   pip install qiskit qiskit-aer qiskit-ibm-runtime",
            "#",
            "# IBM account (one-time):",
            "#   1. Sign up free at https://quantum.ibm.com",
            "#   2. Copy your API token from account settings",
            "#   3. Run once:  python -c \"from qiskit_ibm_runtime import "
            "QiskitRuntimeService; "
            "QiskitRuntimeService.save_account(channel='ibm_quantum', "
            "token='YOUR_TOKEN_HERE', overwrite=True)\"",
            "",
            "from qiskit import QuantumCircuit, transpile",
            "",
            f"{var} = QuantumCircuit({n}, {n})",
            "",
        ]

        for gate_name, qubits, params in self._log:
            lines.append(_gate_line(gate_name, qubits, params))

        lines += [
            "",
            f"{var}.measure(range({n}), range({n}))",
            "",
            f"print({var}.draw())",
            "",
            "",
            "# ================================================================",
            "# OPTION 1 — Simulate locally (instant, no account needed)",
            "# ================================================================",
            "# from qiskit_aer import AerSimulator",
            "# sim = AerSimulator()",
            f"# job = sim.run({var}, shots=1024)",
            "# counts = job.result().get_counts()",
            "# print(counts)",
            "",
            "",
            "# ================================================================",
            "# OPTION 2 — Run on real IBM Quantum hardware",
            "# ================================================================",
            "# Requires IBM account saved above. Jobs go into a queue —",
            "# runtime varies from seconds to hours depending on load.",
            "#",
            "# from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2",
            "#",
            "# service = QiskitRuntimeService()",
            "# backend = service.least_busy(operational=True, simulator=False)",
            "#",
            "# # Transpile: converts to native gates + qubit routing for this backend",
            f"# {var}_compiled = transpile({var}, backend=backend, optimization_level=1)",
            f"# print({var}_compiled.draw())  # inspect what the hardware will run",
            "#",
            "# sampler = SamplerV2(backend)",
            f"# job = sampler.run([{var}_compiled], shots=1024)",
            "# print(f'Job ID: {job.job_id()}')  # save this to check status later",
            "#",
            "# result = job.result()",
            "# counts = result[0].data.meas.get_counts()",
            "# print(counts)",
            "#",
            "# # Check a previously submitted job:",
            "# # job = service.job('YOUR_JOB_ID')",
            "# # print(job.status())",
            "",
            "",
            "# ================================================================",
            "# OPTION 3 — Run on Bluequbit (easiest alternative hardware)",
            "# ================================================================",
            "# pip install bluequbit",
            "# Sign up free: https://bluequbit.ai",
            "#",
            "# import bluequbit",
            "# bq = bluequbit.init('YOUR_BLUEQUBIT_TOKEN')",
            f"# result = bq.run({var}, device='cpu')   # or 'gpu' or 'quantum'",
            "# print(result.get_counts())",
            "#",
            "# Bluequbit accepts Qiskit QuantumCircuit directly — no extra conversion.",
        ]

        return "\n".join(lines)

    def to_qasm2(self) -> str:
        """Export this circuit as OpenQASM 2.0 source code.

        OpenQASM 2.0 is a universal quantum assembly language understood by
        IBM Quantum, Google Cirq, Amazon Braket, and Qiskit. Save the output
        as a .qasm file and import it into any of those frameworks.

        Returns:
            String of valid OpenQASM 2.0 code.

        Example:
            >>> qc = QuantumCircuit(2)
            >>> qc.h(0).cnot(0, 1)
            >>> print(qc.to_qasm2())
        """
        # Gates defined in the standard qelib1.inc header
        _SIMPLE: Dict[str, str] = {
            "I": "id", "H": "h", "X": "x", "Y": "y", "Z": "z",
            "S": "s", "Sdg": "sdg", "T": "t", "Tdg": "tdg",
            "SX": "sx", "SXdg": "sxdg",
        }

        def _fmt(val: float) -> str:
            rounded = round(val, 8)
            return f"{rounded:.8f}".rstrip("0").rstrip(".")

        def _gate_line(name: str, qubits: List[int], params: Optional[dict]) -> str:
            p = params or {}
            q = qubits

            if name in _SIMPLE:
                return f"{_SIMPLE[name]} q[{q[0]}];"

            # Rotation / phase gates
            if name == "Rx":
                return f"rx({_fmt(p['theta'])}) q[{q[0]}];"
            if name == "Ry":
                return f"ry({_fmt(p['theta'])}) q[{q[0]}];"
            if name == "Rz":
                return f"rz({_fmt(p['theta'])}) q[{q[0]}];"
            if name == "P":
                return f"p({_fmt(p['lam'])}) q[{q[0]}];"
            if name == "U":
                return (
                    f"u({_fmt(p['theta'])},{_fmt(p['phi'])},{_fmt(p['lam'])}) "
                    f"q[{q[0]}];"
                )

            # Two-qubit gates
            if name in ("CNOT", "CX"):
                return f"cx q[{q[0]}],q[{q[1]}];"
            if name == "CY":
                return f"cy q[{q[0]}],q[{q[1]}];"
            if name == "CZ":
                return f"cz q[{q[0]}],q[{q[1]}];"
            if name == "SWAP":
                return f"swap q[{q[0]}],q[{q[1]}];"
            if name == "CP":
                return f"cp({_fmt(p['lam'])}) q[{q[0]}],q[{q[1]}];"

            # Three-qubit
            if name in ("CCX", "Toffoli"):
                return f"ccx q[{q[0]}],q[{q[1]}],q[{q[2]}];"

            # Barrier
            if name == "BARRIER":
                all_q = ",".join(f"q[{i}]" for i in range(self.num_qubits))
                return f"barrier {all_q};"

            # Unknown
            return f"// Unsupported gate: {name} on qubits {q}"

        n = self.num_qubits
        lines: List[str] = [
            "// Generated by qcsim",
            "// https://github.com/LochanPS/Quantum-Collective-Monthly-Projects",
            "//",
            "// Import into Qiskit:",
            "//   from qiskit import QuantumCircuit",
            "//   qc = QuantumCircuit.from_qasm_file('circuit.qasm')",
            "//",
            "// Import into Cirq:",
            "//   import cirq",
            "//   circuit = cirq.from_qasm(open('circuit.qasm').read())",
            "//",
            "// Submit directly to IBM Quantum via Qiskit Runtime.",
            "",
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            "",
            f"qreg q[{n}];",
            f"creg c[{n}];",
            "",
        ]

        for gate_name, qubits, params in self._log:
            if gate_name != "BARRIER":
                lines.append(_gate_line(gate_name, qubits, params))
            else:
                lines.append(_gate_line(gate_name, qubits, params))

        lines += [
            "",
            f"measure q -> c;",
        ]

        return "\n".join(lines)
