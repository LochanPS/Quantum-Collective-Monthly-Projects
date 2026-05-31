# Submitting Circuits to the Library

Anyone can contribute a circuit. No quantum physics degree needed.
If you built something interesting in qcsim, we want it in the library.

---

## What Makes a Good Library Circuit

A circuit is worth submitting if it:
- Demonstrates a quantum concept (superposition, entanglement, interference)
- Implements a known algorithm (Grover, Deutsch-Jozsa, QFT, teleportation)
- Is a useful building block (Bell state, GHZ, phase oracle, SWAP network)
- Is an interesting experiment you discovered while exploring

A circuit is NOT worth submitting if it:
- Is identical to an existing circuit (the dedup check will catch this)
- Does nothing (all empty cells)
- Is a trivially renamed copy of an existing circuit

---

## Method 1 — Build in the TUI and Export (recommended)

**Step 1: Launch the simulator**
```bash
cd Quantum-Collective-Monthly-Projects/2026-05-circuit-simulator/reference
qcsim-interactive
```

**Step 2: Build your circuit**
- Choose number of qubits and columns at the setup screen
- Use arrow keys to navigate the grid
- Press `H`, `X`, `C` (CNOT), `W` (SWAP) to place gates
- Press `?` on any gate to see what it does
- Press `R` to run and verify output looks correct

**Step 3: Export**
- Press `E` to export
- Enter a descriptive name (e.g., "4-qubit GHZ State")
- Choose a save path (e.g., `my-circuit.json`)

**Step 4: Submit to the library**
```bash
python circuit-library/add_circuit.py my-circuit.json
```

This will:
1. Validate the JSON format
2. Ask you for missing metadata (description, category, difficulty, tags)
3. Check for duplicates via fingerprint
4. Add the file to `circuit-library/`
5. Update `index.json`

**Step 5: Open a PR**
```bash
git add circuit-library/
git commit -m "feat(library): add 4-qubit GHZ State"
git push
```
Open a pull request on GitHub. CI will run the duplicate check automatically.

---

## Method 2 — Write the JSON directly

If you're comfortable with JSON, write the circuit file directly:

```json
{
  "name": "My Circuit Name",
  "version": "1.0",
  "description": "What this circuit does and why it is interesting.",
  "author": "your-github-username",
  "created_at": "2026-06-01",
  "category": "entanglement",
  "difficulty": "beginner",
  "tags": ["entanglement", "beginner"],
  "source_url": "https://en.wikipedia.org/wiki/...",
  "num_qubits": 2,
  "num_cols": 4,
  "backend": "kronecker",
  "gates": [
    {"gate": "H",      "row": 0, "col": 0},
    {"gate": "CNOT_C", "row": 0, "col": 1, "linked_row": 1},
    {"gate": "CNOT_T", "row": 1, "col": 1, "linked_row": 0}
  ]
}
```

Then run `add_circuit.py my-circuit.json` as above.

---

## JSON Format Reference

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Descriptive name. Unique in the library. |
| `num_qubits` | int (1–20) | Number of qubits |
| `num_cols` | int (1–20) | Number of gate columns |
| `backend` | string | `"kronecker"` or `"tensor"` |
| `gates` | array | List of gate objects (see below) |

### Recommended fields (add_circuit.py will prompt for these)

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | 1–3 sentences explaining the circuit |
| `author` | string | Your GitHub username |
| `category` | string | One of: `entanglement`, `algorithm`, `education`, `error-correction`, `benchmark`, `other` |
| `difficulty` | string | `beginner`, `intermediate`, or `advanced` |
| `tags` | array | From the canonical list in `tags.json` |
| `source_url` | string | Wikipedia, arXiv, textbook reference |

### Gate object format

```json
{"gate": "H", "row": 0, "col": 0}
```

| Field | Description |
|-------|-------------|
| `gate` | Gate type: `H`, `X`, `CNOT_C`, `CNOT_T`, `SWAP_A`, `SWAP_B` |
| `row` | Qubit row (0-indexed from top) |
| `col` | Column position (0-indexed from left) |
| `linked_row` | Required for CNOT and SWAP: the row of the partner qubit |

**CNOT rule:** Every `CNOT_C` must have a matching `CNOT_T` entry in the same column with `linked_row` pointing back. Same for `SWAP_A` / `SWAP_B`.

### Available tags

See `circuit-library/tags.json` for the full list with descriptions.

Current tags: `beginner`, `intermediate`, `advanced`, `fundamental`, `entanglement`,
`superposition`, `ghz`, `bell`, `teleportation`, `algorithm`, `grover`,
`deutsch-jozsa`, `qft`, `error-correction`, `noise`, `phase`, `rotation`,
`swap`, `toffoli`, `education`, `benchmark`, `research`

Tags not in this list will be rejected. To add a new tag, open a PR editing `tags.json`.

---

## What Happens After You Submit

1. CI runs `check_duplicates.py` — fails if fingerprint matches an existing circuit
2. CI validates all JSON is well-formed
3. Maintainer ([@LochanPS](https://github.com/LochanPS)) reviews the circuit
4. If the circuit runs correctly and is genuinely new → merged
5. After merge, `"verified": true` is set in `index.json`

Typical review time: 24–72 hours.

---

## Duplicate Detection

Every circuit gets a **fingerprint** — a SHA-256 hash of its normalized gate structure.

Two circuits with the same fingerprint are considered identical and the second submission
is rejected. The fingerprint normalizes:
- Empty column positions (Bell in cols 0,1 = Bell in cols 0,5)
- Gate ordering within a column
- Parametric angles (rounded to 3 decimal places)

Two circuits that produce the **same quantum state via different gate sequences** are
NOT considered duplicates. Different implementations of the same algorithm have educational
value and are both accepted.

---

## Circuit Ideas

**Need inspiration?** Here are circuits not yet in the library:

**Beginner**
- 4-qubit GHZ state
- 5-qubit GHZ state
- Quantum coin flip (single H gate, 1 qubit)
- Bit-flip of 3 qubits (X on each)
- Phase flip (Z on |+⟩ state)
- SWAP test setup
- Uniform superposition (H on every qubit)

**Intermediate**
- 2-qubit Quantum Fourier Transform
- 3-qubit Quantum Fourier Transform
- Grover oracle for `|01⟩`
- Grover oracle for `|10⟩`
- Quantum teleportation (3 qubits)
- Superdense coding (2 qubits)
- Bell basis measurement circuit
- Phase kickback demonstration
- Controlled phase gate chain

**Advanced**
- Bernstein-Vazirani algorithm (3-bit secret)
- Simon's algorithm (2-qubit case)
- 3-qubit bit-flip error correction code
- Quantum Fourier Transform (4 qubits)
- Grover's algorithm (4 qubits, 2 iterations)
- Phase estimation (small scale)

---

## Questions?

- Discord: `#problem-discussion`
- GitHub Discussions: [Q&A category](../../discussions/categories/q-a)

We merge every genuinely new, correctly functioning circuit. Don't overthink it.
