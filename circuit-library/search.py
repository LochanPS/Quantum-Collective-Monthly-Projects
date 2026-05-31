#!/usr/bin/env python3
"""
search.py — Search the Quantum Collective circuit library.

Usage:
    python circuit-library/search.py
    python circuit-library/search.py ghz
    python circuit-library/search.py --tags entanglement
    python circuit-library/search.py --qubits 3
    python circuit-library/search.py bell --load
    python circuit-library/search.py --list-tags
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# ── Find library root ──────────────────────────────────────────────────────

def _find_library_dir() -> Path:
    """Locate circuit-library/ directory.

    Searches in order:
    1. QCSIM_LIBRARY_PATH env var
    2. Directory of this script
    3. Parent directories up to 3 levels
    """
    env = os.environ.get("QCSIM_LIBRARY_PATH")
    if env:
        p = Path(env)
        if p.exists() and (p / "index.json").exists():
            return p

    # Start from this script's location
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent, here.parent.parent.parent]:
        idx = candidate / "circuit-library" / "index.json"
        if idx.exists():
            return idx.parent
        # Maybe we are already inside circuit-library/
        if (candidate / "index.json").exists():
            return candidate

    raise FileNotFoundError(
        "Could not find circuit-library/index.json. "
        "Run from the repo root or set QCSIM_LIBRARY_PATH."
    )


# ── Core search ────────────────────────────────────────────────────────────

def load_index(library_dir: Path) -> List[dict]:
    """Load and return all circuit entries from index.json."""
    idx_file = library_dir / "index.json"
    with open(idx_file) as f:
        data = json.load(f)
    return data.get("circuits", [])


def search_circuits(
    circuits: List[dict],
    query: Optional[str] = None,
    tags: Optional[List[str]] = None,
    qubits: Optional[int] = None,
    author: Optional[str] = None,
) -> List[dict]:
    """Filter circuits by query, tags, qubit count, or author.

    Args:
        circuits: Full list from index.json.
        query: Substring match against circuit name (case-insensitive).
        tags: All specified tags must be present.
        qubits: Exact qubit count match.
        author: Substring match against author field.

    Returns:
        Filtered list of circuit dicts.
    """
    results = circuits

    if query:
        q = query.lower()
        results = [c for c in results if q in c.get("name", "").lower()]

    if tags:
        for tag in tags:
            t = tag.lower()
            results = [c for c in results if t in [x.lower() for x in c.get("tags", [])]]

    if qubits is not None:
        results = [c for c in results if c.get("num_qubits") == qubits]

    if author:
        a = author.lower()
        results = [c for c in results if a in c.get("author", "").lower()]

    return results


def list_all_tags(circuits: List[dict]) -> List[str]:
    """Return sorted unique list of all tags in the library."""
    tags: set[str] = set()
    for c in circuits:
        tags.update(c.get("tags", []))
    return sorted(tags)


# ── Display ────────────────────────────────────────────────────────────────

def _col(text: str, width: int) -> str:
    """Left-justify text in a fixed-width column, truncating if needed."""
    text = str(text)
    if len(text) > width:
        text = text[:width - 2] + ".."
    return text.ljust(width)


def print_results(circuits: List[dict], library_dir: Path, verbose: bool = False):
    """Print search results as a formatted table."""
    if not circuits:
        print("  No circuits found.")
        return

    print()
    hdr = (
        f"  {'#':<4} "
        f"{'Name':<30} "
        f"{'Qubits':<7} "
        f"{'Tags':<30} "
        f"{'Author':<20} "
        f"{'File'}"
    )
    sep = "  " + "-" * (len(hdr) - 2)
    print(hdr)
    print(sep)

    for i, c in enumerate(circuits, start=1):
        tags_str = ", ".join(c.get("tags", []))
        row = (
            f"  {i:<4} "
            f"{_col(c.get('name', '?'), 30)} "
            f"{_col(c.get('num_qubits', '?'), 7)} "
            f"{_col(tags_str, 30)} "
            f"{_col(c.get('author', '?'), 20)} "
            f"{c.get('file', '?')}"
        )
        print(row)

        if verbose:
            desc = c.get("description", "")
            if desc:
                print(f"       {desc}")
            fp = c.get("fingerprint", "")
            if fp:
                print(f"       Fingerprint: {fp}")
            print()

    print(sep)
    print(f"  {len(circuits)} result(s)  |  Library: {library_dir}")
    print()


# ── Load a circuit ─────────────────────────────────────────────────────────

def load_circuit(circuit_entry: dict, library_dir: Path) -> dict:
    """Load and return the full JSON data for a circuit."""
    rel = circuit_entry.get("file", "")
    path = library_dir / rel
    if not path.exists():
        raise FileNotFoundError(f"Circuit file not found: {path}")
    with open(path) as f:
        return json.load(f)


def launch_tui_with_circuit(circuit_path: Path):
    """Launch the qcsim interactive TUI with a pre-loaded circuit."""
    try:
        subprocess.run(
            [sys.executable, "-m", "qcsim.tui", "--load", str(circuit_path)],
            check=True,
        )
    except FileNotFoundError:
        print("  qcsim not found. Install with: pip install -e reference/")
    except KeyboardInterrupt:
        pass


# ── Interactive picker ─────────────────────────────────────────────────────

def interactive_pick(circuits: List[dict], library_dir: Path, do_load: bool = False):
    """Let user pick a circuit from results by number."""
    if len(circuits) == 1:
        choice = 1
    else:
        try:
            raw = input("  Pick a number to inspect (or Enter to skip): ").strip()
        except EOFError:
            return
        if not raw:
            return
        try:
            choice = int(raw)
        except ValueError:
            return

    if not (1 <= choice <= len(circuits)):
        print("  Invalid choice.")
        return

    entry = circuits[choice - 1]
    try:
        data = load_circuit(entry, library_dir)
    except FileNotFoundError as e:
        print(f"  {e}")
        return

    print()
    print(f"  Name    : {data.get('name')}")
    print(f"  Qubits  : {data.get('num_qubits')}")
    print(f"  Cols    : {data.get('num_cols')}")
    print(f"  Backend : {data.get('backend')}")
    print(f"  Gates   : {len(data.get('gates', []))}")
    desc = data.get("description", "")
    if desc:
        print(f"  About   : {desc}")
    print(f"  File    : {library_dir / entry['file']}")
    print()

    if do_load:
        circuit_path = library_dir / entry["file"]
        print(f"  Opening in qcsim interactive builder...")
        launch_tui_with_circuit(circuit_path)
    else:
        try:
            ans = input("  Open in qcsim interactive builder? [y/N]: ").strip().lower()
        except EOFError:
            ans = ""
        if ans == "y":
            circuit_path = library_dir / entry["file"]
            launch_tui_with_circuit(circuit_path)


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="qcsim-search",
        description="Search the Quantum Collective circuit library.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python circuit-library/search.py
  python circuit-library/search.py ghz
  python circuit-library/search.py --tags entanglement beginner
  python circuit-library/search.py --qubits 3
  python circuit-library/search.py bell --load
  python circuit-library/search.py --list-tags
        """,
    )
    parser.add_argument("query", nargs="?", help="Name search (case-insensitive substring).")
    parser.add_argument("--tags", nargs="+", metavar="TAG", help="Filter by tags (all must match).")
    parser.add_argument("--qubits", type=int, metavar="N", help="Filter by exact qubit count.")
    parser.add_argument("--author", metavar="NAME", help="Filter by author (substring).")
    parser.add_argument("--load", action="store_true", help="Load selected circuit into qcsim TUI.")
    parser.add_argument("--list-tags", action="store_true", help="List all available tags.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show descriptions and fingerprints.")

    args = parser.parse_args()

    try:
        library_dir = _find_library_dir()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    all_circuits = load_index(library_dir)

    if args.list_tags:
        tags = list_all_tags(all_circuits)
        print(f"\n  Tags in library ({len(tags)} total):\n")
        for t in tags:
            count = sum(1 for c in all_circuits if t in c.get("tags", []))
            print(f"    {t:<25} ({count} circuit(s))")
        print()
        return

    if not any([args.query, args.tags, args.qubits, args.author]):
        # No filters → show all
        results = all_circuits
        print(f"\n  All circuits in library ({len(results)} total):")
    else:
        results = search_circuits(
            all_circuits,
            query=args.query,
            tags=args.tags,
            qubits=args.qubits,
            author=args.author,
        )
        print(f"\n  Search results ({len(results)} found):")

    print_results(results, library_dir, verbose=args.verbose)

    if results:
        interactive_pick(results, library_dir, do_load=args.load)


if __name__ == "__main__":
    main()
