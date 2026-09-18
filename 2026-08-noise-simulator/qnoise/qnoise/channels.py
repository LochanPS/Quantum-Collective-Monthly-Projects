"""Noise channels expressed as Kraus operators.

A noise channel transforms a density matrix as::

    rho -> sum_k K_k rho K_k^dagger

The set ``{K_k}`` are the channel's *Kraus operators*. Every physical noise
process in this project is defined by giving its Kraus operators. For a channel
to conserve probability (trace), the operators must satisfy the completeness
relation::

    sum_k K_k^dagger K_k = I

Channels here are **single-qubit**: each returns a list of 2x2 matrices, and the
engine embeds them on whichever qubit the channel acts on. Adding a new channel
is the headline contributor task — implement ``kraus()`` and you're done.
"""

from __future__ import annotations

from typing import List

import numpy as np

_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


class NoiseChannel:
    """Base class for a single-qubit noise channel.

    Subclasses implement :meth:`kraus`, returning a list of 2x2 complex arrays.
    """

    name: str = "channel"

    def kraus(self) -> List[np.ndarray]:
        """Return this channel's Kraus operators as a list of 2x2 matrices."""
        raise NotImplementedError

    def is_trace_preserving(self, tol: float = 1e-9) -> bool:
        """Check the completeness relation ``sum_k K_k^dagger K_k = I``."""
        total = sum(K.conj().T @ K for K in self.kraus())
        return bool(np.allclose(total, _I, atol=tol))

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class Depolarizing(NoiseChannel):
    """Depolarizing channel: with probability ``p`` the qubit is replaced by a
    completely random state (an equal mix of I, X, Y, Z errors).

    Kraus operators: {sqrt(1 - 3p/4) I, sqrt(p/4) X, sqrt(p/4) Y, sqrt(p/4) Z}.
    At ``p = 1`` a pure state becomes maximally mixed (I/2).
    """

    name = "depolarizing"

    def __init__(self, p: float) -> None:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"depolarizing p must be in [0, 1], got {p}")
        self.p = p

    def kraus(self) -> List[np.ndarray]:
        p = self.p
        return [
            np.sqrt(1 - 3 * p / 4) * _I,
            np.sqrt(p / 4) * _X,
            np.sqrt(p / 4) * _Y,
            np.sqrt(p / 4) * _Z,
        ]


class BitFlip(NoiseChannel):
    """Bit-flip channel: applies X with probability ``p``.

    Kraus operators: {sqrt(1 - p) I, sqrt(p) X}.
    """

    name = "bit_flip"

    def __init__(self, p: float) -> None:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"bit-flip p must be in [0, 1], got {p}")
        self.p = p

    def kraus(self) -> List[np.ndarray]:
        return [np.sqrt(1 - self.p) * _I, np.sqrt(self.p) * _X]


class PhaseFlip(NoiseChannel):
    """Phase-flip channel: applies Z with probability ``p``.

    Kraus operators: {sqrt(1 - p) I, sqrt(p) Z}.
    """

    name = "phase_flip"

    def __init__(self, p: float) -> None:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"phase-flip p must be in [0, 1], got {p}")
        self.p = p

    def kraus(self) -> List[np.ndarray]:
        return [np.sqrt(1 - self.p) * _I, np.sqrt(self.p) * _Z]


class AmplitudeDamping(NoiseChannel):
    """Amplitude-damping channel (T1 / energy decay): |1> relaxes to |0> with
    probability ``gamma``.

    Kraus operators:
        K0 = [[1, 0], [0, sqrt(1 - gamma)]]
        K1 = [[0, sqrt(gamma)], [0, 0]]
    """

    name = "amplitude_damping"

    def __init__(self, gamma: float) -> None:
        if not 0.0 <= gamma <= 1.0:
            raise ValueError(f"amplitude-damping gamma must be in [0, 1], got {gamma}")
        self.gamma = gamma

    def kraus(self) -> List[np.ndarray]:
        g = self.gamma
        k0 = np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=complex)
        k1 = np.array([[0, np.sqrt(g)], [0, 0]], dtype=complex)
        return [k0, k1]


class PhaseDamping(NoiseChannel):
    """Phase-damping channel (T2 / pure dephasing): loss of phase coherence
    without energy loss, parameter ``gamma``.

    Kraus operators:
        K0 = [[1, 0], [0, sqrt(1 - gamma)]]
        K1 = [[0, 0], [0, sqrt(gamma)]]
    """

    name = "phase_damping"

    def __init__(self, gamma: float) -> None:
        if not 0.0 <= gamma <= 1.0:
            raise ValueError(f"phase-damping gamma must be in [0, 1], got {gamma}")
        self.gamma = gamma

    def kraus(self) -> List[np.ndarray]:
        g = self.gamma
        k0 = np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=complex)
        k1 = np.array([[0, 0], [0, np.sqrt(g)]], dtype=complex)
        return [k0, k1]


class GeneralizedAmplitudeDamping(NoiseChannel):
    """Generalized amplitude-damping channel (T1 decay at non-zero temperature):
    the qubit relaxes with strength ``gamma`` toward a thermal state that has
    population ``excited_population`` in |1>, instead of toward pure |0>.

    Real qubits sit in a warm environment, so some relaxation events *excite*
    |0> -> |1> rather than decay |1> -> |0>. With ``p = 1 - excited_population``
    (Nielsen & Chuang, section 8.3.5), the Kraus operators are:
        K0 = sqrt(p)     [[1, 0], [0, sqrt(1 - gamma)]]
        K1 = sqrt(p)     [[0, sqrt(gamma)], [0, 0]]
        K2 = sqrt(1 - p) [[sqrt(1 - gamma), 0], [0, 1]]
        K3 = sqrt(1 - p) [[0, 0], [sqrt(gamma), 0]]

    ``excited_population = 0`` is exactly :class:`AmplitudeDamping`. At
    ``gamma = 1`` any input becomes the thermal state
    diag(1 - excited_population, excited_population).
    """

    name = "generalized_amplitude_damping"

    def __init__(self, gamma: float, excited_population: float) -> None:
        if not 0.0 <= gamma <= 1.0:
            raise ValueError(
                f"generalized amplitude-damping gamma must be in [0, 1], got {gamma}"
            )
        if not 0.0 <= excited_population <= 1.0:
            raise ValueError(f"excited_population must be in [0, 1], got {excited_population}")
        self.gamma = gamma
        self.excited_population = excited_population

    def kraus(self) -> List[np.ndarray]:
        g = self.gamma
        p = 1 - self.excited_population
        k0 = np.sqrt(p) * np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=complex)
        k1 = np.sqrt(p) * np.array([[0, np.sqrt(g)], [0, 0]], dtype=complex)
        k2 = np.sqrt(1 - p) * np.array([[np.sqrt(1 - g), 0], [0, 1]], dtype=complex)
        k3 = np.sqrt(1 - p) * np.array([[0, 0], [np.sqrt(g), 0]], dtype=complex)
        return [k0, k1, k2, k3]
