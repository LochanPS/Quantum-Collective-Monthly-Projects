# qviz Documentation

Everything beyond the quick-start lives here. Start with whichever row
matches what you're trying to do.

| I want to... | Read |
|---|---|
| Understand what qviz is and run it | [../README.md](../README.md) (package README) |
| See how the pieces fit together | [Architecture.md](Architecture.md) |
| Contribute code and not get stuck | [Developer-Guide.md](Developer-Guide.md) |
| Add a new quantum algorithm | [Algorithm-Development.md](Algorithm-Development.md) |
| Change how things are drawn in the terminal | [Rendering-Guide.md](Rendering-Guide.md) |
| Look up a function/class signature | [API-Reference.md](API-Reference.md) |
| Find something worth building | [Roadmap.md](Roadmap.md) |
| Follow the contribution workflow | [Contributing.md](Contributing.md) |
| Debug a common problem | [FAQ.md](FAQ.md) |

## Reading order for a new contributor

1. **[../README.md](../README.md)** — what qviz is, install, run it once.
2. **[Architecture.md](Architecture.md)** — the four layers and how data flows.
3. **[Developer-Guide.md](Developer-Guide.md)** — design decisions, pitfalls,
   the one bug you must know about before writing any algorithm.
4. **[Roadmap.md](Roadmap.md)** — pick a task at your level.
5. **[Algorithm-Development.md](Algorithm-Development.md)** or
   **[Rendering-Guide.md](Rendering-Guide.md)** — depending on what you picked.
6. **[Contributing.md](Contributing.md)** — how to submit it.

## Document map

- **Architecture.md** — modules, layers, the `Step` and `AlgorithmResult`
  data model, how the stepper/interpret/render/algorithms/cli layers connect.
- **Developer-Guide.md** — the full "continue building here" guide:
  business context (open-core split), per-module deep dive, the Grover
  label-orientation bug, setup, and what's done vs. left. (This is the
  former `HANDOFF.md`, now public.)
- **Contributing.md** — workflow, commit style, formatting (Black), tests,
  the update-your-checkout commands.
- **Algorithm-Development.md** — step-by-step guide to adding an algorithm
  module that returns an `AlgorithmResult`.
- **Rendering-Guide.md** — how the terminal UI is built, modes, phases,
  windowed circuit, and how to add a rendering feature without breaking
  the ASCII fallback.
- **API-Reference.md** — public functions and classes, per module.
- **Roadmap.md** — the big list: Beginner → Expert, grouped by theme.
- **FAQ.md** — common pitfalls and their fixes.
