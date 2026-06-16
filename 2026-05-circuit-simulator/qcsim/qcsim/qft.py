"""Quantum Fourier Transform utilities.

Reusable QFT and inverse-QFT subroutines for qcsim.
"""

import math

from .circuit import QuantumCircuit


def qft(qc: QuantumCircuit, qubits: list[int]) -> None:
    """Apply the Quantum Fourier Transform in-place.

    Args:
        qc: Circuit to modify.
        qubits: Ordered list of qubits participating in the transform.
    """
    n = len(qubits)

    for i in range(n):
        qc.h(qubits[i])

        for j in range(i + 1, n):
            angle = math.pi / (2 ** (j - i))
            qc.cp(qubits[j], qubits[i], angle)

    # Bit-reversal swaps
    for i in range(n // 2):
        qc.swap(qubits[i], qubits[n - 1 - i])


def inverse_qft(qc: QuantumCircuit, qubits: list[int]) -> None:
    """Apply the inverse Quantum Fourier Transform in-place.

    Args:
        qc: Circuit to modify.
        qubits: Ordered list of qubits participating in the transform.
    """
    n = len(qubits)

    # Undo bit-reversal swaps
    for i in range(n // 2):
        qc.swap(qubits[i], qubits[n - 1 - i])

    for i in reversed(range(n)):
        for j in reversed(range(i + 1, n)):
            angle = -math.pi / (2 ** (j - i))
            qc.cp(qubits[j], qubits[i], angle)

        qc.h(qubits[i])
