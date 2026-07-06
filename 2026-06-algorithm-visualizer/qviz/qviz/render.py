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


def render_statevector(
    step: Step,
    prev: Optional[Step] = None,
    mode: str = "advanced",
    hide_zeros: bool = False,
    threshold: float = 1e-6,
) -> str:
    """Render a step's statevector as an amplitude/probability table.

    Args:
        step: The step to render.
        prev: The previous step, if any -- amplitudes that changed since
            then are highlighted (advanced mode only).
        mode: "beginner" (percentages only) or "advanced" (complex
            amplitudes + phase + change highlighting).
        hide_zeros: If True, basis states with ~zero probability are
            omitted (and a count of hidden states is shown instead).
        threshold: Amplitudes/probabilities below this count as zero.

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
    lines.append(" Probabilities" if beginner else " State Vector")
    lines.append(sep)

    hidden = 0
    for i in range(dim):
        amp = sv[i]
        prob = abs(amp) ** 2
        is_zero = prob < threshold

        if hide_zeros and is_zero:
            hidden += 1
            continue

        lbl = format(i, f"0{n}b")
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
) -> str:
    """Render a full step view.

    Layout: header + annotation, circuit diagram, active-gate caption,
    statevector/probability table, then a plain-English interpretation.

    Args:
        circuit: The original circuit (to rebuild the progress diagram).
        step: The step to render.
        prev: Previous step, for change highlighting.
        mode: "beginner" or "advanced".
        hide_zeros: Hide zero-probability basis states.
    """
    header = f"Step {step.index}: {step.gate_name} on qubit(s) {step.qubits}"
    if step.annotation:
        header += f"\n  {step.annotation}"

    diagram = render_progress_circuit(circuit, step.index)
    caption = render_active_caption(step)
    sv = render_statevector(step, prev=prev, mode=mode, hide_zeros=hide_zeros)
    interpretation = f" State: {interpret_state(step)}"

    return "\n".join([header, "", diagram, caption, "", sv, "", interpretation])
