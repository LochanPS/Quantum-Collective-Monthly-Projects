# qcsim — Quantum Circuit Simulator

**Quantum Collective Monthly Project #1** · Pure Python + NumPy · Zero extra dependencies

**[Quick Start](#quick-start)** · **[Interactive TUI](#interactive-tui-circuit-builder)** · **[Python API](#python-api)** · **[Add a Gate](docs/adding-gates.md)** · **[Circuit Library](../circuit-library/README.md)**

---

## What is qcsim?

A quantum circuit simulator that works exactly like the ones inside Qiskit, Google Cirq, and Amazon Braket — implemented from scratch so you can read every line and understand how it works.

It simulates quantum circuits using the **state vector formalism**: the quantum state of N qubits is stored as 2^N complex numbers (amplitudes). Applying a gate = multiplying by a matrix. Measuring = sampling from the probability distribution.

**Two ways to use it:**
1. **Interactive visual builder** — launch `qcsim-interactive`, build circuits with arrow keys, no coding needed
2. **Python API** — `qc.h(0).cnot(0, 1).measure_all(shots=1024)` in your own scripts

---

## Repository Structure

```
2026-05-circuit-simulator/
│
├── qcsim/                        ← This package. Install with: pip install -e .
│   ├── qcsim/                    ← Source code
│   │   ├── circuit.py            Main simulator — QuantumCircuit class
│   │   ├── gates.py              All gate matrices (H, X, Y, Z, CNOT, Rx, ...)
│   │   ├── state.py              QuantumState — stores 2^N amplitudes
│   │   ├── tui.py                Interactive terminal circuit builder
│   │   ├── visualize.py          ASCII circuit diagrams, histograms, statevectors
│   │   ├── analyzer.py           Live metrics (depth, gate count, T-gates, entanglement)
│   │   ├── fingerprint.py        Circuit fingerprinting for deduplication
│   │   ├── patterns.py           Pattern recognition (Bell state, GHZ, etc.)
│   │   ├── search_cli.py         Entry point for qcsim-search command
│   │   ├── exceptions.py         Error types (QubitIndexError, GateError, etc.)
│   │   └── __init__.py           Public exports
│   ├── examples/                 ← Runnable example scripts
│   │   ├── bell_state.py         Bell state (simplest entangled circuit)
│   │   ├── ghz_state.py          GHZ state (multi-qubit entanglement)
│   │   ├── deutsch_jozsa.py      Deutsch-Jozsa algorithm
│   │   └── grover.py             Grover's search algorithm
│   ├── tests/                    ← 52 passing tests
│   │   ├── test_circuit.py       Core correctness tests
│   │   └── test_vs_qiskit.py     Optional: compare output against Qiskit
│   ├── docs/
│   │   └── adding-gates.md       Step-by-step guide to contributing new gates
│   ├── pyproject.toml            Package config, dependencies, entry points
│   └── README.md                 This file
│
└── circuit-library/              ← Community circuit library (sibling folder)
    ├── examples/                 Verified circuits as JSON files
    ├── search.py                 Search circuits by name, tags, difficulty
    ├── add_circuit.py            Submit a circuit with automatic deduplication
    ├── check_duplicates.py       CI check — prevents duplicate PRs
    ├── tags.json                 Canonical tag list
    ├── index.json                Auto-maintained manifest of all circuits
    └── CONTRIBUTING-CIRCUITS.md  How to submit circuits
```

---

## Quick Start

**Requirements:** Python 3.8+ and pip. Nothing else.

```bash
# Step 1 — Get the code
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-05-circuit-simulator/qcsim

# Step 2 — Install (editable mode: source changes take effect immediately)
pip install -e .

# Step 3 — Launch the interactive circuit builder
qcsim-interactive

# Or run a pre-built example
python examples/bell_state.py

# Or run the tests to verify everything works
pytest tests/ -v
```

**First circuit in Python:**
```python
from qcsim import QuantumCircuit, draw_statevector, draw_histogram

# Create a 2-qubit circuit
qc = QuantumCircuit(2)

# Build a Bell state: apply H to qubit 0, then CNOT with qubit 0 as control
qc.h(0).cnot(0, 1)

# See the circuit diagram
print(qc.draw())

# See the state vector (amplitudes)
print(draw_statevector(qc))

# Measure 1024 times and see the counts
counts = qc.measure_all(shots=1024)
print(draw_histogram(counts, shots=1024))
```

Output:
```
      ┌───┐
q[0]: ┤ H ├──●──
      └───┘  │
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

## Interactive TUI — Circuit Builder

The TUI (Terminal User Interface) lets you build quantum circuits visually without writing code. Think of it as a spreadsheet for quantum gates — rows are qubits, columns are time steps.

### Launch

```bash
qcsim-interactive
```

Or load an existing circuit from the library:
```bash
qcsim-interactive --load ../circuit-library/examples/bell-state.json
```

### Setup Screen

When you launch, you answer three questions:

```
  Number of qubits (1-15): [2]:    ← press Enter to use default [2], or type a number
  Number of columns  (1-20): [6]:  ← how many gate slots wide the circuit should be
  Backend — [K]ronecker or [T]ensor: ← K = default readable mode, T = faster for large circuits
```

After setup, the main builder screen appears.

### What the Screen Looks Like

```
  +-----------------------------------------+
  |   qcsim Interactive Circuit Builder      |
  +-----------------------------------------+
  Qubits: 2   Cols: 6   Backend: kronecker

  q[0]: -[ ]-  -[ ]-  -[ ]-  -[ ]-  -[ ]-  -[ ]-
                                
  q[1]: -[ ]-  -[ ]-  -[ ]-  -[ ]-  -[ ]-  -[ ]-

  Gates: 0  |  Depth: 0  |  2-qubit: 0  |  T-gates: 0  |  Qubits used: 0/2  |  Entangled: no

  Mode : NORMAL
  Pos  : q[0], col 0

  Gates : [H] [X] [C]NOT [W]AP  |  [Backspace] delete  |  [?] gate help
  Action: [R]un  [E]xport  [I]mport  [Esc] reset  [Q]uit
  Move  : Arrow keys
```

The cursor shows as `>[X]<` — double brackets with arrows. Empty cells show `[ ]`. Placed gates show their symbol inside the brackets.

### Moving Around

| Key | What it does |
|-----|-------------|
| `↑` `↓` | Move cursor between qubits (rows) |
| `←` `→` | Move cursor between columns |

### Placing Gates

| Key | Gate | What it does |
|-----|------|-------------|
| `H` | Hadamard | Creates superposition. `H\|0⟩ = (\|0⟩+\|1⟩)/√2` |
| `X` | Pauli-X | Flips the qubit. `X\|0⟩ = \|1⟩` |
| `C` | CNOT | Two-qubit gate — see below |
| `W` | SWAP | Two-qubit gate — see below |
| `Backspace` | Delete | Removes the gate at the cursor |

**Press `?`** on any cell to see that gate's matrix and explanation.

### Placing a CNOT Gate (Two Steps)

CNOT needs two qubits — a **target** and a **control**. Placement is a two-step process:

**Step 1:** Navigate to the qubit you want as the **target** (the one that gets flipped), press `C`.
- The cell shows `[+]` (target symbol), mode changes to `CNOT: press [C] on control qubit`

**Step 2:** Navigate to the qubit you want as the **control** (the one that triggers the flip), press `C` again.
- Both cells lock in. The control shows `[@]`, the target shows `[+]`, a `|` connector appears between them.

```
  q[0]: >[+]<        ← Step 1: you pressed C here (target)
  q[1]: -[ ]-        

  q[0]: -[+]-        ← Step 2: navigate to q[1], press C again (control)
         |
  q[1]: -[@]-
```

Both cells must be in the **same column**. If you press `C` in a different column, the first placement cancels.

### Placing a SWAP Gate (Two Steps)

Same two-step process as CNOT:

**Step 1:** Navigate to the first qubit, press `W` → shows `[~]`  
**Step 2:** Navigate to the second qubit (same column), press `W` → both show `[~]` with `|` connector

### The Info Panel

The line at the bottom updates every time you place or delete a gate:

```
  Gates: 5  |  Depth: 3  |  2-qubit: 2  |  T-gates: 0  |  Qubits used: 2/2  |  Entangled: YES
```

| Metric | What it means |
|--------|--------------|
| Gates | Total number of gates placed |
| Depth | Number of occupied columns (= circuit runtime on real QPU) |
| 2-qubit | CNOT + SWAP count — expensive on real hardware |
| T-gates | T + T† count — relevant for fault-tolerant quantum computing |
| Qubits used | How many qubits have at least one gate |
| Entangled | YES if any 2-qubit gate is present |

### Running the Circuit — `[R]`

Press `R` to simulate the circuit. The screen shows:

1. **Circuit diagram** — ASCII drawing of your gates
2. **Pattern recognition banner** (if circuit is recognized):
   ```
   +------------------------------------------------------+
   |             Pattern recognized: Bell State            |
   +------------------------------------------------------+
   ```
3. **State vector** — the 2^N complex amplitudes with probability bars
4. **Measurement histogram** — result of 2048 simulated measurements

Press Enter to return to the builder.

### Exporting a Circuit — `[E]`

Press `E` to save your circuit as a JSON file:

```
  Circuit name [untitled]: Bell State
  Save path [bell-state.json]: my-circuits/bell-state.json
```

The JSON file stores every gate, its position, and a fingerprint (unique ID for dedup).
You can share this file or submit it to the circuit library.

### Importing a Circuit — `[I]`

Press `I` to load a circuit from a JSON file:

```
  Path to .json file: ../circuit-library/examples/bell-state.json
```

The grid replaces with the loaded circuit. You can then edit it, run it, or re-export.

### Resetting — `[Esc]`

Clears all gates. Prompts for confirmation first.

### Quitting — `[Q]`

Exit the TUI. Prompts for confirmation first.

### Gate Help — `[?]`

Navigate to any gate (or empty cell) and press `?`. An overlay appears:

```
  +--------------------------------------------------------+
  |                    Hadamard Gate                        |
  +--------------------------------------------------------+
  | Matrix: [[1, 1], [1, -1]] / sqrt(2)                    |
  | H|0> = (|0> + |1>) / sqrt(2)  -- superposition         |
  | H|1> = (|0> - |1>) / sqrt(2)  -- superposition         |
  | H*H = Identity                                         |
  |                                                        |
  | Use: Starting point of nearly every quantum algorithm. |
  +--------------------------------------------------------+
```

Press any key to dismiss.

### Complete Keyboard Reference

| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` | Navigate the grid |
| `H` | Place Hadamard gate |
| `X` | Place Pauli-X gate |
| `C` | Place CNOT (first press = target, second press = control) |
| `W` | Place SWAP (first press = first qubit, second press = second qubit) |
| `Backspace` | Delete gate at cursor |
| `?` | Show gate help overlay |
| `R` | Run simulation |
| `E` | Export circuit to JSON |
| `I` | Import circuit from JSON |
| `Esc` | Reset (clear all gates) |
| `Q` | Quit |

---

## Searching the Circuit Library

```bash
# Show all circuits
qcsim-search

# Search by name
qcsim-search ghz
qcsim-search bell

# Filter by difficulty
qcsim-search --difficulty beginner
qcsim-search --difficulty intermediate

# Filter by category
qcsim-search --category entanglement
qcsim-search --category algorithm

# Filter by qubit count
qcsim-search --qubits 3

# Show only verified circuits
qcsim-search --verified

# Show descriptions and fingerprints
qcsim-search -v

# Search and open directly in TUI
qcsim-search bell --load

# List all available tags
qcsim-search --list-tags
```

---

## Python API

### Create a Circuit

```python
from qcsim import QuantumCircuit

qc = QuantumCircuit(2)                        # 2 qubits, start at |00⟩
qc = QuantumCircuit(2, backend="tensor")      # Use tensor backend (faster for 15+ qubits)
```

### Single-Qubit Gates

| Method | Gate | Effect on |0⟩ |
|--------|------|-----------|
| `qc.h(q)` | Hadamard | `(|0⟩+|1⟩)/√2` — superposition |
| `qc.x(q)` | Pauli-X | `|1⟩` — bit flip |
| `qc.y(q)` | Pauli-Y | `i|1⟩` |
| `qc.z(q)` | Pauli-Z | `|0⟩` (Z only affects `|1⟩`) |
| `qc.s(q)` | S gate | `|0⟩` (S adds phase to `|1⟩`) |
| `qc.sdg(q)` | Sdg gate | `|0⟩` (Sdg adds phase to `|1⟩`)|
| `qc.t(q)` | T gate | `|0⟩` (T adds π/4 phase to `|1⟩`) |
| `qc.sx(q)` | √X gate | Square root of X |
| `qc.sxdg(q)` | √X† gate | inverse of SX |
| `qc.rx(q, θ)` | Rx(θ) | Rotation around X-axis by θ radians |
| `qc.ry(q, θ)` | Ry(θ) | Rotation around Y-axis by θ radians |
| `qc.rz(q, θ)` | Rz(θ) | Rotation around Z-axis by θ radians |
| `qc.p(q, λ)` | Phase | Adds phase e^(iλ) to `|1⟩` |
| `qc.u(q, θ, φ, λ)` | Universal | Any single-qubit rotation |
| `qc.i(q)` | Identity | No-op |

### Two-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.cnot(ctrl, tgt)` | CNOT | Flips target qubit when control is `|1⟩` |
| `qc.cx(ctrl, tgt)` | CX | Same as CNOT |
| `qc.cy(ctrl, tgt)` | CY | Controlled-Y |
| `qc.cz(ctrl, tgt)` | CZ | Phase flip when both qubits are `|1⟩` |
| `qc.swap(a, b)` | SWAP | Exchanges the states of two qubits |
| `qc.cp(ctrl, tgt, λ)` | Controlled-Phase | Controlled phase rotation |

### Three-Qubit Gates

| Method | Gate | Effect |
|--------|------|--------|
| `qc.toffoli(c0, c1, tgt)` | Toffoli (CCX) | Flips target when BOTH controls are `|1⟩` |
| `qc.ccx(c0, c1, tgt)` | CCX | Same as Toffoli |

### Custom Gate (any unitary matrix)

```python
import numpy as np

# Any 2^k × 2^k unitary matrix applied to k qubits
U = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
qc.unitary(U, qubits=[0, 1], label="MyCNOT")
```

### Circuit Operations

```python
qc.barrier()            # Visual separator (no simulation effect)
qc.reset()              # Reset all qubits to |0⟩, clear all gates
qc_a.compose(qc_b)      # Append qc_b's gates onto qc_a
```

### Reading Results

```python
sv     = qc.statevector()           # np.ndarray of 2^N complex amplitudes
probs  = qc.probabilities()         # dict: {'00': 0.5, '11': 0.5}
counts = qc.measure_all(shots=1024) # dict: {'00': 512, '11': 512}
E      = qc.expectation_value(O)    # ⟨ψ|O|ψ⟩ for any Hermitian matrix O
```

State is preserved after `measure_all()` — call it as many times as you want.

### Method Chaining

Every gate method returns `self`, so you can chain:

```python
qc = QuantumCircuit(3)
qc.h(0).cnot(0, 1).cnot(1, 2)  # GHZ state
counts = qc.measure_all(shots=1024)
```

---

## Examples

Run these from the `qcsim/` directory:

```bash
python examples/bell_state.py       # 2-qubit entanglement
python examples/ghz_state.py        # 5-qubit entanglement
python examples/deutsch_jozsa.py    # Quantum algorithm: oracle classification
python examples/grover.py           # Quantum search algorithm
```

Each example prints: circuit diagram → state vector → measurement histogram.

---

## Tests

```bash
# Run all 52 tests
pytest tests/ -v

# Run with coverage
pip install pytest-cov
pytest tests/ -v --cov=qcsim

# Compare against Qiskit (requires: pip install qiskit qiskit-aer)
pytest tests/test_vs_qiskit.py -v
```

Tests cover: initial state, all gates, Bell/GHZ entanglement, SWAP/CZ/Toffoli, measurement statistics, circuit operations, error handling, algorithm correctness.

---

## Architecture

### How it Works

```
You call qc.h(0).cnot(0, 1)
          ↓
QuantumCircuit validates qubits, logs the operation
          ↓
Backend expands gate to full 2^N × 2^N matrix (Kronecker)
  OR contracts tensor axis (tensor backend)
          ↓
Matrix multiplied against the state vector
          ↓
State vector updated — 2^N complex amplitudes
          ↓
qc.measure_all() samples from |amplitude|² probabilities
```

### Two Backends

**Kronecker (default):**  
Expands each gate to a full `2^N × 2^N` matrix using Kronecker products, then multiplies.  
Readable, straightforward, matches textbook math.  
Practical limit: ~15 qubits (matrix gets large).

**Tensor:**  
Reshapes the state vector to shape `(2, 2, ..., 2)` — one dimension per qubit.  
Applies the gate by contracting along the target qubit's axis.  
Never builds the full matrix. Scales to 20+ qubits.  
Use with: `QuantumCircuit(n, backend="tensor")`

### Qubit Convention

Qubit 0 = **least significant bit** (rightmost in bitstrings). This matches Qiskit.
- `|01⟩` means q1=0, q0=1
- `|10⟩` means q1=1, q0=0

### Memory Usage

| Qubits | State vector | RAM |
|--------|-------------|-----|
| 10 | 1,024 amplitudes | ~16 KB |
| 15 | 32,768 amplitudes | ~512 KB |
| 20 | 1,048,576 amplitudes | ~16 MB |
| 25 | 33,554,432 amplitudes | ~512 MB |

---

## Contributing

Every contribution type below is welcome. Pick what matches your skill level.

---

### 🟢 No quantum knowledge needed

**Submit a circuit to the library**
Build anything in the TUI, press `E` to export, run `add_circuit.py`.
→ Full guide: **[../circuit-library/CONTRIBUTING-CIRCUITS.md](../circuit-library/CONTRIBUTING-CIRCUITS.md)**

```bash
qcsim-interactive
# build circuit → press E to export → enter name and path

python ../circuit-library/add_circuit.py my-circuit.json
git add ../circuit-library/ && git commit -m "feat(library): add My Circuit" && git push
```

**File a bug report**
Try to break it — wrong qubit index, negative shots, edge cases. Open a [GitHub Issue](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/issues).

**Improve error messages**
Find a Python traceback that could be a clean human-readable message. Fix in `qcsim/exceptions.py` + the relevant method.

**Fix or improve docs**
Anything confusing, wrong, or missing. Edit any `.md` file and open a PR.

---

### 🟡 Python, no quantum needed

**Wire existing gates to TUI keys**
Y, Z, S, T, CZ already exist in the Python API but have no keyboard shortcut in the TUI.
Add them in `qcsim/tui.py` — `_GATE_DISPLAY`, `_handle()`, `_gate_help()`, and `_to_qcsim()`.

**Add a new gate**
The 10-step guide handles everything. You just need the 2×2 matrix (look it up).
→ **[docs/adding-gates.md](docs/adding-gates.md)**

**Write more tests**
Edge cases, larger circuits, measurement statistics. Add to `tests/test_circuit.py`.

**Circuit library search improvements**
Add sort-by-gates, sort-by-newest, or full-text description search to `circuit-library/search.py`.

**CLI improvements**
Colorized output (`colorama`), progress bars on large circuits, better `--help` text.

---

### 🟡🟠 Python + some quantum intuition

**Add gates to TUI from Python API**
Gates that exist in `gates.py` but aren't in the TUI at all: `Y`, `Z`, `S`, `Sdg`, `T`, `Tdg`, `CZ`.

**Partial measurement**
`qc.measure(qubit)` — measure one qubit, collapse state, leave others in superposition.
Needs: project state onto `|0⟩` or `|1⟩` subspace for that qubit, renormalize.

**Gate inverse**
`qc.inverse()` — reverse all gates in the log and apply conjugate transpose of each matrix.

**Circuit equality checker**
`qc1 == qc2` — compare two circuits produce the same unitary (multiply all gate matrices, check equal up to global phase).

**Export to OpenQASM**
OpenQASM is the standard quantum assembly language. Export a qcsim circuit to `.qasm` format so it can run anywhere.

**Export to Qiskit**
Convert qcsim gate log → `qiskit.QuantumCircuit` so users can submit to real IBM hardware.

**Quantum teleportation example**
3-qubit worked example: prepare state, Bell measurement, classical correction.
Add as `examples/teleportation.py`.

**Quantum Fourier Transform**
Implement QFT as a reusable function: `from qcsim.algorithms import qft`.

**Grover's search (oracle-based)**
`grover(oracle_fn, num_qubits, iterations)` — generic Grover with any oracle.

---

### 🔴 Advanced

**Bloch sphere visualizer**
Single-qubit state as a point on a 3D sphere. Matplotlib, `mpl_toolkits.mplot3d`.
Extract `(θ, φ)` from qubit amplitudes: `α|0⟩ + β|1⟩ → θ = 2·arccos(|α|), φ = arg(β/α)`.

**Noise models**
`DepolarizingNoise`, `BitFlipNoise`, `T1T2Noise` — apply random errors after each gate.
Requires density matrix backend (see below).

**Density matrix backend**
`DensityMatrixCircuit` — represents state as 2^N × 2^N matrix instead of 2^N vector.
Required for: mixed states, noise simulation, partial traces.

**Circuit depth optimizer**
Reorder commuting gates to reduce circuit depth without changing the output unitary.
Commuting rule: gates on disjoint qubits always commute.

**GPU backend**
Replace `numpy` with `cupy` — drop-in swap, unlocks 30+ qubit simulation on any NVIDIA GPU.
`QuantumCircuit(n, backend="gpu")`.

**Matrix Product State (MPS) backend**
Represent state as a tensor network. Simulates hundreds of qubits for low-entanglement circuits.
Key reference: Vidal 2003 — efficient classical simulation of slightly entangled quantum computations.

**IBM Quantum integration**
`qc.run_on_ibm(api_token)` — convert to Qiskit circuit, submit to IBM free QPU tier, return real counts.

**Benchmarking suite**
Systematic comparison: qcsim (both backends) vs Qiskit vs Cirq — random circuits, varying depth and qubit count, plot runtime vs N.

**Quantum error correction**
Implement 3-qubit bit-flip code or surface code as a simulation. Research-level but very educational.

---

### Add a New Gate — Quick Reference

Full guide: **[docs/adding-gates.md](docs/adding-gates.md)**

```
1. Add matrix function to qcsim/gates.py
2. Add circuit method to qcsim/circuit.py
3. Update _replay_gate dispatch in circuit.py
4. Add display symbol to _GATE_DISPLAY in tui.py
5. Add key binding in _handle() in tui.py
6. Add gate help text in _gate_help() in tui.py
7. Add case in _to_qcsim() in tui.py
8. Write 3+ tests in tests/test_circuit.py
9. Update gate table in this README
10. PR title: feat(gates): add GATE_NAME
```

---

## Limitations

- Max ~20 qubits — state vector grows as 2^N
- No noise — pure quantum states only (see Density Matrix extension idea)
- Classical simulation — cannot run on real quantum hardware (yet)
- Kronecker backend: builds full matrix per gate, slow above 15 qubits → switch to `backend="tensor"`

---

## References

- Nielsen & Chuang, *Quantum Computation and Quantum Information* (Ch. 1–4)
- [Qiskit Textbook](https://qiskit.org/learn/) — free, interactive
- [Jarrod McClean's blog](https://jarrodmcclean.com/basic-quantum-circuit-simulation-in-python/) — concise pedagogical reference

---

**Quantum Collective** · [Discord](https://discord.gg/QW3yUpNd) · [GitHub](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects)
