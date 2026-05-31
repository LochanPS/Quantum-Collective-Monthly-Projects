# May 2026 — Quantum Circuit Simulator

**Submission deadline:** May 31, 2026  
**Submit here:** [Discussions → Submissions](../../../discussions/categories/submissions)

---

## The Challenge

Build a quantum circuit simulator using the **state vector formalism**.

Your simulator must:
1. Represent N-qubit quantum states as a vector of 2^N complex amplitudes
2. Apply quantum gates via matrix multiplication
3. Return measurement probabilities or sampled outcomes

This is the same approach used by Qiskit's `StatevectorSimulator` and Google's Cirq.

---

## Background

A quantum state of N qubits = 2^N complex numbers called **amplitudes**:

```
2 qubits: [a, b, c, d]  →  a|00⟩ + b|01⟩ + c|10⟩ + d|11⟩
```

Probability of measuring `|xy⟩` = `|amplitude|²`

Quantum **gates** are unitary matrices applied to the state vector:
- Single-qubit gate on qubit i → expand to full 2^N × 2^N matrix via Kronecker product (`np.kron`)
- Two-qubit gates (CNOT, SWAP) act on a pair of qubits

---

## Tiers

### Beginner
Up to 4 qubits.

- Gates: `H`, `X`, `CNOT`
- Output: `measure_all(shots)` → `{'00': 512, '11': 512}`
- Required test: Bell state gives ~50% `|00⟩`, ~50% `|11⟩`

### Intermediate
Up to 8 qubits.

- Gates: everything above + `Y`, `Z`, `S`, `T`, `SWAP`, `CZ`, `Rx`, `Ry`, `Rz`
- Chained API: `qc.h(0).cnot(0, 1).measure_all()`
- `statevector()` method returning raw amplitudes
- Bonus: circuit diagram printer

### Advanced
Pick one or more:

- 15+ qubit support without building full 2^N × 2^N matrices (tensor axis permutation)
- GPU acceleration (CuPy / JAX)
- Noise models (depolarizing, bit-flip)
- Grover's algorithm or QFT as built-in examples
- Benchmark against Qiskit's StatevectorSimulator

---

## Acceptance Criteria (all tiers)

- [ ] Bell state: `H(0)` + `CNOT(0,1)` → `|00⟩` and `|11⟩` each ~50%, no `|01⟩` or `|10⟩`
- [ ] X gate: `X(0)|0⟩` → `|1⟩` with probability 1.0
- [ ] Probabilities always sum to 1.0
- [ ] Your fork includes tests that cover the above

---

## Reference Implementation

A **complete, production-quality reference implementation** is available in this repo.

**[→ qcsim/ — Full reference implementation](qcsim/README.md)**

What it includes:
- 25+ gates, dual backends (Kronecker + tensor), 52 passing tests
- Interactive terminal circuit builder (`qcsim-interactive`)
- Community circuit library with search + dedup
- Pattern recognition, live circuit metrics, gate help overlays

```bash
cd qcsim
pip install -e .
qcsim-interactive        # Visual circuit builder
python examples/bell_state.py
pytest tests/ -v
```

Use it to:
- **Learn** — read the code to understand how each piece works
- **Compare** — check your implementation against known-correct outputs
- **Extend** — add gates, circuits, visualizations on top of the reference

---

## Expected API

See [`EXAMPLES.md`](EXAMPLES.md) for the expected usage patterns your implementation should match.

---

## Resources

- [Qiskit Textbook](https://qiskit.org/learn/) — free, interactive
- [Quantum Computing: An Applied Approach](https://link.springer.com/book/10.1007/978-3-030-23922-0)
- [Reference implementation](qcsim/README.md) — complete working simulator in this repo
- [Circuit library](circuit-library/README.md) — community circuits to test against
