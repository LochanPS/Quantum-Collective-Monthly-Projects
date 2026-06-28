"""qviz — step-through visualizer for quantum algorithms.

Quantum Collective Monthly Project #2. Depends on qcsim (Monthly Project
#1) as a library: takes any QuantumCircuit built with qcsim, replays its
gate log one gate at a time, and snapshots the state at every step.

Quick start::

    from qcsim import QuantumCircuit
    from qviz import step_through
    from qviz.render import render_step

    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)

    for step in step_through(qc):
        print(render_step(step))
"""

from .render import render_progress_circuit, render_statevector, render_step
from .stepper import Step, apply_log_entry, step_through

__version__ = "0.1.0"
__author__ = "Quantum Collective"

__all__ = [
    "Step",
    "step_through",
    "apply_log_entry",
    "render_step",
    "render_statevector",
    "render_progress_circuit",
]
