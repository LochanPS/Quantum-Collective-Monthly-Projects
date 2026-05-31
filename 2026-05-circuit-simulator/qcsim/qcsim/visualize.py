"""Terminal visualisation for qcsim circuits and results.

Produces Unicode-based diagrams that degrade gracefully on ASCII-only terminals.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Dict

import numpy as np

if TYPE_CHECKING:
    from .circuit import QuantumCircuit

# ================================================================== #
#  Unicode / ASCII safety
# ================================================================== #

def _can_unicode() -> bool:
    """Return True if stdout supports Unicode output."""
    try:
        enc = sys.stdout.encoding or "ascii"
        return enc.lower().replace("-", "") not in ("ascii", "latin1", "cp1252")
    except Exception:
        return False


_U = _can_unicode()

# Symbols — fall back to ASCII equivalents when needed
_CTRL   = "●" if _U else "@"
_TARG   = "⊕" if _U else "X"
_SWAP_S = "╳" if _U else "x"
_CROSS  = "┼" if _U else "+"
_VERT   = "│" if _U else "|"
_BLOCK  = "█" if _U else "#"
_LIGHT  = "░" if _U else "."
_TL     = "┌" if _U else "+"
_TR     = "┐" if _U else "+"
_BL     = "└" if _U else "+"
_BR     = "┘" if _U else "+"
_LM     = "┤" if _U else "|"
_RM     = "├" if _U else "|"
_DASH   = "─" if _U else "-"
_HLINE  = "═" if _U else "="
_TITLE  = "╔" if _U else "+"

# ================================================================== #
#  Circuit diagram
# ================================================================== #

_CELL_W = 5  # fixed width per gate column (chars)


def draw_circuit(circuit: "QuantumCircuit") -> str:
    """Render the circuit as an ASCII/Unicode diagram.

    Layout uses 3 text rows per qubit (top, wire, bottom) plus a spacer
    row between consecutive qubits for vertical connector lines.

    Args:
        circuit: The QuantumCircuit to render.

    Returns:
        Multi-line string ready to pass to print().
    """
    n = circuit.num_qubits
    log = circuit._log
    W = _CELL_W

    # ---- Row index helpers ----
    # Qubit i → rows[4i] (top), rows[4i+1] (wire), rows[4i+2] (bot)
    # Spacer i→i+1 → rows[4i+3]
    total_rows = 4 * n - 1
    rows = [""] * total_rows

    # ---- Label prefix ----
    max_lbl = max(len(f"q[{n-1}]"), 4)
    lbl_w = max_lbl + 2  # 'q[0]: '

    for i in range(n):
        lbl = f"q[{i}]:"
        rows[4 * i]     = " " * lbl_w           # top: spaces
        rows[4 * i + 1] = lbl.ljust(lbl_w)      # wire: 'q[0]: '
        rows[4 * i + 2] = " " * lbl_w           # bot: spaces
        if i < n - 1:
            rows[4 * i + 3] = " " * lbl_w       # spacer

    # ---- Opening wire ----
    _add_wire_segment(rows, n, W, is_vert={})

    # ---- Process each gate ----
    for name, qubits, params in log:
        _render_gate(rows, n, W, name, qubits, params)
        if name != "BARRIER":
            _add_wire_segment(rows, n, W, is_vert={})

    # ---- Trim trailing whitespace per row ----
    lines = [r.rstrip() for r in rows]

    # ---- Header ----
    header = _circuit_header(circuit)
    return header + "\n" + "\n".join(lines)


def _add_wire_segment(rows, n: int, W: int, is_vert: dict) -> None:
    """Append a short wire segment to every row."""
    for i in range(n):
        rows[4 * i]     += " "
        rows[4 * i + 1] += _DASH
        rows[4 * i + 2] += " "
        if i < n - 1:
            rows[4 * i + 3] += _VERT if is_vert.get(i) else " "


def _render_gate(rows, n: int, W: int, name: str, qubits: list, params: dict) -> None:
    """Append one gate column to all rows."""

    if name == "BARRIER":
        lbl = params.get("label", "") if params else ""
        for i in range(n):
            rows[4 * i]     += " "
            rows[4 * i + 1] += _VERT
            rows[4 * i + 2] += " "
            if i < n - 1:
                rows[4 * i + 3] += " "
        return

    # ---- Single-qubit gates ----
    if len(qubits) == 1:
        q = qubits[0]
        # Build label for display
        if params and "theta" in params:
            theta = params["theta"]
            display = f"{name}({theta:.2f})"
        elif params and "lam" in params:
            lam = params["lam"]
            display = f"{name}({lam:.2f})"
        else:
            display = name

        # Box characters
        inner = f" {display} "
        w = max(len(inner), 3)
        inner = inner.center(w)
        top_box = _TL + _DASH * w + _TR
        mid_box = _LM + inner + _RM
        bot_box = _BL + _DASH * w + _BR
        wire_w = w + 2
        blank   = " " * wire_w
        wire    = _DASH * wire_w

        for i in range(n):
            if i == q:
                rows[4 * i]     += blank    # space above box (box drawn on next lines)
                rows[4 * i + 1] += mid_box
                rows[4 * i + 2] += blank
            else:
                rows[4 * i]     += blank
                rows[4 * i + 1] += wire
                rows[4 * i + 2] += blank
            if i < n - 1:
                rows[4 * i + 3] += " " * wire_w

        # Fix: top and bottom of box need to be on top/bot rows
        # Recalculate: top row of qubit q gets the top of the box
        # We need to replace the last `wire_w` characters of each row
        _replace_last(rows, 4 * q,     blank, top_box)
        _replace_last(rows, 4 * q + 2, blank, bot_box)
        return

    # ---- Two-qubit gates ----
    if len(qubits) == 2:
        a, b = qubits[0], qubits[1]
        lo, hi = min(a, b), max(a, b)

        if name in ("CNOT", "CX"):
            ctrl, tgt = a, b
            _render_controlled(rows, n, ctrl, tgt, _CTRL, _TARG, lo, hi)
        elif name == "CY":
            ctrl, tgt = a, b
            _render_controlled(rows, n, ctrl, tgt, _CTRL, "Y", lo, hi)
        elif name == "CZ":
            ctrl, tgt = a, b
            _render_controlled(rows, n, ctrl, tgt, _CTRL, "Z", lo, hi)
        elif name in ("SWAP",):
            _render_swap(rows, n, a, b, lo, hi)
        elif name == "CP":
            ctrl, tgt = a, b
            _render_controlled(rows, n, ctrl, tgt, _CTRL, "P", lo, hi)
        else:
            # Generic 2-qubit: show as box on both qubits
            _render_generic_multi(rows, n, name, qubits)
        return

    # ---- Three-qubit gates ----
    if len(qubits) == 3:
        if name in ("CCX", "Toffoli"):
            c0, c1, tgt = qubits
            _render_toffoli(rows, n, c0, c1, tgt)
        else:
            _render_generic_multi(rows, n, name, qubits)
        return

    # ---- Fallback: generic multi-qubit ----
    _render_generic_multi(rows, n, name, qubits)


def _replace_last(rows, row_idx: int, old: str, new: str) -> None:
    """Replace the last occurrence of `old` at the end of rows[row_idx]."""
    row = rows[row_idx]
    if row.endswith(old):
        rows[row_idx] = row[: len(row) - len(old)] + new


def _render_controlled(
    rows, n: int, ctrl: int, tgt: int,
    ctrl_sym: str, tgt_sym: str, lo: int, hi: int
) -> None:
    """Render a generic controlled gate between ctrl and tgt."""
    W = _CELL_W  # 5
    # ctrl row
    d2 = _DASH * 2
    if ctrl < tgt:
        rows[4 * ctrl]     += " " * W
        rows[4 * ctrl + 1] += f"{d2}{ctrl_sym}{d2}"
        rows[4 * ctrl + 2] += f"  {_VERT}  "
    else:
        rows[4 * ctrl]     += f"  {_VERT}  "
        rows[4 * ctrl + 1] += f"{d2}{ctrl_sym}{d2}"
        rows[4 * ctrl + 2] += " " * W

    # tgt row
    if ctrl < tgt:
        rows[4 * tgt]     += f"  {_VERT}  "
        rows[4 * tgt + 1] += f"{d2}{tgt_sym}{d2}"
        rows[4 * tgt + 2] += " " * W
    else:
        rows[4 * tgt]     += " " * W
        rows[4 * tgt + 1] += f"{d2}{tgt_sym}{d2}"
        rows[4 * tgt + 2] += f"  {_VERT}  "

    # Pass-through qubits
    for i in range(n):
        if i in (ctrl, tgt):
            continue
        if lo < i < hi:
            rows[4 * i]     += f"  {_VERT}  "
            rows[4 * i + 1] += f"{d2}{_CROSS}{d2}"
            rows[4 * i + 2] += f"  {_VERT}  "
        else:
            rows[4 * i]     += " " * W
            rows[4 * i + 1] += _DASH * W
            rows[4 * i + 2] += " " * W

    # Spacer rows
    for i in range(n - 1):
        if lo <= i < hi:
            rows[4 * i + 3] += f"  {_VERT}  "
        else:
            rows[4 * i + 3] += " " * W


def _render_swap(rows, n: int, a: int, b: int, lo: int, hi: int) -> None:
    """Render a SWAP gate."""
    W = _CELL_W

    d2 = _DASH * 2
    for i in range(n):
        if i == lo:
            rows[4 * i]     += " " * W
            rows[4 * i + 1] += f"{d2}{_SWAP_S}{d2}"
            rows[4 * i + 2] += f"  {_VERT}  "
        elif i == hi:
            rows[4 * i]     += f"  {_VERT}  "
            rows[4 * i + 1] += f"{d2}{_SWAP_S}{d2}"
            rows[4 * i + 2] += " " * W
        elif lo < i < hi:
            rows[4 * i]     += f"  {_VERT}  "
            rows[4 * i + 1] += f"{d2}{_CROSS}{d2}"
            rows[4 * i + 2] += f"  {_VERT}  "
        else:
            rows[4 * i]     += " " * W
            rows[4 * i + 1] += _DASH * W
            rows[4 * i + 2] += " " * W

    for i in range(n - 1):
        if lo <= i < hi:
            rows[4 * i + 3] += f"  {_VERT}  "
        else:
            rows[4 * i + 3] += " " * W


def _render_toffoli(rows, n: int, c0: int, c1: int, tgt: int) -> None:
    """Render a Toffoli (CCX) gate."""
    W = _CELL_W
    all_q = sorted([c0, c1, tgt])
    lo, hi = all_q[0], all_q[-1]

    for i in range(n):
        if i in (c0, c1):
            above = any(j > i for j in [c0, c1, tgt] if j != i)
            below = any(j < i for j in [c0, c1, tgt] if j != i)
            top = f"  {_VERT}  " if below else " " * W
            bot = f"  {_VERT}  " if above else " " * W
            rows[4 * i]     += top
            rows[4 * i + 1] += f"{_DASH*2}{_CTRL}{_DASH*2}"
            rows[4 * i + 2] += bot
        elif i == tgt:
            above = any(j < i for j in [c0, c1])
            below = any(j > i for j in [c0, c1])
            top = f"  {_VERT}  " if above else " " * W
            bot = f"  {_VERT}  " if below else " " * W
            rows[4 * i]     += top
            rows[4 * i + 1] += f"{_DASH*2}{_TARG}{_DASH*2}"
            rows[4 * i + 2] += bot
        elif lo < i < hi:
            rows[4 * i]     += f"  {_VERT}  "
            rows[4 * i + 1] += f"{_DASH*2}{_CROSS}{_DASH*2}"
            rows[4 * i + 2] += f"  {_VERT}  "
        else:
            rows[4 * i]     += " " * W
            rows[4 * i + 1] += _DASH * W
            rows[4 * i + 2] += " " * W

    for i in range(n - 1):
        if lo <= i < hi:
            rows[4 * i + 3] += f"  {_VERT}  "
        else:
            rows[4 * i + 3] += " " * W


def _render_generic_multi(rows, n: int, name: str, qubits: list) -> None:
    """Fallback: render a multi-qubit gate as a spanning box."""
    W = _CELL_W
    lo, hi = min(qubits), max(qubits)
    label = name[:3]  # truncate for display

    for i in range(n):
        if lo <= i <= hi:
            rows[4 * i]     += f"  {_VERT}  "
            rows[4 * i + 1] += f"{_DASH}[{label}]{_DASH}" if i in qubits else f"{_DASH*2}{_CROSS}{_DASH*2}"
            rows[4 * i + 2] += f"  {_VERT}  "
        else:
            rows[4 * i]     += " " * W
            rows[4 * i + 1] += _DASH * W
            rows[4 * i + 2] += " " * W

    for i in range(n - 1):
        if lo <= i < hi:
            rows[4 * i + 3] += f"  {_VERT}  "
        else:
            rows[4 * i + 3] += " " * W


def _circuit_header(circuit: "QuantumCircuit") -> str:
    """Build the circuit info header string."""
    gate_count = sum(1 for e in circuit._log if e[0] != "BARRIER")
    line = (
        f" Circuit: {circuit.num_qubits} qubit(s)  "
        f"{gate_count} gate(s)"
    )
    sep = _HLINE * (len(line) + 2)
    return f"{sep}\n{line}\n{sep}"


# ================================================================== #
#  State vector display
# ================================================================== #

def draw_statevector(circuit: "QuantumCircuit", threshold: float = 1e-6) -> str:
    """Render the current state vector as an amplitude table with bars.

    Args:
        circuit: The QuantumCircuit whose state vector to display.
        threshold: Amplitudes with |amp| < threshold are shown as zero.

    Returns:
        Multi-line string ready to pass to print().
    """
    sv = circuit.statevector()
    n = circuit.num_qubits
    dim = len(sv)
    bar_w = 20
    probs = np.abs(sv) ** 2

    lines = []
    sep = _HLINE * 56
    lines.append(sep)
    lines.append(" State Vector")
    lines.append(sep)

    for i in range(dim):
        lbl = circuit._state.label(i)
        amp = sv[i]
        prob = probs[i]
        if abs(amp) < threshold and prob < threshold:
            re_s = f"{0.0:+.4f}"
            im_s = f"{0.0:+.4f}i"
        else:
            re_s = f"{amp.real:+.4f}"
            im_s = f"{amp.imag:+.4f}i"

        filled = int(round(prob * bar_w))
        empty  = bar_w - filled
        bar    = _BLOCK * filled + _LIGHT * empty
        pct    = prob * 100

        lines.append(f" |{lbl}>  {re_s}{im_s}  {bar}  {pct:5.1f}%")

    lines.append(sep)
    norm = float(np.sum(probs))
    lines.append(f" Norm: {norm:.10f}")
    lines.append(sep)
    return "\n".join(lines)


# ================================================================== #
#  Measurement histogram
# ================================================================== #

def draw_histogram(counts: Dict[str, int], shots: int) -> str:
    """Render measurement counts as a horizontal bar chart.

    Args:
        counts: Dict mapping bitstring to count (from measure_all()).
        shots: Total number of shots (used to compute percentages).

    Returns:
        Multi-line string ready to pass to print().
    """
    bar_w = 32
    sep = _HLINE * 56
    lines = []
    lines.append(sep)
    lines.append(f" Measurement Results  ({shots} shots)")
    lines.append(sep)

    for state in sorted(counts):
        cnt = counts[state]
        pct = cnt / shots * 100
        filled = int(round(pct / 100 * bar_w))
        empty  = bar_w - filled
        bar    = _BLOCK * filled + _LIGHT * empty
        lines.append(f" |{state}>  {bar}  {cnt:5d}  {pct:5.1f}%")

    lines.append(sep)
    lines.append(f" Total: {shots} shots  |  {len(counts)} outcome(s)")
    lines.append(sep)
    return "\n".join(lines)


# ================================================================== #
#  Banner
# ================================================================== #

def banner() -> str:
    """Return the qcsim welcome banner."""
    lines = [
        "╔══════════════════════════════════════════════════════╗",
        "║       qcsim  —  Quantum Circuit Simulator            ║",
        "║       Quantum Collective  v0.1.0                     ║",
        "║       LSB convention  |  Kronecker expansion         ║",
        "╚══════════════════════════════════════════════════════╝",
    ]
    if not _U:
        lines = [l.replace("╔", "+").replace("╗", "+").replace("╚", "+")
                  .replace("╝", "+").replace("║", "|").replace("═", "=")
                 for l in lines]
    return "\n".join(lines)
