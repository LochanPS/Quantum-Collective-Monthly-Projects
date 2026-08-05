"""Phase 9/10 tests — CLI report builders and presets (no stdin)."""

import pytest

from qnoise import presets
from qnoise.cli import build_circuit, build_model, run_report, sweep_report
from qnoise.demos import DEMOS


@pytest.mark.parametrize("name", list(DEMOS))
def test_every_demo_builds_and_reports(name):
    qc = build_circuit(name)
    report = run_report(qc, presets.light(), shots=256, seed=0)
    assert "ideal" in report and "noisy" in report
    assert "fidelity vs ideal" in report
    assert "sampled measurement" in report


def test_ideal_model_report_has_unit_fidelity():
    qc = build_circuit("bell")
    report = run_report(qc, presets.ideal(), shots=128, seed=0)
    assert "fidelity vs ideal: 1.000" in report


def test_readout_error_mentioned_when_present():
    qc = build_circuit("plus")
    report = run_report(qc, presets.ibm_ish(), shots=256, seed=0)
    assert "with readout error" in report


def test_sweep_report_monotonic_fidelity_text():
    qc = build_circuit("bell")
    report = sweep_report(qc, [0.0, 0.1, 0.4])
    assert "fidelity vs rate" in report
    # rate 0.000 gives fidelity 1.000
    assert "0.000" in report and "1.000" in report
    first_row = [l for l in report.splitlines() if l.strip().startswith("0.000")][0]
    assert "1.000" in first_row


def test_build_model_names():
    assert build_model("ideal").readout_error is None
    assert build_model("ibm_ish").readout_error is not None
    assert build_model("depol", 0.1).channels_for("H")  # has a channel on H


def test_presets_ion_and_ibm_valid_on_ghz():
    qc = build_circuit("ghz3")
    for nm in (presets.ibm_ish(), presets.ion_ish()):
        from qnoise import run
        dm = run(qc, nm)
        assert dm.is_valid()
