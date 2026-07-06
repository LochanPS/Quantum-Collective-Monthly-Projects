# qviz FAQ & Common Pitfalls

## Setup

**`qviz-step: command not found` after `git pull`.**
The console-script entry point is new in your checkout. Re-run
`pip install -e .` in `2026-06-algorithm-visualizer/qviz`.

**`ModuleNotFoundError: No module named 'qcsim'`.**
qcsim isn't on PyPI — install it from the sibling folder first:
`pip install -e ../../2026-05-circuit-simulator/qcsim`.

**Do I need to reinstall after editing source?**
No. Both packages install with `-e` (editable), so source edits are picked
up immediately. Reinstall only if entry points or dependencies changed.

## Output looks wrong

**Garbled boxes / `UnicodeEncodeError` in the terminal.**
Your terminal isn't UTF-8. qviz falls back to ASCII automatically via
`_can_unicode()`. If you hit an actual `UnicodeEncodeError`, a glyph was
printed without an ASCII fallback — that's a bug; see the fallback rules
in [Rendering-Guide.md](Rendering-Guide.md#unicode--ascii-fallback--respect-this).

**The bitstring in the state table looks reversed.**
qcsim labels states `q(n-1)...q0` — leftmost char is the highest qubit,
rightmost is qubit 0. This is Qiskit's convention. The `ancilla|input`
split and the measurement histogram all use this same descending order.

**My algorithm's labels attach to the wrong gates.**
`annotations` (and `phases`) must have exactly one entry per gate, in
`circuit._log` order. You probably applied a gate without appending its
annotation. Use the `add()` helper pattern from
[Algorithm-Development.md](Algorithm-Development.md).

## Behavior surprises

**`hide-zeros` seems to do nothing.**
There are no zero-probability states to hide in the current state (e.g. a
uniform superposition). qviz prints a note saying so — the toggle is still
working.

**Grover finds the "wrong" state for an asymmetric target.**
Classic label-orientation bug. A bitstring parameter must be reversed
(`param[::-1]`) before indexing onto qubits. See the Grover bug in
[Developer-Guide.md](Developer-Guide.md#the-grover-bug--read-before-writing-any-algorithm-with-a-bitstring-parameter),
and always test a non-palindromic case.

**QFT measurement says "uniform magnitudes" — is that right?**
Yes. The QFT of a basis state has equal-magnitude amplitudes; all the
information lives in the phases. Measuring gives every outcome roughly
equally — the inverse QFT reads the phases back.

## Contributing

**CI fails on formatting but my change is fine.**
Run `black qviz/ tests/ --line-length 100`. CI enforces Black across the
whole repo.

**Where does my feature's code go?**
Interpretation (what a state means) → `interpret.py`. Terminal formatting
→ `render.py`. Algorithm meaning → `algorithms/`. Menu/keys → `cli.py`.
See [Architecture.md](Architecture.md).

Can I add a matplotlib chart, desktop UI, or web view?

No. qviz is intentionally terminal-only. New visualization features should extend the terminal renderer while preserving ASCII compatibility. See Developer-Guide.md
## Still stuck?

Open a [GitHub issue](https://github.com/LochanPS/Quantum-Collective-Monthly-Projects/issues)
or ask in the community channels linked from the
[root README](../../../README.md).
