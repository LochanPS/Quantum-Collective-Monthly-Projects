"""qcsim — Quantum Circuit Simulator
Quantum Collective Monthly Project #1

A clean, readable, Qiskit-compatible state-vector simulator built from
scratch in pure Python + NumPy. Designed to be understood, extended,
and built upon.

Quick start::

    from qcsim import QuantumCircuit
    from qcsim.visualize import draw_statevector, draw_histogram, banner

    print(banner())

    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)

    print(qc.draw())
    print(draw_statevector(qc))

    counts = qc.measure_all(shots=1024)
    print(draw_histogram(counts, shots=1024))

Convention: LSB (Qiskit-compatible) — qubit 0 is the rightmost bit in
bitstrings. '01' means q1=0, q0=1.
"""

from .circuit import QuantumCircuit
from .exceptions import CircuitCompositionError, GateError, QCSimError, QubitIndexError
from . import gates
from .state import QuantumState
from .visualize import banner, draw_histogram, draw_statevector
from .qft import qft, inverse_qft

__version__ = "0.1.0"
__author__ = "Quantum Collective"

__all__ = [
    "QuantumCircuit",
    "QuantumState",
    "gates",
    # Exceptions
    "QCSimError",
    "QubitIndexError",
    "GateError",
    "CircuitCompositionError",
    # Visualisation
    "banner",
    "draw_statevector",
    "draw_histogram",
    # Algorithms
    "qft",
    "inverse_qft",
]
