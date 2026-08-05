# Contributing to qnoise

## Setup

```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-08-noise-simulator/qnoise
pip install -e ../../2026-05-circuit-simulator/qcsim   # qcsim first
pip install -e ".[dev]"                                # qnoise + pytest
pytest                                                 # should be all green
```

## Workflow

1. **Pick something** from the [Roadmap](Roadmap.md). Post in
   [Discussions → Q&A](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/q-a)
   so two people don't build the same thing.
2. **Build in your fork**, with tests.
3. **Submit** by posting in
   [Discussions → Submissions](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/discussions/categories/submissions).
   You do **not** need to open a PR against the main repo.

## Ground rules that keep the engine trustworthy

- **Pure Python + NumPy.** The only runtime dependencies are `numpy` and
  `qcsim`. Don't add others to the core.
- **The parity guarantee is sacred.** With noise off, qnoise must reproduce
  qcsim's exact statevector result. If your change could affect evolution, keep
  `test_engine_ideal.py` and `test_properties.py` green.
- **Keep `rho` physical.** Any new channel or operation must leave `rho`
  Hermitian, unit-trace, and positive semidefinite. There's a helper:
  `DensityMatrix.is_valid()`. New channels should satisfy
  `channel.is_trace_preserving()`.
- **LSB convention everywhere.** Qubit 0 is the rightmost bit, matching qcsim.
- **Tests with every change.** Match the style already in `tests/`. Prefer a
  small, sharp assertion (a known channel on a known state → a known matrix).

## Adding a channel?

See the dedicated [Channel Development](Channel-Development.md) guide — it's the
easiest first contribution.

## Running a subset of tests

```bash
pytest tests/test_channels.py -v
pytest -k depolarizing
```

## Code style

Follow the surrounding code: docstrings on public functions, type hints, and the
same comment density as the existing modules. No formatter is enforced, but keep
lines readable (~90 cols).
