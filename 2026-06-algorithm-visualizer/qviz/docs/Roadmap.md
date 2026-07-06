# qviz Roadmap & Future Contributions

A menu of things worth building, grouped by theme and tagged by difficulty.
Pick anything unclaimed. Nothing here is assigned — open an issue or PR to
claim it.

**Difficulty tags:** 🟢 Beginner · 🔵 Intermediate · 🟠 Advanced · 🔴 Expert

Two contributions cut across everything — read these first:
- Adding an algorithm → [Algorithm-Development.md](Algorithm-Development.md)
- Adding a rendering feature → [Rendering-Guide.md](Rendering-Guide.md)

---

## 1. New quantum algorithms

Each is a new module returning an `AlgorithmResult`. Ordered roughly by
effort.

- 🟢 **Superdense coding** — 2 qubits, send 2 classical bits with 1 qubit.
  Short, great teaching example, no new plumbing.
- 🟢 **Quantum teleportation** — 3 qubits. The stepper already supports
  mid-circuit MEASURE/RESET (`apply_log_entry`); the work is the module +
  showing the classical feed-forward correctly through the steps.
- 🔵 **Simon's algorithm** — hidden-period problem, exponential speedup.
  Oracle uses CNOT fan-out keyed on the secret string; needs a
  non-palindrome test.
- 🔵 **Quantum counting** — combines Grover + phase estimation to count
  solutions. Depends on QPE below.
- 🔵 **Quantum walk (discrete, on a line/cycle)** — coin + shift operators;
  a nice `Preparation → Coin → Shift` phase story.
- 🟠 **Quantum Phase Estimation (QPE)** — estimate an eigenphase. Reuses
  the existing QFT (inverse). Foundational for counting/Shor.
- 🟠 **Amplitude estimation** — QPE applied to a Grover operator.
- 🟠 **Shor subroutines** — the period-finding core (modular exponentiation
  + inverse QFT) as a visualized module; full factoring is out of scope,
  the subroutine is not.
- 🟠 **VQE step** — one variational step (ansatz → expectation → note the
  classical update). Terminal-only: show the energy estimate, not a live
  optimizer plot.
- 🟠 **QAOA step** — one cost/mixer layer with the phase story.
- 🔴 **Quantum error correction examples** — 3-qubit bit-flip / phase-flip
  code, or a Shor 9-qubit code. Show syndrome extraction as its own phase.
  Needs mid-circuit measurement (already supported).
- 🔴 **Generalize Grover to N qubits** — the current oracle is 2-qubit
  only. Needs a multi-controlled-Z; qcsim has Toffoli but not
  arbitrary-arity controlled-Z. May need a new qcsim gate or an
  ancilla-based decomposition (check `qcsim/gates.py`, `circuit.py`).

---

## 2. Visualization modes

New ways to render the same `Step`/`AlgorithmResult` data.

- 🟢 **Improve QFT annotations** — name *which* qubit-pair frequency each
  controlled-phase encodes (they already show type + `pi/n` angle).
- 🔵 **Comparison mode** — run two configs side by side (Grover 1 vs 2
  iterations; two oracle types) and diff their state tables per step.
- 🔵 **Measurement history** — accumulate multi-shot results across a run,
  show how the distribution sharpens.
- 🔵 **State-evolution timeline** — a compact one-line-per-step sparkline of
  the dominant-state probability across the whole run (Grover already has a
  version of this; generalize it).
- 🟠 **Subsystem / partial-trace views** — reduced state of a register
  (e.g. just the input qubits of DJ/BV), factoring out the ancilla.
- 🟠 **Entanglement visualization** — per-step entanglement measure (e.g.
  bipartite entropy) with a simple bar; flag when a step creates
  entanglement.
- 🔴 **Density-matrix visualization** — show the reduced density matrix of a
  subsystem as an ASCII heatmap. Bigger lift (needs partial trace).

---

## 3. Educational features

- 🟢 **Glossary** — a `docs/Glossary.md` of terms (superposition, oracle,
  ancilla, phase kickback, amplitude amplification) linked from
  annotations.
- 🔵 **Guided tutorials / walkthroughs** — scripted runs with pauses and
  prompts ("what will measuring q0 give?") for each core algorithm.
- 🔵 **Interactive checkpoints / quizzes** — at key steps, ask the user to
  predict the next state before revealing it.
- 🔵 **Exportable teaching material** — dump a run as Markdown/HTML (text
  only) for slides or handouts.
- 🟠 **Algorithm "explain me" mode** — a longer narrative track per
  algorithm (the theory, not just per-gate notes).

---

## 4. Debugging & verification tools

- 🔵 **Step-diff viewer** — given two consecutive steps, print exactly which
  amplitudes changed and by how much (complements the yellow highlight).
- 🔵 **Circuit validator** — sanity checks before stepping (qubit indices in
  range, no obviously malformed gate log).
- 🔵 **Oracle visualizer** — for oracle-based algorithms, print the truth
  table the oracle implements.
- 🟠 **Correctness / invariant checker** — assert per-step invariants (norm
  == 1, expected register untouched during a phase).
- 🔴 **Algorithm verification harness** — property-based: generate many
  parameter instances per algorithm and assert the final answer matches the
  expected classical computation.

---

## 5. Performance

- 🔵 **Benchmarking script** — time stepping across qubit counts; publish a
  small table so regressions are visible.
- 🟠 **Lazy rendering** — only render the current step, not all steps, for
  large circuits (the CLI already does this; audit for waste).
- 🟠 **Caching** — memoize windowed-circuit builds when jumping around.
- 🔴 **Large-circuit stepping** — profile and optimize `step_through` for
  15+ qubit circuits. **Profile first** — it's already incremental, so
  confirm there's a real bottleneck before rewriting.

---

## 6. Rendering polish

- 🟢 **Compact layout option** — a `--compact` view that trims blank lines
  for small terminals.
- 🟢 **Better ASCII rendering** — improve alignment/spacing of the state
  table and circuit window on narrow terminals.
- 🔵 **Themes** — color schemes (or no-color mode) selectable at launch;
  keep the ASCII fallback intact.
- 🔵 **Customizable views** — let the user choose which panels show
  (state / circuit / interpretation / measurement).

---

## 7. Testing

- 🟢 **More per-algorithm correctness tests** — edge cases (1-qubit DJ,
  single-bit BV, all-ones secret).
- 🔵 **Randomized circuit generation** — build random valid circuits, step
  them, assert the final step matches `circuit.statevector()`.
- 🔵 **Regression suite** — snapshot known-good rendered output for the core
  algorithms; diff on change.
- 🟠 **Property-based testing** (Hypothesis) — invariants over random
  parameters (norm preserved, annotation/phase alignment always holds).

---

## 8. Developer tooling

- 🔵 **Algorithm template** — a `docs/` or scaffolding script that stamps
  out a new `algorithms/<name>.py` with the `add()` helper and a test stub.
- 🟠 **Plugin / extension API** — discover algorithm modules dynamically so
  contributors can drop in a file without editing `cli.py`.
- 🟠 **Profiling / debug utilities** — a `--profile` flag timing each layer.

---

## 9. Documentation

- 🟢 **Architecture diagrams** — a real image/ASCII diagram of the layer
  flow for [Architecture.md](Architecture.md).
- 🟢 **Troubleshooting guide** — expand [FAQ.md](FAQ.md) as issues surface.
- 🔵 **Per-algorithm write-ups** — a short `docs/algorithms/<name>.md`
  explaining the theory behind each reference algorithm.
- 🔵 **Worked examples** — annotated example scripts using the Python API.

---

## Already done — don't re-do

Per-step snapshotting (incremental) · core four algorithms + summaries +
structured outcomes · plain-English interpretation · changed-amplitude
highlighting · hide-zeros (with no-op note) · phase column · phase
progress bar · windowed circuit · measurement stage · execution summary ·
register-split labels · beginner/advanced layouts · autoplay · menu-loop ·
Grover amplitude-amplification view · mid-circuit MEASURE/RESET plumbing.

See [Developer-Guide.md](Developer-Guide.md#whats-already-done-dont-re-do)
for details.
