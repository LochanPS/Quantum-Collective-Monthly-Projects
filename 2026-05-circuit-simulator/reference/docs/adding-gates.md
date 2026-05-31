# Adding New Gates to qcsim

This guide walks through adding a new quantum gate to the simulator end-to-end.
Follow every step in order. If you skip one, the gate will be partially broken.

---

## Before You Start

A quantum gate is a **unitary matrix** — a square complex matrix where U†U = I (conjugate
transpose equals identity). If your gate is not unitary, measurement probabilities will
stop summing to 1 and all results will be wrong.

Check unitarity before submitting:
```python
import numpy as np

U = np.array([[...]])  # your gate matrix
assert np.allclose(U.conj().T @ U, np.eye(len(U))), "Gate is not unitary!"
```

---

## Step 1 — Define the matrix in `qcsim/gates.py`

Open `qcsim/gates.py`. Add your gate as a module-level function that returns a numpy array.

**Template:**
```python
def MY_GATE() -> np.ndarray:
    """One-line description. Mathematical effect on basis states.

    MY_GATE|0⟩ = ...
    MY_GATE|1⟩ = ...

    Returns:
        2x2 complex numpy array.
    """
    return np.array([
        [top_left,  top_right],
        [bot_left,  bot_right],
    ], dtype=complex)
```

**Real example — adding the √X gate (SX):**
```python
def SX() -> np.ndarray:
    """SX gate (sqrt-X gate). SX² = X.

    SX|0⟩ = (1+i)|0⟩/2 + (1-i)|1⟩/2
    SX|1⟩ = (1-i)|0⟩/2 + (1+i)|1⟩/2

    Returns:
        2x2 complex numpy array.
    """
    return np.array([[1 + 1j, 1 - 1j],
                     [1 - 1j, 1 + 1j]], dtype=complex) * 0.5
```

**Rules:**
- Function name = gate name in CAPS (e.g., `H`, `X`, `SX`, `Rx`)
- Parametric gates take float arguments (e.g., `Rx(theta: float)`)
- Always use `dtype=complex` on the array
- Write the mathematical effect in the docstring — beginners learn from this

---

## Step 2 — Add the circuit method in `qcsim/circuit.py`

Open `qcsim/circuit.py`. Find the section `# Single-qubit gates` or `# Two-qubit gates`
and add a method.

**Template for a single-qubit gate:**
```python
def my_gate(self, qubit: int) -> "QuantumCircuit":
    """Apply MY_GATE to a qubit. One-line description.

    Mathematical effect:
        MY_GATE|0⟩ = ...

    Args:
        qubit: Target qubit index.

    Returns:
        Self, for method chaining.

    Raises:
        QubitIndexError: If qubit index is out of range.
    """
    self._check(qubit)
    self._gate_single(G.MY_GATE(), qubit)
    self._log.append(("MY_GATE", [qubit], None))
    return self
```

**Template for a parametric gate (e.g., Rx):**
```python
def my_rotation(self, qubit: int, theta: float) -> "QuantumCircuit":
    """Apply MY_ROTATION(θ) to a qubit.

    Args:
        qubit: Target qubit index.
        theta: Rotation angle in radians.

    Returns:
        Self, for method chaining.

    Raises:
        QubitIndexError: If qubit index is out of range.
    """
    self._check(qubit)
    self._gate_single(G.MY_ROTATION(theta), qubit)
    self._log.append(("MY_ROTATION", [qubit], {"theta": theta}))
    return self
```

**Template for a two-qubit controlled gate:**
```python
def my_controlled(self, control: int, target: int) -> "QuantumCircuit":
    """Apply Controlled-MY_GATE. Applies gate to target when control is |1⟩.

    Args:
        control: Control qubit index.
        target: Target qubit index.

    Returns:
        Self, for method chaining.

    Raises:
        QubitIndexError: If either index is out of range or they are equal.
    """
    self._check(control, "control")
    self._check(target, "target")
    self._check_distinct(control, target)
    self._gate_controlled(G.MY_GATE(), control, target)
    self._log.append(("C_MY_GATE", [control, target], None))
    return self
```

**Important:** `_gate_single` and `_gate_controlled` handle both Kronecker and
tensor backends automatically. Never call `_apply` or `_expand_single` directly
in new gate methods.

---

## Step 3 — Add to the gate log replay in `_replay_gate`

Still in `circuit.py`, find `_replay_gate`. Add your gate to the dispatch dict:

```python
dispatch = {
    # ... existing gates ...
    "MY_GATE": lambda: self.my_gate(qubits[0]),
    # For parametric:
    "MY_ROTATION": lambda: self.my_rotation(qubits[0], p["theta"]),
    # For two-qubit:
    "C_MY_GATE": lambda: self.my_controlled(qubits[0], qubits[1]),
}
```

This is needed for `circuit.compose()` to work correctly.

---

## Step 4 — Add the display label in `qcsim/visualize.py`

In `visualize.py`, `_render_gate` dispatches based on `gate_name`. For most single-qubit
gates the box renderer handles them automatically — you only need to add special cases
for unusual display.

For a standard single-qubit gate (label ≤ 4 chars): **no change needed** — the existing
`len(qubits) == 1` branch renders any label automatically as a box gate.

For a gate that needs a custom symbol (like the CNOT `●` and `⊕`), add it to the
`if len(qubits) == 2` block in `_render_gate`.

---

## Step 5 — Add to the TUI gate palette in `qcsim/tui.py`

**5a. Add a display symbol** to `_GATE_DISPLAY`:
```python
_GATE_DISPLAY: Dict[str, str] = {
    # ... existing ...
    "MY_GATE": "M",   # 1-char symbol shown in the grid cell
}
```

**5b. Add a key binding** in `_handle`:
```python
elif key == "m":          # key the user presses
    self._place_single("MY_GATE")
```

**5c. Update the help line** at the bottom of `_render_grid`:
```python
lines.append("  Gates : [H] [X] [C]NOT [W]AP [M]y_gate  |  [Backspace] delete  |  [?] gate help")
```

**5d. Add gate help content** in `_gate_help`:
```python
_GATE_HELP = {
    # ... existing ...
    "MY_GATE": (
        "My Gate — Short title",
        "Matrix: [[a, b], [c, d]]",
        "MY_GATE|0> = ...",
        "MY_GATE|1> = ...",
        "",
        "Use: When you need this gate because...",
    ),
}
```

---

## Step 6 — Export: add to `_replay_gate` in `tui.py`

In `CircuitBuilder._to_qcsim`, add a case for your gate in the column-processing loop:

```python
elif g == "MY_GATE":
    qc.my_gate(row)
```

---

## Step 7 — Write tests in `tests/test_circuit.py`

Add a test class. Every gate needs at least these three tests:

```python
class TestMyGate:
    def test_effect_on_zero(self):
        """MY_GATE|0⟩ = expected state."""
        qc = QuantumCircuit(1)
        qc.my_gate(0)
        sv = qc.statevector()
        # Check the expected amplitudes
        assert abs(sv[0] - expected_0) < 1e-10
        assert abs(sv[1] - expected_1) < 1e-10

    def test_self_inverse(self):
        """If MY_GATE is its own inverse, applying twice = identity."""
        qc = QuantumCircuit(1)
        qc.my_gate(0).my_gate(0)
        assert abs(qc.probabilities().get("0", 0) - 1.0) < 1e-10

    def test_probabilities_sum_to_one(self):
        """Norm is preserved."""
        qc = QuantumCircuit(2)
        qc.my_gate(0).my_gate(1)
        assert abs(sum(qc.probabilities().values()) - 1.0) < 1e-10
```

Run the tests before opening a PR:
```bash
pytest tests/ -v
```

All 52 existing tests must still pass. Your new tests must also pass.

---

## Step 8 — Document it

Add your gate to the gate table in `README.md`:

```markdown
| `qc.my_gate(q)` | MY_GATE | What it does in plain English |
```

---

## Step 9 — Prevent duplicates

Before submitting, verify your gate matrix is not already in `gates.py` under a different name:

```python
import numpy as np
from qcsim import gates

my_matrix = np.array([[...]])

for name in dir(gates):
    fn = getattr(gates, name)
    if callable(fn) and not name.startswith("_"):
        try:
            existing = fn()
            if isinstance(existing, np.ndarray) and existing.shape == my_matrix.shape:
                if np.allclose(existing, my_matrix):
                    print(f"DUPLICATE: {name} has the same matrix as your gate!")
        except TypeError:
            pass  # parametric gate, skip
```

---

## Step 10 — Open a PR

```bash
git checkout -b feat/gate-my-gate
git add qcsim/gates.py qcsim/circuit.py qcsim/tui.py tests/test_circuit.py README.md
git commit -m "feat(gates): add MY_GATE"
git push && open a PR
```

**PR title format:** `feat(gates): add <GATE_NAME>`

**PR checklist:**
- [ ] Gate matrix is unitary (U†U = I)
- [ ] Gate function added to `gates.py` with docstring
- [ ] Circuit method added to `circuit.py`
- [ ] `_replay_gate` updated
- [ ] TUI key binding added
- [ ] Gate help text added
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Gate added to README table
- [ ] No existing gate with same matrix

---

## Reference: Common Gate Patterns

### Phase gate (diagonal)
```python
def MY_PHASE(lam: float) -> np.ndarray:
    return np.array([[1, 0], [0, np.exp(1j * lam)]], dtype=complex)
```

### Rotation gate
```python
def MY_ROT(theta: float) -> np.ndarray:
    c, s = np.cos(theta/2), np.sin(theta/2)
    return np.array([[c, -1j*s], [-1j*s, c]], dtype=complex)
```

### Hadamard-family gate
```python
_S2 = 1 / np.sqrt(2)
def MY_H_FAMILY() -> np.ndarray:
    return np.array([[1, 1j], [1j, 1]], dtype=complex) * _S2
```

---

## Questions?

Post in [GitHub Discussions / Q&A](../../discussions/categories/q-a) or `#code-help` on Discord.
