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

import datetime
import json
import os
import shutil
import sys
from pathlib import Path

# Use normalized fingerprint from qcsim if available, else fallback
try:
    # __file__ = .../2026-05-circuit-simulator/circuit-library/add_circuit.py
    # parent.parent = .../2026-05-circuit-simulator/
    sys.path.insert(0, str(Path(__file__).parent.parent / "qcsim"))
    from qcsim.fingerprint import compute as _fp_compute

    def _compute_fingerprint(gates, num_qubits):
        return _fp_compute(gates, num_qubits)

except ImportError:
    import hashlib, json as _json

    def _compute_fingerprint(gates, num_qubits):
        raw = _json.dumps(
            {
                "gates": sorted(gates, key=lambda g: (g.get("col", 0), g.get("row", 0))),
                "num_qubits": num_qubits,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


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
    return _compute_fingerprint(data.get("gates", []), data["num_qubits"])


def _load_canonical_tags() -> set:
    tags_file = LIBRARY_DIR / "tags.json"
    if not tags_file.exists():
        return set()
    with open(tags_file) as f:
        return set(json.load(f).get("tags", {}).keys())


VALID_CATEGORIES = {
    "entanglement",
    "algorithm",
    "education",
    "error-correction",
    "benchmark",
    "other",
}
VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}


def validate(data: dict) -> list:
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
    # Validate tags against canonical list
    canonical = _load_canonical_tags()
    if canonical:
        bad_tags = [t for t in data.get("tags", []) if t not in canonical]
        if bad_tags:
            errors.append(
                f"Unknown tags: {bad_tags}. "
                f"Valid tags listed in circuit-library/tags.json. "
                f"Open a PR to add new tags."
            )
    # Validate category and difficulty if present
    cat = data.get("category", "")
    if cat and cat not in VALID_CATEGORIES:
        errors.append(f"'category' must be one of: {sorted(VALID_CATEGORIES)}")
    diff = data.get("difficulty", "")
    if diff and diff not in VALID_DIFFICULTIES:
        errors.append(f"'difficulty' must be one of: {sorted(VALID_DIFFICULTIES)}")
    return errors


def _prompt_missing_metadata(data: dict) -> dict:
    """Interactively fill in missing metadata fields."""
    print("\n  Filling in missing metadata (press Enter to skip optional fields):\n")

    if not data.get("description"):
        v = input("  Description (what does this circuit do?): ").strip()
        if v:
            data["description"] = v

    if not data.get("category"):
        cats = sorted(VALID_CATEGORIES)
        print(f"  Categories: {', '.join(cats)}")
        v = input("  Category: ").strip().lower()
        if v in VALID_CATEGORIES:
            data["category"] = v

    if not data.get("difficulty"):
        diffs = sorted(VALID_DIFFICULTIES)
        print(f"  Difficulty: {', '.join(diffs)}")
        v = input("  Difficulty: ").strip().lower()
        if v in VALID_DIFFICULTIES:
            data["difficulty"] = v

    if not data.get("tags"):
        canonical = _load_canonical_tags()
        print(f"  Available tags: {', '.join(sorted(canonical))}")
        v = input("  Tags (comma-separated): ").strip()
        if v:
            data["tags"] = [t.strip() for t in v.split(",") if t.strip()]

    if not data.get("source_url"):
        v = input("  Source URL (paper, textbook, Wikipedia — optional): ").strip()
        if v:
            data["source_url"] = v

    # Auto-fill fields
    if not data.get("created_at"):
        data["created_at"] = datetime.date.today().isoformat()
    if not data.get("version"):
        data["version"] = "1.0"
    if not data.get("num_gates"):
        data["num_gates"] = sum(
            1 for g in data.get("gates", []) if g.get("gate") not in ("CNOT_T", "SWAP_B")
        )
    data["verified"] = False  # maintainer sets this to True after review

    return data


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_circuit.py <circuit.json>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"Error: file not found: {src}")
        sys.exit(1)

    # Load
    with open(src) as f:
        data = json.load(f)

    # Fill missing metadata interactively
    data = _prompt_missing_metadata(data)

    # Validate
    errors = validate(data)
    if errors:
        print("\nValidation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Compute normalized fingerprint
    fp = compute_fingerprint(data)
    data["fingerprint"] = fp

    # Load index and check for duplicates
    index = load_index()
    for existing in index["circuits"]:
        if existing.get("fingerprint") == fp:
            print(f"\nDuplicate detected!")
            print(f"  This circuit matches: {existing['name']} ({existing['file']})")
            print(f"  Fingerprint: {fp}")
            print(
                "\nIf your circuit is genuinely different (different algorithm, different approach),"
            )
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

    # Write updated data (with fingerprint + metadata) to destination
    with open(dest, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nAdded: {dest}")

    # Update index with full metadata
    index["circuits"].append(
        {
            "file": dest_rel,
            "name": data["name"],
            "num_qubits": data["num_qubits"],
            "num_gates": data.get("num_gates", 0),
            "category": data.get("category", ""),
            "difficulty": data.get("difficulty", ""),
            "tags": data.get("tags", []),
            "fingerprint": fp,
            "author": data.get("author", "unknown"),
            "created_at": data.get("created_at", ""),
            "version": data.get("version", "1.0"),
            "verified": data.get("verified", False),
        }
    )
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
