# July 2026 — Quantum Algorithm Visualizer

**Status:** In preparation — full reveal July 1, 2026
**Submit here:** [Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)

---

## What is this?

A **step-through visualizer for quantum algorithms** — watch a circuit execute one gate at a time and see exactly how the state vector evolves at each step, instead of only seeing the final answer.

Running `qc.h(0).cnot(0,1)` tells you the Bell state exists. It doesn't show you *how it got there* — which gate created the superposition, which gate created the entanglement, what the amplitudes looked like in between. That's the gap this project fills: take any circuit built with [qcsim](../2026-05-circuit-simulator/qcsim/), replay it gate-by-gate, and render the state at every step.

This is the natural sequel to May's circuit simulator — it builds directly on top of `qcsim` rather than starting from scratch.

```
Step 0: |00⟩
Step 1: H(q0)     -> (|00⟩ + |10⟩) / √2
Step 2: CNOT(0,1) -> (|00⟩ + |11⟩) / √2     <- entangled
```

---

## What's Already Built

Nothing yet — this README is the problem statement, written ahead of the July 1 reveal so early contributors can start thinking about it.

What *will* exist by reveal day: a minimal reference stepper (depends on `qcsim` as a library) that can replay any circuit's gate log and snapshot the state after each step, plus terminal-only rendering (statevector bars, probability histogram, circuit diagram with the current step highlighted) — the same ASCII style as `qcsim`'s existing `draw_statevector`/`draw_histogram`.

**Reference algorithms at launch:** Quantum Fourier Transform, Grover's search, Deutsch-Jozsa, Bernstein-Vazirani. Quantum teleportation and a basic VQE step are planned as follow-up additions, not launch-day requirements.

**Free vs. extended:** the terminal stepper is the free, open-source core. A graphical version (real-time animated charts, Bloch sphere per step) lives in a separate paid product built on the same engine — if you're contributing here, you're contributing to the open core, not blocked by or required to build the graphical layer.

---

## What You Can Build

### Start Here — Core Features

- **New algorithm modules** — any circuit with clear conceptual steps (e.g. quantum walk, simple amplitude estimation) plugs into the stepper the same way the core four do
- **Step annotations** — human-readable labels per step ("Oracle marks |11⟩", "Diffusion amplifies marked state") so the visualizer teaches *why*, not just *what*
- **Export a step-by-step trace** — JSON or text log of every step's state, for use in writeups/teaching material

### Go Deeper — Extend the Stepper

- **Diffing between steps** — highlight which amplitudes changed and by how much
- **Multi-qubit subsystem views** — for algorithms where only a subset of qubits matters at a given step (e.g. ancilla qubits in Deutsch-Jozsa)
- **Comparison mode** — run two algorithms side by side (e.g. Grover with 1 vs 2 iterations)

### Advanced — Push the Limits

- **Algorithm correctness checker** — verify a stepped-through algorithm actually reaches the expected final state, useful as a contributor-facing test harness
- **Generalize to N-qubit oracles** — Grover/Deutsch-Jozsa currently assume small fixed qubit counts; generalize the oracle interface

---

## Minimum Requirements (for your own implementation)

If you're building your own stepper rather than extending the reference:

1. Given a circuit's gate sequence, produce the state vector after **every individual gate**, not just the final state
2. Render at least one of: amplitude bars, probability histogram, or circuit diagram with current-step highlighting
3. Correctly step through at least one of the core four algorithms end to end
4. Tests confirming the final step matches the circuit's actual final state (no drift from the step-by-step replay)

---

## How to Contribute

**Add an algorithm module:** depend on `qcsim` as a library, build the circuit, define step annotations — guide will land in `docs/adding-algorithms.md` alongside the full reveal.

**Submit your own visualizer:** fork, build, post in [GitHub Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)

---

## Learning Resources

- **[qcsim source code](../2026-05-circuit-simulator/qcsim/qcsim/)** — the simulator this builds on
- [Qiskit Textbook — Grover's Algorithm](https://qiskit.org/learn/) — the canonical walkthrough
- [Quantum Algorithm Zoo](https://quantumalgorithmzoo.org/) — catalogue of known quantum algorithms, good source for "Go Deeper" ideas

---

Want to suggest what this should cover? Open a [feature request](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/issues/new?template=feature_request.md) tagged `future-challenge`.
