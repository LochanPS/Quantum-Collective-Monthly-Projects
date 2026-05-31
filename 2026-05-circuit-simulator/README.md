# May 2026 — Quantum Circuit Simulator

**[→ Reference Implementation](qcsim/README.md)** · **[→ Circuit Library](circuit-library/README.md)** · **[→ Submit Solution](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)**

---

## What is this?

Build a **quantum circuit simulator** — a program that simulates what happens inside a quantum computer when you apply quantum gates to qubits.

The math works like this:
- A quantum state of N qubits = 2^N complex numbers called **amplitudes**
- Quantum gates are unitary matrices — applying a gate multiplies the state by a matrix
- Measuring a qubit gives a probabilistic result: probability = |amplitude|²

```
2 qubits: state = [a, b, c, d]  →  represents  a|00⟩ + b|01⟩ + c|10⟩ + d|11⟩
```

This is exactly how Qiskit's `StatevectorSimulator`, Google Cirq, and Amazon Braket work internally.

---

## What's Already Built

A **complete reference implementation** lives in this repo at [`qcsim/`](qcsim/).

It includes everything listed below. Study it, run it, extend it.

```bash
cd qcsim
pip install -e .
qcsim-interactive        # Interactive visual circuit builder
pytest tests/ -v         # Run 52 tests
```

**Currently implemented:**
- State vector simulation for up to 20 qubits
- Gates: H, X, CNOT, SWAP (interactive TUI), plus Y, Z, S, T, Rx, Ry, Rz, Toffoli, and 15+ more via Python API
- Two simulation backends: Kronecker expansion and tensor formalism
- Interactive terminal circuit builder (arrow keys + letter keys)
- Circuit diagram printer, statevector display, measurement histogram
- Community circuit library with search and deduplication
- 52 passing tests, Qiskit-compatible output

**[→ Full feature list and documentation](qcsim/README.md)**

---

## What You Can Build

The reference implementation is a foundation. Here's what's missing and what you can contribute — or build your own version with your own approach.

### Start Here — Core Features

Good first contributions if you're new to quantum computing:

- **More gates in the TUI** — Currently H, X, CNOT, SWAP are interactive. Add Y, Z, S, T as TUI keys
- **New single-qubit gates** — ISWAP, ECR, DCX, or any unitary 2×2 matrix
- **Partial measurement** — `qc.measure(qubit)` to measure a single qubit and collapse the state
- **Gate inverse** — `qc.inverse()` to reverse a circuit with conjugate-transposed gates
- **Circuit equality** — `qc1 == qc2` to compare two circuits gate-by-gate
- **More circuit library entries** — submit interesting circuits (Bell, GHZ variants, teleportation, etc.)

### Go Deeper — Extend the Simulator

Once you understand the core, these add real capability:

- **Bloch sphere visualisation** — single-qubit state as (θ, φ) on the Bloch sphere (Matplotlib)
- **Circuit depth optimiser** — reorder gates to reduce circuit depth without changing the output
- **Density matrix backend** — `DensityMatrixCircuit` class for mixed-state simulation
- **Noise models** — depolarizing channel, bit-flip, phase-flip, T1/T2 relaxation
  ```python
  qc = NoisyQuantumCircuit(2, noise=DepolarizingNoise(p=0.01))
  ```
- **Grover's algorithm** as a reusable built-in function for any oracle
- **Quantum Fourier Transform** as a reusable subroutine
- **Quantum teleportation** as a 3-qubit worked example

### Advanced — Push the Limits

Research-level extensions with real impact:

- **GPU acceleration** — replace NumPy with CuPy for 30+ qubit simulation on a GPU
- **Matrix Product State (MPS)** — tensor network representation for hundreds of qubits in low-entanglement circuits
- **Quantum error correction** — surface codes, stabilizer formalism, logical qubit simulation
- **IBM Quantum integration** — export qcsim circuits to Qiskit, run on real quantum hardware
- **Benchmarking suite** — systematic comparison of qcsim vs Qiskit vs Cirq for random circuits

---

## Minimum Requirements (for your own implementation)

If you're building from scratch (not extending the reference), your simulator must:

1. Bell state: `H(q0)` + `CNOT(q0, q1)` → ~50% `|00⟩` and ~50% `|11⟩`, nothing else
2. X gate: `X(q0)|0⟩` → `|1⟩` with probability 1.0
3. Probabilities always sum to 1.0
4. Your fork includes tests covering the above

See [`EXAMPLES.md`](EXAMPLES.md) for exact expected API and output format.

---

## How to Contribute

**Add a gate to the reference implementation:**
→ Follow the 10-step guide in [`qcsim/docs/adding-gates.md`](qcsim/docs/adding-gates.md)

**Submit a circuit to the library:**
→ Build in the TUI, export, run `add_circuit.py` — see [`circuit-library/CONTRIBUTING-CIRCUITS.md`](circuit-library/CONTRIBUTING-CIRCUITS.md)

**Submit your own simulator:**
→ Fork, build, post in [GitHub Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)

---

## Learning Resources

- **[qcsim source code](qcsim/qcsim/)** — best way to learn: read the implementation
- [Qiskit Textbook](https://qiskit.org/learn/) — free, interactive, code-first
- [Quantum Computing: An Applied Approach](https://link.springer.com/book/10.1007/978-3-030-23922-0) — textbook
- [3Blue1Brown Linear Algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) — math foundation
- [FAQ](../docs/FAQ.md) — common questions answered
