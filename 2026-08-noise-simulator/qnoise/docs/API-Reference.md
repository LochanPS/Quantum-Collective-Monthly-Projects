# API Reference

All symbols below are importable from the top-level `qnoise` package.

## DensityMatrix (`qnoise.density`)

The state of a (possibly mixed) N-qubit system.

| Member | Description |
|--------|-------------|
| `DensityMatrix(num_qubits)` | Initialise to `|0…0><0…0|`. |
| `.from_statevector(psi)` *(classmethod)* | Build a pure `rho = |psi><psi|`. |
| `.from_matrix(rho)` *(classmethod)* | Wrap an existing 2^N×2^N matrix. |
| `.matrix()` | Copy of the underlying `rho`. |
| `.set(rho)` | Overwrite `rho` (used by the engine). |
| `.probabilities()` | `real(diag(rho))` — per-basis-state probability array. |
| `.probabilities_dict(threshold=1e-10)` | Non-negligible probs keyed by bitstring (LSB). |
| `.trace()` | `Tr(rho)` — should be 1.0. |
| `.purity()` | `Tr(rho²)` — 1.0 pure, `1/2^N` maximally mixed. |
| `.is_valid(tol=1e-9)` | Hermitian **and** unit trace **and** positive semidefinite. |
| `.apply_unitary(U)` | In place `rho -> U rho U†`. |
| `.label(index)` | Index → LSB bitstring (matches qcsim). |

## Engine (`qnoise.engine`)

| Function | Description |
|----------|-------------|
| `run(qc, noise_model=None)` | Replay `qc` onto `rho`, applying noise after each gate. `None`/ideal → noiseless. Returns `DensityMatrix`. |
| `run_ideal(qc)` | Noiseless replay. Its diagonal matches `qc.probabilities()` exactly. |
| `gate_unitary(name, qubits, params, num_qubits)` | Full 2^N×2^N unitary for one logged gate (via qcsim). |
| `embed_single(op, qubit, num_qubits)` | Embed a 2×2 operator on `qubit` (LSB convention). |
| `apply_channel(dm, channel, qubit)` | In place `rho -> Σ K rho K†` for a single-qubit channel. |

## Channels (`qnoise.channels`)

All are single-qubit; `.kraus()` returns a list of 2×2 arrays.

| Class | Parameter | Meaning |
|-------|-----------|---------|
| `Depolarizing(p)` | `p ∈ [0,1]` | With prob `p`, replace with a random state. `p=1` → maximally mixed. |
| `BitFlip(p)` | `p` | Apply X with probability `p`. |
| `PhaseFlip(p)` | `p` | Apply Z with probability `p`. |
| `AmplitudeDamping(gamma)` | `γ` | T1 energy decay `|1> -> |0>`. |
| `PhaseDamping(gamma)` | `γ` | T2 dephasing (phase loss, no energy loss). |
| `NoiseChannel` | — | Base class. Implement `.kraus()`. `.is_trace_preserving()` checks completeness. |

## NoiseModel & presets (`qnoise.model`, exposed as `qnoise.presets`)

| Member | Description |
|--------|-------------|
| `NoiseModel()` | Empty model. |
| `.add_channel(channel, gates=None)` | Attach a channel to given gate names (default: all). Chainable. |
| `.add_readout_error(p1_given_0, p0_given_1)` | Attach classical readout error. Chainable. |
| `.channels_for(gate_name)` | Channels firing after a gate. |
| `.readout_error` | The attached `ReadoutError` or `None`. |
| `presets.ideal()` | No noise. |
| `presets.light()` | 1% depolarizing everywhere. |
| `presets.depolarizing(p, gates=None)` | Depolarizing at rate `p`. |
| `presets.ibm_ish()` | Superconducting-style: light 1-qubit, heavier 2-qubit, T1/T2, readout error. |
| `presets.ion_ish()` | Trapped-ion-style: very low error. |

> Preset rates are **illustrative**, not real device calibrations.

## Measurement (`qnoise.measure`)

| Member | Description |
|--------|-------------|
| `sample(dm, shots=1024, readout_error=None, seed=None)` | Draw shots from `diag(rho)`; returns bitstring→count. |
| `ReadoutError(p1_given_0=0.0, p0_given_1=0.0)` | Classical readout error; rates may be floats or `{qubit: rate}` dicts. |

## Metrics (`qnoise.metrics`)

| Function | Description |
|----------|-------------|
| `fidelity(rho, sigma)` | State fidelity in `[0,1]`; 1.0 iff identical. Pure-state fast path. |
| `trace_distance(rho, sigma)` | `½·Σ|eig(rho-sigma)|` in `[0,1]`. |
| `tvd(dist_a, dist_b)` | Total-variation distance of two probability dicts. |

## Rendering (`qnoise.render`)

| Function | Description |
|----------|-------------|
| `compare(ideal, noisy, width=18, threshold=1e-4)` | Side-by-side ASCII histograms. |
| `metrics_footer(fidelity, trace_distance, tvd)` | One-line metrics summary. |

## Demos (`qnoise.demos`)

`DEMOS` maps names to circuit builders: `bell`, `ghz3`, `ghz4`, `plus`,
`grover2`. Each returns a fresh `qcsim.QuantumCircuit`.

## CLI (`qnoise.cli`)

`qnoise-run` console script → `main()`. Testable helpers: `build_circuit(name)`,
`build_model(name, p=0.05)`, `run_report(qc, noise_model, shots, seed)`,
`sweep_report(qc, rates)`.
