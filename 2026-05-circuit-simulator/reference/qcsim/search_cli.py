"""
qcsim-search entry point.
Delegates to circuit-library/search.py, finding it relative to the repo root.
"""

import sys
import os
from pathlib import Path


def main():
    """Entry point for qcsim-search command."""
    # Find circuit-library/search.py relative to this installed package
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent.parent / "circuit-library" / "search.py",  # repo source
        here.parent.parent / "circuit-library" / "search.py",
        Path.cwd() / "circuit-library" / "search.py",
    ]

    search_script = None
    for c in candidates:
        if c.exists():
            search_script = c
            break

    if search_script is None:
        print(
            "circuit-library/search.py not found.\n"
            "Run from the repo root or set QCSIM_LIBRARY_PATH to the circuit-library/ folder."
        )
        sys.exit(1)

    # Delegate: exec search.py with the same args
    import runpy
    sys.argv[0] = str(search_script)
    runpy.run_path(str(search_script), run_name="__main__")
