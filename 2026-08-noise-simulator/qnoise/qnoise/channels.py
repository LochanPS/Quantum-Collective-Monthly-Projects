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


class CoherentOverRotation(NoiseChannel):
    """Coherent over-rotation: every time it fires, the qubit is rotated by a
    small extra angle ``epsilon`` about ``axis`` (a miscalibrated gate).

    This is a *unitary* error, so it has a single Kraus operator:
        K0 = R_axis(epsilon) = exp(-i * epsilon * sigma_axis / 2)

    Unlike the stochastic channels above, it never mixes the state (purity
    stays 1). Its errors add up coherently: n applications rotate by
    ``n * epsilon``, so infidelity grows roughly like n^2 instead of n.
    """

    name = "coherent_over_rotation"

    _PAULI = {"x": _X, "y": _Y, "z": _Z}

    def __init__(self, epsilon: float, axis: str = "x") -> None:
        axis = axis.lower()
        if axis not in self._PAULI:
            raise ValueError(f"axis must be 'x', 'y' or 'z', got {axis!r}")
        self.epsilon = float(epsilon)
        self.axis = axis

    def kraus(self) -> List[np.ndarray]:
        half = self.epsilon / 2
        return [np.cos(half) * _I - 1j * np.sin(half) * self._PAULI[self.axis]]

    def __repr__(self) -> str:
        return f"CoherentOverRotation(epsilon={self.epsilon}, axis={self.axis!r})"
