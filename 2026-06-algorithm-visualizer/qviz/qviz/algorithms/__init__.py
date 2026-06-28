"""Reference algorithm modules for qviz.

Each module exposes a build function returning (circuit, annotations) --
a qcsim QuantumCircuit with the algorithm applied, and a list of
human-readable strings, one per gate, in the same order as the circuit's
gate log. Pass both to qviz.stepper.step_through() and attach annotations
by index to label each Step.
"""

from .bernstein_vazirani import bernstein_vazirani
from .deutsch_jozsa import deutsch_jozsa
from .grover import grover
from .qft_algorithm import qft_algorithm

__all__ = ["deutsch_jozsa", "bernstein_vazirani", "grover", "qft_algorithm"]
