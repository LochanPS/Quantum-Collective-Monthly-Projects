# FAQ

**Do I need to have done May's or June's challenge first?**
No, but qnoise depends on `qcsim` (May's project) as a library, so you install
it first. You don't need to understand qcsim's internals — just build circuits
with it.

**Why a density matrix instead of a state vector?**
Noise turns a pure state into a *mixture* of states, which a single state vector
can't represent. A density matrix can represent both pure and mixed states. See
[Architecture](Architecture.md).

**How many qubits can it handle?**
The density matrix is 2^N × 2^N, so memory grows as O(4^N). Expect a practical
ceiling around 8–10 qubits on a laptop. The Monte-Carlo trajectory backend on
the [Roadmap](Roadmap.md) is the way past that.

**With noise off, does it exactly match qcsim?**
Yes — that's a tested guarantee. `run(qc, presets.ideal())` and `run_ideal(qc)`
reproduce qcsim's statevector probabilities bit-for-bit.

**Are the `ibm_ish` / `ion_ish` preset numbers real?**
No. They're illustrative shapes (superconducting has heavier 2-qubit error;
trapped ions have very low error), not calibrations of any specific device.
Fitting a model to real backend data is an Advanced roadmap item.

**What's a Kraus operator, briefly?**
A set of matrices `{Kₖ}` that describe a noise process via
`rho -> Σₖ Kₖ rho Kₖ†`. Every channel here is defined by giving its Kraus
operators. See [Channel Development](Channel-Development.md).

**Why does purity drop but trace stays 1?**
Trace is total probability — it must stay 1 (channels are trace-preserving).
Purity `Tr(rho²)` measures how "mixed" the state is; noise lowers it from 1.0
(pure) toward `1/2^N` (maximally mixed). That drop *is* decoherence.

**Is measurement collapsing the state?**
No. `sample()` draws outcomes from the diagonal of `rho` without modifying it, so
you can sample repeatedly — the same choice qcsim makes.

**How is this different from the paid graphical version?**
The terminal engine here is the free, open-source core. A separate paid product
adds animated/graphical visualization on top of the same engine. Contributing
here means contributing to the open core; you're never blocked by the graphical
layer.

**Where do I get help?**
Discord `#code-help`, or
[Discussions → Q&A](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/q-a).
