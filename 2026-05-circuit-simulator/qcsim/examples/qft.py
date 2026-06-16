"""Quantum Fourier Transform (QFT) — qcsim example.

Demonstrates the Quantum Fourier Transform (QFT) and its inverse (IQFT).

Run:
    python examples/qft.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcsim import QuantumCircuit, banner, draw_statevector


# ================================================================== #
#  Quantum Fourier Transform
# ================================================================== #

def qft(qc: QuantumCircuit, qubits: list[int]) -> None:
    """Apply the Quantum Fourier Transform in-place."""
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
    """Apply the inverse Quantum Fourier Transform in-place."""
    n = len(qubits)

    # Undo bit-reversal swaps
    for i in range(n // 2):
        qc.swap(qubits[i], qubits[n - 1 - i])

    for i in reversed(range(n)):
        for j in reversed(range(i + 1, n)):
            angle = -math.pi / (2 ** (j - i))
            qc.cp(qubits[j], qubits[i], angle)

        qc.h(qubits[i])


# ================================================================== #
#  Main
# ================================================================== #

def main():
    print(banner())
    print()
    print("  Demonstrates QFT and inverse QFT on a 3-qubit state.")
    print("  The original state should be recovered after IQFT.")
    print()

    qc = QuantumCircuit(3)

    # Prepare |101>
    qc.x(0)
    qc.x(2)

    print("  Initial computational basis state |101>")
    print()
    print(draw_statevector(qc))
    print()

    qft(qc, [0, 1, 2])

    print("  Circuit")
    print()
    print(qc.draw())
    print()

    print("  After QFT (Fourier basis)")
    print()
    print(draw_statevector(qc))
    print()

    inverse_qft(qc, [0, 1, 2])

    print("  After IQFT (recovered original state)")
    print()
    print(draw_statevector(qc))
    print()


if __name__ == "__main__":
    main()