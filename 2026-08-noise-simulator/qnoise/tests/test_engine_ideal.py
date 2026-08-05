"""Phase 2 tests — noiseless replay must match qcsim exactly.

This is Minimum Requirement #5: with noise off, qnoise reproduces qcsim's
statevector result with no drift.
"""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import DensityMatrix
from qnoise.engine import gate_unitary, run_ideal


def _assert_matches_qcsim(qc: QuantumCircuit):
    dm = run_ideal(qc)
    assert dm.is_valid()
    # Ideal replay stays pure.
    assert dm.purity() == pytest.approx(1.0, abs=1e-9)
    # Diagonal == qcsim probabilities, bit-for-bit.
    ref = qc.probabilities()
    got = dm.probabilities_dict()
    assert set(ref) == set(got)
    for bitstring, prob in ref.items():
        assert got[bitstring] == pytest.approx(prob, abs=1e-12)


def test_bell_state():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    _assert_matches_qcsim(qc)


def test_ghz_state():
    qc = QuantumCircuit(3)
    qc.h(0).cnot(0, 1).cnot(1, 2)
    _assert_matches_qcsim(qc)


def test_single_qubit_rotations():
    qc = QuantumCircuit(1)
    qc.rx(0, 0.7).ry(0, 1.1).rz(0, 0.3)
    _assert_matches_qcsim(qc)


def test_mixed_gate_zoo():
    qc = QuantumCircuit(3)
    (
        qc.h(0)
        .t(0)
        .cnot(0, 1)
        .cz(1, 2)
        .swap(0, 2)
        .sx(1)
        .p(2, 0.9)
        .toffoli(0, 1, 2)
    )
    _assert_matches_qcsim(qc)


def test_barrier_is_skipped():
    qc = QuantumCircuit(2)
    qc.h(0).barrier().cnot(0, 1)
    _assert_matches_qcsim(qc)


def test_gate_unitary_is_unitary():
    U = gate_unitary("CNOT", [0, 1], None, 2)
    assert np.allclose(U @ U.conj().T, np.eye(4))
    # CNOT with control q0, target q1 (LSB): |01> -> |11>, i.e. index 1 -> 3.
    assert U[3, 1] == pytest.approx(1.0)


def test_reset_and_measure_skipped_without_error():
    # Non-unitary log entries must not crash the ideal replay.
    qc = QuantumCircuit(1)
    qc.x(0).reset(0).h(0)
    dm = run_ideal(qc)
    assert dm.is_valid()
