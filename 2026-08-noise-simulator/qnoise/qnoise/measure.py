"""Measurement sampling and readout (measurement) error.

A real quantum computer's *measurement* is imperfect: even a perfectly prepared
|0> is sometimes read as 1, and vice versa. That's readout error, and it
distorts the final histogram independently of any gate noise.

Sampling here reads the diagonal of the density matrix (the basis-state
probabilities) and draws shots from it, optionally flipping each sampled bit
according to a :class:`ReadoutError`.
"""

from __future__ import annotations

from typing import Dict, Optional, Union

import numpy as np

from .density import DensityMatrix


class ReadoutError:
    """Classical measurement error applied bit-by-bit at readout time.

    Parameterised by two conditional probabilities:
        - ``p1_given_0``: probability of reading 1 when the qubit is really 0.
        - ``p0_given_1``: probability of reading 0 when the qubit is really 1.

    Rates may be uniform (one float pair for all qubits) or per-qubit via a
    dict ``{qubit_index: (p1_given_0, p0_given_1)}``.
    """

    def __init__(
        self,
        p1_given_0: Union[float, Dict[int, float]] = 0.0,
        p0_given_1: Union[float, Dict[int, float]] = 0.0,
    ) -> None:
        self.p1_given_0 = p1_given_0
        self.p0_given_1 = p0_given_1

    def _rate(self, table: Union[float, Dict[int, float]], qubit: int) -> float:
        if isinstance(table, dict):
            return float(table.get(qubit, 0.0))
        return float(table)

    def apply_to_bitstring(self, bits: str, rng: np.random.Generator) -> str:
        """Return a possibly-corrupted copy of ``bits`` (LSB string).

        ``bits[-1]`` is qubit 0 (rightmost), matching the LSB convention.
        """
        n = len(bits)
        out = list(bits)
        for pos, ch in enumerate(bits):
            qubit = n - 1 - pos  # LSB: rightmost char is qubit 0
            if ch == "0":
                if rng.random() < self._rate(self.p1_given_0, qubit):
                    out[pos] = "1"
            else:
                if rng.random() < self._rate(self.p0_given_1, qubit):
                    out[pos] = "0"
        return "".join(out)

    def __repr__(self) -> str:
        return f"ReadoutError(p1_given_0={self.p1_given_0}, p0_given_1={self.p0_given_1})"


def sample(
    dm: DensityMatrix,
    shots: int = 1024,
    readout_error: Optional[ReadoutError] = None,
    seed: Optional[int] = None,
) -> Dict[str, int]:
    """Sample measurement outcomes from a density matrix.

    Draws ``shots`` outcomes from the diagonal of ``rho`` (the basis-state
    probabilities). If ``readout_error`` is given, each sampled bitstring is
    corrupted per its rates before being counted.

    Args:
        dm: The state to measure.
        shots: Number of measurement repetitions.
        readout_error: Optional classical measurement error.
        seed: Optional RNG seed for reproducibility.

    Returns:
        Dict mapping bitstring (LSB convention) to count. Counts sum to ``shots``.
    """
    rng = np.random.default_rng(seed)
    probs = dm.probabilities()
    probs = np.clip(probs, 0.0, None)
    total = probs.sum()
    if total <= 0:
        raise ValueError("density matrix has zero total probability")
    probs = probs / total

    draws = rng.choice(dm.dim, size=shots, p=probs)
    counts: Dict[str, int] = {}
    for idx in draws:
        bits = dm.label(int(idx))
        if readout_error is not None:
            bits = readout_error.apply_to_bitstring(bits, rng)
        counts[bits] = counts.get(bits, 0) + 1
    return counts
