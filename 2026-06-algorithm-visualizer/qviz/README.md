# qviz — Quantum Algorithm Visualizer

**Quantum Collective Monthly Project #2** · Depends on [qcsim](../../2026-05-circuit-simulator/qcsim/) · Terminal-only by design

## What is this?

Step through a quantum algorithm one gate at a time and watch the state vector evolve, instead of only seeing the final answer. Built on top of `qcsim` (Monthly Project #1) — any circuit `qcsim` can build, `qviz` can step through.

Each step shows a **phase progress bar** (Preparation → Oracle → Diffusion/Interference/Transform), the gate's purpose *in the algorithm*, and a plain-English reading of what the state means. The run ends with a **measurement stage** (sampled histogram) and a **structured execution summary** (measured vs expected, success/fail, key takeaway).

Two genuinely different modes:
- **Beginner** — phase bar, plain "% chance" table, intuitive explanations. No amplitudes, no circuit clutter.
- **Advanced** — full complex amplitudes, phase column (multiples of π), change-highlighting, and a **windowed circuit** that shows only the current phase's gates (so long multi-iteration circuits don't sprawl).

Ancilla and input registers are visually split in the state labels (`ancilla|input`); zero-probability states can be hidden (auto-on for larger systems).

## Documentation

Full docs live in **[docs/](docs/)** — start at the
**[documentation index](docs/README.md)**.

| Topic | Doc |
|---|---|
| How it fits together | [Architecture](docs/Architecture.md) |
| Contribute without getting stuck | [Developer Guide](docs/Developer-Guide.md) |
| Add a new algorithm | [Algorithm Development](docs/Algorithm-Development.md) |
| Change the terminal UI | [Rendering Guide](docs/Rendering-Guide.md) |
| Function/class signatures | [API Reference](docs/API-Reference.md) |
| Find something to build | [Roadmap](docs/Roadmap.md) |
| Workflow, formatting, tests | [Contributing](docs/Contributing.md) |
| Common pitfalls | [FAQ](docs/FAQ.md) |

## Setup

### First time (fresh clone)

```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-06-algorithm-visualizer/qviz

# qcsim isn't on PyPI yet -- install it first from the sibling folder
pip install -e ../../2026-05-circuit-simulator/qcsim

# then install qviz
pip install -e .

# run the interactive stepper
qviz-step
```

### Already have the repo / an older qcsim?

Pull the latest and reinstall both packages so you get the newest qcsim
gates and the qviz visualizer (both are installed with `-e`, so a `git
pull` picks up source changes automatically -- but re-run the installs if
dependencies or entry points changed):

```bash
cd Quantum-Collective-Monthly-Projects
git pull origin main

cd 2026-06-algorithm-visualizer/qviz
pip install -e ../../2026-05-circuit-simulator/qcsim   # refresh qcsim
pip install -e .                                        # refresh qviz

qviz-step
```

> If `qviz-step` isn't found after pulling, it means the entry point is new
> in your checkout -- just re-run `pip install -e .` above to register it.

## Reference algorithms

| Algorithm | Module | Notes |
|---|---|---|
| Deutsch-Jozsa | `qviz.algorithms.deutsch_jozsa` | constant vs. balanced oracle, any input size |
| Bernstein-Vazirani | `qviz.algorithms.bernstein_vazirani` | recovers a hidden bitstring, any length |
| Grover's search | `qviz.algorithms.grover` | v1 supports 2-qubit marked states only — generalizing to N qubits needs a multi-controlled-Z oracle, a good Advanced-tier contribution. Includes an amplitude-amplification-across-steps view |
| Quantum Fourier Transform | `qviz.algorithms.qft_algorithm` | wraps qcsim's `qft()`; annotates each Hadamard / controlled-phase (with angle) / swap. Naming which frequency each phase encodes is a good Beginner-tier contribution |

Each returns an `AlgorithmResult` (`circuit`, `annotations`, `phases`, `title`, `info`, `registers`, `summarize`, `outcome`) — see [Algorithm Development](docs/Algorithm-Development.md).

## Architecture (overview)

Four layers, each depending only on the ones below: `stepper.py` (replay
→ `Step`s) → `algorithms/` (build circuits, return `AlgorithmResult`) →
`interpret.py` + `phases.py` (meaning) → `render.py` (terminal output) →
`cli.py` (interactive UI). Full detail in
[docs/Architecture.md](docs/Architecture.md).

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

54 passing tests: stepper correctness, rendering + beginner/advanced modes, state interpretation, phase/register/outcome structure, measurement sampling + execution summary, and per-algorithm correctness (including non-palindromic bitstring cases that catch label-orientation bugs). See [Contributing](docs/Contributing.md) and [FAQ](docs/FAQ.md).

## Contributing

Pick something from the **[Roadmap](docs/Roadmap.md)** (Beginner →
Expert), then follow the **[Contributing guide](docs/Contributing.md)**.
New algorithm? → [Algorithm Development](docs/Algorithm-Development.md).
UI feature? → [Rendering Guide](docs/Rendering-Guide.md).

See the [challenge README](../README.md) for the challenge framing and
contribution tiers.
