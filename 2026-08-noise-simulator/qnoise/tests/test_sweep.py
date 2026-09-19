"""Noise sweep library function."""

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qnoise import (
    AmplitudeDamping,
    Depolarizing,
    NoiseModel,
    SweepPoint,
    fidelity,
    presets,
    run,
    run_ideal,
    sweep,
)


def _bell() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)
    return qc


def test_one_point_per_rate_in_order():
    rates = [0.2, 0.0, 0.1]
    points = sweep(_bell(), Depolarizing, rates)
    assert [pt.rate for pt in points] == rates
    assert all(isinstance(pt, SweepPoint) for pt in points)


def test_zero_rate_matches_ideal():
    (pt,) = sweep(_bell(), Depolarizing, [0.0])
    assert pt.fidelity == pytest.approx(1.0)
    assert pt.trace_distance == pytest.approx(0.0, abs=1e-9)
    assert pt.tvd == pytest.approx(0.0, abs=1e-9)
    assert pt.purity == pytest.approx(1.0)


def test_fidelity_falls_and_distances_grow_with_rate():
    points = sweep(_bell(), Depolarizing, [0.0, 0.05, 0.2, 0.5])
    fids = [pt.fidelity for pt in points]
    dists = [pt.trace_distance for pt in points]
    assert fids == sorted(fids, reverse=True)
    assert dists == sorted(dists)
    assert fids[-1] < fids[0]


def test_channel_factory_equals_all_gate_model():
    # A bare channel is attached after every gate, same as presets.depolarizing.
    a = sweep(_bell(), Depolarizing, [0.1])[0]
    b = sweep(_bell(), presets.depolarizing, [0.1])[0]
    assert a == b


def test_model_factory_matches_direct_run():
    qc = _bell()
    factory = lambda g: NoiseModel().add_channel(AmplitudeDamping(g), gates=["CNOT"])
    (pt,) = sweep(qc, factory, [0.3])
    noisy = run(qc, factory(0.3))
    assert pt.fidelity == pytest.approx(fidelity(run_ideal(qc), noisy))
    assert pt.purity == pytest.approx(noisy.purity())


def test_bad_factory_rejected():
    with pytest.raises(TypeError):
        sweep(_bell(), lambda p: p, [0.1])


def test_empty_rates_gives_empty_result():
    assert sweep(_bell(), Depolarizing, []) == []
