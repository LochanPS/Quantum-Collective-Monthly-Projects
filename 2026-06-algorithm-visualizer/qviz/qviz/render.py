"""Terminal rendering for algorithm step-through.

Mirrors qcsim's visualize.py bar-chart style (same unicode/ASCII fallback
pattern) since steps carry a raw statevector array rather than a
QuantumCircuit, so qcsim's draw_statevector() (which expects a circuit)
can't be reused directly.
"""

from __future__ import annotations

import sys

from qcsim import QuantumCircuit
from qcsim.visualize import draw_circuit

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


def render_statevector(step: Step, threshold: float = 1e-6) -> str:
    """Render a step's statevector as an amplitude table with bars.

    Same visual format as qcsim's draw_statevector(), but reads from a
    Step's stored arrays instead of a live circuit.

    Args:
        step: The step to render.
        threshold: Amplitudes with |amp| < threshold display as zero.

    Returns:
        Multi-line string ready to pass to print().
    """
    sv = step.statevector
    dim = len(sv)
    n = dim.bit_length() - 1
    bar_w = 20

    lines = []
    sep = _HLINE * 56
    lines.append(sep)
    lines.append(" State Vector")
    lines.append(sep)

    for i in range(dim):
        lbl = format(i, f"0{n}b")
        amp = sv[i]
        prob = abs(amp) ** 2
        if abs(amp) < threshold and prob < threshold:
            re_s = f"{0.0:+.4f}"
            im_s = f"{0.0:+.4f}i"
        else:
            re_s = f"{amp.real:+.4f}"
            im_s = f"{amp.imag:+.4f}i"

        filled = int(round(prob * bar_w))
        empty = bar_w - filled
        bar = _BLOCK * filled + _LIGHT * empty
        pct = prob * 100

        lines.append(f" |{lbl}>  {re_s}{im_s}  {bar}  {pct:5.1f}%")

    lines.append(sep)
    return "\n".join(lines)


def render_progress_circuit(circuit: QuantumCircuit, up_to_index: int) -> str:
    """Draw a circuit diagram containing only gates up to and including
    the given step index -- a simple way to "highlight" progress: gates
    not yet reached just aren't drawn.

    Args:
        circuit: The original, fully-built circuit.
        up_to_index: Highest Step.index to include (0-indexed, inclusive).

    Returns:
        Multi-line circuit diagram string (qcsim's draw_circuit format).
    """
    partial = QuantumCircuit(circuit.num_qubits, backend=circuit.backend)
    count = 0
    for name, qubits, params in circuit._log:
        if count > up_to_index:
            break
        if apply_log_entry(partial, name, list(qubits), params):
            count += 1
    return draw_circuit(partial)


def render_step(circuit: QuantumCircuit, step: Step) -> str:
    """Render a full step view: header, progress diagram, statevector.

    Args:
        circuit: The original circuit being stepped through (needed to
            rebuild the progress diagram up to this step).
        step: The step to render.

    Returns:
        Multi-line string ready to pass to print().
    """
    header = f"Step {step.index}: {step.gate_name} on qubit(s) {step.qubits}"
    if step.annotation:
        header += f"\n  {step.annotation}"

    diagram = render_progress_circuit(circuit, step.index)
    sv = render_statevector(step)

    return "\n".join([header, "", diagram, "", sv])
