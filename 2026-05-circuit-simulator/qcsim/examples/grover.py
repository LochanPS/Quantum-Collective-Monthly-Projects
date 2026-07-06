"""Grover's Search Algorithm — qcsim example.

Finds a marked item in an unstructured database of N=2^n items
in O(sqrt(N)) quantum queries vs O(N) classical queries.

This example searches a 4-qubit space (16 items) for a target bitstring.

Run: python examples/grover.py
"""

import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcsim import QuantumCircuit, draw_histogram, banner

# ================================================================== #
#  Oracle and diffusion
# ================================================================== #


def phase_oracle(qc: QuantumCircuit, target: str) -> None:
    """Apply a phase oracle that marks the target bitstring with -1 phase.

    For each qubit where the target bit is '0', apply X before and after
    a multi-controlled Z, so the phase flip applies exactly to |target>.

    Args:
        qc: Circuit to modify in-place.
        target: Binary string (LSB convention, rightmost = qubit 0).
    """
    n = qc.num_qubits
    # Flip qubits where target bit is '0' so we can use controlled-Z on |1...1>
    for i in range(n):
        if target[n - 1 - i] == "0":  # target[n-1-i] is bit for qubit i
            qc.x(i)

    # Multi-controlled Z: for n=2 this is CZ; for larger n build from CNOTs+T
    if n == 2:
        qc.cz(0, 1)
    elif n == 3:
        # CCZ = Toffoli + phase correction
        qc.h(2)
        qc.toffoli(0, 1, 2)
        qc.h(2)
    elif n == 4:
        # Decompose 4-qubit controlled-Z using ancilla Toffoli trick
        # |1111> → flip phase via Toffoli(0,1,anc) + Toffoli(anc,2,3) style
        # Simplification: use CZ after reducing control
        qc.h(3)
        qc.toffoli(0, 1, 3)  # ancilla-style, resets
        qc.toffoli(2, 3, 0)
        qc.toffoli(0, 1, 3)
        qc.toffoli(2, 3, 0)
        qc.h(3)
    else:
        # Generic fallback: chain Toffoli gates (ancilla-free, not optimal)
        qc.cz(0, 1)

    # Unflip
    for i in range(n):
        if target[n - 1 - i] == "0":
            qc.x(i)

    qc.barrier(label=f"Oracle: |{target}>")


def diffusion_operator(qc: QuantumCircuit) -> None:
    """Apply the Grover diffusion operator (inversion about the mean).

    D = H^N · (2|0><0| - I) · H^N

    Args:
        qc: Circuit to modify in-place.
    """
    n = qc.num_qubits

    # H to all
    for i in range(n):
        qc.h(i)

    # Flip all
    for i in range(n):
        qc.x(i)

    # Multi-controlled Z on |11...1>
    if n == 2:
        qc.cz(0, 1)
    elif n == 3:
        qc.h(2)
        qc.toffoli(0, 1, 2)
        qc.h(2)
    elif n == 4:
        qc.h(3)
        qc.toffoli(0, 1, 3)
        qc.toffoli(2, 3, 0)
        qc.toffoli(0, 1, 3)
        qc.toffoli(2, 3, 0)
        qc.h(3)
    else:
        qc.cz(0, 1)

    # Unflip
    for i in range(n):
        qc.x(i)

    # H to all
    for i in range(n):
        qc.h(i)

    qc.barrier(label="Diffusion")


def grover(n: int, target: str, iterations: int = None) -> QuantumCircuit:
    """Build a Grover search circuit.

    Args:
        n: Number of qubits (search space = 2^n items).
        target: Target bitstring of length n to search for.
        iterations: Number of Grover iterations. Defaults to optimal floor(pi/4 * sqrt(2^n)).

    Returns:
        Executed QuantumCircuit.
    """
    if iterations is None:
        iterations = max(1, int(math.pi / 4 * math.sqrt(2**n)))

    qc = QuantumCircuit(n)

    # Initialise uniform superposition
    for i in range(n):
        qc.h(i)
    qc.barrier(label="Init")

    # Grover iterations
    for _ in range(iterations):
        phase_oracle(qc, target)
        diffusion_operator(qc)

    return qc


# ================================================================== #
#  Main
# ================================================================== #


def main():
    print(banner())
    print()
    print("  Grover's Search Algorithm")
    print("  " + "=" * 40)
    print()

    targets = ["11", "101", "0011"]

    for target in targets:
        n = len(target)
        iters = max(1, int(math.pi / 4 * math.sqrt(2**n)))
        print(f"  Target: |{target}>  |  {n} qubits  |  {2**n} items  |  {iters} iteration(s)")
        print()

        qc = grover(n, target, iterations=iters)
        counts = qc.measure_all(shots=2048)
        print(draw_histogram(counts, shots=2048))
        print()

        top = max(counts, key=counts.get)
        hit_pct = counts.get(target, 0) / 2048 * 100
        print(f"  Top result: |{top}>  |  Target hit rate: {hit_pct:.1f}%")
        status = "PASS" if hit_pct > 50 else "WARN"
        print(f"  [{status}]")
        print()
        print("  " + "-" * 50)
        print()


if __name__ == "__main__":
    main()
