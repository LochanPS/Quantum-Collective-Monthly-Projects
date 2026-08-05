"""Phase 7 tests — fidelity, trace distance, TVD."""

import numpy as np
import pytest

from qnoise import DensityMatrix, fidelity, trace_distance, tvd


def _dm(vec):
    return DensityMatrix.from_statevector(np.array(vec, dtype=complex))


def test_fidelity_identical_is_one():
    a = _dm([1, 0])
    assert fidelity(a, a) == pytest.approx(1.0)


def test_fidelity_orthogonal_is_zero():
    a = _dm([1, 0])
    b = _dm([0, 1])
    assert fidelity(a, b) == pytest.approx(0.0, abs=1e-9)


def test_fidelity_symmetric():
    a = _dm([1, 0])
    b = _dm([1, 1])
    assert fidelity(a, b) == pytest.approx(fidelity(b, a))


def test_fidelity_mixed_states():
    # Two different maximally-mixed vs pure: F(I/2, |0><0|) = 1/2.
    mixed = DensityMatrix.from_matrix(np.eye(2) / 2)
    pure = _dm([1, 0])
    assert fidelity(mixed, pure) == pytest.approx(0.5)
    # General mixed-mixed path (both non-pure) runs without the fast path.
    m2 = DensityMatrix.from_matrix(np.diag([0.7, 0.3]).astype(complex))
    assert 0.0 <= fidelity(mixed, m2) <= 1.0


def test_trace_distance_bounds():
    a = _dm([1, 0])
    assert trace_distance(a, a) == pytest.approx(0.0)
    b = _dm([0, 1])
    assert trace_distance(a, b) == pytest.approx(1.0)


def test_tvd_basic():
    assert tvd({"0": 1.0}, {"0": 1.0}) == pytest.approx(0.0)
    assert tvd({"0": 1.0}, {"1": 1.0}) == pytest.approx(1.0)
    assert tvd({"0": 0.5, "1": 0.5}, {"0": 0.4, "1": 0.6}) == pytest.approx(0.1)
