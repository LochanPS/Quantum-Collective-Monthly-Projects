# Changelog

All notable changes to this project are documented here.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

---

## [0.2.0] — 2026-06-01

### Added
- Interactive terminal circuit builder (`qcsim-interactive`)
  - Arrow key navigation, gate placement, CNOT two-step cursor
  - Live info panel: depth, gate count, T-gates, entanglement
  - Gate help overlay (`?` key): matrix + plain-English explanation
  - Pattern recognition banner after Run (Bell, GHZ, etc.)
  - Export/import circuits as JSON
  - `--load <file>` flag to pre-load circuits on launch
- Tensor backend (`backend="tensor"`) — O(2^N) per gate, no matrix built
- `qcsim-search` CLI — search circuit library by name/tags/difficulty/category
- Community circuit library (`circuit-library/`)
  - `add_circuit.py` — submit circuits with fingerprint dedup
  - `search.py` — filter by name, tags, qubits, difficulty, category, verified
  - `check_duplicates.py` — CI gate, blocks duplicate PRs
  - `tags.json` — 22 canonical tags
  - `known_patterns.json` — fingerprints of reference circuits
  - Bell State and GHZ (3q) as seed circuits
- `qcsim/analyzer.py` — `CircuitAnalyzer`: depth, T-count, entanglement, qubit utilization
- `qcsim/fingerprint.py` — normalized fingerprinting (empty col compression, angle rounding, Jaccard similarity)
- `qcsim/patterns.py` — fingerprint + structural pattern recognition
- `docs/adding-gates.md` — 10-step gate contribution guide
- `circuit-library/CONTRIBUTING-CIRCUITS.md` — circuit submission guide
- SSH accessibility: SIGWINCH resize handler, 80×24 minimum size check
- Root `.gitignore` covering all Python artifacts

### Changed
- Renamed `2026-05-circuit-simulator/reference/` → `qcsim/` (clearer name)
- Moved `circuit-library/` from repo root → `2026-05-circuit-simulator/circuit-library/`
- CI rewritten: now runs tests on Python 3.9 + 3.11, lint scoped to source dirs only
- All READMEs updated: main repo, qcsim, circuit library
- PR template and issue templates updated for gate/circuit contributions

### Fixed
- Recursion bug in `_gate_swap` (was calling itself instead of `_expand_swap`)
- Unicode encoding error on Windows in `visualize.py` (ASCII fallback)
- `pyproject.toml` invalid build backend (`legacy:build` → `setuptools.build_meta`)
- Deutsch-Jozsa test assertion (incorrect expected state)

---

## [0.1.0] — 2026-05-24

### Added
- `QuantumState` — 2^N complex128 state vector, LSB qubit convention (Qiskit-compatible)
- `QuantumCircuit` — main simulation engine with Kronecker expansion
  - 25+ gates: H, X, Y, Z, S, Sdg, T, Tdg, SX, Rx, Ry, Rz, P, U, CNOT, CY, CZ, SWAP, CP, Toffoli
  - Method chaining API
  - `statevector()`, `probabilities()`, `measure_all(shots)`, `expectation_value(O)`
  - `compose()`, `barrier()`, `reset()`
- ASCII circuit visualization (`draw_circuit`, `draw_statevector`, `draw_histogram`)
- 52 passing tests (core correctness + Qiskit comparison)
- Examples: Bell state, GHZ, Deutsch-Jozsa, Grover
- `pyproject.toml` with optional dev/qiskit dependencies
