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
import signal
import shutil
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .circuit import QuantumCircuit
from .visualize import draw_histogram, draw_statevector
from .analyzer import analyze_grid
from .patterns import recognize_grid
from .fingerprint import compute as compute_fingerprint

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
    if ch == b"\x0b":   # Ctrl+K
        return "ctrl+k"
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
        if ch == "\x0b":   # Ctrl+K
            return "ctrl+k"
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
    "SXdg":     "D",   # SX-dagger gate
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

    def expand_cols(self, by: int = 1, max_cols: int = 20) -> bool:
        """Add `by` empty columns to the right. Returns False if already at max."""
        if self.num_cols + by > max_cols:
            return False
        for row in self.cells:
            row.extend(Cell() for _ in range(by))
        self.num_cols += by
        return True

    def expand_qubits(self, by: int = 1, max_qubits: int = 15) -> bool:
        """Add `by` empty qubit rows at the bottom. Returns False if already at max."""
        if self.num_qubits + by > max_qubits:
            return False
        for _ in range(by):
            self.cells.append([Cell() for _ in range(self.num_cols)])
        self.num_qubits += by
        return True

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
        data["fingerprint"] = compute_fingerprint(gates, self.num_qubits)
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

    # Info panel — live circuit metrics
    metrics = analyze_grid(grid)
    lines.append(metrics.summary_line())
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
    lines.append("  Gates : [H] [X] [D] [C]NOT S[W]AP  |  [Backspace] delete")
    lines.append("  Help  : [?] gate info")
    lines.append("  Expand: [+] add column  [*] add qubit row")
    lines.append("  Action: [R]un  [E]xport JSON  [Ctrl+K] py/qasm  [I]mport  [Q]uit")
    lines.append("  Reset : [Esc] reset grid")
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
        self._resize_flag: bool = False  # set by SIGWINCH handler

    # ------------------------------------------------------------------ #
    #  Entry point
    # ------------------------------------------------------------------ #

    def run(self):
        _clear()
        self._register_resize_handler()
        self._check_terminal_size()
        self._setup()
        self._main_loop()

    def _register_resize_handler(self):
        """Register SIGWINCH handler on Unix for terminal resize events."""
        if os.name != "nt":
            try:
                signal.signal(signal.SIGWINCH, self._on_resize)
            except (AttributeError, OSError):
                pass  # not available on all platforms

    def _on_resize(self, signum, frame):
        """Called when terminal is resized (Unix only)."""
        self._resize_flag = True

    def _check_terminal_size(self):
        """Warn if terminal is smaller than the recommended minimum."""
        cols, rows = shutil.get_terminal_size(fallback=(80, 24))
        if cols < 80 or rows < 20:
            print(f"  Warning: terminal is {cols}x{rows}. Recommend 80x24 minimum.")
            print(f"  Resize your terminal for best experience.")
            print()

    # ------------------------------------------------------------------ #
    #  Setup
    # ------------------------------------------------------------------ #

    def _setup(self):
        print("  +-----------------------------------------+")
        print("  |   qcsim Interactive Circuit Builder      |")
        print("  |   Quantum Collective  v0.1.0             |")
        print("  +-----------------------------------------+")
        print()

        n = self._ask_int("  Number of qubits (1-15): ", 1, 15, default=2)
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
            # Handle terminal resize (Unix SIGWINCH)
            if self._resize_flag:
                self._resize_flag = False
                self._check_terminal_size()

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
        elif key == "d":
            self._place_single("SXdg")

        # Two-qubit gates
        elif key == "c":
            self._handle_cnot()
        elif key == "w":
            self._handle_swap()

        # Delete
        elif key == "backspace":
            self._delete()

        # Gate help
        elif key == "?":
            self._gate_help()

        # Grid expansion
        elif key == "+":
            self._expand_cols()
        elif key == "*":
            self._expand_qubits()

        # Actions
        elif key == "r":
            self._run()
        elif key == "e":
            self._export()
        elif key == "ctrl+k":
            self._export_qiskit()
        elif key == "i":
            self._import()
        elif key == "esc":
            self._reset()
        elif key == "q":
            self._quit()

    # ------------------------------------------------------------------ #
    #  Grid expansion
    # ------------------------------------------------------------------ #

    def _expand_cols(self):
        """Add one column to the right of the grid."""
        if self.grid.expand_cols(by=1, max_cols=20):
            self.status = f"Added column. Grid now {self.grid.num_cols} cols."
        else:
            self.status = "Already at max columns (20)."

    def _expand_qubits(self):
        """Add one qubit row at the bottom of the grid."""
        if self.grid.expand_qubits(by=1, max_qubits=15):
            self.status = f"Added qubit. Grid now {self.grid.num_qubits} qubits."
        else:
            self.status = "Already at max qubits (15)."

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
                elif g == "SXdg":
                    qc.sxdg(row)
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
    #  Gate help overlay
    # ------------------------------------------------------------------ #

    def _gate_help(self):
        """Show a help overlay for the gate at the current cursor position."""
        cell = self.grid.get(self.cursor_row, self.cursor_col)
        gate = cell.gate
        _clear()

        _GATE_HELP = {
            "H": (
                "Hadamard Gate",
                "Matrix: [[1, 1], [1, -1]] / sqrt(2)",
                "H|0> = (|0> + |1>) / sqrt(2)  -- superposition",
                "H|1> = (|0> - |1>) / sqrt(2)  -- superposition",
                "H*H = Identity  (applying twice returns to original state)",
                "",
                "Use: Starting point of nearly every quantum algorithm.",
                "     Creates the quantum parallelism that gives QC its power.",
            ),
            "X": (
                "Pauli-X Gate (NOT gate)",
                "Matrix: [[0, 1], [1, 0]]",
                "X|0> = |1>",
                "X|1> = |0>",
                "X*X = Identity",
                "",
                "Use: Initialise qubits to |1>, flip bits, build CNOT.",
            ),
            "SXdg": (
                "SX-dagger Gate",
                "Matrix: [[0.5-0.5j, 0.5+0.5j], [0.5+0.5j, 0.5-0.5j]]",
                "SXdg|0> = (0.5-0.5i)|0> + (0.5+0.5i)|1>",
                "SXdg|1> = (0.5+0.5i)|0> + (0.5-0.5i)|1>",
                "SXdg*SXdg = X",
                "",
                "Use: Inverse of SX gate. Creates opposite phase superposition.",
            ),
            "CNOT_C": (
                "CNOT Gate — Control qubit (@)",
                "4x4 matrix acting on 2 qubits.",
                "Flips the target qubit when this control qubit is |1>.",
                "",
                "  |00> -> |00>   (control=0, target unchanged)",
                "  |01> -> |01>",
                "  |10> -> |11>   (control=1, target flipped)",
                "  |11> -> |10>",
                "",
                "Use: Creates entanglement. Foundation of quantum teleportation.",
                "     Together with H, produces all Bell states.",
                "",
                f"  This is the CONTROL qubit. Linked to q[{cell.linked_row}] (target).",
            ),
            "CNOT_T": (
                "CNOT Gate — Target qubit (+)",
                "This qubit is flipped when the control qubit is |1>.",
                f"  Linked control: q[{cell.linked_row}]",
                "",
                "See control qubit (@) for full gate description.",
            ),
            "SWAP_A": (
                "SWAP Gate",
                "Exchanges the quantum states of two qubits completely.",
                "",
                "  |01> -> |10>",
                "  |10> -> |01>",
                "  SWAP(SWAP(a,b)) = identity",
                "",
                "Use: Routing qubits on hardware with limited connectivity.",
                f"  Swapping with q[{cell.linked_row}].",
            ),
            "SWAP_B": (
                "SWAP Gate — second qubit",
                f"  Swapping with q[{cell.linked_row}].",
                "See first SWAP qubit for full description.",
            ),
            "": (
                "Empty Cell",
                f"  Position: q[{self.cursor_row}], col {self.cursor_col}",
                "",
                "Place a gate here:",
                "  [H]  Hadamard          creates superposition",
                "  [X]  Pauli-X           flips the qubit (NOT gate)",
                "  [C]  CNOT              controlled-NOT (two-qubit entanglement)",
                "  [W]  SWAP              exchange two qubit states",
                "",
                "Navigate with arrow keys. [Backspace] to delete.",
            ),
        }

        title, *body = _GATE_HELP.get(gate, ("Unknown gate", f"Gate: {gate!r}"))

        width = 56
        border = "  +" + "-" * width + "+"
        print(border)
        print(f"  | {title.center(width - 2)} |")
        print(border)
        for line in body:
            padded = line[:width - 2].ljust(width - 2)
            print(f"  | {padded} |")
        print(border)
        print()
        _input("  Press Enter to return to builder...")

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

            # Pattern recognition
            pattern = recognize_grid(self.grid)

            _clear()
            print(circ_str)
            print()
            if pattern:
                width = 54
                print(f"  +{'-'*width}+")
                print(f"  | {'Pattern recognized: ' + pattern:^{width-2}} |")
                print(f"  +{'-'*width}+")
                print()
            print(sv_str)
            print()
            print(hist_str)
            print()
            print(f"  {qc.summary()}")
        except Exception as exc:
            print(f"  Simulation error: {exc}")
            import traceback
            traceback.print_exc()

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
    #  Qiskit export
    # ------------------------------------------------------------------ #

    def _export_qiskit(self):
        _clear()
        print("  Export circuit code\n")
        print("  Format:")
        print("    [1] Qiskit Python (.py)  — run on IBM Quantum or Aer simulator")
        print("    [2] OpenQASM 2.0  (.qasm) — universal, works with Qiskit/Cirq/Braket")
        print()
        fmt = _input("  Choose [1/2, default 1]: ").strip() or "1"
        if fmt not in ("1", "2"):
            print("  Invalid choice.")
            print()
            _input("  Press Enter to continue...")
            return

        name = _input("  Circuit name [untitled]: ") or "untitled"
        safe_name = name.lower().replace(" ", "_")

        if fmt == "1":
            default_path = f"{safe_name}_qiskit.py"
            path = _input(f"  Save path [{default_path}]: ") or default_path
            if not path.endswith(".py"):
                path += ".py"
        else:
            default_path = f"{safe_name}.qasm"
            path = _input(f"  Save path [{default_path}]: ") or default_path
            if not path.endswith(".qasm"):
                path += ".qasm"

        try:
            qc = self._to_qcsim()
            if fmt == "1":
                code = qc.to_qiskit_code(var="qc")
                hint1 = "  Run it:  python " + path
                hint2 = "  Needs:   pip install qiskit qiskit-aer"
                hint3 = "  IBM run: pip install qiskit-ibm-runtime"
            else:
                code = qc.to_qasm2()
                hint1 = "  Load in Qiskit: QuantumCircuit.from_qasm_file('" + path + "')"
                hint2 = "  Load in Cirq:   cirq.from_qasm(open('" + path + "').read())"
                hint3 = "  Compatible with: IBM Quantum, Google Cirq, Amazon Braket"

            abs_path = os.path.abspath(path)
            with open(path, "w") as f:
                f.write(code)
            print(f"\n  Saved: {abs_path}")
            print()
            print(hint1)
            print(hint2)
            print(hint3)
        except Exception as exc:
            print(f"  Error: {exc}")

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
    """Entry point for qcsim-interactive.

    Usage:
        qcsim-interactive                         # blank canvas
        qcsim-interactive --load circuit.json     # pre-load a circuit
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="qcsim-interactive",
        description="qcsim terminal circuit builder.",
    )
    parser.add_argument(
        "--load",
        metavar="FILE",
        default=None,
        help="Pre-load a circuit JSON file (from circuit-library or exported file).",
    )
    args = parser.parse_args()

    builder = CircuitBuilder()

    if args.load:
        # Pre-load circuit: skip setup, go straight to builder
        try:
            with open(args.load) as f:
                data = json.load(f)
            builder.grid = CircuitGrid.from_json(data)
            builder.backend = data.get("backend", "kronecker")
            builder.cursor_row = 0
            builder.cursor_col = 0
            builder.mode = "NORMAL"
            builder.status = f"Loaded: {data.get('name', 'circuit')}"
            _clear()
            builder._main_loop()
        except FileNotFoundError:
            print(f"  File not found: {args.load}")
            sys.exit(1)
        except Exception as exc:
            print(f"  Error loading circuit: {exc}")
            sys.exit(1)
    else:
        try:
            builder.run()
        except KeyboardInterrupt:
            _clear()
            print("  Interrupted. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
