# Quantum Collective — Monthly Projects

Monthly collaborative coding challenges from **Quantum Collective** — a 600+ member quantum computing community based in Bangalore, India.

Build real quantum tools. Learn by shipping.

---

## 🚀 What's Live Now

### **May 2026: Quantum Circuit Simulator (qcsim)**

Production-ready quantum circuit simulator + interactive terminal UI + community circuit library.

**Get started in 30 seconds:**
```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-05-circuit-simulator/reference
pip install -e .
qcsim-interactive  # Launch the circuit builder
```

**What you get:**
- 🎮 **Interactive TUI** — Build circuits visually with arrow keys + letter keys
- 📊 **Live Metrics** — Depth, gate count, T-gate cost, entanglement detection
- 🔍 **Pattern Recognition** — Identifies Bell, GHZ, and other known circuits
- 📚 **Circuit Library** — Community circuits, searchable by difficulty/algorithm
- 🔗 **25+ Gates** — H, X, CNOT, SWAP, Rx, Ry, Rz, Toffoli, etc.
- 🐍 **Clean Python API** — Method chaining, Qiskit-compatible qubit convention
- 💪 **2 Backends** — Kronecker (readable) + Tensor (scales to 20+ qubits)

**Links:**
- **[→ Full qcsim README](2026-05-circuit-simulator/reference/README.md)** — Complete guide to API, examples, TUI
- **[→ Add a Gate](2026-05-circuit-simulator/reference/docs/adding-gates.md)** — 10-step guide to contributing new gates
- **[→ Submit Circuits](circuit-library/CONTRIBUTING-CIRCUITS.md)** — Share your circuits in the community library
- **[→ Interactive Builder](2026-05-circuit-simulator/reference#interactive-tui)** — How to use qcsim-interactive
- **[→ Search Library](circuit-library/README.md)** — Browse & load community circuits

**52 tests, Qiskit-compatible, zero dependencies (NumPy only).**

---

## 📅 Upcoming Challenges

| Month | Challenge | Status |
|-------|-----------|--------|
| June 2026 | Algorithm Visualizer | *Design phase — details TBD* |

---

## 🌟 About Quantum Collective

We're students, researchers, builders, and professionals learning quantum computing together through hands-on projects, not just theory.

### What We Do

- 🛠️ **Monthly Projects** — Ship real quantum tools (this repo!)
- 📚 **Weekly Sessions** — Learning + member project spotlights (Sundays 4 PM IST)
- 🎤 **Expert Talks** — Quantum algorithms, hardware, applications
- 🚀 **Hackathons** — Large-scale quantum challenges (coming soon)
- 💬 **Active Community** — Discord for help, WhatsApp for updates

### Join Us

| Platform | Link | Purpose |
|----------|------|---------|
| 💬 WhatsApp | [Join Group](https://chat.whatsapp.com/KK2cx4st54uJONp0f8BWdS) | Announcements, updates |
| 💻 Discord | [Join Server](https://discord.gg/QW3yUpNd) | Code help, discussions, weekly sessions |
| 🔗 LinkedIn | [Quantum Collective India](https://www.linkedin.com/company/113013769/) | News, member showcases |
| 🎥 YouTube | [Quantum Collective India](https://www.youtube.com/@QuantumCollectiveIndia) | Recorded sessions |

**Weekly Meetings** — Every Sunday, 4:00 PM IST
- Part 1: Teaching session on quantum concepts
- Part 2: Member project showcases
- Link posted in Discord + WhatsApp

### Community Values

✅ **Inclusive** — All backgrounds and skill levels welcome  
✅ **Collaborative** — We build together, not compete  
✅ **Hands-on** — Learn by shipping real things  
✅ **Supportive** — Ask questions, help others, grow together  
✅ **Open** — No gatekeeping, quantum is for everyone

---

## 📖 How It Works

| Week | Activity |
|------|----------|
| Week 1 | Problem released — read the challenge README, ask questions in Discussions |
| Weeks 2–3 | Build your solution in your own fork |
| Week 4 | Post your submission in Discussions, get community feedback |

### Difficulty Tiers

- **Beginner** — core functionality, get something working
- **Intermediate** — performance, clean API, full feature set
- **Advanced** — optimization, novel extensions, research-level work

### How to Submit

1. Fork this repo
2. Build your solution in your fork
3. Open a **Discussion** in the [Submissions](../../discussions/categories/submissions) category
4. Include: your fork link, which tier, a 2–3 sentence description of your approach

No PRs needed. No merge conflicts. See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

---

## 📞 Help & Resources

| Need | Where |
|------|-------|
| Challenge questions | [GitHub Discussions / Q&A](../../discussions/categories/q-a) |
| Code help | Discord `#code-help` |
| Submit solution | [GitHub Discussions / Submissions](../../discussions/categories/submissions) |
| Bug report | [GitHub Issues](../../issues) |
| General FAQ | [docs/FAQ.md](docs/FAQ.md) |
| Quantum basics | [Qiskit Textbook](https://qiskit.org/learn/) |

---

## 🏆 Recognition

Top submissions each month featured on:
- LinkedIn & YouTube
- Weekly session showcases
- Community hall of fame *(coming soon)*

---

## 📁 Repository Structure

```
Quantum-Collective-Monthly-Projects/
├── 2026-05-circuit-simulator/           ← May 2026 Challenge (LIVE)
│   ├── reference/                       ← qcsim package (pip install -e .)
│   │   ├── qcsim/                      ← Core simulator
│   │   ├── examples/                   ← Example circuits (Bell, GHZ, Deutsch-Jozza, Grover)
│   │   ├── docs/adding-gates.md        ← How to add new gates
│   │   ├── tests/                      ← 52 tests (core + Qiskit comparison)
│   │   └── README.md                   ← Full qcsim guide
│   ├── EXAMPLES.md                     ← Expected API patterns
│   └── README.md                       ← May challenge description
│
├── 2026-06-algorithm-visualizer/        ← June 2026 Challenge (upcoming)
│
├── circuit-library/                     ← Community circuit library
│   ├── examples/                       ← Verified circuits (Bell, GHZ, etc.)
│   ├── search.py                       ← Search library by name/tags
│   ├── add_circuit.py                  ← Submit circuits with dedup check
│   ├── CONTRIBUTING-CIRCUITS.md        ← How to submit circuits
│   └── README.md                       ← Library overview
│
├── docs/
│   └── FAQ.md                          ← Frequently asked questions
│
├── CONTRIBUTING.md                     ← How to submit solutions
└── README.md                           ← This file
```

---

## 📄 License

Apache-2.0 — Build freely, share openly.

---

**Built with ❤️ by Quantum Collective** — *Learn • Build • Ship • Grow Together*
