"""Phase 10 — property / invariant tests over randomized circuits."""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import DensityMatrix, Depolarizing, NoiseModel, presets, run, run_ideal

_1Q = ["h", "x", "y", "z", "s", "t", "sx"]
_PARAM = ["rx", "ry", "rz"]


def _random_circuit(num_qubits: int, depth: int, rng: np.random.Generator) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    for _ in range(depth):
        if num_qubits > 1 and rng.random() < 0.3:
            a, b = rng.choice(num_qubits, size=2, replace=False)
            getattr(qc, rng.choice(["cnot", "cz", "swap"]))(int(a), int(b))
        elif rng.random() < 0.3:
            q = int(rng.integers(num_qubits))
            getattr(qc, rng.choice(_PARAM))(q, float(rng.uniform(0, 2 * np.pi)))
        else:
            q = int(rng.integers(num_qubits))
            getattr(qc, rng.choice(_1Q))(q)
    return qc


@pytest.mark.parametrize("seed", range(8))
def test_noise_off_matches_qcsim_random(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(1, 4))
    qc = _random_circuit(n, depth=12, rng=rng)
    dm = run_ideal(qc)
    ref = qc.probabilities()
    got = dm.probabilities_dict()
    for bitstring, prob in ref.items():
        assert got.get(bitstring, 0.0) == pytest.approx(prob, abs=1e-10)
    assert dm.purity() == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("seed", range(8))
def test_any_noise_keeps_rho_valid_random(seed):
    rng = np.random.default_rng(100 + seed)
    n = int(rng.integers(1, 4))
    qc = _random_circuit(n, depth=10, rng=rng)
    p = float(rng.uniform(0.0, 0.3))
    dm = run(qc, presets.depolarizing(p))
    assert dm.trace() == pytest.approx(1.0, abs=1e-9)
    assert dm.is_valid()


def test_single_qubit_single_gate():
    qc = QuantumCircuit(1)
    qc.h(0)
    dm = run(qc, presets.depolarizing(0.1))
    assert dm.is_valid()
    assert dm.probabilities().sum() == pytest.approx(1.0)


def test_empty_circuit_is_ground_state():
    qc = QuantumCircuit(2)
    dm = run(qc, presets.light())
    assert dm.probabilities()[0] == pytest.approx(1.0)


def test_two_qubit_channel_applies_to_both_qubits():
    # Depolarizing attached to CNOT hits both control and target.
    nm = NoiseModel().add_channel(Depolarizing(0.2), gates=["CNOT"])
    qc = QuantumCircuit(2)
    qc.cnot(0, 1)  # acts on |00> -> |00>, but noise still fires on both qubits
    dm = run(qc, nm)
    assert dm.purity() < 1.0
    assert dm.is_valid()
