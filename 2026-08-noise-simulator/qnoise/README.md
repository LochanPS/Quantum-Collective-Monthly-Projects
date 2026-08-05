# qnoise — Noisy Quantum Simulator

**Quantum Collective — Monthly Project #3 (August 2026)**

A density-matrix noise simulator built on top of
[qcsim](../../2026-05-circuit-simulator/qcsim/). Take any circuit built with
qcsim, evolve it as a **density matrix**, apply realistic hardware noise, and
see what the circuit *actually* does on an imperfect quantum device — side by
side with the ideal result.

```
Bell state — ideal vs depolarizing(p=0.05)

  ideal                         noisy
  00  █████████  50.0%          00  █████████  47.6%
  01             0.0%           01  ▏          2.4%
  10             0.0%           10  ▏          2.4%
  11  █████████  50.0%          11  █████████  47.6%

  fidelity vs ideal: 0.904   trace distance: 0.096   TVD: 0.049
  purity: ideal 1.000 -> noisy 0.821
```

---

## Install

qnoise depends on `qcsim`. Install qcsim first (editable), then qnoise:

```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-08-noise-simulator/qnoise
pip install -e ../../2026-05-circuit-simulator/qcsim   # install qcsim first
pip install -e . && qnoise-run
```

Already have the repo? Pull and refresh both editable installs:

```bash
cd Quantum-Collective-Monthly-Projects && git pull origin main
cd 2026-08-noise-simulator/qnoise
pip install -e ../../2026-05-circuit-simulator/qcsim
pip install -e .
```

---

## The one concept to learn

qcsim represents a state as a **state vector** — one clean list of amplitudes,
good for *pure* states only. A noisy state is a statistical *mixture* of many
possible state vectors, which no single vector can express. The tool for that is
a **density matrix** `rho` (a 2^N × 2^N matrix). Two rules run the whole engine:

| Operation | On a density matrix |
|-----------|---------------------|
| Apply a gate `U` | `rho -> U rho U†` |
| Apply noise | `rho -> Σₖ Kₖ rho Kₖ†`  (Kraus operators `{Kₖ}`) |

Everything else — every channel, every metric — is built on those two lines.

---

## Quick start (Python API)

```python
from qcsim import QuantumCircuit
from qnoise import run, run_ideal, presets, fidelity, sample

qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

ideal = run_ideal(qc)                     # pure DensityMatrix, matches qcsim
noisy = run(qc, presets.depolarizing(0.05))

print(noisy.probabilities_dict())         # noisy distribution
print("fidelity:", fidelity(ideal, noisy))
print(sample(noisy, shots=1024))          # sampled measurement counts
```

Build a custom noise model:

```python
from qnoise import NoiseModel, Depolarizing, AmplitudeDamping

nm = (NoiseModel()
      .add_channel(Depolarizing(0.001), gates=["H", "X", "Rx"])  # 1-qubit gates
      .add_channel(Depolarizing(0.01), gates=["CNOT", "CZ"])     # 2-qubit gates
      .add_channel(AmplitudeDamping(0.002))                      # T1 on all gates
      .add_readout_error(p1_given_0=0.01, p0_given_1=0.02))

noisy = run(qc, nm)
```

---

## What's inside

| Module | What it does |
|--------|--------------|
| `density.py` | `DensityMatrix` — ρ, probabilities, purity, validity checks |
| `engine.py` | Replay a qcsim circuit onto ρ; apply gates and Kraus channels |
| `channels.py` | Noise channels: depolarizing, T1, T2, bit-flip, phase-flip |
| `model.py` | `NoiseModel` — attach channels per gate; hardware-ish presets |
| `measure.py` | Sampling from ρ + classical readout error |
| `metrics.py` | Fidelity, trace distance, total-variation distance |
| `render.py` | Side-by-side ideal-vs-noisy ASCII histograms |
| `demos.py` | Demo circuits (Bell, GHZ, Grover, ...) |
| `cli.py` | `qnoise-run` interactive front end |

---

## Docs

- **[Documentation index](docs/README.md)** — start here
- **[Architecture](docs/Architecture.md)** — how the engine works, design decisions
- **[Channel Development](docs/Channel-Development.md)** — add a noise channel (the headline contributor path)
- **[API Reference](docs/API-Reference.md)** — every public function and class
- **[Roadmap](docs/Roadmap.md)** — Beginner → Expert contribution ideas, by tier
- **[Contributing](docs/Contributing.md)** — workflow and submission
- **[FAQ](docs/FAQ.md)**

---

## Tests

```bash
pip install -e ".[dev]"
pytest
```

84 passing tests, including a parity check that with **noise off**, qnoise
reproduces qcsim's exact statevector result.

---

## License

Apache-2.0.
