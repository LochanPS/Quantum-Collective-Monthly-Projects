"""Phase 3 tests — noise channels (Kraus operators)."""

import numpy as np
import pytest

from qnoise import (
    AmplitudeDamping,
    BitFlip,
    Depolarizing,
    DensityMatrix,
    GeneralizedAmplitudeDamping,
    PhaseDamping,
    PhaseFlip,
    apply_channel,
)

ALL_CHANNELS = [
    Depolarizing(0.1),
    Depolarizing(0.0),
    Depolarizing(1.0),
    BitFlip(0.3),
    PhaseFlip(0.3),
    AmplitudeDamping(0.4),
    PhaseDamping(0.4),
    GeneralizedAmplitudeDamping(0.4, 0.2),
    GeneralizedAmplitudeDamping(1.0, 1.0),
]


@pytest.mark.parametrize("ch", ALL_CHANNELS)
def test_completeness_relation(ch):
    # sum_k K_k^dagger K_k = I
    assert ch.is_trace_preserving()


@pytest.mark.parametrize("ch", ALL_CHANNELS)
def test_channel_preserves_trace_and_validity(ch):
    # Start from |+> so off-diagonals exist (exercises dephasing channels too).
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    dm = DensityMatrix.from_statevector(plus)
    apply_channel(dm, ch, 0)
    assert dm.trace() == pytest.approx(1.0)
    assert dm.is_valid()


def test_depolarizing_p1_gives_maximally_mixed():
    # Fully depolarizing a pure state -> I/2.
    dm = DensityMatrix.from_statevector(np.array([1, 0], dtype=complex))
    apply_channel(dm, Depolarizing(1.0), 0)
    assert np.allclose(dm.matrix(), np.eye(2) / 2)
    assert dm.purity() == pytest.approx(0.5)


def test_depolarizing_p0_is_identity():
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    dm = DensityMatrix.from_statevector(plus)
    before = dm.matrix()
    apply_channel(dm, Depolarizing(0.0), 0)
    assert np.allclose(dm.matrix(), before)


def test_amplitude_damping_gamma1_relaxes_to_ground():
    # |1> fully damped -> |0>.
    dm = DensityMatrix.from_statevector(np.array([0, 1], dtype=complex))
    apply_channel(dm, AmplitudeDamping(1.0), 0)
    expected = np.zeros((2, 2), dtype=complex)
    expected[0, 0] = 1.0
    assert np.allclose(dm.matrix(), expected)


def test_generalized_amplitude_damping_zero_temperature_matches_amplitude_damping():
    # No thermal excitation -> identical action to plain amplitude damping.
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    gad = DensityMatrix.from_statevector(plus)
    ad = DensityMatrix.from_statevector(plus)
    apply_channel(gad, GeneralizedAmplitudeDamping(0.3, 0.0), 0)
    apply_channel(ad, AmplitudeDamping(0.3), 0)
    assert np.allclose(gad.matrix(), ad.matrix())


@pytest.mark.parametrize("start", [[1, 0], [0, 1], [1, 1]])
def test_generalized_amplitude_damping_gamma1_gives_thermal_state(start):
    # Full relaxation forgets the input and lands on diag(1 - p_exc, p_exc).
    psi = np.array(start, dtype=complex) / np.linalg.norm(start)
    dm = DensityMatrix.from_statevector(psi)
    apply_channel(dm, GeneralizedAmplitudeDamping(1.0, 0.25), 0)
    assert np.allclose(dm.matrix(), np.diag([0.75, 0.25]))


def test_generalized_amplitude_damping_excites_ground_state():
    # Unlike plain amplitude damping, a warm bath can push |0> up to |1>.
    dm = DensityMatrix.from_statevector(np.array([1, 0], dtype=complex))
    apply_channel(dm, GeneralizedAmplitudeDamping(0.5, 0.2), 0)
    # P(1) = gamma * p_exc = 0.5 * 0.2
    assert dm.probabilities()[1] == pytest.approx(0.1)


def test_bit_flip_full_flips_population():
    dm = DensityMatrix.from_statevector(np.array([1, 0], dtype=complex))
    apply_channel(dm, BitFlip(1.0), 0)
    # |0><0| -> |1><1|
    assert dm.matrix()[1, 1] == pytest.approx(1.0)


def test_phase_damping_kills_coherence():
    # |+> under full phase damping -> diagonal I/2 (populations kept, phase gone).
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    dm = DensityMatrix.from_statevector(plus)
    apply_channel(dm, PhaseDamping(1.0), 0)
    assert dm.matrix()[0, 1] == pytest.approx(0.0)
    assert np.allclose(np.real(np.diag(dm.matrix())), [0.5, 0.5])


def test_invalid_rate_rejected():
    with pytest.raises(ValueError):
        Depolarizing(1.5)
    with pytest.raises(ValueError):
        AmplitudeDamping(-0.1)
    with pytest.raises(ValueError):
        GeneralizedAmplitudeDamping(0.5, 1.2)


def test_embed_targets_correct_qubit():
    # BitFlip(1.0) on qubit 1 of |00> should give |10> (index 2).
    dm = DensityMatrix(2)  # |00>
    apply_channel(dm, BitFlip(1.0), 1)
    assert dm.probabilities()[2] == pytest.approx(1.0)
