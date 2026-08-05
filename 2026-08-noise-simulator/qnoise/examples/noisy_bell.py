"""Ideal vs. noisy Bell state — the headline example.

Run:  python examples/noisy_bell.py
"""

from qcsim import QuantumCircuit
from qnoise import run, run_ideal, presets, fidelity, trace_distance, tvd
from qnoise.render import compare, metrics_footer


def main() -> None:
    qc = QuantumCircuit(2)
    qc.h(0).cnot(0, 1)

    ideal = run_ideal(qc)
    noisy = run(qc, presets.depolarizing(0.05))

    di, dn = ideal.probabilities_dict(), noisy.probabilities_dict()
    print("Bell state — ideal vs depolarizing(p=0.05)\n")
    print(compare(di, dn))
    print()
    print(metrics_footer(fidelity(ideal, noisy), trace_distance(ideal, noisy), tvd(di, dn)))
    print(f"\n  purity: {ideal.purity():.3f} (ideal) -> {noisy.purity():.3f} (noisy)")


if __name__ == "__main__":
    main()
