# qviz API Reference

Public functions and classes, by module. Import the common ones from the
package root: `from qviz import step_through, render_step, ...`.

## `qviz.stepper`

```python
step_through(circuit: QuantumCircuit) -> list[Step]
```
Replay a circuit's gate log on a fresh state; one `Step` per non-barrier
gate. The last Step's `statevector` equals `circuit.statevector()`. Does
not mutate `circuit`.

```python
apply_log_entry(working, name, qubits, params) -> bool
```
Apply one gate-log entry to `working` in place. Returns `False` for
BARRIER (no step should be recorded), `True` otherwise. Dispatches
MEASURE/RESET correctly; use this instead of qcsim's `_replay_gate` for
non-unitary entries.

```python
@dataclass
class Step:
    index: int; gate_name: str; qubits: list[int]; params: dict | None
    statevector: np.ndarray; probabilities: dict[str, float]; annotation: str
```

## `qviz.interpret`

```python
interpret_state(step: Step) -> str
```
Plain-English reading: definite outcome / uniform / equal superposition /
most-likely.

```python
phase_label(amp: complex, threshold=1e-9) -> str
```
Phase as a multiple of pi (`"0"`, `"pi"`, `"+0.5*pi"`); `""` for
negligible amplitudes.

```python
nonzero_states(step, threshold=1e-9) -> list[tuple[str, float, complex]]
```
`(label, probability, amplitude)` for weighted basis states, sorted by
descending probability.

```python
dominant_gap(step) -> float
```
Probability of the single most likely outcome (handy for tracking
amplitude amplification).

## `qviz.phases`

```python
segments(phases: list[str]) -> list[tuple[str, int, int]]
```
Group consecutive equal phase labels into `(phase, start, end)` segments.

```python
current_segment_index(segs, step_index) -> int
```
Index of the segment containing `step_index`.

## `qviz.render`

```python
render_step(circuit, step, prev=None, mode="advanced",
            hide_zeros=False, phases=None, registers=None) -> str
```
The composer. Beginner vs advanced layouts. `phases`/`registers` enable
the progress bar, windowed circuit, and register split.

```python
render_statevector(step, prev=None, mode="advanced", hide_zeros=False,
                   threshold=1e-6, ancilla_bits=0) -> str
render_progress_circuit(circuit, up_to_index) -> str
render_windowed_circuit(circuit, lo, hi) -> str
render_phase_progress(phases, step_index) -> str
render_active_caption(step) -> str
sample_measurements(step, register, shots) -> dict[str, int]
render_measurement(result, final_step, shots=100) -> str
render_execution_summary(result, final_step) -> str
```

## `qviz.algorithms.base`

```python
@dataclass
class AlgorithmResult:
    circuit; annotations; title; phases; info; registers; summarize; outcome
    def summary(final_step) -> str
    def execution_summary(final_step) -> ExecutionSummary | None

@dataclass
class ExecutionSummary:
    measured: str; expected: str; success: bool; takeaway: str

input_register(bitstring: str, num_input_qubits: int) -> str
```

Phase constants: `PHASE_PREPARATION`, `PHASE_ORACLE`, `PHASE_DIFFUSION`,
`PHASE_INTERFERENCE`, `PHASE_TRANSFORM`, `PHASE_MEASUREMENT`.

## `qviz.algorithms`

```python
deutsch_jozsa(num_input_qubits=2, oracle="balanced") -> AlgorithmResult
bernstein_vazirani(secret: str) -> AlgorithmResult
grover(marked_state="11", iterations=None) -> AlgorithmResult   # 2 qubits, v1
qft_algorithm(num_qubits=3, initial_state=None) -> AlgorithmResult
```

## `qviz.cli`

```python
main() -> None      # entry point for the `qviz-step` console script
```
