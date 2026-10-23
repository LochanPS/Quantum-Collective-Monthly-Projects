"""Fidelity decay curve — sweep depolarizing rate on a GHZ state.

Run:  python examples/noise_sweep.py
"""

from qnoise import Depolarizing, sweep
from qnoise.demos import ghz3


def main() -> None:
    qc = ghz3()
    print("GHZ(3) — fidelity vs depolarizing rate\n")
    print("  rate    fidelity  purity  TVD    bar")
    for pt in sweep(qc, Depolarizing, [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]):
        bar = "#" * int(round(pt.fidelity * 30))  # ASCII so it prints on any console
        print(f"  {pt.rate:4.2f}    {pt.fidelity:6.3f}   {pt.purity:5.3f}  {pt.tvd:5.3f}  {bar}")


if __name__ == "__main__":
    main()
