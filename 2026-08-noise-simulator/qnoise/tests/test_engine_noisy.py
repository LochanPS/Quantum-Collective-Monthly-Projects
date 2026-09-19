"""Phase 5 tests — noisy engine loop."""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import BitFlip, DensityMatrix, Depolarizing, NoiseModel, presets, run, run_ideal


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


# --------------------------------------------------------------------------- #
#  Per-qubit noise
# --------------------------------------------------------------------------- #


def test_qubit_limited_channel_only_hits_that_qubit():
    # A certain bit flip on qubit 1 only: |11> -> |01>, qubit 0 untouched.
    nm = NoiseModel().add_channel(BitFlip(1.0), gates=["X"], qubits=[1])
    qc = QuantumCircuit(2)
    qc.x(0).x(1)
    assert run(qc, nm).probabilities()[0b01] == pytest.approx(1.0)


def test_qubit_limited_channel_on_two_qubit_gate():
    # CNOT touches qubits 0 and 1; the channel is limited to qubit 0.
    nm = NoiseModel().add_channel(BitFlip(1.0), gates=["CNOT"], qubits=[0])
    qc = QuantumCircuit(2)
    qc.x(0).cnot(0, 1)  # ideal |11>
    assert run(qc, nm).probabilities()[0b10] == pytest.approx(1.0)


def test_bad_qubit_decoheres_more_than_its_neighbour():
    nm = (
        NoiseModel()
        .add_channel(Depolarizing(0.01))
        .add_channel(Depolarizing(0.3), qubits=[1])  # the bad qubit
    )
    qc = QuantumCircuit(2)
    qc.h(0).h(1)
    dm = run(qc, nm)
    rho = dm.matrix().reshape(2, 2, 2, 2)
    # Partial traces: axis order is (q1, q0, q1', q0').
    rho_q0 = np.einsum("aiaj->ij", rho)
    rho_q1 = np.einsum("iaja->ij", rho)
    purity_q0 = np.real(np.trace(rho_q0 @ rho_q0))
    purity_q1 = np.real(np.trace(rho_q1 @ rho_q1))
    assert purity_q1 < purity_q0 < 1.0


def test_unrestricted_channels_unchanged_by_per_qubit_api():
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    plain = NoiseModel().add_channel(Depolarizing(0.05))
    explicit = NoiseModel().add_channel(Depolarizing(0.05), qubits=[0, 1])
    assert np.allclose(run(qc, plain).matrix(), run(qc, explicit).matrix())


def test_channels_for_filters_by_qubit():
    ch_all, ch_bad = Depolarizing(0.01), Depolarizing(0.2)
    nm = NoiseModel().add_channel(ch_all, gates=["H"]).add_channel(ch_bad, gates=["H"], qubits=[2])
    assert nm.channels_for("H", 0) == [ch_all]
    assert nm.channels_for("H", 2) == [ch_all, ch_bad]
    assert nm.channels_for("H") == [ch_all, ch_bad]


@pytest.mark.parametrize("qubits", [[], [-1]])
def test_invalid_qubit_restriction_rejected(qubits):
    with pytest.raises(ValueError):
        NoiseModel().add_channel(Depolarizing(0.1), qubits=qubits)
