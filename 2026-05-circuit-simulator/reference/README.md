# qcsim — Quantum Circuit Simulator

**Quantum Collective Monthly Project #1**

A production-quality quantum circuit simulator built from scratch in pure Python + NumPy.
Production-grade backend + interactive terminal UI + community circuit library.

**Live now:** [Try it online](#quick-start) · [Build gates](#adding-gates) · [Share circuits](#circuit-library)

---

## Table of Contents

- [What is this?](#what-is-this)
- [Quick Start](#quick-start)
- **[🎮 Interactive TUI](#interactive-tui)** ← Start here for hands-on building
- [Core API](#api-reference)
- [Examples](#examples)
- [Architecture](#architecture)
- **[📚 Contributing](#contributing)** ← Add gates, submit circuits
- [Tests](#tests)
- [References](#references)

---

## What is this?

`qcsim` is a **production-ready quantum circuit simulator** using the state vector formalism:
the quantum state of N qubits is stored as 2^N complex amplitudes. Gates applied via matrix
multiplication. Measurement outcomes sampled from the probability distribution.

Same approach as Qiskit's `StatevectorSimulator`, Google Cirq, Amazon Braket — implemented
here from scratch so you can read, understand, and extend it.

**What makes qcsim different:**
- **Zero bloat:** NumPy only. No quantum-specific frameworks.
- **Readable code:** Matches the math directly. Learn how quantum simulation *actually works*.
- **Dual backends:** Kronecker expansion (readable) + tensor formalism (scales to 20+ qubits).
- **Interactive:** Terminal-based visual circuit builder — no CLI coding needed.
- **Community:** Circuit library + pattern recognition + searchable by difficulty/algorithm.

---

## Quick Start

**Prerequisites:** Python 3.8+ and pip. That's it.

```bash
# 1. Clone the repo
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-05-circuit-simulator/reference

# 2. Install (editable mode — changes to source reflect immediately)
pip install -e .

# 3. Launch the interactive circuit builder
qcsim-interactive

# 4. Or run the examples
python examples/bell_state.py
python examples/ghz_state.py
python examples/deutsch_jozsa.py
python examples/grover.py

# 5. Run the tests
pip install pytest
pytest tests/ -v
```

**First circuit (Python API):**
```python
from qcsim import QuantumCircuit, draw_statevector, draw_histogram, banner

print(banner())

# Bell state
qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

print(qc.draw())
print(draw_statevector(qc))

counts = qc.measure_all(shots=1024)
print(draw_histogram(counts, shots=1024))
```

Output:
```
 Circuit: 2 qubit(s)  2 gate(s)
═══════════════════════════════════

      ┌───┐
q[0]: ┤ H ├──●──
      └───┘  │
             │
q[1]: ───────⊕──

State Vector
════════════════════════════════════════════════════════
 |00>  +0.7071+0.0000i  ██████████░░░░░░░░░░   50.0%
 |11>  +0.7071+0.0000i  ██████████░░░░░░░░░░   50.0%
════════════════════════════════════════════════════════

Measurement Results  (1024 shots)
════════════════════════════════════════════════════════
 |00>  ████████████████░░░░░░░░░░░░░░░░   519   50.7%
 |11>  ███████████████░░░░░░░░░░░░░░░░░   505   49.3%
════════════════════════════════════════════════════════
```

---

## Interactive TUI

**Launch the visual circuit builder:**
```bash
qcsim-interactive
```

**What you get:**
- Grid-based circuit layout (rows = qubits, columns = gate positions)
- Arrow keys navigate, letter keys place gates
- Live info panel: depth, gate count, T-gate cost, entanglement status
- Gate help overlay: press `?` for matrix + explanation
- Pattern recognition: Run → circuit automatically identified (Bell State, GHZ, etc.)
- Export/import circuits as JSON
- Search library: `qcsim-search ghz --load` loads a circuit directly

**Keyboard:**
- Arrow keys: navigate
- `[H]` = Hadamard, `[X]` = Pauli-X, `[C]` = CNOT, `[W]` = SWAP
- `[?]` = gate help, `[R]` = run & measure, `[E]` = export, `[I]` = import
- `[Backspace]` = delete gate, `[Esc]` = reset, `[Q]` = quit

**Pre-load a circuit:**
```bash
qcsim-interactive --load circuit-library/examples/bell-state.json
```

---

## API Reference

### Circuit Creation

```python
qc = QuantumCircuit(num_qubits)              # 1–20 qubits, all start at |0⟩
qc = QuantumCircuit(num_qubits, backend="tensor")  # Tensor backend (faster for 15+ qubits)
```

### Single-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.h(q)` | Hadamard | `H\|0⟩ = (\|0⟩+\|1⟩)/√2` |
| `qc.x(q)` | Pauli-X | Flips `\|0⟩ ↔ \|1⟩` |
| `qc.y(q)` | Pauli-Y | `Y\|0⟩ = i\|1⟩` |
| `qc.z(q)` | Pauli-Z | `Z\|1⟩ = -\|1⟩` |
| `qc.s(q)` | S (√Z) | `S\|1⟩ = i\|1⟩` |
| `qc.t(q)` | T (√S) | `T\|1⟩ = e^(iπ/4)\|1⟩` |
| `qc.sx(q)` | SX (√X) | Square root of X |
| `qc.rx(q, θ)` | Rx(θ) | Rotation around X-axis by θ radians |
| `qc.ry(q, θ)` | Ry(θ) | Rotation around Y-axis by θ radians |
| `qc.rz(q, θ)` | Rz(θ) | Rotation around Z-axis by θ radians |
| `qc.p(q, λ)` | P(λ) | Phase gate: adds e^(iλ) to `\|1⟩` |
| `qc.u(q, θ, φ, λ)` | U | Generic single-qubit unitary |
| `qc.i(q)` | Identity | No-op placeholder |

### Two-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.cnot(ctrl, tgt)` | CNOT | Flips target when control is `\|1⟩` |
| `qc.cy(ctrl, tgt)` | CY | Controlled-Y |
| `qc.cz(ctrl, tgt)` | CZ | Phase flip when both are `\|1⟩` |
| `qc.swap(a, b)` | SWAP | Exchanges two qubit states |
| `qc.cp(ctrl, tgt, λ)` | CP | Controlled phase gate |

### Three-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.toffoli(c0, c1, tgt)` | CCX | Flips target when BOTH controls are `\|1⟩` |

### Circuit Operations

```python
qc.barrier()              # Visual separator (no physical effect)
qc.reset()                # Reset all qubits to |0⟩, clear gate log
qc_a.compose(qc_b)        # Append qc_b's gates to qc_a (in-place)
```

### Readout

```python
sv    = qc.statevector()         # np.ndarray of 2^N complex amplitudes
probs = qc.probabilities()       # dict {'00': 0.5, '11': 0.5}
counts = qc.measure_all(shots=1024)  # dict {'00': 512, '11': 512}
E      = qc.expectation_value(O)     # ⟨ψ|O|ψ⟩ for Hermitian O
```

**State is preserved after `measure_all()`** — call it multiple times safely.

### Method Chaining

All gate methods return `self`:
```python
qc = QuantumCircuit(3)
qc.h(0).cnot(0, 1).cnot(1, 2).toffoli(0, 1, 2)
```

---

## Examples

**Terminal UI examples:**
```bash
qcsim-interactive                           # Build a circuit from scratch
qcsim-search ghz --load                     # Search library, open in TUI
qcsim-search --difficulty beginner          # Find beginner circuits
```

**Python code examples:**
```bash
python examples/bell_state.py               # Bell state — superposition + entanglement
python examples/ghz_state.py                # GHZ state — 5-qubit entanglement
python examples/deutsch_jozsa.py            # Deutsch-Jozsa — quantum speed-up
python examples/grover.py                   # Grover's search — amplitude amplification
```

---

## Architecture

### State Vector Formalism

An N-qubit system is described by 2^N complex numbers called **amplitudes**:

```
2 qubits: [a₀₀, a₀₁, a₁₀, a₁₁]   →   a₀₀|00⟩ + a₀₁|01⟩ + a₁₀|10⟩ + a₁₁|11⟩
```

Probability of measuring state `|xy⟩` is `|amplitude|²`. All probabilities sum to 1.

### Qubit Convention — LSB (Qiskit-compatible)

Qubit 0 is the **least significant bit** (rightmost character in bitstrings):
- `'01'` means q1=0, q0=1
- `'10'` means q1=1, q0=0

This matches Qiskit's default — directly compare results.

### Backends

**Kronecker Expansion (default)**
- Full 2^N × 2^N matrix per gate
- Most readable; directly mirrors the math
- Practical limit: ~15 qubits

**Tensor Formalism**
- Reshape state to (2,)*N, contract along target axis
- No full matrix built — O(2^N) memory
- Scales to ~20+ qubits
- Use: `QuantumCircuit(num_qubits, backend="tensor")`

### Memory and Performance

| Qubits | State Vector Size | RAM |
|--------|-----------------|-----|
| 10 | 1,024 amplitudes | ~16 KB |
| 15 | 32,768 amplitudes | ~512 KB |
| 20 | 1,048,576 amplitudes | ~16 MB |
| 25 | 33,554,432 amplitudes | ~512 MB |

---

## Contributing

### Adding New Gates

**Full 10-step guide:** [`docs/adding-gates.md`](docs/adding-gates.md)

Quick summary:
1. Define gate matrix in `qcsim/gates.py`
2. Add circuit method in `qcsim/circuit.py`
3. Add TUI key binding in `qcsim/tui.py`
4. Write tests in `tests/test_circuit.py`
5. Update README gate table
6. Open a PR with title `feat(gates): add <GATE_NAME>`

**Read the full guide before submitting.** It covers unitarity checks, duplicate detection,
and gate help text.

### Circuit Library

**Submit a circuit to the community library.**

**Quick path:**
```bash
# 1. Build in the TUI
qcsim-interactive
# Build your circuit → press E to export

# 2. Submit to library
python circuit-library/add_circuit.py my-circuit.json

# 3. Open a PR
git add circuit-library/
git commit -m "feat(library): add My Circuit Name"
git push
```

**Full guide:** [`circuit-library/CONTRIBUTING-CIRCUITS.md`](../circuit-library/CONTRIBUTING-CIRCUITS.md)

Covers:
- Method 1: TUI export (recommended)
- Method 2: Write JSON directly
- JSON format reference
- How deduplication works
- Circuit ideas for beginners/intermediate/advanced

**Search the library:**
```bash
python circuit-library/search.py                    # Show all
python circuit-library/search.py ghz                # Search by name
python circuit-library/search.py --difficulty beginner  # By difficulty
python circuit-library/search.py --verified         # Only verified circuits
python circuit-library/search.py bell --load        # Search and open
```

---

## Tests

```bash
pytest tests/ -v                        # 52 tests — core correctness
pytest tests/test_vs_qiskit.py -v      # Optional: compare against Qiskit
```

Coverage:
- Initial state, norm preservation
- All single-qubit gates (identity, phase checks, unitarity)
- CNOT, CZ, SWAP (adjacent, non-adjacent, reversed qubits)
- Bell, GHZ, 5-qubit entangled states
- Toffoli correctness
- Measurement statistics
- Circuit operations (reset, compose)
- Error handling
- Algorithm correctness (Deutsch-Jozsa, Grover)

**Compare against Qiskit:**
```bash
pip install qiskit qiskit-aer
pytest tests/test_vs_qiskit.py -v
```

---

## Module Structure

```
reference/
├── qcsim/
│   ├── __init__.py           Public API surface
│   ├── circuit.py            QuantumCircuit — main simulation engine
│   ├── state.py              QuantumState — state vector storage
│   ├── gates.py              All gate matrices (H, X, Y, Z, Rx, ...)
│   ├── analyzer.py           Circuit metrics (depth, gate count, T-cost)
│   ├── fingerprint.py        Normalized circuit fingerprinting
│   ├── patterns.py           Pattern recognition (Bell, GHZ, ...)
│   ├── visualize.py          ASCII diagrams, histograms, statevectors
│   ├── tui.py                Interactive terminal circuit builder
│   ├── search_cli.py         Entry point for qcsim-search
│   └── exceptions.py         Custom exception hierarchy
├── examples/
│   ├── bell_state.py         Bell state circuit
│   ├── ghz_state.py          GHZ state (5-qubit)
│   ├── deutsch_jozsa.py      Deutsch-Jozsa algorithm
│   └── grover.py             Grover search
├── tests/
│   ├── test_circuit.py       52 tests — core functionality
│   └── test_vs_qiskit.py     Optional Qiskit comparison
├── docs/
│   └── adding-gates.md       Complete guide to adding new gates
└── README.md                 This file
```

Top-level (parent directory):
```
circuit-library/
├── examples/                 Bell state, GHZ, and other verified circuits
├── known_patterns.json       Fingerprints for pattern recognition
├── tags.json                 Canonical tag list (beginner, entanglement, etc.)
├── index.json                Auto-maintained circuit manifest
├── search.py                 Search library by name/tags/difficulty
├── add_circuit.py            Submit a circuit with deduplication
├── check_duplicates.py       CI gate — prevents duplicate submissions
└── CONTRIBUTING-CIRCUITS.md  Full guide to submitting circuits
```

---

## Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| State representation | State vector | Simple, exact, easy to understand |
| Primary backend | Kronecker expansion | Most readable; directly mirrors the math |
| Dual backends | Kronecker + tensor | Readable + scalable to 20+ qubits |
| Qubit convention | LSB (Qiskit-compatible) | Interoperable with Qiskit output |
| State after measurement | Preserved | Matches production simulator behavior |
| Max qubits | 20 | 2^20 ≈ 16 MB, practical on any laptop |
| Language | Python + NumPy | No exotic dependencies, readable |
| Error handling | warn + raise | Visible failures, not silent wrong answers |
| UI | Terminal TUI | Zero-dependency, works over SSH |
| Circuit library | Flat JSON + fingerprint dedup | Simple, scalable, no database needed |

---

## Limitations

- **Memory wall at ~20 qubits** — state vector requires 2^N complex128 amplitudes
- **Kronecker expansion** — builds full 2^N × 2^N unitary per gate (use tensor backend for >15q)
- **No noise** — pure state simulation only
- **Classical simulation** — cannot run on actual quantum hardware

---

## References

- Nielsen & Chuang, *Quantum Computation and Quantum Information* (Ch. 1–4)
- [Qiskit Textbook](https://qiskit.org/learn/) — free, interactive, code-first
- [Jarrod McClean's blog](https://jarrodmcclean.com/basic-quantum-circuit-simulation-in-python/) — compact pedagogical reference

---

## License

Apache-2.0 — build freely, share openly.

---

**Quantum Collective** · [Discord](https://discord.gg/QW3yUpNd) · [GitHub](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects)
