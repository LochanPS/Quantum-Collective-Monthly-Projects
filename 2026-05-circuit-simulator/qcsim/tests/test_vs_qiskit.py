"""Optional comparison tests against Qiskit's StatevectorSimulator.

These tests are SKIPPED automatically if qiskit or qiskit-aer is not installed.
They are not part of the main CI — run manually to prove correctness:

    pip install qiskit qiskit-aer
    pytest tests/test_vs_qiskit.py -v

Each test builds the same circuit in both qcsim and Qiskit, then compares
statevectors. Tolerance is 1e-6 to account for float differences.
"""

import numpy as np
import pytest

qiskit = pytest.importorskip("qiskit", reason="qiskit not installed")
aer = pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed")

from qiskit import QuantumCircuit as QiskitCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

from qcsim import QuantumCircuit

TOL = 1e-6


def _qiskit_sv(qiskit_qc: QiskitCircuit) -> np.ndarray:
    """Run a Qiskit circuit and return its statevector."""
    sv = Statevector(qiskit_qc)
    return np.array(sv)


def _compare(qcsim_qc: QuantumCircuit, qiskit_qc: QiskitCircuit) -> None:
    """Assert qcsim and Qiskit statevectors match up to global phase."""
    ours = qcsim_qc.statevector()
    theirs = _qiskit_sv(qiskit_qc)

    # Remove global phase: find first non-zero element and align
    idx = np.argmax(np.abs(ours) > TOL)
    if np.abs(ours[idx]) > TOL and np.abs(theirs[idx]) > TOL:
        phase = ours[idx] / theirs[idx]
        theirs = theirs * phase

    assert np.allclose(
        ours, theirs, atol=TOL
    ), f"Statevectors differ.\nqcsim:  {ours}\nQiskit: {theirs}"


# ------------------------------------------------------------------ #
#  Tests
# ------------------------------------------------------------------ #


def test_bell_state_vs_qiskit():
    """Bell state: H(0) + CNOT(0,1)."""
    # qcsim
    ours = QuantumCircuit(2)
    ours.h(0).cnot(0, 1)

    # Qiskit (same LSB convention)
    theirs = QiskitCircuit(2)
    theirs.h(0)
    theirs.cx(0, 1)

    _compare(ours, theirs)


def test_ghz_state_vs_qiskit():
    """GHZ: H(0) + CNOT(0,1) + CNOT(1,2)."""
    ours = QuantumCircuit(3)
    ours.h(0).cnot(0, 1).cnot(1, 2)

    theirs = QiskitCircuit(3)
    theirs.h(0)
    theirs.cx(0, 1)
    theirs.cx(1, 2)

    _compare(ours, theirs)


def test_x_gate_vs_qiskit():
    """X on qubit 0."""
    ours = QuantumCircuit(2)
    ours.x(0)

    theirs = QiskitCircuit(2)
    theirs.x(0)

    _compare(ours, theirs)


def test_swap_vs_qiskit():
    """SWAP(0,1) on |01⟩."""
    ours = QuantumCircuit(2)
    ours.x(0).swap(0, 1)

    theirs = QiskitCircuit(2)
    theirs.x(0)
    theirs.swap(0, 1)

    _compare(ours, theirs)


def test_non_adjacent_cnot_vs_qiskit():
    """CNOT(0,2) in 3-qubit circuit."""
    ours = QuantumCircuit(3)
    ours.x(0).cnot(0, 2)

    theirs = QiskitCircuit(3)
    theirs.x(0)
    theirs.cx(0, 2)

    _compare(ours, theirs)


def test_5_qubit_uniform_vs_qiskit():
    """H on all 5 qubits."""
    ours = QuantumCircuit(5)
    for i in range(5):
        ours.h(i)

    theirs = QiskitCircuit(5)
    for i in range(5):
        theirs.h(i)

    _compare(ours, theirs)


def test_s_t_gates_vs_qiskit():
    """S and T gates on qubit 0."""
    ours = QuantumCircuit(1)
    ours.h(0).s(0).t(0)

    theirs = QiskitCircuit(1)
    theirs.h(0)
    theirs.s(0)
    theirs.t(0)

    _compare(ours, theirs)
