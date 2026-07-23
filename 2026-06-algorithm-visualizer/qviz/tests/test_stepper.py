from __future__ import annotations

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qviz import step_through
from qviz.algorithms import bernstein_vazirani, deutsch_jozsa, grover, qft_algorithm
from qviz.interpret import interpret_state, nonzero_states, phase_label
from qviz.phases import current_segment_index, segments
from qviz.render import (
    render_execution_summary,
    render_measurement,
    render_phase_progress,
    render_progress_circuit,
    render_statevector,
    render_step,
    render_windowed_circuit,
    sample_measurements,
)

# ================================================================== #
#  Stepper correctness
# ================================================================== #


class TestStepper:
    def test_step_count_matches_non_barrier_gates(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        steps = step_through(qc)
        assert len(steps) == 2

    def test_final_step_matches_circuit_final_state(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        steps = step_through(qc)
        assert np.allclose(steps[-1].statevector, qc.statevector())

    def test_intermediate_step_is_not_final_state(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        steps = step_through(qc)
        # After H alone, q1 is untouched -- not yet entangled, differs from final
        assert not np.allclose(steps[0].statevector, qc.statevector())

    def test_step_indices_are_sequential(self):
        qc = QuantumCircuit(2)
        qc.h(0).x(1).cnot(0, 1)
        steps = step_through(qc)
        assert [s.index for s in steps] == [0, 1, 2]

    def test_barrier_does_not_produce_a_step(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.barrier()
        qc.x(0)
        steps = step_through(qc)
        assert len(steps) == 2
        assert [s.gate_name for s in steps] == ["H", "X"]

    def test_does_not_mutate_original_circuit(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        sv_before = qc.statevector().copy()
        step_through(qc)
        assert np.allclose(qc.statevector(), sv_before)

    def test_empty_circuit_yields_no_steps(self):
        qc = QuantumCircuit(1)
        assert step_through(qc) == []


# ================================================================== #
#  Rendering
# ================================================================== #


class TestRender:
    def test_render_statevector_returns_string(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        steps = step_through(qc)
        out = render_statevector(steps[-1])
        assert isinstance(out, str)
        assert "State Vector" in out

    def test_render_progress_circuit_grows_with_index(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        early = render_progress_circuit(qc, 0)
        late = render_progress_circuit(qc, 1)
        assert "1 gate(s)" in early
        assert "2 gate(s)" in late

    def test_render_step_includes_annotation(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        steps = step_through(qc)
        steps[0].annotation = "Test annotation"
        out = render_step(qc, steps[0])
        assert "Test annotation" in out


# ================================================================== #
#  Algorithm correctness
# ================================================================== #


class TestDeutschJozsa:
    def test_annotation_count_matches_gate_count(self):
        res = deutsch_jozsa(2, "balanced")
        assert len(res.annotations) == len(res.circuit._log)

    def test_constant_oracle_leaves_input_at_zero(self):
        res = deutsch_jozsa(2, "constant_0")
        probs = res.circuit.probabilities()
        # Input qubits are q0,q1 (rightmost 2 chars); should always read '00'
        assert all(state[-2:] == "00" for state in probs)

    def test_balanced_oracle_leaves_input_nonzero(self):
        res = deutsch_jozsa(2, "balanced")
        probs = res.circuit.probabilities()
        assert all(state[-2:] != "00" for state in probs)

    def test_summary_reports_constant(self):
        res = deutsch_jozsa(2, "constant_0")
        steps = step_through(res.circuit)
        assert "CONSTANT" in res.summary(steps[-1])

    def test_summary_reports_balanced(self):
        res = deutsch_jozsa(2, "balanced")
        steps = step_through(res.circuit)
        assert "BALANCED" in res.summary(steps[-1])

    def test_info_carries_oracle_type(self):
        res = deutsch_jozsa(2, "balanced")
        assert res.info["Oracle type"] == "balanced"

    def test_invalid_oracle_raises(self):
        with pytest.raises(ValueError):
            deutsch_jozsa(2, "not_a_real_oracle")


class TestBernsteinVazirani:
    def test_annotation_count_matches_gate_count(self):
        res = bernstein_vazirani("101")
        assert len(res.annotations) == len(res.circuit._log)

    def test_recovers_secret_with_certainty(self):
        res = bernstein_vazirani("101")
        probs = res.circuit.probabilities()
        # qcsim labels are q(n-1)...q0 (leftmost = highest qubit), so the
        # input substring reads secret bits in reverse order.
        assert all(state[-3:][::-1] == "101" for state in probs)

    def test_recovers_non_palindromic_secret(self):
        """'101' is a palindrome -- reversal bugs hide there. Use '100' to catch them."""
        res = bernstein_vazirani("100")
        probs = res.circuit.probabilities()
        assert all(state[-3:][::-1] == "100" for state in probs)

    def test_summary_recovers_non_palindromic_secret(self):
        res = bernstein_vazirani("100")
        steps = step_through(res.circuit)
        summary = res.summary(steps[-1])
        assert "100" in summary and "matches" in summary

    def test_invalid_secret_raises(self):
        with pytest.raises(ValueError):
            bernstein_vazirani("102")
        with pytest.raises(ValueError):
            bernstein_vazirani("")


class TestGrover:
    def test_annotation_count_matches_gate_count(self):
        res = grover("11")
        assert len(res.annotations) == len(res.circuit._log)

    def test_finds_marked_state(self):
        res = grover("11")
        assert res.circuit.probabilities().get("11", 0) > 0.99

    def test_finds_different_marked_state(self):
        res = grover("01")
        assert res.circuit.probabilities().get("01", 0) > 0.99

    def test_finds_asymmetric_marked_state_other_direction(self):
        """'01' and '10' are bit-reversals of each other."""
        res = grover("10")
        assert res.circuit.probabilities().get("10", 0) > 0.99

    def test_all_marked_states_are_found(self):
        for state in ("00", "01", "10", "11"):
            res = grover(state)
            probs = res.circuit.probabilities()
            assert probs.get(state, 0) > 0.99

    def test_multiple_iterations_still_returns_valid_distribution(self):
        res = grover("11", iterations=2)
        probs = res.circuit.probabilities()
        assert abs(sum(probs.values()) - 1.0) < 1e-9

    def test_probability_distribution_is_normalized(self):
        res = grover("11")
        probs = res.circuit.probabilities()
        assert abs(sum(probs.values()) - 1.0) < 1e-12

    def test_iteration_count_is_reported(self):
        res = grover("11", iterations=2)
        assert res.info["Iterations"] == "2"

    def test_search_register_definition(self):
        res = grover("11")
        assert res.registers["search"] == [0, 1]

    def test_summary_reports_found(self):
        res = grover("10")
        steps = step_through(res.circuit)
        assert "FOUND" in res.summary(steps[-1])

    def test_outcome_matches_marked_state(self):
        res = grover("01")
        steps = step_through(res.circuit)
        outcome = res.execution_summary(steps[-1])

        assert outcome.success
        assert outcome.expected == "01"

    @pytest.mark.parametrize(
        "state",
        ["", "0", "1", "000", "abc", "12", "2", "111"],
    )
    def test_invalid_marked_states_raise(self, state):
        with pytest.raises(ValueError):
            grover(state)

class TestQFT:
    def test_annotation_count_matches_gate_count(self):
        res = qft_algorithm(3, "101")
        assert len(res.annotations) == len(res.circuit._log)

    def test_returns_normalized_state(self):
        res = qft_algorithm(3)
        probs = res.circuit.probabilities()
        assert abs(sum(probs.values()) - 1.0) < 1e-9

    def test_annotations_mention_controlled_phase(self):
        res = qft_algorithm(3)
        assert any("Controlled-phase" in a for a in res.annotations)


# ================================================================== #
#  Interpretation
# ================================================================== #


class TestInterpret:
    def test_definite_state(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        steps = step_through(qc)
        assert "definitely" in interpret_state(steps[-1]).lower()

    def test_uniform_superposition(self):
        qc = QuantumCircuit(2)
        qc.h(0).h(1)
        steps = step_through(qc)
        assert "uniform" in interpret_state(steps[-1]).lower()

    def test_equal_superposition_subset(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)  # Bell: |00> + |11>
        steps = step_through(qc)
        text = interpret_state(steps[-1]).lower()
        assert "superposition of 2" in text

    def test_phase_label_pi(self):
        qc = QuantumCircuit(1)
        qc.x(0).z(0)  # Z|1> = -|1>, phase pi
        steps = step_through(qc)
        _, _, amp = nonzero_states(steps[-1])[0]
        assert phase_label(amp) == "pi"

    def test_nonzero_states_sorted_by_probability(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        steps = step_through(qc)
        probs = [p for _, p, _ in nonzero_states(steps[-1])]
        assert probs == sorted(probs, reverse=True)


# ================================================================== #
#  Rendering modes
# ================================================================== #


class TestRenderModes:
    def test_beginner_mode_hides_complex_numbers(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        steps = step_through(qc)
        out = render_statevector(steps[-1], mode="beginner")
        assert "chance" in out
        assert "i " not in out  # no imaginary component shown

    def test_hide_zeros_omits_zero_states(self):
        qc = QuantumCircuit(2)
        qc.x(0)  # only |01> populated
        steps = step_through(qc)
        out = render_statevector(steps[-1], hide_zeros=True)
        assert "hidden" in out

    def test_render_step_includes_interpretation(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        steps = step_through(qc)
        out = render_step(qc, steps[-1])
        assert "State:" in out


# ================================================================== #
#  Phases, registers, structured outcome
# ================================================================== #


class TestPhasesAndOutcome:
    def test_phases_align_with_gates(self):
        for build, args in [
            (deutsch_jozsa, (2, "balanced")),
            (bernstein_vazirani, ("100",)),
            (grover, ("10",)),
            (qft_algorithm, (3, "101")),
        ]:
            res = build(*args)
            steps = step_through(res.circuit)
            assert len(res.phases) == len(res.annotations) == len(steps)

    def test_segments_group_consecutive_phases(self):
        segs = segments(["A", "A", "B", "B", "B", "A"])
        assert segs == [("A", 0, 1), ("B", 2, 4), ("A", 5, 5)]

    def test_current_segment_index(self):
        segs = segments(["A", "A", "B", "B"])
        assert current_segment_index(segs, 0) == 0
        assert current_segment_index(segs, 3) == 1

    def test_grover_has_all_three_phases(self):
        res = grover("11")
        assert set(res.phases) == {"Preparation", "Oracle", "Diffusion"}

    def test_registers_split_input_and_ancilla(self):
        res = deutsch_jozsa(2, "balanced")
        assert res.registers["input"] == [0, 1]
        assert res.registers["ancilla"] == [2]

    def test_outcome_success_on_correct_run(self):
        for build, args in [
            (deutsch_jozsa, (2, "constant_0")),
            (bernstein_vazirani, ("100",)),
            (grover, ("10",)),
        ]:
            res = build(*args)
            steps = step_through(res.circuit)
            es = res.execution_summary(steps[-1])
            assert es.success, f"{res.title} outcome not success"

    def test_dj_outcome_matches_oracle_class(self):
        res = deutsch_jozsa(2, "constant_1")
        steps = step_through(res.circuit)
        es = res.execution_summary(steps[-1])
        assert es.expected == "CONSTANT" and es.measured == "CONSTANT"


# ================================================================== #
#  Redesign rendering: progress, windowed circuit, measurement, summary
# ================================================================== #


class TestRedesignRendering:
    def test_phase_progress_marks_current(self):
        res = grover("11")
        steps = step_through(res.circuit)
        out = render_phase_progress(res.phases, len(steps) - 1)
        assert "Diffusion" in out  # last step is in the diffusion phase

    def test_windowed_circuit_narrower_than_full(self):
        res = grover("11", iterations=2)
        full = render_progress_circuit(res.circuit, len(res.phases) - 1)
        # a single-phase window should be no wider than the full circuit
        window = render_windowed_circuit(res.circuit, 0, 1)
        assert max(len(l) for l in window.splitlines()) <= max(len(l) for l in full.splitlines())

    def test_sample_measurements_totals_shots(self):
        res = grover("10")
        steps = step_through(res.circuit)
        counts = sample_measurements(steps[-1], res.registers["search"], shots=50)
        assert sum(counts.values()) == 50

    def test_measurement_projects_to_marked_state(self):
        res = grover("10")
        steps = step_through(res.circuit)
        counts = sample_measurements(steps[-1], res.registers["search"], shots=50)
        # Deterministic |10> final state -> every shot reads "10"
        assert counts == {"10": 50}

    def test_execution_summary_reports_success(self):
        res = bernstein_vazirani("100")
        steps = step_through(res.circuit)
        out = render_execution_summary(res, steps[-1])
        assert "Execution Summary" in out
        assert "SUCCESS" in out
        assert "100" in out

    def test_measurement_stage_renders(self):
        res = grover("11")
        steps = step_through(res.circuit)
        out = render_measurement(res, steps[-1], shots=20)
        assert "Measurement" in out and "most frequent" in out

    def test_register_split_in_statevector(self):
        res = deutsch_jozsa(2, "balanced")
        steps = step_through(res.circuit)
        out = render_step(res.circuit, steps[-1], phases=res.phases, registers=res.registers)
        assert "ancilla|input" in out

    def test_hide_zeros_note_when_nothing_to_hide(self):
        qc = QuantumCircuit(2)
        qc.h(0).h(1)  # uniform: no zero states
        steps = step_through(qc)
        out = render_statevector(steps[-1], hide_zeros=True)
        assert "no zero-probability states to hide" in out
