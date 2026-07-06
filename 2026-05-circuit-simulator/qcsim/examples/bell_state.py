"""Bell State — qcsim example.

Demonstrates the most fundamental entangled state in quantum computing:
    |Phi+> = (|00> + |11>) / sqrt(2)

Run: python examples/bell_state.py
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcsim import QuantumCircuit, draw_statevector, draw_histogram, banner


def main():
    print(banner())
    print()
    print("  Bell State Preparation")
    print("  " + "=" * 30)
    print()

    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)

    print(qc.draw())
    print()
    print(draw_statevector(qc))
    print()

    counts = qc.measure_all(shots=2048)
    print(draw_histogram(counts, shots=2048))
    print()
    print(f"  {qc.summary()}")


if __name__ == "__main__":
    main()
