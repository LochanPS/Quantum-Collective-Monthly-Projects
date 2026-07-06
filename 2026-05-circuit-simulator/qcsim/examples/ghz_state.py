"""GHZ State — qcsim example.

Greenberger-Horne-Zeilinger state for 5 qubits:
    |GHZ> = (|00000> + |11111>) / sqrt(2)

Demonstrates multi-qubit entanglement and chained CNOT gates.

Run: python examples/ghz_state.py
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcsim import QuantumCircuit, draw_statevector, draw_histogram, banner


def make_ghz(n: int) -> QuantumCircuit:
    """Build an n-qubit GHZ circuit."""
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cnot(i, i + 1)
    return qc


def main():
    print(banner())
    print()
    print("  GHZ State (5 qubits)")
    print("  " + "=" * 30)
    print()

    qc = make_ghz(5)

    print(qc.draw())
    print()
    print(draw_statevector(qc))
    print()

    counts = qc.measure_all(shots=2048)
    print(draw_histogram(counts, shots=2048))
    print()
    print(f"  {qc.summary()}")
    print()
    print("  Note: only |00000> and |11111> appear.")
    print("  All 5 qubits are maximally entangled.")


if __name__ == "__main__":
    main()
