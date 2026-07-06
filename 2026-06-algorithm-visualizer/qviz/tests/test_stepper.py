from __future__ import annotations

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qviz import step_through
from qviz.algorithms import bernstein_vazirani, deutsch_jozsa, grover, qft_algorithm
from qviz.interpret import interpret_state, nonzero_states, phase_label
from qviz.render import render_progress_circuit, render_statevector, render_step


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
        """'01' and '10' are bit-reversals of each other -- catches the
        label-orientation bug that a palindromic target would hide."""
        res = grover("10")
        assert res.circuit.probabilities().get("10", 0) > 0.99

    def test_summary_reports_found(self):
        res = grover("10")
        steps = step_through(res.circuit)
        assert "FOUND" in res.summary(steps[-1])

    def test_invalid_marked_state_raises(self):
        with pytest.raises(ValueError):
            grover("111")  # 3 bits, not supported in v1


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
