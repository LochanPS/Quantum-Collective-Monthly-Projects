"""Interactive step-through CLI for qviz.

Pick a reference algorithm, step through it gate-by-gate watching the
state evolve, read a plain-English interpretation at every step and an
algorithm-specific summary at the end -- then return to the menu to try
another one, no relaunch needed. Terminal-only by design (see the
challenge README).
"""

from __future__ import annotations

import time
from typing import Callable, Dict, List, Optional

from .algorithms import AlgorithmResult, bernstein_vazirani, deutsch_jozsa, grover, qft_algorithm
from .interpret import dominant_gap
from .render import render_step
from .stepper import Step, step_through

_BOLD = "\033[1m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def _clear() -> None:
    print("\033[2J\033[H", end="")


# ------------------------------------------------------------------ #
#  Algorithm builders (prompt for parameters, return AlgorithmResult)
# ------------------------------------------------------------------ #

def _build_deutsch_jozsa() -> AlgorithmResult:
    n = input("  Number of input qubits [2]: ").strip()
    n = int(n) if n else 2
    oracle = input("  Oracle [constant_0/constant_1/balanced, default balanced]: ").strip() or "balanced"
    return deutsch_jozsa(n, oracle)


def _build_bernstein_vazirani() -> AlgorithmResult:
    secret = input("  Secret bitstring [101]: ").strip() or "101"
    return bernstein_vazirani(secret)


def _build_grover() -> AlgorithmResult:
    target = input("  Marked 2-bit state [11]: ").strip() or "11"
    iters = input("  Iterations [1]: ").strip()
    return grover(target, int(iters) if iters else None)


def _build_qft() -> AlgorithmResult:
    n = input("  Number of qubits [3]: ").strip()
    n = int(n) if n else 3
    initial = input(f"  Initial state bitstring [{'0' * n}]: ").strip() or "0" * n
    return qft_algorithm(n, initial)


_ALGORITHMS: Dict[str, Callable[[], AlgorithmResult]] = {
    "1": _build_deutsch_jozsa,
    "2": _build_bernstein_vazirani,
    "3": _build_grover,
    "4": _build_qft,
}

_ALGORITHM_NAMES = {
    "1": "Deutsch-Jozsa",
    "2": "Bernstein-Vazirani",
    "3": "Grover's search",
    "4": "Quantum Fourier Transform",
}


def _attach_annotations(steps: List[Step], annotations: List[str]) -> None:
    for step, note in zip(steps, annotations):
        step.annotation = note


def _info_panel(result: AlgorithmResult) -> str:
    facts = "   ".join(f"{_DIM}{k}:{_RESET} {v}" for k, v in result.info.items())
    return f"  {facts}" if facts else ""


def _grover_amplification_bars(result: AlgorithmResult, steps: List[Step]) -> str:
    """Track the marked state's probability across the run -- makes Grover's
    amplitude amplification visible as a climbing bar per step."""
    marked = result.info.get("Marked state", "").strip("|>")
    if not marked:
        return ""
    lines = ["  Amplitude amplification (marked-state probability per step):"]
    for s in steps:
        p = s.probabilities.get(marked, 0.0)
        bar = "#" * int(round(p * 30))
        lines.append(f"    step {s.index:2d}  {bar:<30} {p * 100:5.1f}%")
    return "\n".join(lines)


# ------------------------------------------------------------------ #
#  Interactive stepping
# ------------------------------------------------------------------ #

def _interactive_loop(result: AlgorithmResult, steps: List[Step], mode: str, hide_zeros: bool) -> str:
    """Runs the stepper UI. Returns the (possibly toggled) mode so it
    persists to the next algorithm chosen from the menu."""
    if not steps:
        print("  This circuit has no steppable gates.")
        input("  Press Enter to return to the menu...")
        return mode

    idx = 0
    while True:
        _clear()
        head = f"  qviz — {result.title}   (step {idx + 1}/{len(steps)})   mode: {mode}"
        print(head)
        info = _info_panel(result)
        if info:
            print(info)
        print()
        prev = steps[idx - 1] if idx > 0 else None
        print(render_step(result.circuit, steps[idx], prev=prev, mode=mode, hide_zeros=hide_zeros))
        print()

        if idx == len(steps) - 1:
            summary = result.summary(steps[idx])
            if summary:
                print(f"  {_BOLD}{summary}{_RESET}")
                print()
            if result.title == "Grover's search":
                bars = _grover_amplification_bars(result, steps)
                if bars:
                    print(bars)
                    print()

        print(
            "  [Enter] next  [b] back  [j N] jump  [a] autoplay  "
            "[m] toggle mode  [h] toggle hide-zeros  [q] back to menu"
        )
        cmd = input("  > ").strip().lower()

        if cmd == "q":
            return mode
        elif cmd == "b":
            idx = max(0, idx - 1)
        elif cmd == "m":
            mode = "beginner" if mode == "advanced" else "advanced"
        elif cmd == "h":
            hide_zeros = not hide_zeros
        elif cmd == "a":
            idx = _autoplay(result, steps, idx, mode, hide_zeros)
        elif cmd.startswith("j"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = min(len(steps) - 1, max(0, int(parts[1]) - 1))
        else:  # Enter / anything else = next
            idx = min(len(steps) - 1, idx + 1)


def _autoplay(
    result: AlgorithmResult, steps: List[Step], start: int, mode: str, hide_zeros: bool, delay: float = 0.9
) -> int:
    """Advance automatically from `start` to the last step. Returns the
    final index so the caller lands there."""
    for idx in range(start, len(steps)):
        _clear()
        print(f"  qviz — {result.title}   (autoplay {idx + 1}/{len(steps)})")
        info = _info_panel(result)
        if info:
            print(info)
        print()
        prev = steps[idx - 1] if idx > 0 else None
        print(render_step(result.circuit, steps[idx], prev=prev, mode=mode, hide_zeros=hide_zeros))
        if idx < len(steps) - 1:
            time.sleep(delay)
    return len(steps) - 1


# ------------------------------------------------------------------ #
#  Menu
# ------------------------------------------------------------------ #

def main() -> None:
    mode = "advanced"
    while True:
        _clear()
        print("  qviz — Quantum Algorithm Visualizer\n")
        print("  Choose an algorithm:")
        for key, name in _ALGORITHM_NAMES.items():
            print(f"    [{key}] {name}")
        print("    [q] quit\n")
        choice = input("  > ").strip().lower()

        if choice == "q":
            _clear()
            print("  Bye.")
            return

        builder = _ALGORITHMS.get(choice)
        if builder is None:
            print("  Invalid choice.")
            time.sleep(0.8)
            continue

        try:
            result = builder()
        except ValueError as exc:
            print(f"  {exc}")
            input("  Press Enter to return to the menu...")
            continue

        # Auto-hide zero states once the space gets big enough to clutter.
        hide_zeros = result.circuit.num_qubits > 3
        steps = step_through(result.circuit)
        _attach_annotations(steps, result.annotations)
        mode = _interactive_loop(result, steps, mode, hide_zeros)


if __name__ == "__main__":
    main()
