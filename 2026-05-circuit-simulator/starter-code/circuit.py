"""
Starter scaffold for the May 2026 challenge.
Copy this into your fork and fill in the TODOs.
Do not submit this file directly to the main repo.
"""

import numpy as np


class QuantumState:
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        # TODO: initialize state vector of size 2^num_qubits
        # Hint: np.zeros(2**num_qubits, dtype=complex), then set index 0 to 1.0

    def get_amplitudes(self) -> np.ndarray:
        # TODO: return copy of state vector
        raise NotImplementedError

    def get_probabilities(self) -> np.ndarray:
        # TODO: return |amplitude|^2 for each basis state
        raise NotImplementedError


class QuantumCircuit:
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        # TODO: create a QuantumState

    def h(self, qubit: int) -> "QuantumCircuit":
        """Apply Hadamard gate. H = [[1,1],[1,-1]] / sqrt(2)"""
        # TODO: expand to full 2^N x 2^N operator, apply to state
        # Hint: np.kron() builds the full operator from the 2x2 gate + identity matrices
        raise NotImplementedError

    def x(self, qubit: int) -> "QuantumCircuit":
        """Apply Pauli-X (NOT) gate. X = [[0,1],[1,0]]"""
        raise NotImplementedError

    def cnot(self, control: int, target: int) -> "QuantumCircuit":
        """Apply CNOT. Flips target when control is |1>."""
        # Harder than single-qubit gates — CNOT is a 4x4 matrix
        # Think about how to embed it into the full 2^N x 2^N space
        raise NotImplementedError

    def probabilities(self) -> dict:
        """Return {basis_state_string: probability}. E.g. {'00': 0.5, '11': 0.5}"""
        raise NotImplementedError

    def measure_all(self, shots: int = 1024) -> dict:
        """Sample measurement outcomes. Return counts. E.g. {'00': 512, '11': 512}"""
        # Hint: np.random.choice with p=probabilities
        raise NotImplementedError
