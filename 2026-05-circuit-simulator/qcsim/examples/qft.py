"""Quantum Fourier Transform (QFT) — qcsim example.

Demonstrates the Quantum Fourier Transform (QFT) and its inverse (IQFT).

Run:
    python examples/qft.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcsim import QuantumCircuit, banner, draw_statevector


# ================================================================== #
#  Quantum Fourier Transform
# ================================================================== #

from qcsim import (
    QuantumCircuit,
    banner,
    draw_statevector,
    qft,
    inverse_qft,
)

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