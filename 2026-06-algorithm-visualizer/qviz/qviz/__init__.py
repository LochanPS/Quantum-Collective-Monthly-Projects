"""qviz — step-through visualizer for quantum algorithms.

Quantum Collective Monthly Project #2. Depends on qcsim (Monthly Project
#1) as a library: takes any QuantumCircuit built with qcsim, replays its
gate log one gate at a time, and snapshots the state at every step.

Quick start::

    from qcsim import QuantumCircuit
    from qviz import step_through, render_step

    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)

    steps = step_through(qc)
    for i, step in enumerate(steps):
        prev = steps[i - 1] if i else None
        print(render_step(qc, step, prev=prev))
"""

from .algorithms import AlgorithmResult
from .interpret import interpret_state, nonzero_states, phase_label
from .render import render_progress_circuit, render_statevector, render_step
from .stepper import Step, apply_log_entry, step_through

__version__ = "0.2.0"
__author__ = "Quantum Collective"

__all__ = [
    "Step",
    "step_through",
    "apply_log_entry",
    "AlgorithmResult",
    "render_step",
    "render_statevector",
    "render_progress_circuit",
    "interpret_state",
    "nonzero_states",
    "phase_label",
]
