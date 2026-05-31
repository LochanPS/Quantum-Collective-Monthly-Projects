"""
qcsim Interactive Circuit Builder
===================================
Terminal-based quantum circuit builder.
Arrow keys to navigate, letter keys to place gates.
Zero extra dependencies beyond the qcsim package itself.

Run:
    python -m qcsim.tui
    # or after pip install -e .:
    qcsim-interactive
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .circuit import QuantumCircuit
from .visualize import draw_histogram, draw_statevector

# ================================================================== #
#  Cross-platform keyboard input
# ================================================================== #

def _read_key() -> str:
    """Read one keypress and return a normalised string.

    Returns one of: 'up', 'down', 'left', 'right', 'enter', 'esc',
    'backspace', or a single lowercase character.
    """
    if os.name == "nt":
        return _read_key_windows()
    return _read_key_unix()


def _read_key_windows() -> str:
    import msvcrt
    ch = msvcrt.getch()
    if ch in (b"\x00", b"\xe0"):  # special key prefix
        ch2 = msvcrt.getch()
        return {
            b"H": "up", b"P": "down", b"K": "left", b"M": "right",
            b"S": "backspace",
        }.get(ch2, "")
    if ch == b"\r":
        return "enter"
    if ch == b"\x1b":
        return "esc"
    if ch == b"\x08":
        return "backspace"
    try:
        return ch.decode("utf-8").lower()
    except Exception:
        return ""


def _read_key_unix() -> str:
    import tty
    import termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            rest = sys.stdin.read(2)
            return {
                "[A": "up", "[B": "down", "[C": "right", "[D": "left",
            }.get(rest, "esc")
        if ch == "\r" or ch == "\n":
            return "enter"
        if ch in ("\x08", "\x7f"):
            return "backspace"
        return ch.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _input(prompt: str) -> str:
    """Input that works after tty.setraw is restored."""
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


# ================================================================== #
#  Gate definitions
# ================================================================== #

# Display symbols for each gate type (ASCII-safe)
_GATE_DISPLAY: Dict[str, str] = {
    "H":        "H",
    "X":        "X",
    "CNOT_C":   "@",   # CNOT control  (@  looks like a control dot)
    "CNOT_T":   "+",   # CNOT target   (+ looks like XOR/circle-plus)
    "SWAP_A":   "~",   # SWAP endpoint A
    "SWAP_B":   "~",   # SWAP endpoint B
    "":         " ",   # empty
}

# Keys the user presses to place gates
_KEY_TO_GATE: Dict[str, str] = {
    "h": "H",
    "x": "X",
    "c": "CNOT",
    "w": "SWAP",
}

_BASIC_GATES = ["H", "X", "CNOT", "SWAP"]


# ================================================================== #
#  Data model
# ================================================================== #

@dataclass
class Cell:
    """One slot in the circuit grid."""
    gate: str = ""          # gate type or '' for empty
    linked_row: int = -1    # for two-qubit gates: the row of the partner qubit


@dataclass
class CircuitGrid:
    """The full grid of cells."""
    num_qubits: int
    num_cols: int
    cells: List[List[Cell]] = field(default_factory=list)

    def __post_init__(self):
        if not self.cells:
            self.reset()

    def reset(self):
        self.cells = [
            [Cell() for _ in range(self.num_cols)]
            for _ in range(self.num_qubits)
        ]

    def get(self, row: int, col: int) -> Cell:
        return self.cells[row][col]

    def set(self, row: int, col: int, cell: Cell):
        self.cells[row][col] = cell

    def clear_cell(self, row: int, col: int):
        """Clear a cell and its linked partner."""
        cell = self.cells[row][col]
        if cell.linked_row >= 0:
            self.cells[cell.linked_row][col] = Cell()
        self.cells[row][col] = Cell()

    def to_json(self, name: str = "untitled", backend: str = "kronecker") -> dict:
        gates = []
        for row in range(self.num_qubits):
            for col in range(self.num_cols):
                c = self.cells[row][col]
                if c.gate:
                    entry: dict = {"gate": c.gate, "row": row, "col": col}
                    if c.linked_row >= 0:
                        entry["linked_row"] = c.linked_row
                    gates.append(entry)
        data = {
            "name": name,
            "num_qubits": self.num_qubits,
            "num_cols": self.num_cols,
            "backend": backend,
            "gates": gates,
        }
        raw = json.dumps(
            {"gates": sorted(gates, key=lambda g: (g["col"], g["row"])),
             "num_qubits": self.num_qubits},
            sort_keys=True,
        )
        data["fingerprint"] = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return data

    @classmethod
    def from_json(cls, data: dict) -> "CircuitGrid":
        grid = cls(num_qubits=data["num_qubits"], num_cols=data["num_cols"])
        for entry in data.get("gates", []):
            row, col = entry["row"], entry["col"]
            linked = entry.get("linked_row", -1)
            grid.cells[row][col] = Cell(gate=entry["gate"], linked_row=linked)
        return grid


# ================================================================== #
#  Renderer
# ================================================================== #

def _render_grid(
    grid: CircuitGrid,
    cursor_row: int,
    cursor_col: int,
    mode: str,
    status: str,
    backend: str,
) -> str:
    """Build the full TUI display string."""
    n = grid.num_qubits
    nc = grid.num_cols
    lines: List[str] = []

    # Header
    lines.append("  +-----------------------------------------+")
    lines.append("  |   qcsim Interactive Circuit Builder      |")
    lines.append("  +-----------------------------------------+")
    lines.append(
        f"  Qubits: {n}   Cols: {nc}   Backend: {backend}"
    )
    lines.append("")

    # Grid
    lbl_w = len(f"q[{n-1}]: ")

    for row in range(n):
        lbl = f"q[{row}]: ".ljust(lbl_w)
        line = "  " + lbl
        for col in range(nc):
            cell = grid.get(row, col)
            sym = _GATE_DISPLAY.get(cell.gate, "?")
            at_cursor = row == cursor_row and col == cursor_col
            if at_cursor:
                line += f">[{sym}]<"
            else:
                line += f"-[{sym}]-"
        lines.append(line)

        # Vertical connector between this row and the next
        if row < n - 1:
            conn = "  " + " " * lbl_w
            for col in range(nc):
                cell = grid.get(row, col)
                next_cell = grid.get(row + 1, col)
                # Draw | if this cell connects to row+1 or row+1 connects here
                show_vert = (
                    (cell.gate in ("CNOT_C", "CNOT_T", "SWAP_A", "SWAP_B")
                     and cell.linked_row == row + 1)
                    or (next_cell.gate in ("CNOT_C", "CNOT_T", "SWAP_A", "SWAP_B")
                        and next_cell.linked_row == row)
                )
                if show_vert:
                    conn += "   |  "
                else:
                    conn += "      "
            lines.append(conn)

    lines.append("")

    # Mode / status line
    mode_labels = {
        "NORMAL":      "NORMAL",
        "CNOT_FIRST":  "CNOT: press [C] on control qubit (target locked)",
        "SWAP_FIRST":  "SWAP: press [W] on second qubit (first locked)",
    }
    lines.append(f"  Mode : {mode_labels.get(mode, mode)}")
    lines.append(f"  Pos  : q[{cursor_row}], col {cursor_col}")
    if status:
        lines.append(f"  Info : {status}")
    lines.append("")

    # Help
    lines.append("  Gates : [H] [X] [C]NOT [W]AP  |  [Backspace] delete")
    lines.append("  Action: [R]un  [E]xport  [I]mport  [Esc] reset  [Q]uit")
    lines.append("  Move  : Arrow keys")

    return "\n".join(lines)


# ================================================================== #
#  Builder (main state machine)
# ================================================================== #

class CircuitBuilder:
    """Interactive circuit builder state machine."""

    def __init__(self):
        self.grid: Optional[CircuitGrid] = None
        self.backend: str = "kronecker"
        self.cursor_row: int = 0
        self.cursor_col: int = 0
        self.mode: str = "NORMAL"
        self.pending_row: int = -1
        self.pending_col: int = -1
        self.status: str = ""

    # ------------------------------------------------------------------ #
    #  Entry point
    # ------------------------------------------------------------------ #

    def run(self):
        _clear()
        self._setup()
        self._main_loop()

    # ------------------------------------------------------------------ #
    #  Setup
    # ------------------------------------------------------------------ #

    def _setup(self):
        print("  +-----------------------------------------+")
        print("  |   qcsim Interactive Circuit Builder      |")
        print("  |   Quantum Collective  v0.1.0             |")
        print("  +-----------------------------------------+")
        print()

        n = self._ask_int("  Number of qubits (1-10): ", 1, 10, default=2)
        nc = self._ask_int("  Number of columns  (1-20): ", 1, 20, default=6)

        while True:
            b = _input("  Backend — [K]ronecker (readable) or [T]ensor (fast): ").lower()
            if b in ("k", "kronecker", ""):
                self.backend = "kronecker"
                break
            if b in ("t", "tensor"):
                self.backend = "tensor"
                break

        self.grid = CircuitGrid(num_qubits=n, num_cols=nc)
        self.cursor_row = 0
        self.cursor_col = 0
        print()
        print(f"  Ready. {n} qubits | {nc} columns | {self.backend} backend.")
        print("  Press any key to start building...")
        _read_key()

    @staticmethod
    def _ask_int(prompt: str, lo: int, hi: int, default: int) -> int:
        while True:
            raw = _input(f"{prompt}[{default}]: ")
            if raw == "":
                return default
            try:
                v = int(raw)
                if lo <= v <= hi:
                    return v
            except ValueError:
                pass
            print(f"  Enter a number between {lo} and {hi}.")

    # ------------------------------------------------------------------ #
    #  Main loop
    # ------------------------------------------------------------------ #

    def _main_loop(self):
        while True:
            _clear()
            print(
                _render_grid(
                    self.grid,
                    self.cursor_row,
                    self.cursor_col,
                    self.mode,
                    self.status,
                    self.backend,
                )
            )
            self.status = ""  # clear after display
            key = _read_key()
            self._handle(key)

    def _handle(self, key: str):
        n = self.grid.num_qubits
        nc = self.grid.num_cols

        # Navigation
        if key == "up":
            self.cursor_row = max(0, self.cursor_row - 1)
        elif key == "down":
            self.cursor_row = min(n - 1, self.cursor_row + 1)
        elif key == "left":
            self.cursor_col = max(0, self.cursor_col - 1)
        elif key == "right":
            self.cursor_col = min(nc - 1, self.cursor_col + 1)

        # Single-qubit gates
        elif key == "h":
            self._place_single("H")
        elif key == "x":
            self._place_single("X")

        # Two-qubit gates
        elif key == "c":
            self._handle_cnot()
        elif key == "w":
            self._handle_swap()

        # Delete
        elif key == "backspace":
            self._delete()

        # Actions
        elif key == "r":
            self._run()
        elif key == "e":
            self._export()
        elif key == "i":
            self._import()
        elif key == "esc":
            self._reset()
        elif key == "q":
            self._quit()

    # ------------------------------------------------------------------ #
    #  Gate placement
    # ------------------------------------------------------------------ #

    def _place_single(self, gate_name: str):
        if self.mode != "NORMAL":
            self.mode = "NORMAL"
            self.status = "Cancelled pending gate."
            return
        r, c = self.cursor_row, self.cursor_col
        self.grid.clear_cell(r, c)
        self.grid.set(r, c, Cell(gate=gate_name))
        self.status = f"Placed {gate_name} at q[{r}], col {c}."

    def _handle_cnot(self):
        r, c = self.cursor_row, self.cursor_col
        if self.mode == "NORMAL":
            # First press = TARGET
            self.mode = "CNOT_FIRST"
            self.pending_row = r
            self.pending_col = c
            self.grid.clear_cell(r, c)
            self.grid.set(r, c, Cell(gate="CNOT_T", linked_row=-1))
            self.status = f"CNOT target at q[{r}]. Navigate to control qubit, press [C]."
        elif self.mode == "CNOT_FIRST":
            # Second press = CONTROL (must be same column)
            tgt_row = self.pending_row
            col = self.pending_col
            if c != col:
                self.status = f"CNOT control must be in col {col} (same as target). Try again."
                self.grid.clear_cell(tgt_row, col)
                self.mode = "NORMAL"
                return
            if r == tgt_row:
                self.status = "CNOT: control and target must be on different qubit rows."
                self.grid.clear_cell(tgt_row, col)
                self.mode = "NORMAL"
                return
            # Commit both cells
            self.grid.set(tgt_row, col, Cell(gate="CNOT_T", linked_row=r))
            self.grid.set(r, col, Cell(gate="CNOT_C", linked_row=tgt_row))
            self.mode = "NORMAL"
            self.status = f"CNOT: ctrl=q[{r}], tgt=q[{tgt_row}], col {col}."

    def _handle_swap(self):
        r, c = self.cursor_row, self.cursor_col
        if self.mode == "NORMAL":
            self.mode = "SWAP_FIRST"
            self.pending_row = r
            self.pending_col = c
            self.grid.clear_cell(r, c)
            self.grid.set(r, c, Cell(gate="SWAP_A", linked_row=-1))
            self.status = f"SWAP first qubit at q[{r}]. Navigate to second qubit, press [W]."
        elif self.mode == "SWAP_FIRST":
            a_row = self.pending_row
            col = self.pending_col
            if c != col:
                self.status = f"SWAP second qubit must be in col {col}. Try again."
                self.grid.clear_cell(a_row, col)
                self.mode = "NORMAL"
                return
            if r == a_row:
                self.status = "SWAP: need two different qubit rows."
                self.grid.clear_cell(a_row, col)
                self.mode = "NORMAL"
                return
            self.grid.set(a_row, col, Cell(gate="SWAP_A", linked_row=r))
            self.grid.set(r, col, Cell(gate="SWAP_B", linked_row=a_row))
            self.mode = "NORMAL"
            self.status = f"SWAP: q[{a_row}] <-> q[{r}], col {col}."

    def _delete(self):
        r, c = self.cursor_row, self.cursor_col
        self.grid.clear_cell(r, c)
        if self.mode != "NORMAL":
            self.mode = "NORMAL"
        self.status = f"Deleted gate at q[{r}], col {c}."

    # ------------------------------------------------------------------ #
    #  Build qcsim circuit from grid
    # ------------------------------------------------------------------ #

    def _to_qcsim(self) -> QuantumCircuit:
        """Convert the grid to a runnable QuantumCircuit."""
        qc = QuantumCircuit(self.grid.num_qubits, backend=self.backend)
        n = self.grid.num_qubits
        nc = self.grid.num_cols

        for col in range(nc):
            handled = set()
            for row in range(n):
                if row in handled:
                    continue
                cell = self.grid.get(row, col)
                g = cell.gate
                if g == "H":
                    qc.h(row)
                elif g == "X":
                    qc.x(row)
                elif g == "CNOT_C":
                    tgt = cell.linked_row
                    if tgt >= 0:
                        qc.cnot(row, tgt)
                        handled.add(tgt)
                elif g == "CNOT_T":
                    pass  # handled when ctrl row is visited
                elif g == "SWAP_A":
                    other = cell.linked_row
                    if other >= 0 and other > row:
                        qc.swap(row, other)
                        handled.add(other)
                elif g == "SWAP_B":
                    pass  # handled by SWAP_A
                handled.add(row)
        return qc

    # ------------------------------------------------------------------ #
    #  Run
    # ------------------------------------------------------------------ #

    def _run(self):
        _clear()
        print("  Running simulation...\n")
        try:
            qc = self._to_qcsim()
            circ_str = qc.draw()
            sv_str = draw_statevector(qc)
            counts = qc.measure_all(shots=2048)
            hist_str = draw_histogram(counts, shots=2048)

            _clear()
            print(circ_str)
            print()
            print(sv_str)
            print()
            print(hist_str)
            print()
            print(f"  {qc.summary()}")
        except Exception as exc:
            print(f"  Simulation error: {exc}")

        print()
        _input("  Press Enter to return to builder...")

    # ------------------------------------------------------------------ #
    #  Export
    # ------------------------------------------------------------------ #

    def _export(self):
        _clear()
        print("  Export circuit\n")
        name = _input("  Circuit name [untitled]: ") or "untitled"
        safe_name = name.lower().replace(" ", "-")
        default_path = f"{safe_name}.json"
        path = _input(f"  Save path [{default_path}]: ") or default_path
        if not path.endswith(".json"):
            path += ".json"

        data = self.grid.to_json(name=name, backend=self.backend)
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"\n  Saved: {path}")
            print(f"  Fingerprint: {data['fingerprint']}")
            print()
            print("  To share in the circuit library:")
            print(f"  Copy {path} to circuit-library/ in the repo and open a PR.")
        except Exception as exc:
            print(f"  Error saving: {exc}")

        print()
        _input("  Press Enter to continue...")

    # ------------------------------------------------------------------ #
    #  Import
    # ------------------------------------------------------------------ #

    def _import(self):
        _clear()
        print("  Import circuit\n")
        path = _input("  Path to .json file: ")
        if not path:
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self.grid = CircuitGrid.from_json(data)
            self.backend = data.get("backend", "kronecker")
            self.cursor_row = 0
            self.cursor_col = 0
            self.mode = "NORMAL"
            self.status = f"Loaded: {data.get('name', 'circuit')}"
            print(f"\n  Loaded '{data.get('name')}' — "
                  f"{self.grid.num_qubits}q, {self.grid.num_cols} cols.")
        except Exception as exc:
            print(f"  Error loading: {exc}")

        print()
        _input("  Press Enter to continue...")

    # ------------------------------------------------------------------ #
    #  Reset / Quit
    # ------------------------------------------------------------------ #

    def _reset(self):
        _clear()
        ans = _input("  Reset circuit? All gates will be cleared. [y/N]: ").lower()
        if ans == "y":
            self.grid.reset()
            self.mode = "NORMAL"
            self.cursor_row = 0
            self.cursor_col = 0
            self.status = "Circuit reset."

    def _quit(self):
        _clear()
        ans = _input("  Quit? [y/N]: ").lower()
        if ans == "y":
            _clear()
            print("  Goodbye!")
            sys.exit(0)


# ================================================================== #
#  Entry point
# ================================================================== #

def main():
    """Entry point for qcsim-interactive."""
    try:
        CircuitBuilder().run()
    except KeyboardInterrupt:
        _clear()
        print("  Interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
