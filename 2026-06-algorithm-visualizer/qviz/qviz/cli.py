"""Interactive step-through CLI for qviz.

Pick a reference algorithm, then step forward/backward through it one
gate at a time, watching the state vector evolve. Terminal-only by
design -- see the challenge README for why the graphical version lives
in a separate paid product instead of here.
"""

from __future__ import annotations

import sys
from typing import Callable, Dict, Tuple

from qcsim import QuantumCircuit

from .algorithms import bernstein_vazirani, deutsch_jozsa, grover, qft_algorithm
from .render import render_step
from .stepper import Step, step_through


def _clear() -> None:
    print("\033[2J\033[H", end="")


def _build_deutsch_jozsa() -> Tuple[QuantumCircuit, list]:
    n = input("  Number of input qubits [2]: ").strip()
    n = int(n) if n else 2
    oracle = input("  Oracle [constant_0/constant_1/balanced, default balanced]: ").strip() or "balanced"
    return deutsch_jozsa(n, oracle)


def _build_bernstein_vazirani() -> Tuple[QuantumCircuit, list]:
    secret = input("  Secret bitstring [101]: ").strip() or "101"
    return bernstein_vazirani(secret)


def _build_grover() -> Tuple[QuantumCircuit, list]:
    target = input("  Marked 2-bit state [11]: ").strip() or "11"
    return grover(target)


def _build_qft() -> Tuple[QuantumCircuit, list]:
    n = input("  Number of qubits [3]: ").strip()
    n = int(n) if n else 3
    initial = input("  Initial state bitstring [000]: ").strip() or "0" * n
    return qft_algorithm(n, initial)


_ALGORITHMS: Dict[str, Callable[[], Tuple[QuantumCircuit, list]]] = {
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


def _attach_annotations(steps: list, annotations: list) -> None:
    for step, note in zip(steps, annotations):
        step.annotation = note


def _interactive_loop(circuit: QuantumCircuit, steps: list, algorithm_name: str) -> None:
    if not steps:
        print("  This circuit has no steppable gates.")
        return

    idx = 0
    while True:
        _clear()
        print(f"  qviz — {algorithm_name}   (step {idx + 1}/{len(steps)})\n")
        print(render_step(circuit, steps[idx]))
        print()
        print("  [Enter] next  [b] back  [j N] jump to step N  [q] quit")
        cmd = input("  > ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "b":
            idx = max(0, idx - 1)
        elif cmd.startswith("j"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                idx = min(len(steps) - 1, max(0, int(parts[1]) - 1))
        else:
            idx = min(len(steps) - 1, idx + 1)
            if idx == len(steps) - 1 and cmd == "":
                # Allow one more Enter at the final step to exit cleanly.
                pass


def main() -> None:
    _clear()
    print("  qviz — Quantum Algorithm Visualizer\n")
    print("  Choose an algorithm:")
    for key, name in _ALGORITHM_NAMES.items():
        print(f"    [{key}] {name}")
    print()
    choice = input("  > ").strip()

    builder = _ALGORITHMS.get(choice)
    if builder is None:
        print("  Invalid choice.")
        sys.exit(1)

    circuit, annotations = builder()
    steps = step_through(circuit)
    _attach_annotations(steps, annotations)
    _interactive_loop(circuit, steps, _ALGORITHM_NAMES[choice])


if __name__ == "__main__":
    main()
