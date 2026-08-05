"""Phase 6 tests — measurement sampling, readout error, reset."""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import DensityMatrix, ReadoutError, presets, run, run_ideal, sample


def test_sample_counts_sum_to_shots():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    dm = run_ideal(qc)
    counts = sample(dm, shots=500, seed=0)
    assert sum(counts.values()) == 500
    # Bell state: only 00 and 11 appear.
    assert set(counts) <= {"00", "11"}


def test_sample_approximates_probabilities():
    qc = QuantumCircuit(1)
    qc.h(0)
    dm = run_ideal(qc)
    counts = sample(dm, shots=20000, seed=42)
    assert counts["0"] / 20000 == pytest.approx(0.5, abs=0.03)


def test_sample_deterministic_with_seed():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    dm = run_ideal(qc)
    a = sample(dm, shots=200, seed=7)
    b = sample(dm, shots=200, seed=7)
    assert a == b


def test_readout_error_distorts_perfect_distribution():
    # Perfect |00>, but readout flips 0->1 heavily: some 01/10/11 must appear.
    dm = DensityMatrix(2)  # |00>
    re = ReadoutError(p1_given_0=0.3, p0_given_1=0.0)
    counts = sample(dm, shots=5000, readout_error=re, seed=1)
    assert "00" in counts
    assert sum(v for k, v in counts.items() if k != "00") > 0


def test_readout_error_zero_is_noop():
    dm = DensityMatrix(2)
    re = ReadoutError(0.0, 0.0)
    counts = sample(dm, shots=1000, readout_error=re, seed=2)
    assert counts == {"00": 1000}


def test_readout_error_per_qubit_targets_right_bit():
    # |00>, only qubit 0 (rightmost) flips 0->1 with certainty.
    dm = DensityMatrix(2)
    re = ReadoutError(p1_given_0={0: 1.0}, p0_given_1=0.0)
    counts = sample(dm, shots=100, readout_error=re, seed=3)
    # Every shot reads '01' (q0=1, q1=0).
    assert counts == {"01": 100}


def test_reset_returns_qubit_to_ground():
    # X then reset -> back to |0>; density-matrix reset is deterministic.
    qc = QuantumCircuit(1)
    qc.x(0).reset(0)
    dm = run_ideal(qc)
    assert dm.probabilities()[0] == pytest.approx(1.0)
    assert dm.is_valid()


def test_reset_mid_circuit_with_noise_stays_valid():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1).reset(0).h(1)
    dm = run(qc, presets.light())
    assert dm.is_valid()
    assert dm.trace() == pytest.approx(1.0)
