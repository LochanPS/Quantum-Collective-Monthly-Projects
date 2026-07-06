# qviz — Quantum Algorithm Visualizer

**Quantum Collective Monthly Project #2**  
Built on top of **qcsim** (Monthly Project #1)  
Terminal-first, open-source quantum algorithm learning tool.

---

## Why qviz Exists

Most quantum simulators show only the final result.

For example:

```python
qc.h(0)
qc.cnot(0, 1)
```

produces a Bell state:

```text
(|00⟩ + |11⟩) / √2
```

But it doesn't show:

- Which gate created the superposition
- Which gate created the entanglement
- How the amplitudes evolved
- Why the algorithm works

qviz fills that gap.

Instead of showing only the final state, qviz replays a quantum circuit gate-by-gate and visualizes the state evolution at every step.

```text
Step 0: |00⟩

Step 1:
H(q0)

(|00⟩ + |10⟩)/√2

Step 2:
CNOT(q0,q1)

(|00⟩ + |11⟩)/√2
↑ Bell state created
```

---

## What qviz Provides

qviz is a terminal-based visualizer that can step through any circuit built using qcsim.

Features include:

- Gate-by-gate circuit replay
- State-vector evolution
- Probability visualizations
- Circuit rendering
- Measurement stage
- Execution summaries
- Algorithm-aware explanations
- Beginner and Advanced viewing modes

---

## Beginner vs Advanced Modes

### Beginner Mode

Designed for learning.

Shows:

- Probabilities
- Plain-English explanations
- Algorithm progress
- Measurement outcomes
- High-level intuition

Hides:

- Complex amplitudes
- Phase details
- Unnecessary mathematical notation

### Advanced Mode

Designed for deeper quantum understanding.

Shows:

- Full state vectors
- Complex amplitudes
- Phase information
- State changes
- Detailed algorithm internals

Includes:

- Windowed circuit rendering
- Phase-aware visualizations
- Register information

---

## Algorithms Included

| Algorithm | Description |
|------------|-------------|
| Deutsch–Jozsa | Distinguish constant vs balanced oracles |
| Bernstein–Vazirani | Recover a hidden bitstring |
| Grover Search | Find a marked state using amplitude amplification |
| Quantum Fourier Transform | Visualize Hadamards, phase rotations, and swaps |

---

## Documentation

Full documentation lives in `docs/`.

Start here:

| Topic | Document |
|---------|---------|
| Documentation Index | docs/README.md |
| Architecture | docs/Architecture.md |
| Developer Guide | docs/Developer-Guide.md |
| Algorithm Development | docs/Algorithm-Development.md |
| Rendering/UI Guide | docs/Rendering-Guide.md |
| API Reference | docs/API-Reference.md |
| Roadmap | docs/Roadmap.md |
| Contributing | docs/Contributing.md |
| FAQ | docs/FAQ.md |

---

## Installation

### Fresh Clone

```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git

cd Quantum-Collective-Monthly-Projects/2026-06-algorithm-visualizer/qviz

pip install -e ../../2026-05-circuit-simulator/qcsim
pip install -e .

qviz-step
```

### Updating an Existing Checkout

```bash
cd Quantum-Collective-Monthly-Projects

git pull origin main

cd 2026-06-algorithm-visualizer/qviz

pip install -e ../../2026-05-circuit-simulator/qcsim
pip install -e .

qviz-step
```

If `qviz-step` is missing after an update:

```bash
pip install -e .
```

to refresh the command-line entry point.

---

## Python API

```python
from qcsim import QuantumCircuit
from qviz import step_through, render_step

qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

steps = step_through(qc)

for i, step in enumerate(steps):
    prev = steps[i - 1] if i else None
    print(render_step(qc, step, prev=prev))
```

---

## Architecture

qviz is intentionally modular:

```text
cli.py
  ↓
render.py
  ↓
interpret.py / phases.py
  ↓
algorithms/
  ↓
stepper.py
  ↓
qcsim
```

This architecture cleanly separates the simulation engine, algorithm layer, interpretation layer, rendering layer, and CLI, making it straightforward to extend qviz with new algorithms, educational features, and terminal rendering improvements.

---

## Testing

Run:

```bash
pytest tests/ -v
```

Tests cover:

- Stepper correctness
- Rendering
- Measurement logic
- State interpretation
- Phase tracking
- Algorithm correctness
- Label orientation edge cases

---

## Contributing

There are contribution opportunities ranging from Beginner to Expert.

### Beginner

- Documentation improvements
- Better explanations
- Algorithm annotations
- Tutorials
- UI polish

### Intermediate

- New quantum algorithms
- Additional visualization modes
- Export functionality
- State comparison tools

### Advanced

- Generalized Grover oracles
- Algorithm verification tools
- Performance optimizations
- New rendering systems

See:

- `docs/Roadmap.md`
- `docs/Contributing.md`
- `docs/Algorithm-Development.md`

---

## Project Origins

qviz began as the July 2026 Quantum Collective challenge:

> Build a tool that shows how a quantum algorithm evolves, not just where it ends.

The project has since grown into a complete educational visualizer for learning and exploring quantum algorithms while remaining fully terminal-based and open source.

---

## Learning Resources

- qcsim source code
- Qiskit Textbook
- Quantum Algorithm Zoo
- Project documentation in `docs/`
