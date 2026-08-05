"""qnoise-run — interactive terminal front end.

Pick a demo circuit and a noise model, then see the ideal vs. noisy probability
distribution side by side, the drift metrics, and a sampled measurement
histogram (with optional readout error).

The heavy lifting lives in small pure functions (``run_report``, ``sweep_report``)
so the behaviour is testable without stdin.
"""

from __future__ import annotations

import sys
from typing import Dict, List, Optional, Tuple

from qcsim import QuantumCircuit

from . import model as presets
from .demos import DEMOS
from .engine import run, run_ideal
from .measure import sample
from .metrics import fidelity, trace_distance, tvd
from .model import NoiseModel
from .render import _BAR, compare, metrics_footer

BANNER = r"""
   __ _ _ __   ___ (_)___  ___
  / _` | '_ \ / _ \| / __|/ _ \    Noisy Quantum Simulator
 | (_| | | | | (_) | \__ \  __/    Quantum Collective — Project #3
  \__, |_| |_|\___/|_|___/\___|    ideal -> noisy -> (someday) corrected
     |_|
"""

#: Named noise-model builders offered in the menu.
MODELS = {
    "ideal": ("no noise (sanity check)", presets.ideal),
    "light": ("1% depolarizing everywhere", presets.light),
    "ibm_ish": ("superconducting-ish + readout error", presets.ibm_ish),
    "ion_ish": ("trapped-ion-ish (very low error)", presets.ion_ish),
}


def build_circuit(name: str) -> QuantumCircuit:
    """Return a fresh demo circuit by name."""
    return DEMOS[name]()


def build_model(name: str, p: float = 0.05) -> NoiseModel:
    """Return a noise model by name; ``depol`` uses the custom rate ``p``."""
    if name == "depol":
        return presets.depolarizing(p)
    return MODELS[name][1]()


def run_report(
    qc: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 1024,
    seed: Optional[int] = None,
) -> str:
    """Produce the full ideal-vs-noisy text report for one run."""
    ideal = run_ideal(qc)
    noisy = run(qc, noise_model)
    di = ideal.probabilities_dict()
    dn = noisy.probabilities_dict()

    lines = [compare(di, dn), ""]
    lines.append(
        metrics_footer(
            fidelity(ideal, noisy),
            trace_distance(ideal, noisy),
            tvd(di, dn),
        )
    )
    lines.append(
        f"  purity: ideal {ideal.purity():.3f} -> noisy {noisy.purity():.3f}"
        f"   (1.000 = pure, {1 / noisy.dim:.3f} = maximally mixed)"
    )

    counts = sample(noisy, shots=shots, readout_error=noise_model.readout_error, seed=seed)
    lines.append("")
    lines.append(f"  sampled measurement ({shots} shots"
                 + (", with readout error" if noise_model.readout_error else "")
                 + "):")
    for bitstring in sorted(counts):
        frac = counts[bitstring] / shots
        bar = _BAR * int(round(frac * 18))
        lines.append(f"    {bitstring}  {bar.ljust(18)} {counts[bitstring]:>5}")
    return "\n".join(lines)


def sweep_report(
    qc: QuantumCircuit,
    rates: List[float],
) -> str:
    """Fidelity vs. depolarizing rate — the decoherence decay curve as a table."""
    ideal = run_ideal(qc)
    lines = ["  depolarizing sweep — fidelity vs rate:", ""]
    lines.append("    rate     fidelity   purity   bar")
    for p in rates:
        noisy = run(qc, presets.depolarizing(p))
        f = fidelity(ideal, noisy)
        bar = _BAR * int(round(f * 20))
        lines.append(f"    {p:5.3f}    {f:6.3f}    {noisy.purity():5.3f}   {bar}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  interactive loop
# --------------------------------------------------------------------------- #

def _prompt(msg: str, default: str) -> str:
    try:
        raw = input(f"{msg} [{default}]: ").strip()
    except EOFError:
        return default
    return raw or default


def _choose_circuit() -> QuantumCircuit:
    print("\n  circuits: " + ", ".join(DEMOS))
    name = _prompt("  pick a circuit", "bell")
    if name not in DEMOS:
        print(f"  unknown circuit {name!r}, using bell")
        name = "bell"
    return build_circuit(name)


def _choose_model() -> NoiseModel:
    print("\n  noise models:")
    for key, (desc, _) in MODELS.items():
        print(f"    {key:10s} {desc}")
    print(f"    {'depol':10s} custom depolarizing rate")
    name = _prompt("  pick a noise model", "light")
    if name == "depol":
        p = float(_prompt("  depolarizing rate p", "0.05"))
        return build_model("depol", p)
    if name not in MODELS:
        print(f"  unknown model {name!r}, using light")
        name = "light"
    return build_model(name)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the ``qnoise-run`` console script."""
    print(BANNER)
    print("  See what a circuit actually does on a noisy device.")
    print("  Ctrl-C or 'q' at any prompt to quit.\n")
    try:
        while True:
            qc = _choose_circuit()
            nm = _choose_model()
            shots = int(_prompt("  shots", "1024"))
            print()
            print(run_report(qc, nm, shots=shots))
            if _prompt("\n  run a depolarizing sweep on this circuit? (y/n)", "n") == "y":
                print()
                print(sweep_report(qc, [0.0, 0.01, 0.05, 0.1, 0.2, 0.4]))
            if _prompt("\n  another run? (y/n)", "y") != "y":
                break
    except (KeyboardInterrupt, EOFError):
        print("\n  bye.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
