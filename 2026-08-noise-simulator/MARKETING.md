# qnoise — Marketing & Launch Kit

Everything you need to announce **Monthly Project #3: Noisy Quantum Simulator**.
Copy-paste ready. Swap links/handles as needed.

- Repo: https://github.com/LochanPS/Quantum-Collective-Monthly-Projects
- Folder: `2026-08-noise-simulator/`
- Discord: https://discord.gg/QW3yUpNd · WhatsApp / LinkedIn / YouTube as per main README

---

## 1. Positioning — the one thing to communicate

> **A perfect simulator lies to you. Real quantum computers are noisy — qnoise shows you the difference.**

The arc of the three projects tells a story; lead with it:

**Build it (qcsim) → Watch it run (qviz) → See what breaks it (qnoise).**

qnoise is the "reality check" chapter: the same Bell state that's flawless in a
textbook simulator leaks, decoheres, and misfires on real hardware. That gap is
*the entire reason quantum error correction exists* — and now you can see it in
your terminal.

---

## 2. Taglines (pick per channel)

- See what your quantum circuit *actually* does on noisy hardware.
- Ideal → noisy → (someday) corrected.
- Your Bell state isn't as clean as you think.
- Decoherence, in your terminal.
- The difference between the textbook and the machine.
- Noise is not a bug. It's the whole point.

---

## 3. Descriptions (three lengths)

**One line (GitHub "About", package summary):**
> Density-matrix noise simulator for quantum circuits — see the gap between ideal and real hardware, in your terminal.

**Short (50 words):**
> qnoise is an open-source, terminal-based noise simulator built on qcsim. Take any quantum circuit and watch what really happens on imperfect hardware: decoherence, gate error, and readout error, rendered as ideal-vs-noisy histograms with fidelity metrics. Five noise channels, hardware presets, 84 tests. Pure Python + NumPy.

**Long (announcement paragraph):**
> Month three of the Quantum Collective build-along is live. After building a
> circuit simulator (qcsim) and an algorithm visualizer (qviz), we're confronting
> the thing every real quantum computer has and no textbook simulator shows:
> **noise.** qnoise evolves your circuit as a *density matrix* and applies
> realistic hardware noise — amplitude damping (T1), phase damping (T2),
> depolarizing, bit/phase flips, and readout error — then shows you, side by side,
> how far the noisy result drifted from the ideal one. It ships with hardware-style
> presets (`ibm_ish`, `ion_ish`), a fidelity/trace-distance/TVD metrics panel, an
> interactive CLI, and 84 tests, including a guarantee that with noise off it
> reproduces qcsim exactly. It's the natural setup for the next chapter: quantum
> error correction, which only means anything once you can simulate noise.

---

## 4. Feature bullets (for slides / README / posts)

- 🎛️ **Density-matrix engine** — the correct tool for mixed states: `ρ → UρU†` per gate, `ρ → ΣKρK†` per noise channel
- 🌫️ **5 noise channels** — depolarizing, amplitude damping (T1), phase damping (T2), bit-flip, phase-flip
- 🏭 **Hardware presets** — `ibm_ish` (superconducting-style), `ion_ish` (trapped-ion-style), plus a custom `NoiseModel` builder
- 📉 **Readout error** — model imperfect measurement, per-qubit
- 📊 **Ideal vs noisy** — colored side-by-side histograms; leakage into "wrong" outcomes flagged in red
- 🎚️ **Drift metrics** — state fidelity, trace distance, total-variation distance, purity gauge
- 🔬 **Noise sweep** — fidelity-vs-rate decay curve, built into the CLI
- ✅ **Trust anchor** — with noise off, reproduces qcsim's exact result. 84 passing tests
- 🧩 **Built to extend** — add a noise channel in ~15 lines; Beginner→Expert roadmap
- 🐍 **Zero heavy deps** — pure Python + NumPy, terminal-only, cross-platform

---

## 5. Social posts

### LinkedIn (company / founder voice)

> **Month 3 of building quantum tools in public is live: qnoise 🌫️**
>
> A perfect simulator lies to you. It tells you a Bell state is exactly 50/50,
> clean, forever. But run that circuit on a real quantum computer and it's messy —
> qubits leak energy, gates misfire, measurement itself is wrong a few percent of
> the time.
>
> qnoise makes that gap visible. Give it any circuit and it shows you the ideal
> result next to what a *noisy* device actually produces — with fidelity metrics
> quantifying exactly how far things drifted.
>
> The build-along so far:
> 1️⃣ qcsim — build the circuit
> 2️⃣ qviz — watch the algorithm run
> 3️⃣ qnoise — see what noise does to it
>
> It's open source, terminal-based, pure Python. And it's the foundation for
> where we're headed next: quantum error correction — which only matters once you
> can simulate the noise it's fighting.
>
> Come build with us 👇 [repo link]
>
> #QuantumComputing #OpenSource #Python #QuantumCollective #BuildInPublic

### Twitter / X (thread)

> 1/ A perfect quantum simulator lies to you.
> It says your Bell state is a clean 50/50.
> Real hardware? Not even close.
> So we built qnoise — a noise simulator you run in your terminal. 🧵

> 2/ qcsim gave you the perfect Bell state.
> qviz showed you how it's built, gate by gate.
> qnoise shows you what NOISE does to it:
> decoherence, gate error, readout error — side by side with the ideal.

> 3/ Under the hood it swaps the state *vector* for a density *matrix* — the only
> thing that can represent a mixed (noisy) state. Two rules run everything:
> gate: ρ → UρU†
> noise: ρ → ΣKρK†

> 4/ 5 noise channels (T1, T2, depolarizing, bit/phase flip), hardware presets,
> readout error, a fidelity gauge, and a noise-sweep decay curve — all in a
> colored terminal UI.

> 5/ Best part: turn the noise off and it reproduces the ideal simulator EXACTLY.
> 84 tests guard that. Trust, then break it on purpose.

> 6/ Open source, pure Python + NumPy. Next up: quantum error correction 👀
> Star / build with us: [repo link]
> #QuantumComputing #Python #OpenSource

### WhatsApp / Telegram broadcast

> 🌫️ *Monthly Project #3 is LIVE: qnoise*
>
> See what your quantum circuit *actually* does on real, noisy hardware — not the
> perfect textbook version.
>
> ✅ 5 noise types (T1, T2, depolarizing, bit/phase flip)
> ✅ IBM-style & ion-style presets
> ✅ Ideal vs noisy, side by side, in color
> ✅ Pure Python, runs in your terminal
>
> 3 commands to try it:
> `git clone <repo>`
> `cd 2026-08-noise-simulator/qnoise`
> `pip install -e ../../2026-05-circuit-simulator/qcsim && pip install -e . && qnoise-run`
>
> Weekly session Sunday 4 PM IST — bring questions. Repo + Discord in bio.

### Discord announcement

> @everyone 🌫️ **Project #3 dropped: qnoise — Noisy Quantum Simulator**
>
> The reality-check chapter. Build a circuit, then watch noise wreck it:
> decoherence, gate error, readout error — with fidelity metrics on the drift.
>
> • Reference engine is live in `2026-08-noise-simulator/qnoise/`
> • Easiest first contribution: **add a noise channel** (~15 lines, guide in docs)
> • Full Beginner→Expert roadmap in `docs/Roadmap.md`
> • Claim a task in #q-a, submit in #submissions
>
> `qnoise-run` to try it. Let's break some qubits. 🧊

### Instagram / visual caption

> Same circuit. Two realities. 🧊➡️🌫️
> Left: the perfect simulator. Right: what a real quantum computer does.
> That gap is why quantum error correction exists — and now you can watch it.
> Open source, link in bio. #quantumcomputing #python #opensource

---

## 6. "Why it matters" narrative (for a blog post / video intro)

> Every intro to quantum computing shows you the same magic trick: two gates, a
> Bell state, perfect correlation. What they don't show you is that this only
> happens on paper. On a real machine, a qubit holds its state for microseconds
> before it decays. Every gate is a physical pulse that's slightly off. Reading
> the answer is itself a noisy measurement. The "perfect" Bell state comes back
> with a few percent of everything-else mixed in.
>
> This isn't a footnote — it's the central engineering problem of the entire
> field. Quantum error correction, the thing standing between us and useful
> quantum computers, exists entirely to fight this noise. But you can't
> appreciate the cure until you've seen the disease.
>
> qnoise is the disease, made visible, in your terminal.

---

## 7. Demo script (for a 60–90s GIF or video)

1. Run `qnoise-run`. (Colored banner lands.)
2. Pick `bell`, then `ideal`. → Perfect 50/50, fidelity 1.000, "excellent". "This is the lie."
3. Run again: `bell`, then `ibm_ish`. → Red leakage bars appear in 01/10, fidelity drops, purity < 1. "This is the truth."
4. Run again: `bell`, `depol`, rate `0.2`. → Big spread. "Crank the noise, watch it fall apart."
5. Say `y` to the sweep. → The fidelity-vs-rate decay curve prints. "The decoherence curve, live."
6. Tag: "ideal → noisy → next month, corrected."

Recording tip: use a dark-theme terminal at ~100 cols; the colored panels and
eighth-block bars are the visual hook. `asciinema rec` → embed, or screen-record
to GIF.

---

## 8. Screenshot captions

- "Ideal vs noisy: the red dots are leakage — outcomes that shouldn't exist, created by noise."
- "The fidelity gauge: 1.000 is perfect, and noise drags it down in real time."
- "One circuit, swept across noise rates — the decoherence decay curve."
- "Turn noise off and it matches the perfect simulator exactly. 84 tests prove it."
- "One hub, three tools: build → visualize → add noise."

---

## 9. Launch checklist

- [ ] Repo README + challenge README live (done — folder `2026-08-noise-simulator/`)
- [ ] Record the demo GIF (script in §7) and drop it in the challenge README
- [ ] Pin a Discord announcement (copy in §5) + open #submissions thread
- [ ] LinkedIn post (§5) from the org page, tag contributors
- [ ] X thread (§5), pin for the week
- [ ] WhatsApp broadcast (§5) with the 3-command quick start
- [ ] Add "Project #3" to the Sunday session agenda; do a live `qnoise-run` walk
- [ ] Update the repo's social preview image to a qnoise screenshot
- [ ] Seed 2–3 "good first issue" tasks from `docs/Roadmap.md` 🟢 tier

---

## 10. Hashtags & handles

`#QuantumComputing` `#QuantumCollective` `#OpenSource` `#Python` `#BuildInPublic`
`#QuantumError` `#Decoherence` `#SciComp` `#NumPy` `#LearnInPublic`

---

## 11. Call to action (standard footer for any post)

> ⭐ Star the repo · 🍴 Fork & build · 💬 Join the Discord · 🗓️ Sundays 4 PM IST
> Easiest way in: add a noise channel — 15 lines, guide in `docs/Channel-Development.md`.
