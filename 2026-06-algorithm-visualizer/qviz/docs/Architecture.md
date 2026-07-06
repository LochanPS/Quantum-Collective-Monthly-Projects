# qviz Architecture

qviz is a thin, layered package on top of [qcsim](../../../2026-05-circuit-simulator/qcsim/).
Each layer has one job and depends only on the ones below it.

```
cli.py            interactive terminal UI (menu, step loop, autoplay)
  │
  ├── render.py         turns a Step into printable text (bars, phases, circuit window, measurement, summary)
  │     ├── interpret.py    plain-English reading of a state (definite / uniform / superposition)
  │     └── phases.py       groups per-step phase labels into segments
  │
  ├── algorithms/       each module builds a circuit + returns an AlgorithmResult
  │     └── base.py         AlgorithmResult, ExecutionSummary, helpers, phase constants
  │
  └── stepper.py        replays a circuit gate-by-gate → list[Step]
        │
        └── qcsim.QuantumCircuit   (the dependency; not modified by qviz)
```

## The two data structures everything revolves around

### `Step` (stepper.py)

A snapshot of the circuit **immediately after one gate**:

```python
@dataclass
class Step:
    index: int              # position in the gate sequence (0-based)
    gate_name: str          # "H", "CNOT", ...
    qubits: list[int]       # qubits the gate acted on
    params: dict | None     # gate params (e.g. {"lam": 1.57})
    statevector: np.ndarray # full state right after this gate
    probabilities: dict     # {bitstring: probability}
    annotation: str         # human explanation (filled by the algorithm layer)
```

`step_through(circuit)` returns `list[Step]` — one per non-barrier gate.
The last Step's `statevector` matches `circuit.statevector()` exactly.

### `AlgorithmResult` (algorithms/base.py)

Everything the UI needs to present one algorithm run:

```python
@dataclass
class AlgorithmResult:
    circuit: QuantumCircuit
    annotations: list[str]   # one per gate, same order as circuit._log
    title: str
    phases: list[str]        # one per gate (Preparation/Oracle/Diffusion/...)
    info: dict               # always-shown facts (marked state, secret, ...)
    registers: dict          # {"input": [0,1], "ancilla": [2]}
    summarize: callable      # final Step → narrative answer
    outcome: callable        # final Step → ExecutionSummary (measured/expected/success)
```

The **1:1 alignment** rule: `annotations` and `phases` each have exactly
one entry per gate in `circuit._log`. The CLI zips `annotations` onto each
`Step.annotation`; `phases` drives the progress bar and windowed circuit.
Break the alignment and labels silently attach to the wrong gate — the
`test_*_count_matches_gate_count` and `test_phases_align_with_gates` tests
guard against it.

## Layer responsibilities

| Layer | Owns | Never does |
|---|---|---|
| `stepper.py` | Replaying gates, snapshotting state | Any algorithm-specific meaning |
| `interpret.py` | Plain-English state descriptions, phase math | Terminal formatting (ANSI, bars) |
| `phases.py` | Grouping phase labels into segments | Rendering |
| `render.py` | ASCII/ANSI output, layout, modes | Algorithm logic |
| `algorithms/` | Building circuits + all algorithm meaning | Rendering, stepping |
| `cli.py` | Menu, key handling, autoplay | Computing state (delegates to stepper) |

**Why the split matters:** the interpretation and algorithm layers are
front-end-agnostic. A future graphical front-end (the paid Lab Suite)
reuses `interpret_state`, `AlgorithmResult`, and the stepper without
touching `render.py` or `cli.py`.

## Data flow for one run

1. `cli.py` calls an algorithm builder → `AlgorithmResult`.
2. `step_through(result.circuit)` → `list[Step]`.
3. Annotations are zipped onto the steps.
4. Per step, `render_step(...)` composes: phase progress
   (`phases.py`) + windowed circuit + state table + interpretation
   (`interpret.py`).
5. On the last step, `render_measurement` samples the meaningful register
   and `render_execution_summary` calls `result.outcome(final_step)`.

See [Developer-Guide.md](Developer-Guide.md) for the per-module deep dive
and design decisions, and [API-Reference.md](API-Reference.md) for exact
signatures.
