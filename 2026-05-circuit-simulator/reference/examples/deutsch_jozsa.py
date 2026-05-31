"""Deutsch-Jozsa Algorithm — qcsim example.

Determines whether a black-box function f: {0,1}^n -> {0,1} is
constant (same output for all inputs) or balanced (outputs 0 for
exactly half, 1 for the other half) in a SINGLE quantum query.

Classically this requires up to 2^(n-1)+1 queries in the worst case.

Run: python examples/deutsch_jozsa.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qcsim import QuantumCircuit, draw_histogram, banner


# ================================================================== #
#  Oracle builders
# ================================================================== #

def constant_oracle(qc: QuantumCircuit, input_qubits: list, ancilla: int,
                    output: int) -> None:
    """Oracle for constant function f(x) = output (0 or 1).

    If output == 1: flip the ancilla (X gate).
    If output == 0: do nothing.

    Args:
        qc: Circuit to modify in-place.
        input_qubits: Input register qubit indices (unused for constant f).
        ancilla: Ancilla qubit index.
        output: Constant output value (0 or 1).
    """
    if output == 1:
        qc.x(ancilla)
    qc.barrier(label=f"Oracle: f(x)={output} (constant)")


def balanced_oracle(qc: QuantumCircuit, input_qubits: list, ancilla: int) -> None:
    """Oracle for the balanced function f(x) = x_0 XOR x_1 XOR ...

    Implemented as CNOT from each input qubit to the ancilla.

    Args:
        qc: Circuit to modify in-place.
        input_qubits: Input register qubit indices.
        ancilla: Ancilla qubit index.
    """
    for q in input_qubits:
        qc.cnot(q, ancilla)
    qc.barrier(label="Oracle: f(x)=x0 XOR... (balanced)")


# ================================================================== #
#  Deutsch-Jozsa circuit
# ================================================================== #

def deutsch_jozsa(n_input: int, oracle_type: str = "balanced") -> QuantumCircuit:
    """Build the Deutsch-Jozsa circuit.

    Args:
        n_input: Number of input qubits.
        oracle_type: 'constant0', 'constant1', or 'balanced'.

    Returns:
        QuantumCircuit after full algorithm.
    """
    n_total = n_input + 1
    ancilla = n_total - 1
    input_qubits = list(range(n_input))

    qc = QuantumCircuit(n_total)

    # Step 1: Prepare ancilla in |−⟩ = X|0⟩ → H|1⟩
    qc.x(ancilla)
    qc.barrier()

    # Step 2: Apply H to all qubits
    for q in range(n_total):
        qc.h(q)
    qc.barrier(label="After H layer")

    # Step 3: Oracle
    if oracle_type == "constant0":
        constant_oracle(qc, input_qubits, ancilla, output=0)
    elif oracle_type == "constant1":
        constant_oracle(qc, input_qubits, ancilla, output=1)
    else:
        balanced_oracle(qc, input_qubits, ancilla)

    # Step 4: Apply H to input register only
    for q in input_qubits:
        qc.h(q)
    qc.barrier(label="After final H")

    return qc


def classify(counts: dict, n_input: int) -> str:
    """Classify the oracle as constant or balanced from measurement.

    If all input qubits measure |0⟩, the function is constant.
    Otherwise it is balanced.

    Args:
        counts: Measurement counts from measure_all().
        n_input: Number of input qubits.

    Returns:
        'constant' or 'balanced'.
    """
    # Input register is qubits 0..n_input-1 (LSB: rightmost n_input bits)
    all_zero = "0" * n_input
    for bitstring, cnt in counts.items():
        if cnt == 0:
            continue
        input_bits = bitstring[-n_input:]  # rightmost n_input bits = input register
        if input_bits != all_zero:
            return "balanced"
    return "constant"


# ================================================================== #
#  Main
# ================================================================== #

def main():
    print(banner())
    print()
    print("  Deutsch-Jozsa Algorithm")
    print("  " + "=" * 40)
    print()

    for oracle_type, expected in [
        ("constant0", "constant"),
        ("constant1", "constant"),
        ("balanced",  "balanced"),
    ]:
        print(f"  Oracle: {oracle_type}  (expected: {expected})")
        print()

        qc = deutsch_jozsa(n_input=3, oracle_type=oracle_type)
        print(qc.draw())
        print()

        counts = qc.measure_all(shots=1024)
        print(draw_histogram(counts, shots=1024))
        print()

        result = classify(counts, n_input=3)
        status = "PASS" if result == expected else "FAIL"
        print(f"  Result: {result}  [{status}]")
        print()
        print("  " + "-" * 50)
        print()


if __name__ == "__main__":
    main()
