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

`render_step(circuit, step, prev=None, mode="advanced", hide_zeros=False)`
— combines header + annotation + progress diagram + active-gate caption
+ statevector/probability table + a plain-English interpretation into one
printable block. `prev` (the previous Step) enables changed-amplitude
highlighting; `mode` is `"beginner"` (percentages only) or `"advanced"`
(complex amplitudes + phase column + highlighting).

### `interpret.py` — plain-English state reading

`interpret_state(step)` returns a sentence describing what the current
state *means* (definite outcome / uniform superposition / equal
superposition of a subset / most-likely-outcome). `phase_label(amp)`
gives an amplitude's phase as a multiple of pi (used by the QFT phase
column). `nonzero_states(step)` returns `(label, prob, amp)` sorted by
probability. Kept separate from `render.py` so any front-end can reuse
the wording.

### `algorithms/*.py` — the reference algorithms

**API (changed in v0.2):** each module's build function returns an
`AlgorithmResult` (see `algorithms/base.py`), NOT the old
`(circuit, annotations)` tuple. Fields:
- `circuit` — the built qcsim circuit
- `annotations` — list with **exactly one string per gate** in
  `circuit._log` order (1:1 alignment is load-bearing — `cli.py` zips
  these onto `Step.annotation` by position; desync = silently wrong
  labels, so keep the annotation-count test for every algorithm)
- `title` — display name
- `info` — dict of always-displayed defining facts (marked state,
  secret, oracle type) shown on every step
- `summarize(final_step)` — returns the algorithm's plain-English answer
  (Balanced/Constant, recovered secret, target found, QFT done)

`input_register(bitstring, k)` in `base.py` extracts the rightmost `k`
input-register bits from a full qcsim label and reverses them to q0..q(k-1)
order — use it in summaries so you don't re-derive the label orientation
(see the Grover bug below).

| Module | Status | Notes |
|---|---|---|
| `deutsch_jozsa.py` | done, fully annotated + summary | any input size, 3 oracle types |
| `bernstein_vazirani.py` | done, fully annotated + summary | any secret length |
| `grover.py` | done, fully annotated + summary + amplitude-amplification view | **2-qubit marked states only** — see bug story below before touching this |
| `qft_algorithm.py` | done, per-gate annotations (H / CP-with-angle / SWAP) + summary | wraps `qcsim.qft.qft()`; annotations now read the emitted gate log. Making them name *which* frequency each CP encodes is still an open Beginner-tier task |

### `cli.py` — interactive stepper

Menu picks an algorithm, prompts for parameters, then a step loop:
`Enter` next, `b` back, `j N` jump, `a` autoplay (auto-advances with a
delay), `m` toggle beginner/advanced mode, `h` toggle hide-zeros, `q`
**back to the menu** (not exit — pick another algorithm without
relaunching; `q` at the menu exits). Beginner/advanced mode and the
final-step summary + Grover amplitude-amplification bars are shown here.
The stepper/render/algorithm layers are unit-tested; `cli.py` itself is
a thin wrapper tested manually via piped stdin.

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
pytest tests/ -v          # should show 39 passed
qviz-step                 # try the interactive CLI
```

## What's actually left (mapped to the public README's tiers)

**Beginner**
- [ ] Make `qft_algorithm.py` annotations name *which* qubit-pair frequency each controlled-phase encodes (they already label type + angle, just not the specific frequency meaning)

**Intermediate**
- [ ] New algorithm module: Simon's algorithm, a simple quantum walk, or amplitude estimation — return an `AlgorithmResult` (title/info/annotations/summarize), keep gate-by-gate annotation alignment, add a non-palindrome test case
- [ ] Export a step trace to JSON/text (for teaching writeups) — `Step` already carries everything needed
- [ ] Comparison mode: run two configs side by side (e.g. Grover 1 vs 2 iterations)

**Advanced**
- [ ] Multi-qubit subsystem views — reduced/partial-trace state display for ancilla-heavy algorithms (DJ, BV both have an ancilla qubit shown in full, not factored out)
- [ ] Generalize `grover.py` beyond 2 qubits — needs a multi-controlled-Z. qcsim has Toffoli (CCX) but not arbitrary-arity controlled-Z; may need a new qcsim gate or an ancilla-based decomposition. Check `2026-05-circuit-simulator/qcsim/qcsim/gates.py` and `circuit.py` first.

**Expert**
- [ ] Property-based correctness-checking harness — generate many oracle instances per algorithm, verify the stepper's final state matches expected
- [ ] Teleportation algorithm module — stepper already supports MEASURE/RESET via `apply_log_entry`, this is "just" writing the algorithm + verifying classical-control logic reads correctly through the steps
- [ ] Basic VQE step module — same stepper support story as teleportation

**Already done, don't re-do:**
- Per-step state snapshotting (already incremental, not quadratic)
- Circuit-diagram step highlighting (progressive rendering) + active-gate caption
- Core four algorithms with correctness tests + per-algorithm final summaries
- Plain-English state interpretation per step (`interpret.py`)
- Changed-amplitude highlighting, hide-zero-states, phase column (`render.py`)
- Beginner/advanced detail modes + autoplay + menu-loop flow (`cli.py`)
- Grover amplitude-amplification-across-steps view
- Mid-circuit MEASURE/RESET stepper support (the plumbing — not algorithm modules using it)

## Commit message style (match the existing history)

Look at recent commits in this repo (`git log --oneline -10`) before
committing — they're written in a specific terse-but-complete style with
a "why" section. Match it, don't invent a new convention.
