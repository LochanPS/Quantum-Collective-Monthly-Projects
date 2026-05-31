# qcsim — Quantum Circuit Simulator

**Quantum Collective Monthly Project #1**

A production-quality, dependency-light quantum circuit simulator built from scratch
in pure Python + NumPy. Designed to be read, understood, and built upon.

---

## What is this?

`qcsim` simulates quantum circuits using the **state vector formalism**: the quantum
state of N qubits is stored as 2^N complex amplitudes. Gates are applied by matrix
multiplication. Measurement outcomes are sampled from the resulting probability
distribution.

This is the same approach used internally by Qiskit's `StatevectorSimulator`, Google's
Cirq, and Amazon Braket — implemented here from scratch so you can see exactly how it
works.

---

## Quick Start

```bash
pip install -e .
```

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

## Architecture

### State Vector Formalism

An N-qubit system is described by 2^N complex numbers called **amplitudes**:

```
2 qubits: [a₀₀, a₀₁, a₁₀, a₁₁]   →   a₀₀|00⟩ + a₀₁|01⟩ + a₁₀|10⟩ + a₁₁|11⟩
```

The probability of measuring state `|xy⟩` is `|amplitude|²`. All probabilities sum to 1.

### Qubit Convention — LSB (Qiskit-compatible)

Qubit 0 is the **least significant bit** (rightmost character in bitstrings):
- `'01'` means q1=0, q0=1
- `'10'` means q1=1, q0=0

This matches Qiskit's default convention — you can directly compare results.

### Gate Application — Kronecker Product Expansion

To apply a 2×2 gate G to qubit k in an N-qubit system, we expand it to the full
2^N × 2^N operator:

```
Full operator = I_{N-1} ⊗ ... ⊗ G_k ⊗ ... ⊗ I_0
```

In NumPy terms:
```python
ops = [np.eye(2)] * N
ops[N - 1 - k] = G          # qubit 0 is rightmost Kronecker factor (LSB)
full_U = reduce(np.kron, ops)
new_state = full_U @ state
```

For **controlled gates** (CNOT, CZ, Toffoli), we use the projector decomposition:

```
CNOT = |0⟩⟨0|_ctrl ⊗ I_tgt  +  |1⟩⟨1|_ctrl ⊗ X_tgt
```

This handles non-adjacent qubits naturally — no SWAP routing needed.

### Memory and Performance

| Qubits | State Vector Size | RAM |
|--------|-----------------|-----|
| 10 | 1,024 amplitudes | ~16 KB |
| 15 | 32,768 amplitudes | ~512 KB |
| 20 | 1,048,576 amplitudes | ~16 MB |
| 25 | 33,554,432 amplitudes | ~512 MB |

The Kronecker expansion builds a 2^N × 2^N matrix per gate (O(4^N) memory during
gate application). This is the bottleneck for larger circuits.

**Practical limit: ~15 qubits** with the current Kronecker approach. **Up to 20 qubits**
if you apply gates without materialising the full unitary (tensor axis permutation —
a natural extension for contributors).

---

## API Reference

### Circuit Creation

```python
qc = QuantumCircuit(num_qubits)   # 1–20 qubits, all start at |0⟩
```

### Single-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.h(q)` | Hadamard | `H\|0⟩ = (\|0⟩+\|1⟩)/√2` |
| `qc.x(q)` | Pauli-X | Flips `\|0⟩ ↔ \|1⟩` |
| `qc.y(q)` | Pauli-Y | `Y\|0⟩ = i\|1⟩` |
| `qc.z(q)` | Pauli-Z | `Z\|1⟩ = -\|1⟩` |
| `qc.s(q)` | S (√Z) | `S\|1⟩ = i\|1⟩` |
| `qc.sdg(q)` | S† | Inverse of S |
| `qc.t(q)` | T (√S) | `T\|1⟩ = e^(iπ/4)\|1⟩` |
| `qc.tdg(q)` | T† | Inverse of T |
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
| `qc.cx(ctrl, tgt)` | CX | Alias for CNOT |
| `qc.cy(ctrl, tgt)` | CY | Controlled-Y |
| `qc.cz(ctrl, tgt)` | CZ | Phase flip when both are `\|1⟩` |
| `qc.swap(a, b)` | SWAP | Exchanges two qubit states |
| `qc.cp(ctrl, tgt, λ)` | CP | Controlled phase gate |

### Three-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.toffoli(c0, c1, tgt)` | CCX | Flips target when BOTH controls are `\|1⟩` |
| `qc.ccx(c0, c1, tgt)` | CCX | Alias for Toffoli |

### Custom Gate

```python
import numpy as np

# Apply any 2^k × 2^k unitary matrix to k qubits
U = np.array([[1, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 0, 1],
              [0, 0, 1, 0]], dtype=complex)  # CNOT matrix
qc.unitary(U, qubits=[0, 1], label="MyCNOT")
```

### Circuit Operations

```python
qc.barrier()              # Visual separator (no physical effect)
qc.barrier(label="foo")   # Labelled barrier
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
qc.h(0).cnot(0, 1).cnot(1, 2).barrier().toffoli(0, 1, 2)
```

---

## Examples

```bash
python examples/bell_state.py       # Bell state — superposition + entanglement
python examples/ghz_state.py        # GHZ state — 5-qubit entanglement
python examples/deutsch_jozsa.py    # Deutsch-Jozsa — quantum speed-up
python examples/grover.py           # Grover's search — amplitude amplification
```

---

## Tests

```bash
pytest tests/ -v                        # 52 tests — core correctness
pytest tests/test_vs_qiskit.py -v      # Optional: compare against Qiskit
```

The test suite covers:
- Initial state, norm preservation
- All single-qubit gates (identity checks, phase checks, unitarity)
- CNOT on adjacent, non-adjacent, and reversed qubits
- Bell, GHZ, 5-qubit entangled states
- SWAP, CZ, Toffoli correctness
- 5-qubit circuits
- Measurement statistics (sampling quality)
- Circuit operations (reset, compose)
- Error handling (invalid qubit index, same-qubit gates, invalid shots)
- Algorithm correctness (Deutsch-Jozsa, Grover)

### Comparing against Qiskit

```bash
pip install qiskit qiskit-aer
pytest tests/test_vs_qiskit.py -v
```

This runs 7 circuits through both qcsim and Qiskit's StatevectorSimulator and
compares statevectors up to global phase. Proves numerical equivalence.

---

## Building on Top of qcsim

This is the base. Here is what contributors can and should add:

### Beginner Extensions

- **More single-qubit gates**: ISWAP, ECR, DCX
- **Gate inverse**: `qc.inverse()` — reverse the circuit with conjugate-transposed gates
- **Partial measurement**: `qc.measure(qubit)` — measure a single qubit, collapse state
- **Circuit equality**: `qc1 == qc2` — compare two circuits gate-by-gate

### Intermediate Extensions

- **Tensor axis permutation**: Replace Kronecker expansion with the tensor reshape method
  for gates on any qubits — avoids building the 2^N × 2^N matrix entirely:
  ```python
  psi = psi.reshape([2]*N)
  psi = np.tensordot(G, psi, axes=[[1],[N-1-k]])
  psi = np.moveaxis(psi, 0, N-1-k)
  psi = psi.reshape(2**N)
  ```
  This alone extends practical limits from ~15 to ~25 qubits on a laptop.

- **Circuit visualiser improvements**: Multi-column gate alignment, parametric gate display, gate counts per qubit

- **Bloch sphere**: Single-qubit state → (θ, φ) angles on the Bloch sphere

- **Density matrix**: Add `DensityMatrixCircuit` class for mixed-state / noisy simulation

### Advanced Extensions

- **Noise models**: Depolarizing channel, bit-flip, phase-flip, T1/T2 relaxation
  ```python
  qc = NoisyQuantumCircuit(2, noise=DepolarizingNoise(p=0.01))
  ```

- **GPU acceleration**: Replace NumPy with CuPy for GPU-accelerated gate application —
  can simulate 30+ qubits on an A100

- **Matrix Product State (MPS)**: Represent the state as a tensor network — simulates
  hundreds of qubits for low-entanglement circuits

- **Quantum error correction**: Surface codes, stabilizer formalism (use qcsim to
  simulate logical qubits built from physical qubits)

- **Interactive visualiser**: Matplotlib or Plotly-based animated circuit + Bloch sphere

- **Benchmarking suite**: Systematic comparison of qcsim vs Qiskit vs Cirq for
  random circuits at various depths and qubit counts

### How to Submit Your Extension

1. Fork this repo
2. Build your solution in your fork
3. Post in [Discussions → Submissions](../../../discussions/categories/submissions):
   - Link to your fork
   - Which tier (Beginner / Intermediate / Advanced)
   - 2–3 sentence description of your approach

---

## Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| State representation | State vector | Simple, exact, easy to understand |
| Gate method | Kronecker expansion | Most readable; directly mirrors the math |
| Qubit convention | LSB (Qiskit-compatible) | Interoperable with Qiskit output |
| State after measurement | Preserved | Matches production simulator behavior |
| Max qubits | 20 | 2^20 ≈ 16 MB, practical on any laptop |
| Language | Python + NumPy | No exotic dependencies, readable |
| Error handling | warn + raise | Visible failures, not silent wrong answers |

---

## Module Structure

```
qcsim/
├── __init__.py       Public API surface
├── exceptions.py     Custom exception hierarchy (QCSimError, QubitIndexError, ...)
├── state.py          QuantumState — state vector storage and access
├── gates.py          All gate matrices as numpy functions (H, X, Y, Z, Rx, ...)
├── circuit.py        QuantumCircuit — the main simulation engine
└── visualize.py      ASCII diagrams, histograms, statevector display
```

---

## Limitations

- **Memory wall at ~20 qubits** — state vector requires 2^N complex128 amplitudes
- **Kronecker expansion** — builds full 2^N × 2^N unitary per gate; bottleneck above ~15 qubits
- **No noise** — pure state simulation only; see Density Matrix extension for noisy circuits
- **Classical simulation** — cannot run on actual quantum hardware

---

## References

- Nielsen & Chuang, *Quantum Computation and Quantum Information* (Ch. 1–4)
- [Qiskit Textbook](https://qiskit.org/learn/) — free, interactive, code-first
- [arXiv:2506.08142](https://arxiv.org/abs/2506.08142) — "How to Write a Simulator for Quantum Circuits from Scratch"
- [Jarrod McClean's blog](https://jarrodmcclean.com/basic-quantum-circuit-simulation-in-python/) — compact pedagogical reference

---

## License

Apache-2.0 — build freely, share openly.

---

**Quantum Collective** · [Discord](https://discord.gg/QW3yUpNd) · [WhatsApp](https://chat.whatsapp.com/KK2cx4st54uJONp0f8BWdS) · [LinkedIn](https://www.linkedin.com/company/113013769/)
