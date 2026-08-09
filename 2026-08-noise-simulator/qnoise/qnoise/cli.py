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
from .render import compare, measurement_panel, metrics_panel
from .style import S


def banner() -> str:
    """Colored startup banner."""
    art = [
        r"  __ _ _ __   ___  (_)___  ___ ",
        r" / _` | '_ \ / _ \ | / __|/ _ \\",
        r"| (_| | | | | (_) || \__ \  __/",
        r" \__, |_| |_|\___/ |_|___/\___|",
        r" |_|",
    ]
    art = [S.c(line, "violet", "bold") for line in art]
    art[0] += S.c("   Noisy Quantum Simulator", "white", "bold")
    art[1] += S.c("   Quantum Collective  ·  Project #3", "grey")
    art[2] += S.c("   ideal " + S.arrow + " noisy " + S.arrow + " (someday) corrected", "cyan")
    return "\n" + "\n".join(art) + "\n"


# Kept as a module attribute for callers/tests that reference it.
BANNER = banner()

#: Named noise-model builders offered in the menu.
MODELS = {
    "ideal": ("no noise (sanity check)", presets.ideal),
    "light": ("1% depolarizing everywhere", presets.light),
    "ibm_ish": ("superconducting-ish + readout error", presets.ibm_ish),
    "ion_ish": ("trapped-ion-ish (very low error)", presets.ion_ish),
}

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

    counts = sample(noisy, shots=shots, readout_error=noise_model.readout_error, seed=seed)

    blocks = [
        compare(di, dn),
        metrics_panel(
            fidelity(ideal, noisy),
            trace_distance(ideal, noisy),
            tvd(di, dn),
            ideal.purity(),
            noisy.purity(),
            noisy.dim,
        ),
        measurement_panel(counts, shots, has_readout=noise_model.readout_error is not None),
    ]
    return "\n\n".join(blocks)


def sweep_report(
    qc: QuantumCircuit,
    rates: List[float],
) -> str:
    """Fidelity vs. depolarizing rate — the decoherence decay curve as a panel."""
    ideal = run_ideal(qc)
    lines = [
        f"{S.c('rate', 'grey', 'bold')}   {S.c('fidelity', 'grey', 'bold')}   "
        f"{S.c('decay curve', 'grey', 'bold')}",
        S.c(S.h * 38, "grey"),
    ]
    for p in rates:
        noisy = run(qc, presets.depolarizing(p))
        f = fidelity(ideal, noisy)
        styles = ("green",) if f >= 0.9 else ("yellow",) if f >= 0.7 else ("red",)
        bar = S.bar(f, 22, *styles)
        lines.append(f"{p:5.3f}   {S.c(f'{f:6.3f}', *styles)}   {bar}")
    return S.frame(lines, title="DEPOLARIZING SWEEP", width=42,
                   title_style=("bold", "orange"))


# --------------------------------------------------------------------------- #
#  interactive loop
# --------------------------------------------------------------------------- #

def _prompt(msg: str, default: str) -> str:
    # NOTE: EOF (no more input, e.g. piped/closed stdin) propagates so the main
    # loop exits cleanly. Returning the default here would loop forever on the
    # "another run? [y]" prompt.
    raw = input(f"{msg} [{default}]: ").strip()
    return raw or default


_CIRCUIT_DESC = {
    "bell": "2-qubit Bell pair",
    "ghz3": "3-qubit GHZ state",
    "ghz4": "4-qubit GHZ state",
    "plus": "3 independent |+> qubits",
    "grover2": "2-qubit Grover search",
}


def _choose_circuit() -> QuantumCircuit:
    lines = []
    for name in DEMOS:
        lines.append(f"{S.c(name.ljust(9), 'cyan', 'bold')} {S.c(_CIRCUIT_DESC.get(name, ''), 'grey')}")
    print()
    print(S.frame(lines, title="CIRCUITS", width=42, title_style=("bold", "cyan")))
    name = _prompt(S.c("  pick a circuit", "bold"), "bell")
    if name not in DEMOS:
        print(S.c(f"  unknown circuit {name!r}, using bell", "yellow"))
        name = "bell"
    return build_circuit(name)


def _choose_model() -> NoiseModel:
    lines = []
    for key, (desc, _) in MODELS.items():
        lines.append(f"{S.c(key.ljust(9), 'green', 'bold')} {S.c(desc, 'grey')}")
    lines.append(f"{S.c('depol'.ljust(9), 'green', 'bold')} {S.c('custom depolarizing rate', 'grey')}")
    print()
    print(S.frame(lines, title="NOISE MODELS", width=48, title_style=("bold", "green")))
    name = _prompt(S.c("  pick a noise model", "bold"), "light")
    if name == "depol":
        p = float(_prompt(S.c("  depolarizing rate p", "bold"), "0.05"))
        return build_model("depol", p)
    if name not in MODELS:
        print(S.c(f"  unknown model {name!r}, using light", "yellow"))
        name = "light"
    return build_model(name)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the ``qnoise-run`` console script."""
    print(banner())
    print(S.c("  See what a circuit actually does on a noisy device.", "white"))
    print(S.c(f"  {S.bullet} Ctrl-C or 'q' at any prompt to quit.", "grey"))
    try:
        while True:
            qc = _choose_circuit()
            nm = _choose_model()
            shots = int(_prompt(S.c("  shots", "bold"), "1024"))
            print()
            print(run_report(qc, nm, shots=shots))
            if _prompt("\n  " + S.c("run a depolarizing sweep?", "bold") + " (y/n)", "n") == "y":
                print()
                print(sweep_report(qc, [0.0, 0.01, 0.05, 0.1, 0.2, 0.4]))
            if _prompt("\n  " + S.c("another run?", "bold") + " (y/n)", "y") != "y":
                break
    except (KeyboardInterrupt, EOFError):
        pass
    print(S.c("\n  bye " + S.arrow + " keep the qubits cold.", "violet"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
