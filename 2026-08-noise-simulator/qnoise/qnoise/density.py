"""Density-matrix representation of an N-qubit quantum state.

Where qcsim uses a *state vector* (pure states only), a noisy state is a
statistical mixture of many possible state vectors — and no single vector can
represent that. The density matrix ``rho`` (a 2^N x 2^N complex matrix) can
represent both pure and mixed states, which is exactly why noise simulation
needs it.

Two facts to hold onto:
    - A pure state ``|psi>`` becomes ``rho = |psi><psi|`` (outer product).
    - The diagonal of ``rho`` is the measurement probability of each basis
      state — the direct analogue of ``|amplitude|^2`` in qcsim.

Convention — LSB (Qiskit-compatible, little-endian), identical to qcsim:
    - Qubit 0 is the least significant bit (rightmost character in bitstrings).
    - Bitstring '01' means q1=0, q0=1.
"""

from __future__ import annotations

import numpy as np


class DensityMatrix:
    """Density matrix for an N-qubit quantum system.

    Storage: a ``(2^N, 2^N)`` complex128 numpy array. Index 0 corresponds to
    the |00...0> basis state, matching qcsim's ordering.
    """

    def __init__(self, num_qubits: int) -> None:
        """Initialise all qubits to |0>, i.e. ``rho = |0...0><0...0|``.

        Args:
            num_qubits: Number of qubits in the system.
        """
        self.num_qubits = num_qubits
        self.dim = 2**num_qubits
        self._rho: np.ndarray = np.zeros((self.dim, self.dim), dtype=complex)
        self._rho[0, 0] = 1.0 + 0j  # |00...0><00...0|

    # ------------------------------------------------------------------ #
    #  Constructors
    # ------------------------------------------------------------------ #

    @classmethod
    def from_statevector(cls, psi: np.ndarray) -> "DensityMatrix":
        """Build a *pure*-state density matrix from a state vector.

        ``rho = |psi><psi|``. Use this to lift a qcsim result into density-matrix
        form, e.g. ``DensityMatrix.from_statevector(qc.statevector())``.

        Args:
            psi: Complex state vector of shape (2^N,).

        Returns:
            A pure DensityMatrix representing the same state.
        """
        psi = np.asarray(psi, dtype=complex).reshape(-1)
        dim = psi.shape[0]
        num_qubits = int(round(np.log2(dim)))
        if 2**num_qubits != dim:
            raise ValueError(f"state vector length {dim} is not a power of 2")
        dm = cls(num_qubits)
        dm._rho = np.outer(psi, psi.conj())
        return dm

    @classmethod
    def from_matrix(cls, rho: np.ndarray) -> "DensityMatrix":
        """Wrap an existing 2^N x 2^N matrix (no validation beyond shape)."""
        rho = np.asarray(rho, dtype=complex)
        if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
            raise ValueError("density matrix must be square")
        dim = rho.shape[0]
        num_qubits = int(round(np.log2(dim)))
        if 2**num_qubits != dim:
            raise ValueError(f"matrix dimension {dim} is not a power of 2")
        dm = cls(num_qubits)
        dm._rho = rho.copy()
        return dm

    # ------------------------------------------------------------------ #
    #  Accessors
    # ------------------------------------------------------------------ #

    def matrix(self) -> np.ndarray:
        """Return a copy of the underlying density matrix."""
        return self._rho.copy()

    def set(self, rho: np.ndarray) -> None:
        """Overwrite the density matrix (internal use by the engine)."""
        self._rho = np.asarray(rho, dtype=complex)

    def label(self, index: int) -> str:
        """Convert a matrix index to a bitstring (LSB convention, matches qcsim)."""
        return format(index, f"0{self.num_qubits}b")

    def probabilities(self) -> np.ndarray:
        """Return the measurement probability of every basis state.

        These are the real parts of the diagonal of ``rho``. Sums to 1 up to
        floating-point error.

        Returns:
            Real float64 array of shape (2^N,).
        """
        return np.real(np.diag(self._rho))

    def probabilities_dict(self, threshold: float = 1e-10) -> dict[str, float]:
        """Return non-negligible probabilities keyed by bitstring (LSB)."""
        probs = self.probabilities()
        return {
            self.label(i): float(probs[i])
            for i in range(self.dim)
            if probs[i] > threshold
        }

    # ------------------------------------------------------------------ #
    #  Physical quantities / validity
    # ------------------------------------------------------------------ #

    def trace(self) -> float:
        """Return Tr(rho). Should always be 1.0 for a physical state."""
        return float(np.real(np.trace(self._rho)))

    def purity(self) -> float:
        """Return Tr(rho^2): 1.0 for a pure state, < 1.0 for a mixed state.

        A handy one-number readout of "how much noise has crept in": a perfect
        pure state has purity 1.0; a maximally mixed N-qubit state has purity
        1 / 2^N.
        """
        return float(np.real(np.trace(self._rho @ self._rho)))

    def is_valid(self, tol: float = 1e-9) -> bool:
        """Check that ``rho`` is a physically valid density matrix.

        Valid means: Hermitian, unit trace, and positive semidefinite
        (all eigenvalues >= -tol).

        Args:
            tol: Numerical tolerance for the three checks.

        Returns:
            True if all three conditions hold.
        """
        if not np.allclose(self._rho, self._rho.conj().T, atol=tol):
            return False
        if abs(self.trace() - 1.0) > 1e-6:
            return False
        # Hermitian => use eigvalsh for real eigenvalues.
        eigvals = np.linalg.eigvalsh(self._rho)
        return bool(np.all(eigvals >= -tol))

    # ------------------------------------------------------------------ #
    #  Evolution
    # ------------------------------------------------------------------ #

    def apply_unitary(self, U: np.ndarray) -> None:
        """Apply a full-system unitary in place: ``rho -> U rho U^dagger``.

        Args:
            U: A (2^N, 2^N) unitary matrix acting on the whole system.
        """
        U = np.asarray(U, dtype=complex)
        self._rho = U @ self._rho @ U.conj().T

    # ------------------------------------------------------------------ #
    #  Dunder
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return (
            f"DensityMatrix(num_qubits={self.num_qubits}, "
            f"purity={self.purity():.4f})"
        )
