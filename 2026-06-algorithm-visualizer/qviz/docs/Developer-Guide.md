# qviz Developer Guide

Read this before writing code. It carries the design decisions, the
per-module details, and the one bug you must understand before adding any
algorithm. (This was previously `HANDOFF.md`; it's now public docs.)

For a higher-level map first, read [Architecture.md](Architecture.md).

## What qviz is

`qviz` = Quantum Collective Monthly Project #2, "Quantum Algorithm
Visualizer." Steps through a quantum algorithm one gate at a time and
shows how the state vector evolves, instead of only the final answer. It's
a community challenge — the repo is public and contributors submit PRs.

- **Package:** `2026-06-algorithm-visualizer/qviz/`
- **Dependency:** `2026-05-circuit-simulator/qcsim/` (Monthly Project #1),
  imported as a library via `pip install -e` — not vendored or copied.
- **Challenge spec:** [`../../README.md`](../../README.md) — contribution
  tiers and context.

## Critical design constraint: terminal-only

This repo is open-source (Apache-2.0). A separate product (the "Lab
Suite") provides a graphical version built on the same engine. For qviz:

**Do not add a graphical UI here.** No matplotlib, no web view, nothing
beyond ASCII/ANSI in the terminal. Terminal-first is a deliberate product
decision, not a limitation to "fix." Rendering features must degrade
gracefully on ASCII-only terminals — see [Rendering-Guide.md](Rendering-Guide.md).

## Per-module deep dive

### `stepper.py` — the core engine

`step_through(circuit)` takes an already-built `qcsim.QuantumCircuit`,
replays its internal gate log (`circuit._log`) one entry at a time on a
**fresh** circuit, and returns a `Step` per gate.

**It's already incremental**, not quadratic — each gate is applied once,
on top of the running `working` circuit, not replayed from scratch per
step. Before "optimizing" this for the Expert performance task, profile —
it may already be fine.

`apply_log_entry(working, name, qubits, params)` is the shared dispatcher:
- `BARRIER` → no-op, returns `False` (no Step recorded)
- `MEASURE` → `working.measure(qubit)`
- `RESET` → `working.reset(qubit)`
- everything else → `working._replay_gate(...)` (qcsim's unitary dispatch)

**Important:** qcsim's `_replay_gate` silently no-ops on
MEASURE/RESET/BARRIER — it only knows unitary gates. Always go through
`apply_log_entry`, never call `_replay_gate` directly for those three.

**Consequence:** mid-circuit measurement already works at the stepper
level. Teleportation and VQE are deferred because nobody's written those
*algorithm modules* yet — not because the plumbing is missing.

### `interpret.py` — plain-English state reading

- `interpret_state(step)` → a sentence: definite outcome / uniform
  superposition / equal superposition of a subset / most-likely-outcome.
- `phase_label(amp)` → an amplitude's phase as a multiple of pi.
- `nonzero_states(step)` → `(label, prob, amp)` sorted by probability.

Kept separate from `render.py` so any front-end reuses the wording.

### `phases.py` — phase segments

`segments(phases)` groups consecutive equal phase labels into
`(phase, start, end)` tuples, so Grover's repeated Oracle/Diffusion show
up as separate segments per iteration. `current_segment_index(segs, i)`
finds the segment a step falls in. Used by the progress bar and the
windowed circuit.

### `render.py` — terminal output

The presentation layer. Key functions (see [API-Reference.md](API-Reference.md)
for signatures): `render_step` (the composer), `render_statevector`,
`render_phase_progress`, `render_windowed_circuit`, `render_measurement`,
`render_execution_summary`. All non-ASCII glyphs are gated behind a
`_can_unicode()` check with ASCII fallbacks — respect this for anything
you add. See [Rendering-Guide.md](Rendering-Guide.md).

### `algorithms/*.py` — the reference algorithms

Each build function returns an `AlgorithmResult` (see
[Algorithm-Development.md](Algorithm-Development.md) for the full how-to).
Current status:

| Module | Status |
|---|---|
| `deutsch_jozsa.py` | done — any input size, 3 oracle types, full annotations/phases/summary/outcome |
| `bernstein_vazirani.py` | done — any secret length |
| `grover.py` | done — **2-qubit marked states only**; includes amplitude-amplification view |
| `qft_algorithm.py` | done — per-gate annotations (H / CP-with-angle / SWAP); naming which frequency each CP encodes is an open Beginner task |

### `cli.py` — interactive stepper

Menu → parameter prompts → step loop. Keys: `Enter` next, `b` back,
`j N` jump, `a` autoplay, `m` toggle beginner/advanced, `h` toggle
hide-zeros, `q` **back to the menu** (pick another algorithm without
relaunching; `q` at the menu exits). The stepper/render/algorithm layers
are unit-tested; `cli.py` is a thin wrapper tested manually via piped
stdin.

## The Grover bug — read before writing ANY algorithm with a bitstring parameter

qcsim labels basis states as `q(n-1)...q1q0` — **the leftmost character is
the highest-index qubit**, not qubit 0. `grover.py` originally did:

```python
for q, bit in enumerate(marked_state):  # WRONG
    if bit == "0":
        qc.x(q)
```

This mapped `marked_state[0]` to qubit 0, backwards from qcsim's printed
convention. For symmetric targets (`"11"`, `"00"`) it's invisible —
reversing a palindrome changes nothing. It only broke for asymmetric
targets (`"01"` actually marked `"10"`).

**Fix:** reverse once at the top — `target_bits = marked_state[::-1]` —
then index `target_bits[i]` for qubit `i`. The `input_register(bitstring, k)`
helper in `base.py` does the same reversal for reading results back.

**Enforced rule:** any test with a bitstring parameter (marked state,
secret, target) MUST include a **non-palindromic** case (`"01"`/`"10"`,
`"100"`), not just symmetric ones. See
`test_finds_asymmetric_marked_state_other_direction` and
`test_recovers_non_palindromic_secret` in `tests/test_stepper.py`.

## Setup

```bash
cd 2026-06-algorithm-visualizer/qviz
python -m venv .venv
.venv\Scripts\activate                          # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -e ../../2026-05-circuit-simulator/qcsim   # qcsim first, not on PyPI
pip install -e ".[dev]"
pytest tests/ -v          # should show 54 passed
qviz-step                 # try the interactive CLI
```

Already have the repo? See the update commands in
[Contributing.md](Contributing.md#updating-your-checkout).

## What's already done (don't re-do)

- Per-step state snapshotting (incremental, not quadratic)
- Core four algorithms with correctness tests + summaries + structured `outcome()`
- Plain-English state interpretation per step
- Changed-amplitude highlighting, hide-zeros (with no-op note), phase column
- Phase progress bar + windowed circuit (fixes long-horizontal circuits)
- Measurement stage + structured execution summary
- Register-split state labels (`ancilla|input`)
- Divergent Beginner vs Advanced layouts
- Autoplay + menu-loop flow
- Grover amplitude-amplification-across-steps view
- Mid-circuit MEASURE/RESET stepper support (the plumbing)

**Deliberately excluded (as clutter):** full Before→After side-by-side per
step — change-highlighting already shows deltas without doubling output
height, which fits the terminal-first, uncluttered goal.

## What's left

The full, tiered list lives in [Roadmap.md](Roadmap.md).

## Commit style

Match the existing history (`git log --oneline -10`): terse-but-complete
subject, a body explaining the *why*, not just the *what*. See
[Contributing.md](Contributing.md).
