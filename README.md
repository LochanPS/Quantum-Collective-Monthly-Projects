# Quantum Collective — Monthly Projects

Monthly collaborative coding challenges from **Quantum Collective** — a 600+ member quantum computing community based in Bangalore, India.

Build real quantum tools. Learn by shipping.

**[Discord](https://discord.gg/QW3yUpNd) · [WhatsApp](https://chat.whatsapp.com/KK2cx4st54uJONp0f8BWdS) · [LinkedIn](https://www.linkedin.com/company/113013769/) · [YouTube](https://www.youtube.com/@QuantumCollectiveIndia)**

---

## 📁 Repository Structure

```
Quantum-Collective-Monthly-Projects/
│
├── 2026-05-circuit-simulator/               ← May 2026: Quantum Circuit Simulator (LIVE)
│   ├── qcsim/                               ← Full reference implementation
│   │   ├── qcsim/                          ← Core simulator source code
│   │   ├── examples/                       ← Runnable examples (Bell, GHZ, Grover, etc.)
│   │   ├── tests/                          ← 52 tests
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
├── 2026-06-algorithm-visualizer/            ← June 2026: Coming soon
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

### May 2026 — Quantum Circuit Simulator

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
| 🎮 Interactive TUI | Build circuits visually — no coding needed |
| 🔗 25+ Gates | H, X, CNOT, SWAP, Rx, Ry, Rz, Toffoli and more |
| 📊 Live Metrics | Depth, gate count, T-gate cost, entanglement |
| 🔍 Pattern Recognition | Recognizes Bell state, GHZ, and other known circuits |
| 📚 Circuit Library | Searchable community circuits |
| 🐍 Python API | Clean method chaining, Qiskit-compatible |
| 💪 Dual Backends | Kronecker (readable) + Tensor (scales to 20+ qubits) |
| ✅ Tested | 52 passing tests, Qiskit-compatible output |

**Jump straight to:**
- **[→ Full documentation](2026-05-circuit-simulator/qcsim/README.md)** — API, TUI guide, architecture
- **[→ Add a gate](2026-05-circuit-simulator/qcsim/docs/adding-gates.md)** — Contribute new gates
- **[→ Submit a circuit](2026-05-circuit-simulator/circuit-library/CONTRIBUTING-CIRCUITS.md)** — Add to library
- **[→ Circuit library](2026-05-circuit-simulator/circuit-library/README.md)** — Browse community circuits
- **[→ Challenge description](2026-05-circuit-simulator/README.md)** — What to build + feature ideas

---

## 📅 Challenges

| Month | Challenge | Status | Folder |
|-------|-----------|--------|--------|
| May 2026 | Quantum Circuit Simulator | ✅ Live | [`2026-05-circuit-simulator/`](2026-05-circuit-simulator/) |
| June 2026 | Algorithm Visualizer | 🔜 Coming soon | [`2026-06-algorithm-visualizer/`](2026-06-algorithm-visualizer/) |

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
