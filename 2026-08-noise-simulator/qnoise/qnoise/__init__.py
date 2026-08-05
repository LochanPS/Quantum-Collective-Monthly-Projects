"""qnoise — Noisy Quantum Simulator
Quantum Collective Monthly Project #3

A density-matrix noise simulator built on top of qcsim. Take any circuit built
with qcsim, evolve it as a density matrix, and apply realistic hardware noise
(decoherence, gate error, readout error) to see what the circuit *actually*
does on an imperfect quantum device.

Two rules run the whole engine:
    - Apply a gate U:   rho -> U rho U^dagger
    - Apply noise:      rho -> sum_k K_k rho K_k^dagger   (Kraus operators)

Quick start (once the engine lands)::

    from qcsim import QuantumCircuit
    from qnoise import DensityMatrix

    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)

    rho = DensityMatrix.from_statevector(qc.statevector())
    print(rho.probabilities_dict())   # ideal Bell distribution

Convention: LSB (Qiskit-compatible), identical to qcsim — qubit 0 is the
rightmost bit in bitstrings.
"""

from .density import DensityMatrix
from .engine import run, run_ideal, apply_channel, embed_single, gate_unitary
from .channels import (
    NoiseChannel,
    Depolarizing,
    BitFlip,
    PhaseFlip,
    AmplitudeDamping,
    PhaseDamping,
)
from .model import NoiseModel
from . import model as presets
from .measure import ReadoutError, sample
from .metrics import fidelity, trace_distance, tvd

__version__ = "0.1.0"
__author__ = "Quantum Collective"

__all__ = [
    "DensityMatrix",
    # engine
    "run",
    "run_ideal",
    "apply_channel",
    "embed_single",
    "gate_unitary",
    # channels
    "NoiseChannel",
    "Depolarizing",
    "BitFlip",
    "PhaseFlip",
    "AmplitudeDamping",
    "PhaseDamping",
    # models
    "NoiseModel",
    "presets",
    # measurement
    "ReadoutError",
    "sample",
    # metrics
    "fidelity",
    "trace_distance",
    "tvd",
]
