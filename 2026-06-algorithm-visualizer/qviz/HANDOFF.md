# qviz Handoff — Continue Building Here

Read this whole file before touching code. It's written for a fresh Claude
session with zero memory of how this got built — it has no other context,
so this file has to carry it all.

## What this is

`qviz` = Quantum Collective Monthly Project #2, "Quantum Algorithm
Visualizer." Steps through a quantum algorithm one gate at a time and
shows how the state vector evolves, instead of only the final answer.
It's a community challenge — repo is public, contributors submit PRs.

**Repo:** `Quantum-Collective-Monthly-Projects` (GitHub: LochanPS)
**This package:** `2026-06-algorithm-visualizer/qviz/`
**Sibling/dependency:** `2026-05-circuit-simulator/qcsim/` — Monthly
Project #1, a quantum circuit simulator. `qviz` imports it as a library
(`pip install -e` from the sibling path, not vendored/copied).
**Challenge spec (the public-facing problem statement):**
`2026-06-algorithm-visualizer/README.md` — read this for contribution
tiers (Beginner/Intermediate/Advanced/Expert) and the open-core business
context. Don't duplicate that content here, just know it exists.

## Critical business context (don't violate this)

This repo is **open-source (Apache-2.0)**. There is a **separate private
repo**, `Quantum-Software-Lab-Suite`, which is a paid desktop product
built on the same `qcsim`/`qviz` foundation. The split is deliberate:

- **Free (this repo, terminal-only):** the stepper engine, the core
  algorithms, ASCII rendering. Anyone can use it, no paywall.
- **Paid (Lab Suite, separate repo):** graphical/animated version of the
  same stepper, Bloch sphere, noise models, GPU backend, etc.

**Do not build a graphical UI in this package.** If you're tempted to add
matplotlib charts, a web view, anything visual beyond ASCII — stop, that
belongs in the Lab Suite repo, not here. Terminal-only is a deliberate
product decision, not a limitation to "fix."

## Architecture (what exists, how it fits together)

```
qviz/
├── qviz/
│   ├── stepper.py       Step dataclass + step_through() + apply_log_entry()
│   ├── render.py        terminal rendering (statevector bars, progress diagram)
│   ├── algorithms/
│   │   ├── deutsch_jozsa.py
│   │   ├── bernstein_vazirani.py
│   │   ├── grover.py          (2-qubit only, v1)
│   │   └── qft_algorithm.py   (wraps qcsim's existing qft())
│   └── cli.py            interactive step/back/jump terminal interface
└── tests/test_stepper.py  25 passing tests
```

### `stepper.py` — the core engine

`step_through(circuit)` takes an already-built `qcsim.QuantumCircuit`,
replays its internal gate log (`circuit._log`) one entry at a time on a
**fresh** circuit, and returns a `Step` per gate with:
- `index`, `gate_name`, `qubits`, `params`
- `statevector`, `probabilities` (snapshotted right after that gate)
- `annotation` (empty by default — algorithm modules fill this in)

**This is already incremental**, not quadratic — each gate is applied
once, on top of the running `working` circuit, not replayed from scratch
per step. If you're tempted to "optimize" this for the Expert-tier
performance task, profile first; it may already be fine.

`apply_log_entry(working, name, qubits, params)` is the shared helper
that correctly dispatches BARRIER (no-op, returns False so no Step gets
recorded), MEASURE (calls `working.measure(qubit)`), RESET (calls
`working.reset(qubit)`), and everything else (calls
`working._replay_gate(...)`, qcsim's existing unitary-gate dispatch).

**Important:** `_replay_gate` (qcsim internal) silently no-ops on
MEASURE/RESET/BARRIER — it only knows unitary gates. Don't call it
directly for those three; always go through `apply_log_entry`.

**This means mid-circuit measurement is already supported at the
stepper level.** Teleportation and VQE were deferred from launch not
because the stepper can't handle them, but because nobody's written
those algorithm modules yet. That's the actual remaining work, not a
plumbing gap.

### `render.py` — terminal output

`render_statevector(step)` — amplitude bars, mirrors qcsim's
`visualize.py` style (re-implemented here, not imported, because it
needs a live circuit object and `Step` only has a raw array).

`render_progress_circuit(circuit, up_to_index)` — rebuilds a circuit
containing only gates `[0..up_to_index]` and draws it with qcsim's
`draw_circuit()`. This is how "current-step highlighting" works: gates
not yet reached simply aren't drawn yet. Simple, correct, no real
highlighting logic needed.

`render_step(circuit, step)` — combines header + annotation + progress
diagram + statevector into one printable block.

### `algorithms/*.py` — the reference algorithms

Each module exposes one function returning `(circuit, annotations)`
where `annotations` is a list with **exactly one string per gate** in
`circuit._log` order. This 1:1 alignment is load-bearing — `cli.py`
zips `annotations` onto `Step.annotation` by position. If you add a gate
without adding its annotation (or vice versa), they desync silently
(no error, just wrong labels) — there's a test pattern for this, see below.

| Module | Status | Notes |
|---|---|---|
| `deutsch_jozsa.py` | done, fully annotated | any input size, 3 oracle types |
| `bernstein_vazirani.py` | done, fully annotated | any secret length |
| `grover.py` | done, fully annotated | **2-qubit marked states only** — see bug story below before touching this |
| `qft_algorithm.py` | done, **generic annotations** | wraps `qcsim.qft.qft()`; annotations just say "QFT step" since the wrapped function doesn't tag what each gate does — writing precise ones is an open Beginner-tier task |

### `cli.py` — interactive stepper

Menu picks an algorithm, prompts for parameters, then a step/back/jump
loop (`Enter`/`b`/`j N`/`q`). Tested manually via piped stdin during
build — works, but has no automated tests (it's a thin wrapper over
already-tested `stepper.py`/`render.py`/`algorithms/*`, low risk).

## The Grover bug — read this before writing ANY new algorithm with a bitstring parameter

qcsim labels basis states as `q(n-1)...q1q0` — **leftmost character is
the highest-index qubit**, not qubit 0. `grover.py` originally did:

```python
for q, bit in enumerate(marked_state):  # WRONG
    if bit == "0":
        qc.x(q)
```

This silently mapped `marked_state[0]` to qubit 0, which is backwards
from qcsim's printed convention. For symmetric targets (`"11"`, `"00"`)
this is invisible — reversing a palindrome doesn't change it. It only
broke for asymmetric targets (`"01"` actually marked `"10"`).

**Fix applied:** reverse the string once at the top —
`target_bits = marked_state[::-1]` — then index `target_bits[i]` for
qubit `i`.

**Lesson, enforced going forward:** any test involving a bitstring
parameter (marked state, secret, target) MUST include a non-palindromic
case (`"01"`/`"10"`, `"100"`, etc.), not just symmetric ones (`"11"`,
`"00"`, `"101"`). See `test_finds_asymmetric_marked_state_other_direction`
and `test_recovers_non_palindromic_secret` in `tests/test_stepper.py` —
keep this pattern for every new algorithm module.

## Setup

```bash
cd 2026-06-algorithm-visualizer/qviz
python -m venv .venv
.venv\Scripts\activate                          # Windows
pip install -e ../../2026-05-circuit-simulator/qcsim   # qcsim first, not on PyPI
pip install -e ".[dev]"
pytest tests/ -v          # should show 25 passed
qviz-step                 # try the interactive CLI
```

## What's actually left (mapped to the public README's tiers)

**Beginner**
- [ ] Write precise per-gate annotations for `qft_algorithm.py` (currently generic "QFT step" placeholder)

**Intermediate**
- [ ] New algorithm module: Simon's algorithm, a simple quantum walk, or amplitude estimation — follow the `(circuit, annotations)` pattern, gate-by-gate annotation alignment, non-palindrome test cases
- [ ] Step-diff view: given two consecutive `Step`s, show which amplitudes changed and by how much
- [ ] Export a step trace to JSON/text (for teaching writeups)

**Advanced**
- [ ] Multi-qubit subsystem views — reduced/partial-trace state display for ancilla-heavy algorithms (DJ, BV both have an ancilla qubit that's currently shown in full, not factored out)
- [ ] Side-by-side comparison mode (e.g. Grover with 1 vs 2 iterations)
- [ ] Generalize `grover.py` beyond 2 qubits — needs a multi-controlled-Z. qcsim has Toffoli (CCX) but not arbitrary-arity controlled-Z; may need a new qcsim gate or an ancilla-based decomposition. Check `2026-05-circuit-simulator/qcsim/qcsim/gates.py` and `circuit.py` first.

**Expert**
- [ ] Property-based correctness-checking harness — generate many oracle instances per algorithm, verify the stepper's final state matches expected
- [ ] Teleportation algorithm module — stepper already supports MEASURE/RESET via `apply_log_entry`, this is "just" writing the algorithm + verifying classical-control logic reads correctly through the steps
- [ ] Basic VQE step module — same stepper support story as teleportation

**Already done, don't re-do:**
- Per-step state snapshotting (and it's already incremental, not quadratic)
- Circuit-diagram step highlighting (via progressive rendering)
- Core four algorithms with correctness tests
- Mid-circuit MEASURE/RESET stepper support (the plumbing — not algorithm modules using it)

## Commit message style (match the existing history)

Look at recent commits in this repo (`git log --oneline -10`) before
committing — they're written in a specific terse-but-complete style with
a "why" section. Match it, don't invent a new convention.
