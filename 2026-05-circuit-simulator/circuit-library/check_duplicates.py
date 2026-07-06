#!/usr/bin/env python3
"""
check_duplicates.py — CI gate for the circuit library.

Run by GitHub Actions on every PR that touches circuit-library/.
Exits non-zero if any two circuits share the same fingerprint.

Usage:
    python circuit-library/check_duplicates.py

Also validates that every file listed in index.json actually exists.
"""

import json
import sys
from pathlib import Path

LIBRARY_DIR = Path(__file__).parent
INDEX_FILE = LIBRARY_DIR / "index.json"


def main():
    errors = []

    if not INDEX_FILE.exists():
        print("ERROR: circuit-library/index.json not found.")
        sys.exit(1)

    with open(INDEX_FILE) as f:
        index = json.load(f)

    circuits = index.get("circuits", [])
    print(f"Checking {len(circuits)} circuit(s)...\n")

    seen_fingerprints: dict[str, str] = {}  # fingerprint -> name
    seen_names: dict[str, str] = {}  # lower_name -> file

    for entry in circuits:
        name = entry.get("name", "?")
        fp = entry.get("fingerprint", "")
        file = entry.get("file", "")
        path = LIBRARY_DIR / file

        # ── File exists ──
        if not path.exists():
            errors.append(f"MISSING FILE: '{file}' listed in index.json but not found on disk.")

        # ── No duplicate fingerprints ──
        if fp:
            if fp in seen_fingerprints:
                errors.append(
                    f"DUPLICATE CIRCUIT:\n"
                    f"  '{name}' ({file})\n"
                    f"  matches '{seen_fingerprints[fp]}'\n"
                    f"  Fingerprint: {fp}\n"
                    f"  These circuits have identical gate structures. "
                    f"Rename or change at least one gate position."
                )
            else:
                seen_fingerprints[fp] = name

        # ── No duplicate names (case-insensitive) ──
        lower = name.lower().strip()
        if lower in seen_names:
            errors.append(
                f"DUPLICATE NAME: '{name}' ({file}) conflicts with '{seen_names[lower]}'."
            )
        else:
            seen_names[lower] = file

        # ── Validate JSON fields ──
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                required = {"name", "num_qubits", "num_cols", "backend", "gates"}
                missing = required - set(data.keys())
                if missing:
                    errors.append(
                        f"INVALID FORMAT: '{file}' missing fields: {', '.join(sorted(missing))}"
                    )
            except json.JSONDecodeError as e:
                errors.append(f"INVALID JSON: '{file}' — {e}")

    # ── Report ──
    if errors:
        print(f"FAILED — {len(errors)} error(s):\n")
        for err in errors:
            print(f"  {err}\n")
        sys.exit(1)
    else:
        print(f"OK — {len(circuits)} circuit(s), no duplicates, all files present.")
        sys.exit(0)


if __name__ == "__main__":
    main()
