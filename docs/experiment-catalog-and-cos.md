# Course Outcomes & Experiment Catalog

Concept-wise course outcomes (COs) and experiments + sub-experiments for the lab,
following the existing pattern (Superposition = 4 sub-experiments, Entanglement = 4).
Designed to be NBA/NAAC-mappable: each CO carries a Bloom's level (BL). Each
sub-experiment lists Aim / What the student does / Expected observation /
Deliverable (what gets graded).

Bloom's: BL1 Remember, BL2 Understand, BL3 Apply, BL4 Analyse, BL5 Evaluate, BL6 Create.

Suggested module order: 1 Foundations -> 2 Superposition -> 3 Entanglement ->
4 Gates & Circuits -> 5 Algorithms -> 6 Communication -> 7 Cryptography ->
8 Noise & NISQ -> 9 Error Correction.

---

## Module 1 — Foundations (qubit, Bloch sphere, measurement)

**COs**
- CO1.1 (BL2): Explain a qubit state as a vector and its Bloch-sphere picture.
- CO1.2 (BL3): Prepare basis and superposition states and predict measurement
  statistics.

**Experiments**
1. **Single-qubit states** — Aim: represent |0>, |1>, |+>, |->. Do: set states,
   view amplitudes + Bloch vector. Observe: mapping of amplitudes to the sphere.
   Deliverable: table of 4 states with their Bloch coordinates.
2. **Measurement in the computational basis** — Aim: see probabilistic collapse.
   Do: measure |+> repeatedly (many shots). Observe: ~50/50 outcomes converging.
   Deliverable: histogram + explanation of shot count vs stability.
3. **Basis change** — Aim: measure in the X basis. Do: apply H then measure |0>.
   Observe: deterministic vs random by basis. Deliverable: compare Z-basis vs
   X-basis outcomes for the same state.
4. **Global vs relative phase** — Aim: distinguish what is observable. Do: add a
   global phase, then a relative phase; measure. Observe: global phase invisible,
   relative phase changes interference. Deliverable: short note with evidence.

---

## Module 2 — Superposition (existing: 4 sub-experiments)

**COs**
- CO2.1 (BL2): Explain superposition and interference.
- CO2.2 (BL3): Build circuits that create and manipulate superposition.

**Experiments**
1. **Create superposition** — H on |0>; verify equal amplitudes. Deliverable:
   circuit + measured histogram.
2. **Interference** — H, phase, H; show constructive/destructive interference.
   Deliverable: vary the phase, plot outcome probability.
3. **Multi-qubit superposition** — H on each of n qubits; 2^n equal outcomes.
   Deliverable: n=2 and n=3 histograms.
4. **Superposition to computation** — set up a simple phase-kickback demo as a
   bridge to algorithms. Deliverable: explain how phase encodes information.

---

## Module 3 — Entanglement (existing: 4 sub-experiments)

**COs**
- CO3.1 (BL2): Explain entanglement and correlation vs classical.
- CO3.2 (BL4): Analyse Bell states and non-local correlations.

**Experiments**
1. **Create a Bell pair** — H + CNOT; show correlated outcomes. Deliverable:
   circuit + correlated histogram.
2. **The four Bell states** — prepare all four; distinguish them. Deliverable:
   table of the 4 states + preparation circuits.
3. **Correlation test** — measure both qubits in same/different bases; observe
   correlation change. Deliverable: correlation vs basis-angle table.
4. **CHSH / Bell inequality** — measure the CHSH value; observe it exceeding the
   classical bound. Deliverable: computed S value + interpretation.

---

## Module 4 — Gates & Circuits (Circuit Simulator + Circuit Doctor)

**COs**
- CO4.1 (BL3): Construct circuits from single- and multi-qubit gates.
- CO4.2 (BL4): Debug a faulty circuit and reason about gate identities.

**Experiments**
1. **Single-qubit gate zoo** — X, Y, Z, H, S, T; track Bloch motion. Deliverable:
   effect table for each gate on |0> and |+>.
2. **Controlled gates & universality** — CNOT, CZ, Toffoli; build a small target
   function. Deliverable: truth table verified by simulation.
3. **Gate identities** — show HXH = Z, two CNOTs = swap-like effects, etc.
   Deliverable: prove 3 identities with before/after states.
4. **Break-and-fix (Circuit Doctor)** — take a broken circuit, use the plain-English
   Circuit Doctor, repair it. Deliverable: diagnosis + corrected circuit.

---

## Module 5 — Algorithms (Algorithm Visualiser)

**COs**
- CO5.1 (BL3): Implement canonical quantum algorithms.
- CO5.2 (BL4): Analyse where and why quantum advantage appears.

**Experiments**
1. **Deutsch-Jozsa** — constant vs balanced oracle in one query. Deliverable:
   run both oracles; explain the single-query result.
2. **Grover's search** — amplitude amplification; optimal iteration count.
   Deliverable: success probability vs iterations plot; find the optimum.
3. **Quantum Fourier Transform / phase estimation** — estimate an eigenphase.
   Deliverable: estimated vs true phase, effect of qubit count on precision.
4. **Shor (small N)** — period-finding for a small factoring case. Deliverable:
   recovered period + factors, with the classical-vs-quantum step comparison.

---

## Module 6 — Quantum Communication

**COs**
- CO6.1 (BL3): Implement teleportation and superdense coding.
- CO6.2 (BL4): Compare direct vs repeater-based transmission.

**Experiments**
1. **Teleportation** — teleport an arbitrary state using a Bell pair + classical
   bits. Deliverable: input vs output state fidelity (~1) and the protocol steps.
2. **Superdense coding** — send 2 classical bits via 1 qubit + shared entanglement.
   Deliverable: all 4 messages recovered correctly.
3. **Direct vs repeater** — simulate loss over distance with and without a repeater.
   Deliverable: fidelity/success vs distance for both.
4. **Entanglement swapping** — connect two independent pairs. Deliverable: show the
   end nodes become entangled without direct interaction.

---

## Module 7 — Quantum Cryptography

**COs**
- CO7.1 (BL3): Execute BB84 key exchange.
- CO7.2 (BL5): Evaluate security by introducing an eavesdropper.

**Experiments**
1. **BB84 key exchange** — Alice/Bob random bases; sift a shared key. Deliverable:
   sifted key + sift-rate explanation.
2. **Eavesdropper (intercept-resend)** — insert Eve; observe error rate rise.
   Deliverable: QBER with and without Eve; the abort threshold.
3. **Error estimation & abort** — show the protocol aborting when QBER is too high.
   Deliverable: decision rule + a run that aborts.
4. **Compare with a classical channel** — contrast detectability of eavesdropping.
   Deliverable: short evaluation: why quantum detects, classical does not.

---

## Module 8 — Noise & NISQ

**COs**
- CO8.1 (BL3): Model noise channels on circuits.
- CO8.2 (BL4): Benchmark and predict noisy behaviour.

**Experiments**
1. **Noise channels** — apply bit-flip, phase-flip, depolarizing; see state decay.
   Deliverable: fidelity vs noise strength for each channel.
2. **Noisy Bell pair** — measure correlation loss under noise. Deliverable: CHSH/
   correlation degradation curve.
3. **Benchmark a circuit** — run a clean vs noisy algorithm (e.g. Grover).
   Deliverable: success probability clean vs noisy.
4. **Predict & mitigate** — vary depth; predict where noise dominates; try a simple
   mitigation. Deliverable: depth-vs-fidelity plot + mitigation effect.

---

## Module 9 — Error Correction

**COs**
- CO9.1 (BL3): Encode/decode with a basic quantum code.
- CO9.2 (BL5): Evaluate the error-correction threshold.

**Experiments**
1. **3-qubit bit-flip code** — encode, inject a bit-flip, detect via syndrome,
   correct. Deliverable: recovered state + syndrome table.
2. **3-qubit phase-flip code** — same in the phase basis. Deliverable: recovered
   state + explanation of the basis change.
3. **Shor 9-qubit code (or Steane)** — protect against arbitrary single-qubit
   error. Deliverable: demonstrate correction of a combined error.
4. **Threshold behaviour** — vary physical error rate; find where correction helps
   vs hurts. Deliverable: logical vs physical error-rate curve; identify threshold.

---

## Notes for building this into the software

- Each sub-experiment should map to a gradable assignment template (auto-graded
  where possible; teacher-approved gate as in the platform plan).
- Deliverables are the graded artifacts — they feed the signed lab report and the
  per-concept mastery rollup.
- COs are written for NBA/NAAC mapping; colleges can renumber to their scheme.
- Difficulty rises across modules 1 -> 9; modules 1-5 are self-sufficient for a
  first-semester elective, 6-9 for an advanced/second semester.
