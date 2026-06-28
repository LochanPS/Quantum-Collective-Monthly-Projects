from __future__ import annotations

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qviz import step_through
from qviz.algorithms import bernstein_vazirani, deutsch_jozsa, grover, qft_algorithm
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
        qc, ann = deutsch_jozsa(2, "balanced")
        assert len(ann) == len(qc._log)

    def test_constant_oracle_leaves_input_at_zero(self):
        qc, _ = deutsch_jozsa(2, "constant_0")
        probs = qc.probabilities()
        # Input qubits are q0,q1 (rightmost 2 chars); should always read '00'
        assert all(state[-2:] == "00" for state in probs)

    def test_balanced_oracle_leaves_input_nonzero(self):
        qc, _ = deutsch_jozsa(2, "balanced")
        probs = qc.probabilities()
        assert all(state[-2:] != "00" for state in probs)

    def test_invalid_oracle_raises(self):
        with pytest.raises(ValueError):
            deutsch_jozsa(2, "not_a_real_oracle")


class TestBernsteinVazirani:
    def test_annotation_count_matches_gate_count(self):
        qc, ann = bernstein_vazirani("101")
        assert len(ann) == len(qc._log)

    def test_recovers_secret_with_certainty(self):
        qc, _ = bernstein_vazirani("101")
        probs = qc.probabilities()
        # qcsim labels are q(n-1)...q0 (leftmost = highest qubit), so the
        # input substring reads secret bits in reverse order.
        assert all(state[-3:][::-1] == "101" for state in probs)

    def test_recovers_non_palindromic_secret(self):
        """'101' is a palindrome -- reversal bugs hide there. Use '100' to catch them."""
        qc, _ = bernstein_vazirani("100")
        probs = qc.probabilities()
        assert all(state[-3:][::-1] == "100" for state in probs)

    def test_invalid_secret_raises(self):
        with pytest.raises(ValueError):
            bernstein_vazirani("102")
        with pytest.raises(ValueError):
            bernstein_vazirani("")


class TestGrover:
    def test_annotation_count_matches_gate_count(self):
        qc, ann = grover("11")
        assert len(ann) == len(qc._log)

    def test_finds_marked_state(self):
        qc, _ = grover("11")
        probs = qc.probabilities()
        assert probs.get("11", 0) > 0.99

    def test_finds_different_marked_state(self):
        qc, _ = grover("01")
        probs = qc.probabilities()
        assert probs.get("01", 0) > 0.99

    def test_finds_asymmetric_marked_state_other_direction(self):
        """'01' and '10' are bit-reversals of each other -- catches the
        label-orientation bug that a palindromic target would hide."""
        qc, _ = grover("10")
        probs = qc.probabilities()
        assert probs.get("10", 0) > 0.99

    def test_invalid_marked_state_raises(self):
        with pytest.raises(ValueError):
            grover("111")  # 3 bits, not supported in v1


class TestQFT:
    def test_annotation_count_matches_gate_count(self):
        qc, ann = qft_algorithm(3, "101")
        assert len(ann) == len(qc._log)

    def test_returns_normalized_state(self):
        qc, _ = qft_algorithm(3)
        probs = qc.probabilities()
        assert abs(sum(probs.values()) - 1.0) < 1e-9
