# qnoise Documentation

Reference docs for the noisy quantum simulator.

## Start here
- **[Architecture](Architecture.md)** — how a circuit becomes a noisy density
  matrix, and the design decisions behind the engine.
- **[Channel Development](Channel-Development.md)** — the headline contributor
  task: add a new noise channel in ~15 lines.

## Reference
- **[API Reference](API-Reference.md)** — every public class and function.
- **[Roadmap](Roadmap.md)** — Beginner → Expert contribution ideas, organized by
  difficulty tier. **Pick something here to work on.**

## Process
- **[Contributing](Contributing.md)** — fork → build → submit workflow.
- **[FAQ](FAQ.md)** — common questions.

## The 60-second mental model

qcsim uses a **state vector** (pure states only). Noise produces **mixed
states**, so qnoise uses a **density matrix** `rho`. Two rules run everything:

- Apply a gate: `rho -> U rho U†`
- Apply noise: `rho -> Σₖ Kₖ rho Kₖ†` (Kraus operators)

The engine replays a qcsim circuit's gate log, applying the first rule for each
gate and the second rule for each noise channel attached to that gate.
