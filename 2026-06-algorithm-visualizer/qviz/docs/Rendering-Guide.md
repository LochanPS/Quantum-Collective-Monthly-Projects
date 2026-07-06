# qviz Rendering Guide

How the terminal UI is built, and how to add to it without breaking the
ASCII fallback or the two-mode split. All rendering lives in `render.py`
(with helpers in `interpret.py` and `phases.py`).

## Unicode / ASCII fallback — respect this

`render.py` calls `_can_unicode()` once at import and picks glyphs
accordingly:

```python
_BLOCK = "█" if _U else "#"
_LIGHT = "░" if _U else "."
_PHASE = "∠" if _U else "phase "
```

**Every non-ASCII character you print must have an ASCII fallback gated on
`_U`.** A past bug: the `∠` phase symbol was printed unconditionally and
crashed with `UnicodeEncodeError` on Windows cp1252 terminals. If you add
a glyph, add its fallback. The CLI's clear-screen and ANSI color escapes
(`_BOLD`, `_DIM`, `_YELLOW`, `_RESET`) are assumed supported.

## The two modes are different layouts, not a flag

`render_step(..., mode=...)` branches on `"beginner"` vs `"advanced"` and
produces genuinely different output:

| | Beginner | Advanced |
|---|---|---|
| State table | `% chance` only | complex amplitudes + phase column |
| Circuit diagram | none (clutter) | windowed to current phase |
| Change highlight | no | yes (yellow, vs previous step) |
| Interpretation | "What this means:" | " State:" |

When you add a rendering feature, decide which mode(s) it belongs in.
Beginner should stay uncluttered — resist adding math there.

## Phase progress + windowed circuit

- `render_phase_progress(phases, step_index)` — one line showing the phase
  segments with the current one highlighted and finished ones ticked.
- `render_windowed_circuit(circuit, lo, hi)` — draws only the gates with
  step-index in `[lo, hi]`. The window is the current phase segment (from
  `phases.segments`). This keeps multi-iteration circuits from sprawling
  horizontally. The diagram is purely structural (the real state is shown
  separately), so windowing out earlier gates is fine.

## State table (`render_statevector`)

Handles both modes, `hide_zeros`, the phase column, change-highlighting,
and the `ancilla|input` register split (`ancilla_bits` param). Notable
behaviors:
- `hide_zeros` prints a note when there's nothing to hide, so the toggle
  never looks like a no-op.
- Bit order is qcsim's descending convention (`q(n-1)...q0`) — the
  measurement histogram's `_project_label` matches this so the two never
  disagree.

## Measurement + summary (end of run)

- `sample_measurements(step, register, shots)` — samples the final state,
  projecting onto a register (descending qubit order).
- `render_measurement(result, final_step, shots)` — histogram of the
  meaningful register (input/search/qubits) + most-frequent outcome.
- `render_execution_summary(result, final_step)` — calls
  `result.outcome(...)` for the measured/expected/success verdict plus the
  narrative from `result.summarize(...)`.

## Adding a rendering feature

1. Put the string-building in `render.py`; put any *interpretation* logic
   (what a state means, phase math) in `interpret.py` so a future
   front-end can reuse it.
2. Gate every non-ASCII glyph on `_U`.
3. Decide beginner vs advanced (or both). Keep beginner minimal.
4. If it's a per-step element, add it in `render_step`; if it's an
   end-of-run element, the CLI shows it on the last step (see `cli.py`
   `_interactive_loop`).
5. Add a test that asserts the feature's marker text appears (see
   `TestRedesignRendering` in `tests/test_stepper.py`).

See [API-Reference.md](API-Reference.md) for exact signatures.
