"""Terminal rendering — colored, framed ideal-vs-noisy views.

All output degrades gracefully on plain / non-color / ASCII terminals via the
shared :mod:`qnoise.style` helpers.
"""

from __future__ import annotations

from typing import Dict, List

from .style import S

_BAR_W = 16


def _pct(p: float) -> str:
    return f"{p * 100:5.1f}%"


def _fidelity_styles(f: float):
    if f >= 0.9:
        return ("green",)
    if f >= 0.7:
        return ("yellow",)
    return ("red",)


def compare(
    ideal: Dict[str, float],
    noisy: Dict[str, float],
    threshold: float = 1e-4,
    title: str = "IDEAL vs NOISY",
) -> str:
    """Framed, colored side-by-side of the ideal and noisy distributions.

    Bars in the ideal column are cyan. In the noisy column, outcomes that are
    *supposed* to appear (nonzero in the ideal) are green; leakage outcomes
    (near-zero in the ideal but present under noise) are red — so noise pops.
    """
    keys = sorted(
        k for k in set(ideal) | set(noisy)
        if ideal.get(k, 0.0) > threshold or noisy.get(k, 0.0) > threshold
    )

    # Build header manually for alignment (visible widths).
    lines: List[str] = []
    header = (
        S.c(" st ", "grey")
        + "  " + S.c("ideal".ljust(_BAR_W + 7), "cyan", "bold")
        + "  " + S.c("noisy", "white", "bold")
    )
    lines.append(header)
    lines.append(S.c(S.h * (_BAR_W * 2 + 24), "grey"))

    for k in keys:
        ip = ideal.get(k, 0.0)
        np_ = noisy.get(k, 0.0)
        is_leak = ip <= threshold and np_ > threshold
        ideal_bar = S.bar(ip, _BAR_W, "cyan")
        noisy_styles = ("red",) if is_leak else ("green",)
        noisy_bar = S.bar(np_, _BAR_W, *noisy_styles)
        marker = S.c(" " + S.dot, "red") if is_leak else "  "
        left = f"{S.c(k, 'bold')}  {ideal_bar} {S.c(_pct(ip), 'grey')}"
        right = f"{noisy_bar} {S.c(_pct(np_), *noisy_styles)}{marker}"
        lines.append(f"{left}   {right}")

    return S.frame(lines, title=title, width=_BAR_W * 2 + 26)


def metrics_panel(
    fidelity: float,
    trace_distance: float,
    tvd: float,
    ideal_purity: float,
    noisy_purity: float,
    dim: int,
) -> str:
    """A framed panel: a fidelity gauge plus the drift numbers."""
    fstyles = _fidelity_styles(fidelity)
    gauge = S.bar(fidelity, 24, *fstyles)
    verdict = (
        "excellent" if fidelity >= 0.95
        else "good" if fidelity >= 0.9
        else "degraded" if fidelity >= 0.7
        else "severe"
    )
    lines = [
        f"{S.c('fidelity', 'bold')}  {gauge} {S.c(f'{fidelity:.3f}', *fstyles, )}  "
        f"{S.c('(' + verdict + ')', *fstyles)}",
        "",
        f"{S.c('trace distance', 'grey')}  {trace_distance:.3f}"
        f"     {S.c('TVD', 'grey')}  {tvd:.3f}",
        f"{S.c('purity', 'grey')}  {ideal_purity:.3f} {S.arrow} "
        f"{S.c(f'{noisy_purity:.3f}', 'magenta')}"
        f"   {S.c(f'(1.000 pure  {1 / dim:.3f} fully mixed)', 'dim', 'grey')}",
    ]
    return S.frame(lines, title="DRIFT FROM IDEAL", width=_BAR_W * 2 + 26,
                   title_style=("bold", "magenta"))


def measurement_panel(counts: Dict[str, int], shots: int, has_readout: bool) -> str:
    """A framed panel of the sampled measurement histogram."""
    title = f"SAMPLED · {shots} shots"
    if has_readout:
        title += " · readout error on"
    total = max(1, shots)
    lines: List[str] = []
    for bitstring in sorted(counts):
        frac = counts[bitstring] / total
        bar = S.bar(frac, _BAR_W + 6, "violet")
        lines.append(
            f"{S.c(bitstring, 'bold')}  {bar} {S.c(str(counts[bitstring]).rjust(5), 'white')}"
        )
    if not lines:
        lines = [S.c("(no counts)", "grey")]
    return S.frame(lines, title=title, width=_BAR_W * 2 + 26,
                   title_style=("bold", "violet"))


# Backwards-compatible one-line footer (still used by examples).
def metrics_footer(fidelity: float, trace_distance: float, tvd: float) -> str:
    fstyles = _fidelity_styles(fidelity)
    return (
        f"  {S.c('fidelity vs ideal:', 'bold')} {S.c(f'{fidelity:.3f}', *fstyles)}   "
        f"trace distance: {trace_distance:.3f}   TVD: {tvd:.3f}"
    )
