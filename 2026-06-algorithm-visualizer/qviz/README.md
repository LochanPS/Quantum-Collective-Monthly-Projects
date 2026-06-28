# qviz — Quantum Algorithm Visualizer

**Quantum Collective Monthly Project #2** · Depends on [qcsim](../../2026-05-circuit-simulator/qcsim/) · Terminal-only by design

## What is this?

Step through a quantum algorithm one gate at a time and watch the state vector evolve, instead of only seeing the final answer. Built on top of `qcsim` (Monthly Project #1) — any circuit `qcsim` can build, `qviz` can step through.

## Setup

```bash
# qcsim isn't on PyPI yet -- install it first from the sibling folder
pip install -e ../../2026-05-circuit-simulator/qcsim

# then install qviz
pip install -e .

# run the interactive stepper
qviz-step
```

## Reference algorithms

| Algorithm | Module | Notes |
|---|---|---|
| Deutsch-Jozsa | `qviz.algorithms.deutsch_jozsa` | constant vs. balanced oracle, any input size |
| Bernstein-Vazirani | `qviz.algorithms.bernstein_vazirani` | recovers a hidden bitstring, any length |
| Grover's search | `qviz.algorithms.grover` | v1 supports 2-qubit marked states only — generalizing to N qubits needs a multi-controlled-Z oracle, a good Advanced-tier contribution |
| Quantum Fourier Transform | `qviz.algorithms.qft_algorithm` | wraps qcsim's existing `qft()`; step annotations are intentionally generic right now — writing precise ones is a good Beginner-tier contribution |

## Architecture

- `stepper.py` — replays a circuit's gate log on a fresh state, snapshotting after every gate
- `render.py` — terminal rendering (statevector bars, progress circuit diagram), same visual style as qcsim's `visualize.py`
- `algorithms/` — each module returns `(circuit, annotations)`, one annotation string per gate
- `cli.py` — interactive step/back/jump terminal interface

## Python API

```python
from qcsim import QuantumCircuit
from qviz import step_through, render_step

qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

for step in step_through(qc):
    print(render_step(qc, step))
```

## Tests

```bash
pytest tests/ -v
```

25 passing tests: stepper correctness (final step matches circuit's actual final state, barriers produce no step, original circuit untouched), rendering, and per-algorithm correctness (including non-palindromic bitstring cases, which catch label-orientation bugs that symmetric test inputs like "11" or "101" would silently hide).

See the [challenge README](../README.md) for contribution tiers (Beginner through Expert) and what the paid Lab Suite extends this with.
