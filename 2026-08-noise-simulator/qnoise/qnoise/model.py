"""Noise models — bundle channels and attach them to gates.

A :class:`NoiseModel` maps gate names to the noise channels that fire after
those gates run. A channel can also be limited to certain qubits, which models a
"bad qubit" whose error rate is higher than its neighbours'. The engine consults
the model via :meth:`NoiseModel.channels_for`.

Presets (:func:`ideal`, :func:`light`, :func:`depolarizing`) return ready-made
models so a user can pick one instead of wiring channels by hand. Adding a
preset is a good first contribution.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

from .channels import AmplitudeDamping, Depolarizing, NoiseChannel, PhaseDamping
from .measure import ReadoutError

# Gate names qcsim uses for one- and two-qubit gates (for "apply to all gates").
_ONE_QUBIT_GATES = [
    "I", "H", "X", "Y", "Z", "S", "Sdg", "T", "Tdg", "SX", "SXdg",
    "Rx", "Ry", "Rz", "P", "U",
]
_TWO_QUBIT_GATES = ["CNOT", "CY", "CZ", "SWAP", "CP"]
_ALL_GATES = _ONE_QUBIT_GATES + _TWO_QUBIT_GATES + ["CCX"]


class NoiseModel:
    """A collection of noise channels attached to gate names."""

    def __init__(self) -> None:
        # gate name -> [(channel, qubits it is limited to, or None for all)]
        self._by_gate: Dict[str, List[Tuple[NoiseChannel, Optional[FrozenSet[int]]]]] = {}
        self.readout_error: Optional[ReadoutError] = None

    def add_channel(
        self,
        channel: NoiseChannel,
        gates: Optional[Iterable[str]] = None,
        qubits: Optional[Iterable[int]] = None,
    ) -> "NoiseModel":
        """Attach ``channel`` to the given gate names (default: all gates).

        Args:
            channel: The noise channel to add.
            gates: Gate names it applies after. ``None`` means every gate.
            qubits: Only fire on these qubits. ``None`` (default) means every
                qubit the gate touches. For a two-qubit gate, the channel
                fires on whichever of its qubits are in this set.

        Returns:
            ``self`` (chainable).

        Raises:
            ValueError: If ``qubits`` is given but empty, or has a negative index.
        """
        targets = list(gates) if gates is not None else list(_ALL_GATES)
        only: Optional[FrozenSet[int]] = None
        if qubits is not None:
            only = frozenset(qubits)
            if not only:
                raise ValueError("qubits must name at least one qubit (or be None for all)")
            if any(q < 0 for q in only):
                raise ValueError(f"qubit indices must be non-negative, got {sorted(only)}")
        for g in targets:
            self._by_gate.setdefault(g, []).append((channel, only))
        return self

    def channels_for(self, gate_name: str, qubit: Optional[int] = None) -> List[NoiseChannel]:
        """Return the channels that fire after ``gate_name`` (possibly empty).

        Args:
            gate_name: Gate name as it appears in the qcsim log.
            qubit: If given, only channels that fire on this qubit. If omitted,
                every channel attached to the gate, whatever its qubits.
        """
        attached = self._by_gate.get(gate_name, [])
        return [ch for ch, only in attached if qubit is None or only is None or qubit in only]

    def add_readout_error(
        self,
        p1_given_0: float = 0.0,
        p0_given_1: float = 0.0,
    ) -> "NoiseModel":
        """Attach classical measurement (readout) error to this model.

        Applied at sampling time, not during evolution. See
        :class:`qnoise.measure.ReadoutError`.

        Returns:
            ``self`` (chainable).
        """
        self.readout_error = ReadoutError(p1_given_0, p0_given_1)
        return self

    def __repr__(self) -> str:
        n = sum(len(v) for v in self._by_gate.values())
        return f"NoiseModel({n} channel attachments across {len(self._by_gate)} gates)"


# --------------------------------------------------------------------------- #
#  Presets
# --------------------------------------------------------------------------- #

def ideal() -> NoiseModel:
    """A no-op model. Running with it reproduces the noiseless result."""
    return NoiseModel()


def depolarizing(p: float, gates: Optional[Iterable[str]] = None) -> NoiseModel:
    """Depolarizing noise with rate ``p`` after every gate (or ``gates``)."""
    return NoiseModel().add_channel(Depolarizing(p), gates=gates)


def light() -> NoiseModel:
    """A mild, generic noise model: 1% depolarizing after every gate."""
    return NoiseModel().add_channel(Depolarizing(0.01))


def ibm_ish() -> NoiseModel:
    """A rough superconducting-style model: light depolarizing on 1-qubit gates,
    heavier on 2-qubit gates, some T1/T2 damping, plus readout error.

    Numbers are illustrative, not a real device calibration — see the Advanced
    roadmap for fitting a model to actual backend data.
    """
    nm = NoiseModel()
    nm.add_channel(Depolarizing(0.001), gates=_ONE_QUBIT_GATES)
    nm.add_channel(Depolarizing(0.01), gates=_TWO_QUBIT_GATES + ["CCX"])
    nm.add_channel(AmplitudeDamping(0.002), gates=_ONE_QUBIT_GATES)
    nm.add_channel(PhaseDamping(0.002), gates=_ONE_QUBIT_GATES)
    nm.add_readout_error(p1_given_0=0.01, p0_given_1=0.02)
    return nm


def ion_ish() -> NoiseModel:
    """A rough trapped-ion-style model: very low gate error, negligible 2-qubit
    penalty, small dephasing, low readout error. Illustrative only.
    """
    nm = NoiseModel()
    nm.add_channel(Depolarizing(0.0005))
    nm.add_channel(PhaseDamping(0.001), gates=_ONE_QUBIT_GATES)
    nm.add_readout_error(p1_given_0=0.002, p0_given_1=0.003)
    return nm
