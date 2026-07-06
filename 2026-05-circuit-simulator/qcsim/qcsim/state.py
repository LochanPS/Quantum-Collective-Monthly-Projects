"""Quantum state representation using the state vector formalism."""

from __future__ import annotations

import numpy as np


class QuantumState:
    """State vector for an N-qubit quantum system.

    Convention — LSB (Qiskit-compatible, little-endian):
        - Qubit 0 is the least significant bit (rightmost character in bitstrings).
        - State vector index = q_{n-1}·2^{n-1} + ... + q_1·2^1 + q_0·2^0
        - Bitstring '01' means q1=0, q0=1.

    Storage: 2^N complex128 amplitudes in a contiguous numpy array.
    Index 0 always corresponds to the |00...0⟩ basis state.
    """

    def __init__(self, num_qubits: int) -> None:
        """Initialise all qubits to |0⟩.

        Args:
            num_qubits: Number of qubits in the system.
        """
        self.num_qubits = num_qubits
        self.dim = 2**num_qubits
        self._vec: np.ndarray = np.zeros(self.dim, dtype=complex)
        self._vec[0] = 1.0 + 0j  # |00...0⟩

    # ------------------------------------------------------------------ #
    #  Accessors
    # ------------------------------------------------------------------ #

    def amplitudes(self) -> np.ndarray:
        """Return a copy of the state vector.

        Returns:
            Complex128 numpy array of shape (2^N,).
        """
        return self._vec.copy()

    def set(self, vec: np.ndarray) -> None:
        """Overwrite the state vector (internal use by gate application).

        Args:
            vec: Complex numpy array of shape (2^N,).
        """
        self._vec = np.asarray(vec, dtype=complex)

    def probabilities(self) -> np.ndarray:
        """Return |amplitude|² for every basis state.

        Returns:
            Real float64 array of shape (2^N,). Sums to 1 (up to floating-point error).
        """
        return np.abs(self._vec) ** 2

    def probabilities_dict(self, threshold: float = 1e-10) -> dict[str, float]:
        """Return non-negligible probabilities keyed by bitstring.

        Args:
            threshold: States with probability below this are excluded.

        Returns:
            Dict mapping bitstring (e.g. '01') to float probability.
        """
        probs = self.probabilities()
        return {self.label(i): float(probs[i]) for i in range(self.dim) if probs[i] > threshold}

    def label(self, index: int) -> str:
        """Convert a state-vector index to a bitstring (LSB convention).

        Args:
            index: Integer index into the state vector (0 ≤ index < 2^N).

        Returns:
            Bitstring of length N. Rightmost character corresponds to qubit 0.

        Example:
            For N=2: label(2) == '10'  (q1=1, q0=0)
        """
        return format(index, f"0{self.num_qubits}b")

    def norm(self) -> float:
        """Return the L2 norm of the state vector (should always be 1.0)."""
        return float(np.sqrt(np.sum(np.abs(self._vec) ** 2)))

    def reset(self) -> None:
        """Reset all qubits to |0⟩."""
        self._vec[:] = 0.0
        self._vec[0] = 1.0 + 0j

    def prob_one(self, qubit: int) -> float:
        """Marginal probability that a single qubit reads 1.

        Args:
            qubit: Qubit index (LSB convention).

        Returns:
            Sum of |amplitude|² over every basis state with that qubit's bit set.
        """
        indices = np.arange(self.dim)
        mask = ((indices >> qubit) & 1) == 1
        return float(np.sum(np.abs(self._vec[mask]) ** 2))

    def collapse(self, qubit: int, outcome: int) -> None:
        """Project the state onto a fixed outcome for one qubit and renormalise.

        Args:
            qubit: Qubit index (LSB convention).
            outcome: 0 or 1 — the bit value to collapse onto.

        Raises:
            ZeroDivisionError: If the outcome has zero probability (should not
                happen if `outcome` was sampled from `prob_one`).
        """
        indices = np.arange(self.dim)
        keep = ((indices >> qubit) & 1) == outcome
        self._vec[~keep] = 0.0
        norm = np.sqrt(np.sum(np.abs(self._vec) ** 2))
        self._vec /= norm
