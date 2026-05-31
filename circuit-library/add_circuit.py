#!/usr/bin/env python3
"""
add_circuit.py — Submit a circuit to the Quantum Collective library.

Usage:
    python add_circuit.py my-circuit.json

What it does:
    1. Validates the JSON format
    2. Checks for duplicate fingerprints (same circuit = rejected)
    3. Adds the circuit file to circuit-library/
    4. Updates index.json

After running, commit the new file + updated index.json and open a PR.

Fingerprint:
    SHA-256 hash of the canonical gate sequence + qubit count.
    Two circuits that place the same gates in the same positions are identical.
    Circuits that produce the same quantum state via different gate sequences
    are NOT considered duplicates by this check (that's intentional — different
    implementations of the same algorithm have educational value).
"""

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

LIBRARY_DIR = Path(__file__).parent
INDEX_FILE = LIBRARY_DIR / "index.json"

REQUIRED_FIELDS = {"name", "num_qubits", "num_cols", "backend", "gates"}


def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            return json.load(f)
    return {"circuits": []}


def save_index(index: dict):
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    print(f"  Updated index.json ({len(index['circuits'])} circuits total).")


def compute_fingerprint(data: dict) -> str:
    gates = sorted(data.get("gates", []), key=lambda g: (g["col"], g["row"]))
    raw = json.dumps(
        {"gates": gates, "num_qubits": data["num_qubits"]},
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def validate(data: dict) -> list[str]:
    errors = []
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append(f"Missing fields: {', '.join(sorted(missing))}")
    if not isinstance(data.get("gates"), list):
        errors.append("'gates' must be a list.")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errors.append("'name' must be a non-empty string.")
    if data.get("backend") not in ("kronecker", "tensor"):
        errors.append("'backend' must be 'kronecker' or 'tensor'.")
    n = data.get("num_qubits", 0)
    if not (1 <= n <= 20):
        errors.append("'num_qubits' must be between 1 and 20.")
    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_circuit.py <circuit.json>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"Error: file not found: {src}")
        sys.exit(1)

    # Load and validate
    with open(src) as f:
        data = json.load(f)

    errors = validate(data)
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Compute fingerprint
    fp = compute_fingerprint(data)
    data["fingerprint"] = fp

    # Load index and check for duplicates
    index = load_index()
    for existing in index["circuits"]:
        if existing.get("fingerprint") == fp:
            print(f"\nDuplicate detected!")
            print(f"  This circuit matches: {existing['name']} ({existing['file']})")
            print(f"  Fingerprint: {fp}")
            print("\nIf your circuit is genuinely different (different algorithm, different approach),")
            print("modify a gate position so the fingerprint differs, then resubmit.")
            sys.exit(1)

    # Determine destination
    safe_name = data["name"].lower().replace(" ", "-").replace("/", "-")
    dest_rel = f"{safe_name}.json"
    dest = LIBRARY_DIR / dest_rel

    # Avoid overwriting
    if dest.exists():
        stem = dest.stem
        i = 2
        while dest.exists():
            dest = LIBRARY_DIR / f"{stem}-{i}.json"
            dest_rel = dest.name
            i += 1

    # Copy file
    shutil.copy(src, dest)
    print(f"\nAdded: {dest}")

    # Update index
    index["circuits"].append({
        "file": dest_rel,
        "name": data["name"],
        "num_qubits": data["num_qubits"],
        "tags": data.get("tags", []),
        "fingerprint": fp,
        "author": data.get("author", "unknown"),
    })
    save_index(index)

    print(f"\nFingerprint : {fp}")
    print(f"Circuit     : {data['name']}")
    print(f"Qubits      : {data['num_qubits']}")
    print()
    print("Next steps:")
    print(f"  git add circuit-library/{dest_rel} circuit-library/index.json")
    print(f"  git commit -m 'feat(library): add {data['name']}'")
    print("  git push && open a PR")


if __name__ == "__main__":
    main()
