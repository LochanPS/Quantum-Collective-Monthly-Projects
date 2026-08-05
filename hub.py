#!/usr/bin/env python3
"""Quantum Collective — terminal hub.

One launcher for all three terminal products. Pick a tool, use it, and when it
exits you land back here to pick the next one.

    python hub.py

Each tool is a normal installed package; the hub just launches its entry point
in a subprocess (so a tool crashing or calling sys.exit never takes the hub
down with it). If a tool isn't installed yet, the hub shows the install command
instead of launching.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys

# Base directory of this repo (folder containing this file).
try:
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent
except Exception:  # pragma: no cover
    ROOT = None


class Product:
    def __init__(self, key, name, tagline, package, entry, folder, extra_install=None):
        self.key = key
        self.name = name
        self.tagline = tagline
        self.package = package          # import name, e.g. "qcsim"
        self.entry = entry              # "module:function", e.g. "qcsim.tui:main"
        self.folder = folder            # path relative to repo root
        self.extra_install = extra_install or []  # deps to install first

    def installed(self) -> bool:
        return importlib.util.find_spec(self.package) is not None

    def launch(self) -> None:
        module, func = self.entry.split(":")
        code = f"from {module} import {func}; {func}()"
        subprocess.run([sys.executable, "-c", code])

    def install_hint(self) -> str:
        lines = [f'cd "{self.folder}"']
        for dep in self.extra_install:
            lines.append(f"pip install -e {dep}")
        lines.append("pip install -e .")
        return "   " + "\n   ".join(lines)


QCSIM_PATH = "2026-05-circuit-simulator/qcsim"

PRODUCTS = [
    Product(
        "1",
        "Circuit Simulator  (qcsim)",
        "Build quantum circuits visually — May's foundation. Project #1",
        "qcsim",
        "qcsim.tui:main",
        f"{QCSIM_PATH}",
    ),
    Product(
        "2",
        "Algorithm Visualizer  (qviz)",
        "Step through algorithms gate-by-gate — watch the state evolve. Project #2",
        "qviz",
        "qviz.cli:main",
        "2026-06-algorithm-visualizer/qviz",
        extra_install=[f"../../{QCSIM_PATH}"],
    ),
    Product(
        "3",
        "Noisy Simulator  (qnoise)",
        "See what a circuit really does on noisy hardware. Project #3",
        "qnoise",
        "qnoise.cli:main",
        "2026-08-noise-simulator/qnoise",
        extra_install=[f"../../{QCSIM_PATH}"],
    ),
]


def _can_unicode() -> bool:
    try:
        enc = sys.stdout.encoding or "ascii"
        return enc.lower().replace("-", "") not in ("ascii", "latin1", "cp1252")
    except Exception:
        return False


_U = _can_unicode()
_OK = "✓" if _U else "[installed]"
_NO = "✗" if _U else "[not installed]"
_LINE = "─" if _U else "-"


BANNER = r"""
  ___                 _                   ___     _ _         _   _
 / _ \ _  _ __ _ _ _ | |_ _  _ _ __      / __|___| | |___ __ | |_(_)_ _____
| (_) | || / _` | ' \|  _| || | '  \    | (__/ _ \ | / -_) _|| |  _| \ V / -_)
 \__\_\\_,_\__,_|_||_|\__|\_,_|_|_|_|    \___\___/_|_\___\__||_|\__|_|\_/\___|

              Monthly Projects — terminal product hub
"""


def render_menu() -> None:
    print(BANNER)
    print("  " + _LINE * 66)
    for p in PRODUCTS:
        status = _OK if p.installed() else _NO
        print(f"   {p.key}.  {p.name:<32} {status}")
        print(f"       {p.tagline}")
    print()
    print("   q.  quit")
    print("  " + _LINE * 66)


def handle(choice: str) -> bool:
    """Return False to quit, True to keep looping."""
    choice = choice.strip().lower()
    if choice in ("q", "quit", "exit"):
        return False
    for p in PRODUCTS:
        if choice == p.key:
            if not p.installed():
                print(f"\n  {p.name} isn't installed yet. From the repo root, run:\n")
                print(p.install_hint())
                print()
                input("  press Enter to return to the menu...")
                return True
            print(f"\n  launching {p.name} ...\n")
            try:
                p.launch()
            except KeyboardInterrupt:
                pass
            print(f"\n  ...back from {p.name}.\n")
            return True
    print(f"\n  unknown choice: {choice!r}\n")
    return True


def main() -> int:
    try:
        while True:
            render_menu()
            try:
                choice = input("\n  pick a product (1-3, q): ")
            except EOFError:
                break
            if not handle(choice):
                break
            print()
    except KeyboardInterrupt:
        pass
    print("\n  bye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
