"""Build a custom noise model and measure with readout error.

Run:  python examples/custom_model.py
"""

from qcsim import QuantumCircuit
from qnoise import (
    AmplitudeDamping,
    Depolarizing,
    NoiseModel,
    run,
    run_ideal,
    sample,
)


def main() -> None:
    qc = QuantumCircuit(3)
    qc.h(0).cnot(0, 1).cnot(1, 2)  # GHZ(3)

    # Hand-built model: light 1-qubit depolarizing, heavier on CNOT, some T1,
    # plus classical readout error.
    nm = (
        NoiseModel()
        .add_channel(Depolarizing(0.002), gates=["H"])
        .add_channel(Depolarizing(0.02), gates=["CNOT"])
        .add_channel(AmplitudeDamping(0.005))
        .add_readout_error(p1_given_0=0.01, p0_given_1=0.03)
    )

    ideal = run_ideal(qc)
    noisy = run(qc, nm)

    print("GHZ(3) with a custom noise model\n")
    print("  ideal :", {k: round(v, 3) for k, v in ideal.probabilities_dict().items()})
    print("  noisy :", {k: round(v, 3) for k, v in noisy.probabilities_dict().items()})
    print("\n  sampled (2000 shots, with readout error):")
    counts = sample(noisy, shots=2000, readout_error=nm.readout_error, seed=0)
    for bitstring in sorted(counts):
        print(f"    {bitstring}: {counts[bitstring]}")


if __name__ == "__main__":
    main()
