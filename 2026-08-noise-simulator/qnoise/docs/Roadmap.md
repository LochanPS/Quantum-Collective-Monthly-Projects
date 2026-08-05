# Roadmap — what you can build

Every item below is a real, self-contained contribution. Pick one, open a
Discussion, and go. Tiers are a rough guide to difficulty, not a gate — a
motivated beginner can absolutely reach into the higher tiers.

Legend: **[S]** small (an afternoon) · **[M]** medium (a weekend) ·
**[L]** large (multi-session).

---

## 🟢 Beginner — extend the surface

You mostly touch one file, no deep quantum background needed.

### Noise channels (`channels.py`)
- **[S] Coherent over-rotation channel** — a gate that always rotates slightly
  too far (a unitary error). Single Kraus operator.
- **[S] Generalized amplitude damping** — T1 relaxation toward a warm/thermal
  state instead of pure |0>. Extends `AmplitudeDamping`.
- **[S] Biased dephasing channel** — asymmetric phase noise (different rates for
  |0> and |1>).
- **[M] Two-qubit correlated depolarizing** — a 4×4 Kraus channel for CNOT that
  the engine applies to the qubit *pair* (needs a small engine hook — see below).

### Noise models & presets (`model.py`)
- **[S] More hardware-ish presets** — e.g. `photonic_ish`, `neutral_atom_ish`,
  with documented (illustrative) rates.
- **[S] `from_rates(...)` constructor** — build a `NoiseModel` from a small dict
  of gate→rate, so users don't chain `add_channel` calls.

### Demos & docs (`demos.py`, `docs/`)
- **[S] More demo circuits** — QFT, Deutsch-Jozsa, a teleportation circuit
  (great for showing how noise wrecks a fragile protocol).
- **[S] A "noise gallery"** — a script that renders every channel's effect on
  |+> as a before/after, for the docs.

### CLI (`cli.py`)
- **[S] `--json` output** — dump the report as JSON for use in writeups.
- **[M] Save/replay a run config** — write the chosen circuit + model to a file
  and reload it.

---

## 🟡 Intermediate — extend the engine

You touch `engine.py` / `model.py` and think about correctness.

- **[M] Per-qubit noise rates** — a "bad qubit" with a higher error rate than
  its neighbours. Extend `NoiseModel` to key channels by `(gate, qubit)`.
- **[M] Distinct 1-qubit vs 2-qubit gate noise as a first-class concept** —
  today it's done by listing gate names; make it a clean API.
- **[M] Two-qubit channel support in the engine** — `apply_channel` currently
  embeds single-qubit Kraus ops; add an `apply_channel_pair` that embeds a 4×4
  channel on a qubit pair (unblocks correlated noise).
- **[M] Noise sweep as a library function** — generalize `cli.sweep_report` into
  `sweep(qc, channel_factory, rates)` returning structured data (rate, fidelity,
  purity, TVD) for plotting.
- **[M] Metrics pack** — add **effective error per gate**, **process fidelity**,
  and **Hellinger distance** of the sampled distributions to `metrics.py`.
- **[M] Readout-error-only mode** — show how measurement error *alone* distorts a
  perfect distribution, isolated from gate noise (partly there via
  `ReadoutError`; make it a headline CLI option + doc).

---

## 🟠 Advanced — new capabilities

Bigger designs, real quantum-info depth.

- **[L] Fit a noise model from real calibration data** — read an IBM backend's
  T1/T2/gate-error/readout JSON and build a matching `NoiseModel` automatically.
  The most "real-world" contribution here.
- **[L] Monte-Carlo trajectory backend** — instead of an O(4^N) density matrix,
  sample many pure-state runs with stochastic quantum jumps and average. Lets
  qnoise reach far more qubits. Should reproduce the density-matrix result in the
  large-shot limit (that's your test).
- **[L] Correlated / crosstalk noise** — a gate on one qubit disturbs its
  neighbour; spatially-correlated errors across the register.
- **[M] Pauli/Clifford twirling** — twirl a channel into a Pauli channel and
  show the fidelity is preserved; a stepping stone toward efficient simulation.
- **[L] Amplitude-damping-aware measurement timing** — model idle decoherence
  between gates based on gate durations, not just per-gate application.

---

## 🔴 Expert — the sequel

These point at where the whole monthly arc is heading: **error correction needs
a noise model to be meaningful.** Building any of these here makes qnoise the
foundation for a future quantum-error-correction challenge.

- **[L] Repetition-code demo** — encode one logical qubit in three physical
  ones, inject bit-flip noise with qnoise, run majority-vote decoding, and plot
  logical vs physical error rate. The "aha" that motivates QEC.
- **[L] Syndrome extraction under noise** — measure stabilizers on a noisy state
  and show the syndrome is itself unreliable.
- **[L] Threshold-style plot** — logical error rate vs physical error rate across
  code distances, showing the crossover.
- **[L] Density-matrix → stabilizer bridge** — for Clifford circuits, a stabilizer
  backend that scales to many qubits, cross-checked against the density matrix on
  small cases.

---

## How to claim one

1. Skim the [Architecture](Architecture.md) and, for channels, the
   [Channel Development](Channel-Development.md) guide.
2. Post in **[Discussions → Q&A](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/q-a)**
   saying which item you're taking (avoids overlap).
3. Build in your fork, with tests.
4. Submit via **[Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)**.

See [Contributing](Contributing.md) for the full workflow.
