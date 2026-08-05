"""Terminal rendering — side-by-side ideal vs. noisy distributions."""

from __future__ import annotations

import sys
from typing import Dict


def _can_unicode() -> bool:
    """Return True if stdout supports Unicode block characters (matches qcsim)."""
    try:
        enc = sys.stdout.encoding or "ascii"
        return enc.lower().replace("-", "") not in ("ascii", "latin1", "cp1252")
    except Exception:
        return False


_BAR = "█" if _can_unicode() else "#"  # full block, ASCII fallback


def _bars(dist: Dict[str, float], keys, width: int) -> Dict[str, str]:
    out = {}
    for k in keys:
        p = dist.get(k, 0.0)
        filled = int(round(p * width))
        out[k] = _BAR * filled
    return out


def compare(
    ideal: Dict[str, float],
    noisy: Dict[str, float],
    width: int = 18,
    threshold: float = 1e-4,
) -> str:
    """Render ideal and noisy probability distributions side by side.

    Args:
        ideal: Ideal distribution (bitstring -> probability).
        noisy: Noisy distribution (bitstring -> probability).
        width: Bar width in characters for 100% probability.
        threshold: Hide basis states below this probability in both.

    Returns:
        A multi-line string ready to print.
    """
    keys = sorted(
        k for k in set(ideal) | set(noisy)
        if ideal.get(k, 0.0) > threshold or noisy.get(k, 0.0) > threshold
    )
    ibars = _bars(ideal, keys, width)
    nbars = _bars(noisy, keys, width)

    left_w = width + 8  # bar + " 100.0%"
    header = f"  {'ideal'.ljust(left_w)}    noisy"
    lines = [header, "  " + "-" * (left_w + 4 + width + 8)]
    for k in keys:
        ip = ideal.get(k, 0.0)
        np_ = noisy.get(k, 0.0)
        left = f"{k}  {ibars[k].ljust(width)} {ip * 100:5.1f}%"
        right = f"{k}  {nbars[k].ljust(width)} {np_ * 100:5.1f}%"
        lines.append(f"  {left.ljust(left_w + 4)}{right}")
    return "\n".join(lines)


def metrics_footer(fidelity: float, trace_distance: float, tvd: float) -> str:
    """One-line summary of the drift metrics."""
    return (
        f"  fidelity vs ideal: {fidelity:.3f}   "
        f"trace distance: {trace_distance:.3f}   "
        f"TVD: {tvd:.3f}"
    )
