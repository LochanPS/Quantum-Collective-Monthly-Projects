"""Plain-English interpretation of a quantum state.

Turns a Step's raw amplitude array into sentences a beginner can read:
what the current state *means*, which outcomes are likely, and (for
phase-carrying states like the QFT output) what the phases are doing.
Kept separate from render.py so the wording can be reused by any
front-end, not just the terminal.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from .stepper import Step


def nonzero_states(step: Step, threshold: float = 1e-9) -> List[Tuple[str, float, complex]]:
    """Return (label, probability, amplitude) for basis states with weight.

    Sorted by descending probability.
    """
    sv = step.statevector
    n = len(sv).bit_length() - 1
    out: List[Tuple[str, float, complex]] = []
    for i, amp in enumerate(sv):
        prob = abs(amp) ** 2
        if prob > threshold:
            out.append((format(i, f"0{n}b"), prob, amp))
    out.sort(key=lambda t: t[1], reverse=True)
    return out


def phase_label(amp: complex, threshold: float = 1e-9) -> str:
    """Human-readable phase of an amplitude, as a multiple of pi.

    Returns "" for negligible amplitudes (phase is meaningless there).
    """
    if abs(amp) < threshold:
        return ""
    angle = math.atan2(amp.imag, amp.real)  # (-pi, pi]
    frac = angle / math.pi
    if abs(frac) < 1e-6:
        return "0"
    if abs(abs(frac) - 1.0) < 1e-6:
        return "pi"
    return f"{frac:+.3g}*pi"


def interpret_state(step: Step) -> str:
    """One-to-two sentence plain-English reading of the current state."""
    states = nonzero_states(step)
    if not states:
        return "The state is empty (all amplitudes zero) -- this shouldn't happen for a valid circuit."

    dim = len(step.statevector)
    k = len(states)
    top_label, top_prob, _ = states[0]

    # Single definite outcome.
    if k == 1:
        return (
            f"The system is definitely in |{top_label}>. "
            f"Measuring now gives {top_label} with 100% certainty."
        )

    probs = [p for _, p, _ in states]
    all_equal = max(probs) - min(probs) < 1e-6

    # Uniform over the whole space.
    if all_equal and k == dim:
        pct = top_prob * 100
        return (
            f"Uniform superposition: all {dim} outcomes are equally likely ({pct:.1f}% each). "
            f"The system is 'considering' every possibility at once."
        )

    # Equal superposition over a subset.
    if all_equal:
        pct = top_prob * 100
        labels = ", ".join(f"|{s}>" for s, _, _ in states[:4])
        more = "" if k <= 4 else f" (+{k - 4} more)"
        return (
            f"Equal superposition of {k} states: {labels}{more} -- each {pct:.1f}%. "
            f"A measurement returns one of them at random, the rest have zero chance."
        )

    # General: name the front-runner(s).
    second = states[1] if k > 1 else None
    lead = f"Most likely outcome: |{top_label}> at {top_prob * 100:.1f}%"
    if second and second[1] > 0.05:
        lead += f", then |{second[0]}> at {second[1] * 100:.1f}%"
    return lead + f". {k} outcomes have non-zero probability."


def dominant_gap(step: Step) -> float:
    """Probability of the single most likely outcome -- handy for tracking
    Grover's amplitude amplification across steps (it climbs toward 1)."""
    states = nonzero_states(step)
    return states[0][1] if states else 0.0
