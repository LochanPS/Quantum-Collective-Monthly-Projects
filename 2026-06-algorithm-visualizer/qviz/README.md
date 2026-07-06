# qviz — Quantum Algorithm Visualizer

**Quantum Collective Monthly Project #2** · Depends on [qcsim](../../2026-05-circuit-simulator/qcsim/) · Terminal-only by design

## What is this?

Step through a quantum algorithm one gate at a time and watch the state vector evolve, instead of only seeing the final answer. Built on top of `qcsim` (Monthly Project #1) — any circuit `qcsim` can build, `qviz` can step through.

Each step shows a **phase progress bar** (Preparation → Oracle → Diffusion/Interference/Transform), the gate's purpose *in the algorithm*, and a plain-English reading of what the state means. The run ends with a **measurement stage** (sampled histogram) and a **structured execution summary** (measured vs expected, success/fail, key takeaway).

Two genuinely different modes:
- **Beginner** — phase bar, plain "% chance" table, intuitive explanations. No amplitudes, no circuit clutter.
- **Advanced** — full complex amplitudes, phase column (multiples of π), change-highlighting, and a **windowed circuit** that shows only the current phase's gates (so long multi-iteration circuits don't sprawl).

Ancilla and input registers are visually split in the state labels (`ancilla|input`); zero-probability states can be hidden (auto-on for larger systems).

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
| Grover's search | `qviz.algorithms.grover` | v1 supports 2-qubit marked states only — generalizing to N qubits needs a multi-controlled-Z oracle, a good Advanced-tier contribution. Includes an amplitude-amplification-across-steps view |
| Quantum Fourier Transform | `qviz.algorithms.qft_algorithm` | wraps qcsim's `qft()`; annotates each Hadamard / controlled-phase (with angle) / swap. Naming which frequency each phase encodes is a good Beginner-tier contribution |

Each returns an `AlgorithmResult` (`circuit`, `annotations`, `phases`, `title`, `info`, `registers`, `summarize`, `outcome`) — see `qviz/algorithms/base.py`.

## Architecture

- `stepper.py` — replays a circuit's gate log on a fresh state, snapshotting after every gate
- `interpret.py` — plain-English state reading, phase labels, ranked non-zero states
- `phases.py` — groups per-step phase labels into segments (for the progress bar + windowed circuit)
- `render.py` — terminal rendering: amplitude/probability bars, phase column, change highlighting, phase progress bar, windowed circuit, measurement stage, execution summary, beginner/advanced layouts
- `algorithms/` — each module returns an `AlgorithmResult` (circuit + per-gate annotations + per-gate phase + info panel + registers + final summary + structured outcome)
- `cli.py` — interactive stepper: step/back/jump/autoplay, mode + hide-zeros toggles, loops back to the menu when done

## Python API

```python
from qcsim import QuantumCircuit
from qviz import step_through, render_step

qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

steps = step_through(qc)
for i, step in enumerate(steps):
    prev = steps[i - 1] if i else None
    print(render_step(qc, step, prev=prev, mode="advanced"))
```

## Tests

```bash
pytest tests/ -v
```

54 passing tests: stepper correctness (final step matches circuit's actual final state, barriers produce no step, original circuit untouched), rendering + beginner/advanced modes, state interpretation, phase/register/outcome structure, measurement sampling + execution summary, and per-algorithm correctness + summaries (including non-palindromic bitstring cases, which catch label-orientation bugs that symmetric test inputs like "11" or "101" would silently hide).

See the [challenge README](../README.md) for contribution tiers (Beginner through Expert) and what the paid Lab Suite extends this with.
