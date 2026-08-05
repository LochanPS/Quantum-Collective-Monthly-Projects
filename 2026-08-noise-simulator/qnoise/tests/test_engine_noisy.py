"""Phase 5 tests — noisy engine loop."""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import DensityMatrix, Depolarizing, NoiseModel, presets, run, run_ideal


def test_noise_off_matches_ideal():
    # run() with the ideal preset == run_ideal() == qcsim.
    qc = QuantumCircuit(3)
    qc.h(0).cnot(0, 1).cnot(1, 2)
    a = run(qc, presets.ideal()).matrix()
    b = run_ideal(qc).matrix()
    assert np.allclose(a, b)


def test_none_model_is_noiseless():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    dm = run(qc, None)
    assert dm.purity() == pytest.approx(1.0)


def test_depolarizing_bell_spreads_and_stays_valid():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    dm = run(qc, presets.depolarizing(0.05))
    probs = dm.probabilities_dict()
    # Leakage into the "wrong" outcomes appears.
    assert probs["01"] > 0.0
    assert probs["10"] > 0.0
    # Dominant outcomes still 00 and 11.
    assert probs["00"] > probs["01"]
    assert probs["11"] > probs["10"]
    # Physical state, purity dropped below 1.
    assert dm.is_valid()
    assert dm.purity() < 1.0
    assert dm.trace() == pytest.approx(1.0)


def test_more_noise_lowers_purity_monotonically():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    purities = [run(qc, presets.depolarizing(p)).purity() for p in (0.0, 0.05, 0.2)]
    assert purities[0] == pytest.approx(1.0)
    assert purities[0] > purities[1] > purities[2]


def test_channel_only_on_selected_gate():
    # Attach noise only to H; X-only circuit should stay pure.
    nm = NoiseModel().add_channel(Depolarizing(0.2), gates=["H"])
    qc = QuantumCircuit(1)
    qc.x(0)
    assert run(qc, nm).purity() == pytest.approx(1.0)
    # But an H circuit picks up the noise.
    qc2 = QuantumCircuit(1)
    qc2.h(0)
    assert run(qc2, nm).purity() < 1.0
