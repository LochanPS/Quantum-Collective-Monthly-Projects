# qnoise — Build Roadmap (execution plan)

Internal working doc. Ordered phases. Each phase = independently testable.
Build the reference `qnoise` package that depends on `qcsim` as a library.

**Guiding constraints (match the repo's existing two projects):**
- Pure Python + NumPy only. `dependencies = ["numpy>=1.24"]`, `qcsim` as path dep.
- Terminal-only. Reuse qcsim's `draw_histogram` ASCII style.
- LSB / Qiskit-compatible qubit convention (qubit 0 = rightmost bit) — identical to qcsim.
- Consume qcsim's gate log `qc._log : List[(name, qubit_list, params_dict)]`.
- Every phase ships with tests. Target parity with prior projects (qcsim 124, qviz 54).

---

## Core architecture (decide once, up front)

```
qcsim.QuantumCircuit  ──(._log gate list)──►  qnoise engine
                                                   │
              ┌────────────────────────────────────┤
              ▼                                      ▼
      DensityMatrix ρ (2^N×2^N)              NoiseModel (channels attached
      ρ → UρU†  per gate                      per gate-name / per-qubit)
              │                                      │
              └──────────► after each gate: ρ → Σ Kρ K†  ◄─┘
                                   │
                     ┌─────────────┼──────────────┐
                     ▼             ▼              ▼
              sample outcomes   metrics vs     side-by-side
              (diag ρ +         ideal ρ_pure   ideal/noisy
              readout error)    (fidelity,     histogram
                                trace dist)
```

**Key type:** `DensityMatrix` wraps a `(2^N, 2^N)` complex ndarray `rho`.
**Key protocol:** a `NoiseChannel` exposes `kraus(qubit, num_qubits) -> list[np.ndarray]`
returning full-system 2^N×2^N Kraus operators (or single-qubit 2×2 that the
engine embeds — decide in Phase 3; single-qubit + embed is simpler for contributors).

---

## Phase 0 — Scaffold
- [ ] `2026-08-noise-simulator/qnoise/` package dir, mirror qviz layout.
- [ ] `pyproject.toml`: name `qnoise`, `numpy>=1.24`, dev extras `pytest`,
      script `qnoise-run = "qnoise.cli:main"`. Path-depend on qcsim (or document
      `pip install -e ../../2026-05-circuit-simulator/qcsim` first, like qviz).
- [ ] `qnoise/__init__.py` exporting the public surface (fill in as built).
- [ ] `tests/` dir + `conftest` if needed.
- [ ] Confirm `import qcsim` works from inside the package (smoke test).
**Done when:** `pip install -e .` succeeds and `import qnoise` works.

## Phase 1 — Density matrix core (`qnoise/density.py`)
- [ ] `DensityMatrix(num_qubits)` → `rho = |0…0><0…0|`.
- [ ] `.from_statevector(psi)` → `outer(psi, conj(psi))`.
- [ ] `.probabilities()` → `real(diag(rho))`; `.probabilities_dict(threshold)`
      keyed by LSB bitstring (copy qcsim's `label()` logic).
- [ ] `.trace()`, `.is_valid()` (Hermitian + trace≈1 + PSD eigenvalues ≥ -tol).
- [ ] `.purity()` = `trace(rho @ rho)` (1.0 pure, <1 mixed) — teaching handle.
- [ ] `.apply_unitary(U)` → `rho = U @ rho @ U.conj().T`.
**Tests:** `|0><0|` init; from_statevector round-trips qcsim probs; purity of Bell=1.

## Phase 2 — Gate application from qcsim log (`qnoise/engine.py` part 1)
- [ ] Reuse gate matrices from `qcsim.gates` (do NOT re-derive). Build a
      name→matrix / name→builder map covering qcsim's `_log` names
      (H,X,Y,Z,S,Sdg,T,Tdg,SX,SXdg,Rx,Ry,Rz,P,U,CNOT,CY,CZ,SWAP,CP,CCX,I,
      BARRIER,RESET,MEASURE).
- [ ] Embed single-qubit gate on target qubit into full 2^N unitary — reuse
      qcsim's expansion helpers (`_expand_single`/`_expand_controlled` logic) or
      mirror them. Handle controlled/multi-qubit via qcsim's own expanders.
- [ ] `run_ideal(qc) -> DensityMatrix`: replay log, `ρ→UρU†` each gate, no noise.
- [ ] BARRIER = no-op; RESET/MEASURE handled in Phase 6.
**Tests:** `run_ideal` diagonal matches `qc.probabilities()` for Bell, GHZ,
Grover — bit-for-bit. **This is Minimum Requirement #5 (noise-off parity).**

## Phase 3 — Noise channels (`qnoise/channels.py`)
Decide: contributor-facing channels return **single-qubit 2×2 Kraus ops**;
engine embeds them per target qubit (simplest to extend). Two-qubit channels
return 4×4.
- [ ] `NoiseChannel` base / protocol: `.kraus() -> list[np.ndarray]`, `.name`.
      Enforce completeness `Σ Kₖ† Kₖ = I` in a validator (test helper).
- [ ] Launch channels, each with correct Kraus operators:
  - [ ] `Depolarizing(p)` — {√(1-3p/4)I, √(p/4)X, √(p/4)Y, √(p/4)Z} (or p·I/2 form; pick one, document)
  - [ ] `AmplitudeDamping(gamma)` (T1) — {[[1,0],[0,√(1-γ)]], [[0,√γ],[0,0]]}
  - [ ] `PhaseDamping(gamma)` (T2) — {[[1,0],[0,√(1-γ)]], [[0,0],[0,√γ]]}
  - [ ] `BitFlip(p)` — {√(1-p)I, √p X}
  - [ ] `PhaseFlip(p)` — {√(1-p)I, √p Z}
- [ ] `apply_channel(rho, kraus_ops_full)` → `Σ K ρ K†`; verify trace preserved.
**Tests:** each channel preserves trace; completeness relation holds;
depolarizing with p=1 on |0> → maximally mixed I/2; amplitude damping γ=1 → |0>.

## Phase 4 — NoiseModel (`qnoise/model.py`)
- [ ] `NoiseModel`: map gate-name → list of channels, and/or qubit → channels.
      API sketch: `nm.add_channel(Depolarizing(0.01), gates=["H","X",...])`,
      `nm.add_readout_error(p0given1, p1given0)` (used in Phase 6).
- [ ] Distinguish 1-qubit vs 2-qubit gate noise (apply to each involved qubit,
      or a 2-qubit channel for CNOT etc.).
- [ ] `presets.py`: `ideal()`, `light()`, `ibm_ish()`, `ion_ish()` returning
      ready-made `NoiseModel`s. (Contributor tier: add presets.)
**Tests:** model returns right channels per gate; ideal preset = no channels.

## Phase 5 — Noisy engine loop (`qnoise/engine.py` part 2)
- [ ] `run(qc, noise_model) -> DensityMatrix`: for each log entry →
      apply gate unitary → look up channels for that gate/qubits → apply Kraus
      after the gate. BARRIER flushes nothing (no-op) but keep as extension hook.
- [ ] Assert `rho.is_valid()` at end (debug flag).
**Tests:** noise-off model reproduces Phase 2 ideal; small depolarizing on Bell
gives the 4-outcome spread with F<1; result independent of qcsim backend choice.

## Phase 6 — Measurement + readout error (`qnoise/measure.py`)
- [ ] `sample(rho, shots, readout_error=None) -> dict[str,int]`: sample from
      `diag(rho)`; if readout error set, flip sampled bits per p(0|1)/p(1|0).
- [ ] RESET on density matrix: partial-trace-and-reinit the qubit (or Kraus
      form of reset). MEASURE-in-log: treat as sampling point (document
      non-collapsing behavior, matching qcsim's choice).
**Tests:** zero readout error → sampling matches diag; readout error alone
distorts a perfect distribution predictably; large-shot histogram → probabilities.

## Phase 7 — Metrics (`qnoise/metrics.py`)
- [ ] `fidelity(rho, sigma)` — state fidelity; fast path when one is pure
      (`<ψ|ρ|ψ>`). General Uhlmann form for mixed-mixed.
- [ ] `trace_distance(rho, sigma)` = ½·Σ|eigenvalues(rho-sigma)|.
- [ ] `tvd(dist_a, dist_b)` — total-variation distance of two prob dicts.
**Tests:** F(ρ,ρ)=1, F=1 iff identical; trace_distance orthogonal states=1;
tvd symmetric, 0 for identical.

## Phase 8 — Rendering (`qnoise/render.py`)
- [ ] Reuse `qcsim.visualize.draw_histogram` for each side.
- [ ] `compare(ideal_dist, noisy_dist)` → side-by-side ASCII bars (the README
      mock-up) + a metrics footer line (fidelity, trace distance).
- [ ] Purity / "how mixed" one-line readout for teaching.
**Tests:** snapshot/text-contains tests (mirror qviz render tests).

## Phase 9 — CLI (`qnoise/cli.py`, entry `qnoise-run`)
- [ ] Menu loop (match qviz-step UX): pick a demo circuit (Bell, GHZ, Grover —
      import qviz algorithms if convenient, else build inline), pick a noise
      preset or set a rate, choose shots.
- [ ] Print ideal-vs-noisy comparison + metrics. Beginner↔Advanced verbosity
      toggle like qviz.
- [ ] Optional: `--sweep` flag → fidelity-vs-rate table (Phase "Go Deeper" idea,
      nice as a built-in demo).
**Done when:** `qnoise-run` produces the README's side-by-side output live.

## Phase 10 — Test sweep + CI parity
- [ ] Full `pytest` green. Aim ≥ ~50 tests (repo norm).
- [ ] Property tests: random circuits, noise-off ⇒ matches qcsim; any model ⇒
      `rho` stays valid; trace always 1±tol.
- [ ] Edge cases: 1 qubit, single gate, RESET mid-circuit, non-palindromic
      bitstrings (qviz-style rigor).

## Phase 11 — Docs (`qnoise/docs/`, mirror qviz docs set)
- [ ] `docs/README.md` (index), `Architecture.md`, `Channel-Development.md`
      (how to add a channel — the headline contributor path), `API-Reference.md`,
      `Contributing.md`, `Roadmap.md` (Beginner→Expert), `FAQ.md`.
- [ ] Package `README.md` (usage + quick start, qviz style).
- [ ] Update root `README.md` challenge table + "What's Live Now" section and
      `CHANGELOG.md` when it goes live.

---

## Suggested build order for the first working slice (vertical demo fast)
1. Phase 0 scaffold
2. Phase 1 DensityMatrix
3. Phase 2 ideal replay (prove noise-off parity with qcsim — the credibility test)
4. Phase 3 just `Depolarizing`
5. Phase 5 minimal loop + Phase 6 sampling
6. Phase 8 compare render → **first end-to-end "Bell noisy vs ideal" screenshot**
Then widen: remaining channels (3), NoiseModel/presets (4), metrics (7), CLI (9),
tests (10), docs (11).

## Open decisions to confirm before coding
- [ ] Folder/title month: using `2026-08` / "August 2026" (repo's own labeling is
      off by one — May folder=2026-05 but June folder=2026-06 titled "July").
      **Confirm with maintainer.**
- [ ] Kraus embedding: single-qubit 2×2 + engine-embed (contributor-friendly) vs
      full 2^N ops. Recommend single-qubit + embed.
- [ ] Max qubits: density matrix is O(4^N) — cap ~8–10 qubits, document clearly
      (trajectory backend is the Advanced escape hatch).
- [ ] Depolarizing convention (Kraus-4 vs mixture form) — pick, document once.
