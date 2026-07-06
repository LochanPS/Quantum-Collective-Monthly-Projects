"""Terminal rendering for algorithm step-through.

Mirrors qcsim's visualize.py bar-chart style (same unicode/ASCII fallback
pattern) since steps carry a raw statevector array rather than a
QuantumCircuit, so qcsim's draw_statevector() (which expects a circuit)
can't be reused directly.

Two detail levels:
  - "beginner": probabilities as plain percentages + a plain-English
    interpretation, zero-amplitude states hidden, no complex numbers.
  - "advanced": full complex amplitudes, phase column, changed-amplitude
    highlighting.
"""

from __future__ import annotations

import sys
from typing import Optional

from qcsim import QuantumCircuit
from qcsim.visualize import draw_circuit

from .interpret import interpret_state, phase_label
from .phases import current_segment_index, segments
from .stepper import Step, apply_log_entry


def _can_unicode() -> bool:
    try:
        enc = sys.stdout.encoding or "ascii"
        return enc.lower().replace("-", "") not in ("ascii", "latin1", "cp1252")
    except Exception:
        return False


_U = _can_unicode()
_BLOCK = "█" if _U else "#"
_LIGHT = "░" if _U else "."
_HLINE = "═" if _U else "="
_PHASE = "∠" if _U else "phase "

# ANSI styling. Terminals that already handle the CLI's clear-screen escape
# handle these too; on the rare terminal that doesn't, they show as stray
# characters but nothing breaks.
_BOLD = "\033[1m"
_DIM = "\033[2m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"

_CHANGE_THRESHOLD = 1e-6


def _changed(prev: Optional[Step], index: int, amp: complex) -> bool:
    """True if this basis amplitude differs from the previous step."""
    if prev is None:
        return False
    if index >= len(prev.statevector):
        return True
    return abs(prev.statevector[index] - amp) > _CHANGE_THRESHOLD


def _split_label(lbl: str, ancilla_bits: int) -> str:
    """Insert a `|` between the ancilla (leftmost) and input registers."""
    if 0 < ancilla_bits < len(lbl):
        return lbl[:ancilla_bits] + "|" + lbl[ancilla_bits:]
    return lbl


def render_statevector(
    step: Step,
    prev: Optional[Step] = None,
    mode: str = "advanced",
    hide_zeros: bool = False,
    threshold: float = 1e-6,
    ancilla_bits: int = 0,
) -> str:
    """Render a step's statevector as an amplitude/probability table.

    Args:
        step: The step to render.
        prev: The previous step, if any -- amplitudes that changed since
            then are highlighted (advanced mode only).
        mode: "beginner" (percentages only) or "advanced" (complex
            amplitudes + phase + change highlighting).
        hide_zeros: If True, basis states with ~zero probability are
            omitted (and a count of hidden states is shown instead). If on
            but there are no zeros, a note says so (so the toggle never
            looks like a no-op).
        threshold: Amplitudes/probabilities below this count as zero.
        ancilla_bits: If > 0, insert a `|` in each label after this many
            leftmost (highest-qubit / ancilla) bits, visually separating
            the ancilla register from the input register.

    Returns:
        Multi-line string ready to pass to print().
    """
    sv = step.statevector
    dim = len(sv)
    n = dim.bit_length() - 1
    bar_w = 20
    beginner = mode == "beginner"

    lines = []
    sep = _HLINE * 60
    lines.append(sep)
    header = " Probabilities" if beginner else " State Vector"
    if ancilla_bits:
        header += "   (label = ancilla|input)"
    lines.append(header)
    lines.append(sep)

    hidden = 0
    for i in range(dim):
        amp = sv[i]
        prob = abs(amp) ** 2
        is_zero = prob < threshold

        if hide_zeros and is_zero:
            hidden += 1
            continue

        lbl = _split_label(format(i, f"0{n}b"), ancilla_bits)
        filled = int(round(prob * bar_w))
        bar = _BLOCK * filled + _LIGHT * (bar_w - filled)
        pct = prob * 100

        if beginner:
            row = f" |{lbl}>  {bar}  {pct:5.1f}% chance"
        else:
            re_s = f"{0.0:+.4f}" if is_zero else f"{amp.real:+.4f}"
            im_s = f"{0.0:+.4f}i" if is_zero else f"{amp.imag:+.4f}i"
            ph = phase_label(amp) if not is_zero else ""
            ph_s = f" {_PHASE}{ph}" if ph else ""
            row = f" |{lbl}>  {re_s}{im_s}  {bar}  {pct:5.1f}%  {ph_s}"
            if _changed(prev, i, amp):
                row = f"{_BOLD}{_YELLOW}{row}{_RESET}"
            elif is_zero:
                row = f"{_DIM}{row}{_RESET}"

        lines.append(row)

    if hidden:
        lines.append(f"{_DIM} ... {hidden} zero-probability state(s) hidden{_RESET}")
    elif hide_zeros:
        lines.append(
            f"{_DIM} (hide-zeros on: no zero-probability states to hide right now){_RESET}"
        )

    lines.append(sep)
    return "\n".join(lines)


def render_progress_circuit(circuit: QuantumCircuit, up_to_index: int) -> str:
    """Draw a circuit diagram containing only gates up to and including
    the given step index -- gates not yet reached simply aren't drawn.
    """
    partial = QuantumCircuit(circuit.num_qubits, backend=circuit.backend)
    count = 0
    for name, qubits, params in circuit._log:
        if count > up_to_index:
            break
        if apply_log_entry(partial, name, list(qubits), params):
            count += 1
    return draw_circuit(partial)


def render_windowed_circuit(circuit: QuantumCircuit, lo: int, hi: int) -> str:
    """Draw only the gates whose step-index falls in [lo, hi].

    Keeps the diagram narrow on long circuits (e.g. multi-iteration
    Grover) by showing just the current phase's gates instead of the whole
    circuit every step. The diagram is purely structural -- the real state
    is shown separately -- so windowing out earlier gates is fine.
    """
    partial = QuantumCircuit(circuit.num_qubits, backend=circuit.backend)
    count = -1
    for name, qubits, params in circuit._log:
        # Advance a step counter for each non-barrier gate, but only apply
        # gates inside the window.
        is_gate = name != "BARRIER"
        if is_gate:
            count += 1
        if is_gate and lo <= count <= hi:
            apply_log_entry(partial, name, list(qubits), params)
        if count > hi:
            break
    return draw_circuit(partial)


def render_phase_progress(phases: list, step_index: int) -> str:
    """One-line progress indicator: the phase segments with the current
    one highlighted, earlier ones marked done.

    Example: ``Preparation [x] > Oracle [>] > Diffusion [ ]``
    """
    if not phases:
        return ""
    segs = segments(phases)
    cur = current_segment_index(segs, step_index)
    done = "✓" if _U else "x"
    active = "▶" if _U else ">"
    arrow = " → " if _U else " > "

    parts = []
    for i, (phase, _, _) in enumerate(segs):
        if i < cur:
            parts.append(f"{_DIM}{phase} {done}{_RESET}")
        elif i == cur:
            parts.append(f"{_BOLD}{_YELLOW}{phase} {active}{_RESET}")
        else:
            parts.append(f"{_DIM}{phase}{_RESET}")
    return "  Phases: " + arrow.join(parts)


def render_active_caption(step: Step) -> str:
    """One-line caption naming the gate that just fired and its qubits.

    A robust stand-in for inline highlighting of qcsim's ASCII diagram
    (which is fragile to poke at): the diagram shows all gates so far,
    this line points at the newest one.
    """
    qubits = ", ".join(f"q{q}" for q in step.qubits)
    arrow = "▶" if _U else ">"
    return f"  {arrow} just applied: {_BOLD}{step.gate_name}{_RESET} on {qubits}"


def render_step(
    circuit: QuantumCircuit,
    step: Step,
    prev: Optional[Step] = None,
    mode: str = "advanced",
    hide_zeros: bool = False,
    phases: Optional[list] = None,
    registers: Optional[dict] = None,
) -> str:
    """Render a full step view, with a genuinely different layout per mode.

    Beginner layout: phase progress, the gate's purpose, a plain percentage
    table, and a plain-English reading of the state. No amplitudes, no
    complex numbers, minimal circuit clutter.

    Advanced layout: phase progress, windowed circuit diagram + active-gate
    caption, full complex amplitudes with a phase column and
    change-highlighting, then the interpretation.

    Args:
        circuit: The original circuit.
        step: The step to render.
        prev: Previous step, for change highlighting (advanced only).
        mode: "beginner" or "advanced".
        hide_zeros: Hide zero-probability basis states.
        phases: Per-step phase labels (enables progress bar + windowed
            circuit). Falls back to plain step numbering if omitted.
    """
    beginner = mode == "beginner"
    ancilla_bits = len((registers or {}).get("ancilla", []))
    blocks: list = []

    progress = render_phase_progress(phases, step.index) if phases else ""
    if progress:
        blocks.append(progress)

    if beginner:
        # Minimal, intuitive. No circuit diagram (it's clutter for a
        # beginner); the phase bar + purpose text carry the structure.
        purpose = step.annotation or f"{step.gate_name} on q{step.qubits}"
        blocks.append(f"  Now: {_BOLD}{purpose}{_RESET}")
        blocks.append("")
        blocks.append(
            render_statevector(
                step, mode="beginner", hide_zeros=hide_zeros, ancilla_bits=ancilla_bits
            )
        )
        blocks.append("")
        blocks.append(f"  What this means: {interpret_state(step)}")
    else:
        header = f"Step {step.index}: {step.gate_name} on qubit(s) {step.qubits}"
        if step.annotation:
            header += f"\n  {step.annotation}"
        blocks.append(header)
        blocks.append("")
        if phases:
            segs = segments(phases)
            cur = current_segment_index(segs, step.index)
            _, lo, hi = segs[cur]
            blocks.append(f"  Circuit window -- {phases[step.index]} phase (steps {lo}-{hi}):")
            blocks.append(render_windowed_circuit(circuit, lo, hi))
        else:
            blocks.append(render_progress_circuit(circuit, step.index))
        blocks.append(render_active_caption(step))
        blocks.append("")
        blocks.append(
            render_statevector(
                step, prev=prev, mode="advanced", hide_zeros=hide_zeros, ancilla_bits=ancilla_bits
            )
        )
        blocks.append("")
        blocks.append(f" State: {interpret_state(step)}")

    return "\n".join(blocks)


# ================================================================== #
#  Measurement stage + execution summary (end of run)
# ================================================================== #


def _project_label(label: str, qubits: list) -> str:
    """Project a full state label onto a subset of qubits.

    Keeps qcsim's descending convention (q_high...q_low, same as the state
    table's labels) so a whole-system register reproduces the label exactly
    and per-register projections stay consistent with what's shown above.
    label is q(n-1)...q0; qubit q sits at index len-1-q.
    """
    n = len(label)
    return "".join(label[n - 1 - q] for q in sorted(qubits, reverse=True))


def sample_measurements(step: Step, register: Optional[list], shots: int) -> dict:
    """Sample `shots` measurements, tallied over the given register (or the
    full state if register is None). Returns {outcome: count}."""
    import random

    labels = list(step.probabilities.keys())
    weights = list(step.probabilities.values())
    if not labels:
        return {}
    counts: dict = {}
    for _ in range(shots):
        full = random.choices(labels, weights=weights, k=1)[0]
        key = _project_label(full, register) if register else full
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def render_measurement(result, final_step: Step, shots: int = 100) -> str:
    """Measurement stage: sample the meaningful register and show a small
    histogram plus the most-frequent outcome."""
    # Pick the primary register to report (input / search / qubits), else all.
    reg = None
    for key in ("input", "search", "qubits"):
        if key in result.registers:
            reg = result.registers[key]
            break
    counts = sample_measurements(final_step, reg, shots)
    if not counts:
        return ""

    reg_name = next(
        (k for k in ("input", "search", "qubits") if k in result.registers), "all qubits"
    )
    lines = [f"  Measurement ({shots} shots, {reg_name} register):"]
    top = max(counts.items(), key=lambda kv: kv[1])
    for outcome, cnt in list(counts.items())[:8]:
        pct = cnt / shots * 100
        bar = _BLOCK * int(round(pct / 100 * 24))
        mark = "  <- most frequent" if outcome == top[0] else ""
        lines.append(f"    {outcome}  {bar:<24} {cnt:4d} ({pct:4.1f}%){mark}")
    return "\n".join(lines)


def render_execution_summary(result, final_step: Step) -> str:
    """Structured end-of-run summary: algorithm, params, measured vs
    expected, correctness, and the key takeaway."""
    es = result.execution_summary(final_step)
    params = "  ".join(f"{k}: {v}" for k, v in result.info.items())
    lines = [
        f"{_BOLD}=== Execution Summary ==={_RESET}",
        f"  Algorithm : {result.title}",
    ]
    if params:
        lines.append(f"  Parameters: {params}")
    if es is not None:
        ok = "✓ SUCCESS" if _U else "SUCCESS"
        no = "✗ MISMATCH" if _U else "MISMATCH"
        verdict = ok if es.success else no
        lines.append(f"  Measured  : {es.measured}")
        lines.append(f"  Expected  : {es.expected}")
        lines.append(f"  Result    : {_BOLD}{verdict}{_RESET}")
        lines.append(f"  Takeaway  : {es.takeaway}")
    narrative = result.summary(final_step)
    if narrative:
        lines.append("")
        lines.append(f"  {narrative}")
    return "\n".join(lines)
