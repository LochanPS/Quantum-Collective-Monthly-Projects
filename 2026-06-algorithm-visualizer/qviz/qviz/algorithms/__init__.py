"""Reference algorithm modules for qviz.

Each module's build function returns an AlgorithmResult (see base.py):
a qcsim circuit, one annotation per gate, a title, an always-displayed
info panel, and a summarize() that states the algorithm's answer from the
final step. Pass the circuit to qviz.stepper.step_through() and attach the
annotations by index to label each Step.
"""

from .base import AlgorithmResult, input_register
from .bernstein_vazirani import bernstein_vazirani
from .deutsch_jozsa import deutsch_jozsa
from .grover import grover
from .qft_algorithm import qft_algorithm

__all__ = [
    "AlgorithmResult",
    "input_register",
    "deutsch_jozsa",
    "bernstein_vazirani",
    "grover",
    "qft_algorithm",
]
