# Quantum Collective Circuit Library

An ever-growing community library of quantum circuits built with qcsim.
Every circuit is a JSON file that anyone can load, run, and build upon.

---

## Browse circuits

| Circuit | Qubits | Tags | Author |
|---------|--------|------|--------|
| [Bell State](examples/bell-state.json) | 2 | entanglement, beginner | Quantum Collective |
| [GHZ State (3q)](examples/ghz-3.json) | 3 | entanglement, beginner | Quantum Collective |

*More circuits added each week by the community.*

---

## Load a circuit in qcsim

```bash
# From the interactive builder
qcsim-interactive
> Press [I] to import
> Path: circuit-library/examples/bell-state.json

# Or from Python
import json
from qcsim.tui import CircuitGrid
from qcsim.circuit import QuantumCircuit

with open("circuit-library/examples/bell-state.json") as f:
    data = json.load(f)

grid = CircuitGrid.from_json(data)
qc = grid  # use the TUI builder to run it, or convert manually
```

---

## Submit your circuit

**Step 1 — Build it**
Use the interactive builder or write it in Python:
```bash
qcsim-interactive
# Build your circuit, then press [E] to export as JSON
```

**Step 2 — Add to library**
```bash
cd Quantum-Collective-Monthly-Projects
python circuit-library/add_circuit.py my-circuit.json
```
This checks for duplicates and adds it to `index.json`.

**Step 3 — Open a PR**
```bash
git add circuit-library/
git commit -m "feat(library): add My Circuit Name"
git push
# Open PR on GitHub
```

---

## Circuit JSON format

```json
{
  "name": "My Circuit",
  "description": "What this circuit demonstrates.",
  "author": "your-github-username",
  "tags": ["beginner", "entanglement"],
  "num_qubits": 2,
  "num_cols": 4,
  "backend": "kronecker",
  "gates": [
    {"gate": "H",      "row": 0, "col": 0},
    {"gate": "CNOT_C", "row": 0, "col": 1, "linked_row": 1},
    {"gate": "CNOT_T", "row": 1, "col": 1, "linked_row": 0}
  ],
  "fingerprint": "auto-computed-by-add_circuit.py"
}
```

**Gate types:** `H`, `X`, `CNOT_C` (control), `CNOT_T` (target), `SWAP_A`, `SWAP_B`
**CNOT/SWAP:** each end of the pair must have `linked_row` pointing to the other row.

---

## Deduplication

`add_circuit.py` computes a SHA-256 fingerprint of the gate sequence.
Circuits with identical fingerprints are rejected — you cannot add the same
circuit twice.

Circuits that produce the same quantum state via *different gate sequences*
are not considered duplicates — different implementations have educational value.

---

## Ideas for circuits to add

**Beginner**
- 4-qubit GHZ state
- Quantum coin flip (single H gate)
- Bit flip (X gate on each qubit)
- Quantum NOT (X then H)

**Intermediate**
- Quantum Fourier Transform (2, 3, 4 qubits)
- Grover oracle for various targets
- Teleportation circuit (3 qubits)
- Superdense coding

**Advanced**
- Bernstein-Vazirani algorithm
- Simon's algorithm
- Phase estimation (small scale)
- Quantum error correction (3-qubit bit-flip code)

---

## Goal

By the end of Month 1 of the Quantum Collective program, we aim to have
**50+ unique circuits** covering all major quantum algorithms and gate combinations.
This library will be used as a foundation for Month 2 and beyond.
