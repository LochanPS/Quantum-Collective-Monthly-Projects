"""Phase 1 tests — DensityMatrix core."""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import DensityMatrix


def test_ground_state_init():
    dm = DensityMatrix(2)
    rho = dm.matrix()
    assert rho.shape == (4, 4)
    # |00><00| — only the (0,0) entry is 1.
    expected = np.zeros((4, 4), dtype=complex)
    expected[0, 0] = 1.0
    assert np.allclose(rho, expected)
    assert dm.trace() == pytest.approx(1.0)
    assert dm.purity() == pytest.approx(1.0)
    assert dm.is_valid()


def test_from_statevector_matches_qcsim_probs():
    qc = QuantumCircuit(3)
    qc.h(0).cnot(0, 1).x(2)
    dm = DensityMatrix.from_statevector(qc.statevector())
    # Diagonal of rho must equal qcsim's own probabilities.
    qc_probs = qc.probabilities()  # dict bitstring -> prob
    for bitstring, prob in qc_probs.items():
        assert dm.probabilities_dict()[bitstring] == pytest.approx(prob, abs=1e-12)


def test_pure_state_has_purity_one():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)  # Bell state, pure
    dm = DensityMatrix.from_statevector(qc.statevector())
    assert dm.purity() == pytest.approx(1.0)
    assert dm.is_valid()


def test_maximally_mixed_state():
    # I/2 on one qubit: purity should be 1/2, trace 1.
    dm = DensityMatrix.from_matrix(np.eye(2) / 2)
    assert dm.trace() == pytest.approx(1.0)
    assert dm.purity() == pytest.approx(0.5)
    assert dm.is_valid()
    # Two-qubit maximally mixed: purity 1/4.
    dm4 = DensityMatrix.from_matrix(np.eye(4) / 4)
    assert dm4.purity() == pytest.approx(0.25)


def test_apply_unitary_matches_gate_on_statevector():
    # Applying H to |0> as a density matrix should give |+><+|.
    from qcsim import gates

    dm = DensityMatrix(1)
    dm.apply_unitary(gates.H())
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    expected = np.outer(plus, plus.conj())
    assert np.allclose(dm.matrix(), expected)
    assert dm.is_valid()


def test_invalid_matrix_detected():
    # Trace != 1 is not a valid density matrix.
    dm = DensityMatrix.from_matrix(np.array([[2, 0], [0, 0]], dtype=complex))
    assert not dm.is_valid()
    # Negative eigenvalue (trace 1 but not PSD).
    bad = np.array([[1.5, 0], [0, -0.5]], dtype=complex)
    assert not DensityMatrix.from_matrix(bad).is_valid()


def test_label_lsb_convention():
    dm = DensityMatrix(2)
    assert dm.label(2) == "10"  # q1=1, q0=0
    assert dm.label(1) == "01"  # q1=0, q0=1


def test_from_statevector_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        DensityMatrix.from_statevector(np.array([1, 0, 0], dtype=complex))
