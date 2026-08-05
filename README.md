# Quantum Collective — Monthly Projects

Monthly collaborative coding challenges from **Quantum Collective** — a 600+ member quantum computing community based in India.

Build real quantum tools. Learn by shipping.

**[Discord](https://discord.gg/QW3yUpNd) · [WhatsApp](https://chat.whatsapp.com/KK2cx4st54uJONp0f8BWdS) · [LinkedIn](https://www.linkedin.com/company/113013769/) · [YouTube](https://www.youtube.com/@QuantumCollectiveIndia)**

---

## 📁 Repository Structure

```
Quantum-Collective-Monthly-Projects/
│
├── 2026-05-circuit-simulator/               ← June 2026: Quantum Circuit Simulator (LIVE)
│   ├── qcsim/                               ← Full reference implementation
│   │   ├── qcsim/                          ← Core simulator source code
│   │   ├── examples/                       ← Runnable examples (Bell, GHZ, Grover, etc.)
│   │   ├── tests/                          ← 124 tests
│   │   ├── docs/adding-gates.md            ← How to add new gates
│   │   └── README.md                       ← Full qcsim documentation
│   ├── circuit-library/                    ← Community-submitted circuits
│   │   ├── examples/                       ← Verified circuits (Bell, GHZ, etc.)
│   │   ├── search.py                       ← Search circuits by name/tags/difficulty
│   │   ├── add_circuit.py                  ← Submit your circuit
│   │   └── CONTRIBUTING-CIRCUITS.md        ← How to submit circuits
│   ├── EXAMPLES.md                         ← Expected API patterns
│   └── README.md                           ← Challenge description + what to build
│
├── 2026-06-algorithm-visualizer/            ← July 2026: Quantum Algorithm Visualizer (LIVE)
│   └── qviz/                                ← Reference implementation (depends on qcsim)
│
├── 2026-08-noise-simulator/                 ← August 2026: Noisy Quantum Simulator (LIVE)
│   ├── qnoise/                              ← Reference implementation (depends on qcsim)
│   │   ├── qnoise/                         ← Engine: density matrix, channels, model, metrics
│   │   ├── examples/                       ← Runnable examples (noisy Bell, sweep, custom model)
│   │   ├── tests/                          ← 84 tests (incl. noise-off parity with qcsim)
│   │   └── docs/                           ← Architecture, Channel-Development, Roadmap, API
│   └── README.md                           ← Challenge description + what to build
│
├── docs/
│   └── FAQ.md                              ← Frequently asked questions
│
├── CHANGELOG.md                            ← What changed and when
├── SECURITY.md                             ← How to report vulnerabilities
├── CONTRIBUTING.md                         ← How to participate and submit
└── README.md                               ← This file
```

---

## 🚀 What's Live Now

### June 2026 — Quantum Circuit Simulator

A full quantum circuit simulator with an interactive visual builder and community circuit library.

**Try it now — 3 commands:**
```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-05-circuit-simulator/qcsim
pip install -e . && qcsim-interactive
```

**What's inside:**
| Feature | Description |
|---------|-------------|
| 🎮 Interactive TUI | Build circuits visually — no coding needed, up to 15 qubits |
| 🔗 25+ Gates | H, X, SXdg, CNOT, SWAP, Rx, Ry, Rz, Toffoli and more |
| 📊 Live Metrics | Depth, gate count, T-gate cost, entanglement |
| 🔍 Pattern Recognition | Recognizes Bell state, GHZ, and other known circuits |
| 📚 Circuit Library | Searchable community circuits |
| 🐍 Python API | Clean method chaining, Qiskit-compatible |
| 💪 Dual Backends | Kronecker (readable) + Tensor (scales to 20+ qubits) |
| 📤 Code Export | Export as Qiskit `.py`, OpenQASM 2.0/3.0, Cirq, or Quil — run on IBM Quantum, Cirq, Braket, Rigetti |
| ✅ Tested | 124 passing tests, Qiskit-compatible output |

**Jump straight to:**
- **[→ Full documentation](2026-05-circuit-simulator/qcsim/README.md)** — API, TUI guide, architecture
- **[→ Add a gate](2026-05-circuit-simulator/qcsim/docs/adding-gates.md)** — Contribute new gates
- **[→ Submit a circuit](2026-05-circuit-simulator/circuit-library/CONTRIBUTING-CIRCUITS.md)** — Add to library
- **[→ Circuit library](2026-05-circuit-simulator/circuit-library/README.md)** — Browse community circuits
- **[→ Challenge description](2026-05-circuit-simulator/README.md)** — What to build + feature ideas

---

### July 2026 — Quantum Algorithm Visualizer

Step through a quantum algorithm one gate at a time and watch the state vector evolve — instead of only seeing the final answer. Built on top of `qcsim` (imports it as a library), terminal-only.

**Try it now:**
```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-06-algorithm-visualizer/qviz
pip install -e ../../2026-05-circuit-simulator/qcsim   # install qcsim first
pip install -e . && qviz-step
```

**Already have the repo (or an older qcsim)?** Pull and refresh both
editable installs:
```bash
cd Quantum-Collective-Monthly-Projects && git pull origin main
cd 2026-06-algorithm-visualizer/qviz
pip install -e ../../2026-05-circuit-simulator/qcsim   # refresh qcsim
pip install -e .                                        # refresh qviz
```
> `git pull` alone picks up source edits (both packages install with `-e`);
> re-run the installs if entry points or dependencies changed. If
> `qviz-step` isn't found afterward, re-run `pip install -e .`.

**What's inside:**
| Feature | Description |
|---------|-------------|
| ⏯️ Step-through engine | Replay any circuit gate-by-gate, snapshot state at every step |
| 🧮 Core four algorithms | QFT, Grover, Deutsch-Jozsa, Bernstein-Vazirani — purpose-annotated per gate |
| 🧭 Phased walkthrough | Preparation → Oracle → Diffusion progress bar, windowed circuit, plain-English state reading |
| 🎯 Measurement + summary | Sampled measurement histogram, then measured-vs-expected success/fail verdict |
| ⌨️ Interactive CLI | Step/back/jump/autoplay, Beginner ↔ Advanced modes, menu loop |
| 🧩 Extensible by design | Clear contributor tiers (Beginner → Expert) — add algorithms, views, and more |
| ✅ Tested | 54 passing tests, including non-palindromic bitstring cases |

**Jump straight to:**
- **[→ Challenge description](2026-06-algorithm-visualizer/README.md)** — What to build + contribution tiers
- **[→ Package README](2026-06-algorithm-visualizer/qviz/README.md)** — Usage, API, quick start
- **[→ Documentation index](2026-06-algorithm-visualizer/qviz/docs/README.md)** — Architecture, Developer Guide, Roadmap, FAQ, and more
- **[→ Roadmap](2026-06-algorithm-visualizer/qviz/docs/Roadmap.md)** — Beginner → Expert contribution ideas

---

### August 2026 — Noisy Quantum Simulator

Take any circuit and see what it *actually* does on a real, imperfect quantum
device. Built on top of `qcsim` (imports it as a library), terminal-only. Where
qcsim gives a perfect Bell state, `qnoise` evolves it as a **density matrix**
and applies realistic hardware noise — showing the gap between ideal and real
that quantum error correction exists to close.

**Try it now:**
```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-08-noise-simulator/qnoise
pip install -e ../../2026-05-circuit-simulator/qcsim   # install qcsim first
pip install -e . && qnoise-run
```

**What's inside:**
| Feature | Description |
|---------|-------------|
| 🎛️ Density-matrix engine | Evolves ρ: `ρ→UρU†` per gate, `ρ→ΣKρK†` per noise channel |
| 🌫️ 5 noise channels | Depolarizing, amplitude damping (T1), phase damping (T2), bit-flip, phase-flip |
| 🏭 Hardware presets | `ibm_ish`, `ion_ish`, `light` + custom `NoiseModel` builder |
| 📉 Readout error | Classical measurement error, per-qubit rates |
| 📊 Ideal vs noisy | Side-by-side ASCII histograms + fidelity / trace distance / TVD |
| 🔬 Noise sweep | Fidelity-vs-rate decay curve, built into the CLI |
| ✅ Parity guarantee | With noise off, reproduces qcsim's exact result — 84 passing tests |

**Jump straight to:**
- **[→ Challenge description](2026-08-noise-simulator/README.md)** — what to build + minimum requirements
- **[→ Package README](2026-08-noise-simulator/qnoise/README.md)** — usage, API, quick start
- **[→ Documentation index](2026-08-noise-simulator/qnoise/docs/README.md)** — architecture, guides
- **[→ Roadmap](2026-08-noise-simulator/qnoise/docs/Roadmap.md)** — Beginner → Expert contribution ideas
- **[→ Add a noise channel](2026-08-noise-simulator/qnoise/docs/Channel-Development.md)** — easiest first contribution

---

## 📅 Challenges

| Month | Challenge | Status | Folder |
|-------|-----------|--------|--------|
| June 2026 | Quantum Circuit Simulator | ✅ Live | [`2026-05-circuit-simulator/`](2026-05-circuit-simulator/) |
| July 2026 | Quantum Algorithm Visualizer | ✅ Live | [`2026-06-algorithm-visualizer/`](2026-06-algorithm-visualizer/) |
| August 2026 | Noisy Quantum Simulator | ✅ Live | [`2026-08-noise-simulator/`](2026-08-noise-simulator/) |

---

## 🌟 About Quantum Collective

We're students, researchers, builders, and professionals learning quantum computing together through hands-on projects, not just theory.

**What we do:**
- 🛠️ Monthly coding challenges — ship real quantum tools
- 📚 Weekly sessions — Every Sunday, 4:00 PM IST (learning + member showcases)
- 🎤 Expert talks — quantum algorithms, hardware, applications
- 💬 Active community — Discord for code help, WhatsApp for updates

**Community values:** Inclusive · Collaborative · Hands-on · Supportive · Open

---

## 📖 How Challenges Work

| Week | What happens |
|------|-------------|
| Week 1 | Challenge released — read the README, ask questions in Discussions |
| Weeks 2–3 | Build in your own fork |
| Week 4 | Post in Discussions, get community feedback |

**To submit:** Fork → build → post in [Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions)  
No PRs to main repo needed. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📞 Help

| Need | Where |
|------|-------|
| Challenge questions | [GitHub Discussions → Q&A](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/q-a) |
| Code help | Discord `#code-help` |
| Submit your solution | [GitHub Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions) |
| Found a bug | [GitHub Issues](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/issues) |
| New here? | [docs/FAQ.md](docs/FAQ.md) |
| Learn quantum basics | [Qiskit Textbook](https://qiskit.org/learn/) (free) |

---

## 🏆 Recognition

Top submissions featured on LinkedIn, YouTube, and weekly session showcases.

---

## 📄 License

Apache-2.0 — Build freely, share openly.
