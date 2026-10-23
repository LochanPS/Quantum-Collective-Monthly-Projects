"""Noise sweeps — run one circuit across a range of noise strengths.

:func:`sweep` returns structured data (one :class:`SweepPoint` per rate) so the
decay curve can be printed, plotted, or saved, instead of only rendered as a
terminal panel.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Union

from qcsim import QuantumCircuit

from .channels import NoiseChannel
from .engine import run, run_ideal
from .metrics import fidelity, trace_distance, tvd
from .model import NoiseModel


@dataclass(frozen=True)
class SweepPoint:
    """Metrics for the circuit run at one noise rate, compared with the ideal run."""

    rate: float
    fidelity: float
    trace_distance: float
    tvd: float
    purity: float


def sweep(
    qc: QuantumCircuit,
    noise: Callable[[float], Union[NoiseChannel, NoiseModel]],
    rates: Iterable[float],
) -> List[SweepPoint]:
    """Run ``qc`` once per rate and measure how far each result drifts from ideal.

    Args:
        qc: The circuit to evaluate.
        noise: Builds the noise for one rate. Either a channel factory, which is
            attached after every gate on every qubit (e.g. ``Depolarizing`` or
            ``lambda g: AmplitudeDamping(g)``), or a model factory (e.g.
            ``presets.depolarizing`` or your own ``lambda p: NoiseModel()...``).
        rates: Noise strengths to try, in the order they should be reported.

    Returns:
        One :class:`SweepPoint` per rate, in the same order as ``rates``.

    Raises:
        TypeError: If ``noise`` returns something other than a channel or model.

    Example:
        >>> from qnoise import Depolarizing, sweep
        >>> for pt in sweep(qc, Depolarizing, [0.0, 0.05, 0.1]):
        ...     print(pt.rate, round(pt.fidelity, 3))
    """
    ideal = run_ideal(qc)
    ideal_dist = ideal.probabilities_dict()
    points: List[SweepPoint] = []
    for rate in rates:
        built = noise(rate)
        if isinstance(built, NoiseChannel):
            model = NoiseModel().add_channel(built)
        elif isinstance(built, NoiseModel):
            model = built
        else:
            raise TypeError(
                f"noise({rate!r}) returned {type(built).__name__}; "
                "expected a NoiseChannel or NoiseModel"
            )
        noisy = run(qc, model)
        points.append(
            SweepPoint(
                rate=rate,
                fidelity=fidelity(ideal, noisy),
                trace_distance=trace_distance(ideal, noisy),
                tvd=tvd(ideal_dist, noisy.probabilities_dict()),
                purity=noisy.purity(),
            )
        )
    return points
