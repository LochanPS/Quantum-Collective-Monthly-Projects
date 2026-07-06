"""Phase-segment helpers.

An algorithm's `phases` list gives one phase label per step. This module
groups consecutive same-phase steps into *segments* (so Grover's repeated
Oracle/Diffusion show up as separate segments per iteration) and locates
the segment a given step falls in -- used for the progress indicator and
the windowed circuit view.
"""

from __future__ import annotations

from typing import List, Tuple

# (phase_label, start_step_index, end_step_index_inclusive)
Segment = Tuple[str, int, int]


def segments(phases: List[str]) -> List[Segment]:
    """Group consecutive equal phase labels into segments."""
    if not phases:
        return []
    out: List[Segment] = []
    start = 0
    for i in range(1, len(phases) + 1):
        if i == len(phases) or phases[i] != phases[start]:
            out.append((phases[start], start, i - 1))
            start = i
    return out


def current_segment_index(segs: List[Segment], step_index: int) -> int:
    """Index into `segs` of the segment containing `step_index` (0 if none)."""
    for i, (_, lo, hi) in enumerate(segs):
        if lo <= step_index <= hi:
            return i
    return 0
