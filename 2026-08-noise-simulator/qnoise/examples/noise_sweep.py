"""Fidelity decay curve — sweep depolarizing rate on a GHZ state.

Run:  python examples/noise_sweep.py
"""

from qnoise import run, run_ideal, presets, fidelity
from qnoise.demos import ghz3


def main() -> None:
    qc = ghz3()
    ideal = run_ideal(qc)
    print("GHZ(3) — fidelity vs depolarizing rate\n")
    print("  rate    fidelity  purity  bar")
    for p in [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]:
        noisy = run(qc, presets.depolarizing(p))
        f = fidelity(ideal, noisy)
        bar = "#" * int(round(f * 30))  # ASCII so it prints on any console
        print(f"  {p:4.2f}    {f:6.3f}   {noisy.purity():5.3f}  {bar}")


if __name__ == "__main__":
    main()
