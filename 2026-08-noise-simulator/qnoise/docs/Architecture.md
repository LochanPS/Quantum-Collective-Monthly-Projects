# Architecture

How qnoise turns a qcsim circuit into a noisy result.

## Data flow

```
qcsim.QuantumCircuit
        │  (._log : list of (name, qubits, params))
        ▼
   engine.run(qc, noise_model)
        │
        │  for each gate in the log:
        │    1. U = gate_unitary(name, qubits, params, N)   # full 2^N unitary
        │    2. rho -> U rho U†                             # DensityMatrix.apply_unitary
        │    3. for each channel attached to this gate:
        │         for each qubit the gate touched:
        │           rho -> Σ K rho K†                       # engine.apply_channel
        ▼
   DensityMatrix (possibly mixed)
        │
        ├─ measure.sample(rho, shots, readout_error)  ->  counts
        └─ metrics.fidelity / trace_distance / tvd    vs  run_ideal(qc)
```

## Why a density matrix?

A pure state `|psi>` is one vector. Noise makes the true state a *probabilistic
mixture* of many vectors — for example "70% this state, 30% that one." No single
vector captures a mixture, but a **density matrix** `rho` does:

- Pure state: `rho = |psi><psi|`, and `Tr(rho²) = 1`.
- Mixed state: `rho = Σ pᵢ |ψᵢ><ψᵢ|`, and `Tr(rho²) < 1`.

The diagonal of `rho` is the measurement probability of each basis state — the
direct analogue of `|amplitude|²`. Cost: `rho` is 2^N × 2^N, so memory is
O(4^N). Practical ceiling is ~8–10 qubits; the Monte-Carlo trajectory backend on
the Roadmap is the escape hatch for going bigger.

## The two evolution rules

**Gates** are unitary, and act by conjugation: `rho -> U rho U†`. This preserves
purity — a pure state stays pure under gates alone.

**Noise channels** act through **Kraus operators** `{Kₖ}`:
`rho -> Σₖ Kₖ rho Kₖ†`. As long as `Σₖ Kₖ† Kₖ = I` (the completeness relation),
this keeps `rho` a valid density matrix (Hermitian, unit trace, positive
semidefinite). Channels are where purity drops — that's decoherence.

## Where each gate's unitary comes from

Rather than re-derive Kronecker/controlled-gate embedding, `engine.gate_unitary`
reads each gate's full 2^N × 2^N matrix straight out of qcsim: it applies the
gate to every basis state `|j>` and collects the resulting state vectors as the
columns of `U`. By construction this matches qcsim's gate action exactly — which
is what makes the **noise-off parity guarantee** hold: with no channels,
`run(qc, ideal)` reproduces qcsim's statevector result bit-for-bit. That parity
is enforced by tests (`test_engine_ideal.py`, `test_properties.py`).

Single-qubit Kraus operators are embedded on their target qubit with
`engine.embed_single`, using the same LSB convention as qcsim (qubit `k` sits at
Kronecker position `N-1-k`).

## Layering

- `density.py` knows nothing about gates or noise — just linear algebra on `rho`.
- `channels.py` are pure Kraus-operator definitions; they don't know about
  circuits.
- `engine.py` is the only module that touches qcsim internals (the gate log).
- `model.py` maps gate names → channels; `measure.py` and `metrics.py` are
  read-only consumers of a finished `rho`.

This keeps the headline contributor task — adding a channel — isolated to one
small, dependency-light file.
