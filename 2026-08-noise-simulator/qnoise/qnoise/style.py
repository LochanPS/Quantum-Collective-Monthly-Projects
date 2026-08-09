"""Terminal styling — color, box-drawing, and precise bars, with fallbacks.

Everything here degrades gracefully:
    - No ANSI color when stdout isn't a TTY, when NO_COLOR is set, or when the
      terminal can't be put into VT mode.
    - ASCII substitutes for box-drawing and block characters on consoles that
      can't encode Unicode (matches qcsim's approach).

Import the module-level ``S`` (a :class:`Style`) and use its helpers.
"""

from __future__ import annotations

import os
import sys

# ANSI color codes (foreground) — used only when color is enabled.
_CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "red": "\033[38;5;203m",
    "green": "\033[38;5;114m",
    "yellow": "\033[38;5;221m",
    "blue": "\033[38;5;75m",
    "cyan": "\033[38;5;80m",
    "magenta": "\033[38;5;176m",
    "violet": "\033[38;5;141m",
    "orange": "\033[38;5;215m",
    "grey": "\033[38;5;245m",
    "white": "\033[38;5;255m",
}

# Eighth-block characters for sub-character bar precision.
_EIGHTHS = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]
_FULL = "█"


def _enable_windows_vt() -> bool:
    """Try to enable ANSI/VT processing on a Windows console. Return success."""
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        # -11 = STD_OUTPUT_HANDLE; mode 7 enables VT processing.
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


def _detect_unicode() -> bool:
    try:
        enc = sys.stdout.encoding or "ascii"
        return enc.lower().replace("-", "") not in ("ascii", "latin1", "cp1252")
    except Exception:
        return False


def _detect_color() -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return _enable_windows_vt()


class Style:
    """Holds the enabled/disabled flags and the drawing helpers."""

    def __init__(self) -> None:
        self.unicode = _detect_unicode()
        self.color = _detect_color()
        # Box-drawing set (Unicode or ASCII fallback).
        if self.unicode:
            self.tl, self.tr, self.bl, self.br = "╭", "╮", "╰", "╯"
            self.h, self.v = "─", "│"
            self.lt, self.rt = "├", "┤"
            self.dot = "●"
            self.circle = "○"
            self.arrow = "→"
            self.bullet = "•"
        else:
            self.tl = self.tr = self.bl = self.br = "+"
            self.h, self.v = "-", "|"
            self.lt = self.rt = "+"
            self.dot = "*"
            self.circle = "o"
            self.arrow = "->"
            self.bullet = "-"

    # ---- color ---------------------------------------------------------- #

    def c(self, text: str, *styles: str) -> str:
        """Wrap ``text`` in the given styles (e.g. ``S.c("hi", "bold", "cyan")``)."""
        if not self.color or not styles:
            return text
        prefix = "".join(_CODES.get(s, "") for s in styles)
        return f"{prefix}{text}{_CODES['reset']}"

    # ---- bars ----------------------------------------------------------- #

    def bar(self, fraction: float, width: int, *styles: str) -> str:
        """Return a bar of ``width`` cells representing ``fraction`` in [0,1].

        Uses eighth-block characters for sub-cell precision when Unicode is
        available; falls back to '#'/'-' otherwise.
        """
        fraction = max(0.0, min(1.0, fraction))
        if not self.unicode:
            filled = int(round(fraction * width))
            return self.c("#" * filled, *styles) + " " * (width - filled)
        total_eighths = int(round(fraction * width * 8))
        full = total_eighths // 8
        rem = total_eighths % 8
        s = _FULL * full
        if rem:
            s += _EIGHTHS[rem]
        pad = width - len(s)
        return self.c(s, *styles) + self.c(" " * max(0, pad), "grey")

    # ---- boxes ---------------------------------------------------------- #

    def _visible_len(self, text: str) -> int:
        """Length of text ignoring ANSI escape sequences."""
        out, i = 0, 0
        while i < len(text):
            if text[i] == "\033":
                j = text.find("m", i)
                if j != -1:
                    i = j + 1
                    continue
            out += 1
            i += 1
        return out

    def frame(self, lines, title: str = "", width: int = 66, title_style=("bold", "cyan")) -> str:
        """Box a list of already-rendered lines with an optional title."""
        top = self.tl + self.h * 2
        if title:
            t = self.c(f" {title} ", *title_style)
            # Between the corners we want exactly `width` cells:
            #   2 (leading h) + visible(title) + fill = width
            top += t + self.h * max(0, width - 2 - self._visible_len(t))
        else:
            top += self.h * (width - 2)
        top += self.tr
        out = [self.c(top, "grey") if False else top]
        for ln in lines:
            pad = width - 1 - self._visible_len(ln)
            out.append(f"{self.v} {ln}{' ' * max(0, pad)}{self.v}")
        out.append(self.bl + self.h * width + self.br)
        return "\n".join(out)


# Module-level singleton.
S = Style()
