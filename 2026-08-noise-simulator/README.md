# August 2026 — Noisy Quantum Simulator

**Status:** ✅ Live — reference implementation in [`qnoise/`](qnoise/)
**Submit here:** [Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)

**Try it now:**
```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-08-noise-simulator/qnoise
pip install -e ../../2026-05-circuit-simulator/qcsim   # install qcsim first
pip install -e . && qnoise-run
```

---

## What is this?

A **noise simulator for quantum circuits** — take any circuit and see what
it *actually* does on a real, imperfect quantum device, instead of the clean
textbook answer.

May's [qcsim](../2026-05-circuit-simulator/qcsim/) gives you a perfect Bell
state: exactly 50% `00`, 50% `11`, nothing else. June's
[qviz](../2026-06-algorithm-visualizer/qviz/) shows you how that state gets
built, gate by gate. But run the same circuit on real hardware and you get
something messier — a few percent `01`, a few percent `10`, amplitudes that
have decayed. Qubits leak energy, gates misfire, and measurement itself is
imperfect.

That gap between *ideal* and *real* is the whole reason quantum error
correction exists. This project makes the gap visible.

```
Bell state on an ideal simulator:      Bell state with depolarizing noise (p=0.05):

  00  ██████████████████  50.0%          00  █████████████████   47.1%
  11  ██████████████████  50.0%          01  █                    2.8%
                                         10  █                    2.9%
                                         11  ████████████████    47.2%

  fidelity vs ideal: 1.000                fidelity vs ideal: 0.941
```

This is the natural third step in the arc: **build** the circuit (qcsim) →
**watch** the algorithm run (qviz) → **see what breaks it** (qnoise). And it
sets up the obvious sequel — you can't correct errors you can't simulate.

---

## The core idea (one concept to learn)

A perfect quantum state is a **state vector** — one clean list of amplitudes.
qcsim uses this. But a noisy state is a *probabilistic mixture* of many
possible state vectors, and a single vector can't represent that. The tool for
the job is a **density matrix** `ρ` — a 2^N × 2^N matrix that describes both
pure and mixed states.

Two rules run the entire simulator:

| Operation | Ideal (state vector) | Noisy (density matrix) |
|-----------|----------------------|------------------------|
| Apply a gate `U` | `ψ → U ψ` | `ρ → U ρ U†` |
| Apply noise | *(none)* | `ρ → Σₖ Kₖ ρ Kₖ†` (Kraus operators) |

That second row — the **Kraus operators** `{Kₖ}` — is how every kind of noise
(energy decay, dephasing, random flips, readout error) gets expressed. Learn
those two lines and you understand the whole engine.

---

## What's Already Built

The reference engine (`qnoise`) is live in [`qnoise/`](qnoise/): it depends on
`qcsim` as a library, takes any circuit's gate log, evolves it as a **density
matrix**, and applies a chosen **noise model** after each gate. Output is
terminal-only — a side-by-side ideal-vs-noisy probability histogram in the same
ASCII style as qcsim's `draw_histogram`, plus fidelity / trace-distance / TVD
numbers quantifying how far the noisy result drifted.

**Reference noise channels shipped:** depolarizing, amplitude damping (T1),
phase damping (T2), bit-flip, phase-flip, and readout (measurement) error.
Hardware-flavored presets (`ibm_ish`, `ion_ish`) bundle these. Correlated/
crosstalk noise and fitting a model from real IBM calibration data are on the
[Roadmap](qnoise/docs/Roadmap.md) as Advanced contributions, not shipped.

**What's in the box:** 84 passing tests (including a parity check that noise-off
reproduces qcsim exactly), an interactive `qnoise-run` CLI, runnable
[`examples/`](qnoise/examples/), and full [docs](qnoise/docs/README.md).

**Jump straight to:**
- **[→ Package README](qnoise/README.md)** — install, quick start, API
- **[→ Documentation index](qnoise/docs/README.md)** — architecture, guides
- **[→ Roadmap](qnoise/docs/Roadmap.md)** — Beginner → Expert ideas, by tier
- **[→ Add a noise channel](qnoise/docs/Channel-Development.md)** — easiest first contribution

**Free vs. extended:** the terminal engine is the free, open-source core. A
graphical version (animated decoherence, Bloch-sphere shrinkage, live noise
sweeps) lives in a separate paid product built on the same engine — contributing
here means contributing to the open core, never blocked by the graphical layer.

---

## What You Can Build

### Start Here — Core Features

- **New noise channels** — any physical noise process expressible as a set of
  Kraus operators plugs into the engine the same way the launch channels do
  (e.g. leakage, coherent over-rotation, biased dephasing)
- **Preset noise models** — bundle channels + rates into a named model
  ("ibm-ish", "trapped-ion-ish") so a user picks one instead of hand-tuning
- **Readout-error visualization** — show how measurement error alone distorts a
  perfect distribution, separate from gate noise

### Go Deeper — Extend the Engine

- **Per-gate / per-qubit noise** — different error rates for 1-qubit vs 2-qubit
  gates, or a "bad qubit" with a higher rate
- **Noise sweep** — run one circuit across a range of noise strengths and plot
  fidelity vs. rate, so you can see the decay curve
- **Metrics pack** — beyond fidelity: trace distance, total-variation distance
  of the distributions, effective error per gate

### Advanced — Push the Limits

- **Fit a model from calibration data** — read an IBM backend's T1/T2/gate-error
  JSON and build a matching noise model automatically
- **Sparse / trajectory backend** — density matrices cost O(4^N) memory;
  implement a Monte-Carlo quantum-trajectory backend that samples pure-state
  runs instead, to reach more qubits
- **Correlated noise** — two-qubit crosstalk / spatially-correlated errors,
  where a gate on one qubit disturbs its neighbor

---

## Minimum Requirements (for your own implementation)

If you're building your own noise simulator rather than extending the reference:

1. Represent state as a **density matrix** and apply gates as `ρ → U ρ U†`,
   reusing (or matching) qcsim's gate set and LSB convention
2. Apply at least **one Kraus noise channel** after gates, and confirm `ρ` stays
   a valid density matrix (Hermitian, trace 1, positive semidefinite)
3. Sample measurement outcomes from the noisy state (the diagonal of `ρ`)
4. Compare noisy vs. ideal with at least one metric (**state fidelity** or
   total-variation distance of the distributions)
5. Tests proving that with **noise turned off**, your engine reproduces qcsim's
   exact statevector result — no drift

---

## How to Contribute

The reference implementation will live in [`qnoise/`](qnoise/), with full docs
in `qnoise/docs/`.

**Add a noise channel:** implement its Kraus operators, register it, done — the
engine applies it like any other.

**Find something to build:** the Roadmap (shipping with the reference) lists
Beginner → Expert ideas across channels, models, metrics, and backends.

**Submit your own simulator:** fork, build, post in
[GitHub Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)
